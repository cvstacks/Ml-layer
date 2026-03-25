from copy import deepcopy
from latext_generator.engine.highlight_engine import build_highlight_html, build_highlight_latex


def _build_preview_generic(original_resume, improved_resume, highlight_fn):
    """
    Core preview builder that applies a highlight function to all sections.

    highlight_fn: either build_highlight_html (for web) or build_highlight_latex (for PDF)
    """

    preview = deepcopy(improved_resume)

    # Summary highlight
    if "summary" in original_resume and "summary" in improved_resume:
        preview["summary"] = highlight_fn(
            original_resume["summary"],
            improved_resume["summary"]
        )

    # Skills highlight (detect reordering / additions / removals)
    original_skills = original_resume.get("skills", [])
    improved_skills = improved_resume.get("skills", [])
    if original_skills != improved_skills:
        old_skills_str = ", ".join(original_skills)
        new_skills_str = ", ".join(improved_skills)
        preview["_skills_highlighted"] = highlight_fn(old_skills_str, new_skills_str)

    # Projects highlight
    preview_projects = []

    for i, project in enumerate(improved_resume.get("projects", [])):

        original_projects = original_resume.get("projects", [])
        original_project = original_projects[i] if i < len(original_projects) else {}

        new_project = project.copy()

        # Highlight descriptions
        highlighted_desc = []
        for j, sentence in enumerate(project.get("description", [])):
            try:
                old_sentence = original_project.get("description", [])[j]
            except IndexError:
                old_sentence = ""

            highlighted_desc.append(highlight_fn(old_sentence, sentence))

        new_project["description"] = highlighted_desc

        # Highlight project title if changed
        old_title = original_project.get("title", "")
        new_title = project.get("title", "")
        if old_title != new_title:
            new_project["title"] = highlight_fn(old_title, new_title)

        preview_projects.append(new_project)

    preview["projects"] = preview_projects

    # Experience highlight
    preview_experience = []

    for i, exp in enumerate(improved_resume.get("experience", [])):

        original_exps = original_resume.get("experience", [])
        original_exp = original_exps[i] if i < len(original_exps) else {}

        new_exp = exp.copy()

        # Highlight experience descriptions (List[str])
        highlighted_desc = []
        for j, bullet in enumerate(exp.get("description", [])):
            try:
                old_bullet = original_exp.get("description", [])[j]
            except (IndexError, AttributeError):
                old_bullet = ""

            highlighted_desc.append(highlight_fn(old_bullet, bullet))

        new_exp["description"] = highlighted_desc

        # Highlight role if changed
        old_role = original_exp.get("role", "")
        new_role = exp.get("role", "")
        if old_role != new_role:
            new_exp["role"] = highlight_fn(old_role, new_role)

        preview_experience.append(new_exp)

    preview["experience"] = preview_experience

    # Achievements highlight
    preview_achievements = []
    original_achievements = original_resume.get("achievements", [])
    improved_achievements = improved_resume.get("achievements", [])

    for j, achievement in enumerate(improved_achievements):
        old_ach = original_achievements[j] if j < len(original_achievements) else ""
        preview_achievements.append(highlight_fn(old_ach, achievement))

    preview["achievements"] = preview_achievements

    return preview


def build_preview(original_resume, improved_resume):
    """
    Builds a preview resume with HTML highlighted improvements.
    For web-based preview (JSON API response).
    """
    return _build_preview_generic(original_resume, improved_resume, build_highlight_html)


def build_preview_latex(original_resume, improved_resume):
    """
    Builds a preview resume with LaTeX highlighted improvements.
    For PDF preview generation.
    """
    return _build_preview_generic(original_resume, improved_resume, build_highlight_latex)