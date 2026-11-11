## Purpose
Defines the MCP server that exposes ArcKit slash commands as tools, making the full governance workflow reachable from any MCP-capable agent without re-implementing intake, gates, or next-step logic.

## ADDED Requirements

### Requirement: MCP Server Exposes Core, OAA, IT4IT, and TOGAF-ADM Commands As Tools
The MCP server SHALL serve one tool per ArcKit command:
- 78 core commands from `plugins/arckit-claude/commands/`
- 5 OAA commands (`oaa-adm-lite`, `product-architecture`, `agile-governance`, `agile-security`, `agile-strategy`)
- 6 IT4IT commands (`it4it-value-network`, `it4it-value-stream`, `it4it-strategy-portfolio`, `it4it-develop-test`, `it4it-consume-fulfil`, `it4it-operate-assure`)
- 12 TOGAF-ADM commands (`adm-preliminary`, `application-inventory`, `application-rationalization`, `architecture-board`, `architecture-change`, `architecture-repository`, `business-capability-map`, `data-architecture`, `discovery`, `gap-analysis`, `technology-architecture`, `transition-architecture`)

Each tool's description SHALL include: the command name, its doc-type code(s), its prerequisite gate tiers (MANDATORY / RECOMMENDED / OPTIONAL), and a one-line summary of what it produces. The tool list SHALL be stable across server restarts; commands are not discovered at runtime.

#### Scenario: Agent lists all commands
- **WHEN** an agent calls `arckit.list_commands`
- **THEN** the response includes all 101 commands (78 core + 5 OAA + 6 IT4IT + 12 TOGAF-ADM), each with name, doc-type code(s), and gate tier labels

#### Scenario: OAA commands are present
- **WHEN** an agent lists commands and filters by overlay
- **THEN** `oaa-adm-lite`, `product-architecture`, `agile-governance`, `agile-security`, and `agile-strategy` appear with their OAA doc-type codes (`OAAL`, `OAPR`, `OAGOV`, `OASEC`, `OASTR`)

#### Scenario: IT4IT commands are present
- **WHEN** an agent lists commands and filters by overlay
- **THEN** all six `it4it-*` commands appear with their doc-type codes (`ITVN`, `ITVS`, `ITSF`, `ITDT`, `ITCF`, `ITOA`)

#### Scenario: TOGAF-ADM commands are present
- **WHEN** an agent lists commands and filters by overlay
- **THEN** all twelve `togaf-adm-*` commands appear with their doc-type codes (`ADMP`, `ACHG`, `BPCM`, `TECH`, `GAPA`, `TRANS`, `DATA`, `BORD`, `APPR`, `REPO`, `APP`, `DISC`)

### Requirement: Meta-Tools Are Exposed In Addition To Per-Command Tools
The MCP server SHALL expose three meta-tools in addition to per-command tools:
- `arckit.list_commands` — enumerate all available commands with doc-type codes and gate tiers
- `arckit.next_step` — given current project state, return the next recommended command from the handoffs graph
- `arckit.check_gates` — given a project ID and a target command, return which prerequisite gates are open or closed

#### Scenario: list_commands returns structured data
- **WHEN** an agent calls `arckit.list_commands`
- **THEN** each entry includes: `command` (tool name), `doc_type` (e.g. `REQ`), `gates` (array of `{code, tier, status}` where status is `open` or `closed`), and `overlay` (`core` / `oaa` / `it4it` / `togaf-adm`)

#### Scenario: check_gates returns gate status
- **WHEN** an agent calls `arckit.check_gates` with `project_id: "001"` and `command: "oaa-adm-lite"`
- **THEN** the response lists all MANDATORY gates (e.g. `PRIN`) with `status: "closed"` if the artefact exists, `status: "open"` if missing, and RECOMMENDED/OPTIONAL gates separately

#### Scenario: next_step returns a handoff
- **WHEN** an agent calls `arckit.next_step` with `project_id: "001"` and `completed: ["requirements"]`
- **THEN** the response returns the next command in the handoffs graph (e.g. `data-model` if `DR-xxx` requirements were generated) with a one-line reason

### Requirement: The Server Reads The Same Doc-Type Source Of Truth As The Plugin
The MCP server SHALL load doc-type codes from `plugins/arckit-claude/config/doc-types.mjs` (or an equivalent static mirror kept in sync by CI) so that tool descriptions, gate checks, and next-step logic use the same codes as the plugin. The `SUBDIR_MAP` and `MULTI_INSTANCE_TYPES` lists SHALL also be mirrored; a code missing from the registry that a command writes SHALL be surfaced as an error, not silently accepted.

#### Scenario: Doc-type parity with the plugin
- **WHEN** a CI check runs `tests/plugin/test_mcp_command_registry.py`
- **THEN** every doc-type code in `doc-types.mjs` is present in the MCP server's registry and vice versa; a missing code fails the test

#### Scenario: Unknown doc-type is rejected
- **WHEN** a command tool is called with a doc-type code not in the registry
- **THEN** the tool returns an error indicating the code is not recognised, and does not write the artefact
