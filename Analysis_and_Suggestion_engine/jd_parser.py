import os

from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from Analysis_and_Suggestion_engine.Schema import JDRequirements
load_dotenv()



llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

structured_llm = llm.with_structured_output(JDRequirements)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert HR AI system.

Extract structured job requirements from the given job description.

Return ONLY valid JSON matching this schema:

{{
  "job_title": "",
  "required_skills": [],
  "preferred_skills": [],
  "experience_required": "",
  "education": "",
  "tools_and_technologies": [],
  "soft_skills": [],
  "responsibilities": []
}}
"""),
    ("human", "{jd_text}")
])

chain = prompt | structured_llm

def extract_jd_requirements(jd_text: str):
    response = chain.invoke({"jd_text": jd_text})

    return response

if __name__ == "__main__":
    jd = ''' Junior Backend Engineer - Java & Spring Boot

PulseFin Solutions is a fast-growing fintech startup based in Gurugram that is building next-generation digital banking and payment platforms. We are looking for a passionate and motivated Junior Backend Engineer to join our core engineering team and help build scalable, reliable backend systems.

What you will be doing:
- Design, develop and maintain robust RESTful APIs and backend services using Java and Spring Boot
- Work on building and integrating microservices that handle high transaction volumes
- Implement database interactions with PostgreSQL or MySQL
- Participate in asynchronous processing and messaging between services
- Help deploy applications using containerization tools and cloud infrastructure
- Collaborate with frontend and DevOps teams in an Agile environment
- Write clean, maintainable code and participate in code reviews

Requirements (Must Have):
- Pursuing or recently completed B.Tech / BE in Computer Science or related field (2024-2027 batch)
- Strong programming skills in Java
- Hands-on experience with Spring Boot framework and building REST APIs
- Good understanding of SQL databases (PostgreSQL or MySQL)
- Basic knowledge of Git and Maven/Gradle

Preferred / Good to Have:
- Exposure to microservices architecture and distributed systems
- Familiarity with message queues like Apache Kafka or RabbitMQ
- Experience working with Docker and Kubernetes
- Knowledge of cloud platforms, preferably AWS (EC2, RDS, etc.)
- Understanding of Spring Security, JWT, or OAuth2 concepts
- Any personal projects or internships involving backend development

We are open to freshers and candidates with 0-2 years of experience who have built strong academic or personal projects in Java/Spring Boot. If you are passionate about building scalable systems and love solving real-world problems, we would love to hear from you!

Location: Gurugram (Hybrid - 3 days in office)
Experience: 0-2 years '''
    print(extract_jd_requirements(jd))