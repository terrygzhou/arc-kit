# slash-commands Delta — bmm-adoption

## MODIFIED Requirements

### Requirement: Commands Are Exposed From Markdown Files
The system SHALL expose every file in `plugins/arckit-claude/commands/`
as a slash command `/arckit:<name>` where `<name>` is the filename stem,
and the YAML frontmatter at the top of the file SHALL be the source of
truth for command metadata.

#### Scenario: 75 commands ship
- **WHEN** the `arckit` plugin loads from `plugins/arckit-claude/`
- **THEN** all 77 files in `commands/` (the 75-file baseline plus
  `archimate.md` plus `bmm.md`) are available as `/arckit:<name>`
  commands

#### Scenario: command set is stable
- **WHEN** the baseline is counted
- **THEN** 77 `.md` command files exist in
  `plugins/arckit-claude/commands/` (75 pre-existing + `archimate.md`
  + `bmm.md`), each carrying the `description` and `doc-type` fields

#### Scenario: frontmatter is authoritative
- **WHEN** a command body and its frontmatter disagree about a field
- **THEN** the frontmatter value governs (e.g. `effort`, `doc-type`)
  and the body is treated as prose instructions

Note: this delta assumes `plantuml-archimate-adoption` is archived
first (its delta moves the baseline 75 → 76); archive both in that
order.

## ADDED Requirements

### Requirement: BMM Command Contract
The plugin SHALL ship `commands/bmm.md` (`/arckit:bmm`, `effort: max`,
`doc-type: BMM`) that generates the project's OMG Business Motivation
Model (BMM 1.3) artefact plus its ArchiMate view set. The command
SHALL: require STKE + PRIN (stop-and-ask if missing); read SOBC/
ROAD/WARD/RISK if present and note if missing; read external strategy
documents from `external/` with citation markers per
`references/citation-instructions.md`; run the standard intake
interview in ONE call (max 2 rounds — Q1 model scope: full model /
motivation-only / strategy-only; Q2 companion menu multiSelect: goal
ladder / case & assumptions overlay / alignment view / Mermaid
mindmap; skip rules when the arguments already name the scope or
menu); load `references/bmm-reference.md` (BMM element/relationship
catalogue + mapping tables + gate criteria) and
`skills/plantuml-syntax/references/archimate.md` § BMM Projection
(pinned encodings for `Objective`, `Measure`, `Strategic Theme` and
the relationship vocabulary); evaluate gates G1–G5 (ladder
completeness, no empty Case/Assumption/Impact-Factor quadrants,
every strategic theme realizes ≥ 1 capability, view conformance —
pinned include, ≤ 12 elements/layer, realization concrete → abstract,
legend for custom notation — and ARCH sequence continuity) with the
3-iteration remediation loop; write the single-instance root-level
`ARC-NNN-BMM-v1.0.md` from `templates/bmm-template.md`, then the
base views [A2] Motivation and [A3] Strategy/Capability as
sequenced `diagrams/ARC-NNN-ARCH-NNN-v1.0.md` documents via
`generate-document-id.mjs --next-num` (never renumbering existing
ARCH documents); emit selected Stage-3 companions; and render every
PlantUML block to a self-contained `.svg` (pinned PlantUML
1.2026.8 jar, offline, no non-local URLs). The command SHALL declare
handoffs to `strategy`, `roadmap`, `sobc` (UK-regime condition), and
`archimate`.

#### Scenario: bmm command writes a governed model artefact
- **WHEN** `/arckit:bmm "001"` completes generation with the default
  full-model scope and base views only
- **THEN** it has written `projects/001-*/ARC-001-BMM-v1.0.md`
  (single-instance, project root, 14-field Document Control +
  generation footer, all nine pipeline sections populated — no
  placeholder-only sections) plus two sequenced
  `projects/001-*/diagrams/ARC-001-ARCH-{NNN}-v1.0.md` base views
  ([A2] Motivation, [A3] Strategy/Capability) whose PlantUML blocks
  carry the pinned include line and whose self-contained `.svg`
  renders are committed alongside

#### Scenario: quality gate fails and is remediated
- **WHEN** a generated BMM model has a goal without an objective
  (G1) or a strategic theme with no capability realization (G3)
- **THEN** the remediation loop re-generates the affected section /
  view before the file is written, up to 3 iterations, with accepted
  trade-offs documented in the artefact after

#### Scenario: intake interview is single-call, bounded
- **WHEN** `/arckit:bmm` starts with no scope or menu in the
  arguments
- **THEN** both questions appear in ONE structured-question call
  (Q1 scope with the full model marked Recommended; Q2 menu with
  base-views-only marked Recommended) and the interview never
  exceeds 2 rounds; arguments that name the scope or menu items skip
  the corresponding question
