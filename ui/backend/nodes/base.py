"""Base ADM phase node — shared scaffold for every phase."""

from datetime import datetime, timezone

from schema import PhaseState, PhaseStatus


class BasePhaseNode:
    """Minimal node that every ADM phase inherits."""

    def __init__(self, target: dict, plugin_root: str):
        self.target = target
        self.phase_id: str = target["id"]
        self.skill: str = target.get("skill", "")
        self.args: str = target.get("args", "")
        self.plugin_root = plugin_root

    async def execute(self, state: dict, config: dict) -> dict:
        """
        Execute one phase:
        1. Read command prompt + prerequisites
        2. Call LLM
        3. Render template → artifact
        4. Persist to projects/
        Returns a state update dict for LangGraph.
        """
        raise NotImplementedError
