from preview.preview_builder import build_preview
from engine.renderer import render_to_tex
from engine.pdf_generator import compile_resume

original_resume = {'name': 'Satyam Kumar Mishra', 'email': 'satyamkumarmishra2005@gmail.com', 'phone': '',

'summary': 'Backend Developer skilled in Java, Spring Boot, and Microservices, with hands-on experience building containerized systems using Docker & Kubernetes. Proficient in event-driven architectures (Kafka, Rabbit MQ) and secure API development (JWT, OAuth2, Keycloak) with experience deploying services on AWS.',

'skills': ['Java', 'SQL', 'Spring Boot', 'Spring MVC', 'Spring Security', 'Spring Cloud', 'Spring Data JPA', 'PostgreSQL', 'MySQL', 'RESTful APIs', 'Microservices', 'API Gateway', 'Eureka', 'Keycloak', 'OAuth2', 'JWT', 'Role-Based Access Control', 'Docker', 'Kubernetes', 'Helm', 'Git', 'Maven', 'Postman', 'RabbitMQ', 'Kafka', 'Cloudinary', 'AWS'],

'experience': [],

'education': [{'institution': 'Dronacharya College of Engineering Gurugram, Haryana', 'degree': 'Bachelor of Technology in Computer Science and Engineering', 'year': 'Aug 2023 - Aug 2027'}],

'projects': [{'title': 'Eazy Bank – Microservices Based Banking System', 'start_date': '', 'end_date': '', 'description': ['Designed and implemented a cloud-native digital banking platform composed of 4 independently deployable microservices (Accounts, Cards, Loans, Messaging) following domain-driven design principles', 'Implemented Spring Cloud Config Server for centralized configuration management, enabling environment-specific configuration updates without service redeployments', 'Integrated Apache Kafka to enable asynchronous, event-driven communication, reducing tight coupling between services and improving system resilience', 'Containerized all services using Docker and deployed them on Kubernetes, leveraging orchestration features such as self-healing, rolling updates, and automated restarts to improve availability and fault tolerance'], 'link': 'GitHub'}, {'title': 'RapidAid – Emergency Response Management System', 'start_date': '', 'end_date': '', 'description': ['Built a microservices-based emergency response platform enabling real-time incident reporting, responder allocation, and notification workflows', 'Implemented a dedicated User Service integrated with Keycloak, providing secure authentication, authorization, and role-based access control (RBAC) across services', 'Designed an event-driven architecture using Kafka to decouple incident intake, responder assignment, and notification services, improving scalability and reliability', 'Developed responder state lifecycle management (Available → Assigned → Dispatched) with automated notifications to ensure consistent state transitions under concurrent incidents'], 'link': 'GitHub'}, {'title': 'MediSort – Medicine Management System', 'start_date': '', 'end_date': '', 'description': ['Developed a medicine management backend to organize prescriptions from PDFs and images with structured metadata storage and efficient retrieval', 'Implemented backend scheduling for dose reminders with escalation logic and user acknowledgment tracking, improving medication adherence workflows', 'Designed automated medicine end-date calculation and stock-based refill prediction, dynamically recalculating schedules based on dosage and inventory changes', 'Deployed the application on AWS, hosting backend services on Amazon EC2, using Amazon RDS (PostgreSQL) for persistent storage and Route 53 for domain-based routing', 'Integrated Cloudinary for secure cloud-based document storage, enabling scalable uploads, access control, and reliable delivery of medical documents via backend APIs'], 'link': 'GitHub'}],

'certifications': [],

'links': ['linkedin.com/in/satyam', 'github.com/satyamkumarmishra2005']}


improved_resume = {'name': 'Satyam Kumar Mishra', 'email': 'satyamkumarmishra2005@gmail.com', 'phone': '',

'summary': 'Backend Engineer specializing in building scalable, high-availability systems with Java and Spring Boot. Experienced in microservices architecture, event-driven design with Kafka, and cloud-native deployments on Kubernetes and AWS. Passionate about solving complex distributed systems challenges, API integrations, and building resilient infrastructure with 99.9%+ uptime.',

'skills': ['Java', 'Spring Boot', 'RESTful APIs', 'SQL', 'PostgreSQL', 'MySQL', 'Git', 'Maven', 'Microservices Architecture', 'Apache Kafka', 'RabbitMQ', 'Docker', 'Kubernetes', 'AWS', 'Spring Security', 'JWT', 'OAuth2', 'Spring Cloud', 'Spring Data JPA', 'Microservices', 'Event Sourcing', 'Asynchronous Processing', 'JDBC', 'Transaction Management', 'Keycloak', 'Role-Based Access Control (RBAC)', 'Helm', 'CI/CD', 'API Gateway', 'Service Discovery (Eureka)', 'High Availability', 'Fault Tolerance'],

'experience': [],

'education': [{'institution': 'Dronacharya College of Engineering Gurugram, Haryana', 'degree': 'Bachelor of Technology in Computer Science and Engineering', 'year': 'Aug 2023 - Aug 2027'}],

'projects': [{'title': 'Eazy Bank – Microservices Banking Platform', 'start_date': '', 'end_date': '', 'description': ['Architected a cloud-native digital banking system with 4 independently deployable microservices (Accounts, Cards, Loans, Messaging), processing transactional workflows leveraging domain-driven design principles.', 'Implemented centralized configuration management with Spring Cloud Config Server, enabling zero-downtime deployments and environment-specific configurations across distributed services.', 'Utilized event-driven architecture with Apache Kafka for asynchronous inter-service communication, ensuring loose coupling and system resilience under high transaction volumes.', 'Deployed on Kubernetes with self-healing capabilities, rolling updates, and horizontal pod autoscaling to achieve 99.9% service availability.'], 'link': 'GitHub'}, {'title': 'RapidAid – Real-time Emergency Response System', 'start_date': '', 'end_date': '', 'description': ['Developed a microservices platform for real-time incident reporting and automated responder allocation, achieving sub-second response times.', 'Integrated Keycloak for enterprise-grade OAuth2/JWT authentication and Role-Based Access Control (RBAC) across multiple services.', 'Designed event-driven workflows using Kafka to decouple incident intake, routing logic, and notification delivery, improving system scalability and fault tolerance.', 'Implemented state machine-based responder lifecycle management with automated notifications and consistency guarantees under concurrent incident loads.'], 'link': 'GitHub'}, {'title': 'MediSort – Medicine Management Backend', 'start_date': '', 'end_date': '', 'description': ['Built a RESTful backend system for prescription management, incorporating intelligent OCR processing from PDFs/images and structured metadata extraction.', 'Engineered a scheduled reminder system with escalation workflows and acknowledgment tracking to improve medication adherence rates.', 'Deployed on AWS infrastructure utilizing EC2 compute instances, RDS for PostgreSQL data persistence, and Route 53 for DNS-based service routing.', 'Integrated Cloudinary CDN for secure document storage with API-based access control and optimized content delivery at scale.'], 'link': 'GitHub'}],

'certifications': [],

 'links': ['linkedin.com/in/satyam', 'github.com/satyamkumarmishra2005']}


print("Building preview...")

preview = build_preview(original_resume, improved_resume)

print("Preview JSON:")
print(preview)


print("\nGenerating LaTeX...")

tex_file = render_to_tex(
    improved_resume,
    template="universal_pro.tex",
    output_path="resume.tex"
)

print("LaTeX generated:", tex_file)


print("\nCompiling PDF...")

pdf_file = compile_resume(tex_file)

print("Final PDF:", pdf_file)