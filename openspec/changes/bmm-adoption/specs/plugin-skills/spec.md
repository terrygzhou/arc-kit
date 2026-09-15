# plugin-skills Delta — bmm-adoption

## ADDED Requirements

### Requirement: BMM Projection Reference Ships Inside plantuml-syntax
The `plantuml-syntax` skill SHALL ship a `## BMM Projection` section
appended to `references/archimate.md` (the pinned-Archimate
reference) that records, for the BMM 1.3 elements without native
macros in the pinned 3.x-flavoured stdlib: the exact stereotyped
encodings (`Objective` → `Motivation_Goal(alias, "Objective: …")`,
`Measure` → `Motivation_Goal(alias, "Measure: …")`, `Strategic
Theme` → `Strategy_Capability(alias, "Theme: …")` or a `group`
container), the required `legend` blocks for any custom notation,
the BMM relationship vocabulary mapped onto pinned macros
(`Rel_Influence` for driver / assumption / impact-factor edges,
`Rel_Realization` concrete → abstract for goal/theme realization,
`Rel_Composition` whole → part for capability nesting per the BPCM
idiom, `Rel_Flow` for outcome streams, and a legend-defined
"contributes to" edge where no native macro exists), the
element-count threshold (≤ 12 per layer, split-never-drop), and a
link to the rendered sample fixture under
`tests/fixtures/archimate/bmm/`. The section SHALL be append-only:
every byte of pre-existing `references/archimate.md` content (incl.
Pinned API and all Mermaid-adjacent sections) is preserved, enforced
by the extended SHA-256 byte-preservation fixture. `SKILL.md` SHALL
list a mapping-table row (BMM motivation/strategy views →
`references/archimate.md` § BMM Projection); BMM-carrying views are
`ARC-*-ARCH-*` documents, so the skill's existing
`**/ARC-*-ARCH-*.md` path glob covers them — no new glob.

#### Scenario: BMM views use the pinned projection, not ad-hoc notation
- **WHEN** `/arckit:bmm` (or `/arckit:archimate` with a
  motivation overlay sourced from a BMM artefact) emits an
  Objective, Measure, or Strategic Theme
- **THEN** the emitted PlantUML uses the stereotyped encodings and
  relationship macros recorded in § BMM Projection, with the
  corresponding `legend` block, and matches the rendered fixture in
  `tests/fixtures/archimate/bmm/`

#### Scenario: append-only edit leaves the Pinned API byte-identical
- **WHEN** the SHA-256 byte-preservation fixture is re-run after
  adding § BMM Projection
- **THEN** every pre-existing section of `references/archimate.md`
  hashes identically to the extended fixture; only the appended
  section is new

### Requirement: BMM Metamodel Reference Ships With The Plugin
The plugin SHALL ship a read-only metamodel reference at
`plugins/arckit-claude/references/bmm-reference.md` (reachable from
the `bmm.md` command body by explicit load, the same pattern as
`references/citation-instructions.md`), containing: the BMM 1.3
element and relationship catalogue; mapping tables (BMM element ↔
ArchiMate Motivation/Strategy tier ↔ ArcKit doc-types STKE/SOBC/
STRAT/ROAD/BPCM/ARCH); alignment notes with BIZBOK *Strategy &
Stakeholder Alignment* and the UK Green-Book 5-case model; and the
gate criteria G1–G5 used by the command's quality gate.

#### Scenario: the bmm command loads the metamodel reference
- **WHEN** `/arckit:bmm` runs
- **THEN** it reads `references/bmm-reference.md` before generation,
  and the sections of the generated [A1] artefact correspond 1:1 to
  the pipeline sections defined by that reference
