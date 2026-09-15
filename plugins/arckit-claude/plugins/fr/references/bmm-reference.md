# BMM (Business Motivation Model) Reference

ArcKit's BMM command (`/arckit:bmm`, doc-type `BMM`) models the **OMG
Business Motivation Model (BMM 1.3)** —
[OMG spec BMM 1.3](https://www.omg.org/spec/BMM/1.3/PDF) — the
metamodel behind BIZBOK's *Strategy & Stakeholder Alignment* and
ArchiMate's Motivation/Strategy tiers. One BMM model per project:
`ARC-NNN-BMM-v1.0.md` at the project root, single-instance, versioned
by `-vN.N`.

BMM answers the question the rest of the toolkit assumes: **why is
this architecture being built, for whom, under what case, and how is
success measured?** It is the upstream "case for" that STKE, SOBC,
STRAT, ROAD, and BPCM artefacts otherwise re-derive locally.

## When to use

- Before `/arckit:strategy` when the project has no recorded case for
  the change (drivers, outcomes, goals).
- When stakeholders disagree about *what* the organisation wants to
  achieve (stakeholder–outcome matrix exposes conflicts).
- When an investment decision needs a documented Case For / Case
  Against with Assumptions and Impact Factors made explicit.

## BMM 1.3 element catalogue

| Element | Kind | Attributes / notes |
| --- | --- | --- |
| **Stakeholder** | element | inherent or desired; an entity (organisation or individual) to which an outcome matters |
| **Outcome** | element | the desired state of affairs for a stakeholder; a goal *realizes* an outcome |
| **Goal** | element | a desired outcome in an idealised state; abstract; realized by objectives/capabilities |
| **Objective** | element | a specific, measurable, time-bound goal; 4.0-only in ArchiMate (no pinned macro — see § Projection) |
| **Measure** | element | quantifies progress toward a goal or objective; 4.0-only (stereotyped in views) |
| **Driver** | element | inherent / desired / imposed; an internal or external force pushing toward an outcome |
| **Assumption** | element | a belief accepted without proof that the case relies on; must be listed, never implicit |
| **Case For** | element | the documented set of reasons supporting the strategic option |
| **Case Against** | element | the documented counter-case; an empty counter-case fails gate G2 |
| **Impact Factor** | element | an element that influences the strength of the case for or against (risk, cost, regulatory shift, …) |
| **Strategic Theme** | element | a named, high-priority strategic direction; instrument of a strategic goal; groups capabilities; 4.0-only (stereotyped) |
| **Capability** | element | an organisational ability; realized by business/application elements; the bridge to BPCM |
| **Strategy / Course of Action** | element | the concrete actions (plans, programmes) that realise a strategic theme |
| **Resource** | element | an asset assigned to a strategy or course of action |

### Relationships (BMM 1.3 vocabulary)

| Relationship | Meaning | Pinned PlantUML ArchiMate macro |
| --- | --- | --- |
| *instruments* | stakeholder → outcome | `Rel_Influence` (labelled "expects" / "values") |
| *realizes* | goal → outcome; capability → process; objective → goal (concrete → abstract) | `Rel_Realization` |
| *contributes to* | capability/goal → outcome | `Rel_Influence` or legend-defined edge (no native macro) |
| *influences* | driver / assumption / impact factor → goal/outcome | `Rel_Influence` |
| *enables / constrains* | driver / resource / constraint → goal, strategy | `Rel_Influence` (labelled "enables" / "constrains") |
| *contains / part of* | strategic theme / capability domain → sub-capability (whole → part) | `Rel_Composition` (default) / `Rel_Aggregation` |
| *measures* | measure → goal / objective | `Rel_Realization` (labelled "measures") |
| *assigned to* | resource → course of action | `Rel_Assignment` |

## BMM ↔ ArchiMate ↔ ArcKit mapping

| BMM element | ArchiMate tier / pinned macro | ArcKit home |
| --- | --- | --- |
| Stakeholder | Motivation / `Motivation_Stakeholder` | STKE (stakeholders.md) + BMM § 1 |
| Outcome | Motivation / `Motivation_Outcome` | BMM § 1–2 |
| Goal | Motivation / `Motivation_Goal` | BMM § 2 |
| Objective | Motivation / *stereotyped* `Motivation_Goal("Objective: …")` | BMM § 2 |
| Measure | Motivation / *stereotyped* `Motivation_Goal("Measure: …")` | BMM § 2 |
| Driver | Motivation / `Motivation_Driver` | BMM § 3; ADM `discovery` drivers |
| Assumption | no 3.x macro (narrative; `Rel_Influence` in [O2]) | BMM § 4 |
| Case For / Case Against | narrative (no ArchiMate element; [O2] overlay groups) | BMM § 5; SOBC 5-case (UK) |
| Impact Factor | no 3.x macro (`Rel_Influence` in [O2]) | BMM § 6 |
| Strategic Theme | Strategy / *stereotyped* `Strategy_Capability("Theme: …")` or `group` | BMM § 7; OAA agile-strategy |
| Capability | Strategy / `Strategy_Capability` | BPCM capability map |
| Strategy / Course of Action | Strategy / `Strategy_CourseOfAction` | BMM § 7; ROAD |
| Resource | Strategy / `Strategy_Resource` | BMM § 7 |
| Stakeholder–Outcome matrix | table (not a diagram) | BMM § 1 |

## Alignment notes

- **BIZBOK *Strategy & Stakeholder Alignment*** is BMM operationalised
  as a practice: stakeholder → outcome → goal → objective → measure,
  then strategic themes → capabilities → strategies. The BMM
  artefact's section order follows that chain.
- **UK Green Book 5-case (SOBC):** the *Strategic Case* ↔ BMM § 1–3
  (stakeholders, outcomes, drivers); *Economic Case* ↔ Case For
  (benefits) + Measures; *options appraisal* ↔ Case For / Case
  Against; *risk assessment* ↔ Impact Factors. BMM stays
  jurisdiction-neutral; the mapping lives on the conditional `sobc`
  handoff.
- **TOGAF ADM:** BMM is the business-motivation input to Phase A
  (architecture vision / stakeholder management) and Phase B (business
  architecture ↔ capabilities). BPCM sits downstream.

## Artefact pipeline

Stages (details in `openspec/changes/bmm-adoption/design.md` §
Artefact Pipeline; implemented by `commands/bmm.md`):

1. **Inputs** — STKE + PRIN mandatory (stop-and-ask if missing);
   SOBC/ROAD/WARD/RISK recommended; `external/` strategy docs cited
   per `citation-instructions.md`.
2. **[A1] Model** — `ARC-{P}-BMM-v1.0.md` (root), sections:
   1 Stakeholders & Outcomes (+ matrix) · 2 Outcomes → Goals →
   Objectives → Measures · 3 Drivers · 4 Assumptions · 5 Case For /
   Case Against · 6 Impact Factors · 7 Strategic Themes →
   Capabilities → Courses of Action → Resources · 8 Traceability +
   external references · 9 Mermaid mindmap companion.
3. **[A2] Motivation view** + **[A3] Strategy/Capability view** —
   sequenced `diagrams/ARC-{P}-ARCH-{NNN}-v1.0.md`, PlantUML
   ArchiMate (pinned include, self-contained `.svg` render).
4. **Companions** (intake-selected): [O1] goal–objective–measure
   ladder · [O2] case & assumptions overlay · [O3] alignment /
   traceability view · [O4] Mermaid mindmap sidecar.
5. **Handoffs** — `strategy`, `roadmap`, `sobc` (UK), `archimate`.

## Intake interview

One structured-question call, max 2 rounds:

- **Q1 — Scope** (single): *Full model* (recommended) /
  Motivation-only / Strategy-only. A scope that omits a tier omits
  the corresponding base view ([A2]/[A3]).
- **Q2 — Diagram menu** (multiSelect): *Base views only*
  (recommended) / +goal ladder [O1] / +case & assumptions overlay
  [O2] / +alignment view [O3] / +Mermaid mindmap [O4].

Skip a question when the arguments already name the scope or menu
items.

## Quality gates (G1–G5)

Evaluated before [A1] is written; 3-iteration remediation loop, with
accepted trade-offs documented in the artefact after the loop:

- **G1 — Ladder completeness.** Every outcome has ≥ 1 goal; every
  goal ≥ 1 objective; every objective ≥ 1 measure. A goal without an
  objective (or an objective without a measure) fails the gate.
- **G2 — No empty quadrants.** Case For, Case Against, Assumptions,
  and Impact Factors are all populated with content; placeholder text
  ("TBC", "—", empty bullets) fails the gate.
- **G3 — Theme realization.** Every strategic theme realizes ≥ 1
  capability (in-model link or BPCM cross-reference).
- **G4 — View conformance.** Pinned include line; ≤ 12 elements per
  layer; split-never-drop; realization concrete → abstract; single
  tier stereotyping; legend for any custom notation (stereotypes,
  legend-defined edges).
- **G5 — Sequence continuity.** BMM-emitted views take the next free
  number in the shared `ARCH` sequence; existing `ARCH` documents are
  never renumbered or rewritten.

## Notation projection (views)

The pinned PlantUML ArchiMate stdlib (3.x-flavoured, PlantUML
1.2026.8) has **no native macros** for BMM's 4.0-aligned elements.
Encodings (documented in `skills/plantuml-syntax/references/
archimate.md` § BMM Projection, fixture
`tests/fixtures/archimate/bmm/`):

| BMM element | Encoding |
| --- | --- |
| Objective | `Motivation_Goal(alias, "Objective: …")` |
| Measure | `Motivation_Goal(alias, "Measure: …")` |
| Strategic Theme | `Strategy_Capability(alias, "Theme: …")` or a `group` container |
| Contributes to | `Rel_Influence` or legend-defined edge |

Full BMM fidelity (case narrative, assumption rationale, impact-factor
analysis) lives in the [A1] artefact; views are **projections** of
it — a diagram never substitutes for the model.
