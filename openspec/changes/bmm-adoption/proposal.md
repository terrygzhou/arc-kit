# BMM (Business Motivation Model) Adoption — proposal

## Why

ArcKit's motivation/strategy coverage is fragmented: `stakeholders` (STKE)
carries stakeholder drivers, `sobc` (SOBC) carries a UK-regime
Green-Book case, `strategy` (STRAT) synthesises, and `archimate`/`bpcm`
render only a subset of motivation elements (drivers, goals,
constraints, capabilities). No first-class artefact captures the OMG
Business Motivation Model (BMM 1.3) — the metamodel behind BIZBOK's
*Strategy & Stakeholder Alignment* and ArchiMate's Motivation/Strategy
tiers: Case For / Case Against, Assumptions, Impact Factors, and the
Outcomes → Goals → Objectives → Measures ladder with Strategic Themes →
Capabilities traceability.

## What Changes

- **New command `/arckit:bmm`** (`commands/bmm.md`, `doc-type: BMM`,
  `effort: max`): generates the BMM model artefact plus its base
  ArchiMate views (Motivation + Strategy/Capability) in PlantUML
  ArchiMate notation, with an optional companion-view menu (goal/objective
  ladder, case & assumptions overlay, alignment/traceability view,
  Mermaid mindmap sidecar). Reuses the archimate command's
  intake-interview, quality-gate, and self-contained-SVG delivery
  machinery.
- **New doc-type `BMM`** (name `Business Motivation Model`, category
  `Planning`, single-instance): `config/doc-types.mjs`
  (`DOC_TYPES` only — NOT `MULTI_INSTANCE_TYPES` / `SUBDIR_MAP`) plus
  the `/arckit:pages` known-artifact-types table (dual registration,
  enforced by `scripts/check-doc-type-registry.py`).
- **New template `bmm-template.md`**: pipeline sectioning —
  stakeholders & outcomes; outcomes → goals → objectives → measures;
  drivers; assumptions; case for / case against; impact factors;
  strategic themes → capabilities → courses of action → resources;
  stakeholder–outcome matrix; traceability + external references;
  canonical 14-field Document Control + generation footer.
- **New metamodel reference `references/bmm-reference.md`**: BMM 1.3
  element/relationship catalogue, mapping tables (BMM ↔ ArchiMate
  Motivation/Strategy tiers ↔ ArcKit doc-types STKE/SOBC/STRAT/ROAD/
  BPCM/ARCH), BIZBOK S&SA and Green-Book alignment notes, gate criteria.
- **Skill reference extension** (append-only):
  `skills/plantuml-syntax/references/archimate.md` gains a
  `## BMM Projection` section — stereotyped encodings of the
  4.0-only BMM elements (`Objective`, `Measure`, `Strategic Theme` have
  no native macros in the pinned 3.x-flavoured stdlib) plus the
  relationship vocabulary (`Rel_Influence`, `Rel_Realization`,
  `Rel_Composition`, `Rel_Flow`); `SKILL.md` mapping-table row.
- **Artefact pipeline** (defined in `design.md` § Artefact Pipeline,
  guarded by `tests/plugin/test_bmm_conformance.py`):
  inputs (STKE + PRIN mandatory; SOBC/ROAD/WARD/RISK recommended;
  external strategy docs) → BMM model artefact
  (`ARC-{P}-BMM-v1.0.md` at project root) → two sequenced base `ARCH`
  views under `diagrams/` (Motivation; Strategy/Capability) → optional
  companion views (menu) → handoffs (`strategy`, `roadmap`, `sobc`,
  `archimate`), with quality gates G1–G5 and the 3-iteration
  remediation loop.
- **Lockstep**: `BMM` section in every tracked `quality-checklist.md`
  copy (via `scripts/sync-shared-assets.py`); append-only
  traceability clauses in `strategy.md` / `sobc.md`;
  `docs/guides/bmm.md` + guide-tree/site-link parity; regenerated
  `extensions/*` via `scripts/converter.py`.

## Capabilities

### Modified Capabilities
- `slash-commands`: command count 76 → 77; new **BMM Command
  Contract** requirement.

### New Capabilities (deltas)
- `artifact-generation`: gains **BMM Artefact Registration (BMM)**
  (dual registration, single-instance root-level artefact,
  template-driven) and **BMM Artefact Pipeline** (stage sequence,
  ARCH-sequence continuity, companion menu, SVG delivery).
- `plugin-skills`: gains **BMM Projection Reference Ships Inside
  plantuml-syntax** (append-only `## BMM Projection` section, pinned
  encodings + rendered fixture, SKILL.md mapping row).

## Non-goals

- No machine-readable BMM JSON schema / OKF export (deferred
  follow-up change — Option D).
- No new hooks; no C4-mode changes to `/arckit:diagram`; no D2
  sidecar pipeline changes.
- No regime-specific BMM variants — BMM stays universal; the
  UK-regime coupling stays on the conditional `sobc` handoff.
- No renumbering or restructuring of existing `ARCH` sequences,
  templates, or Mermaid blocks (all edits append-only / additive).
- No offline SVG rendering service (reuses the existing self-contained
  SVG delivery clause, pinned PlantUML jar).
