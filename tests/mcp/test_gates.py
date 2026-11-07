"""Tests for ``check_gates`` (task 5.x: gate-tier relay).

Covered:

* a command with MANDATORY + RECOMMENDED gates whose project directory is
  missing — every gate is open and ``gate_blocked`` is True;
* a closed mandatory gate (fixture files under ``projects/001/``) exercises
  the ``SUBDIR_MAP`` subdirectory lookup (e.g. ADR under ``decisions/``);
* a command with no gate tiers returns an empty ``gates`` list and
  ``gate_blocked`` False;
* ``gate_blocked`` False when all mandatory gates are closed.
"""

from __future__ import annotations

from arckit_mcp._registry import SUBDIR_MAP
from arckit_mcp.gates import GATE_TIERS
from arckit_mcp.server import _artifact_exists, check_gates


def _write_artifact(root, project_id: str, code: str, sub: str | None = None) -> None:
    """Create a minimal artefact file for *code* under the project dir."""
    pid = project_id.zfill(3)
    sub = sub if sub is not None else SUBDIR_MAP.get(code)
    pdir = root / "projects" / project_id
    if sub:
        pdir = pdir / sub
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / f"ARC-{pid}-{code}-v1.0.md").write_text(f"# {code} fixture\n")


def test_requirements_all_gates_open_when_project_dir_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = check_gates("requirements", "001")
    # requirements gates: STKE MANDATORY; PRIN/RISK/SOBC RECOMMENDED; PLAN OPTIONAL.
    gates = {g["code"]: g for g in result["gates"]}
    assert set(gates) == {"STKE", "PRIN", "RISK", "SOBC"}
    assert gates["STKE"]["tier"] == "MANDATORY"
    assert gates["PRIN"]["tier"] == "RECOMMENDED"
    assert all(g["status"] == "open" for g in result["gates"])
    assert result["gate_blocked"] is True
    assert result["command"] == "requirements"
    assert result["project_id"] == "001"
    # OPTIONAL gate must be silently omitted.
    assert "PLAN" not in gates


def test_closed_mandatory_gate_via_subdir_map(tmp_path, monkeypatch):
    # ADR lives under decisions/ via SUBDIR_MAP — verify the lookup finds it.
    assert SUBDIR_MAP["ADR"] == "decisions"
    _write_artifact(tmp_path, "001", "ADR", sub="decisions")
    assert _artifact_exists("ADR", "001", root=str(tmp_path)) is True
    # And that a non-subdir gate (STKE) is still open.
    assert _artifact_exists("STKE", "001", root=str(tmp_path)) is False


def test_command_with_no_gate_tiers(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # 'analyze' has no non-OPTIONAL gate tiers.
    assert GATE_TIERS["arckit-claude/analyze"] == {}
    result = check_gates("analyze", "001")
    assert result["gates"] == []
    assert result["gate_blocked"] is False


def test_gate_blocked_false_when_all_mandatory_closed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Close the single MANDATORY gate on 'risk' (STKE).
    _write_artifact(tmp_path, "001", "STKE")
    result = check_gates("risk", "001")
    gates = {g["code"]: g for g in result["gates"]}
    assert gates["STKE"]["status"] == "closed"
    # RECOMMENDED PRIN/REQ are still open, but only MANDATORY blocks.
    assert result["gate_blocked"] is False
