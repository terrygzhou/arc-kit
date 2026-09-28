"""Codex extension parity guards for the PlantUML-ArchiMate diagram stack.

Regression guard for the gloryev incident: the *installed* Codex plugin
(6.8.0) had zero ArchiMate support (no command, no ADM ArchiMate template
sections, no plantuml-syntax ArchiMate reference), so generated artefacts
never carried ArchiMate views and no .svg diagrams were produced.

These tests assert the generated Codex extension surfaces the full
ArchiMate stack that exists in the Claude source:

* ``$arckit-archimate`` command-skill exists and carries the pinned include
  line + self-contained SVG delivery policy
* every generated ADM template that the demanded set guards
  (test_archimate_demanded.py) carries its ArchiMate view section in the
  Codex copy too
* the plantuml-syntax reference skill ships ``references/archimate.md``
  with the pinned include line
* the arckit-diagram command-skill mentions the ArchiMate production policy

Generated extensions are verified, not just the converter (repo guideline:
"For generated extension changes, test the generated output").
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_ROOT = REPO_ROOT / "extensions" / "arckit-codex"

PINNED_INCLUDE = "!include <archimate/Archimate>"

# Same demanded set as tests/plugin/test_archimate_demanded.py — the
# templates that SHALL carry a pinned ArchiMate base view.
DEMANDED_TEMPLATES = [
    # Mirrors test_archimate_demanded.py demanded set (base + companions),
    # mapped to the merged template filenames in the generated extension.
    "application-inventory-template.md",
    "rationalization-template.md",
    "capability-map-template.md",
    "tech-architecture-template.md",
    "transition-architecture-template.md",
    "gap-analysis-template.md",
    "data-architecture-template.md",
    "adm-preliminary-template.md",
    "discovery-template.md",
    "oaa-adm-lite-template.md",
    "product-architecture-template.md",
    "architecture-board-template.md",
]


def test_codex_extension_exists():
    assert CODEX_ROOT.is_dir(), "run `python scripts/converter.py` first"
    assert (CODEX_ROOT / ".codex-plugin" / "plugin.json").is_file()


def test_codex_archimate_command_skill_exists():
    skill = CODEX_ROOT / "skills" / "arckit-archimate" / "SKILL.md"
    assert skill.is_file(), (
        "$arckit-archimate command-skill missing from generated Codex "
        "extension — regenerate with `python scripts/converter.py`"
    )


def test_codex_archimate_skill_carries_pinned_include_and_svg_policy():
    text = (CODEX_ROOT / "skills" / "arckit-archimate" / "SKILL.md").read_text()
    assert PINNED_INCLUDE in text, "pinned ArchiMate include line missing"
    assert "self-contained" in text, (
        "self-contained .svg delivery policy missing from Codex archimate skill"
    )


def test_codex_adm_templates_carry_archimate_sections():
    """Every demanded template (Codex copy) carries a PlantUML-ArchiMate view."""
    templates_dir = CODEX_ROOT / "templates"
    missing = []
    for name in DEMANDED_TEMPLATES:
        path = templates_dir / name
        if not path.is_file():
            missing.append(f"{name} (file absent)")
            continue
        text = path.read_text()
        if PINNED_INCLUDE not in text:
            missing.append(name)
    assert not missing, (
        "Codex ADM templates missing the pinned ArchiMate include: "
        + ", ".join(missing)
    )


def test_codex_archimate_skill_registered_in_manifest():
    manifest = json.loads(
        (CODEX_ROOT / ".codex-plugin" / "plugin.json").read_text()
    )
    # The Codex manifest registers skills as a directory, not a file list
    # (test_codex_extension.py::test_codex_plugin_manifest_references_existing_components).
    assert manifest.get("skills") == "./skills/"
    # The skill must actually exist under that directory.
    assert (CODEX_ROOT / manifest["skills"].lstrip("./") / "arckit-archimate").is_dir()


def test_codex_plantuml_syntax_skill_ships_archimate_reference():
    ref = CODEX_ROOT / "skills" / "plantuml-syntax" / "references" / "archimate.md"
    assert ref.is_file(), (
        "archimate.md reference missing from generated Codex plantuml-syntax "
        "skill — the notation docs the archimate command points at"
    )
    assert PINNED_INCLUDE in ref.read_text(), "pinned include line missing in Codex copy"


def test_codex_diagram_skill_mentions_archimate_policy():
    text = (CODEX_ROOT / "skills" / "arckit-diagram" / "SKILL.md").read_text()
    assert "ArchiMate" in text, (
        "Codex arckit-diagram skill must route ArchiMate-representable "
        "diagrams to PlantUML ArchiMate per the Diagram Production Policy"
    )
