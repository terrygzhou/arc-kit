# plugin-skills Specification

## Purpose
The ArcKit Claude Code plugin skills subsystem SHALL provide task-specific instruction bundles under `plugins/arckit-claude/skills/` that auto-activate on matching file paths, carry frontmatter metadata consumed by the Claude Code runtime and the converter, and follow the "grown not built" content convention (concise body, highest-signal Gotchas, progressive disclosure into `references/`).

## Requirements

### Requirement: Skills MUST live in directory-per-skill form with valid frontmatter
Each bundled skill SHALL exist at `plugins/arckit-claude/skills/{name}/SKILL.md` with YAML frontmatter declaring `name` (matching the directory name) and `description` of at most 1,536 characters. The frontmatter MAY additionally declare an optional `paths:` glob list for auto-activation and an optional `disallowed-tools:` denylist for the skill's active lifetime.

#### Scenario: Bundled skill frontmatter is complete
- **WHEN** `plugins/arckit-claude/skills/{name}/SKILL.md` is read for any of the five bundled skills (`architecture-workflow`, `arckit-build`, `mermaid-syntax`, `plantuml-syntax`, `wardley-mapping`)
- **THEN** its frontmatter SHALL contain `name: {name}` and a `description` string of 1,536 characters or fewer

#### Scenario: paths-based auto-activation is declared as a glob list
- **WHEN** a skill declares `paths:` (e.g. `architecture-workflow` → `projects/**`, `mermaid-syntax` → `**/*.mmd`, `**/*.mermaid`, `**/ARC-*-DIAG-*.md`, `**/ARC-*-DATA-*.md`, `plantuml-syntax` → `**/*.puml`, `**/*.plantuml`, `**/ARC-*-DIAG-*.md`, `wardley-mapping` → `**/ARC-*-WARD-*.md`, `**/*.wardley`)
- **THEN** `paths:` SHALL be a YAML list of glob strings, and the skill SHALL be auto-activated by the Claude Code runtime when the session touches a file matching any of the globs

#### Scenario: arckit-build declares no paths
- **WHEN** `skills/arckit-build/SKILL.md` is read
- **THEN** its frontmatter SHALL NOT contain a `paths:` key, so the skill is never auto-activated by file access

### Requirement: The five bundled skills MUST ship with their declared role and structure
The plugin SHALL bundle exactly five skills: `architecture-workflow` (onboarding flow that recommends a tailored `/arckit:*` command sequence under a HARD-GATE that forbids running any `/arckit:*` command itself, with sector-specific routing documents in `references/`), `mermaid-syntax` and `plantuml-syntax` (reference skills covering diagram syntax, shipping syntax documentation in `references/` and stating that references are read-only material, not runnable scripts), `wardley-mapping` (Wardley Map syntax plus evolution-stage scoring, gameplay, doctrine, and climatic patterns, with OWM renderer syntax rules), and `arckit-build` (the bulk-build orchestration harness). Reference material SHALL live in each skill's `references/` folder, reachable from the SKILL.md body by relative link.

#### Scenario: Reference skills ship progressive-disclosure material
- **WHEN** the `mermaid-syntax`, `plantuml-syntax`, or `wardley-mapping` skill is active
- **THEN** the SKILL.md body SHALL contain a table mapping diagram/topic types to files under the skill's own `references/` directory, and the body SHALL state that the reference files are documentation to be read with the `Read` tool, not scripts to execute

#### Scenario: architecture-workflow enforces the hard gate
- **WHEN** the `architecture-workflow` skill is active and the user asks for project onboarding
- **THEN** the skill SHALL detect project state (presence of `projects/`, principles document, artefact counts), ask triage questions one at a time, and output only a recommended command plan — it SHALL NOT run any `/arckit:*` command during the process

### Requirement: arckit-build MUST be a Claude-only, manual-invocation-only bulk-build harness
The `arckit-build` skill SHALL declare `disable-model-invocation: true` so a bulk build that commits code is never auto-triggered; it SHALL be invocable only manually via `/arckit:arckit-build`. It SHALL be a YAML-recipe-driven orchestration harness that computes the artefact dependency DAG from the recipe, dispatches one subagent per target per wave in a single message with multiple `Agent` calls, commits one wave per git commit by default, and persists progress to `projects/{P}-{NAME}/.arckit/state.json` after every wave so a build is resumable.

#### Scenario: Manual invocation only
- **WHEN** the model's context matches the arckit-build use cases ("build everything", "run the recipe", "resume the build")
- **THEN** the skill SHALL NOT be auto-invoked by the model because of `disable-model-invocation: true`; only the explicit user command `/arckit:arckit-build` SHALL start the harness

#### Scenario: Resumable, idempotent build
- **WHEN** a build is started with `--resume` after a prior partial run
- **THEN** the harness SHALL read `state.json`, skip every target whose state is `complete`, whose output file exists at the recorded path, and whose input files' SHA-256 hashes match those recorded at build time, and continue from the last incomplete wave

