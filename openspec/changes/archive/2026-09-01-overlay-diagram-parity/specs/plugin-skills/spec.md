# plugin-skills Delta — overlay-diagram-parity

## ADDED Requirements

### Requirement: Diagram-Emitting Commands MUST Explicitly Load Mermaid Syntax References
Because the `mermaid-syntax` skill's `paths:` auto-activation only fires on files matching `**/*.mmd`, `**/*.mermaid`, `**/ARC-*-DIAG-*.md`, and `**/ARC-*-DATA-*.md`, every artefact-producing command (core or bundled overlay) that renders Mermaid diagrams — whether ` ```mermaid ` blocks are embedded in the command body or in the template the command reads — SHALL include an explicit step that reads the diagram types' files under `${CLAUDE_PLUGIN_ROOT}/skills/mermaid-syntax/references/` before authoring the diagrams, following the wording pattern established by the `togaf/adm` commands. Commands that emit no Mermaid diagrams SHALL remain untouched.

#### Scenario: togaf-adm remains the compliant reference
- **WHEN** any `togaf/adm` command that embeds Mermaid (e.g. `/arckit:gap-analysis`) runs
- **THEN** it reads the relevant `skills/mermaid-syntax/references/*.md` file(s) in a dedicated "Load Mermaid Syntax References" step before generating its diagrams, and this change does not alter that behaviour

#### Scenario: agent-architecture commands load the references
- **WHEN** an `agent/architecture` command (`agent-design`, `agent-governance`, `agent-integration`, `agent-inventory`, `agent-maturity`, or `agent-security`) runs and its template contains ` ```mermaid ` blocks
- **THEN** the command's body includes an explicit step reading the matching `skills/mermaid-syntax/references/` file(s) (e.g. `flowchart.md`, `quadrantChart.md`, `pie.md`) for the diagram types present in that template, before the diagram sections are authored

#### Scenario: oaa commands load the references without expanding OAA's diagram scope
- **WHEN** `product-architecture` runs and is to render its Mermaid C4 Component diagram, or `oaa-adm-lite` runs and is to write the `data-flow-diagram.mmd` deliverable
- **THEN** the command reads the relevant `skills/mermaid-syntax/references/` file(s) first, and the command otherwise continues to state diagram expectations as pointers (a diagram is a review aid), never as an output-count mandate

#### Scenario: non-diagram commands are untouched
- **WHEN** a command (core or overlay) emits no Mermaid diagrams in its body or its rendered template
- **THEN** the change does not add a reference-load step to it
