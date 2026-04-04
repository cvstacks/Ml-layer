from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class Experience(BaseModel):
    company: Optional[str] = ""
    role: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: List[str] = []

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


class JDRequirements(BaseModel):
    job_title: str = Field(description="Title of the job role")
    required_skills: List[str] = Field(description="Mandatory technical skills")
    preferred_skills: List[str] = Field(description="Optional or good-to-have skills")
    experience_required: str = Field(description="Years or type of experience required")
    education: str = Field(description="Educational qualification required")
    tools_and_technologies: List[str] = Field(description="Tools, frameworks, software required")
    soft_skills: List[str] = Field(description="Communication, teamwork etc")
    responsibilities: List[str] = Field(description="Main job responsibilities")