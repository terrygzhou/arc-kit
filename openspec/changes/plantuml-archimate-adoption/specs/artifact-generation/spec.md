# artifact-generation Delta — plantuml-archimate-adoption

## ADDED Requirements

### Requirement: ArchiMate Artefact Registration (ARCH)
The system SHALL register the doc-type code `ARCH` (name `ArchiMate
View`, category `Architecture`) in `config/doc-types.mjs` in all three
structures — `DOC_TYPES`, `MULTI_INSTANCE_TYPES` (filenames carry a
`-NNN-` sequence, e.g. `ARC-001-ARCH-001-v1.0.md`), and
`SUBDIR_MAP` → `diagrams` — AND in the `/arckit:pages`
known-artifact-types table, satisfying the dual-registration guard
(`scripts/check-doc-type-registry.py`). Generation SHALL be
template-driven from `templates/archimate-template.md` (custom
override `.arckit/templates/archimate-template.md` first, per the
template-driven generation contract), and the template SHALL carry the
canonical 14-field Document Control table and generation footer so
rendered `ARC-*-ARCH-*` artefacts pass checklist common checks #1 and
#7.

#### Scenario: unsequenced ARCH write is corrected at the gate
- **WHEN** a write targets `projects/001-*/ARC-001-ARCH-v1.0.md`
  (missing `-NNN-` sequence)
- **THEN** `validate-arc-filename.mjs` assigns the next sequence
  (`ARC-001-ARCH-001-v1.0.md`) and routes the file to `diagrams/`

#### Scenario: ARCH code is registered in both halves
- **WHEN** `scripts/check-doc-type-registry.py` runs after this change
- **THEN** `ARCH` is present in `DOC_TYPES`, `MULTI_INSTANCE_TYPES`,
  `SUBDIR_MAP`, and the pages known-artifact-types table — no parity
  error

#### Scenario: archimate template renders a conforming Document Control
- **WHEN** an artefact is generated from `archimate-template.md`
- **THEN** its Document Control table lists all 14 canonical fields
  (placeholders permitted) and its generation footer carries Generated
  by, Generated on, ArcKit Version, Project, and Model
