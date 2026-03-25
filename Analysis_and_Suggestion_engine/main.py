import requests
from typing import Dict, Any
from fastapi import FastAPI

from Analysis_and_Suggestion_engine.Analysis_Scoring_engine import calculate_final_ats
# from jd_parser import extract_jd_requirements

from Analysis_and_Suggestion_engine.Schema import JDRequirements, ResumeSchema

# def get_match_from_endpoint(endpoint_url: str, headers: dict | None = None) :
#     resp = requests.get(endpoint_url, headers=headers, timeout=10)
#     resp.raise_for_status()
#     data = resp.json()
#
#     parsed_resume = data.get("parsed_resume", {})
#     jd_text1 = data.get("job_description_text", "")
#
#     if not jd_text:
#         return {"error": "No job description text received"}
#
#     # Extract structured requirements
#     jd_struct = extract_jd_requirements(jd_text1)



# Example usage in FastAPI / Flask endpoint
app = FastAPI()


@app.get("/analyze")
def analyze_resume_and_jd():
    endpoint = "https://your-backend.com/api/get-resume-jd-pair/123"
    # result = get_match_from_endpoint(endpoint)
    # return result

if __name__ == "__main__":
    # jd_text = ''
    # jd_str = extract_jd_requirements(jd_text)

    res_str ={
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
            "description": ["Architected a cloud-native digital banking system with 4 independently deployable microservices (Accounts, Cards, Loans, Messaging) processing transactional workflows with domain-driven design principles Built centralized configuration management with Spring Cloud Config Server, enabling zero-downtime deployments and environment-specific configurations across distributed services Implemented event-driven architecture using Apache Kafka for asynchronous inter-service communication, ensuring loose coupling and system resilience under high transaction volumes Deployed on Kubernetes with self-healing capabilities, rolling updates, and horizontal pod autoscaling to achieve 99.9% service availability"],
            "link": "GitHub"
        },
        {
            "title": "RapidAid – Real-time Emergency Response System",
            "start_date": "",
            "end_date": "",
            "description": ["Developed a microservices platform for real-time incident reporting and automated responder allocation with sub-second response times Integrated Keycloak for enterprise-grade OAuth2/JWT authentication and role-based access control (RBAC) across multiple services Designed event-driven workflows using Kafka to decouple incident intake, routing logic, and notification delivery, improving system scalability and fault tolerance Implemented state machine-based responder lifecycle management with automated notifications and consistency guarantees under concurrent incident loads"],
            "link": "GitHub"
        },
        {
            "title": "MediSort – Medicine Management Backend",
            "start_date": "",
            "end_date": "",
            "description": ["Built a RESTful backend system for prescription management with intelligent OCR processing from PDFs/images and structured metadata extraction Engineered scheduled reminder system with escalation workflows and acknowledgment tracking to improve medication adherence rates Deployed on AWS infrastructure with EC2 compute instances, RDS for PostgreSQL data persistence, and Route 53 for DNS-based service routing Integrated Cloudinary CDN for secure document storage with API-based access control and optimized content delivery at scale"],
            "link": "GitHub"
        }
    ],
    "certifications": [],
    "links": [
        "linkedin.com/in/satyam",
        "github.com/satyamkumarmishra2005"
    ]
    }

    jd = {'job_title':'Junior Backend Engineer - Java & Spring Boot' ,
'required_skills':['Java', 'Spring Boot', 'RESTful APIs', 'SQL databases', 'Git', 'Maven/Gradle'] ,
'preferred_skills':['Microservices architecture', 'Distributed systems', 'Apache Kafka', 'RabbitMQ', 'Docker', 'Kubernetes', 'AWS', 'Spring Security', 'JWT', 'OAuth2'] ,
'experience_required':'0-2 years',
'education':'B.Tech / BE in Computer Science or related field (2024-2027 batch)' ,
'tools_and_technologies':['PostgreSQL', 'MySQL', 'Docker', 'Kubernetes', 'AWS'] ,
'soft_skills':['Collaboration', 'Agile environment', 'Problem-solving'] ,
'responsibilities':['Design, develop and maintain robust RESTful APIs and backend services using Java and Spring Boot', 'Work on building and integrating microservices that handle high transaction volumes', 'Implement database interactions with PostgreSQL or MySQL', 'Participate in asynchronous processing and messaging between services', 'Help deploy applications using containerization tools and cloud infrastructure', 'Collaborate with frontend and DevOps teams in an Agile environment', 'Write clean, maintainable code and participate in code reviews']}


    jd_model = JDRequirements.model_validate(jd)

    res_str2 = {'name': 'Satyam Kumar Mishra', 'email': 'satyamkumarmishra2005@gmail.com', 'phone': '',

'summary': 'Backend Engineer specializing in building scalable, high-availability systems with Java and Spring Boot. Experienced in microservices architecture, event-driven design with Kafka, and cloud-native deployments on Kubernetes and AWS. Passionate about solving complex distributed systems challenges, API integrations, and building resilient infrastructure with 99.9%+ uptime.',

'skills': ['Java', 'Spring Boot', 'RESTful APIs', 'SQL', 'PostgreSQL', 'MySQL', 'Git', 'Maven', 'Microservices Architecture', 'Apache Kafka', 'RabbitMQ', 'Docker', 'Kubernetes', 'AWS', 'Spring Security', 'JWT', 'OAuth2', 'Spring Cloud', 'Spring Data JPA', 'Microservices', 'Event Sourcing', 'Asynchronous Processing', 'JDBC', 'Transaction Management', 'Keycloak', 'Role-Based Access Control (RBAC)', 'Helm', 'CI/CD', 'API Gateway', 'Service Discovery (Eureka)', 'High Availability', 'Fault Tolerance'],

'experience': [],

'education': [{'institution': 'Dronacharya College of Engineering Gurugram, Haryana', 'degree': 'Bachelor of Technology in Computer Science and Engineering', 'year': 'Aug 2023 - Aug 2027'}],

'projects': [{'title': 'Eazy Bank – Microservices Banking Platform', 'start_date': '', 'end_date': '', 'description': ['Architected a cloud-native digital banking system with 4 independently deployable microservices (Accounts, Cards, Loans, Messaging), processing transactional workflows leveraging domain-driven design principles.', 'Implemented centralized configuration management with Spring Cloud Config Server, enabling zero-downtime deployments and environment-specific configurations across distributed services.', 'Utilized event-driven architecture with Apache Kafka for asynchronous inter-service communication, ensuring loose coupling and system resilience under high transaction volumes.', 'Deployed on Kubernetes with self-healing capabilities, rolling updates, and horizontal pod autoscaling to achieve 99.9% service availability.'], 'link': 'GitHub'}, {'title': 'RapidAid – Real-time Emergency Response System', 'start_date': '', 'end_date': '', 'description': ['Developed a microservices platform for real-time incident reporting and automated responder allocation, achieving sub-second response times.', 'Integrated Keycloak for enterprise-grade OAuth2/JWT authentication and Role-Based Access Control (RBAC) across multiple services.', 'Designed event-driven workflows using Kafka to decouple incident intake, routing logic, and notification delivery, improving system scalability and fault tolerance.', 'Implemented state machine-based responder lifecycle management with automated notifications and consistency guarantees under concurrent incident loads.'], 'link': 'GitHub'}, {'title': 'MediSort – Medicine Management Backend', 'start_date': '', 'end_date': '', 'description': ['Built a RESTful backend system for prescription management, incorporating intelligent OCR processing from PDFs/images and structured metadata extraction.', 'Engineered a scheduled reminder system with escalation workflows and acknowledgment tracking to improve medication adherence rates.', 'Deployed on AWS infrastructure utilizing EC2 compute instances, RDS for PostgreSQL data persistence, and Route 53 for DNS-based service routing.', 'Integrated Cloudinary CDN for secure document storage with API-based access control and optimized content delivery at scale.'], 'link': 'GitHub'}],

'certifications': [],

 'links': ['linkedin.com/in/satyam', 'github.com/satyamkumarmishra2005']}
    resume_model = ResumeSchema.model_validate(res_str)
    res = calculate_final_ats(resume_model, jd_model)
    print(res)
    # or print(result.model_dump_json(indent=2))
