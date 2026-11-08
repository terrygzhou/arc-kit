#!/usr/bin/env python3
"""Generate arckit-mcp/arckit_mcp/_registry.py from doc-types.mjs.

Reads the canonical document-type registry in
plugins/arckit-claude/config/doc-types.mjs and emits a generated Python
module with DOC_TYPES, SUBDIR_MAP, MULTI_INSTANCE_TYPES and
KNOWN_TYPES. The generated file lives in the sibling arckit-mcp repo
and is imported by the arckit-mcp server; do not edit it by hand.

The mjs file is a flat object literal (same constraint
scripts/check-doc-type-registry.py relies on), so it is parsed with
regex + json instead of a node subprocess — the generator must run in
CI without assuming a node toolchain.

Usage:
    python scripts/generate-mcp-registry.py [output-path]

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
DOC_TYPES_MJS = REPO_ROOT / "plugins" / "arckit-claude" / "config" / "doc-types.mjs"
# Default location is the sibling arckit-mcp repo (the generated files live
# there, not in this tree). Overridable via the ARCKIT_MCP_ROOT env var or
# a CLI arg, so regeneration also works without the repo tree present.
def _default_out_path() -> Path:
    root = Path(os.environ.get("ARCKIT_MCP_ROOT", REPO_ROOT.parent / "arckit-mcp"))
    return root / "arckit_mcp" / "_registry.py"


OUT_PATH = _default_out_path()


def _strip_comments(text: str) -> str:
    """Remove // and /* */ comments (naive, but safe for this file's style)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _block(text: str, name: str) -> str:
    """Extract the full `name = { ... }` block of a flat JS object.

    Mirrors the block() helper in scripts/check-doc-type-registry.py:
    brace counting is safe because the DOC_TYPES/SUBDIR_MAP values are
    flat single-line object literals with no nested braces.
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
         followed by `:` and we are NOT inside a string, quote it. This
         catches nested keys (`name:`, `category:`) that the regex
         approach could not safely reach, because it operates on the
         pre-string-rewritten text.
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
                # a key (followed by `:`). If so, quote it; otherwise
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


def _js_array_to_json(block: str) -> list[str]:
    body = block.strip().lstrip("[").rstrip("]")
    body = body.replace("'", '"')
    body = re.sub(r",\s*$", "", body)
    return json.loads("[" + body + "]")


def parse_mjs() -> dict:
    text = _strip_comments(DOC_TYPES_MJS.read_text(encoding="utf-8"))

    doc_types = _js_obj_to_json(_block(text, "DOC_TYPES"), "DOC_TYPES")
    subdir_map = _js_obj_to_json(_block(text, "SUBDIR_MAP"), "SUBDIR_MAP")
    multi_block = re.search(
        r"export\s+const\s+MULTI_INSTANCE_TYPES\s*=\s*new\s+Set\(", text
    )
    if not multi_block:
        raise SystemExit("doc-types.mjs: cannot find MULTI_INSTANCE_TYPES")
    arr_start = text.index("[", multi_block.end())
    arr_end = text.index("]", arr_start)
    multi = _js_array_to_json(text[arr_start : arr_end + 1])

    return {
        "DOC_TYPES": doc_types,
        "SUBDIR_MAP": subdir_map,
        "MULTI_INSTANCE_TYPES": sorted(multi),
    }


HEADER = '''\
"""Generated by scripts/generate-mcp-registry.py — DO NOT EDIT BY HAND.

Source: plugins/arckit-claude/config/doc-types.mjs
"""

from __future__ import annotations

'''


def _py_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render(reg: dict) -> str:
    lines = [HEADER, ""]

    lines.append("DOC_TYPES: dict = {")
    for code, meta in reg["DOC_TYPES"].items():
        fields = ", ".join(
            f"{_py_str(k)}: {_py_str(v)}" for k, v in meta.items()
        )
        lines.append(f"    {_py_str(code)}: {{{fields}}},")
    lines.append("}")
    lines.append("")

    lines.append("SUBDIR_MAP: dict = {")
    for code, subdir in reg["SUBDIR_MAP"].items():
        lines.append(f"    {_py_str(code)}: {_py_str(subdir)},")
    lines.append("}")
    lines.append("")

    lines.append("MULTI_INSTANCE_TYPES: set = set([")
    for code in reg["MULTI_INSTANCE_TYPES"]:
        lines.append(f"    {_py_str(code)},")
    lines.append("])")
    lines.append("")

    lines.append("KNOWN_TYPES: set = set(DOC_TYPES.keys())")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    global OUT_PATH
    if len(sys.argv) > 1:
        OUT_PATH = Path(sys.argv[1])
    reg = parse_mjs()
    OUT_PATH.write_text(render(reg), encoding="utf-8")
    try:
        display = OUT_PATH.relative_to(REPO_ROOT)
    except ValueError:
        display = OUT_PATH
    print(
        f"generated {display}: "
        f"{len(reg['DOC_TYPES'])} doc types, "
        f"{len(reg['SUBDIR_MAP'])} subdir entries, "
        f"{len(reg['MULTI_INSTANCE_TYPES'])} multi-instance types"
    )


if __name__ == "__main__":
    main()
