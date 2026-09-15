# Business Motivation Model Playbook

> **Guide Origin**: Official | **ArcKit Version**: [VERSION]

`/arckit:bmm` generates the project's **Business Motivation Model (BMM 1.3)** — the OMG metamodel behind BIZBOK *Strategy & Stakeholder Alignment* and the ArchiMate Motivation/Strategy tiers — as a single, versioned document: `projects/<id>/ARC-<id>-BMM-v1.0.md`. It answers **why the architecture is being built, for whom, under what case, and how success is measured**, and emits ArchiMate motivation/strategy *views* as **projections** of that model.

---

## Purpose

Stakeholder analyses, business cases, strategies, and roadmaps each re-derive the "case for" from scratch, and their motivation reasoning rarely lines up. A BMM makes the motivation chain **explicit and traceable** — one canonical source that the rest of the strategic artefacts consume instead of re-inventing:

- Articulates **who** is affected (**stakeholders**) and the **outcomes** they need
- Laddering **Outcomes → Goals → Objectives → Measures** so value is verifiable, not asserted
- Documents **drivers**, **assumptions**, and a balanced **Case For / Case Against**
- Maps **Impact Factors** that can invalidate the model
- Connects motivation to delivery via **Strategic Themes → Capabilities → Courses of Action → Resources**

---

## Inputs

| Artifact | Requirement | What It Provides |
|----------|-------------|------------------|
| Stakeholder Analysis (STKE) | **MANDATORY** | Stakeholders, their goals, business drivers |
| Architecture Principles (PRIN) | **MANDATORY** | Constraints and principles that shape the case |
| Strategic Business Case (SOBC) | Recommended | 5-case material feeding Case For / Case Against (UK-regime Green Book) |
| Architecture Roadmap (ROAD) | Recommended | Existing Courses of Action the BMM cross-references |
| Wardley Maps (WARD) | Recommended | Strategic positioning behind the themes |
| Risk Register (RISK) | Recommended | Impact factors that already carry likelihood/impact scores |
| External strategy docs | Optional | Cited in Traceability → External References |

> **Note**: The command STOPS if STKE or PRIN is missing — the model cannot be built without stakeholders and principles.

---

## Command

```bash
/arckit:bmm Build the Business Motivation Model for <initiative-name>
```

Outputs: `projects/<id>/ARC-<id>-BMM-v1.0.md` (project root, **single-instance** — bumped to `v1.1` on regeneration, never sequenced), plus sequenced `diagrams/ARC-<id>-ARCH-NNN-v1.0.md` ArchiMate motivation/strategy views and self-contained `.svg` renders.

---

## Model Structure

| Section | Contents |
|---------|----------|
| **1. Stakeholders & Outcomes** | Stakeholder register + the outcomes each needs, with influence matrix |
| **2. Outcomes → Goals → Objectives → Measures** | The motivation ladder, fully linked end-to-end |
| **3. Drivers** | Internal/external forces pushing the outcomes |
| **4. Assumptions** | What must hold true, and how each is validated |
| **5. Case For / Case Against** | The documented case and its counter-case |
| **6. Impact Factors** | Things that can invalidate the model, with sensitivity |
| **7. Strategic Themes → Capabilities → Courses of Action → Resources** | The delivery chain from strategy to resourcing |
| **8. Traceability** | Links to STKE / SOBC / ROAD / RISK + external references |
| **9. Mermaid Mindmap** | A companion mindmap of the whole motivation chain |

---

## Workflow Position

The BMM sits **upstream** of the strategic artefacts: it is the "case for" that they consume.

```text
┌──────────────┐   ┌──────────────┐
│  STKE        │   │  PRIN        │
│ (mandatory)  │   │ (mandatory)  │
└──────┬───────┘   └──────┬───────┘
       └────────┬──────────┘
                ▼
      ┌────────────────────┐
      │   /arckit:bmm      │  ◀── SOBC / ROAD / WARD / RISK (if present)
      │  motivation model  │
      └────────┬───────────┘
                │  Strategic Themes + Courses of Action
     ┌──────────┼──────────────┬───────────────┐
     ▼          ▼              ▼               ▼
 ┌────────┐ ┌─────────┐  ┌────────────┐  ┌─────────┐
 │ STRAT  │ │  ROAD   │  │    SOBC    │  │  BPCM   │
 └────────┘ └─────────┘  └────────────┘  └─────────┘
```

**Best Practice**: build the BMM **after** stakeholders and principles, and **before** (or alongside) the strategy, roadmap, and business case, so those artefacts stay traceable to one motivation source.

---

## Example Usage

### Motivation-only

```bash
/arckit:bmm Build the Business Motivation Model for NHS Appointment Booking
```

Generates the [A1] model plus the base motivation/strategy ArchiMate views (SVG renders), and stops there.

### Full model with companions

```bash
/arckit:bmm full model with goal ladder, case & assumptions overlay, and a Mermaid mindmap
```

Adds the selected companions (goal-ladder emphasis, case & assumptions overlay, alignment view, Mermaid mindmap) on top of the base model.

---

## Quality Gates

Before the model is written it passes five gates (G1–G5), with a 3-iteration remediation loop:

- **G1 Ladder completeness** — every outcome ≥ 1 goal, every goal ≥ 1 objective, every objective ≥ 1 measure
- **G2 No empty quadrants** — Case For, Case Against, Assumptions, and Impact Factors all populated
- **G3 Theme realization** — every strategic theme realizes ≥ 1 capability
- **G4 View conformance** — pinned ArchiMate include, ≤ 12 elements/layer, concrete→abstract realization, single-tier stereotyping, legend for any custom notation
- **G5 Sequence continuity** — emitted views take the next free `ARCH` number; existing views are never renumbered

---

## Key Differentiators

- **Single-instance, versioned** — one motivation model per project (`v1.0` → `v1.1`), not a sequenced stack
- **Views are projections, not the model** — ArchiMate motivation/strategy views render the model; the [A1] document stays the source of truth
- **Jurisdiction-neutral** — the Green-Book / UK mapping on the `sobc` handoff is *conditional*; the model itself is regime-agnostic

---

## Tips

- Fill the **Case Against** honestly — an empty counter-case fails G2 and usually signals an unexamined assumption.
- Keep **measures** falsifiable; a measure without a baseline and target is an objective in disguise.
- Cross-reference the **Roadmap** instead of re-deriving Courses of Action — BMM links, it never rewrites.

---

## Follow-On Commands

| Command | When | Why |
|---------|------|-----|
| `/arckit:strategy` | After the BMM | Consume BMM Strategic Themes into the strategy narrative |
| `/arckit:roadmap` | After the BMM | Sequence BMM Courses of Action / Plans into a roadmap |
| `/arckit:sobc` | When a UK Green Book case is needed | Map the 5 cases ↔ BMM Case sections (UK-regime, conditional) |
| `/arckit:archimate` | To view a layer | Reuse BMM elements as the Motivation overlay on a layer view |

---

## Output Example

```text
## Business Motivation Model Created

### Model Overview
- 6 stakeholders, 4 outcomes, 9 goals, 12 objectives, 12 measures
- 5 strategic themes, each realizing ≥ 1 capability

### Key Motivation Decisions
- Case For dominates the Economic Case; the "Do Nothing" counter-case is bounded
- Two Impact Factors flagged as model-invalidating at threshold

### Synthesised From
- ARC-001-STKE-v1.0 (mandatory) · ARC-001-PRIN-v1.0 (mandatory) · ARC-001-SOBC-v1.0 (recommended)
```
