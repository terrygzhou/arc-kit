"""Pydantic models for ADM state, phases, and SSE events."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class PhaseStatus(str, Enum):
    """Lifecycle status of a single ADM phase."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ERROR = "error"


class PhaseState(BaseModel):
    """State for one ADM phase (ADMP, BPCM, …)."""

    id: str
    status: PhaseStatus = PhaseStatus.PENDING
    config: dict[str, Any] = {}
    artifacts: dict[str, str] = {}
    questions: list[dict[str, Any]] = []
    answers: list[dict[str, Any]] = []
    progress: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


class AdmCycleState(BaseModel):
    """Top-level state carried through the LangGraph DAG."""

    project_id: str
    project_name: str = ""
    phases: dict[str, PhaseState] = {}
    current_phase: str | None = None
    metadata: dict[str, Any] = {}

    class Config:
        extra = "allow"


class SSEEvent(BaseModel):
    """Event streamed to the HTMX frontend via SSE."""

    type: str  # "phase_update" | "progress" | "question" | "complete"
    phase: str
    timestamp: datetime
    data: dict[str, Any] | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
