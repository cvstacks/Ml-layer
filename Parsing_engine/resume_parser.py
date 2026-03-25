import re

def clean_text(text):
    text = re.sub(r'\xa0', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

def extract_personal_info(text):

    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phones = re.findall(r"\+?\d[\d\s-]{8,}", text)
    links = re.findall(r"https?://\S+", text)

    return {
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "links": links
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
    "summary": ["summary", "profile", "objective", "about me", "professional summary"],
    "skills": ["skills", "technical skills", "competencies", "core competencies", "technologies"],
    "experience": ["experience", "work experience", "professional experience", "employment history"],
    "education": ["education", "academic background", "qualifications"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "professional certifications", "licenses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments", "recognitions",
                      "publications", "achievements & awards", "awards & honors"],
    "languages": ["languages", "language proficiency"]
}

# Maximum word count for a line to be considered a section heading
MAX_HEADING_WORDS = 6


def is_section_heading(line):
    """
    Check if a line is likely a section heading rather than body text.
    Section headings are typically short (few words) and don't end with
    sentence punctuation.
    """
    stripped = line.strip()

    if not stripped:
        return False

    # Too many words to be a heading
    if len(stripped.split()) > MAX_HEADING_WORDS:
        return False

    # Lines ending with sentence punctuation are body text, not headings
    if stripped.endswith(('.', ',', ';', ':')):
        return False

    return True


def split_sections(text):

    sections = {}
    current_section = "general"
    sections[current_section] = []

    lines = text.split("\n")

    for line in lines:

        lower_line = line.lower().strip()

        matched = False

        if is_section_heading(line):
            for section, keywords in SECTION_KEYWORDS.items():
                if any(lower_line == keyword or lower_line.startswith(keyword + ":") or
                       lower_line.startswith(keyword + " :") for keyword in keywords):
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

def extract_achievements(text):
    """Extract individual achievement items from the achievements section text."""
    if not text:
        return []

    # Split by bullet points, newlines, or numbered items
    tokens = re.split(r"[\n•·▪▸►]|\d+[.)]\s*", text)

    achievements = []
    for token in tokens:
        token = token.strip()
        # Filter out very short or empty items
        if len(token) > 5:
            achievements.append(token)

    return achievements

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
        "achievements": extract_achievements(sections.get("achievements", "")),
        "languages": sections.get("languages", ""),
        "tables": tables
    }