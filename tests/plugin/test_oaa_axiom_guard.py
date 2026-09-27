"""
Guard test for scripts/check_oaa_axioms.py — the O-AA C208 integrity guard.

Unit-level: the per-file check functions must flag each defect class
(corrupted axiom name, out-of-range axiom number, "Learning Unit"
phrasing, stale C208 chapter coordinates, missing playbook context,
oaa-adm-lite axiom-set drift) and pass clean content.

Integration-level: the guard's main() passes on the checked-out repo
(canonical source + Claude mirror both clean) and fails when an axiom
name is corrupted in a scanned tree.
"""

import importlib.util
import shutil
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD_SCRIPT = REPO_ROOT / "scripts" / "check_oaa_axioms.py"

_spec = importlib.util.spec_from_file_location("check_oaa_axioms", GUARD_SCRIPT)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)

CANON = guard.CANON_AXIOMS
CANON_TABLE = "".join(
    f"| {n} | {name} | {'oaa-adm-lite' if n <= 10 else 'product-architecture'} |\n"
    for n, name in CANON.items()
)


@pytest.fixture()
def oaa_tree() -> Path:
    """Throwaway tree UNDER the repo root (the guard calls path.relative_to(ROOT))."""
    root = Path(tempfile.mkdtemp(prefix="oaa-guard-fixtures-", dir=str(guard.ROOT)))
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _valid_adm_tree(root: Path) -> None:
    """Minimal commands/templates/references tree with a consistent oaa-adm-lite set {1..10}."""
    items = "\n".join(f"- **Axiom {n} ({CANON[n]})** — applied in sprint window {n}\n" for n in range(1, 11))
    _write(root, "commands/oaa-adm-lite.md", f"# OAA ADM Lite\n\n## Axiom Alignment\n{items}\n")
    _write(root, "templates/oaa-adm-lite-template.md", f"# OAA ADM Lite Template\n\n## Axiom Alignment\n{items}\n")
    _write(
        root,
        "references/oaa-reference.md",
        "# OAA Reference\n\n| # | Axiom (C208 Ch. 9) | Applied by |\n|---|---|---|\n" + CANON_TABLE,
    )


# --- integration -----------------------------------------------------------


def test_guard_main_passes_on_repo():
    assert guard.main() == 0


def test_guard_main_fails_on_corrupted_axiom_name(oaa_tree, monkeypatch):
    canon = oaa_tree / "plugins" / "arckit-oaa"
    _valid_adm_tree(canon)
    monkeypatch.setattr(guard, "ROOT", oaa_tree)
    monkeypatch.setattr(guard, "SOURCE_ROOTS", (canon,))
    assert guard.main() == 0

    tpl = canon / "templates" / "oaa-adm-lite-template.md"
    tpl.write_text(
        tpl.read_text(encoding="utf-8").replace(
            "Axiom 1 (Customer Experience Focus)", "Axiom 1 (Agile Architecture)"
        ),
        encoding="utf-8",
    )
    assert guard.main() == 1


# --- axiom citations -------------------------------------------------------


def test_named_citation_with_published_name_passes(oaa_tree):
    path = _write(oaa_tree, "OAPR-fixture.md", "Axiom 15 (Project to Product Shift) drives product ownership.\n")
    assert guard.check_axiom_citations(path, path.read_text(encoding="utf-8")) == []


def test_named_citation_with_wrong_name_fails(oaa_tree):
    path = _write(oaa_tree, "OAPR-fixture.md", "Axiom 12: Agile Architecture — shape the organisation.\n")
    failures = guard.check_axiom_citations(path, path.read_text(encoding="utf-8"))
    assert len(failures) == 1
    assert "Axiom 12" in failures[0]
    assert "Organization Mirroring Architecture" in failures[0]


def test_unnamed_citation_passes(oaa_tree):
    path = _write(oaa_tree, "OAPR-fixture.md", "Per Axiom 16, security is embedded in every sprint.\n")
    assert guard.check_axiom_citations(path, path.read_text(encoding="utf-8")) == []


def test_out_of_range_axiom_number_fails(oaa_tree):
    path = _write(oaa_tree, "OAPR-fixture.md", "C208 defines Axiom 17 in its extended edition.\n")
    failures = guard.check_axiom_citations(path, path.read_text(encoding="utf-8"))
    assert len(failures) == 1
    assert "Axiom 17" in failures[0]
    assert "16 axioms" in failures[0]


# --- 16-axiom table --------------------------------------------------------


def test_canonical_table_passes(oaa_tree):
    path = _write(
        oaa_tree,
        "references/oaa-reference.md",
        "| # | Axiom (C208 Ch. 9) | Applied by |\n|---|---|---|\n" + CANON_TABLE,
    )
    assert guard.check_axiom_table(path, path.read_text(encoding="utf-8")) == []


