# Tasks: ArcKit MCP Server

## 1. Package Scaffolding

- [ ] 1.1 Create `arckit-mcp/` Python package with `__init__.py`, `pyproject.toml` (declaring `mcp` SDK as the only new runtime dep), and verify `pip install -e arckit-mcp/` succeeds
- [ ] 1.2 Create `arckit_mcp/` module layout: `__init__.py`, `_registry.py` (generated), `gates.py`, `handoffs.py`, `server.py` (MCP server entry point), and verify `python -c "import arckit_mcp"` succeeds

## 2. Doc-Type Registry Generator

- [ ] 2.1 Write `scripts/generate-mcp-registry.py` that reads `plugins/arckit-claude/config/doc-types.mjs` and generates `arckit_mcp/_registry.py` containing `DOC_TYPES` (dict of code → {name, category, regime?, severity?}), `SUBDIR_MAP`, `MULTI_INSTANCE_TYPES` (set), and `KNOWN_TYPES` (set)
- [ ] 2.2 Run the generator to produce the committed `arckit_mcp/_registry.py` and verify all 177 doc-type codes are present (spot-check REQ, STKE, ADR, DIAG, OAPR, OAAL, ITVN, ADMP)
- [ ] 2.3 Verify the TOGAF-ADM referenced codes (ADMP, BPCM, PRIN, STRAT, REQ, STKE, RISK, SOBC, HLD, DIAG, APPR, ARCH, TECH, DATA) against `KNOWN_TYPES` in `doc-types.mjs`; `HLD` is currently missing (referenced by `architecture-board.md`) — flag in PR notes as a plugin-side action item (register in `doc-types.mjs`), out of scope for this change

## 3. Gate-Tier Generator

- [ ] 3.1 Write the gate-tier extraction logic (in `scripts/generate-mcp-registry.py` or a separate `scripts/generate-mcp-gates.py`) that parses MANDATORY/RECOMMENDED/OPTIONAL blocks from every command markdown body in `plugins/arckit-claude/commands/` and `plugins/arckit-oaa/commands/`, `plugins/arckit-it4it/commands/`, `plugins/arckit-togaf-adm/commands/`, and emits `arckit_mcp/gates.py` with `GATE_TIERS: dict[str, dict[str, str]]`
- [ ] 3.2 Verify OAA/IT4IT commands have `PRIN: MANDATORY` and TOGAF-ADM `adm_preliminary` has `ADMP: MANDATORY` in the generated `gates.py`

## 4. Handoffs-Graph Generator

- [ ] 4.1 Write the handoffs extraction logic that parses `handoffs:` frontmatter from every command markdown and emits `arckit_mcp/handoffs.py` with `HANDOFFS: dict[str, list[tuple[str, str, str]]]` (command → list of (target, condition_text, condition_code))
- [ ] 4.2 Verify `requirements` handoffs include `data-model`, `research`, `risk`, `dpia` in the generated `handoffs.py`

## 5. Gate Check Tool (`arckit.check_gates`)

- [ ] 5.1 Implement `arckit.check_gates(command, project_id)` in `arckit_mcp/server.py` that scans `projects/{project_id}/` for gate artefacts (e.g., `ARC-{project_id}-{GATE_CODE}-v*.md`), returns the response shape from spec `arckit-mcp-gates`, and sets `gate_blocked: true` iff any MANDATORY gate is open
- [ ] 5.2 Verify RECOMMENDED/OPTIONAL gates do not set `gate_blocked` (unit test in `tests/mcp/test_gates.py`)

## 6. Next-Step Tool (`arckit.next_step`)

- [ ] 6.1 Implement `arckit.next_step(project_id)` in `arckit_mcp/server.py` that walks the handoffs graph: for each completed command (artefact present in `projects/{project_id}/`), collect its handoffs, filter to those whose conditions are satisfied (or have no condition), and return the next recommended command or `null`
- [ ] 6.2 Verify `next_step` returns `null` when all handoffs are complete (unit test in `tests/mcp/test_next_step.py` with a fixture project)

## 7. List Commands Tool (`arckit.list_commands`)

