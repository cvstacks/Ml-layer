import os
import re
from copy import deepcopy
from jinja2 import Environment, FileSystemLoader
from latext_generator.engine.highlight_engine import resolve_highlight_markers


# LaTeX packages needed for highlight preview
HIGHLIGHT_PREAMBLE = r"""
\usepackage[normalem]{ulem}
\usepackage{xcolor}
"""


class ResumeRenderer:

    def __init__(self, template_dir="templates"):

        self.template_dir = template_dir

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False
        )

    def render_resume(self, resume_json, template_name="ats_classic.tex", mode="download"):
        """
        Render resume to LaTeX.

        mode:
            "download" — clean PDF, full escaping, no highlights
            "preview"  — highlighted PDF, highlight markers resolved to LaTeX commands
        """

        # Deep copy to avoid mutating the original
        resume_data = deepcopy(resume_json)

        if mode == "preview":
            # Resolve highlight markers into LaTeX commands BEFORE escaping
            resume_data = resolve_all_highlights(resume_data)
            # Then sanitize but preserve highlight commands
            resume_data = sanitize_resume_preserve_highlights(resume_data)
        else:
            # Standard full sanitization
            resume_data = sanitize_resume(resume_data)

        template = self.env.get_template(template_name)

        latex_content = template.render(resume=resume_data)

        # In preview mode, inject highlight packages into preamble
        if mode == "preview":
            latex_content = inject_highlight_preamble(latex_content)

        return latex_content


    def save_latex(self, latex_content, output_path):

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(latex_content)

        return output_path


def render_to_tex(resume_json, template="ats_classic.tex", output_path="output.tex", mode="download"):
    """
    Render resume JSON to a .tex file.

    mode: "download" (clean) or "preview" (with highlights)
    """

    renderer = ResumeRenderer()

    latex = renderer.render_resume(resume_json, template, mode=mode)

    renderer.save_latex(latex, output_path)

    return output_path


def inject_highlight_preamble(latex_content):
    """
    Inject highlight-related LaTeX packages into the document preamble.
    Inserts after \\begin{document} is found, we place the packages
    right before it.
    """
    marker = r"\begin{document}"

    if marker in latex_content:
        latex_content = latex_content.replace(
            marker,
            HIGHLIGHT_PREAMBLE + "\n" + marker
        )

    return latex_content


# ---------------------------
# LATEX SAFETY FUNCTIONS
# ---------------------------

def escape_latex(text):

    if not isinstance(text, str):
        return text

    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


def escape_latex_preserve_highlights(text):
    """
    Escape LaTeX special characters but preserve highlight commands.
    Highlight commands use \\textcolor, \\sout, \\ForestGreen, etc.
    We protect them by temporarily replacing them, escaping, then restoring.
    """
    if not isinstance(text, str):
        return text

    # Protect highlight commands by extracting them
    # Pattern matches: \textcolor{...}{...} and \sout{...}
    protected = []
    counter = [0]

    def protect(match):
        placeholder = f"%%PROTECT{counter[0]}%%"
        protected.append((placeholder, match.group(0)))
        counter[0] += 1
        return placeholder

    # Protect \textcolor{...}{...} (including nested \textcolor inside \sout)
    text = re.sub(
        r'\\sout\{\\textcolor\{[^}]+\}\{[^}]*\}\}',
        protect, text
    )
    text = re.sub(
        r'\\textcolor\{[^}]+\}\{[^}]*\}',
        protect, text
    )

    # Now escape the remaining text
    text = escape_latex(text)

    # Restore protected commands
    for placeholder, original in protected:
        text = text.replace(placeholder, original)

    return text