#### Scenario: Recipe-driven target resolution
- **WHEN** the harness resolves a recipe by name
- **THEN** it SHALL apply the precedence: project override `.arckit/recipes/{NAME}.yaml`, then core plugin `${CLAUDE_PLUGIN_ROOT}/skills/arckit-build/recipes/{NAME}.yaml`, then sibling community plugins `${CLAUDE_PLUGIN_ROOT}/../arckit-*/recipes/{NAME}.yaml` (first hit wins); the default recipe SHALL be `uk-saas`

### Requirement: Skill content MUST follow the "grown not built" convention
Each skill's highest-signal content SHALL be its Gotchas section (`## Common Gotchas` or `## Common Syntax Gotchas`), capturing repeatable mistakes as they are observed while the skill is active. The SKILL.md body SHALL remain concise because it stays in context across turns and costs recurring tokens; detailed reference material SHALL be pushed into the skill's `references/` folder for progressive disclosure, and the `description` field SHALL lead with the key use case.

#### Scenario: Gotchas are present in reference skills
- **WHEN** `mermaid-syntax`, `plantuml-syntax`, or `wardley-mapping` is read
- **THEN** its SKILL.md SHALL contain a Gotchas section listing, at minimum, the recurring syntax or positioning footguns with their fix (e.g. Mermaid `<br/>` in edge labels, `end` as a reserved node ID, PlantUML `Rel_Down` contradicting `Lay_Right`, Wardley positioning by age rather than market maturity)

#### Scenario: Body stays concise, detail lives in references/
- **WHEN** a skill's detailed syntax or doctrine material would exceed a short section
- **THEN** the SKILL.md body SHALL link to a file in the skill's `references/` directory rather than inlining the detail

### Requirement: The converter MUST strip Claude-only skill frontmatter for non-Claude targets
`scripts/converter.py` SHALL strip the `paths:` frontmatter key from every generated `SKILL.md` when producing non-Claude extension targets (Codex, Gemini, OpenCode, Copilot, Kimi), so generated skills carry only the target-platform-valid fields.

#### Scenario: Generated Codex skill has no paths key
- **WHEN** `python scripts/converter.py` generates `extensions/arckit-codex/skills/architecture-workflow/SKILL.md` from the Claude source
- **THEN** the generated frontmatter SHALL contain `name` and `description` and SHALL NOT contain a `paths:` key, while the Claude source `plugins/arckit-claude/skills/architecture-workflow/SKILL.md` retains `paths: ["projects/**"]`

### Requirement: Skill directories MUST be re-scannable without restarting the session
During plugin development, the `/reload-skills` command SHALL re-scan the skill directories and pick up new or changed `SKILL.md` files without requiring the Claude Code session to restart.

#### Scenario: Development-time skill reload
- **WHEN** a developer adds or edits `plugins/arckit-claude/skills/{name}/SKILL.md` and issues `/reload-skills` in an active session
- **THEN** the session SHALL see the new or updated skill without a restart, and the skill's frontmatter and body SHALL be re-read from disk

### Requirement: Onboarding Triage Answers MUST Seed The Project Intake Store
When the `architecture-workflow` skill completes its triage questions (sector, project type, current stage, primary goal, and any deep questions asked), it SHALL persist those answers to `projects/{NNN}-{slug}/.arckit/intake/shared.json` (creating the path when missing and merging without clobbering existing keys) and SHALL state in its plan output that the answers were saved so the recommended commands will prefill from them. Artefact-producing commands' intake interviews SHALL treat `shared.json` as a prefill source with lower precedence than existing `projects/` artefacts and that command's own saved answers. Persisting answers SHALL NOT count as running a command: the HARD-GATE (no `/arckit:*` execution during onboarding) remains fully in force.

#### Scenario: Triage answers seed the shared intake file
- **WHEN** the user completes the triage questions for a new project and `architecture-workflow` outputs its recommended command plan
- **THEN** the sector, project type, stage, and goal answers are written to `projects/{NNN}-{slug}/.arckit/intake/shared.json` and the plan message notes that the answers were saved

#### Scenario: Seeded answers prefill later commands
- **WHEN** a recommended command (e.g. `/arckit:principles`) runs its intake interview after onboarding and a template input matches a seeded answer (e.g. the sector or the compliance frameworks chosen in a deep question)
- **THEN** the input is prefilled from `shared.json` and not re-asked

#### Scenario: Precedence is preserved
- **WHEN** a later run of the same command has a saved per-command answer in `.arckit/intake/{command-stem}.json` that conflicts with `shared.json`
- **THEN** the per-command answer wins; when an existing `projects/` artefact states a value, it wins over both

#### Scenario: HARD-GATE unaffected by persistence
- **WHEN** `architecture-workflow` has persisted its triage answers
- **THEN** it still has executed no `/arckit:*` command and its output remains a recommended plan only — the user decides when and what to run

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
