"""Tests for /arckit:solution-design and the SOLN doc-type registration.

Mirrors the registration-point discipline established by the BMM and ARCH
conformance guards: every point that fails silently when missed gets a
check here.

  - SOLN in doc-types.mjs DOC_TYPES (category Architecture) and
    MULTI_INSTANCE_TYPES (sidecar DIAGs are sequenced; SOLN itself is
    also multi-instance, e.g. re-runs produce v1.1, v1.2 …)
  - SOLN in /arckit:pages known-artifact-types table
  - SOLN in generate-document-id.sh MULTI_INSTANCE_TYPES (both copies:
    repo-root scripts/ and plugins/arckit-claude/scripts/)
  - commands/solution-design.md frontmatter (doc-type SOLN, effort high,
    handoffs include hld-review/dld-review/traceability/sow/diagram),
    REQ-mandatory clause, 6-diagram instruction, DIAG generator call
  - templates/solution-design-template.md: all 14 ## sections present
    (including Overview, Requirements Traceability, Design Rationale
    added by 11b943d7), 6 plantuml blocks each opening @startuml and
    closing @enduml, "View this diagram" callout after each block
  - skills/plantuml-syntax/SKILL.md: mapping rows for all 6 diagram types
    referencing /arckit:solution-design
  - skills/plantuml-syntax/references/object-diagrams.md present in
    plugins/arckit-claude and all extension trees that carry
    plantuml-syntax skills
  - docs/guides/solution-design.md and plugins/arckit-claude/docs/guides/
    solution-design.md (identical copies)
  - guide-groups.mjs: solution-design entry
  - docs/guides.html: solution-design link
  - extensions/arckit-codex/prompts/ and commands/ carry the solution-
    design prompt and command
  - Registry guard scripts pass

Expected user input to /arckit:solution-design:
  $ARGUMENTS  – project ID or domain name (e.g. "001", "patient records"),
                optionally a comma-separated diagram subset (e.g. "sequence,class")

Mandatory source artefacts (command stops if missing):
  ARC-{P}-REQ-v*.md   – requirements (FR, NFR, INT, BR, DR)

Recommended source artefacts:
  ARC-000-PRIN-v*.md  – technology principles / constraints
  ARC-{P}-STKE-v*.md  – stakeholders (drives Use Case actors)
  ARC-{P}-DATA-v*.md  – data model (drives Class Diagram)
  decisions/ARC-*-ADR-*.md  – recorded ADRs (Design Rationale consistency)

Optional source artefacts:
  ARC-{P}-SOBC-v*.md, ARC-{P}-RSCH-v*.md, HLDR/DLDR artefacts,
  external/ files, projects/000-global/external/

Templates read by the command:
  plugins/arckit-claude/templates/solution-design-template.md
  (dual-tree copy: .arckit/templates/solution-design-template.md in the
   project root; user-override copy takes precedence if present)

Output artefacts written:
  projects/{P}/ARC-{P}-SOLN-v{X}.md   – primary solution design document
  projects/{P}/diagrams/ARC-{P}-DIAG-{NNN}-v1.0.md
                                        – one per populated diagram type,
                                          only when user selected a single
                                          type in Q1 or explicitly requested
                                          standalone DIAG artefacts
"""

import re
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

# --- registration points -------------------------------------------------
DOC_TYPES_MJS   = REPO_ROOT / "plugins/arckit-claude/config/doc-types.mjs"
PAGES_CMD       = REPO_ROOT / "plugins/arckit-claude/commands/pages.md"
GEN_DOC_ID      = REPO_ROOT / "scripts/bash/generate-document-id.sh"
GEN_DOC_ID_PLG  = REPO_ROOT / "plugins/arckit-claude/scripts/bash/generate-document-id.sh"
GUIDE_GROUPS    = REPO_ROOT / "plugins/arckit-claude/config/guide-groups.mjs"

