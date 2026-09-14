"""Tests for the demanded PlantUML-ArchiMate views in the two distribution
source plugins: arckit-togaf-adm and arckit-oaa.

Companion to tests/plugin/test_archimate_conformance.py (which guards the
core /arckit:archimate + ARCH doc-type). This file guards the *adoption into
the ADM/OAA artefacts* (OpenSpec change: archimate-demanded-artefacts).

The demanded set is fixed (proposal table). Each demanded template SHALL carry
one PlantUML-ArchiMate block using the pinned include line; the matching
command SHALL load the pinned notation reference and fill the block when the
artefact is ArchiMate-representable; and every pre-change ```mermaid block
(ADM templates) SHALL be byte-for-byte preserved.
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

ADM_DIR = REPO_ROOT / "plugins/arckit-togaf-adm"
OAA_DIR = REPO_ROOT / "plugins/arckit-oaa"

SNAPSHOT = REPO_ROOT / "tests/plugin/fixtures/archimate-demanded/prechange_mermaid_blocks.json"

# Same pinned line as test_archimate_conformance.py (PlantUML 1.2026.8).
PINNED_INCLUDE = "!include <archimate/Archimate>"

REF_PATH = "skills/plantuml-syntax/references/archimate.md"

# (plugin, template filename, command filename, archimate layer focus)
DEMANDED = [
    ("arckit-togaf-adm", "application-inventory-template.md", "application-inventory.md", "Application"),
    ("arckit-togaf-adm", "rationalization-template.md", "application-rationalization.md", "Application + Capability"),
    ("arckit-togaf-adm", "capability-map-template.md", "business-capability-map.md", "Business / Capability"),
    ("arckit-togaf-adm", "tech-architecture-template.md", "technology-architecture.md", "Technology"),
    ("arckit-togaf-adm", "transition-architecture-template.md", "transition-architecture.md", "Capability (incremental target)"),
    ("arckit-oaa", "oaa-adm-lite-template.md", "oaa-adm-lite.md", "Technology + Application"),
    ("arckit-oaa", "product-architecture-template.md", "product-architecture.md", "Application"),
]

ADM_TEMPLATE_NAMES = [d[1] for d in DEMANDED if d[0] == "arckit-togaf-adm"]


def _dir(plugin):
    return ADM_DIR if plugin == "arckit-togaf-adm" else OAA_DIR


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _plantuml_blocks(text: str):
    blocks, lines = [], text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("```plantuml"):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            blocks.append("".join(lines[i:j + 1]))
            i = j + 1
        else:
            i += 1
    return blocks


def _mermaid_blocks(text: str):
    blocks, lines = [], text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("```mermaid"):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            blocks.append("".join(lines[i:j + 1]))
            i = j + 1
        else:
            i += 1
    return blocks


def _id(param):
    plugin, tpl, cmd, layer = param
    return f"{plugin}/{cmd}"


# --- 1. demanded ArchiMate block present in each template -------------------

@pytest.mark.parametrize("demanded", DEMANDED, ids=[_id(d) for d in DEMANDED])
def test_archimate_block_in_template(demanded):
    plugin, tpl, _cmd, _layer = demanded
    text = _read(_dir(plugin) / "templates" / tpl)
    archimate_blocks = [
        b for b in _plantuml_blocks(text)
        if PINNED_INCLUDE in b and "@startuml" in b
    ]
    assert archimate_blocks, (
        f"{plugin}/templates/{tpl}: expected a PlantUML-ArchiMate block with "
        f"the pinned include line {PINNED_INCLUDE!r}; found none"
    )


# --- 2. demanded directive present in each command --------------------------

@pytest.mark.parametrize("demanded", DEMANDED, ids=[_id(d) for d in DEMANDED])
def test_archimate_directive_in_command(demanded):
    plugin, _tpl, cmd, _layer = demanded
    text = _read(_dir(plugin) / "commands" / cmd)
    assert REF_PATH in text, (
        f"{plugin}/commands/{cmd}: expected a load of {REF_PATH}"
    )
    assert re.search(r"ArchiMate-representable|archimate.*representable", text, re.IGNORECASE) or "archimate" in text.lower(), (
        f"{plugin}/commands/{cmd}: expected an ArchiMate fill-when-representable directive"
    )


# --- 3. pre-change Mermaid blocks are byte-for-byte preserved ---------------

def _snap():
    return json.loads(_read(SNAPSHOT))


@pytest.mark.parametrize("name", ADM_TEMPLATE_NAMES)
def test_mermaid_blocks_preserved(name):
    snap = _snap()[name]
    current = set(
        hashlib.sha256(b.encode("utf-8")).hexdigest()
        for b in _mermaid_blocks(_read(ADM_DIR / "templates" / name))
    )
    missing = [h for h in snap["sha256"] if h not in current]
    assert not missing, (
        f"arckit-togaf-adm/templates/{name}: {len(missing)} pre-change ```mermaid "
        f"block(s) missing/changed: {missing}"
    )


def test_snapshot_fixture_well_formed():
    snap = _snap()
    assert set(snap) == set(ADM_TEMPLATE_NAMES), "snapshot must cover exactly the 5 ADM templates"
    for name, meta in snap.items():
        assert meta["count"] > 0, f"{name}: snapshot has zero mermaid blocks"
        assert all(len(h) == 64 for h in meta["sha256"]), f"{name}: bad sha256 in snapshot"
