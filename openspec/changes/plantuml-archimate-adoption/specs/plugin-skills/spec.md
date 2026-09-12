# plugin-skills Delta — plantuml-archimate-adoption

## ADDED Requirements

### Requirement: ArchiMate Notation Reference Ships Inside plantuml-syntax
The `plantuml-syntax` skill SHALL ship a read-only ArchiMate notation
reference at `references/archimate.md`, reachable from `SKILL.md` by
relative link, beginning with a **Pinned API** section that records:
the exact stdlib include line, the element types available per
ArchiMate layer (business / application / technology / data /
motivation), the relationship functions (realization, serving,
aggregation, composition, association, assignment, derivation, and
any others verified), the colour-library include, the minimum
PlantUML version, and the notation decision (native ArchiMate vs
C4-PlantUML fallback). The reference SHALL state element-count
thresholds (≤ 12 elements per layer) and antipatterns (mixing C4 and
ArchiMate elements in one diagram, unlabelled cross-layer edges).
`SKILL.md` SHALL list `references/archimate.md` in its
topic→reference mapping table, and the skill's `paths:` globs SHALL
include `**/ARC-*-ARCH-*.md`.

#### Scenario: archimate command loads the pinned reference
- **WHEN** `/arckit:archimate` runs
- **THEN** it reads `references/archimate.md` and emits PlantUML
  whose include line, element types, and relationship functions match
  the Pinned API section — not an ad-hoc variant

#### Scenario: skill auto-activates on generated ArchiMate artefacts
- **WHEN** the session touches `projects/001-*/diagrams/ARC-001-ARCH-001-v1.0.md`
- **THEN** the `plantuml-syntax` skill auto-activates via its
  `**/ARC-*-ARCH-*.md` path glob