def test_corrupted_table_row_name_fails(oaa_tree):
    text = CANON_TABLE.replace("| 11 | Partitioning Over Layering |", "| 11 | Agile Architecture |")
    path = _write(oaa_tree, "references/oaa-reference.md", text)
    failures = guard.check_axiom_table(path, text)
    assert len(failures) == 1
    assert "row 11" in failures[0]
    assert "Partitioning Over Layering" in failures[0]


def test_missing_table_row_fails(oaa_tree):
    text = CANON_TABLE.replace("| 9 | Modular Data Platform | oaa-adm-lite |\n", "")
    path = _write(oaa_tree, "references/oaa-reference.md", text)
    failures = guard.check_axiom_table(path, text)
    assert len(failures) == 1
    assert "missing row for Axiom 9" in failures[0]


# --- learning-unit vocabulary ----------------------------------------------


def test_learning_unit_phrasing_fails(oaa_tree):
    path = _write(oaa_tree, "OAPR-fixture.md", "Use C208 Learning Unit 7 for product architecture.\n")
    failures = guard.check_learning_units(path, path.read_text(encoding="utf-8"))
    assert len(failures) == 1
    assert "Learning Unit" in failures[0]


def test_no_learning_units_passes(oaa_tree):
    path = _write(oaa_tree, "OAPR-fixture.md", "Use C208 Ch. 14 (Product Architecture) for the product view.\n")
    assert guard.check_learning_units(path, path.read_text(encoding="utf-8")) == []


# --- playbook context ------------------------------------------------------


def test_g216_without_security_context_fails(oaa_tree):
    text = "The engagement cites G216 for cadence.\n" + "a" * 100 + " security controls.\n"
    path = _write(oaa_tree, "OASEC-fixture.md", text)
    failures = guard.check_playbook_context(path, text)
    assert len(failures) == 1
    assert "G216" in failures[0]


def test_g216_with_security_context_passes(oaa_tree):
    text = "Security controls follow the O-AA Security Playbook (G216) per sprint.\n"
    path = _write(oaa_tree, "OASEC-fixture.md", text)
    assert guard.check_playbook_context(path, text) == []


def test_g226_without_context_fails(oaa_tree):
    text = "Cite G226 for the delivery cadence.\n" + "a" * 100 + " agile enterprise architect role.\n"
    path = _write(oaa_tree, "OAPR-fixture.md", text)
    failures = guard.check_playbook_context(path, text)
    assert any("G226" in f for f in failures)


# --- stale chapter coordinates ----------------------------------------------


def test_stale_chapter_coordinate_fails(oaa_tree):
    path = _write(oaa_tree, "OAPR-fixture.md", "See Chapter 12 — Product Architecture for the product view.\n")
    failures = guard.check_chapter_citations(path, path.read_text(encoding="utf-8"))
    assert len(failures) == 1
    assert "Ch. 14" in failures[0]


def test_stale_adm_range_fails(oaa_tree):
    path = _write(oaa_tree, "OAAL-fixture.md", "The ADM Lite mapping covers Chapters 1–9 of C208.\n")
    failures = guard.check_chapter_citations(path, path.read_text(encoding="utf-8"))
    assert len(failures) == 1
    assert "C182" in failures[0]


def test_verified_chapter_coordinates_pass(oaa_tree):
    text = (
        "Ch. 8 (Agile Governance), Ch. 11 (Agile Strategy), Ch. 14 (Product Architecture), "
        "and Ch. 4.6 + Axiom 16 + G216 for security.\n"
    )
    path = _write(oaa_tree, "OAPR-fixture.md", text)
    assert guard.check_chapter_citations(path, text) == []


# --- oaa-adm-lite axiom-set consistency --------------------------------------


def test_adm_lite_set_consistency_passes(oaa_tree):
    _valid_adm_tree(oaa_tree)
    assert guard.check_adm_lite_set_consistency(oaa_tree) == []


def test_adm_lite_set_drift_fails(oaa_tree):
    _valid_adm_tree(oaa_tree)
    ref = oaa_tree / "references" / "oaa-reference.md"
    rows = "".join(f"| {n} | {CANON[n]} | oaa-adm-lite |\n" for n in range(1, 5))
    ref.write_text(f"# OAA Reference\n\n| # | Axiom | Applied by |\n|---|---|---|\n{rows}", encoding="utf-8")
    failures = guard.check_adm_lite_set_consistency(oaa_tree)
    assert len(failures) == 1
    assert "drift" in failures[0]
    assert "{1, 2, 3, 4}" in failures[0]


def test_adm_lite_set_missing_files_fail():
    root = Path(tempfile.mkdtemp(prefix="oaa-guard-empty-", dir=str(guard.ROOT)))
    try:
        failures = guard.check_adm_lite_set_consistency(root)
        assert len(failures) == 1
        assert "missing file(s)" in failures[0]
    finally:
        shutil.rmtree(root, ignore_errors=True)
