"""Tests for /arckit:archimate and the ARCH doc-type registration.

Mirrors the registration-point discipline established by CDAU
(tests/plugin/test_repo_audit.py): every point that fails silently when
missed gets a guard here.

  - ARCH in doc-types.mjs DOC_TYPES / MULTI_INSTANCE_TYPES / SUBDIR_MAP
  - ARCH in the /arckit:pages allow-list (dual registration)
  - MULTI_INSTANCE_TYPES parity with both bash copies
  - archimate-template.md: pinned ArchiMate include line, no placeholder leaks
  - commands/archimate.md frontmatter (doc-type: ARCH, effort: high) +
    multi-instance ID helper usage
  - every tracked quality-checklist.md copy carries the ARCH section
  - docs/DIAGRAMS.md maps the generated path to /arckit:archimate
"""

import glob
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_TYPES_MJS = REPO_ROOT / "plugins/arckit-claude/config/doc-types.mjs"
PAGES_CMD = REPO_ROOT / "plugins/arckit-claude/commands/pages.md"
COMMAND = REPO_ROOT / "plugins/arckit-claude/commands/archimate.md"
TEMPLATE = REPO_ROOT / "plugins/arckit-claude/templates/archimate-template.md"
DIAGRAMS_MD = REPO_ROOT / "docs/DIAGRAMS.md"
BASH_COPIES = (
    REPO_ROOT / "scripts/bash/generate-document-id.sh",
    REPO_ROOT / "plugins/arckit-claude/scripts/bash/generate-document-id.sh",
)

# Same tracked-copy set as test_adm_doc_control_conformance.py.
CHECKLIST_GLOBS = (
    "plugins/arckit-*/references/quality-checklist.md",
    "plugins/arckit-claude/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/*/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/*/*/references/quality-checklist.md",
    "scripts/autoresearch/program.md",
)

# Pinned API (skills/plantuml-syntax/references/archimate.md, pinned 2026-09-13
# against PlantUML 1.2026.8). Changing the include line is a Pinned API change:
# update the pin date + re-render tests/fixtures/archimate/ first.
PINNED_INCLUDE = "!include <archimate/Archimate>"

# Curly-brace field tokens the archimate template may ship (the command
# resolves every one of them). Anything else is a leaked placeholder.
KNOWN_TEMPLATE_TOKENS = {
    "abstract",
    "alias",
    "archimate_view",
    "count",
    "description",
    "diagram_name",
    "element",
    "elements",
    "from",
    "how",
    "label",
    "layers",
    "motivation",
    "owner",
    "protocol",
    "relationship",
    "responsibility",
    "target",
    "to",
    "type",
}

CHECKLIST_SECTION = "ARCH -- ArchiMate View"


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


def bash_multi_instance(path: Path) -> set[str]:
    match = re.search(r'^MULTI_INSTANCE_TYPES="([^"]*)"', read(path), re.MULTILINE)
    assert match, f"MULTI_INSTANCE_TYPES assignment not found in {path}"
    return set(match.group(1).split())


def frontmatter_of(path: Path) -> dict:
    text = read(path)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{path.name}: YAML frontmatter missing or unparseable"
    fm = yaml.safe_load(match.group(1))
    assert isinstance(fm, dict), f"{path.name}: frontmatter is not a mapping"
    return fm


# --- doc-type registration ------------------------------------------------


def test_arch_registered_in_doc_types():
    assert re.search(
        r"^\s*'ARCH':\s*\{\s*name:\s*'ArchiMate View',\s*category:\s*'Architecture'",
        read(DOC_TYPES_MJS),
        re.MULTILINE,
    ), "ARCH missing from DOC_TYPES (name: ArchiMate View, category: Architecture)"


def test_arch_is_multi_instance():
    # A project can carry several ArchiMate views (layer per view); without
    # this the ID helper overwrites the previous view instead of sequencing.
    assert "ARCH" in mjs_multi_instance()


def test_arch_maps_to_diagrams_subdir():
    assert re.search(r"'ARCH':\s*'diagrams'", read(DOC_TYPES_MJS)), \
        "ARCH missing from SUBDIR_MAP or not mapped to 'diagrams'"


def test_arch_does_not_collide_with_an_existing_code():
    codes = re.findall(r"^\s*'([A-Z0-9-]+)':\s*\{", read(DOC_TYPES_MJS), re.MULTILINE)
    assert codes.count("ARCH") == 1, f"ARCH declared {codes.count('ARCH')} times"


def test_arch_in_pages_allowlist():
    # Dual registration: /arckit:pages keeps its own allow-list inside the
    # prompt. Without a row the view is silently absent from the dashboard.
    assert re.search(r"\| *ARCH *\|", read(PAGES_CMD)), \
        "ARCH missing from the /arckit:pages allow-list"


