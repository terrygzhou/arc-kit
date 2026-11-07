"""ArcKit MCP server.

Exposes the ArcKit architecture-governance harness as MCP tools so an AI
agent can inspect projects, check gate tiers, walk handoff chains, and
persist artefacts without leaving the session.

The module ships four layers:

* ``_registry`` (generated) - canonical doc-type codes, subdirs, multi-instance
  set, and regimes, emitted from ``plugins/arckit-claude/config/doc-types.mjs``
  by ``scripts/generate-mcp-registry.py``.
* ``gates`` (generated) - per-command gate-tier tables (MANDATORY /
  RECOMMENDED / OPTIONAL codes), emitted from the command markdown bodies by
  ``scripts/generate-mcp-gates.py``.
* ``handoffs`` (generated) - the handoff graph, emitted from command
  frontmatter by ``scripts/generate-mcp-handoffs.py``.
* ``server`` - the MCP server entry point (wired up in a follow-up task).
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
