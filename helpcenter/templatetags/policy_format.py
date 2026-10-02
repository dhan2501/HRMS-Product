"""
Turns the lightweight markdown-style text produced by helpcenter/extraction.py
into real, nicely laid-out HTML — headings become <h3>/<h4>, consecutive
bullet lines become one <ul>, consecutive numbered lines become one <ol>,
and everything else becomes properly spaced <p> paragraphs. This is what
makes an imported PDF/DOCX auto-arrange itself on the Help page instead of
showing up as one dense block of text.
"""

import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

H1_RE       = re.compile(r'^#\s+(.*)')
H2_RE       = re.compile(r'^##\s+(.*)')
BULLET_RE   = re.compile(r'^-\s+(.*)')
NUMBERED_RE = re.compile(r'^\d+[\.\)]\s+(.*)')


@register.filter(name='render_policy_text', is_safe=True)
def render_policy_text(text):
    if not text:
        return ''

    lines = text.replace('\r\n', '\n').split('\n')

    html_parts  = []
    para_buffer = []
    list_buffer = []
    list_type   = [None]  # 'ul' or 'ol' — list so the nested helpers can mutate it

    def flush_para():
        if para_buffer:
            joined = ' '.join(l.strip() for l in para_buffer if l.strip())
            if joined:
                html_parts.append(f'<p class="mb-3 leading-relaxed">{escape(joined)}</p>')
            para_buffer.clear()

    def flush_list():
        if list_buffer:
            tag = list_type[0] or 'ul'
            cls = 'list-disc' if tag == 'ul' else 'list-decimal'
            items = ''.join(f'<li class="mb-1 pl-1">{escape(item)}</li>' for item in list_buffer)
            html_parts.append(f'<{tag} class="{cls} pl-5 mb-4 space-y-1 marker:text-brand-400">{items}</{tag}>')
            list_buffer.clear()
        list_type[0] = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            flush_para()
            flush_list()
            continue

        m = H1_RE.match(line)
        if m:
            flush_para(); flush_list()
            html_parts.append(
                f'<h3 class="text-slate-800 font-bold text-base mt-5 mb-2 first:mt-0 pb-1.5 border-b border-slate-100">{escape(m.group(1))}</h3>'
            )
            continue

        m = H2_RE.match(line)
        if m:
            flush_para(); flush_list()
            html_parts.append(
                f'<h4 class="text-slate-700 font-semibold text-sm mt-4 mb-1.5">{escape(m.group(1))}</h4>'
            )
            continue

        m = BULLET_RE.match(line)
        if m:
            flush_para()
            if list_type[0] == 'ol':
                flush_list()
            list_type[0] = 'ul'
            list_buffer.append(m.group(1))
            continue

        m = NUMBERED_RE.match(line)
        if m:
            flush_para()
            if list_type[0] == 'ul':
                flush_list()
            list_type[0] = 'ol'
            list_buffer.append(m.group(1))
            continue

        flush_list()
        para_buffer.append(line)

    flush_para()
    flush_list()

    return mark_safe(''.join(html_parts))