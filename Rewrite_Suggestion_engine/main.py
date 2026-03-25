from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from Analysis_and_Suggestion_engine.Schema import ResumeSchema,JDRequirements

load_dotenv()

from pydantic import BaseModel
from typing import List, Dict, Any

class RewriteOutput(BaseModel):
    improved_resume: Dict[str, Any]
    changes_made: List[str]
    learning_recommendations: List[str]

rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a professional ATS resume optimization engine.

You are given:
- resume_json (structured resume data)
- jd_requirements
- matched_skills
- missing_skills

STRICT RULES (MANDATORY):

1. You may ONLY use information explicitly present in resume_json.
2. Do NOT invent, assume, infer, or fabricate:
   - New skills
   - New tools
   - New certifications
   - New projects
   - New experience
   - New companies
   - New metrics or numerical values
   - New achievements or awards
3. If a required JD skill is missing:
   - Do NOT add it into the resume.
   - Only include it under learning_recommendations.
4. You must preserve the exact structure and keys of resume_json.
   - Do not remove fields.
   - Do not add new fields.
   - Only modify values within existing fields.
   - The "achievements" field must be preserved as-is or improved in wording only.
5. Do not change the factual meaning of any statement.
6. Do not add any numerical metrics unless the exact number already exists.
7. Learning recommendations must be derived strictly from missing_skills.
8. Changes are NOT mandatory.
   - If the resume is already well aligned, return it unchanged.
   - Only modify sections if it clearly improves ATS alignment.

ALLOWED IMPROVEMENTS:

You MAY:
- Rephrase summary for clarity and JD alignment
- Strengthen wording without adding new facts
- Reorder skills to prioritize JD-relevant skills
- Reorder experience, projects, or bullet points
- Remove redundant wording
- Improve ATS keyword relevance using existing content only
- Improve wording of achievement statements for clarity and impact (without changing facts)
- Rephrase experience descriptions for stronger action verbs and ATS keywords

You may NOT:
- Add new factual content
- Insert missing JD skills into resume
- Create artificial achievements
- Inflate impact

IMPORTANT SCHEMA NOTES:
- experience[].description is a List of strings (bullet points), NOT a single string
- projects[].description is a List of strings (bullet points), NOT a single string
- achievements is a List of strings
- Preserve these list formats in the output

Return output strictly following the required structured schema.
Return ONLY valid JSON.
Do NOT include markdown.
Do NOT include explanations outside JSON.
"""),
    ("human", """
resume_json:
{resume_json}

jd_requirements:
{jd_requirements}

matched_skills:
{matched_skills}

missing_skills:
{missing_skills}
""")
])

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

structured_llm = llm.with_structured_output(RewriteOutput)

rewrite_chain = rewrite_prompt | structured_llm

def controlled_rewrite_engine(resume_model,jd_model,matched_skills,missing_skills):
    result = rewrite_chain.invoke({
        "resume_json": resume_model.model_dump(),
        "jd_requirements": jd_model.model_dump(),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    })

    return result

if "__main__" == __name__:
    res_text = {
    "name": "Satyam Kumar Mishra",
    "email": "satyamkumarmishra2005@gmail.com",
    "phone": "",
    "summary": "Backend Engineer specializing in building scalable, high-availability systems with Java and Spring Boot. Experienced in microservices architecture, event-driven design with Kafka, and cloud-native deployments on Kubernetes and AWS. Passionate about solving complex distributed systems challenges, API integrations, and building resilient infrastructure with 99.9%+ uptime.",
    "skills": [
        "Java",
        "SQL",
        "Spring Boot",
        "Spring Security",
        "Spring Cloud",
        "Spring Data JPA",
        "RESTful APIs",
        "Microservices",
        "Apache Kafka",
        "RabbitMQ",
        "Event Sourcing",
        "Asynchronous Processing",
        "PostgreSQL",
        "MySQL",
        "JDBC",
        "Transaction Management",
        "OAuth2",
        "JWT",
        "Keycloak",
        "Role-Based Access Control (RBAC)",
        "AWS",
        "Docker",
        "Kubernetes",
        "Helm",
        "CI/CD",
        "Git",
        "Maven",
        "Microservices Architecture",
        "API Gateway",
        "Service Discovery (Eureka)",
        "High Availability",
        "Fault Tolerance"
    ],
    "experience": [],
    "education": [
        {
            "institution": "Dronacharya College of Engineering Gurugram, Haryana",
            "degree": "Bachelor of Technology in Computer Science and Engineering",
            "year": "Aug 2023 - Aug 2027"
        }
    ],
    "projects": [
        {
            "title": "Eazy Bank – Microservices Banking Platform",
            "start_date": "",
            "end_date": "",
            "description": ["Architected a cloud-native digital banking system with 4 independently deployable microservices (Accounts, Cards, Loans, Messaging) processing transactional workflows with domain-driven design principles", "Built centralized configuration management with Spring Cloud Config Server, enabling zero-downtime deployments and environment-specific configurations across distributed services"],
            "link": "GitHub"
        },
        {
            "title": "RapidAid – Real-time Emergency Response System",
            "start_date": "",
            "end_date": "",
            "description": ["Developed a microservices platform for real-time incident reporting and automated responder allocation with sub-second response times", "Integrated Keycloak for enterprise-grade OAuth2/JWT authentication and role-based access control (RBAC) across multiple services"],
            "link": "GitHub"
        },
        {
            "title": "MediSort – Medicine Management Backend",
            "start_date": "",
            "end_date": "",
            "description": ["Built a RESTful backend system for prescription management with intelligent OCR processing from PDFs/images and structured metadata extraction", "Engineered scheduled reminder system with escalation workflows and acknowledgment tracking to improve medication adherence rates"],
            "link": "GitHub"
        }
    ],
    "certifications": [],
    "achievements": [],
    "links": [
        "linkedin.com/in/satyam",
        "github.com/satyamkumarmishra2005"
    ]
    }
    jd_text = {'job_title':'Junior Backend Engineer - Java & Spring Boot' ,
'required_skills':['Java', 'Spring Boot', 'RESTful APIs', 'SQL databases', 'Git', 'Maven/Gradle'] ,
'preferred_skills':['Microservices architecture', 'Distributed systems', 'Apache Kafka', 'RabbitMQ', 'Docker', 'Kubernetes', 'AWS', 'Spring Security', 'JWT', 'OAuth2'] ,
'experience_required':'0-2 years',
'education':'B.Tech / BE in Computer Science or related field (2024-2027 batch)' ,
'tools_and_technologies':['PostgreSQL', 'MySQL', 'Docker', 'Kubernetes', 'AWS'] ,
'soft_skills':['Collaboration', 'Agile environment', 'Problem-solving'] ,
'responsibilities':['Design, develop and maintain robust RESTful APIs and backend services using Java and Spring Boot', 'Work on building and integrating microservices that handle high transaction volumes', 'Implement database interactions with PostgreSQL or MySQL', 'Participate in asynchronous processing and messaging between services', 'Help deploy applications using containerization tools and cloud infrastructure', 'Collaborate with frontend and DevOps teams in an Agile environment', 'Write clean, maintainable code and participate in code reviews']}

    resume_model = ResumeSchema.model_validate(res_text)
    jd_model = JDRequirements.model_validate(jd_text)
    matched_skills = ['Java', 'Spring Boot', 'RESTful APIs', 'SQL databases', 'Git', 'Maven/Gradle']
    mising_skills = []

    res = controlled_rewrite_engine(resume_model, jd_model, matched_skills, mising_skills)
    print(res)