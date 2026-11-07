## Why

ArcKit's 78 core slash commands + OAA/IT4IT/TOGAF-ADM overlays are locked behind a Claude Code plugin. Non-Claude agents (Hermes) cannot use them — they would have to re-implement the intake flow, the prerequisite gates, the doc-type registry, and the next-step logic by hand. An MCP server that exposes these commands as tools makes the whole governance workflow reachable from any MCP-capable agent with zero duplication.

## What Changes

- New `arckit-mcp/` package (Python) that serves the 78 core + OAA + IT4IT + TOGAF-ADM commands as MCP tools (one per command, plus 3 meta-tools: `arckit.list_commands`, `arckit.next_step`, `arckit.check_gates`)
- Each command tool returns its intake questions/instructions in a progressive relay — the MCP is guidance + state, not an execution engine; the agent (Hermes) runs the LLM-driven generation in its own session and calls back to persist artefacts
- `arckit.check_gates` runs the prerequisite gate logic (MANDATORY `PRIN` hard-stop for OAA/IT4IT, `ADMP` recommended for TOGAF-ADM, etc.) and returns which gates are open/closed
- `arckit.next_step` walks the handoffs graph and returns the next recommended command given current project state
- `arckit.list_commands` enumerates available commands with their doc-type codes and prerequisite gates, so an agent can pick without trial-and-error
- The MCP server reads the same source of truth as the plugin: `doc-types.mjs`, `SUBDIR_MAP`, `MULTI_INSTANCE_TYPES` — it imports or mirrors them so doc-type codes stay in sync
- No breaking changes to the plugin or CLI

## Capabilities

### New Capabilities
- `arckit-mcp-server`: MCP server that exposes ArcKit slash commands as tools, including intake relay, gate checks, next-step guidance, and command enumeration
- `arckit-mcp-command-relay`: Progressive intake relay — each command tool returns the command's intake questions + instructions so the agent can run the generation in its own session
- `arckit-mcp-gates`: Prerequisite gate checking (MANDATORY/RECOMMENDED/OPTIONAL tiers) shared with the plugin's existing gate logic
- `arckit-mcp-next-step`: Handoffs-graph walker that returns the next recommended command given current project state
- `arckit-mcp-doc-type-registry`: MCP-side mirror of `doc-types.mjs` / `SUBDIR_MAP` / `MULTI_INSTANCE_TYPES` so tool descriptions and gate checks use the same codes as the plugin

### Modified Capabilities
- None (no existing spec changes; all additions are new)

## Impact

- New package `arckit-mcp/` (Python, no new runtime deps beyond `mcp` SDK)
- New tests in `tests/plugin/test_mcp_command_registry.py` (doc-type code parity with `doc-types.mjs`) and `tests/mcp/` (gate logic, next-step walker, intake relay shape)
- No changes to `plugins/arckit-claude/` source
- CI: new test job for `tests/mcp/` and the doc-type parity test
- Docs: new `docs/guides/mcp.md` guide + `docs/index.html` entry
