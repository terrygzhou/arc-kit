"""
Generator-side tests for ``scripts/generate-mcp-intake.py``.

OpenSpec task 1.2 of the ``generate-mcp-intake`` change.  These tests exercise
the GENERATOR script, not the emitted module (the emitted module is tested in
the sibling arckit-mcp repo via ``tests/plugin/test_mcp_intake_data.py``).

Assertions:

1. The emitted module is byte-identical across two consecutive generator runs
   (byte-stability — sorted keys, no timestamps).
2. ``COVERAGE`` marks at least one core-plugin doc-type (e.g. ``ADR``) as
   ``"no-static-questions"``.
3. At least one overlay doc-type (``OASTR``) is ``"covered"`` with non-empty
   ``questions`` in ``INTAKE``.
4. The dedup rule: ``INTAKE["OASTR"]["source"]`` points to the flat-tree
   ``plugins/arckit-oaa/templates/agile-strategy-template.md``, NOT the nested
   copy under ``plugins/arckit-claude/plugins/oaa/templates/``.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate-mcp-intake.py"


def _run_generator(out_path: Path) -> None:
    """Run the generator script writing its output to ``out_path``."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(out_path)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"generate-mcp-intake.py failed (rc={result.returncode}):\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert out_path.is_file(), "generator did not write the output file"


def _load_module(out_path: Path):
    """Load the emitted module from ``out_path`` via importlib."""
    spec = importlib.util.spec_from_file_location("_intake_generated", out_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generated():
    """Run the generator once into a temp dir; return (module, bytes1, bytes2).

    The bytes from two consecutive runs are captured for the byte-stability
    assertion.  The module is loaded from the first run's output.
    """
    with tempfile.TemporaryDirectory(prefix="mcp-intake-gen-test-") as tmp:
        out1 = Path(tmp) / "intake_run1.py"
        out2 = Path(tmp) / "intake_run2.py"

        _run_generator(out1)
        _run_generator(out2)

        bytes1 = out1.read_bytes()
        bytes2 = out2.read_bytes()

        module = _load_module(out1)
        return module, bytes1, bytes2


# ---------------------------------------------------------------------------
# 1. Byte-stability
# ---------------------------------------------------------------------------

def test_byte_stable(generated):
    """Two consecutive generator runs emit byte-identical output."""
    module, bytes1, bytes2 = generated
    assert bytes1 == bytes2, (
        "generator output is not byte-stable across two runs "
        f"({len(bytes1)} vs {len(bytes2)} bytes)"
    )


# ---------------------------------------------------------------------------
# 2. Core-plugin doc-type is "no-static-questions"
# ---------------------------------------------------------------------------

def test_core_doc_type_no_static_questions(generated):
    """ADR (a core arckit-claude doc-type) is marked no-static-questions."""
    module, _, _ = generated
    coverage = module.COVERAGE
    assert "ADR" in coverage, (
        f"ADR not in COVERAGE ({len(coverage)} codes); "
        "core-plugin doc-type missing"
    )
    assert coverage["ADR"] == "no-static-questions", (
        f"COVERAGE['ADR'] = {coverage['ADR']!r}, "
        "expected 'no-static-questions' for a core-plugin doc-type "
        "whose template has no static intake questions"
    )


# ---------------------------------------------------------------------------
# 3. Overlay doc-type is "covered" with non-empty questions
# ---------------------------------------------------------------------------

def test_overlay_doc_type_covered(generated):
    """OASTR (arckit-oaa agile strategy) is covered with non-empty questions."""
    module, _, _ = generated
    coverage = module.COVERAGE
    intake = module.INTAKE

    assert "OASTR" in coverage, "OASTR not in COVERAGE"
    assert coverage["OASTR"] == "covered", (
        f"COVERAGE['OASTR'] = {coverage['OASTR']!r}, expected 'covered'"
    )
    assert "OASTR" in intake, "OASTR not in INTAKE"
    entry = intake["OASTR"]
    assert isinstance(entry["questions"], list), "INTAKE['OASTR'].questions is not a list"
    assert len(entry["questions"]) > 0, (
        "INTAKE['OASTR'].questions is empty; "
        "a 'covered' doc-type must have at least one question"
    )
    for q in entry["questions"]:
        assert isinstance(q, str) and q.strip(), (
            f"INTAKE['OASTR'].questions has a blank entry: {q!r}"
        )


# ---------------------------------------------------------------------------
# 4. Dedup rule: flat-tree source wins
# ---------------------------------------------------------------------------

def test_dedup_flat_tree_wins(generated):
    """INTAKE['OASTR']['source'] points to the flat-tree template, not the nested copy."""
    module, _, _ = generated
    intake = module.INTAKE

    assert "OASTR" in intake, "OASTR not in INTAKE"
    source = intake["OASTR"]["source"]

    expected_flat = "plugins/arckit-oaa/templates/agile-strategy-template.md"
    nested_prefix = "plugins/arckit-claude/plugins/oaa/templates/"

    assert source == expected_flat, (
        f"INTAKE['OASTR']['source'] = {source!r}, expected {expected_flat!r} "
        "(flat-tree path, not the nested mirror)"
    )
    assert not source.startswith(nested_prefix), (
        f"INTAKE['OASTR']['source'] = {source!r} points to the nested mirror; "
        "flat-tree templates must win the dedup"
    )