@pytest.mark.parametrize("bash_path", BASH_COPIES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_multi_instance_parity_with_bash(bash_path: Path):
    expected = mjs_multi_instance()
    actual = bash_multi_instance(bash_path)
    assert actual == expected, (
        f"MULTI_INSTANCE_TYPES drift in {bash_path.relative_to(REPO_ROOT)}: "
        f"missing={sorted(expected - actual)} extra={sorted(actual - expected)}"
    )


def test_registry_guard_script_passes():
    guard = REPO_ROOT / "scripts/check-doc-type-registry.py"
    assert guard.is_file(), "check-doc-type-registry.py missing"
    result = subprocess.run(
        ["python3", str(guard)], capture_output=True, text=True, cwd=REPO_ROOT
    )
    assert result.returncode == 0, f"registry guard failed:\n{result.stdout}\n{result.stderr}"


# --- template ---------------------------------------------------------------


def test_template_exists():
    assert TEMPLATE.is_file(), "archimate-template.md missing from arckit-claude"


def test_template_carries_pinned_include():
    text = read(TEMPLATE)
    assert PINNED_INCLUDE in text, f"pinned include line missing: {PINNED_INCLUDE}"
    assert "@startuml" in text and "@enduml" in text, \
        "PlantUML block must be wrapped in @startuml/@enduml"


def test_template_has_no_unresolved_placeholders():
    # Outside fenced code blocks every {token} must be a registered template
    # field; a typo'd or invented token would ship into generated views.
    text = read(TEMPLATE)
    stripped = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    found = set(re.findall(r"\{([a-z][a-z0-9_]*)\}", stripped))
    unknown = found - KNOWN_TEMPLATE_TOKENS
    assert not unknown, f"unknown placeholder tokens in archimate-template.md: {sorted(unknown)}"


# --- command contract -------------------------------------------------------


def test_command_exists():
    assert COMMAND.is_file(), "archimate.md missing"


def test_command_frontmatter_declares_arch_and_high_effort():
    fm = frontmatter_of(COMMAND)
    assert fm.get("doc-type") == "ARCH", f"doc-type frontmatter: {fm.get('doc-type')!r}"
    assert fm.get("effort") == "high", f"effort frontmatter: {fm.get('effort')!r}"
    assert "description" in fm, "description frontmatter missing"


def test_command_writes_arch_via_helper():
    body = read(COMMAND)
    assert "generate-document-id.sh" in body
    assert "--next-num" in body, "multi-instance types require --next-num"
    assert "ARCH" in body
    assert "diagrams/" in body, "generated views must land in projects/{p}/diagrams/"


# --- quality checklist lockstep ---------------------------------------------


def test_every_quality_checklist_copy_has_arch_section():
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


# --- docs mapping -----------------------------------------------------------


def test_diagrams_md_maps_generated_path_to_archimate_command():
    text = read(DIAGRAMS_MD)
    assert "/arckit:archimate" in text, \
        "docs/DIAGRAMS.md must map the generated ArchiMate path to /arckit:archimate"
    assert re.search(r"ARC-[A-Z0-9*-]*ARCH", text), \
        "docs/DIAGRAMS.md must show the ARC-*-ARCH-* artifact pattern"


# --- ArchiMate SVG self-containment (OpenSpec archimate-svg-delivery) -------
#
# The Diagram Production Policy (skills/plantuml-syntax/references/archimate.md,
# § Diagram Production Policy + § Offline Self-Contained SVG Rendering) requires
# emitted ArchiMate .svg deliverables to be self-contained: rendered offline
# against the pinned jar, with no external URL beyond the W3C XML namespace
# declarations and no `xlink:href` pointing off-file. The committed fixture
# three-layer.svg is the render-truth reference.

FIXTURE_SVG = REPO_ROOT / "tests/fixtures/archimate/three-layer.svg"
ARCHIMATE_REFERENCE = REPO_ROOT / "plugins/arckit-claude/skills/plantuml-syntax/references/archimate.md"

# The only URLs a self-contained ArchiMate SVG may carry: W3C XML namespace
# declarations. Anything else is an external (server/CDN) dependency.
ALLOWED_URLS = {
    "http://www.w3.org/2000/svg",
    "http://www.w3.org/1999/xlink",
}


def extract_urls(svg_text: str) -> set[str]:
    return set(re.findall(r"https?://[^\"' )>]+", svg_text))


def extract_xlink_hrefs(svg_text: str) -> set[str]:
    return set(re.findall(r"""xlink:href=["\']([^"\']*)["\']""", svg_text))


def test_fixture_svg_is_self_contained():
    assert FIXTURE_SVG.is_file(), "render-truth fixture three-layer.svg missing"
    text = read(FIXTURE_SVG)
    urls = extract_urls(text) - ALLOWED_URLS
    assert not urls, f"fixture SVG carries external URLs (breaks offline delivery): {sorted(urls)}"
    for href in extract_xlink_hrefs(text):
        assert href.startswith("#"), f"fixture SVG xlink:href escapes the file: {href!r}"


@pytest.mark.parametrize("svg_path", sorted(glob.glob(str(REPO_ROOT / "projects/**/*.svg"), recursive=True)))
def test_project_archimate_svgs_are_self_contained(svg_path: str):
    # Any ArchiMate SVG committed under a project's diagrams/ tree must satisfy
    # the same self-containment standard as the fixture.
    text = read(Path(svg_path))
    urls = extract_urls(text) - ALLOWED_URLS
    assert not urls, f"{svg_path}: external URL in self-contained ArchiMate SVG: {sorted(urls)}"
    for href in extract_xlink_hrefs(text):
        assert href.startswith("#"), f"{svg_path}: xlink:href escapes the file: {href!r}"


def test_reference_documents_diagram_production_policy():
    text = read(ARCHIMATE_REFERENCE)
    assert "## Diagram Production Policy" in text, \
        "archimate.md reference missing the Diagram Production Policy section"
    assert "## Offline Self-Contained SVG Rendering" in text, \
        "archimate.md reference missing the Offline Self-Contained SVG Rendering section"
    # The two policy points the OpenSpec spec locks: (c) .svg is the only new
    # emitted file, and self-containment is the delivery expectation.
    assert "only new file" in text, "policy must state the .svg is the only new emitted file"


def test_command_quality_gate_has_self_contained_svg_criterion():
    text = read(COMMAND)
    assert "Self-contained SVG" in text, \
        "archimate.md quality gate missing the self-contained-SVG deliverable criterion"
