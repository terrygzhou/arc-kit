# Design: ArcKit MCP Server

## Context

ArcKit's 78 core commands + OAA/IT4IT/TOGAF-ADM overlays live in `plugins/arckit-claude/` and are only invocable through a Claude Code plugin session. The doc-type registry (`doc-types.mjs`), multi-instance type set, subdirectory map, and gate-tier logic are all baked into the plugin's command markdown files and bash helpers. Non-Claude agents (Hermes, other MCP-capable runtimes) cannot use them without re-implementing intake flows, prerequisite gates, doc-type codes, and next-step logic. See [proposal.md](proposal.md) for motivation.

The doc-type SSoT is `plugins/arckit-claude/config/doc-types.mjs` (340 lines, 177 type codes). `MULTI_INSTANCE_TYPES` is triplicated across `doc-types.mjs`, `scripts/bash/generate-document-id.sh`, and `plugins/arckit-claude/scripts/bash/generate-document-id.sh` — a silent-drift history (TNDR/CMPT in v5.9.0, PR #566; GRNT until CDAU 2026-07). `SUBDIR_MAP` maps 11 type codes to subdirectories. Gate tiers (MANDATORY/RECOMMENDED/OPTIONAL) are encoded as prose in each command's markdown body — no machine-readable gate table exists.

## Goals / Non-Goals

**Goals:**

- Expose all 101 commands (78 core + 5 OAA + 6 IT4IT + 12 TOGAF-ADM) as MCP tools with stable, machine-readable schemas.
- Three meta-tools (`arckit.list_commands`, `arckit.next_step`, `arckit.check_gates`) that let an agent navigate the governance workflow without trial-and-error.
- Prompt-relay execution model: the MCP server returns intake questions + instructions; the agent runs LLM generation in its own session and calls back to persist artefacts. The MCP server never runs an LLM.
- Doc-type registry mirror that is byte-equivalent to `doc-types.mjs` and fails loudly (missing code = error, not silent skip) to prevent the silent-drift class of bugs that has already bitten ArcKit twice.
- Gate-tier encoding that is consistent across all three overlays (OAA/IT4IT MANDATORY `PRIN` hard-stop; TOGAF-ADM MANDATORY `PRIN`/`ADMP`/`BPCM`/`APP`/`GAPA` hard-stop, matching the real doc-type codes in `doc-types.mjs`).
- CI parity check that extends `scripts/check-doc-type-registry.py` into the MCP package so the mirror can never silently diverge.

**Non-Goals:**

- No changes to `plugins/arckit-claude/` source, generated `extensions/` trees, or `scripts/converter.py`.
- No LLM execution in the MCP server. No model calls, no prompt rendering, no agent orchestration.
- No support for jurisdictional overlays (UAE, FR, CA, EU, AT, US, AU, UK Finance, FDE) — only OAA, IT4IT, TOGAF-ADM.
- No database. State is derived from the project's `projects/` directory tree on each call.
- No changes to the existing six MCP servers bundled with the Claude plugin (AWS, Azure, GCP, Data Commons, govreposcrape, govcode).

## Decisions

### D1: Tool shape — hybrid meta-tools + per-command tools

**Decision:** Expose 101 per-command tools (`arckit_requirements`, `arckit_stakeholders`, …, `arckit_adm_preliminary`, …) plus 3 meta-tools. Each per-command tool returns `{id, command, doc_type, intake: [{id, question, required, hint}], instructions, gates: [{code, tier, status}]}`.

**Rationale:** A single "run command" tool would require the agent to know which command to call and what arguments to pass — trial-and-error. Per-command tools make each tool self-describing (doc-type, intake, gates) so an LLM can pick the right one from the tool description alone. The three meta-tools handle discovery (`list_commands`), sequencing (`next_step`), and gate verification (`check_gates`) — operations that don't map to a single command.

**Alternatives considered:**
- *Single tool + command name arg:* simpler surface but the agent must call `arckit.list_commands` first to know what's available, and the tool description would be too long to enumerate 101 commands. Rejected.
- *No meta-tools:* the agent would have to infer next-steps from the command descriptions alone. Rejected — handoffs-graph walking is non-trivial and the agent would duplicate that logic.

### D2: Execution model — prompt relay, not LLM execution

**Decision:** The MCP server is a guidance + state layer. Each command tool returns intake questions, instructions (the command's prompt body, minimally reformatted), and gate status. The agent (Hermes) runs the LLM generation in its own session, then calls back to the MCP server to persist the artefact (via a `arckit.persist_artifact` callback or equivalent).

**Rationale:** The MCP spec does not support streaming LLM calls. A command like `/arckit:requirements` may generate 5–20 pages of markdown. The agent's own session has the context (project files, external docs, prior artefacts) that the MCP server does not. The MCP server's job is to provide the *contract* — what the command expects, what it produces, what gates it checks — not to do the generation.

**Alternatives considered:**
- *MCP server runs the LLM:* would require the server to host model calls, manage auth keys, and manage the project's file context. Violates the "no new runtime deps beyond `mcp`" constraint and the "no breaking changes to plugin" constraint. Rejected.
- *MCP server returns only gate status, agent runs the full command locally:* the agent would still need the intake questions and instructions to know what to generate. Rejected — that's the prompt-relay contract.

### D3: Doc-type registry — import or mirror `doc-types.mjs`

**Decision:** The MCP package ships a generated Python module `arckit_mcp/_registry.py` that is generated from `doc-types.mjs` by a script (`scripts/generate-mcp-registry.py`). The generated file is committed to the repo. A CI parity test (`tests/plugin/test_mcp_command_registry.py`) runs the generator, diffs against the committed file, and fails if they diverge.

**Rationale:** `doc-types.mjs` is an ESM JavaScript module. Python cannot import it directly. Hand-copying 177 type codes into Python would be the exact same silent-drift pattern that TNDR/CMPT and GRNT already caused. A generator + CI parity check is the same pattern ArcKit already uses for `SUBDIR_MAP` and `MULTI_INSTANCE_TYPES` (via `scripts/check-multi-instance-parity.py`). The generator reads `DOC_TYPES`, `SUBDIR_MAP`, `MULTI_INSTANCE_TYPES`, `KNOWN_TYPES` from the `.mjs` file and emits a Python dataclass module.

**Alternatives considered:**
- *Node.js polyglot runtime:* the MCP server would need a Node.js subprocess to eval `doc-types.mjs`. Adds a runtime dep and a process boundary. Rejected — the `mcp` SDK is the only new runtime dep.
- *Hand-maintained Python copy:* same silent-drift risk as the bash `MULTI_INSTANCE_TYPES` duplication. Rejected.
- *MCP server reads the `.mjs` file at runtime:* the server would need a JS parser in Python. Rejected — fragile, and the `.mjs` file has comments and ESM syntax that a simple parser would have to handle.

### D4: Gate-tier encoding — machine-readable gate table

**Decision:** The MCP package ships a `arckit_mcp/gates.py` module that encodes the gate tier for every doc-type code across all overlays. The encoding is derived from the command markdown bodies (MANDATORY/RECOMMENDED/OPTIONAL sections) at generation time, not hand-maintained.

```python
# Generated at build time from command frontmatter + body
# Source: grep MANDATORY/RECOMMENDED/OPTIONAL from commands/*.md
GATE_TIERS: dict[str, dict[str, str]] = {
    # command → {gate_code: tier}
    'oaa_adm_lite': {'PRIN': 'MANDATORY'},
    'it4it_value_network': {'PRIN': 'MANDATORY'},
    'adm_preliminary': {'PRIN': 'MANDATORY'},
    'requirements': {'STKE': 'MANDATORY', 'PRIN': 'RECOMMENDED', 'RISK': 'RECOMMENDED', 'SOBC': 'RECOMMENDED', 'PLAN': 'OPTIONAL'},
    # ...
}
```

**Rationale:** Gate tiers are currently prose in command markdown. An agent calling `arckit.check_gates` needs a machine-readable answer. The generator extracts the tier vocabulary from the markdown body (the "MANDATORY (warn if missing)" / "RECOMMENDED (read if available)" / "OPTIONAL (read if available, skip silently)" blocks) and emits a Python dict. The generator is run in CI alongside the doc-type parity check.

**Alternatives considered:**
- *Hand-maintained gate table:* 101 commands × up to 5 gates each = ~500 entries. Hand-maintained tables drift. Rejected.
- *MCP server parses markdown at runtime:* the server would need a markdown parser and would re-parse on every call. Rejected — the gate table is static per command.

### D5: Multi-instance sequence numbers

**Decision:** The `arckit.persist_artifact` callback accepts a `type_code` and an optional `sequence` arg. If `type_code ∈ MULTI_INSTANCE_TYPES` and `sequence` is not supplied, the server scans the project's `projects/` tree for existing `ARC-NNN-{TYPE}-[0-9]+-v*.md` files and assigns the next sequence number. The server returns the full filename (e.g., `ARC-001-ADR-003-v1.0.md`).

**Rationale:** Multi-instance types (ADR, DIAG, RSCH, etc.) need a monotonically increasing sequence number. The existing `generate-document-id.sh` does this with `--next-num DIR`. The MCP server does the same scan — `projects/{NNN}*/` for the type code — and picks max+1. No external state needed.

### D6: Handoffs-graph walk for `arckit.next_step`

**Decision:** The MCP package ships a `arckit_mcp/handoffs.py` module that is generated from the `handoffs:` frontmatter of every command markdown. The generator parses `handoffs:` lists and `condition:` fields and emits a directed graph:

```python
# command → [(target_command, condition_text, condition_code), ...]
HANDOFFS: dict[str, list[tuple[str, str, str]]] = {
    'requirements': [
        ('data-model', 'DR-xxx data requirements were generated', 'DR'),
        ('research', '', ''),
        ('risk', '', ''),
        ('dpia', '', ''),
    ],
    # ...
}
```

`arckit.next_step(project_id)` walks the graph: for each command that has been completed in the project (determined by the presence of its artefact file in `projects/{id}/`), collect its handoffs. Return the handoffs whose conditions are satisfied (or have no condition). If all handoffs are complete or conditional-and-false, return `next: null`.

**Rationale:** The handoffs graph is already encoded in command frontmatter. The generator extracts it. The walk is a standard graph traversal — no LLM needed.

**Alternatives considered:**
- *LLM-based next-step:* would require the MCP server to run a model call. Violates the prompt-relay constraint. Rejected.
- *Agent infers next-steps from tool descriptions:* the agent would need to read every tool's description and track which commands are done. Rejected — the handoffs graph already encodes this.

### D7: `arckit.check_gates` response shape

**Decision:** `arckit.check_gates(command, project_id)` returns:

```json
{
  "command": "requirements",
  "doc_type": "REQ",
  "gates": [
    {"code": "STKE", "tier": "MANDATORY", "status": "open"},
    {"code": "PRIN", "tier": "RECOMMENDED", "status": "open"},
    {"code": "RISK", "tier": "RECOMMENDED", "status": "open"},
    {"code": "SOBC", "tier": "RECOMMENDED", "status": "open"},
    {"code": "PLAN", "tier": "OPTIONAL", "status": "open"}
  ],
  "gate_blocked": true
}
```

- `status` is `"open"` (artefact not found in project) or `"closed"` (artefact found).
- `gate_blocked: true` iff at least one MANDATORY gate is open.
- RECOMMENDED/OPTIONAL gates are reported but do not set `gate_blocked`.
- MANDATORY gates are hard-stops: the agent MUST close them before proceeding.

**Rationale:** Mirrors the plugin's existing behaviour (MANDATORY = warn + stop, RECOMMENDED = note + continue, OPTIONAL = silently skip). The agent can check `gate_blocked` before deciding whether to proceed.

### D8: TOGAF-ADM doc-type codes

**Decision:** The generator must verify that all doc-type codes used by TOGAF-ADM overlay commands (ADMP and the codes referenced across the 12 TOGAF-ADM command files) exist in `KNOWN_TYPES` of `doc-types.mjs`. If a code is missing, the generator fails with an explicit error listing the missing codes. The MCP package does not register new codes — it mirrors the existing registry.

**Rationale:** The spec says "missing code = error." ADMP is confirmed in `doc-types.mjs` (line 83). The 12 TOGAF-ADM overlay commands reference a small set of doc-type codes: ADMP, BPCM, PRIN, STRAT, REQ, STKE, RISK, SOBC, HLD, DIAG, APPR, ARCH, TECH, DATA. All are present in `KNOWN_TYPES` except `HLD`, which appears once (in `architecture-board.md` as a recommended prerequisite). If a code is missing, the TOGAF-ADM commands that reference it are either (a) using a code that should be registered in `doc-types.mjs` (a plugin bug) or (b) using a code that was intentionally left out. The generator's job is to flag this, not to silently register new codes.

**Action item:** Before writing the generator, verify the TOGAF-ADM doc-type code set (ADMP, BPCM, HLD) against `KNOWN_TYPES` of `doc-types.mjs`. `HLD` is currently missing from `KNOWN_TYPES` and is referenced by `architecture-board.md`; flag this in the design and add a task to either register `HLD` in `doc-types.mjs` (plugin change, out of scope for this change) or adjust the TOGAF-ADM spec wording so the generator passes.

### D9: `mcp` SDK dependency

**Decision:** The `arckit-mcp/` package declares `mcp` (the official Model Context Protocol Python SDK) as its only new runtime dependency. No FastAPI, no Flask, no HTTP server. The `mcp` SDK provides the MCP protocol (stdio transport) out of the box.

**Rationale:** The MCP spec defines stdio as the primary transport. The agent spawns the server as a subprocess and communicates over stdin/stdout. The `mcp` SDK's `Server` class handles the protocol. No HTTP layer needed.

**Alternatives considered:**
- *FastAPI + MCP adapter:* adds a runtime dep and a process boundary. Rejected.
- *Raw MCP protocol implementation:* the `mcp` SDK is the official implementation. Re-implementing the protocol is fragile. Rejected.

### D10: Test and CI layout

**Decision:**
- `tests/plugin/test_mcp_command_registry.py` — doc-type parity: run the generator, diff against committed `_registry.py`, fail on divergence. Also verify `MULTI_INSTANCE_TYPES` and `SUBDIR_MAP` are byte-equivalent.
- `tests/mcp/test_gates.py` — gate-tier encoding: verify that every MANDATORY gate in the gate table is actually referenced in the corresponding command markdown body.
- `tests/mcp/test_next_step.py` — handoffs-graph walk: fixture project with completed artefacts, verify `next_step` returns the correct next command.
- `tests/mcp/test_intake_shape.py` — intake relay: verify that every command tool returns the expected `{id, command, doc_type, intake, instructions, gates}` shape.
- CI: new job in `.github/workflows/` that runs `pytest tests/plugin/test_mcp_command_registry.py tests/mcp/` on PRs that touch `arckit-mcp/`, `plugins/arckit-claude/config/doc-types.mjs`, or `plugins/arckit-claude/commands/`.

## Risks / Trade-offs

- **Silent drift in the generated registry** → Mitigated by the CI parity test. The generator runs in CI on every PR that touches `doc-types.mjs` or `arckit-mcp/`. A divergence is a CI failure, not a silent bug.
- **Handoffs graph is incomplete** → Some commands have no `handoffs:` frontmatter. The graph walker returns `next: null` for those. Acceptable — the agent can still call `arckit.list_commands` to discover available commands.
- **Gate-tier extraction from markdown is fragile** → The MANDATORY/RECOMMENDED/OPTIONAL vocabulary is consistent across all commands (verified by `scripts/check-doc-type-registry.py`). The generator uses a fixed regex pattern. If the vocabulary changes, the generator fails. Acceptable.
- **Multi-instance sequence scan is O(n) over project files** → The project tree is small (tens of artefacts, not thousands). Acceptable.
- **`HLD` referenced by `architecture-board.md` is not in `KNOWN_TYPES`** → Resolved in D8. `HLD` is confirmed missing from `KNOWN_TYPES`. The fix is a plugin change (register it in `doc-types.mjs`), which is out of scope for this change — the TOGAF-ADM overlay spec would need to be adjusted to use only codes that exist in `KNOWN_TYPES`, or the plugin change would need to be tracked separately.
- **No HTTP transport** → The `mcp` SDK supports both stdio and HTTP transports. This design uses stdio only. If an agent needs a persistent server (not a subprocess), the agent can use the HTTP transport. No change to the MCP server code needed — the `mcp` SDK handles both.

## Migration Plan

1. **No data migration.** The MCP server is additive — it reads the project's `projects/` directory and the plugin's `doc-types.mjs`. No existing data is modified.
2. **Rollback:** Remove the `arckit-mcp/` package, the CI job, and the tests. The plugin and CLI are untouched.
3. **Adoption:** The agent (Hermes) adds the `arckit-mcp` server to its MCP config. No changes to existing Claude Code plugin usage.

## Open Questions

None. All design decisions are resolved. The `HLD` registration gap identified in D8 is a plugin-side action item (register `HLD` in `doc-types.mjs`), out of scope for this change — it is tracked in the task list as a pre-generator verification step.
