# BMM Adoption — design

## Context

Motivation content is scattered across ArcKit: STKE (stakeholder
drivers), SOBC (UK Green-Book 5-case), STRAT (synthesis), WARD
(positioning), BPCM/ArchiMate views (drivers, goals, constraints,
capabilities — a proper subset of BMM). BMM 1.3 (OMG Business
Motivation Model) is the metamodel underpinning BIZBOK *Strategy &
Stakeholder Alignment* and ArchiMate's Motivation/Strategy tiers; it
adds the missing quadrants — Case For / Case Against, Assumptions,
Impact Factors, and the Outcomes → Goals → Objectives → Measures
ladder with Strategic Themes → Capabilities → Courses-of-Action
traceability.

Key constraint: the pinned PlantUML ArchiMate stdlib
(`skills/plantuml-syntax/references/archimate.md`, PlantUML 1.2026.8)
is 3.x-flavoured. It exposes `Motivation_Stakeholder/Driver/Goal/
Outcome/Constraint/Assessment/Principle/Value` and `Strategy_
Capability/CourseOfAction/Resource/ValueStream`, but **no native
macros for `Objective`, `Measure`, or `Strategic Theme`** (ArchiMate
4.0 / BMM-aligned additions). Those three need stereotyped encodings
+ a legend; full BMM fidelity lives in the markdown artefact, and the
diagram layer is a *projection* of it (recorded in spike task 0).

## Goals / Non-Goals

**Goals:** a single governed BMM artefact per project that is the
canonical "case for" of the architecture; a generated base + optional
ArchiMate view set (self-contained SVGs); one traceability chain from
drivers to capabilities/roadmap; honest projection rules where the
pinned notation lacks a native element.

**Non-Goals:** BMM JSON-schema/OKF interop (follow-up); new hooks;
C4/D2 pipeline changes; regime-specific BMM variants; renumbering
existing ARCH sequences.

## Decisions

- **Adoption option A (dedicated command + `BMM` doc-type) as the
  core, with Option B (ArchiMate Motivation/Strategy views) folded
  into the pipeline as Stage 2/3, and a light Option C slice**
  (append-only traceability clauses in `strategy.md` / `sobc.md`).
  Option D (machine-readable metamodel + optional `arckit-bmm`
  overlay plugin) is deferred to a follow-up change.
- **Single-instance, root-level artefact** (like STRAT/SOBC): one
  BMM model per project — `ARC-{P}-BMM-v1.0.md` at the project root.
  `BMM` therefore goes into `DOC_TYPES` only: **not**
  `MULTI_INSTANCE_TYPES`, **not** `SUBDIR_MAP`.
- **BMM 4.0-only elements are stereotyped, never faked as native.**
  `Objective` → `Motivation_Goal(alias, "Objective: …")`;
  `Measure` → `Motivation_Goal(alias, "Measure: …")`;
  `Strategic Theme` → `Strategy_Capability(alias, "Theme: …")` or a
  `group` container — each with a `legend` block, all recorded in
  `references/archimate.md` § BMM Projection with a rendered sample
  fixture (`tests/fixtures/archimate/bmm/`). Task 0 renders the
  spike samples against the pinned jar before any template ships.
- **Relationship vocabulary (BMM → pinned macros):**
  driver / assumption / impact-factor → outcome/goal edges use
  `Rel_Influence`; goal/objective realization of capability or
  business elements uses `Rel_Realization` (concrete → abstract,
  never flipped); capability hierarchy nesting uses `Rel_Composition`
  (whole → part, the BPCM idiom, L1 → L2 → optional L3,
  ≤ 12-element split gate); outcome streams (optional) use
  `Rel_Flow`. "Contributes to" is rendered as a legend-defined edge
  style where no native macro exists.
- **Views sequence into the existing shared `ARCH` sequence space**
  under `projects/{p}/diagrams/` (`ARC-{P}-ARCH-{NNN}-v1.0.md`,
  `--next-num`). BMM views NEVER renumber or rewrite existing ARCH
  documents; multi-instance parity is unaffected (`ARCH` already
  registered).
- **Intake interview (single call, max 2 rounds):** Q1 model scope —
  *Full model (recommended) / Motivation-only / Strategy-only*;
  Q2 diagram menu — *Base views only (recommended) / +goal ladder /
  +case & assumptions overlay / +alignment view / +Mermaid mindmap*
  (multiSelect). Skip rules: arguments that name the scope or menu
  items skip the corresponding question.
- **Quality gates G1–G5 (below) with the 3-iteration remediation
  loop**, matching the archimate command's gate machinery.
- **Static tests, no renderer in CI** (as archimate): pytest asserts
  registry parity, template structure, command frontmatter,
  reference sections, fixture well-formedness, checklist lockstep,
  guide parity.
- **Checklist lockstep:** `BMM` section added to the canonical
  `references/quality-checklist.md` and propagated with
  `scripts/sync-shared-assets.py --check` (all tracked copies,
  incl. the customised OAA copy).

