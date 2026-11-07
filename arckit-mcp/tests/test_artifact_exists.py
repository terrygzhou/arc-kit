"""Regression test for ``_artifact_exists`` project-prefix matching.

The artifact filename regex captures the project as a 3-digit group. The gate
previously compared that captured 3-digit value against the *full* directory
slug (e.g. ``001-spp``), so slug'd project ids could never match and every
gate reported open even when the artifact files exist.

The fix compares the captured project group against the numeric prefix of the
slug (``001-spp`` -> ``001``), which preserves numeric-only project ids
(``001`` -> ``001``) and makes slug'd ids work.
"""

from __future__ import annotations

from arckit_mcp.server import _artifact_exists


def _write_artifact(root, project_dir_name: str, code: str) -> None:
    """Create a minimal artefact file for *code* under *project_dir_name*."""
    pdir = root / "projects" / project_dir_name
    pdir.mkdir(parents=True, exist_ok=True)
    # The on-disk filename always carries the 3-digit numeric project id.
    (pdir / f"ARC-{project_dir_name.split('-')[0]}-{code}-v1.0.md").write_text(
        f"# {code} fixture\n"
    )


def test_slug_project_finds_artifact(tmp_path):
    """A slug'd project dir (``001-spp``) must find its artifact by prefix."""
    _write_artifact(tmp_path, "001-spp", "STKE")
    assert _artifact_exists("STKE", "001-spp", root=str(tmp_path)) is True


def test_slug_project_missing_code_is_false(tmp_path):
    """A different slug with no artifact file must not match."""
    _write_artifact(tmp_path, "001-spp", "STKE")
    # ``002-x`` has no project dir under root -> no artifact.
    assert _artifact_exists("STKE", "002-x", root=str(tmp_path)) is False


def test_numeric_only_project_still_works(tmp_path):
    """Numeric-only project ids keep working (prefix == full id)."""
    _write_artifact(tmp_path, "001", "STKE")
    assert _artifact_exists("STKE", "001", root=str(tmp_path)) is True
