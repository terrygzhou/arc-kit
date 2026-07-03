"""LangGraph compilation — recipe YAML → StateGraph."""

from __future__ import annotations

import logging
from typing import Any
from pathlib import Path

import yaml
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from schema import AdmCycleState
from nodes.preliminary import PreliminaryNode

logger = logging.getLogger(__name__)


def load_recipe(recipe_path: str | Path) -> dict[str, Any]:
    """Parse a recipe YAML file."""
    with open(recipe_path) as f:
        return yaml.safe_load(f)


def compile_graph(
    recipe_path: str | Path,
    plugin_root: str = "plugins/arckit-togaf-adm",
) -> Any:
    """
    Convert recipe targets + deps into a LangGraph StateGraph.

    Every target becomes a node.  Dependencies become directed edges.
    Compiled with an in-memory checkpointer for HIL interrupt/resume.
    Returns the *compiled* graph (CompiledStateGraph).
    """
    recipe = load_recipe(recipe_path)
    checkpointer = MemorySaver()

    graph = StateGraph(AdmCycleState)

    # Register nodes — use closure-safe defaults
    for tgt in recipe.get("targets", []):
        tid = tgt["id"]
        graph.add_node(tid, _make_node_fn(tgt, plugin_root))

    # Wire edges
    for tgt in recipe.get("targets", []):
        for dep in tgt.get("deps", []):
            graph.add_edge(dep, tgt["id"])

    # Set entry point (first target)
    entry = recipe.get("targets", [{}])[0]
    if entry:
        graph.set_entry_point(entry["id"])

    compiled = graph.compile(checkpointer=checkpointer)
    logger.info("Compiled %d nodes", len(recipe.get("targets", [])))
    return compiled


def _make_node_fn(target: dict[str, Any], plugin_root: str):
    """Factory that returns a LangGraph-compatible node function."""

    phase_id = target["id"]

    if phase_id == "ADMP":
        import asyncio

        node = PreliminaryNode(target, plugin_root)

        async def admp_fn(state: dict[str, Any]) -> dict[str, Any]:
            return await node.execute(state, state.get("_config", {}))

        return admp_fn

    # Default placeholder for remaining phases
    from schema import PhaseState, PhaseStatus
    from datetime import datetime, timezone

    def default_fn(state: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        state["phases"][phase_id] = dict(
            PhaseState(id=phase_id, status=PhaseStatus.PENDING, started_at=now)
        )
        state["current_phase"] = phase_id
        return state

    return default_fn
