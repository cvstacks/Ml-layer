import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from dotenv import load_dotenv
from Parsing_engine.resume_parser import fix_broken_words
import re

load_dotenv()


class Experience(BaseModel):
    company: Optional[str] = ""
    role: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: List[str] = []

    # Coerce None → "" for all string fields
    @field_validator('company', 'role', 'start_date', 'end_date', mode='before')
    @classmethod
    def none_to_empty(cls, v):
        return v if v is not None else ""


class Education(BaseModel):
    institution: Optional[str] = ""
    degree: Optional[str] = ""
    year: Optional[str] = ""

    @field_validator('institution', 'degree', 'year', mode='before')
    @classmethod
    def none_to_empty(cls, v):
        return v if v is not None else ""


class Project(BaseModel):
    title: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: List[str] = []
    link: Optional[str] = ""

    @field_validator('title', 'start_date', 'end_date', 'link', mode='before')
    @classmethod
    def none_to_empty(cls, v):
        return v if v is not None else ""


class ResumeSchema(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    summary: Optional[str] = ""
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[str] = []
    achievements: List[str] = []
    links: List[str] = []

    @field_validator('name', 'email', 'phone', 'summary', mode='before')
    @classmethod
    def none_to_empty(cls, v):
        return v if v is not None else ""



llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    # google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


prompt = ChatPromptTemplate.from_messages([
    ("system",
     """
     You are an expert resume parser.
 
     Rules:
     - Only include PROFESSIONAL WORK EXPERIENCE in the experience field.
     - Do NOT include school leadership, clubs, academic roles, or projects as experience.
     - If no professional experience exists, return empty list.
     - Preserve spaces correctly in summary.
     - Extract only factual data present in resume.
     - Extract achievements, awards, honors, and accomplishments into the achievements field.
     - Do NOT hallucinate.
     Return ONLY valid JSON.
     """),
    ("human",
     """
     Extract structured resume data from the text below.
 
     STRICT INSTRUCTIONS:
 
     1. Extract ONLY information explicitly present in the resume.
     2. Do NOT hallucinate or infer missing data.
     3. If a section does not exist, return an empty list or empty string.
     4. Only include PROFESSIONAL WORK EXPERIENCE in "experience".
        - Do NOT include school leadership, student roles, clubs, or projects in experience.
     5. Preserve proper word spacing in summary.
     6. Extract GitHub, LinkedIn, portfolio, website, or other personal URLs into "links".
     7. For projects:
        - Extract project title if present.
        - If a title exists before description, use it.
        - If not clearly present, use the first line as title.
     8. Dates should remain exactly as written in resume.
     9. Do NOT reformat text unless necessary for spacing.
     10. Return ONLY valid JSON.
     11. Do NOT include explanations or markdown.
     12. For experience: extract each bullet point or responsibility as a separate item in the description list.
     13. For achievements/awards/honors/accomplishments:
         - Extract each achievement as a separate string in the "achievements" list.
         - Include awards, honors, recognitions, publications, and notable accomplishments.
         - If no achievements section exists, return empty list.
 
     JSON Schema:
 
     {{
       "name": "",
       "email": "",
       "phone": "",
       "summary": "",
       "skills": [],
       "experience": [
         {{
           "company": "",
           "role": "",
           "start_date": "",
           "end_date": "",
           "description": []
         }}
       ],
       "education": [
         {{
           "institution": "",
           "degree": "",
           "year": ""
         }}
       ],
       "projects": [
         {{
           "title": "",
           "start_date": "",
           "end_date": "",
           "description": [],
           "link": ""
         }}
       ],
       "certifications": [],
       "achievements": [],
       "links": []
     }}
 
     Resume Text:
     {resume_text}
     """)
])

def normalize_multiline_text(text: str):
    if not text:
        return ""

    # Replace line breaks with space
    text = text.replace("\n", " ")

    # Collapse extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def parse_resume_with_llm(resume_text: str):

    chain = prompt | llm

    response = chain.invoke({
        "resume_text": resume_text
    })

    try:
        content = response.content.strip()

        # Remove markdown if present
        content = content.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(content)

        # Validate using Pydantic
        validated = ResumeSchema(**parsed)

        data = validated.model_dump()

        # Normalize project descriptions
        for project in data.get("projects", []):
            desc = project.get("description", [])

            if isinstance(desc, list):
                project["description"] = [normalize_multiline_text(d) for d in desc]
            else:
                project["description"] = [normalize_multiline_text(desc)]

        # Normalize experience descriptions
        for exp in data.get("experience", []):
            desc = exp.get("description", [])

            if isinstance(desc, list):
                exp["description"] = [normalize_multiline_text(d) for d in desc]
            elif isinstance(desc, str) and desc:
                exp["description"] = [normalize_multiline_text(desc)]
            else:
                exp["description"] = []

        # Normalize achievements
        achievements = data.get("achievements", [])
        if isinstance(achievements, list):
            data["achievements"] = [normalize_multiline_text(a) for a in achievements if a]

        data["summary"] = fix_broken_words(data.get("summary", ""))

        return data

    except Exception as e:
        print("LLM Parsing Failed:", e)
        return None