# --- command + template ---------------------------------------------------
COMMAND   = REPO_ROOT / "plugins/arckit-claude/commands/solution-design.md"
TEMPLATE  = REPO_ROOT / "plugins/arckit-claude/templates/solution-design-template.md"
TEMPLATE2 = REPO_ROOT / ".arckit/templates/solution-design-template.md"

# --- skill + reference ----------------------------------------------------
SKILL      = REPO_ROOT / "plugins/arckit-claude/skills/plantuml-syntax/SKILL.md"
OBJ_REF    = REPO_ROOT / "plugins/arckit-claude/skills/plantuml-syntax/references/object-diagrams.md"

# --- guides ----------------------------------------------------------------
GUIDE        = REPO_ROOT / "docs/guides/solution-design.md"
PLUGIN_GUIDE = REPO_ROOT / "plugins/arckit-claude/docs/guides/solution-design.md"
SITE         = REPO_ROOT / "docs/guides.html"

# --- extension trees -------------------------------------------------------
CODEX_PROMPT = REPO_ROOT / "extensions/arckit-codex/prompts/arckit.solution-design.md"
CODEX_CMD    = REPO_ROOT / "extensions/arckit-codex/commands/arckit.solution-design.md"

# All 7 extension trees that carry plantuml-syntax skills
PLANTUML_EXTENSION_SKILLS = [
    REPO_ROOT / "extensions/arckit-codex/skills/plantuml-syntax",
    REPO_ROOT / "extensions/arckit-copilot/skills/plantuml-syntax",
    REPO_ROOT / "extensions/arckit-gemini/skills/plantuml-syntax",
    REPO_ROOT / "extensions/arckit-kimi/skills/plantuml-syntax",
    REPO_ROOT / "extensions/arckit-opencode/skills/plantuml-syntax",
    REPO_ROOT / "extensions/arckit-paperclip/skills/plantuml-syntax",
    REPO_ROOT / "extensions/arckit-vibe/skills/plantuml-syntax",
]

# Template sections that must be present (14 ## headings, in order)
TEMPLATE_SECTIONS = (
    "## Document Control",
    "## Revision History",
    "## Overview",
    "## Use Case Diagram",
    "## Sequence Diagram",
    "## Component Diagram",
    "## Deployment Diagram",
    "## Class Diagram",
    "## Object Diagram",
    "## Requirements Traceability",
    "## Design Rationale",
    "## Summary",
    "## External References",
)

