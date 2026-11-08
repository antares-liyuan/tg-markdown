# -*- coding: utf-8 -*-
"""Markdown → Telegram HTML (parse_mode="HTML"), zero dependencies.

Why HTML instead of Telegram's MarkdownV2: MarkdownV2 requires escaping _ * [ ] ( ) ~ ` > # + - = | { } . !
everywhere; one miss and the whole message is rejected with HTTP 400. Text written by people or LLMs can't
guarantee that. HTML mode only needs & < > escaped, which is far more robust.

Supports: **bold** / __bold__ / `code` / [text](https://link) / # headings → bold / - * + lists → • /
> quotes → <blockquote> / ``` code blocks → <pre> / tables → aligned monospace <pre> (Telegram has no tables) /
--- rules → a line.
to_plain(): strip Markdown symbols for a plain-text fallback when Telegram still rejects the HTML.
split_html_safe(): split by source lines so a chunk never cuts through a tag, table or code block.
"""
import html, re, unicodedata

_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
_BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*|__(?=\S)(.+?)(?<=\S)__")
_CODE = re.compile(r"`([^`\n]+)`")


def _inline(t):
    """行内: 先把 `代码` 和链接摘出来占位, 再转义, 再处理粗体, 最后放回 —— 避免代码/链接里的符号被误处理。"""
    slots = []
    def keep(s):
        slots.append(s); return f"\x00{len(slots) - 1}\x00"
    t = _CODE.sub(lambda m: keep("<code>" + html.escape(m.group(1), quote=False) + "</code>"), t)
    t = _LINK.sub(lambda m: keep('<a href="' + html.escape(m.group(2), quote=True) + '">' + html.escape(m.group(1), quote=False) + "</a>"), t)
    t = html.escape(t, quote=False)
    t = _BOLD.sub(lambda m: "<b>" + (m.group(1) or m.group(2)) + "</b>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m.group(1))], t)


def _width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def _table(rows):
    rows = [[re.sub(r"\*\*|__|`", "", c).strip() for c in r] for r in rows]
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    w = [max(_width(r[i]) for r in rows) for i in range(n)]
    out = [" │ ".join(c + " " * (w[i] - _width(c)) for i, c in enumerate(r)).rstrip() for r in rows]
    if len(out) > 1:
        out.insert(1, "─┼─".join("─" * x for x in w))
    return "<pre>" + html.escape("\n".join(out), quote=False) + "</pre>"


def to_html(md):
    lines = (md or "").split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            buf = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            out.append("<pre>" + html.escape("\n".join(buf), quote=False) + "</pre>"); i += 1; continue
        if s.startswith("|") and s.count("|") >= 2:
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"\s*:?-{2,}:?\s*", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows: out.append(_table(rows))
            continue
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(_inline(lines[i].strip().lstrip(">").strip())); i += 1
            out.append("<blockquote>" + "\n".join(buf) + "</blockquote>"); continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            out.append("<b>" + _inline(m.group(2)) + "</b>")
        elif re.fullmatch(r"-{3,}|\*{3,}|_{3,}", s):
            out.append("────────")
        else:
            m = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
            out.append((m.group(1) + "• " + _inline(m.group(2))) if m else _inline(line))
        i += 1
    return "\n".join(out)


def to_plain(md):
    t = re.sub(r"```.*?\n|```", "", md or "")
    t = _LINK.sub(lambda m: f"{m.group(1)} {m.group(2)}", t)
    t = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), t)
    t = _CODE.sub(r"\1", t)
    t = re.sub(r"(?m)^#{1,6}\s+", "", t)
    t = re.sub(r"(?m)^(\s*)[-*+]\s+", r"\1• ", t)
    t = re.sub(r"(?m)^>\s?", "", t)
    t = re.sub(r"(?m)^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$\n?", "", t)
    return t


def split_html_safe(md, limit=3800):
    """按源文行切块(不在标签中间切), 每块单独转 HTML 后都不超过 limit。超长单行退化成纯文本截断。"""
    chunks, cur = [], []
    for line in (md or "").split("\n"):
        trial = "\n".join(cur + [line])
        if cur and len(to_html(trial)) > limit:
            chunks.append("\n".join(cur)); cur = [line]
        else:
            cur.append(line)
    if cur: chunks.append("\n".join(cur))
    return chunks
