#!/usr/bin/env python3
"""Generate arckit-mcp/arckit_mcp/intake.py from template question blocks.

The generated module lives in the sibling arckit-mcp repo, not in this
tree. It is imported by the arckit-mcp server; do not edit it by hand.

Reads (pure Python/regex — no node in CI):

* the ``plugins/arckit-claude/config/doc-types.mjs`` DOC_TYPES object
  (the same source ``generate-mcp-registry.py`` consumes), and
* every ``## Intake Interview Questions`` block in the flat template tree
  (``plugins/{arckit-oaa,it4it,togaf-adm,agent-architecture}/templates/*.md``)
  and the nested duplicate tree
  (``plugins/arckit-claude/plugins/**/templates/*.md``),

then extracts, for each question block:

* the bold-bullet questions (any line starting with a list marker whose
  text is bold, or whose bolded leading token is followed by a colon);
* the MANDATORY-tier prerequisite doc-type codes of the command that
  produces the template's doc-type (the command mapping is
  template-filename-stem → command-filename-stem, which holds for every
  overlay template; MANDATORY tiers are parsed with the same
  conventions as ``generate-mcp-gates.py``).

Questions are **keyed by doc-type code**, resolved per template via the
front-matter ``docType:`` field, then the Document Control
``Document Type`` row (matched case-insensitively against the doc-types
names, e.g. ``Gap Analysis`` → ``GAPA``), then the filename stem
(normalised against the doc-types names). A template that resolves to
no code is recorded in ``PARSER_NOTES`` and excluded from the output
dicts.

Tree scan + dedup: the flat tree wins. A nested template whose doc-type
code is already covered by a flat template is discarded entirely. Scan
order is sorted by path, so output is byte-stable.

Usage:
    python scripts/generate-mcp-intake.py [output-path]

    The optional argument overrides the default output location
    (sibling arckit-mcp repo). The ARCKIT_MCP_ROOT env var also
    overrides the sibling-repo root.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

FLAT_TEMPLATE_GLOBS = [
    PLUGINS_DIR / "arckit-oaa" / "templates" / "*.md",
    PLUGINS_DIR / "arckit-it4it" / "templates" / "*.md",
    PLUGINS_DIR / "arckit-togaf-adm" / "templates" / "*.md",
    PLUGINS_DIR / "arckit-agent-architecture" / "templates" / "*.md",
]
NESTED_TEMPLATES_DIR = PLUGINS_DIR / "arckit-claude" / "plugins"
DOC_TYPES_MJS = PLUGINS_DIR / "arckit-claude" / "config" / "doc-types.mjs"

# Plugin dirs that ship commands with tiered prerequisite blocks (the
# same set generate-mcp-gates.py scans).
GATE_PLUGIN_DIRS = [
    PLUGINS_DIR / name
    for name in ("arckit-claude", "arckit-oaa", "arckit-it4it", "arckit-togaf-adm")
]

# ---------------------------------------------------------------------------
# doc-types.mjs parsing (same two-pass approach as generate-mcp-registry.py)
# ---------------------------------------------------------------------------


def _strip_comments(text: str) -> str:
    """Remove // and /* */ comments (naive, but safe for this file's style).

    Same approach as scripts/generate-mcp-registry.py.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _block(text: str, name: str) -> str:
    """Extract the full ``name = { ... }`` block of a flat JS object.

    Mirrors the block() helper in scripts/check-doc-type-registry.py:
    brace counting is safe because the DOC_TYPES values are flat
    single-line object literals with no nested braces.
    """
    m = re.search(rf"export\s+const\s+{re.escape(name)}\s*=\s*", text)
    if not m:
        raise SystemExit(f"doc-types.mjs: cannot find `export const {name}`")
    start = text.index("{", m.end() - 1)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise SystemExit(f"doc-types.mjs: unterminated block for {name}")