def resolve_all_highlights(resume):
    """
    Walk through all text fields in the resume and resolve
    highlight markers into actual LaTeX commands.
    """
    resume["summary"] = resolve_highlight_markers(resume.get("summary", ""))

    resume["skills"] = [
        resolve_highlight_markers(s) for s in resume.get("skills", [])
    ]

    for exp in resume.get("experience", []):
        exp["role"] = resolve_highlight_markers(exp.get("role", ""))
        exp["company"] = resolve_highlight_markers(exp.get("company", ""))
        desc = exp.get("description", [])
        if isinstance(desc, list):
            exp["description"] = [resolve_highlight_markers(d) for d in desc]

    for project in resume.get("projects", []):
        project["title"] = resolve_highlight_markers(project.get("title", ""))
        project["description"] = [
            resolve_highlight_markers(d) for d in project.get("description", [])
        ]

    resume["achievements"] = [
        resolve_highlight_markers(a) for a in resume.get("achievements", [])
    ]

    resume["certifications"] = [
        resolve_highlight_markers(c) for c in resume.get("certifications", [])
    ]

    # Handle highlighted skills string if present
    if "_skills_highlighted" in resume:
        resume["_skills_highlighted"] = resolve_highlight_markers(
            resume["_skills_highlighted"]
        )

    return resume


def sanitize_resume(resume):
    """Full sanitization for download mode — escape everything."""

    resume["name"] = escape_latex(resume.get("name", ""))
    resume["email"] = escape_latex(resume.get("email", ""))
    resume["phone"] = escape_latex(resume.get("phone", ""))

    resume["summary"] = escape_latex(resume.get("summary", ""))

    resume["skills"] = [
        escape_latex(s) for s in resume.get("skills", [])
    ]

    for exp in resume.get("experience", []):
        exp["company"] = escape_latex(exp.get("company", ""))
        exp["role"] = escape_latex(exp.get("role", ""))
        exp["start_date"] = escape_latex(exp.get("start_date", ""))
        exp["end_date"] = escape_latex(exp.get("end_date", ""))

        desc = exp.get("description", [])
        if isinstance(desc, list):
            exp["description"] = [escape_latex(d) for d in desc]
        elif isinstance(desc, str):
            exp["description"] = [escape_latex(desc)]
        else:
            exp["description"] = []

    for project in resume.get("projects", []):
        project["title"] = escape_latex(project.get("title", ""))
        project["description"] = [
            escape_latex(d) for d in project.get("description", [])
        ]

    for edu in resume.get("education", []):
        edu["institution"] = escape_latex(edu.get("institution", ""))
        edu["degree"] = escape_latex(edu.get("degree", ""))
        edu["year"] = escape_latex(edu.get("year", ""))

    resume["achievements"] = [
        escape_latex(a) for a in resume.get("achievements", [])
    ]

    resume["certifications"] = [
        escape_latex(c) for c in resume.get("certifications", [])
    ]

    return resume


def sanitize_resume_preserve_highlights(resume):
    """
    Sanitization for preview mode — escape LaTeX specials but
    preserve highlight commands (\\textcolor, \\sout).
    """

    esc = escape_latex_preserve_highlights

    resume["name"] = escape_latex(resume.get("name", ""))
    resume["email"] = escape_latex(resume.get("email", ""))
    resume["phone"] = escape_latex(resume.get("phone", ""))

    resume["summary"] = esc(resume.get("summary", ""))

    resume["skills"] = [
        esc(s) for s in resume.get("skills", [])
    ]

    for exp in resume.get("experience", []):
        exp["company"] = esc(exp.get("company", ""))
        exp["role"] = esc(exp.get("role", ""))
        exp["start_date"] = escape_latex(exp.get("start_date", ""))
        exp["end_date"] = escape_latex(exp.get("end_date", ""))

        desc = exp.get("description", [])
        if isinstance(desc, list):
            exp["description"] = [esc(d) for d in desc]
        elif isinstance(desc, str):
            exp["description"] = [esc(desc)]
        else:
            exp["description"] = []

    for project in resume.get("projects", []):
        project["title"] = esc(project.get("title", ""))
        project["description"] = [
            esc(d) for d in project.get("description", [])
        ]

    for edu in resume.get("education", []):
        edu["institution"] = escape_latex(edu.get("institution", ""))
        edu["degree"] = escape_latex(edu.get("degree", ""))
        edu["year"] = escape_latex(edu.get("year", ""))

    resume["achievements"] = [
        esc(a) for a in resume.get("achievements", [])
    ]

    resume["certifications"] = [
        esc(c) for c in resume.get("certifications", [])
    ]

    # Handle highlighted skills display string
    if "_skills_highlighted" in resume:
        resume["_skills_highlighted"] = esc(resume["_skills_highlighted"])

    return resume