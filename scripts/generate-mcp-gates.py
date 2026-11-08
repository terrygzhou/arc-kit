#!/usr/bin/env python3
"""Generate arckit-mcp/arckit_mcp/gates.py from command prerequisite blocks.

The generated module lives in the sibling arckit-mcp repo, not in this
tree. It is imported by the arckit-mcp server; do not edit it by hand.

Scans the command markdown under ``plugins/arckit-{claude,oaa,it4it,togaf-adm}/commands/``
for prerequisite sections — the ``**MANDATORY`` / ``**RECOMMENDED`` /
``**OPTIONAL`` header lines that open a prerequisite block, plus a plain
``# Prerequisites`` style section when no tiered block is present.

From every tiered block it extracts the prerequisite items, in order:
each ``- **CODE** (Name)`` bullet, or a plain ``- **CODE**:`` bullet, or a
trailing bare code such as ``- ``ARC-*-CODE-*.md``, and records the tier the
item appeared under. The output is a generated Python module:

    GATE_TIERS: dict = {
        "plugin/command": {"CODE": "MANDATORY" | "RECOMMENDED" | "OPTIONAL", ...},
        ...
    }

where the key is ``{plugin-basename}/{command-filename-stem}`` (for example
``arckit-oaa/adm-preliminary``) and commands with no tiered prerequisite
block get an empty dict (they are still listed so the gate tool can report
"no declared prerequisites").

Codes are normalised: the code part is upper-cased; a leading ``ARC``
prefix (as in ``ARC-REQ`` or ``ARC-*-REQ``) and any ``-*`` / ``*-``
wildcard fragments are stripped, so ``- **REQ**``, ``- **ARC-REQ**`` and
the trailing ``ARC-*-REQ-*.md`` forms all map to ``REQ``.  A bullet whose
bolded word is not a doc-type code (e.g. a prose list like
``- **HIGH-RISK**: ...`` inside a non-prerequisite list) is skipped.

Usage:
    python scripts/generate-mcp-gates.py [output-path]

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
    return root / "arckit_mcp" / "gates.py"


OUT_PATH = _default_out_path()

PLUGINS_DIR = REPO_ROOT / "plugins"
PLUGIN_DIRS = [PLUGINS_DIR / name for name in ("arckit-claude", "arckit-oaa", "arckit-it4it", "arckit-togaf-adm")]

# ``**TIER**`` header line (bold word may be the line start or follow a list dash).
TIER_HEADER_RE = re.compile(r"^\s*(?:-\s+)?\*\*(MANDATORY|RECOMMENDED|OPTIONAL)\*\*")
# Plain-heading tier variant, e.g. ``### MANDATORY (stop if missing …)`` —
# the one-off style used by application-rationalization.md.
HEADING_TIER_RE = re.compile(r"^\s*#+\s*(MANDATORY|RECOMMENDED|OPTIONAL)\b")
# Plain prerequisites section header (non-tiered fallback).
PLAIN_PREQ_RE = re.compile(r"^\s*#+\s*prerequisites", re.IGNORECASE)
# Trailing bare-code reference at the end of a bullet, e.g. ``(``ARC-*-REQ-*.md``)``
# or a plain ``- ``ARC-*-REQ-*.md```` bullet.
TRAILING_CODE_RE = re.compile(r"(`|'|\()" r"(ARC[~-]\*?-\*?)([A-Z][A-Z0-9]{1,6})" r"-\*?(\.md)?[`'\)]")
# A bare code used as the bullet text itself, e.g. ``- REQ (Requirements)``.
BARE_CODE_RE = re.compile(r"^([A-Z][A-Z0-9]{1,6})\b(?!\s*[(`])")


def _clean_code(raw: str) -> str:
    """Normalise an extracted raw code fragment to a bare doc-type code.

    Strips an optional leading ``ARC`` / ``ARC-*`` prefix and any wildcard
    fragments; returns ``""`` when the fragment is not a clean code.
    """
    c = raw.strip().lstrip("*").strip()
    if c.startswith("ARC"):
        c = c[3:]
    c = c.split("-")[0]
    return c if c else ""


def _bullet_code(line: str) -> str:
    """Extract the doc-type code from a prerequisite bullet line.

    Precedence: a bolded leading ``**CODE**`` or ``**CODE**:`` token, then a
    trailing ``ARC-*-CODE-*.md`` reference, then a bare leading code word.
    Returns ``""`` when the line carries no recognisable code.
    """
    m = re.match(r"^\s*(?:[-*]\s+)?\*\*([A-Za-z0-9*~-]+)\*\*", line)
    if m:
        code = _clean_code(m.group(1))
        # Only accept when the bolded word is plausibly a doc-type code
        # (short, uppercase after cleaning) — this keeps prose bullets
        # like ``- **HIGH-RISK**: ...`` out of the table.
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


def parse_plugin_dir(plugin_dir: Path, gates: dict[str, dict[str, str]]) -> None:
    commands_dir = plugin_dir / "commands"
    if not commands_dir.is_dir():
        return
    # Keys are ``{plugin-basename}/{command-filename-stem}``, e.g.
    # ``arckit-oaa/agile-strategy`` — the plugin directory name, not a
    # short alias, so the table lines up with the plugin manifests.
    prefix = plugin_dir.name
    for md in sorted(commands_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        lines = text.splitlines()

        # --- Tiered blocks: every ``**TIER**`` header starts a block; the
        # block ends at the next tier header or a non-list structural line.
        tiers: dict[str, str] = {}
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
                    continue  # blank line inside a block is fine
                if TIER_HEADER_RE.match(line) or HEADING_TIER_RE.match(line) or PLAIN_PREQ_RE.match(line):
                    # A new structural header ends the previous block.
                    if PLAIN_PREQ_RE.match(line):
                        in_block = False
                        current_tier = None
                    continue
                if not stripped.startswith(("-", "*", " ")):
                    # Prose, headings, fences, etc. end the block.
                    in_block = False
                    current_tier = None
                    continue
                # List bullet (or continuation indent): extract the code.
                code = _bullet_code(stripped)
                if code and current_tier:
                    tiers.setdefault(code, current_tier)
            elif PLAIN_PREQ_RE.match(line):
                # Non-tiered prerequisites section: bullets are MANDATORY.
                in_block = True
                current_tier = "MANDATORY"
        if tiers:
            gates[f"{prefix}/{md.stem}"] = tiers
    # Commands without any tiered block get an empty mapping so the gate
    # tool can report "no declared prerequisites" instead of KeyError.
    for md in sorted(commands_dir.glob("*.md")):
        gates.setdefault(f"{prefix}/{md.stem}", {})


def render(gates: dict[str, dict[str, str]]) -> str:
    out: list[str] = [
        '"""Generated gate-tier table.',
        "",
        "DO NOT EDIT BY HAND. This file is regenerated from the ``MANDATORY`` /",
        "``RECOMMENDED`` / ``OPTIONAL`` prerequisite blocks in the command markdown",
        "bodies under ``plugins/arckit-{claude,oaa,it4it,togaf-adm}/commands/`` by",
        "``scripts/generate-mcp-gates.py``.",
        "",
        'Shape: ``GATE_TIERS[command][code] = tier`` where tier is one of',
        '``"MANDATORY"``, ``"RECOMMENDED"``, ``"OPTIONAL"``.',
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "",
        "GATE_TIERS: dict = {",
    ]
    for command in sorted(gates):
        tiers = gates[command]
        if not tiers:
            out.append(f'    {json.dumps(command)}: {{}},')
        else:
            out.append(f'    {json.dumps(command)}: {{')
            for code in sorted(tiers):
                out.append(f'        {json.dumps(code)}: {json.dumps(tiers[code])},')
            out.append("    },")
    out.append("}")
    out.append("")
    return "\n".join(out)


def main() -> None:
    global OUT_PATH
    if len(sys.argv) > 1:
        OUT_PATH = Path(sys.argv[1])
    gates: dict[str, dict[str, str]] = {}
    for plugin_dir in PLUGIN_DIRS:
        parse_plugin_dir(plugin_dir, gates)
    OUT_PATH.write_text(render(gates), encoding="utf-8")
    total = sum(len(v) for v in gates.values())
    cmds_with = sum(1 for v in gates.values() if v)
    try:
        display = OUT_PATH.relative_to(REPO_ROOT)
    except ValueError:
        display = OUT_PATH
    print(
        f"generated {display}: "
        f"{total} gate entries across {cmds_with}/{len(gates)} commands"
    )


if __name__ == "__main__":
    main()