def _js_obj_to_json(block: str, name: str) -> dict:
    """Convert a JS object literal (single-quoted keys/values, trailing
    commas allowed) to a JSON object, then parse it.

    Two-pass scanner over the brace-walked block:
      1. Walk the text once, tracking in-string state (single-quoted JS
         string, including the possibility of an escaped apostrophe
         inside a value like 'l'analyse'), and rewrite every string
         literal to a double-quoted JSON string (escaping backslashes
         and embedded double quotes).
      2. In the same walk, whenever we see a bare identifier immediately
         followed by ``:`` and we are NOT inside a string, quote it.
         This catches nested keys (``name:``, ``category:``) that the
         regex approach could not safely reach, because it operates on
         the pre-string-rewritten text.
    """
    body = block.strip()
    assert body[0] == "{" and body[-1] == "}", f"unexpected block for {name}"
    body = body[1:-1]

    out: list[str] = []
    i = 0
    n = len(body)
    IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9-]*")
    while i < n:
        c = body[i]
        if c in "'\"":
            # Quoted string. Walk to the matching closing quote, handling
            # backslash escapes. Standard JSON escapes pass through
            # unchanged; any other backslash-escape is preserved as a
            # backslash escape so it round-trips as JSON.
            j = i + 1
            buf = []
            while j < n:
                ch = body[j]
                if ch == "\\" and j + 1 < n:
                    esc = body[j + 1]
                    buf.append(esc if esc in '"\\bfnrt' else "\\" + esc)
                    j += 2
                    continue
                if ch == c:
                    break
                buf.append(ch)
                j += 1
            out.append('"' + "".join(buf) + '"')
            i = j + 1
            continue
        if c.isalpha() or c == "_":
            m = IDENT.match(body, i)
            if m:
                word = m.group(0)
                # Look ahead past whitespace to see if the identifier is
                # a key (followed by ``:``). If so, quote it; otherwise
                # leave it (should not happen in this file — all values
                # are strings or numbers).
                k = m.end()
                while k < n and body[k] in " \t":
                    k += 1
                if k < n and body[k] == ":":
                    out.append(f'"{word}"')
                else:
                    out.append(word)
                i = m.end()
                continue
        out.append(c)
        i += 1

    body = "".join(out)
    # Remove trailing commas (both inside nested objects and at the very
    # end of the top-level body, which would sit right before the
    # closing brace we re-wrap below).
    body = re.sub(r",\s*([}\]])", r"\1", body)
    body = re.sub(r",\s*$", "", body)
    try:
        return json.loads("{" + body + "}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"doc-types.mjs: cannot parse {name}: {e}")


def parse_doc_types() -> dict[str, dict]:
    text = _strip_comments(DOC_TYPES_MJS.read_text(encoding="utf-8"))
    return _js_obj_to_json(_block(text, "DOC_TYPES"), "DOC_TYPES")


# ---------------------------------------------------------------------------
# MANDATORY-tier prerequisite parsing (generate-mcp-gates.py conventions)
# ---------------------------------------------------------------------------

TIER_HEADER_RE = re.compile(r"^\s*(?:-\s+)?\*\*(MANDATORY|RECOMMENDED|OPTIONAL)\*\*")
HEADING_TIER_RE = re.compile(r"^\s*#+\s*(MANDATORY|RECOMMENDED|OPTIONAL)\b")
PLAIN_PREQ_RE = re.compile(r"^\s*#+\s*prerequisites", re.IGNORECASE)
TRAILING_CODE_RE = re.compile(r"(`|'|\()" r"(ARC[~-]\*?-\*?)([A-Z][A-Z0-9]{1,6})" r"-\*?(\.md)?[`'\)]")
BARE_CODE_RE = re.compile(r"^([A-Z][A-Z0-9]{1,6})\b(?!\s*[(`])")


def _clean_code(raw: str) -> str:
    c = raw.strip().lstrip("*").strip()
    if c.startswith("ARC"):
        c = c[3:]
    c = c.split("-")[0]
    return c if c else ""


def _bullet_code(line: str) -> str:
    m = re.match(r"^\s*(?:[-*]\s+)?\*\*([A-Za-z0-9*~-]+)\*\*", line)
    if m:
        code = _clean_code(m.group(1))
        if code and 2 <= len(code) <= 8 and code.isupper():
            return code
    m = TRAILING_CODE_RE.search(line)
    if m:
        return m.group(2)
    m = BARE_CODE_RE.match(line)
    if m and not line.lstrip("-* ").startswith("**"):
        code = m.group(1)
        if 2 <= len(code) <= 8:
            return code
    return ""


def mandatory_codes_for(commands: list[Path]) -> list[str]:
    """MANDATORY-tier codes across the given command files, in first-seen
    order (deduped). Reuses the tier-block scan of generate-mcp-gates.py,
    but keeps only MANDATORY entries."""
    seen: list[str] = []
    for cmd in commands:
        if not cmd.is_file():
            continue
        lines = cmd.read_text(encoding="utf-8").splitlines()
        in_block = False
        current_tier: str | None = None
        for line in lines:
            h = TIER_HEADER_RE.match(line) or HEADING_TIER_RE.match(line)
            if h:
                in_block = True
                current_tier = h.group(1)
                continue
            if in_block:
                stripped = line.strip()
                if not stripped:
                    continue
                if TIER_HEADER_RE.match(line) or HEADING_TIER_RE.match(line) or PLAIN_PREQ_RE.match(line):
                    if PLAIN_PREQ_RE.match(line):
                        in_block = False
                        current_tier = None
                    continue
                if not stripped.startswith(("-", "*", " ")):
                    in_block = False
                    current_tier = None
                    continue
                code = _bullet_code(stripped)
                if code and current_tier == "MANDATORY":
                    if code not in seen:
                        seen.append(code)
            elif PLAIN_PREQ_RE.match(line):
                in_block = True
                current_tier = "MANDATORY"
    return seen


# ---------------------------------------------------------------------------
# Question-block parsing
# ---------------------------------------------------------------------------

QUESTION_BLOCK_RE = re.compile(r"^##\s+Intake Interview Questions\s*$")
FRONTMATTER_DOC_TYPE_RE = re.compile(r"^docType:\s*['\"]?([A-Z][A-Z0-9]{1,7})['\"]?")
DOC_CONTROL_RE = re.compile(r"^\|.*Document Type.*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)
BOLD_BULLET_RE = re.compile(r"^\s*[-*]\s+\*\*(.+?)\*\*(:|\s*$)")


def _extract_questions(text: str) -> list[str]:
    """Bold-bullet questions inside the ``## Intake Interview Questions``
    block. Tolerates prose, tables, and ``###`` subheaders around the
    bullets; stops at the next same-or-higher-level heading."""
    lines = text.splitlines()
    questions: list[str] = []
    in_block = False
    for line in lines:
        if not in_block:
            if QUESTION_BLOCK_RE.match(line):
                in_block = True
            continue
        # Stop at same-or-higher-level headings (##, #), but not ### sub-headers
        # which are used to group question bullets within the block.
        if re.match(r"^(#{1,2})\s", line):
            break
        m = BOLD_BULLET_RE.match(line)
        if m:
            q = m.group(1).strip()
            if q:
                questions.append(q)
        elif re.match(r"^\s*[-*]\s+\S", line):
            # Plain (non-bold) bullet: keep the text so format drift
            # (de-bolding a question) still round-trips.
            body = re.sub(r"^\s*[-*]\s+", "", line).strip()
            if body:
                questions.append(body)
    return questions


def _doc_type_code(text: str, stem: str, names: dict[str, str]) -> str:
    """Resolve the doc-type code for one template.

    Precedence: front-matter ``docType:`` → Document Control
    ``Document Type`` row (case-insensitive name match) → filename stem
    normalised against the doc-types names. Returns ``""`` when no
    candidate resolves to a known code.
    """
    m = FRONTMATTER_DOC_TYPE_RE.search(text)
    if m:
        return m.group(1)
    m = DOC_CONTROL_RE.search(text)
    if m:
        value = m.group(1).strip()
        # Formats seen: `Gap Analysis`, `AAIN — Agent Integration
        # Architecture`, `**Document Type** | Architecture Change Request`.
        value = value.lstrip("*").strip()
        parts = [p.strip() for p in re.split(r"[—–\-:]", value) if p.strip()]
        for part in parts:
            part = part.replace("*", "").strip()
            for code, meta in names.items():
                if part.lower() == str(meta.get("name", "")).lower():
                    return code
        if parts:
            # Whole cell, e.g. a bare name spanning the whole value.
            for code, meta in names.items():
                if value.replace("*", "").strip().lower() == str(meta.get("name", "")).lower():
                    return code
    # Filename-stem fallback: ``gap-analysis`` → ``gap analysis``.
    norm = stem.replace("-template", "").replace("-", " ").strip().lower()
    for code, meta in names.items():
        if norm == str(meta.get("name", "")).lower():
            return code
    return ""


# ---------------------------------------------------------------------------
# Scan + render
# ---------------------------------------------------------------------------


#: nested short-alias plugin dir → overlay plugin that owns its commands.
NESTED_ALIAS_TO_OVERLAY = {
    "it4it": "arckit-it4it",
    "oaa": "arckit-oaa",
}
#: flat overlay plugin dir name → its own commands dir.
FLAT_OWNERS = {
    "arckit-oaa": "arckit-oaa",
    "arckit-it4it": "arckit-it4it",
    "arckit-togaf-adm": "arckit-togaf-adm",
    # arckit-agent-architecture ships no tiered prerequisites of its own.
    "arckit-agent-architecture": "",
}


def _producing_command(path: Path) -> Path | None:
    """Command that produces a flat-tree template (stem mapping)."""
    owner = FLAT_OWNERS.get(path.parent.parent.name, "")
    if not owner:
        return None
    cmd = PLUGINS_DIR / owner / "commands" / f"{path.stem.replace('-template', '')}.md"
    return cmd


def _nested_overlay_command(path: Path) -> Path | None:
    """Overlay command whose MANDATORY tier a nested-only template
    borrows (e.g. nested ``it4it`` alias → ``arckit-it4it``)."""
    alias = path.relative_to(NESTED_TEMPLATES_DIR).parts[0]
    owner = NESTED_ALIAS_TO_OVERLAY.get(alias, "")
    if not owner:
        return None
    cmd = PLUGINS_DIR / owner / "commands" / f"{path.stem.replace('-template', '')}.md"
    return cmd


def collect_templates() -> list[tuple[bool, Path]]:
    """(is_flat, path) pairs, flat tree first, each group sorted by path."""
    flat: list[Path] = []
    for pattern in FLAT_TEMPLATE_GLOBS:
        flat.extend(pattern.parent.glob(pattern.name))
    flat = sorted(flat)
    nested = (
        sorted(NESTED_TEMPLATES_DIR.rglob("*.md"))
        if NESTED_TEMPLATES_DIR.is_dir()
        else []
    )
    return [(True, p) for p in flat] + [(False, p) for p in nested]


def main() -> None:
    out_path = Path(
        os.environ.get("ARCKIT_MCP_ROOT", REPO_ROOT.parent / "arckit-mcp")
    ) / "arckit_mcp" / "intake.py"
    if len(sys.argv) > 1:
        out_path = Path(sys.argv[1])

    doc_types = parse_doc_types()
    names = {code: meta for code, meta in doc_types.items()}

    intake: dict[str, dict] = {}
    notes: list[str] = []

    for is_flat, path in collect_templates():
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        code = _doc_type_code(text, path.stem, names)
        if not code:
            notes.append(f"{rel}: no resolvable doc-type code")
            continue
        questions = _extract_questions(text)
        if not questions:
            # Question block present but no parseable bullets.
            notes.append(f"{rel}: no parseable questions under '## Intake Interview Questions'")
            continue

        if is_flat:
            # Flat tree wins: look up the command in the owning flat
            # plugin's commands dir. arckit-agent-architecture has no
            # tiered prerequisites (its MANDATORY lists stay empty).
            cmd = _producing_command(path)
            mandatory = mandatory_codes_for([cmd]) if cmd is not None and cmd.is_file() else []
            entry = {
                "questions": questions,
                "mandatory_inputs": mandatory,
                "source": rel,
            }
            if code in intake:
                notes.append(f"{rel}: duplicate doc-type {code}, flat tree wins (existing source: {intake[code]['source']})")
            else:
                intake[code] = entry
        else:
            # Nested duplicate: discarded when a flat template already
            # produced questions for this code.
            if code in intake:
                continue
            # Nested-only code (no flat owner): the nested plugin alias
            # (``it4it``, ``oaa``) has no commands dir of its own, so
            # MANDATORY lookup falls back to the overlay plugin.
            mandatory = mandatory_codes_for([_nested_overlay_command(path)])
            intake[code] = {
                "questions": questions,
                "mandatory_inputs": mandatory,
                "source": rel,
            }

    # COVERAGE: union of doc-type codes from the flat-tree doc-types.mjs.
    coverage = {
        code: ("covered" if code in intake else "no-static-questions")
        for code in sorted(doc_types)
    }

    out: list[str] = [
        '"""Generated intake question tables.',
        "",
        "DO NOT EDIT BY HAND. This file is regenerated from the",
        "``## Intake Interview Questions`` blocks in",
        "``plugins/*/templates/*.md`` and ``plugins/arckit-claude/plugins/**/templates/*.md``,",
        "plus the MANDATORY-tier prerequisite inputs of the producing command",
        "(same conventions as ``scripts/generate-mcp-gates.py``). Run",
        "``python scripts/generate-mcp-intake.py`` after editing a template.",
        "",
        'Shape:',
        "",
        '    INTAKE[code] = {"questions": [...], "mandatory_inputs": [code, ...],',
        '                    "source": "plugins/.../...md"}',
        '    COVERAGE[code] = "covered" | "no-static-questions"',
        '    PARSER_NOTES: comment-only list of templates the generator',
        '    could not resolve (see the notes below).',
        '"""',
        "",
        "from __future__ import annotations",
        "",
    ]
    if notes:
        out.append("# PARSER_NOTES:")
        for note in notes:
            out.append(f"#   - {note}")
        out.append("")
    out.append("INTAKE: dict = {")
    for code in sorted(intake):
        entry = intake[code]
        out.append(f"    {json.dumps(code)}: {{")
        out.append(f"        'questions': {json.dumps(entry['questions'], indent=None)},")
        out.append(f"        'mandatory_inputs': {json.dumps(entry['mandatory_inputs'])},")
        out.append(f"        'source': {json.dumps(entry['source'])},")
        out.append("    },")
    out.append("}")
    out.append("")
    out.append("COVERAGE: dict = {")
    for code, status in coverage.items():
        out.append(f"    {json.dumps(code)}: {json.dumps(status)},")
    out.append("}")
    out.append("")
    text_out = "\n".join(out)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text_out, encoding="utf-8")
    try:
        display = out_path.relative_to(REPO_ROOT)
    except ValueError:
        display = out_path
    print(
        f"generated {display}: "
        f"{len(intake)} intake entries "
        f"({sum(1 for s in coverage.values() if s == 'covered')} covered / "
        f"{len(coverage)} known doc types, {len(notes)} parser notes)"
    )


if __name__ == "__main__":
    main()
