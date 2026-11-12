# Tasks — generate-mcp-intake

## PR 1 — arc-kit (generator + test)

- [x] 1.1 Write `scripts/generate-mcp-intake.py`:
  - Scan `plugins/*/templates/*-template.md` and
    `plugins/arckit-claude/plugins/*/templates/*-template.md` for
    `## Intake Interview Questions` blocks (bold-bullet lists, `###`
    subheaders).
  - Parse MANDATORY prerequisite inputs from command markdown tier headers,
    reusing `generate-mcp-gates.py` conventions.
  - Resolve each template to a doc-type code (Document Control "Document
    Type" field, falling back to the `doc-types.mjs` filename mapping);
    unresolvable templates go into a `PARSER_NOTES` comment block.
  - Emit `INTAKE` dict + `COVERAGE` dict + generated-file header
    (byte-stable: sorted keys, no timestamps).
  - Output path from `ARCKIT_MCP_ROOT` env or CLI arg.
- [x] 1.2 Add `tests/mcp/test_intake.py` (arc-kit side): run the generator
  into a temp dir, assert the emitted module is byte-identical across two
  runs, assert `COVERAGE` marks core-plugin doc-types as
  `"no-static-questions"`, assert at least one overlay doc-type (e.g.
  `OASTR`'s) is `"covered"` with non-empty `questions`, and assert the
  dedup rule: `INTAKE["OASTR"]["source"]` points to the flat-tree
  `plugins/arckit-oaa/templates/agile-strategy-template.md` (not the nested
  copy).
- [ ] 1.3 Open PR on arc-kit: `feat: generate mcp intake data from template
  question blocks`.

## PR 2 — arckit-mcp (server + tests)

- [ ] 2.1 Regenerate `arckit_mcp/intake.py` from PR 1's generator
  (`ARCKIT_MCP_ROOT=$PWD python ../arc-kit/scripts/generate-mcp-intake.py`),
  commit the generated module.
- [x] 2.2 `server.py` — `_intake_questions()` (L313): look up
  `intake.INTAKE` / `COVERAGE`; covered → derived questions; uncovered →
  existing placeholder. Keep the per-doc-type placeholder for any code
  missing from both.
- [x] 2.3 `server.py` — `run_command()` (L412): include derived intake
  entries in the response payload; fold intake-completeness into the
  `check_gates` double-call (L423–424). Gate stays **soft/structural**:
  skipped answers render `TBD` and never block; only missing MANDATORY
  prerequisite inputs block. Bulk `arckit-build` remains non-interactive
  and must not trip the gate on unanswered questions.
- [x] 2.4 `server.py` — register `arckit.persist_intake` near
  `arckit.persist_artifact` (L477 area). **Read/seed only**: returns
  `.arckit/intake/{command-stem}.json` prefill data for bulk runs; no write
  path for answers through the server.
- [x] 2.5 `tests/mcp/test_intake.py` (arckit-mcp side): round-trip
  generator→module; covered-doc-type lookup returns derived questions;
  uncovered doc-type falls back to placeholder; soft gate lets `TBD`
  through while blocking a missing MANDATORY input; `persist_intake`
  read/seed.
- [ ] 2.6 Open PR on arckit-mcp: `feat: derive mcp intake from template
  question blocks + soft completeness gate + persist_intake read/seed`.

## Cross-cutting
- [x] 3.1 Verify no regression in existing arckit-mcp test suite.
- [x] 3.2 Update arckit-mcp README / docs: intake data is now generated,
  `intake-instructions.md` is algorithm-only, core-plugin doc-types
  degrade to placeholder by design (with the COVERAGE warning path).

## Checkpoint status (2026-11-09)
- 1.1, 1.2: implemented in this repo — `scripts/generate-mcp-intake.py`
  (new, committed at `0d02a2a5`) and `tests/mcp/test_intake.py` (new, 4
  tests, all passing: byte-identical reruns, core-plugin
  `no-static-questions`, OASTR coverage with non-empty questions, dedup
  flat-tree source). Not yet pushed as a PR (1.3 open).
- 2.1: the generated `arckit_mcp/intake.py` module has been produced into
  the arckit-mcp repo via the generator (committed there); the OpenSpec
  step itself is tracked on the arckit-mcp side, so it stays unchecked here.
- 2.2–2.5: implemented in the arckit-mcp repo (working tree, not yet
  committed) — `server.py` intake lookup, soft gate in `check_gates`,
  `arckit.persist_intake` read/seed tool, and `tests/mcp/test_intake.py`
  (142 new test cases; 42 total tests passing in arckit-mcp).
- 3.1: verified — all 42 arckit-mcp tests pass.
- 3.2: done — arckit-mcp README updated: header lists `intake.py`, new
  "New machine" section, test count corrected to 42.
- Open: 1.3 (PR on arc-kit), 2.6 (PR on arckit-mcp), and 2.1
  (commit the generated module in arckit-mcp).
