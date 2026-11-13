"""Small helpers for authoring slide HTML: code blocks, tables, cards, fragments."""
from html import escape
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

_fmt = HtmlFormatter(style="github-dark", nowrap=True)
PYGMENTS_CSS = HtmlFormatter(style="github-dark").get_style_defs(".code pre")


def code(src, lang="java", title=None, step=None, size=None):
    body = highlight(src.strip("\n"), get_lexer_by_name(lang), _fmt)
    head = f'<div class="code-title">{escape(title)}</div>' if title else ""
    style = f' style="font-size:{size}px"' if size else ""
    return frag(f'<div class="code">{head}<pre{style}>{body}</pre></div>', step)


def frag(inner, step=None, tag="div", cls=""):
    if step is None:
        return f'<{tag} class="{cls}">{inner}</{tag}>' if cls else inner
    return f'<{tag} class="frag {cls}" data-step="{step}">{inner}</{tag}>'


def md(text):
    """Tiny inline markup: `code`, **bold**."""
    import re
    t = escape(text)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t.replace("\n", "<br>")


def bullets(items, start_step=None, cls="bullets"):
    """items: list of str. If start_step is set, each bullet reveals on its own step."""
    lis = []
    for i, it in enumerate(items):
        s = None if start_step is None else start_step + i
        lis.append(f"<li>{md(it)}</li>" if s is None else frag(md(it), s, tag="li"))
    return f'<ul class="{cls}">{"".join(lis)}</ul>'


def table(head, rows, step_per_row=None, cls=""):
    th = "".join(f"<th>{md(h)}</th>" for h in head)
    trs = []
    for i, r in enumerate(rows):
        tds = "".join(f"<td>{md(c)}</td>" for c in r)
        if step_per_row is None:
            trs.append(f"<tr>{tds}</tr>")
        else:
            trs.append(f'<tr class="frag" data-step="{step_per_row + i}">{tds}</tr>')
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


def card(title, body, accent="indigo", step=None):
    return frag(f'<div class="card {accent}"><div class="card-h">{md(title)}</div>'
                f'<div class="card-b">{md(body)}</div></div>', step)


def flow(boxes, step_start=None, vertical=False):
    """A simple arrow diagram; each box can reveal on its own step."""
    parts = []
    for i, b in enumerate(boxes):
        s = None if step_start is None else step_start + i
        if i:
            parts.append(frag('<div class="arrow">' + ("↓" if vertical else "→") + "</div>", s))
        parts.append(frag(f'<div class="fbox">{md(b)}</div>', s))
    return f'<div class="flow {"v" if vertical else "h"}">{"".join(parts)}</div>'
