# Design — generate-mcp-intake

## Context

`arckit-mcp` is a stateless prompt-relay MCP server. It exposes ~120 command
tools via 5 meta-tools, delegates the interview to Agent A, and never proxies
user I/O. Today `_intake_questions()` (server.py L313) synthesizes one
placeholder question per doc-type code from `DOC_TYPES` ×
`_command_doc_types()` (L348–398, hardcoded `name_map` + `overlay_map`).

The intake-upgrade proposal wanted a generated `intake.py` **from
`intake-instructions.md`**. Verified false premise: that file is the
interview *algorithm* (resolve effective template → derive inputs) and
contains zero per-command questions. The real question data:

| Source | What it provides |
|---|---|
| `plugins/*/templates/*-template.md` `## Intake Interview Questions` blocks | **29 question-block templates in the flat tree** — all in overlays: `togaf-adm` 12, `it4it` 6, `oaa` 5, `agent-architecture` 6; **0 in `arckit-claude` core** (78 commands, 67 templates) |
| `plugins/arckit-claude/plugins/{arckit-it4it,oaa}/templates/` | **11 nested duplicates** (it4it × 6 byte-identical; oaa × 5, of which `agile-strategy-template.md` differs only in one command-namespace string: `/arckit-oaa:agile-strategy` vs `/arckit:agile-strategy`). Doc-type `OASTR` is the collision point. |
| Command markdown `**MANDATORY**` tier headers | Prerequisite inputs/artefacts — already parsed by `generate-mcp-gates.py` into `GATE_TIERS` |
| `intake-instructions.md` | Algorithm only; LLM-side, not static |

## Decisions

### 1. Parse template question blocks + MANDATORY tiers, not `intake-instructions.md`
The new `scripts/generate-mcp-intake.py` reads:
- every `## Intake Interview Questions` block under
  `plugins/*/templates/` and `plugins/arckit-claude/plugins/*/templates/`
  (bold-bullet lists under `###` subheaders), and
- the MANDATORY-tier prerequisite inputs from the same command markdown that
  `generate-mcp-gates.py` scans (reusing its regex/tier parsing conventions).

Questions are **keyed by doc-type code**, resolved via each template's
Document Control "Document Type" / doc-types mapping (same mapping
`generate-mcp-registry.py` consumes from `doc-types.mjs`). Keying by command
is wrong: the question list is a property of the *effective template*
(user `.arckit/templates-custom/` overrides are invisible to static
generation), not of the command.

### 2. `INTAKE` dict shape + `COVERAGE` report
```python
INTAKE = {
  "REQ":  {"questions": ["…", "…"], "mandatory_inputs": ["PRIN"],
           "source": "plugins/arckit-togaf-adm/templates/…md"},
  ...
}
COVERAGE = {
  "REQ": "covered",
  "SOMECORECODE": "no-static-questions",  # core plugin has no question block
}
```
`COVERAGE` makes the core-plugin gap *loud*: a consumer seeing
`"no-static-questions"` can warn, and the server falls back to the existing
placeholder. No silent empty dict.

**Tree scan + dedup rule (byte-stability guarantee).** The generator scans
both trees — `plugins/*/templates/*-template.md` (flat) and
`plugins/arckit-claude/plugins/*/templates/*-template.md` (nested) — then
**dedups: the flat tree wins**. A nested template whose doc-type code is
already covered by a flat template is discarded entirely (both its questions
and its MANDATORY inputs come from the flat tree's entry), and its content
differences (the oaa `agile-strategy` namespace-string diff, doc-type
`OASTR`) are irrelevant because the flat copy is authoritative. Scan order
is sorted by path, so output is deterministic regardless of filesystem
traversal order; the byte-stability test (tasks 1.2) runs the generator
twice into a temp dir and asserts identical bytes.

**`COVERAGE` enum source (pinned).** `COVERAGE` is emitted for the **union
of doc-type codes** across all doc-types the MCP server knows, sourced from
the flat-tree `doc-types.mjs` (the same source `generate-mcp-registry.py`
consumes) — NOT the nested tree's `doc-types.mjs` (which doesn't exist).
- `INTAKE[code]["questions"]` non-empty after dedup → `covered`
- code in the union with an empty `INTAKE` entry (no template in either
  tree contributed questions to it, e.g. every `arckit-claude`-only
  doc-type) → `no-static-questions`
- unresolvable template (no parseable Document Control doc-type, no
  filename→doc-type match in `doc-types.mjs`) → recorded in a
  `PARSER_NOTES` comment list in the emitted module, and its doc-type code
  (if any) is excluded from `COVERAGE` (the consumer has no way to know).

### 3. Server changes (arckit-mcp)
- `_intake_questions()` → lookup `INTAKE[code]`; covered → derived list;
  uncovered → existing placeholder (graceful degradation).
- `run_command()` → include derived intake entries in the response;
  intake-completeness folds into the existing `check_gates` double-call
  (L423–424).
- Gate semantics: **soft/structural only** — skipped answers (`TBD`) never
  block; only missing MANDATORY prerequisite *inputs* block. Bulk
  `arckit-build` stays non-interactive.
  - **Tier escalation on collision**: when a soft-gate MANDATORY input
    collides with a hard-gate entry of the same code at a lower tier
    (e.g. `ADMP` is RECOMMENDED in GATE_TIERS but MANDATORY as an intake
    input), the hard-gate entry's tier is escalated to MANDATORY in place.
    The entry is not duplicated — dedup still applies, but the higher
    tier wins. This is a server-side runtime policy; the generated
    `INTAKE` table (arc-kit) remains pure data.
- `arckit.persist_intake` → **read/seed** tool returning saved
  `.arckit/intake/{stem}.json` for bulk prefill. No write path — Agent A
  keeps ownership of persistence.

### 4. Two-repo delivery, one boundary
arc-kit ships the generator; arckit-mcp ships `intake.py` (generated,
DO-NOT-EDIT header) + `server.py` + tests. `intake.py` is regenerated via
`ARCKIT_MCP_ROOT` pointing at the sibling checkout — the same convention
`generate-mcp-registry.py` already uses. No node in CI; parsing is pure
Python/regex.

## Risks / Trade-offs
- **Core-plugin near-coverage**: the main plugin the MCP relay actually
  serves will mostly hit the fallback. Accepted: the COVERAGE report makes
  this visible, and the fallback preserves today's behavior.
- **Question-block format drift**: templates add new subheader styles;
  parser regex must tolerate bold-bullets under `###` headers — covered by
  the round-trip test.
- **Doc-type resolution**: a template may not declare its doc-type code in
  a parseable place; fall back to filename→doc-type mapping from
  `doc-types.mjs` (the registry generator's existing source), and mark
  unresolvable templates in a `PARSER_NOTES` comment list in the emitted
  module.
