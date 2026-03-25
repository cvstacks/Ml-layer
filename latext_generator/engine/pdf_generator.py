import subprocess
import os
import re


def remove_highlights(text):
    """
    Removes HTML highlight tags before LaTeX generation.
    Also removes any residual LaTeX highlight markers.
    """
    if not isinstance(text, str):
        return text

    # Remove HTML tags
    clean_text = re.sub(r"<.*?>", "", text)

    # Remove LaTeX highlight markers (in case they weren't resolved)
    clean_text = clean_text.replace("%%HLADD%%", "")
    clean_text = clean_text.replace("%%/HLADD%%", "")
    clean_text = clean_text.replace("%%HLREM%%", "")
    clean_text = clean_text.replace("%%/HLREM%%", "")

    return clean_text


def clean_resume_json(resume_json):
    """
    Remove all highlight markup (HTML and LaTeX markers) from entire resume.
    Used before generating the final clean PDF for download.
    """

    cleaned = resume_json.copy()

    # Clean summary
    cleaned["summary"] = remove_highlights(cleaned.get("summary", ""))

    # Clean projects
    for project in cleaned.get("projects", []):
        project["title"] = remove_highlights(project.get("title", ""))
        project["description"] = [
            remove_highlights(d) for d in project.get("description", [])
        ]

    # Clean experience descriptions (List[str])
    for exp in cleaned.get("experience", []):
        exp["role"] = remove_highlights(exp.get("role", ""))
        exp["company"] = remove_highlights(exp.get("company", ""))

        desc = exp.get("description", [])
        if isinstance(desc, list):
            exp["description"] = [remove_highlights(d) for d in desc]
        elif isinstance(desc, str):
            exp["description"] = [remove_highlights(desc)]

    # Clean achievements
    cleaned["achievements"] = [
        remove_highlights(a) for a in cleaned.get("achievements", [])
    ]

    # Clean certifications
    cleaned["certifications"] = [
        remove_highlights(c) for c in cleaned.get("certifications", [])
    ]

    # Clean skills
    cleaned["skills"] = [
        remove_highlights(s) for s in cleaned.get("skills", [])
    ]

    # Remove internal keys
    cleaned.pop("_skills_highlighted", None)

    return cleaned


def generate_pdf(tex_file, output_dir="."):
    """
    Compile LaTeX to PDF using pdflatex.
    """

    try:

        subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                tex_file
            ],
            cwd=output_dir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    except subprocess.CalledProcessError as e:

        print("PDF generation failed")
        if e.stderr:
            print(e.stderr.decode())
        if e.stdout:
            # pdflatex often writes errors to stdout
            stdout_text = e.stdout.decode()
            # Print only the last 20 lines for brevity
            lines = stdout_text.strip().split("\n")
            print("\n".join(lines[-20:]))

        raise

    pdf_file = tex_file.replace(".tex", ".pdf")

    return pdf_file


def compile_resume(tex_file):
    """
    Complete compile pipeline.
    """

    if not os.path.exists(tex_file):
        raise FileNotFoundError(f"{tex_file} not found")

    pdf = generate_pdf(tex_file)

    return pdf