# The 6 diagram types that each must appear in the template
DIAGRAM_TYPES = (
    "Use Case Diagram",
    "Sequence Diagram",
    "Component Diagram",
    "Deployment Diagram",
    "Class Diagram",
    "Object Diagram",
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_of(path: Path) -> dict:
    text = read(path)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{path.name}: YAML frontmatter missing or unparseable"
    fm = yaml.safe_load(match.group(1))
    assert isinstance(fm, dict), f"{path.name}: frontmatter is not a mapping"
    return fm


def mjs_multi_instance() -> set[str]:
    match = re.search(
        r"export\s+const\s+MULTI_INSTANCE_TYPES\s*=\s*new\s+Set\(\s*\[(.*?)\]\s*\)",
        read(DOC_TYPES_MJS),
        re.DOTALL,
    )
    assert match, "MULTI_INSTANCE_TYPES set not found in doc-types.mjs"
    body = re.sub(r"//[^\n]*", "", match.group(1))
    return set(re.findall(r"['\"]([A-Z0-9-]+)['\"]", body))


# ---------------------------------------------------------------------------
# doc-type registration
# ---------------------------------------------------------------------------

def test_soln_registered_in_doc_types():
    assert re.search(
        r"^\s*'SOLN':\s*\{\s*name:\s*'Solution Design',\s*category:\s*'Architecture'\s*\}",
        read(DOC_TYPES_MJS),
        re.MULTILINE,
    ), "SOLN missing from DOC_TYPES in doc-types.mjs"


def test_soln_is_multi_instance():
    # SOLN re-runs produce sequenced versions (v1.1, v1.2 …); the ID helper
    # must sequence it, so SOLN must be in MULTI_INSTANCE_TYPES.
    assert "SOLN" in mjs_multi_instance(), "SOLN missing from MULTI_INSTANCE_TYPES in doc-types.mjs"


def test_soln_in_generate_document_id():
    for label, path in (("repo-root", GEN_DOC_ID), ("plugin-tree", GEN_DOC_ID_PLG)):
        text = read(path)
        m = re.search(r'MULTI_INSTANCE_TYPES="([^"]*)"', text)
        assert m, f"{label}: MULTI_INSTANCE_TYPES line not found in {path.name}"
        assert "SOLN" in m.group(1), \
            f"SOLN missing from MULTI_INSTANCE_TYPES in {label} generate-document-id.sh"


def test_soln_in_pages_allowlist():
    assert re.search(r"\| *SOLN *\|", read(PAGES_CMD)), \
        "SOLN missing from the /arckit:pages known-artifact-types table"


# ---------------------------------------------------------------------------
# registry guard scripts
# ---------------------------------------------------------------------------

def test_registry_guard_scripts_pass():
    for guard in (
        "scripts/check-doc-type-registry.py",
        "scripts/check-multi-instance-parity.py",
        "scripts/check-guide-parity.py",
    ):
        path = REPO_ROOT / guard
        assert path.is_file(), f"{guard} missing"
        result = subprocess.run(
            ["python3", str(path)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, \
            f"{guard} failed:\n{result.stdout}\n{result.stderr}"


# ---------------------------------------------------------------------------
# command contract
# ---------------------------------------------------------------------------

def test_command_exists():
    assert COMMAND.is_file(), "solution-design.md missing"


def test_command_frontmatter_declares_soln_and_high_effort():
    fm = frontmatter_of(COMMAND)
    assert fm.get("doc-type") == "SOLN", f"doc-type frontmatter: {fm.get('doc-type')!r}"
    assert fm.get("effort") == "high", f"effort frontmatter: {fm.get('effort')!r}"
    assert "description" in fm, "description frontmatter missing"


def test_command_frontmatter_handoffs():
    fm = frontmatter_of(COMMAND)
    handoffs = fm.get("handoffs")
    assert isinstance(handoffs, list) and handoffs, "handoffs frontmatter missing or not a list"
    commands = [h["command"] for h in handoffs]
    for expected in ("hld-review", "dld-review", "traceability", "sow", "diagram"):
        assert expected in commands, f"handoff command {expected!r} missing from {commands}"


def test_command_requires_req_artefact():
    """The command must stop and flag when ARC-{P}-REQ-v*.md is missing."""
    text = read(COMMAND)
    assert "MANDATORY" in text, "MANDATORY clause missing from solution-design.md"
    assert "REQ" in text, "REQ reference missing from MANDATORY section"
    # The stop-behaviour sentence
    assert re.search(r"stop.*?requirements|requirements.*?stop", text, re.IGNORECASE), \
        "REQ stop-behaviour clause missing"


def test_command_has_six_diagram_types():
    text = read(COMMAND)
    for dt in DIAGRAM_TYPES:
        assert dt in text, f"Diagram type {dt!r} missing from command body"


def test_command_uses_claude_plugin_root_for_diag_generator():
    """After 11b943d7 the DIAG generator call must use the plugin-tree path
    convention:  bash "${CLAUDE_PLUGIN_ROOT}/scripts/bash/generate-document-id.sh"
    The old convention (.arckit/scripts/bash/…) with --next-num in the
    wrong position was the bug fixed in that commit."""
    text = read(COMMAND)
    assert "${CLAUDE_PLUGIN_ROOT}/scripts/bash/generate-document-id.sh" in text, \
        "DIAG generator must use ${CLAUDE_PLUGIN_ROOT} path convention"
    assert ".arckit/scripts/bash/generate-document-id.sh" not in text, \
        "stale .arckit/ path still present in solution-design.md"


# ---------------------------------------------------------------------------
# template conformance
# ---------------------------------------------------------------------------

def test_template_exists():
    assert TEMPLATE.is_file(), "solution-design-template.md missing"


def test_template_has_all_sections():
    text = read(TEMPLATE)
    for section in TEMPLATE_SECTIONS:
        assert section in text, f"Template section {section!r} missing"


def test_template_has_plantuml_blocks():
    text = read(TEMPLATE)
    start_count = len(re.findall(r"```plantuml", text))
    assert start_count >= 6, f"Expected at least 6 plantuml blocks, found {start_count}"
    assert text.count("@startuml") >= 6, "Missing @startuml openers"
    assert text.count("@enduml") >= 6, "Missing @enduml closers"


def test_template_has_view_diagram_callouts():
    text = read(TEMPLATE)
    assert "View this diagram" in text, \
        "'View this diagram' callout missing from template"


def test_template_dual_tree_copy_identical():
    """The .arckit/ copy in the project root must stay in sync with the
    canonical plugin-tree template."""
    assert TEMPLATE2.is_file(), ".arckit/templates/solution-design-template.md missing"
    assert read(TEMPLATE) == read(TEMPLATE2), \
        "Template dual-tree copies diverge (.arckit/ vs plugins/arckit-claude/)"


# ---------------------------------------------------------------------------
# skill + reference
# ---------------------------------------------------------------------------

def test_skill_rows_for_all_six_diagram_types():
    text = read(SKILL)
    for dt in DIAGRAM_TYPES:
        assert dt in text, f"{dt!r} missing from plantuml-syntax SKILL.md mapping table"
    # Each row should reference /arckit:solution-design
    soln_refs = len(re.findall(r"/arckit:solution-design", text))
    assert soln_refs >= 6, \
        f"Expected at least 6 /arckit:solution-design refs in SKILL.md, found {soln_refs}"


def test_object_diagrams_reference_in_source():
    assert OBJ_REF.is_file(), "plantuml-syntax/references/object-diagrams.md missing from source"


def test_object_diagrams_reference_in_extension_trees():
    """object-diagrams.md must be present in every extension tree that
    carries the plantuml-syntax skill.  Missing it means that tree's
    model has no syntax reference for the Object Diagram type."""
    missing = [
        p for p in PLANTUML_EXTENSION_SKILLS
        if not (p / "references" / "object-diagrams.md").is_file()
    ]
    assert not missing, \
        f"object-diagrams.md missing from extension trees: {missing}"


# ---------------------------------------------------------------------------
# guides
# ---------------------------------------------------------------------------

def test_guide_exists():
    assert GUIDE.is_file(), "docs/guides/solution-design.md missing"


def test_plugin_guide_tree_copy_is_identical():
    assert PLUGIN_GUIDE.is_file(), "plugins/arckit-claude/docs/guides/solution-design.md missing"
    assert read(GUIDE) == read(PLUGIN_GUIDE), \
        "Guide copy in plugin tree diverges from docs/guides/solution-design.md"


def test_guide_site_link():
    assert "solution-design" in read(SITE), \
        "solution-design link missing from docs/guides.html"


def test_guide_groups_entry():
    text = read(GUIDE_GROUPS)
    assert "solution-design" in text, \
        "'solution-design' missing from guide-groups.mjs"


# ---------------------------------------------------------------------------
# extension trees
# ---------------------------------------------------------------------------

def test_codex_prompt_exists():
    assert CODEX_PROMPT.is_file(), \
        "extensions/arckit-codex/prompts/arckit.solution-design.md missing"


def test_codex_command_exists():
    assert CODEX_CMD.is_file(), \
        "extensions/arckit-codex/commands/arckit.solution-design.md missing"


def test_codex_prompt_has_soln_frontmatter():
    """The Codex prompt is a converted artifact; its doc-type marker is
    embedded in the body (not YAML).  Check for the SOLN identifier."""
    text = read(CODEX_PROMPT)
    assert "SOLN" in text, "SOLN identifier missing from Codex prompt"

