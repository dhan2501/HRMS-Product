"""
Auto-extracts text from an uploaded policy file (PDF or DOCX) so the admin
never has to retype the content by hand — AND auto-detects the document's
structure (headings, bullet points, numbered lists, plain paragraphs) so it
renders as a properly laid-out document instead of one wall of text,
regardless of whether the source was list-heavy or paragraph-heavy.

The extracted text uses a lightweight markdown-style notation that
`helpcenter/templatetags/policy_format.py` turns into real HTML:
    "# "   -> top-level heading
    "## "  -> sub heading
    "- "   -> bullet list item
    "1. "  -> numbered list item
    blank line -> paragraph / block break

Returns (extracted_text, note) — note is empty on success, or a short
explanation if extraction failed / the format isn't supported.
"""

import re

BULLET_CHARS = ('•', '●', '▪', '‣', '◦', '·', '*', '-')
NUMBERED_LINE_RE = re.compile(r'^(\d+)[\.\)]\s+(.*)')


def extract_text_from_file(django_file):
    if not django_file:
        return '', ''

    name = django_file.name.lower()

    try:
        if name.endswith('.pdf'):
            text, note = _extract_pdf(django_file)
        elif name.endswith('.docx'):
            text, note = _extract_docx(django_file)
        elif name.endswith('.doc'):
            return '', "Old .doc format isn't supported for auto-extraction — please re-save as .docx or .pdf, or add notes manually below."
        elif name.endswith('.txt'):
            text, note = _extract_txt(django_file)
        else:
            return '', 'Unsupported file type for auto text extraction. Supported: PDF, DOCX, TXT.'
    except Exception as e:
        return '', f'Could not extract text automatically ({e}). The file is still saved and downloadable.'

    if text:
        text = _apply_heading_heuristic(text)
    return text, note


def _normalize_bullets_and_numbers(line):
    """
    Turn a raw bullet character or numbered-list marker at the start of a
    line into the '- ' / '1. ' notation the renderer understands.
    """
    stripped = line.strip()
    if not stripped:
        return ''

    for ch in BULLET_CHARS:
        if stripped.startswith(ch + ' '):
            rest = stripped[len(ch):].strip()
            if rest:
                return f'- {rest}'

    m = NUMBERED_LINE_RE.match(stripped)
    if m:
        return f'{m.group(1)}. {m.group(2)}'

    return stripped


def _apply_heading_heuristic(text):
    """
    Best-effort: short, punctuation-free standalone lines are treated as
    section headings (marked '## ') so they render bold/larger instead of
    blending into the surrounding paragraph text. Lines that already carry
    a heading/bullet/number marker are left untouched.
    """
    lines = text.split('\n')
    out = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#') or line.startswith('- ') or NUMBERED_LINE_RE.match(line):
            out.append(raw)
            continue

        word_count = len(line.split())
        looks_like_heading = (
            0 < word_count <= 8
            and not line.endswith(('.', ',', ';', ':', '?', '!'))
            and len(line) <= 70
        )
        out.append(f'## {line}' if looks_like_heading else raw)
    return '\n'.join(out)


def _extract_pdf(django_file):
    try:
        from pypdf import PdfReader
    except ImportError:
        return '', "PDF extraction needs the 'pypdf' package. Run: pip install pypdf"

    django_file.seek(0)
    reader = PdfReader(django_file)
    pages = []
    for page in reader.pages:
        raw = page.extract_text() or ''
        if raw.strip():
            normalized_lines = [_normalize_bullets_and_numbers(l) for l in raw.split('\n')]
            pages.append('\n'.join(normalized_lines).strip())
    full_text = '\n\n'.join(pages).strip()

    if not full_text:
        return '', 'No selectable text found in this PDF (it may be a scanned image). The file is still saved and downloadable.'
    return full_text, ''


def _extract_docx(django_file):
    try:
        import docx
    except ImportError:
        return '', "DOCX extraction needs the 'python-docx' package. Run: pip install python-docx"

    django_file.seek(0)
    document = docx.Document(django_file)
    parts = []

    for para in document.paragraphs:
        text = para.text.strip()
        if not text:
            parts.append('')
            continue

        style_name = (para.style.name if para.style else '') or ''
        style_lower = style_name.lower()

        if 'title' in style_lower or 'heading 1' in style_lower:
            parts.append(f'# {text}')
        elif 'heading' in style_lower:
            parts.append(f'## {text}')
        elif 'list bullet' in style_lower:
            parts.append(f'- {text}')
        elif 'list number' in style_lower:
            parts.append(f'1. {text}')
        elif 'list paragraph' in style_lower and text[:1] in BULLET_CHARS:
            parts.append(_normalize_bullets_and_numbers(text))
        else:
            # Normal body paragraph — force a break after it so each Word
            # paragraph renders as its own <p>, instead of merging with
            # the next one.
            parts.append(_normalize_bullets_and_numbers(text))
            parts.append('')

    # Also pull text out of any tables in the doc (rendered as a bullet list
    # of rows — simple and readable without needing real <table> markup)
    for table in document.tables:
        parts.append('')
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append('- ' + ' | '.join(cells))
        parts.append('')

    full_text = '\n'.join(parts).strip()
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)  # collapse big gaps
    if not full_text:
        return '', 'No text found in this document.'
    return full_text, ''


def _extract_txt(django_file):
    django_file.seek(0)
    raw = django_file.read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('latin-1', errors='ignore')
    normalized_lines = [_normalize_bullets_and_numbers(l) for l in text.split('\n')]
    return '\n'.join(normalized_lines).strip(), ''