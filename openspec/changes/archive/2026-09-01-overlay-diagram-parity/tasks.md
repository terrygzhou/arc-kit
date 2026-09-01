# Tasks — overlay-diagram-parity

## 1. Add load steps to agent/architecture commands
Source root: `plugins/arckit-claude/plugins/agent/architecture/commands/`. Insert a "### N. Load Mermaid Syntax References" step (numbering follows each file's existing step sequence, placed before the diagram-rendering step) naming exactly the references matching the ` ```mermaid ` types in the corresponding template. Wording mirrors `togaf/adm/commands/gap-analysis.md` §5.

- [x] 1.1 `agent-design.md` → `references/c4.md` + `references/flowchart.md` (C4Component, flowchart LR/TD)
- [x] 1.2 `agent-governance.md` → `references/flowchart.md` (flowchart TD)
- [x] 1.3 `agent-integration.md` → `references/sequenceDiagram.md`
- [x] 1.4 `agent-inventory.md` → `references/flowchart.md` (flowchart TD)
- [x] 1.5 `agent-maturity.md` → `references/gantt.md` + `references/quadrantChart.md`
- [x] 1.6 `agent-security.md` → `references/flowchart.md` + `references/mindmap.md`

## 2. Add load steps to oaa commands
- [x] 2.1 `plugins/arckit-claude/plugins/oaa/commands/product-architecture.md` → load `references/c4.md` before the "Product Architecture Diagram" (C4 Component) section; keep diagram language as a review aid, no new mandates
- [x] 2.2 `plugins/arckit-claude/plugins/oaa/commands/oaa-adm-lite.md` → load `references/flowchart.md` before writing the `data-flow-diagram.mmd` deliverable

## 3. Regenerate and validate
- [x] 3.1 Run `.venv/bin/python scripts/converter.py` (regenerates `extensions/arckit-codex`, `arckit-gemini`, `arckit-opencode`, `arckit-copilot`, `arckit-paperclip`)
- [x] 3.2 Spot-check one generated target: the load step survives conversion and `${CLAUDE_PLUGIN_ROOT}` paths are target-appropriate (e.g. `extensions/arckit-codex` skill-path form)
- [x] 3.3 `pytest tests/codex/test_codex_extension.py`
- [x] 3.4 `npx markdownlint-cli2 "plugins/arckit-claude/plugins/{agent,oaa}/**/*.md"` (or full `**/*.md`)
- [x] 3.5 Re-verify parity: `grep -L "Load Mermaid Syntax References" <the 8 edited files>` returns nothing; `grep -rl '```mermaid' .../agent/architecture/templates/` still maps to commands that now load

## 4. Close out
- [x] 4.1 `openspec validate overlay-diagram-parity`
- [x] 4.2 Conventional commit (`feat:` or `docs:` per reviewer judgement — content is command behaviour, so `feat:`), e.g. `feat: add mermaid-syntax reference loads to agent-architecture and oaa overlay commands`
