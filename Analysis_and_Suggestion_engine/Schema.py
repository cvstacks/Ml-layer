from pydantic import BaseModel, Field
from typing import List


class Experience(BaseModel):
    company: str = ""
    role: str = ""
    start_date: str = ""
    end_date: str = ""
    description: List[str] = []


class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    year: str = ""


class Project(BaseModel):
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    description: List[str] = []
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
    achievements: List[str] = []
    links: List[str] = []


class JDRequirements(BaseModel):
    job_title: str = Field(description="Title of the job role")
    required_skills: List[str] = Field(description="Mandatory technical skills")
    preferred_skills: List[str] = Field(description="Optional or good-to-have skills")
    experience_required: str = Field(description="Years or type of experience required")
    education: str = Field(description="Educational qualification required")
    tools_and_technologies: List[str] = Field(description="Tools, frameworks, software required")
    soft_skills: List[str] = Field(description="Communication, teamwork etc")
    responsibilities: List[str] = Field(description="Main job responsibilities")