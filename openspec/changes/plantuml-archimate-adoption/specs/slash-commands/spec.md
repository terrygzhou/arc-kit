# slash-commands Delta — plantuml-archimate-adoption

## MODIFIED Requirements

### Requirement: Commands Are Exposed From Markdown Files
The system SHALL expose every file in `plugins/arckit-claude/commands/`
as a slash command `/arckit:<name>` where `<name>` is the filename stem,
and the YAML frontmatter at the top of the file SHALL be the source of
truth for command metadata.

#### Scenario: 75 commands ship
- **WHEN** the `arckit` plugin loads from `plugins/arckit-claude/`
- **THEN** all 76 files in `commands/` (the 75-file baseline plus
  `archimate.md`) are available as `/arckit:<name>` commands

#### Scenario: command set is stable
- **WHEN** the baseline is counted
- **THEN** 76 `.md` command files exist in
  `plugins/arckit-claude/commands/` (75 pre-existing + `archimate.md`),
  each carrying the `description` and `doc-type` fields

#### Scenario: frontmatter is authoritative
- **WHEN** a command body and its frontmatter disagree about a field
- **THEN** the frontmatter value governs (e.g. `effort`, `doc-type`)
  and the body is treated as prose instructions

## ADDED Requirements

### Requirement: ArchiMate View Command Contract
The plugin SHALL ship `commands/archimate.md` (`/arckit:archimate`,
`effort: high`, `doc-type: ARCH`) that generates ArchiMate-metamodel
views in PlantUML ArchiMate notation. The command SHALL: read existing
REQ/HLD/DLD/WARD artefacts for layer and element extraction; run the
standard intake interview (single call, max 2 rounds — Q1 layer
selection (business / application / technology, optional data),
Q2 motivation/capability inclusion); load
`skills/plantuml-syntax/references/archimate.md` (Pinned API section
governs the emitted include line and element/relationship surface);
evaluate an ArchiMate-specific quality gate (every element
stereotyped into exactly one layer, realization edges point from the
more concrete layer to the more abstract one, ≤ 12 elements per
layer) with the 3-iteration remediation loop; and write
`ARC-NNN-ARCH-NNN-v1.0.md` under `projects/{p}/diagrams/` via
`generate-document-id.mjs` with `--next-num` sequencing.

#### Scenario: archimate command writes a governed artefact
- **WHEN** `/arckit:archimate "business layer for the payment project"`
  completes generation
- **THEN** it has written
  `projects/001-*/diagrams/ARC-001-ARCH-001-v1.0.md` (next free
  sequence), carrying a PlantUML block whose include line matches the
  pinned API in `references/archimate.md`, the ArchiMate quality-gate
  table, and the canonical Document Control header + generation footer

#### Scenario: quality gate fails and is remediated
- **WHEN** a generated ArchiMate diagram mixes C4 and ArchiMate
  elements, or places an element without a layer stereotype
- **THEN** the remediation loop re-generates with the element moved
  into its layer (or the diagram split per layer) before the file is
  written, up to 3 iterations, with accepted trade-offs documented
  after
