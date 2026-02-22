import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from resume_parser import fix_broken_words
import re

load_dotenv()

from pydantic import BaseModel
from typing import List


class Experience(BaseModel):
    company: str = ""
    role: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    year: str = ""


class Project(BaseModel):
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    link: str = ""


class ResumeSchema(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[str] = []
    links: List[str] = []



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
           "description": ""
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
           "description": "",
           "link": ""
         }}
       ],
       "certifications": [],
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

        data = validated.dict()

        for project in data.get("projects", []):
            project["description"] = normalize_multiline_text(project.get("description", ""))

        data["summary"] = fix_broken_words(data.get("summary", ""))

        return data

    except Exception as e:
        print("LLM Parsing Failed:", e)
        return None