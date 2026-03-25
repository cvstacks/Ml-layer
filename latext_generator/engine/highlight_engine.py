from difflib import SequenceMatcher


def diff_words(old, new):
    """
    Returns word-level differences between old and new text.
    Each result item has 'word' and 'type' (same/added/removed).
    """

    old_words = old.split()
    new_words = new.split()

    matcher = SequenceMatcher(None, old_words, new_words)

    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":

            result.extend([
                {"word": w, "type": "same"}
                for w in old_words[i1:i2]
            ])

        elif tag == "delete":

            result.extend([
                {"word": w, "type": "removed"}
                for w in old_words[i1:i2]
            ])

        elif tag == "insert":

            result.extend([
                {"word": w, "type": "added"}
                for w in new_words[j1:j2]
            ])

        elif tag == "replace":

            result.extend([
                {"word": w, "type": "removed"}
                for w in old_words[i1:i2]
            ])

            result.extend([
                {"word": w, "type": "added"}
                for w in new_words[j1:j2]
            ])

    return result


# ---------------------------
# HTML HIGHLIGHT (for web preview)
# ---------------------------

def build_highlight_html(old, new):
    """
    Generates HTML with highlights for web-based preview.
    - Green background for added words
    - Red strikethrough for removed words
    """

    if old == new:
        return new

    tokens = diff_words(old, new)

    html = []

    for token in tokens:

        if token["type"] == "same":
            html.append(token["word"])

        elif token["type"] == "added":
            html.append(
                f"<span class='added'>{token['word']}</span>"
            )

        elif token["type"] == "removed":
            html.append(
                f"<span class='removed'>{token['word']}</span>"
            )

    return " ".join(html)


# ---------------------------
# LATEX HIGHLIGHT (for PDF preview)
# ---------------------------

# Marker tokens to protect highlight commands from LaTeX escaping.
# These are replaced AFTER escaping, so the LaTeX commands survive.
_ADDED_OPEN = "%%HLADD%%"
_ADDED_CLOSE = "%%/HLADD%%"
_REMOVED_OPEN = "%%HLREM%%"
_REMOVED_CLOSE = "%%/HLREM%%"


def _escape_word_for_latex(word):
    """
    Escape special LaTeX characters in a single word.
    This is a lightweight version used inside highlight building
    so that the highlighted text is safe for LaTeX rendering.
    """
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
        word = word.replace(k, v)

    return word


def build_highlight_latex(old, new):
    """
    Generates LaTeX markup with highlights for PDF preview.

    - Added words:   \\textcolor{ForestGreen}{word}
    - Removed words: \\sout{\\textcolor{red}{word}}
    - Same words:    plain text

    Uses marker tokens that are converted to real LaTeX commands
    AFTER the main escape_latex pass, so they survive escaping.
    """

    if old == new:
        return new

    tokens = diff_words(old, new)

    parts = []

    for token in tokens:
        word = _escape_word_for_latex(token["word"])

        if token["type"] == "same":
            parts.append(word)

        elif token["type"] == "added":
            parts.append(f"{_ADDED_OPEN}{word}{_ADDED_CLOSE}")

        elif token["type"] == "removed":
            parts.append(f"{_REMOVED_OPEN}{word}{_REMOVED_CLOSE}")

    return " ".join(parts)


def resolve_highlight_markers(text):
    """
    Converts marker tokens into real LaTeX highlight commands.
    Call this AFTER escape_latex() has been applied to the full document,
    so that the markers survive escaping and become valid LaTeX.
    """
    if not isinstance(text, str):
        return text

    text = text.replace(_ADDED_OPEN, r"\textcolor{ForestGreen}{")
    text = text.replace(_ADDED_CLOSE, "}")
    text = text.replace(_REMOVED_OPEN, r"\sout{\textcolor{red}{")
    text = text.replace(_REMOVED_CLOSE, "}}")

    return text