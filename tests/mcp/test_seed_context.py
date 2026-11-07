"""Tests for ``seed_context`` (task 4.x: project seeding).

Covered:

* seeding a fresh project mints ``projects/001-{slug}/`` with an
  ``external/`` subdirectory;
* a second seed in the same cwd mints ``002``;
* importing a context folder copies files (preserving subdirectories)
  into ``external/``, writes ``external/CONTEXT.md`` with per-file
  Source IDs, and reports the import count;
* Source ID derivation follows the citation-instructions.md rules
  (strip extension, strip version suffix, first letters of significant
  words, uppercase);
* seeding with goals/constraints writes ``GOALS.md`` at the project root;
* the returned project_id is usable with ``check_gates``;
* seeding a name that already exists returns an error dict.
"""

from __future__ import annotations

from pathlib import Path

from arckit_mcp.server import check_gates, seed_context


def _make_context_folder(root: Path, name: str = "context") -> Path:
    """Create *root*/{name} with three files and one subfolder."""
    folder = root / name
    (folder / "data").mkdir(parents=True)
    (folder / "privacy-policy-v2.pdf").write_text("policy v2")
    (folder / "nhs-digital-service-manual.pdf").write_text("manual")
    (folder / "data" / "data-protection-impact-assessment.pdf").write_text("dpia")
    return folder


def test_seed_mints_project_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = seed_context("Payment Gateway")
    assert result["project_id"] == "001"
    assert result["project_dir"] == "projects/001-payment-gateway"
    pdir = tmp_path / "projects" / "001-payment-gateway"
    assert pdir.is_dir()
    assert (pdir / "external").is_dir()
    assert result["files_imported"] == 0
    assert result["context_index"] is None


def test_seed_mints_second_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = seed_context("Alpha")
    second = seed_context("Beta")
    assert first["project_id"] == "001"
    assert second["project_id"] == "002"
    assert second["project_dir"] == "projects/002-beta"
    assert (tmp_path / "projects" / "002-beta").is_dir()


def test_seed_imports_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    folder = _make_context_folder(tmp_path)
    result = seed_context("Payment Gateway", context_folder=str(folder))
    assert result["project_id"] == "001"
    assert result["files_imported"] == 3
    assert result["context_index"] == "external/CONTEXT.md"
    ext = tmp_path / "projects" / "001-payment-gateway" / "external"
    assert (ext / "privacy-policy-v2.pdf").is_file()
    assert (ext / "nhs-digital-service-manual.pdf").is_file()
    assert (ext / "data" / "data-protection-impact-assessment.pdf").is_file()
    index = (ext / "CONTEXT.md").read_text(encoding="utf-8")
    # CONTEXT.md lists each imported file with its Source ID.
    assert "PP" in index
    assert "NDSM" in index
    assert "DPIA" in index
    for name in (
        "privacy-policy-v2.pdf",
        "nhs-digital-service-manual.pdf",
        "data/data-protection-impact-assessment.pdf",
    ):
        assert name in index


def test_seed_source_id_derivation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / "ctx"
    (folder / "sub").mkdir(parents=True)
    (folder / "privacy-policy-v2.pdf").write_text("a")
    (folder / "nhs-digital-service-manual.pdf").write_text("b")
    (folder / "sub" / "data-protection-impact-assessment.pdf").write_text("c")
    result = seed_context("Audit", context_folder=str(folder))
    assert result["files_imported"] == 3
    index = (
        tmp_path / "projects" / "001-audit" / "external" / "CONTEXT.md"
    ).read_text(encoding="utf-8")
    lines = [ln for ln in index.splitlines() if "privacy-policy-v2.pdf" in ln]
    assert lines and "PP" in lines[0]
    lines = [ln for ln in index.splitlines() if "nhs-digital-service-manual.pdf" in ln]
    assert lines and "NDSM" in lines[0]
    lines = [
        ln for ln in index.splitlines() if "data-protection-impact-assessment.pdf" in ln
    ]
    assert lines and "DPIA" in lines[0]


def test_seed_writes_goals_md(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = seed_context(
        "Migration",
        goals=["Cut migration cost", "Zero-downtime cutover"],
        constraints=["No new vendors", "Must stay on GovCloud"],
    )
    assert result["project_id"] == "001"
    pdir = tmp_path / "projects" / "001-migration"
    goals_md = (pdir / "GOALS.md").read_text(encoding="utf-8")
    assert "## Goals" in goals_md
    assert "## Constraints" in goals_md
    assert "Cut migration cost" in goals_md
    assert "Zero-downtime cutover" in goals_md
    assert "No new vendors" in goals_md
    assert "Must stay on GovCloud" in goals_md


def test_seed_returns_project_id_usable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = seed_context("Requirements Pilot")
    pid = result["project_id"]
    gates = check_gates("requirements", pid)
    # No STKE artefact yet in the seeded project, so the MANDATORY
    # gate must block.
    assert gates["gate_blocked"] is True
    assert gates["project_id"] == pid
    assert any(g["code"] == "STKE" and g["status"] == "open" for g in gates["gates"])


def test_seed_name_collision(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = seed_context("Collision")
    assert first["project_id"] == "001"
    second = seed_context("Collision")
    assert "error" in second
    assert second["project_id"] is None
    # The first project directory is untouched.
    assert (tmp_path / "projects" / "001-collision").is_dir()


def test_seed_no_context_folder_no_context_index(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = seed_context("No Folder")
    assert result["files_imported"] == 0
    assert result["context_index"] is None
    assert not (
        tmp_path / "projects" / "001-no-folder" / "external" / "CONTEXT.md"
    ).exists()
