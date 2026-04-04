"""
Unified FastAPI service for CV Stack ML layer.

This wraps all 4 ML engines into a single HTTP API:
  1. Parsing Engine   → POST /parse-resume
  2. Analysis Engine   → POST /analyze
  3. Rewrite Engine    → POST /tailor-resume  (full pipeline: parse JD → analyze → rewrite)
  4. LaTeX Generator   → POST /preview, POST /generate-pdf

Runs on port 8081 by default (matching Spring Boot's parsing.service.url config).
"""

import os
import json
import traceback
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ─── Import ML engines ───────────────────────────────────────────────────────

from Parsing_engine.main import download_resume, detect_file_type, extract_resume
from Parsing_engine.resume_parser import build_response
from Parsing_engine.llm_parser_layer import parse_resume_with_llm

from Analysis_and_Suggestion_engine.Schema import (
    ResumeSchema,
    JDRequirements,
)
from Analysis_and_Suggestion_engine.Analysis_Scoring_engine import calculate_final_ats
from Analysis_and_Suggestion_engine.jd_parser import extract_jd_requirements

from Rewrite_Suggestion_engine.main import controlled_rewrite_engine

from latext_generator.main_pipeline import generate_preview_html

# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="CV Stack ML Service",
    description="AI-powered resume parsing, analysis, rewriting, and PDF generation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request / Response Schemas ───────────────────────────────────────────────


class ResumeUrlRequest(BaseModel):
    resume_url: str


class ResumeJdRequest(BaseModel):
    """Shared request for analyze / tailor endpoints."""
    resume_data: Dict[str, Any]
    jd_text: str


class PreviewRequest(BaseModel):
    original_resume: Dict[str, Any]
    improved_resume: Dict[str, Any]


# ─── 1. PARSING ENDPOINT ─────────────────────────────────────────────────────


def process_resume(file_path: str) -> dict:
    """Parse a local file (PDF/DOCX) into structured resume JSON."""
    extracted = extract_resume(file_path)
    llm_result = parse_resume_with_llm(extracted["text"])

    if llm_result:
        extracted_links = extracted.get("hyperlinks", [])
        if "links" not in llm_result:
            llm_result["links"] = []
        for link in extracted_links:
            if isinstance(link, dict) and "uri" in link:
                if link["uri"] not in llm_result["links"]:
                    llm_result["links"].append(link["uri"])
        return llm_result

    return build_response(extracted["text"], extracted["tables"])


@app.post("/parse-resume")
def parse_resume(request: ResumeUrlRequest):
    """
    Download resume from URL, parse with LLM, return structured data.

    Called by: Spring Boot ResumeParsingService.requestParsing()
    Expects: { "resume_url": "https://..." }
    Returns: ParsedResumeData JSON
    """
    try:
        file_path = download_resume(request.resume_url)
        file_type = detect_file_type(file_path)

        if file_type not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        result = process_resume(file_path)

        if not result:
            raise HTTPException(status_code=500, detail="LLM parsing failed")

        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

        return result

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── 2. ANALYSIS ENDPOINT ────────────────────────────────────────────────────


def parse_jd_text(jd_text: str) -> JDRequirements:
    """Parse raw JD text into structured JD requirements using LLM."""
    return extract_jd_requirements(jd_text)


@app.post("/parse-jd")
def parse_jd(request: dict):
    """
    Parse a raw JD text into structured requirements.

    Expects: { "jd_text": "..." }
    Returns: JDRequirements JSON
    """
    jd_text = request.get("jd_text", "")
    if not jd_text:
        raise HTTPException(status_code=400, detail="jd_text is required")

    try:
        result = parse_jd_text(jd_text)
        return result.model_dump()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
def analyze_resume(request: ResumeJdRequest):
    """
    Analyze resume against JD for ATS scoring.

    Called by: Spring Boot ResumeAnalysisService.analyzeResume()
    Expects: { "resume_data": {...}, "jd_text": "..." }
    Returns: ATS score breakdown with matched/missing skills
    """
    try:
        # Convert dicts to Pydantic models
        resume_model = ResumeSchema.model_validate(request.resume_data)
        jd_model = parse_jd_text(request.jd_text)

        # Run ATS analysis
        result = calculate_final_ats(resume_model, jd_model)
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── 3. FULL PIPELINE: ANALYZE + REWRITE ─────────────────────────────────────


@app.post("/tailor-resume")
def tailor_resume(request: ResumeJdRequest):
    """
    Full pipeline: Parse JD → Analyze ATS → Rewrite resume.

    Called by: Spring Boot ResumeTailoringService.tailorResume()
    Expects: { "resume_data": {...}, "jd_text": "..." }
    Returns: {
        "improved_resume": {...},
        "changes_made": [...],
        "learning_recommendations": [...],
        "ats_analysis": {...}
    }
    """
    try:
        # Step 1: Convert resume to model
        resume_model = ResumeSchema.model_validate(request.resume_data)

        # Step 2: Parse JD text into structured requirements
        jd_model = parse_jd_text(request.jd_text)

        # Step 3: ATS Analysis
        ats_result = calculate_final_ats(resume_model, jd_model)

        matched_skills = ats_result.get("matched_required_skills", [])
        missing_skills = ats_result.get("missing_required_skills", [])

        # Step 4: Controlled Rewrite
        rewrite_result = controlled_rewrite_engine(
            resume_model, jd_model, matched_skills, missing_skills
        )

        # Step 5: Build response
        response = {
            "improved_resume": rewrite_result.improved_resume,
            "changes_made": rewrite_result.changes_made,
            "learning_recommendations": rewrite_result.learning_recommendations,
            "ats_analysis": ats_result,
        }

        return response

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── 4. PREVIEW ENDPOINT ─────────────────────────────────────────────────────


@app.post("/preview")
def generate_preview(request: PreviewRequest):
    """
    Generate HTML preview with highlighted changes between original and improved.

    Called by: Spring Boot ResumeTailoringService.generatePreview()
    Expects: { "original_resume": {...}, "improved_resume": {...} }
    Returns: Resume dict with HTML highlight tags for the frontend
    """
    try:
        result = generate_preview_html(request.original_resume, request.improved_resume)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── Health Check ─────────────────────────────────────────────────────────────


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cv-stack-ml"}


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
