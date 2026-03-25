from latext_generator.preview.preview_builder import build_preview, build_preview_latex
from latext_generator.engine.change_resolver import resolve_resume
from latext_generator.engine.renderer import render_to_tex
from latext_generator.engine.pdf_generator import compile_resume, clean_resume_json


def generate_preview_html(original_resume, improved_resume):
    """
    Generate HTML preview JSON with highlighted changes.
    Returns a resume dict with HTML highlight tags in text fields.
    For web-based frontends.
    """
    return build_preview(original_resume, improved_resume)


def generate_preview_pdf(original_resume, improved_resume, template="universal_pro.tex",
                         output_path="preview.tex"):
    """
    Generate a highlighted preview PDF.
    Changes are shown as:
      - Green text: added words
      - Red strikethrough: removed words

    Returns the path to the compiled PDF.
    """

    # Build resume with LaTeX highlight markers
    preview_resume = build_preview_latex(original_resume, improved_resume)

    # Render to LaTeX in preview mode (injects highlight packages, preserves commands)
    tex_file = render_to_tex(
        preview_resume,
        template=template,
        output_path=output_path,
        mode="preview"
    )

    # Compile to PDF
    pdf_file = compile_resume(tex_file)

    return pdf_file


def generate_final_pdf(improved_resume, original_resume=None, decisions=None,
                       template="universal_pro.tex", output_path="resume.tex"):
    """
    Generate a clean final PDF resume (no highlights).

    Steps:
      1. Apply accept/reject decisions
      2. Remove any residual HTML highlight tags
      3. Render clean LaTeX
      4. Compile to PDF

    Returns the path to the compiled PDF.
    """

    # Apply accept / reject decisions
    resolved_resume = resolve_resume(improved_resume, original_resume, decisions)

    # Remove any residual highlight tags (HTML)
    clean_resume = clean_resume_json(resolved_resume)

    # Render LaTeX in download mode (clean, no highlights)
    tex_file = render_to_tex(
        clean_resume,
        template=template,
        output_path=output_path,
        mode="download"
    )

    # Compile PDF
    pdf_file = compile_resume(tex_file)

    return pdf_file


def full_pipeline(original_resume, improved_resume, template="universal_pro.tex"):
    """
    Full pipeline: generates both preview and final PDFs.

    Returns:
        (preview_pdf_path, final_pdf_path)
    """

    print("Step 1/3: Building HTML preview...")
    html_preview = generate_preview_html(original_resume, improved_resume)

    print("Step 2/3: Generating preview PDF with highlights...")
    preview_pdf = generate_preview_pdf(
        original_resume,
        improved_resume,
        template=template,
        output_path="preview.tex"
    )
    print(f"  Preview PDF: {preview_pdf}")

    print("Step 3/3: Generating final clean PDF...")
    final_pdf = generate_final_pdf(
        improved_resume,
        original_resume=original_resume,
        decisions={},
        template=template,
        output_path="resume.tex"
    )
    print(f"  Final PDF: {final_pdf}")

    return {
        "html_preview": html_preview,
        "preview_pdf": preview_pdf,
        "final_pdf": final_pdf
    }