- [ ] 7.1 Implement `arckit.list_commands()` in `arckit_mcp/server.py` that returns all 101 commands with their doc-type codes, gate codes, and a one-line description, so an agent can pick without trial-and-error
- [ ] 7.2 Verify the response includes all 101 commands (78 core + 5 OAA + 6 IT4IT + 12 TOGAF-ADM) and each entry has a valid doc-type code from `KNOWN_TYPES`

## 8. Per-Command Tools (101 tools)

- [ ] 8.1 Implement the per-command tool registration in `arckit_mcp/server.py` that creates one MCP tool per command (101 total), each returning `{id, command, doc_type, intake: [{id, question, required, hint}], instructions, gates: [{code, tier, status}]}`
- [ ] 8.2 Verify a sample command tool (e.g., `arckit_requirements`) returns the correct shape and gate list (unit test in `tests/mcp/test_intake_shape.py`)

## 9. Persist Artifact Callback

- [ ] 9.1 Implement `arckit.persist_artifact(project_id, type_code, content, sequence=None)` in `arckit_mcp/server.py` that writes the artefact to `projects/{project_id}/ARC-{project_id}-{TYPE_CODE}-v1.0.md` (or with sequence number if `type_code ∈ MULTI_INSTANCE_TYPES` and `sequence` is not supplied, the server scans existing files and assigns next)
- [ ] 9.2 Verify multi-instance types (ADR, DIAG, RSCH) get sequence numbers (unit test in `tests/mcp/`)

## 10. MCP Server Entry Point

- [ ] 10.1 Wire up the `mcp` SDK `Server` in `arckit_mcp/server.py` with stdio transport, registering all 101 per-command tools + 3 meta-tools + `arckit.persist_artifact`
- [ ] 10.2 Verify the server starts and responds to MCP `tools/list` requests (manual test: `python -m arckit_mcp` and send a `tools/list` JSON-RPC request over stdin)

## 11. Tests

- [ ] 11.1 Create `tests/plugin/test_mcp_command_registry.py` that runs the generator, diffs against the committed `_registry.py`, and fails on divergence (doc-type parity)
- [ ] 11.2 Create `tests/mcp/test_gates.py` that verifies gate-tier encoding: every MANDATORY gate in `gates.py` is referenced in the corresponding command markdown body
- [ ] 11.3 Create `tests/mcp/test_next_step.py` with a fixture project (completed `REQ` + `STKE` artefacts) that verifies `next_step` returns `data-model` (condition: DR-xxx generated)
- [ ] 11.4 Create `tests/mcp/test_intake_shape.py` that verifies every command tool returns the expected shape
- [ ] 11.5 Run `pytest tests/plugin/test_mcp_command_registry.py tests/mcp/` and verify all tests pass

## 12. CI

- [ ] 12.1 Add a CI job in `.github/workflows/` that runs `pytest tests/plugin/test_mcp_command_registry.py tests/mcp/` on PRs that touch `arckit-mcp/`, `plugins/arckit-claude/config/doc-types.mjs`, or `plugins/arckit-claude/commands/`
- [ ] 12.2 Verify the CI job runs and passes on a PR that adds a new doc-type code to `doc-types.mjs` but does not regenerate `_registry.py` (should fail)

## 13. Documentation

- [ ] 13.1 Create `docs/guides/mcp.md` that documents how to add the `arckit-mcp` server to an agent's MCP config, lists all available tools, and explains the prompt-relay execution model
- [ ] 13.2 Add a `docs/index.html` entry linking to `docs/guides/mcp.md`
- [ ] 13.3 Run `python3 scripts/check-guide-parity.py --sync` to sync `docs/guides/mcp.md` into `plugins/arckit-claude/docs/guides/` (if the guide is intended to ship to extensions)

## 14. Verification

- [ ] 14.1 Run `python scripts/converter.py` and verify no changes to `extensions/` are produced (the MCP server is not in the converter)
- [ ] 14.2 Run `pytest tests/plugin/` and verify all existing plugin tests still pass (no regressions from the new package)
- [ ] 14.3 Run `./scripts/ci-local.sh` and verify all local CI checks pass
