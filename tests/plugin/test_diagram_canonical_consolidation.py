"""Canonical project folder + diagram consolidation guard.

Regression guard for the gloryev incident (EYW-345): when build-config
``phase_ids`` map every phase to one base ID, artefacts land in a single
canonical folder (``001-glory-ev-customer-app``) while *older* builds
(clobbered ``{P}-{ID}`` values) left sibling per-phase folders
(``001-DATA-...`` etc.) holding stale artefacts and no diagrams.

Guards:

* the recipe default for every ADM target is the *canonical* project
  folder form (no per-phase suffix in the recipe itself — the phase
  folder comes only from an explicit user override of ``{P_<ID>}``)
* the diagram sweep, when a canonical folder holds artefacts for some
  types while stale per-phase folders hold others, reports the
  stale-folder split so the build summary can surface it
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import arckit_cli.diagrams as diagrams

REPO_ROOT = Path(__file__).resolve().parents[2]
ADM_RECIPE = (
    REPO_ROOT / "plugins" / "arckit-claude" / "plugins" / "togaf" / "adm"
    / "recipes" / "togaf-adm-full.yaml"
)


def test_adm_recipe_targets_use_phase_placeholder_folders():
    """Recipe outputs must use {P_<ID>}-{NAME} so user config can pin a
    single canonical folder (build-config phase_ids: {ID: "001"})."""
    raw = yaml.safe_load(ADM_RECIPE.read_text())
    targets = {t["id"]: t for t in raw["targets"]}
    phase_targets = [
        t for t in targets.values()
        if "{P_" in str(t.get("output", {}).get("project", ""))
    ]
    assert phase_targets, "no recipe target uses a {P_<ID>} phase folder"
    for t in phase_targets:
        proj = t["output"]["project"]
        # Exactly the canonical form: {P_<ID>}-{NAME} — nothing the user
        # can't override via build-config phase_ids.
        assert proj == "{P_" + proj.split("{P_")[1], (
            f"target {t['id']}: output.project {proj!r} is not the "
            "{P_<ID>}-{NAME} canonical form"
        )


def test_sweep_reports_stale_per_phase_folders(tmp_path, monkeypatch):
    """Stale sibling folders with artefacts but no diagrams are surfaced."""
    root = tmp_path / "projects"
    canonical = root / "001-Foo"
    stale = root / "001-FOO-bar"
    canonical.mkdir(parents=True)
    stale.mkdir(parents=True)
    (canonical / "ARC-001-TECH-v1.0.md").write_text(
        "## PlantUML ArchiMate View\n```plantuml\n@startuml\nx\n@enduml\n```\n",
        encoding="utf-8",
    )
    (stale / "ARC-001-DATA-v1.0.md").write_text("# Data (stale folder, no view)\n", encoding="utf-8")
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)

    summary = diagrams.consolidate_project_diagrams(tmp_path)

    # The sweep must report the stale folder split: one folder with
    # artefacts but zero inline PlantUML blocks.
    assert summary["stale_folders"] == [str(stale.relative_to(tmp_path))]


def test_sweep_no_stale_report_when_single_folder(tmp_path, monkeypatch):
    root = tmp_path / "projects"
    proj = root / "001-Foo"
    proj.mkdir(parents=True)
    (proj / "doc.md").write_text(
        "```plantuml\n@startuml\nx\n@enduml\n```\n", encoding="utf-8"
    )
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)

    summary = diagrams.consolidate_project_diagrams(tmp_path)

    assert summary.get("stale_folders", []) == []
