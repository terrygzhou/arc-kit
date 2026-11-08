#!/usr/bin/env python3
"""Generate arckit-mcp/arckit_mcp/handoffs.py from command frontmatter.

The generated module lives in the sibling arckit-mcp repo, not in this
tree. It is imported by the arckit-mcp server; do not edit it by hand.

Scans the YAML frontmatter of the command markdown under
``plugins/arckit-{claude,oaa,it4it,togaf-adm}/commands/`` for the optional
``handoffs:`` block. Each handoff entry is a list item of the form::

    - command: <stem>
      description: <text>       (optional)
      condition: <text>         (optional, unquoted or quoted)

The output is a generated Python module:

    HANDOFFS: dict = {
        "plugin/command": [
            (target, condition_text, condition_code), ...
        ],
        ...
    }

where the key is ``{plugin-basename}/{command-filename-stem}`` (e.g.
``arckit-claude/requirements``), ``target`` is the referenced command stem,
``condition_text`` is the verbatim condition prose (``""`` when absent), and
``condition_code`` is the doc-type code extracted from the condition text
when present, else ``""``.

Commands without a ``handoffs:`` block are omitted from the table entirely —
the consumer checks membership, not a default.

The frontmatter is parsed with a small hand-rolled line scanner (no
``import yaml`` dependency) that is sufficient for the two-space-indented
list-of-mappings shape ArcKit uses.

Usage:
    python scripts/generate-mcp-handoffs.py [output-path]

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
# Default location is the sibling arckit-mcp repo (the generated files live
# there, not in this tree). Overridable via the ARCKIT_MCP_ROOT env var or
# a CLI arg, so regeneration also works without the repo tree present.
def _default_out_path() -> Path:
    root = Path(os.environ.get("ARCKIT_MCP_ROOT", REPO_ROOT.parent / "arckit-mcp"))
    return root / "arckit_mcp" / "handoffs.py"


OUT_PATH = _default_out_path()

PLUGINS_DIR = REPO_ROOT / "plugins"
PLUGIN_DIRS = [
    PLUGINS_DIR / name
    for name in ("arckit-claude", "arckit-oaa", "arckit-it4it", "arckit-togaf-adm")
]

def _extract_condition_code(condition_text: str) -> str:
    """Pull a doc-type code out of free-form condition prose.

    Heuristic: the most salient uppercase token in the text. When several
    candidates appear, the one that most plausibly names an ArcKit
    doc-type wins — decided by a small priority table of known codes;
    fall back to the first candidate, else ``""``.
    """
    if not condition_text:
        return ""
    # Known codes first (longest match wins to avoid prefix collisions).
    known = (
        "BPCM", "APP", "APPR", "GAPA", "TRANS", "BORD", "ACHG", "REPO",
        "DISC", "TECH", "OASTR", "OAPR", "OAAL", "OASEC", "OAGOV",
        "ITVN", "ITVS", "ITSF", "ITDT", "ITCF", "ITOA", "AAGI",
        "ADMP", "PRIN", "HLDR", "DLDR", "DATA", "WARD", "WDOC", "WGAM",
        "WCLM", "WVCH", "DIAG", "DFD", "ARCH", "ADR", "PLAT", "SOLN",
        "REQ", "STKE", "RSCH", "DSCT", "TNDR", "CMPT", "SOBC", "PLAN",
        "ROAD", "STRAT", "BKLG", "BMM",
    )
    for code in sorted(known, key=len, reverse=True):
        if re.search(rf"\b{code}\b", condition_text):
            return code
    return ""


def _strip_quotes(value: str) -> str:
    """Strip a matching pair of single or double quotes around a value."""
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        v = v[1:-1]
    return v.strip()


def _parse_handoffs_block(lines: list[str]) -> list[dict[str, str]]:
    """Parse the list-of-mappings under a ``handoffs:`` key.

    Each entry looks like::

      - command: <stem>
        description: <text>
        condition: <text>

    Returns a list of dicts with keys ``command`` (required), and optional
    ``description`` and ``condition``.
    """
    handoffs: list[dict[str, str]] = []
    # Find the ``handoffs:`` line.
    start = -1
    for idx, line in enumerate(lines):
        if re.match(r"^handoffs:\s*$", line):
            start = idx + 1
            break
    if start == -1:
        return handoffs

    # Scan the remaining lines for handoff list items. Each item starts with
    # ``- command:`` (the dash may be at column 0 or indented two spaces).
    # Sub-fields are indented further (no dash). A new top-level key or a
    # dash at the item level ends the block.
    i = start
    n = len(lines)
    while i < n:
        m_item = re.match(r"^\s*-\s+command:\s*(\S+)", lines[i])
        if m_item:
            entry: dict[str, str] = {"command": _strip_quotes(m_item.group(1))}
            i += 1
            # Consume the description / condition sub-fields for this item.
            while i < n:
                s2 = lines[i].strip()
                if not s2:
                    i += 1
                    continue
                # A new list item or a top-level key ends this entry.
                if re.match(r"^\s*-\s+command:", lines[i]):
                    break
                if re.match(r"^\S", lines[i]):
                    break
                m_desc = re.match(r"description:\s*(.*)", s2)
                if m_desc:
                    entry["description"] = _strip_quotes(m_desc.group(1))
                    i += 1
                    continue
                m_cond = re.match(r"condition:\s*(.*)", s2)
                if m_cond:
                    entry["condition"] = _strip_quotes(m_cond.group(1))
                    i += 1
                    continue
                # An unexpected sub-field: skip it.
                i += 1
            handoffs.append(entry)
            continue
        # Blank line or unrecognized line: skip.
        i += 1
    return handoffs


def parse_plugin_dir(plugin_dir: Path, handoffs: dict[str, list[tuple[str, str, str]]]) -> None:
    commands_dir = plugin_dir / "commands"
    if not commands_dir.is_dir():
        return
    prefix = plugin_dir.name
    for md in sorted(commands_dir.glob("*.md")):
        lines = md.read_text(encoding="utf-8").splitlines()
        # Extract the frontmatter (first two ``---`` delimiters).
        if not lines or lines[0] != "---":
            continue
        fm: list[str] = []
        in_fm = False
        for line in lines[1:]:
            if line == "---":
                break
            fm.append(line)
        entries = _parse_handoffs_block(fm)
        if entries:
            tuples: list[tuple[str, str, str]] = []
            for e in entries:
                target = e["command"]
                cond_text = e.get("condition", "")
                cond_code = _extract_condition_code(cond_text)
                tuples.append((target, cond_text, cond_code))
            handoffs[f"{prefix}/{md.stem}"] = tuples


def render(handoffs: dict[str, list[tuple[str, str, str]]]) -> str:
    out: list[str] = [
        '"""Generated handoff graph.',
        "",
        "DO NOT EDIT BY HAND. This file is regenerated from the ``handoffs:``",
        "frontmatter in the command markdown under",
        "``plugins/arckit-{claude,oaa,it4it,togaf-adm}/commands/`` by",
        "``scripts/generate-mcp-handoffs.py``.",
        "",
        "Shape: ``HANDOFFS[command] = [(target, condition_text, condition_code), ...]``.",
        "``condition_text`` is ``\"\"`` when the handoff has no condition;",
        "``condition_code`` is the doc-type code the condition references",
        "when detectable, else ``\"\"``.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "",
        "HANDOFFS: dict = {",
    ]
    for command in sorted(handoffs):
        entries = handoffs[command]
        out.append(f"    {json.dumps(command)}: [")
        for target, cond_text, cond_code in entries:
            out.append(
                f"        ({json.dumps(target)}, {json.dumps(cond_text)}, {json.dumps(cond_code)}),"
            )
        out.append("    ],")
    out.append("}")
    out.append("")
    return "\n".join(out)


def main() -> None:
    global OUT_PATH
    if len(sys.argv) > 1:
        OUT_PATH = Path(sys.argv[1])
    handoffs: dict[str, list[tuple[str, str, str]]] = {}
    for plugin_dir in PLUGIN_DIRS:
        parse_plugin_dir(plugin_dir, handoffs)
    OUT_PATH.write_text(render(handoffs), encoding="utf-8")
    total = sum(len(v) for v in handoffs.values())
    try:
        display = OUT_PATH.relative_to(REPO_ROOT)
    except ValueError:
        display = OUT_PATH
    print(
        f"generated {display}: "
        f"{total} handoff edges across {len(handoffs)} commands"
    )


if __name__ == "__main__":
    main()
