"""Tests for /arckit:bmm and the BMM doc-type registration.

OpenSpec change: bmm-adoption. Mirrors the registration-point discipline
established by the ARCH guard (tests/plugin/test_archimate_conformance.py):
every point that fails silently when missed gets a guard here.

  - BMM in doc-types.mjs DOC_TYPES (category Planning) and ABSENT from
    MULTI_INSTANCE_TYPES / SUBDIR_MAP (single-instance, root-level artefact)
  - BMM in the /arckit:pages allow-list (dual registration)
  - commands/bmm.md frontmatter (doc-type: BMM, effort: max, handoffs
    strategy/roadmap/sobc/archimate) + single-call intake + ARCH-view helper
  - templates/bmm-template.md: 9 pipeline sections + Document Control +
    generation footer, no leaked placeholders
  - references/bmm-reference.md: element catalogue + mapping tables
  - skills/plantuml-syntax/references/archimate.md carries a
    § BMM Projection section; pre-change sections stay byte-identical
    (SHA-256 fixture, archimate-demanded-artefacts pattern)
  - tests/fixtures/archimate/bmm/ spike fixture: rendered .puml + .svg
    pairs, SVGs self-contained (no external URL beyond W3C namespaces)
  - plantuml-syntax SKILL.md mapping row; the existing
    **/ARC-*-ARCH-*.md glob already covers BMM-carrying views
  - every tracked quality-checklist.md copy carries the BMM section
  - strategy.md / sobc.md traceability clauses (Option C slice)
  - docs/guides/bmm.md (+ plugin-tree copy, site link, llms.txt, OAA pointer)
  - 77 .md files in plugins/arckit-claude/commands/
"""

import glob
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_TYPES_MJS = REPO_ROOT / "plugins/arckit-claude/config/doc-types.mjs"
PAGES_CMD = REPO_ROOT / "plugins/arckit-claude/commands/pages.md"
COMMAND = REPO_ROOT / "plugins/arckit-claude/commands/bmm.md"
TEMPLATE = REPO_ROOT / "plugins/arckit-claude/templates/bmm-template.md"
REFERENCE = REPO_ROOT / "plugins/arckit-claude/references/bmm-reference.md"
ARCHIMATE_REFERENCE = REPO_ROOT / "plugins/arckit-claude/skills/plantuml-syntax/references/archimate.md"
SKILL = REPO_ROOT / "plugins/arckit-claude/skills/plantuml-syntax/SKILL.md"
BMM_FIXTURE_DIR = REPO_ROOT / "tests/fixtures/archimate/bmm"
SECTION_FIXTURE = REPO_ROOT / "tests/plugin/fixtures/bmm-archimate-ref/prechange_sections.json"
STRATEGY_CMD = REPO_ROOT / "plugins/arckit-claude/commands/strategy.md"
SOBC_CMD = REPO_ROOT / "plugins/arckit-claude/commands/sobc.md"
GUIDE = REPO_ROOT / "docs/guides/bmm.md"
PLUGIN_GUIDE = REPO_ROOT / "plugins/arckit-claude/docs/guides/bmm.md"
LLMS_TXT = REPO_ROOT / "docs/llms.txt"
OAA_MAPPING = REPO_ROOT / "docs/OAA-PLUGIN-MAPPING.md"
COMMANDS_DIR = REPO_ROOT / "plugins/arckit-claude/commands"

# Same tracked-copy set as test_archimate_conformance.py.
CHECKLIST_GLOBS = (
    "plugins/arckit-*/references/quality-checklist.md",
    "plugins/arckit-claude/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/*/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/*/*/references/quality-checklist.md",
    "scripts/autoresearch/program.md",
)

CHECKLIST_SECTION = "BMM -- Business Motivation Model"

# The 9 [A1] model sections (design.md § Artefact Pipeline, Stage 1).
TEMPLATE_SECTIONS = (
    "## 1. Stakeholders & Outcomes",
    "## 2. Outcomes → Goals → Objectives → Measures",
    "## 3. Drivers",
    "## 4. Assumptions",
    "## 5. Case For / Case Against",
    "## 6. Impact Factors",
    "## 7. Strategic Themes → Capabilities → Courses of Action → Resources",
    "## 8. Traceability",
    "## 9. Mermaid Mindmap",
)

