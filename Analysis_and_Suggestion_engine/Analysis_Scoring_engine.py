from datetime import datetime
import re

from Analysis_and_Suggestion_engine.jd_parser import JDRequirements
from Parsing_engine.llm_parser_layer import ResumeSchema

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def normalize(text):
    return text.lower().strip()


def parse_date(date_str):
    if not date_str or "present" in date_str.lower():
        return datetime.now()

    formats = ["%Y-%m", "%b %Y", "%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None


def calculate_duration_years(start, end):
    start_date = parse_date(start)
    end_date = parse_date(end)

    if not start_date or not end_date:
        return 0

    return (end_date - start_date).days / 365

def build_resume_skill_corpus(resume):
    corpus = []

    corpus.extend(resume.skills)

    for exp in resume.experience:
        # description is now List[str]
        if isinstance(exp.description, list):
            corpus.extend(exp.description)
        elif exp.description:
            corpus.append(exp.description)

    for proj in resume.projects:
        if isinstance(proj.description, list):
            corpus.extend(proj.description)
        elif proj.description:
            corpus.append(proj.description)

    # Include achievements in skill corpus
    if resume.achievements:
        corpus.extend(resume.achievements)

    corpus.append(resume.summary)

    return corpus

def skill_in_text(skill, text):
    return bool(re.search(rf"\b{re.escape(skill)}\b", text.lower()))


def extract_years_from_jd(experience_text: str) -> float:
    if not experience_text:
        return 0

    numbers = re.findall(r'\d+\.?\d*', experience_text)

    if not numbers:
        return 0

    numbers = [float(n) for n in numbers]

    # If range like "0-2 years" → take max
    return max(numbers)

def embedding_experience_score(resume: ResumeSchema, jd: JDRequirements, threshold=0.6):

    required_years = extract_years_from_jd(jd.experience_required)

    total_years = 0
    skill_years = {skill: 0 for skill in jd.required_skills}

    # Precompute skill embeddings
    skill_embeddings = {
        skill: model.encode([skill])
        for skill in jd.required_skills
    }

    for exp in resume.experience:
        duration = calculate_duration_years(exp.start_date, exp.end_date)
        total_years += duration

        # description is now List[str] — combine for embedding
        desc_text = " ".join(exp.description) if isinstance(exp.description, list) else exp.description
        if not desc_text:
            continue

        exp_embedding = model.encode([desc_text])

        for skill, skill_emb in skill_embeddings.items():
            similarity = cosine_similarity(skill_emb, exp_embedding)[0][0]

            if similarity >= threshold:
                skill_years[skill] += duration

    if required_years == 0:
        # JD truly has no experience requirement
        overall_score = 1.0

    elif total_years == 0:
        # Fresher logic
        if required_years <= 2:
            overall_score = 0.75
        else:
            overall_score = 0.4

    else:
        overall_score = min(total_years / required_years, 1.0)

    if not jd.required_skills or required_years == 0:
        skill_exp_score = 1.0
    else:
        skill_scores = [
            min(skill_years[skill] / required_years, 1.0)
            for skill in jd.required_skills
        ]
        skill_exp_score = sum(skill_scores) / len(skill_scores)

    final_score = (0.6 * overall_score) + (0.4 * skill_exp_score)

    return float(final_score), round(total_years, 2), skill_years

def embedding_hard_skill_score(resume: ResumeSchema, jd: JDRequirements, threshold=0.65):

    resume_corpus = build_resume_skill_corpus(resume)

    if not resume_corpus:
        return 0.0, [], jd.required_skills

    resume_embeddings = model.encode(resume_corpus)
    matched = []
    missing = []
    score_sum = 0

    for skill in jd.required_skills:
        skill_embedding = model.encode([skill])

        similarities = cosine_similarity(skill_embedding, resume_embeddings)[0]
        max_similarity = np.max(similarities)

        if max_similarity >= threshold:
            score_sum += max_similarity  
            matched.append(skill)
        else:
            missing.append(skill)

    final_score = score_sum / len(jd.required_skills) if jd.required_skills else 1.0

    return final_score, matched, missing

def embedding_preferred_skill_score(resume: ResumeSchema, jd: JDRequirements, threshold=0.6):

    resume_corpus = build_resume_skill_corpus(resume)

    if not jd.preferred_skills:
        return 1.0

    resume_embeddings = model.encode(resume_corpus)
    score_sum = 0

    for skill in jd.preferred_skills:
        skill_embedding = model.encode([skill])
        similarities = cosine_similarity(skill_embedding, resume_embeddings)[0]
        max_similarity = np.max(similarities)

        if max_similarity >= threshold:
            score_sum += max_similarity

    return score_sum / len(jd.preferred_skills)

def embedding_education_similarity(jd_text, resume_text):

    emb1 = model.encode([jd_text])
    emb2 = model.encode([resume_text])

    return float(cosine_similarity(emb1, emb2)[0][0])

DEGREE_LEVELS = {
    "phd": 4,
    "doctor": 4,
    "master": 3,
    "m.tech": 3,
    "bachelor": 2,
    "b.tech": 2,
    "b.e": 2,
    "bsc": 2,
    "diploma": 1
}

def detect_degree_level(text):
    text = text.lower()
    for key, val in DEGREE_LEVELS.items():
        if key in text:
            return val
    return 0

def embedding_based_education_score(resume: ResumeSchema, jd: JDRequirements):

    if not resume.education:
        return 0.3

    jd_text = jd.education
    jd_level = detect_degree_level(jd_text)

    best_score = 0

    for edu in resume.education:

        resume_text = edu.degree
        resume_level = detect_degree_level(resume_text)

        # 1Semantic similarity
        semantic_sim = embedding_education_similarity(jd_text, resume_text)

        # Degree hierarchy penalty
        if resume_level >= jd_level:
            level_factor = 1.0
        elif resume_level == jd_level - 1:
            level_factor = 0.75
        else:
            level_factor = 0.5

        # Combine
        final = (0.6 * semantic_sim) + (0.4 * level_factor)

        best_score = max(best_score, final)

    return best_score


def _flatten_descriptions(items, attr="description"):
    """Flatten list-of-lists descriptions into a single list of strings."""
    result = []
    for item in items:
        desc = getattr(item, attr, None) if hasattr(item, attr) else item.get(attr, None)
        if isinstance(desc, list):
            result.extend(desc)
        elif desc:
            result.append(desc)
    return result


def full_semantic_score(resume: ResumeSchema, jd: JDRequirements):

    jd_text = " ".join(jd.responsibilities)

    # Build comprehensive resume text including achievements
    resume_parts = [resume.summary]
    resume_parts.extend(resume.skills)
    resume_parts.extend(_flatten_descriptions(resume.experience))
    resume_parts.extend(
        bullet
        for proj in resume.projects
        for bullet in (proj.description if isinstance(proj.description, list) else [proj.description])
    )
    # Include achievements in semantic scoring
    if resume.achievements:
        resume_parts.extend(resume.achievements)

    resume_text = " ".join(resume_parts)

    emb1 = model.encode([jd_text])
    emb2 = model.encode([resume_text])

    return float(cosine_similarity(emb1, emb2)[0][0])

def calculate_final_ats(resume: ResumeSchema, jd: JDRequirements):

    hard_score, matched, missing = embedding_hard_skill_score(resume, jd)
    pref_score = embedding_preferred_skill_score(resume, jd)
    exp_score, total_years, skill_years = embedding_experience_score(resume, jd)
    edu_score = embedding_based_education_score(resume, jd)
    sem_score = full_semantic_score(resume, jd)

    final_score = (
        hard_score * 35 +
        pref_score * 10 +
        exp_score * 20 +
        edu_score * 10 +
        sem_score * 25
    )

    return {
        "ATS_score": round(float(final_score), 2),
        "matched_required_skills": matched,
        "missing_required_skills": missing,
        "total_experience_years": round(total_years, 2),
        "component_breakdown": {
            "hard_skills": hard_score,
            "preferred_skills": pref_score,
            "experience": exp_score,
            "education": edu_score,
            "semantic_alignment": sem_score
        }
    }