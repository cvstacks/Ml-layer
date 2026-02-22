import re

def clean_text(text):
    text = re.sub(r'\xa0', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

def extract_personal_info(text):

    return {
        "email": re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text),
        "phone": re.findall(r"\+?\d[\d\s-]{8,}", text),
        "links": re.findall(r"https?://\S+", text)
    }

def fix_broken_words(text: str):

    # Add space between lowercase and uppercase transitions
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Fix missing spaces after punctuation
    text = re.sub(r'([.,])([A-Za-z])', r'\1 \2', text)

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

SECTION_KEYWORDS = {
    "summary": ["summary", "profile", "objective"],
    "skills": ["skills", "technical skills", "competencies"],
    "experience": ["experience", "work experience", "professional experience"],
    "education": ["education"],
    "projects": ["projects"],
    "certifications": ["certifications"]
}


def split_sections(text):

    sections = {}
    current_section = "general"
    sections[current_section] = []

    lines = text.split("\n")

    for line in lines:

        lower_line = line.lower().strip()

        matched = False

        for section, keywords in SECTION_KEYWORDS.items():
            if any(keyword in lower_line for keyword in keywords):
                current_section = section
                sections[current_section] = []
                matched = True
                break

        if not matched:
            sections.setdefault(current_section, []).append(line)

    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections

def extract_skills(text):

    tokens = re.split(r"[,\n•|]", text)

    skills = []

    for token in tokens:
        token = token.strip()
        if 2 < len(token) < 40:
            skills.append(token)

    return list(set(skills))

def build_response(text, tables):

    text = clean_text(text)
    sections = split_sections(text)

    return {
        "personal_info": extract_personal_info(text),
        "summary": sections.get("summary", ""),
        "skills": extract_skills(sections.get("skills", "")),
        "experience": sections.get("experience", ""),
        "education": sections.get("education", ""),
        "projects": sections.get("projects", ""),
        "certifications": sections.get("certifications", ""),
        "tables": tables
    }