# The only URLs a self-contained ArchiMate SVG may carry: W3C XML namespace
# declarations. Anything else is an external (server/CDN) dependency.
ALLOWED_URLS = {
    "http://www.w3.org/2000/svg",
    "http://www.w3.org/1999/xlink",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def mjs_multi_instance() -> set[str]:
    match = re.search(
        r"export\s+const\s+MULTI_INSTANCE_TYPES\s*=\s*new\s+Set\(\s*\[(.*?)\]\s*\)",
        read(DOC_TYPES_MJS),
        re.DOTALL,
    )
    assert match, "MULTI_INSTANCE_TYPES set not found in doc-types.mjs"
    body = re.sub(r"//[^\n]*", "", match.group(1))
    return set(re.findall(r"['\"]([A-Z0-9-]+)['\"]", body))


def mjs_subdir_map() -> dict[str, str]:
    match = re.search(
        r"export\s+const\s+SUBDIR_MAP\s*=\s*\{(.*?)\n\};",
        read(DOC_TYPES_MJS),
        re.DOTALL,
    )
    assert match, "SUBDIR_MAP not found in doc-types.mjs"
    return dict(re.findall(r"['\"]([A-Z0-9-]+)['\"]\s*:\s*['\"]([a-z0-9-]+)['\"]", match.group(1)))


def frontmatter_of(path: Path) -> dict:
    text = read(path)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{path.name}: YAML frontmatter missing or unparseable"
    fm = yaml.safe_load(match.group(1))
    assert isinstance(fm, dict), f"{path.name}: frontmatter is not a mapping"
    return fm


def split_sections(text: str) -> dict[str, str]:
    """Split a reference file into top-level `## ` sections (keyed by heading),
    with the content before the first heading under '_preamble'."""
    sections: dict[str, str] = {}
    current = "_preamble"
    buf: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            sections[current] = "".join(buf)
            current = line[3:].rstrip("\n")
            buf = [line]
        else:
            buf.append(line)
    sections[current] = "".join(buf)
    return sections


# --- doc-type registration ------------------------------------------------


def test_bmm_registered_in_doc_types():
    assert re.search(
        r"^\s*'BMM':\s*\{\s*name:\s*'Business Motivation Model',\s*category:\s*'Planning'\s*\}",
        read(DOC_TYPES_MJS),
        re.MULTILINE,
    ), "BMM missing from DOC_TYPES (name: Business Motivation Model, category: Planning)"


def test_bmm_is_single_instance():
    # One BMM model per project (like STRAT/SOBC): without this exclusion the
    # ID helper would sequence BMM documents and overwrite the canonical one.
    assert "BMM" not in mjs_multi_instance()


def test_bmm_has_no_subdir_mapping():
    # Single-instance root-level artefact: projects/{p}/ARC-{P}-BMM-v1.0.md,
    # never a subdirectory.
    assert "BMM" not in mjs_subdir_map(), \
        "BMM must not map to a subdirectory (root-level single-instance artefact)"


def test_bmm_does_not_collide_with_an_existing_code():
    codes = re.findall(r"^\s*'([A-Z0-9-]+)':\s*\{", read(DOC_TYPES_MJS), re.MULTILINE)
    assert codes.count("BMM") == 1, f"BMM declared {codes.count('BMM')} times"


def test_bmm_in_pages_allowlist():
    # Dual registration: /arckit:pages keeps its own allow-list inside the
    # prompt. Without a row the model is silently absent from the dashboard.
    assert re.search(r"\| *BMM *\|", read(PAGES_CMD)), \
        "BMM missing from the /arckit:pages allow-list"


def test_registry_guard_scripts_pass():
    for guard in (
        "scripts/check-doc-type-registry.py",
        "scripts/check_doctype_collisions.py",
        "scripts/check-multi-instance-parity.py",
    ):
        path = REPO_ROOT / guard
        assert path.is_file(), f"{guard} missing"
        result = subprocess.run(
            ["python3", str(path)], capture_output=True, text=True, cwd=REPO_ROOT
        )
        assert result.returncode == 0, f"{guard} failed:\n{result.stdout}\n{result.stderr}"


# --- command contract -------------------------------------------------------


def test_command_exists():
    assert COMMAND.is_file(), "bmm.md missing"


def test_command_frontmatter_declares_bmm_and_max_effort():
    fm = frontmatter_of(COMMAND)
    assert fm.get("doc-type") == "BMM", f"doc-type frontmatter: {fm.get('doc-type')!r}"
    assert fm.get("effort") == "max", f"effort frontmatter: {fm.get('effort')!r}"
    assert "description" in fm, "description frontmatter missing"


def test_command_frontmatter_handoffs():
    fm = frontmatter_of(COMMAND)
    handoffs = fm.get("handoffs")
    assert isinstance(handoffs, list) and handoffs, "handoffs frontmatter missing or not a list"
    commands = {entry.get("command") for entry in handoffs if isinstance(entry, dict)}
    missing = {"strategy", "roadmap", "sobc", "archimate"} - commands
    assert not missing, f"handoff commands missing: {sorted(missing)}"
    for entry in handoffs:
        assert isinstance(entry.get("description"), str) and entry["description"], \
            f"handoff entry missing description: {entry}"


def test_command_intake_single_call_max_two_rounds():
    body = read(COMMAND)
    assert "single AskUserQuestion call" in body, \
        "intake interview must ask both questions in a single AskUserQuestion call"
    assert "Maximum 2 rounds" in body, "intake gathering rules missing the max-2-rounds bound"


def test_command_writes_arch_views_via_helper():
    body = read(COMMAND)
    assert "generate-document-id.sh" in body, "views must use the bundled document-ID helper"
    assert "--next-num" in body, "BMM views sequence into the shared ARCH sequence (--next-num)"
    assert "ARCH" in body
    assert "diagrams/" in body, "views must land in projects/{p}/diagrams/"
    assert "renumber" in body.lower(), \
        "the never-renumber-existing-ARCH-docs rule (G5) must be stated"


def test_command_loads_bmm_reference():
    body = read(COMMAND)
    assert "references/bmm-reference.md" in body
    assert "skills/plantuml-syntax/references/archimate.md" in body
    assert "BMM Projection" in body, \
        "the command must load the archimate reference § BMM Projection for view encoding"


def test_command_carries_gates_g1_to_g5():
    body = read(COMMAND)
    for gate in ("G1", "G2", "G3", "G4", "G5"):
        assert gate in body, f"quality gate {gate} missing from the command"
    assert "3 iterations" in body or "three iterations" in body.lower(), \
        "the 3-iteration remediation loop is missing"


def test_command_has_self_contained_svg_clause():
    # [D*] delivery: pinned jar, offline, .svg is the only new rendered file.
    body = read(COMMAND)
    assert "plantuml-1.2026.8.jar -tsvg" in body
    assert "Offline Self-Contained SVG Rendering" in body


# --- template ---------------------------------------------------------------


def test_template_exists():
    assert TEMPLATE.is_file(), "bmm-template.md missing from arckit-claude"


def test_template_has_all_nine_pipeline_sections():
    text = read(TEMPLATE)
    missing = [s for s in TEMPLATE_SECTIONS if s not in text]
    assert not missing, f"missing pipeline sections in bmm-template.md: {missing}"
    assert "Matrix" in text, "stakeholder–outcome matrix table missing"
    assert "mermaid" in text.lower(), "Mermaid mindmap companion block missing"


def test_template_has_document_control_and_footer():
    text = read(TEMPLATE)
    assert "<!-- DOC-CONTROL-HEADER -->" in text, \
        "the 14-field Document Control marker is missing"
    assert "Revision History" in text, "Revision History table missing"
    assert "**Generated by**" in text and "ArcKit Version" in text, \
        "generation metadata footer missing"


def test_template_has_no_unresolved_placeholders():
    # Outside fenced code blocks every {token} is an unresolved placeholder
    # (house style uses bracket [TOKENS] for template fields); a curly token
    # leaking out would ship into the generated model.
    text = read(TEMPLATE)
    stripped = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    found = set(re.findall(r"\{([a-z][a-z0-9_]*)\}", stripped))
    assert not found, f"unresolved placeholder tokens in bmm-template.md: {sorted(found)}"


# --- reference ----------------------------------------------------------------


def test_bmm_reference_exists_with_tables():
    text = read(REFERENCE)
    assert "BMM 1.3 element catalogue" in text, "element catalogue table missing"
    assert "| BMM element |" in text, "BMM ↔ ArchiMate ↔ ArcKit mapping table missing"
    assert "Green Book" in text, "UK Green-Book alignment note missing"
    for gate in ("G1", "G2", "G3", "G4", "G5"):
        assert gate in text, f"gate {gate} missing from the reference"


# --- diagram layer (append-only) ----------------------------------------------


def test_archimate_reference_has_bmm_projection_section():
    text = read(ARCHIMATE_REFERENCE)
    assert "## BMM Projection" in text, "archimate.md missing the § BMM Projection section"
    section = split_sections(text)["BMM Projection"]
    for marker in ("Objective", "Measure", "Theme", "Motivation_Goal", "Strategy_Capability",
                   "legend", "tests/fixtures/archimate/bmm/"):
        assert marker in section, f"§ BMM Projection missing {marker!r}"


def test_archimate_reference_prebmm_sections_byte_preserved():
    # Section bodies are hashed with trailing newlines normalised (rstrip("\n"))
    # so a later append-only top-level section (which extends the previous
    # section's body by its separator line) cannot invalidate a pre-change hash.
    snap = json.loads(read(SECTION_FIXTURE))
    current = split_sections(read(ARCHIMATE_REFERENCE))
    for name, meta in snap["sections"].items():
        assert name in current, f"pre-BMM section {name!r} no longer exists (renamed or merged)"
        actual = hashlib.sha256(current[name].rstrip("\n").encode("utf-8")).hexdigest()
        assert actual == meta["sha256"], (
            f"pre-BMM section {name!r} is no longer byte-identical — BMM Projection "
            f"edits must be append-only"
        )


def test_archimate_reference_section_fixture_well_formed():
    snap = json.loads(read(SECTION_FIXTURE))
    assert snap["file"] == str(ARCHIMATE_REFERENCE.relative_to(REPO_ROOT)), \
        "fixture targets the wrong reference file"
    for name, meta in snap["sections"].items():
        assert len(meta["sha256"]) == 64, f"{name!r}: bad sha256 in fixture"
        assert meta["lines"] > 0, f"{name!r}: fixture section has zero lines"
    assert "BMM Projection" not in snap["sections"], \
        "fixture must not include the BMM Projection section itself"


def test_bmm_spike_fixture_pairs_rendered():
    pumls = sorted(p.name for p in BMM_FIXTURE_DIR.glob("*.puml"))
    svgs = sorted(p.name for p in BMM_FIXTURE_DIR.glob("*.svg"))
    assert pumls, "tests/fixtures/archimate/bmm/ has no .puml spike samples"
    for puml in pumls:
        svg = puml.replace(".puml", ".svg")
        assert svg in svgs, f"{puml} has no rendered .svg sibling ({svg})"
        puml_text = read(BMM_FIXTURE_DIR / puml)
        assert "!include <archimate/Archimate>" in puml_text, \
            f"{puml} missing the pinned include line"
        assert "@startuml" in puml_text and "@enduml" in puml_text


@pytest.mark.parametrize("svg_name", ["bmm-motivation.svg", "bmm-strategy.svg", "bmm-ladder.svg"])
def test_bmm_fixture_svgs_are_self_contained(svg_name: str):
    path = BMM_FIXTURE_DIR / svg_name
    assert path.is_file(), f"spike fixture {svg_name} missing"
    text = read(path)
    urls = set(re.findall(r"https?://[^\"' )>]+", text)) - ALLOWED_URLS
    assert not urls, f"{svg_name} carries external URLs (breaks offline delivery): {sorted(urls)}"
    for href in re.findall(r"""xlink:href=["\']([^"\']*)["\']""", text):
        assert href.startswith("#"), f"{svg_name} xlink:href escapes the file: {href!r}"


# --- skill mapping -------------------------------------------------------------


def test_skill_mapping_row_for_bmm_views():
    text = read(SKILL)
    assert "/arckit:bmm" in text, \
        "plantuml-syntax SKILL.md missing the BMM mapping row"
    assert "BMM Projection" in text, \
        "the mapping row must point at references/archimate.md § BMM Projection"


def test_arch_glob_covers_bmm_carrying_views():
    # BMM views are sequenced ARCH documents (ARC-{P}-ARCH-{NNN}-v1.0.md);
    # the existing skill glob already covers them — no new glob needed.
    fm = frontmatter_of(SKILL)
    assert "**/ARC-*-ARCH-*.md" in fm.get("paths", []), \
        "the ARCH artifact glob (covering BMM views) is missing from the skill paths"


# --- quality checklist lockstep ---------------------------------------------


def test_every_quality_checklist_copy_has_bmm_section():
    copies = sorted(set(
        Path(p) for pattern in CHECKLIST_GLOBS
        for p in glob.glob(str(REPO_ROOT / pattern), recursive=True)
    ))
    assert copies, "no quality-checklist copies found — glob drift?"
    missing = []
    checked = 0
    for path in copies:
        text = read(path)
        if "Per-Type Checks" not in text:
            continue  # not a checklist copy (e.g. scripts/autoresearch/program.md)
        checked += 1
        if CHECKLIST_SECTION not in text:
            missing.append(str(path.relative_to(REPO_ROOT)))
    assert checked >= 31, f"expected >= 31 checklist copies, checked {checked}"
    assert not missing, f"missing '{CHECKLIST_SECTION}': {missing}"


# --- Option C slice: traceability clauses --------------------------------------


def test_strategy_consumes_bmm_themes():
    text = read(STRATEGY_CMD)
    assert "BMM" in text, \
        "strategy.md must name the BMM Strategic-Theme traceability clause"


def test_sobc_maps_bmm_case_sections():
    text = read(SOBC_CMD)
    assert "BMM" in text, \
        "sobc.md must carry the 5-case ↔ BMM Case section mapping clause"
    assert "UK" in text, "the Green-Book mapping is UK-regime — say so"


# --- docs lockstep --------------------------------------------------------------


def test_guide_exists():
    assert GUIDE.is_file(), "docs/guides/bmm.md missing"
    text = read(GUIDE)
    assert "/arckit:bmm" in text
    assert "BMM 1.3" in text


def test_plugin_guide_tree_copy_is_identical():
    # check-guide-parity.py enforces byte-identity for guides present in both
    # trees; a core (shipped) guide must be in both.
    assert PLUGIN_GUIDE.is_file(), \
        "plugins/arckit-claude/docs/guides/bmm.md missing — the guide ships to extensions"
    assert PLUGIN_GUIDE.read_bytes() == GUIDE.read_bytes(), \
        "plugin-tree guide copy drifted from the root copy"


def test_guide_site_links_and_parity_scripts_pass():
    for guard in ("scripts/check-guide-site-links.py", "scripts/check-guide-parity.py"):
        result = subprocess.run(
            ["python3", str(REPO_ROOT / guard)], capture_output=True, text=True, cwd=REPO_ROOT
        )
        assert result.returncode == 0, f"{guard} failed:\n{result.stdout}\n{result.stderr}"


def test_llms_txt_has_bmm_entry():
    assert "/arckit:bmm" in read(LLMS_TXT), "docs/llms.txt missing the /arckit:bmm command entry"


def test_oaa_mapping_pointer_mentions_bmm():
    text = read(OAA_MAPPING)
    assert "BMM" in text, "OAA-PLUGIN-MAPPING.md missing the BMM ↔ OASTR pointer"


# --- command count ----------------------------------------------------------------


def test_commands_directory_has_77_md_files():
    count = len(list(COMMANDS_DIR.glob("*.md")))
    assert count == 77, f"expected 77 command files, found {count}"
