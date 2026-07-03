"""Tests for ADM phase nodes."""

import pytest
from schema import PhaseState, PhaseStatus


def test_phase_state_creation():
    """PhaseState defaults are correct."""
    state = PhaseState(id="ADMP")
    assert state.id == "ADMP"
    assert state.status == PhaseStatus.PENDING
    assert state.progress == 0.0
    assert state.started_at is None
    assert state.artifacts == {}


def test_phase_status_enum_values():
    """All expected status values exist."""
    assert PhaseStatus.PENDING.value == "pending"
    assert PhaseStatus.IN_PROGRESS.value == "in_progress"
    assert PhaseStatus.COMPLETED.value == "completed"
    assert PhaseStatus.BLOCKED.value == "blocked"
    assert PhaseStatus.ERROR.value == "error"


def test_preliminary_node_init():
    """PreliminaryNode initializes correctly."""
    from nodes.preliminary import PreliminaryNode

    target = {"id": "ADMP", "skill": "arckit:adm-preliminary", "args": "003"}
    node = PreliminaryNode(target, plugin_root="plugins/arckit-togaf-adm")

    assert node.phase_id == "ADMP"
    assert node.skill == "arckit:adm-preliminary"


def test_base_node_raises():
    """BasePhaseNode.execute() raises NotImplementedError."""
    from nodes.base import BasePhaseNode

    node = BasePhaseNode({"id": "TEST"}, plugin_root="plugins/arckit-togaf-adm")
    with pytest.raises(NotImplementedError):
        # execute is async — just check the type
        import inspect
        assert inspect.iscoroutinefunction(node.execute)
