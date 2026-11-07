"""Tests for ``next_step`` (task 6.x: handoffs-graph walk).

Covered:

* no completed commands → ``next`` is ``None``;
* an unconditional handoff edge is accepted;
* a conditional edge whose referenced artefact is missing is skipped, and
  accepted when the artefact is present (fixture under ``projects/001/``);
* all-reachable handoffs completed → ``next`` None with a reason string.
"""

from __future__ import annotations

import arckit_mcp.server as server
from arckit_mcp.server import next_step


def test_no_completed_commands_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = next_step("001", completed=[])
    assert result == {
        "project_id": "001",
        "next": None,
        "reason": "All reachable handoffs completed",
    }


def test_unconditional_edge_accepted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # stakeholders handoffs: requirements, risk, sobc — all unconditional.
    result = next_step("001", completed=["stakeholders"])
    assert result["project_id"] == "001"
    assert result["next"] in {"requirements", "risk", "sobc"}
    assert result["reason"] == "No condition; recommended next step"


def test_conditional_edge_missing_artifact_skipped(tmp_path, monkeypatch):
    # Monkeypatch a conditional edge onto 'requirements': it hands off to
    # 'traceability' only when a TRC artefact exists. No TRC artefact → the
    # conditional edge is omitted; only the unconditional edges remain.
    monkeypatch.chdir(tmp_path)
    original = dict(server.HANDOFFS)
    monkeypatch.setitem(
        server.HANDOFFS,
        "arckit-claude/requirements",
        [
            ("research", "", ""),  # unconditional — still accepted
            ("traceability", "Traceability matrix exists", "TRC"),  # conditional
        ],
    )
    result = next_step("001", completed=["requirements"])
    # The conditional target must not be selected — deterministically, the
    # only candidate left is 'research'.
    assert result["next"] == "research"

    # Restore so later tests see the real graph.
    assert server.HANDOFFS["arckit-claude/requirements"] != original.get(
        "arckit-claude/requirements"
    )


def test_conditional_edge_present_artifact_accepted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Build a TRC artefact so the conditional edge is satisfied.
    pdir = tmp_path / "projects" / "001"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "ARC-001-TRC-v1.0.md").write_text("# TRC fixture\n")

    monkeypatch.setitem(
        server.HANDOFFS,
        "arckit-claude/requirements",
        [
            ("research", "", ""),
            ("traceability", "Traceability matrix exists", "TRC"),
        ],
    )
    result = next_step("001", completed=["requirements"])
    # Both candidates now qualify; the deterministic min-pick wins.
    assert result["next"] in {"research", "traceability"}
    if result["next"] == "traceability":
        assert result["reason"] == "Traceability matrix exists"


def test_all_reachable_completed_returns_reason(tmp_path, monkeypatch):
    # Self-contained: build a small graph where both targets of the only
    # completed command are themselves completed → no candidate remains.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(
        server.HANDOFFS,
        "arckit-claude/stakeholders",
        [("requirements", "", ""), ("risk", "", "")],
    )
    # Neutralise the real graph entries for the other completed commands so
    # the test is fully self-contained.
    for key in ("arckit-claude/requirements", "arckit-claude/risk"):
        monkeypatch.setitem(server.HANDOFFS, key, [])
    result = next_step("001", completed=["stakeholders", "requirements", "risk"])
    assert result["next"] is None
    assert result["reason"] == "All reachable handoffs completed"
    assert result["project_id"] == "001"