## Artefact Pipeline

The pipeline is the implementable contract for the later
implementation; `tasks.md` phases against it and
`tests/plugin/test_bmm_conformance.py` guards its static shape.

```
INPUTS (context, per the Project Context hook)
  STKE + PRIN            MANDATORY — STOP and point at /arckit:stakeholders
  SOBC, ROAD, WARD, RISK  RECOMMENDED — read if present, note if missing
  external/              OPTIONAL — strategy docs, cited per citation-instructions

STAGE 1 — MODEL
  [A1] ARC-{P}-BMM-v1.0.md (project root; template bmm-template.md)
       sections: 1 Stakeholders & Outcomes (incl. stakeholder–outcome
       matrix table) · 2 Outcomes → Goals → Objectives → Measures
       ladder · 3 Drivers · 4 Assumptions · 5 Case For / Case
       Against · 6 Impact Factors · 7 Strategic Themes →
       Capabilities → Courses of Action → Resources · 8 Traceability
       (links to STKE/SOBC/STRAT/ROAD/BPCM/REQ/ADR + external refs)
       · 9 Mermaid mindmap companion (append-only block) · Document
       Control (14 fields) + generation footer

STAGE 2 — BASE VIEWS (diagrams/, sequenced ARCH docs; always emitted
  unless Q2 selects a motivation/strategy-only scope that omits them)
  [A2] Motivation view      stakeholders → outcomes; driver/constraint
                            influence edges (Rel_Influence)
  [A3] Strategy/Capability view  themes → capability nesting
                            (Rel_Composition, BPCM idiom, optional
                            L3) → courses of action / resources;
                            realization concrete → abstract into
                            Business/Application tiers

STAGE 3 — OPTIONAL COMPANIONS (user-selected at intake; each its own
  sequenced ARCH doc or in-artefact block; spec-only menu, like
  archimate-coverage-expansion)
  [O1] Goal–Objective–Measure ladder view (motivation overlay;
       stereotyped Objective/Measure per § BMM Projection)
  [O2] Case & assumptions overlay (Case For/Against + assumptions +
       impact factors as influence structure; narrative stays in [A1])
  [O3] Alignment/traceability view (Goal/Objective → Strategic
       Theme → Capability (BPCM) → ROAD milestone → REQ → ADR
       realization chain; split at natural boundaries when > 12)
  [O4] Mermaid mindmap companion inside [A1] (GitHub rendering;
       byte-preserving append)
  [D*] Self-contained .svg render of every PlantUML block — pinned
       plantuml-1.2026.8 jar, offline, no non-local URLs; the .svg
       is the only new rendered file

STAGE 4 — HANDOFFS (downstream commands; BMM writes traceability
  clauses, not their artefacts)
  strategy   STRAT consumes Strategic Themes → strategy narrative
  roadmap    ROAD from Courses of Action / Plans
  sobc       5-case ↔ BMM Case section mapping (UK-regime conditional)
  archimate  Motivation overlay on layer views reuses BMM elements

GATES (evaluated before [A1] is written; 3-iteration remediation loop)
  G1 ladder completeness — every goal ≥ 1 objective, every objective
     ≥ 1 measure
  G2 no empty quadrants — Case For, Case Against, Assumptions,
     Impact Factors all populated (placeholder text fails the gate)
  G3 every Strategic Theme realizes ≥ 1 capability (in-model link
     or BPCM cross-reference)
  G4 view conformance — pinned include line, ≤ 12 elements/layer,
     split-never-drop, realization concrete → abstract, legend for
     custom notation, single-tier stereotyping
  G5 ARCH sequence continuity — new views take the next free
     sequence; no renumbering of existing ARCH documents
```

Pipeline invariants (guard-checked): append-only edits to existing
templates/commands/Mermaid blocks (byte-preserved, SHA-256 fixture
extended per the archimate-demanded-artefacts pattern); all new
content additive; `extensions/*` regenerated, never hand-edited.

## Risks / Trade-offs

- **3.x vs 4.0 macro gap** — mitigated by the stereotyped encodings
  + legend + rendered fixture (task 0); if the pinned stdlib cannot
  express a required edge, the fallback is a legend-defined custom
  edge, never a notation mix.
- **Narrative vs diagram fidelity** — BMM's value (the *why*, case
  text, assumption rationale) stays in [A1]; diagrams are
  projections. Stated explicitly in the reference to prevent
  "diagram as spec" misuse.
- **Command count 76 → 77** is a spec-level change: expressed as a
  MODIFIED requirement delta in `slash-commands`, not a silent edit.
- **SOBC coupling** — BMM core stays jurisdiction-neutral; UK
  Green-Book mapping lives on the conditional `sobc` handoff, so
  non-UK projects lose nothing.
- **Optional menu drift** — the 4-item companion menu is spec-only
  (as the existing 8-type ArchiMate menu), guarded by the
  conformance test rather than executed CI.
