"""Tests for the demanded PlantUML-ArchiMate views in the two distribution
source plugins: arckit-togaf-adm and arckit-oaa.

Companion to tests/plugin/test_archimate_conformance.py (which guards the
core /arckit:archimate + ARCH doc-type). This file guards the *adoption into
the ADM/OAA artefacts* (OpenSpec changes: archimate-demanded-artefacts and
archimate-coverage-expansion).

The demanded set is now the full 17-artefact base list (superseding the
original 7). Each demanded template SHALL carry one PlantUML-ArchiMate base
view using the pinned include line; the matching command SHALL load the pinned
notation reference and fill the block when the artefact is ArchiMate-
representable; the four Batch-1 companion views SHALL appear as a separate
pinned block; and every pre-change ```mermaid block (ADM templates) SHALL be
byte-for-byte preserved.
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

# Original 7 demanded base views (plugin, template filename, command filename, layer focus).
DEMANDED = [
    ("arckit-togaf-adm", "application-inventory-template.md", "application-inventory.md", "Application"),
    ("arckit-togaf-adm", "rationalization-template.md", "application-rationalization.md", "Application + Capability"),
    ("arckit-togaf-adm", "capability-map-template.md", "business-capability-map.md", "Business / Capability"),
    ("arckit-togaf-adm", "tech-architecture-template.md", "technology-architecture.md", "Technology"),
    ("arckit-togaf-adm", "transition-architecture-template.md", "transition-architecture.md", "Capability (incremental target)"),
    ("arckit-oaa", "oaa-adm-lite-template.md", "oaa-adm-lite.md", "Technology + Application"),
    ("arckit-oaa", "product-architecture-template.md", "product-architecture.md", "Application"),
]

# 10 newly-in-scope base views added by archimate-coverage-expansion.
NEW_BASE = [
    ("arckit-togaf-adm", "adm-preliminary-template.md", "adm-preliminary.md", "Strategy"),
    ("arckit-togaf-adm", "architecture-board-template.md", "architecture-board.md", "Strategy / governance"),
    ("arckit-togaf-adm", "architecture-change-template.md", "architecture-change.md", "Implementation increments"),
    ("arckit-togaf-adm", "architecture-repository-template.md", "architecture-repository.md", "Structure"),
    ("arckit-togaf-adm", "data-architecture-template.md", "data-architecture.md", "Application/Technology data objects"),
    ("arckit-togaf-adm", "discovery-template.md", "discovery.md", "Motivation"),
    ("arckit-togaf-adm", "gap-analysis-template.md", "gap-analysis.md", "Capability (target vs current)"),
    ("arckit-oaa", "agile-governance-template.md", "agile-governance.md", "Strategy / governance"),
    ("arckit-oaa", "agile-security-template.md", "agile-security.md", "Technology / Application security"),
    ("arckit-oaa", "agile-strategy-template.md", "agile-strategy.md", "Strategy / value stream"),
]

# Full 17-artefact demanded base set.
ALL_BASE = DEMANDED + NEW_BASE

# Four Batch-1 companion views: (plugin, template, command, companion-type marker).
COMPANION = [
    ("arckit-togaf-adm", "transition-architecture-template.md", "transition-architecture.md", "Companion View (Implementation & Migration)"),
    ("arckit-togaf-adm", "gap-analysis-template.md", "gap-analysis.md", "Companion View (Implementation & Migration)"),
    ("arckit-togaf-adm", "tech-architecture-template.md", "technology-architecture.md", "Companion View (Physical)"),
    ("arckit-oaa", "oaa-adm-lite-template.md", "oaa-adm-lite.md", "Companion View (Physical)"),
]

# ADM in-scope templates carrying pre-change ```mermaid blocks (fixture keys).
ADM_MERMAID_NAMES = [
    "adm-preliminary-template.md",
    "application-inventory-template.md",
    "architecture-board-template.md",
    "capability-map-template.md",
    "data-architecture-template.md",
    "gap-analysis-template.md",
    "rationalization-template.md",
    "tech-architecture-template.md",
    "transition-architecture-template.md",
]


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


def _cid(param):
    plugin, tpl, cmd, marker = param
    kind = marker.split("(", 1)[1].rstrip(")") if "(" in marker else marker
    return f"{plugin}/{cmd}[{kind}]"


# --- 1. demanded ArchiMate base view present in all 17 templates -------------

@pytest.mark.parametrize("demanded", ALL_BASE, ids=[_id(d) for d in ALL_BASE])
def test_archimate_block_in_template(demanded):
    plugin, tpl, _cmd, _layer = demanded
    text = _read(_dir(plugin) / "templates" / tpl)
    archimate_blocks = [
        b for b in _plantuml_blocks(text)
        if PINNED_INCLUDE in b and "@startuml" in b
    ]
    assert archimate_blocks, (
        f"{plugin}/templates/{tpl}: expected a PlantUML-ArchiMate base-view block "
        f"with the pinned include line {PINNED_INCLUDE!r}; found none"
    )


# --- 2. demanded base-view directive present in each command -----------------

@pytest.mark.parametrize("demanded", ALL_BASE, ids=[_id(d) for d in ALL_BASE])
def test_archimate_directive_in_command(demanded):
    plugin, _tpl, cmd, _layer = demanded
    text = _read(_dir(plugin) / "commands" / cmd)
    assert REF_PATH in text, (
        f"{plugin}/commands/{cmd}: expected a load of {REF_PATH}"
    )
    assert re.search(r"ArchiMate-representable|archimate.*representable", text, re.IGNORECASE) or "archimate" in text.lower(), (
        f"{plugin}/commands/{cmd}: expected an ArchiMate fill-when-representable directive"
    )


# --- 2b. Batch-1 companion view present in the 4 artefacts ------------------

@pytest.mark.parametrize("companion", COMPANION, ids=[_cid(c) for c in COMPANION])
def test_companion_view_in_template(companion):
    plugin, tpl, _cmd, marker = companion
    text = _read(_dir(plugin) / "templates" / tpl)
    assert marker in text, (
        f"{plugin}/templates/{tpl}: expected the companion-view section "
        f"{marker!r}; found none"
    )
    archimate_blocks = [
        b for b in _plantuml_blocks(text)
        if PINNED_INCLUDE in b and "@startuml" in b
    ]
    assert len(archimate_blocks) >= 2, (
        f"{plugin}/templates/{tpl}: expected a second (companion) PlantUML-ArchiMate "
        f"block; found {len(archimate_blocks)}"
    )



# --- 2c. ArchiMate views are rendered to a self-contained SVG -------------
# PlantUML does not render in markdown, so every ArchiMate-carrying command
# must direct rendering the inline source to a self-contained .svg, and every
# ArchiMate template section must carry the .svg delivery note.

CMD_SVG_MARKERS = ("plantuml-1.2026.8.jar -tsvg", "Offline Self-Contained SVG Rendering")
TPL_SVG_MARKER = "self-contained `.svg`"


@pytest.mark.parametrize("demanded", ALL_BASE, ids=[_id(d) for d in ALL_BASE])
def test_svg_delivery_in_base_command(demanded):
    plugin, _tpl, cmd, _layer = demanded
    text = _read(_dir(plugin) / "commands" / cmd)
    for marker in CMD_SVG_MARKERS:
        assert marker in text, (
            f"{plugin}/commands/{cmd}: expected a self-contained SVG-render "
            f"clause containing {marker!r}"
        )


@pytest.mark.parametrize("demanded", ALL_BASE, ids=[_id(d) for d in ALL_BASE])
def test_svg_delivery_in_base_template(demanded):
    plugin, tpl, _cmd, _layer = demanded
    text = _read(_dir(plugin) / "templates" / tpl)
    assert TPL_SVG_MARKER in text, (
        f"{plugin}/templates/{tpl}: expected a self-contained `.svg` delivery note"
    )


@pytest.mark.parametrize("companion", COMPANION, ids=[_cid(c) for c in COMPANION])
def test_svg_delivery_in_companion_command(companion):
    plugin, _tpl, cmd, _marker = companion
    text = _read(_dir(plugin) / "commands" / cmd)
    for marker in CMD_SVG_MARKERS:
        assert marker in text, (
            f"{plugin}/commands/{cmd}: expected the companion-view self-contained "
            f"SVG-render clause containing {marker!r}"
        )


@pytest.mark.parametrize("companion", COMPANION, ids=[_cid(c) for c in COMPANION])
def test_svg_delivery_in_companion_template(companion):
    plugin, tpl, _cmd, _marker = companion
    text = _read(_dir(plugin) / "templates" / tpl)
    assert text.count(TPL_SVG_MARKER) >= 2, (
        f"{plugin}/templates/{tpl}: expected the `.svg` delivery note on BOTH the "
        f"base and the companion sections (found {text.count(TPL_SVG_MARKER)})"
    )


# --- 3. pre-change Mermaid blocks are byte-for-byte preserved ---------------

def _snap():
    return json.loads(_read(SNAPSHOT))


@pytest.mark.parametrize("name", ADM_MERMAID_NAMES)
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
    assert set(snap) == set(ADM_MERMAID_NAMES), "snapshot must cover exactly the ADM mermaid-carrying in-scope templates"
    for name, meta in snap.items():
        assert meta["count"] > 0, f"{name}: snapshot has zero mermaid blocks"
        assert all(len(h) == 64 for h in meta["sha256"]), f"{name}: bad sha256 in snapshot"


# --- 2d. BPCM capability map rendered as a PlantUML-ArchiMate view ----------
# OpenSpec change: bpcm-capmap-archimate. The BPCM capability hierarchy
# (L1 domains -> L2 sub-capabilities -> optional L3) is ArchiMate-representable
# as nested Strategy_Capability joined by a whole->part edge
# (Rel_Composition "...contains..."). That view is ADDITIVE to the Mermaid
# mindmap and to the existing capability->target realization view.

BPCM_TPL = "capability-map-template.md"
BPCM_CMD = "business-capability-map.md"
BPCM_CAPMAP_SECTION = "Capability Map (ArchiMate View)"
BPCM_WHOLE_TO_PART = "Rel_Composition"


def test_bpcm_capmap_archimate_view_in_template():
    text = _read(ADM_DIR / "templates" / BPCM_TPL)
    assert BPCM_CAPMAP_SECTION in text, (
        f"arckit-togaf-adm/templates/{BPCM_TPL}: expected a "
        f"{BPCM_CAPMAP_SECTION!r} section (ArchiMate capability map)"
    )
    assert "Strategy_Capability" in text, (
        f"arckit-togaf-adm/templates/{BPCM_TPL}: expected Strategy_Capability "
        f"elements in the capability-map view"
    )
    capmap_blocks = [b for b in _plantuml_blocks(text) if BPCM_WHOLE_TO_PART in b]
    assert capmap_blocks, (
        f"arckit-togaf-adm/templates/{BPCM_TPL}: expected a PlantUML-ArchiMate "
        f"capability-map block using the whole->part {BPCM_WHOLE_TO_PART!r} edge"
    )


def test_bpcm_capmap_directive_in_command():
    text = _read(ADM_DIR / "commands" / BPCM_CMD).lower()
    assert BPCM_WHOLE_TO_PART.lower() in text, (
        f"arckit-togaf-adm/commands/{BPCM_CMD}: expected the whole->part "
        f"{BPCM_WHOLE_TO_PART!r} edge to be named"
    )
    assert "whole" in text, (
        f"arckit-togaf-adm/commands/{BPCM_CMD}: expected the whole->part "
        f"(parent->child) edge direction to be stated"
    )
    assert "contains" in text, (
        f"arckit-togaf-adm/commands/{BPCM_CMD}: expected whole->part edges to "
        f"be labelled 'contains'"
    )
    assert "split" in text or "capability-domain" in text, (
        f"arckit-togaf-adm/commands/{BPCM_CMD}: expected the <=12-element "
        f"split gate (split at a capability-domain boundary)"
    )
