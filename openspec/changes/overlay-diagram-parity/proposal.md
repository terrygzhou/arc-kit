## Why

Mermaid diagram support is asymmetric across the bundled overlay plugins. `togaf/adm` commands ship an explicit step that reads the `mermaid-syntax` skill's reference files (`architecture-repository`, `data-architecture`, `gap-analysis`, and 5 more), but no other overlay does: `agent/architecture` renders 13 ` ```mermaid ` blocks embedded in 6 templates with no syntax-reference load, and `oaa` emits a Mermaid C4 Component diagram (`product-architecture`) and a `data-flow-diagram.mmd` deliverable (`oaa-adm-lite`) the same way. The `mermaid-syntax` skill's `paths:` auto-activation only fires on files matching `**/*.mmd`, `**/*.mermaid`, `**/ARC-*-DIAG-*.md`, and `**/ARC-*-DATA-*.md`, so overlay artefacts named `ARC-*-DES-*`, `ARC-*-SEC-*`, etc. never auto-trigger it — an explicit command-level load is the only parity mechanism.

## What Changes

- New requirement under the `plugin-skills` capability: every artefact-producing command (core or overlay) that renders Mermaid diagrams SHALL include an explicit step that reads the relevant `${CLAUDE_PLUGIN_ROOT}/skills/mermaid-syntax/references/*.md` file(s) before diagram authoring, mirroring the existing `togaf/adm` wording.
- Add that load step to the six `agent/architecture` commands (`agent-design`, `agent-governance`, `agent-integration`, `agent-inventory`, `agent-maturity`, `agent-security` — their templates embed the 13 ` ```mermaid ` blocks) and to the two `oaa` commands (`product-architecture`, `oaa-adm-lite`).
- Regenerate the generated extensions (`extensions/arckit-codex`, `arckit-gemini`, `arckit-opencode`, `arckit-copilot`, `arckit-paperclip`) via `python scripts/converter.py`.
- Non-goals: no new commands; no changes to the five pinned bundled skills (the `plugin-skills` spec pins exactly five); no `mmdc`/mermaid-cli validation hook; no expansion of OAA's diagramming scope (its template's "outcomes, not outputs… not diagram count" tone guard stays intact — OAA gets syntax pointers only, not diagramming mandates).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `plugin-skills`: the `mermaid-syntax` reference skill gains a consumption contract — diagram-emitting commands must load its `references/` explicitly because `paths:` auto-activation does not cover overlay artefact filenames.

## Impact

- Source edits: 8 command files under `plugins/arckit-claude/plugins/agent/architecture/commands/` and `plugins/arckit-claude/plugins/oaa/commands/`.
- Spec: `openspec/specs/plugin-skills/spec.md` gains one requirement (via this change's delta).
- Generated targets: all five converter outputs are regenerated; they are gitignored and never hand-edited.
- No runtime, hook, or CLI changes.
