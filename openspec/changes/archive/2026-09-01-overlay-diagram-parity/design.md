# Design — overlay-diagram-parity

## Context

See proposal.md for motivation. Current state: `togaf/adm` commands carry a numbered "### N. Load Mermaid Syntax References" step that names the exact `${CLAUDE_PLUGIN_ROOT}/skills/mermaid-syntax/references/{type}.md` files matching the diagram types embedded in the command body. `agent/architecture` embeds its 13 ` ```mermaid ` blocks in templates (not command bodies); `oaa` describes its diagrams in prose (C4 Component; `data-flow-diagram.mmd`). No core command change is needed — the core set already loads where it diagrams.

## Goals / Non-Goals

- Goal: one consistent, findable load step per diagram-emitting command, with wording close enough to the `togaf/adm` pattern that a reader recognises the convention.
- Non-Goal: no template edits — syntax guidance must stay at the command layer so template overrides in `.arckit/templates-custom/` (including user-edited copies that drop diagram hints) still inherit the load step. No hook, no new skill, no `mmdc` validation.

## Decisions

1. **Command-level load, not template-level hint.** Alternative: add "read the mermaid-syntax references" inside the six agent-architecture templates. Rejected because templates are the user-overridable tier (`template-customization` spec: custom copy wins) — a hint in a template disappears when the user customises it, whereas the command body is the fixed tier.
2. **Per-template file selection, not a blanket "read all references".** Each command names only the reference files for the diagram types its template actually embeds (e.g. `agent-maturity` → `flowchart.md` + `pie.md`; `agent-security` → `flowchart.md`). Keeps context cost proportional to the diagrams actually rendered; matches the `togaf/adm` precedent of naming specific files.
3. **Reference resolution stays relative to the source plugin root.** Overlay commands already use `${CLAUDE_PLUGIN_ROOT}` for their own templates; the `skills/mermaid-syntax/` path resolves to the core plugin root (skills live there, not inside the overlay plugin). Verified by the `togaf/adm` precedent — the same cross-plugin reference already ships and is converted without issue.
4. **OAA keeps pointers, gets load steps.** `product-architecture` and `oaa-adm-lite` gain only the read step; no new "you must produce diagram X" language, preserving the `oaa-adm-lite-template.md` outcomes-over-outputs guard.

## Risks / Trade-offs

- [Diagram type added to a template later without updating the command's load list] → the step's file list is the source of truth; tasks.md records a re-check step, and the delta spec's agent-architecture scenario ("for the diagram types present in that template") makes drift a spec violation CI review can catch.
- [Converter output diff is large (8 commands × 5 targets)] → generated dirs are gitignored; the converter is deterministic and idempotent, so diff noise is confined to the working tree.
- [Wording drift between the 8 edited commands] → copy the `togaf/adm` step structure verbatim ("### N. Load Mermaid Syntax References" + one sentence) and adapt numbering per file.

## Migration Plan

Pure additive prose edits to 8 command files + converter regeneration. Rollback = revert the commit; no state, schema, or install-time change.

## Open Questions

None.
