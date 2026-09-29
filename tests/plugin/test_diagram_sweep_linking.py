"""Post-build diagram sweep: cross-linking + coverage guarantees.

Regression guard for the gloryev incident (EYW-345/348): the post-build
sweep (``consolidate_project_diagrams``) materialised ``.puml`` sidecars
and ``.svg`` renders under each project's ``diagrams/`` folder, but the
generated artefacts (a) never linked the rendered SVGs, (b) silently
skipped docs whose types carry no ArchiMate view (ADMP/BPCM/STKE), and
(c) left the canonical folder and the per-phase subfolders
(``001-ADMP-...`` vs ``001-...``) inconsistent with each other.

These tests guard the sweep's *linking* step: after consolidation, every
source document that gained sidecars is cross-linked from its
``diagrams/manifest.json`` (the link of record — the LLM-generated
arteffact text is not reliably editable by the CLI), and the sweep
reports per-document coverage so callers can surface gaps.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import arckit_cli.diagrams as diagrams


def _project_with_blocks(tmp_path: Path) -> Path:
    proj = tmp_path / "projects" / "001-Foo"
    proj.mkdir(parents=True)
    (proj / "ARC-001-TECH-v1.0.md").write_text(
        "# Tech\n\n## PlantUML ArchiMate View\n\n"
        "```plantuml\n@startuml\nrectangle \"App\"\n@enduml\n```\n",
        encoding="utf-8",
    )
    (proj / "ARC-001-BPCM-v1.0.md").write_text("# Capmap (no view)\n", encoding="utf-8")
    return proj


def test_sweep_manifest_links_documents_to_sidecars(tmp_path, monkeypatch):
    """manifest.json must record which documents each sidecar came from."""
    proj = _project_with_blocks(tmp_path)
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)

    summary = diagrams.consolidate_project_diagrams(tmp_path)

    manifest = json.loads((proj / "diagrams" / "manifest.json").read_text())
    blocks = manifest["blocks"]
    assert len(blocks) == 1
    entry = next(iter(blocks.values()))
    # The link of record: the source document that owns this sidecar.
    assert entry.get("source_doc") == "001-Foo/ARC-001-TECH-v1.0.md", (
        "manifest entry must record the source document relative to "
        "projects/ (the artefact→diagram link the CLI can guarantee)"
    )
    # Coverage report: every doc scanned, with its block count, so the
    # build summary can surface docs that gained no diagrams.
    assert summary["docs_without_blocks"] == 1  # BPCM doc
    assert summary["docs_scanned"] == 1


def test_sweep_rerun_preserves_document_links(tmp_path, monkeypatch):
    proj = _project_with_blocks(tmp_path)
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)

    diagrams.consolidate_project_diagrams(tmp_path)
    second = diagrams.consolidate_project_diagrams(tmp_path)

    # No jar: status is "pending" (not "rendered"), so the sidecar is
    # re-written each run — but the manifest entry must still carry the
    # source_doc link on every pass.
    assert second["puml_written"] == 1
    manifest = json.loads((proj / "diagrams" / "manifest.json").read_text())
    entry = next(iter(manifest["blocks"].values()))
    assert entry.get("source_doc") == "001-Foo/ARC-001-TECH-v1.0.md"


def test_sweep_links_survive_source_doc_removal(tmp_path, monkeypatch):
    """Removing the source doc must not orphan sidecars silently."""
    proj = _project_with_blocks(tmp_path)
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)
    diagrams.consolidate_project_diagrams(tmp_path)

    (proj / "ARC-001-TECH-v1.0.md").unlink()
    summary = diagrams.consolidate_project_diagrams(tmp_path)

    # Orphaned sidecars are reported, not deleted (rendered output is an
    # intentional deliverable — the human decides to prune).
    assert summary["orphaned"] == 1


def test_sweep_flags_duplicate_sidecar_names_across_folders(tmp_path, monkeypatch):
    """The same heading-derived sidecar name landing in two build folders
    (canonical + stale per-phase split, gloryev EYW-345/348 pattern) must be
    surfaced in the summary so the build log can disambiguate which folder is
    canonical — duplicated .puml/.svg sidecars are the 'duplicated PlantUML
    diagrams' symptom of an un-merged stale build."""
    root = tmp_path / "projects"
    canonical = root / "001-Foo"
    stale = root / "001-FOO-bar"
    canonical.mkdir(parents=True)
    stale.mkdir(parents=True)
    heading = "## PlantUML ArchiMate View\n```plantuml\n@startuml\nx\n@enduml\n```\n"
    (canonical / "ARC-001-TECH-v1.0.md").write_text(heading, encoding="utf-8")
    (stale / "ARC-001-TECH-v1.0.md").write_text(heading, encoding="utf-8")
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)

    summary = diagrams.consolidate_project_diagrams(tmp_path)

    # Both folders materialise the identically-named sidecar…
    assert (canonical / "diagrams" / "plantuml-archimate-view.puml").is_file()
    assert (stale / "diagrams" / "plantuml-archimate-view.puml").is_file()
    # …and the sweep must report the collision so the build summary can
    # surface it instead of leaving two silent duplicates.
    assert summary["duplicate_sidecars"], (
        f"duplicate sidecar names across folders must be reported, got {summary!r}"
    )
    assert "plantuml-archimate-view.puml" in summary["duplicate_sidecars"]
    # Both folders must be named so the log can point at the canonical one.
    assert summary["duplicate_sidecars"]["plantuml-archimate-view.puml"] == [
        str(stale.relative_to(tmp_path) / "diagrams"),
        str(canonical.relative_to(tmp_path) / "diagrams"),
    ]
