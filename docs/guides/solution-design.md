# Solution Design Guide

> **Guide Origin**: Official | **ArcKit Version**: [VERSION]

`/arckit:solution-design` generates a governed UML 2.5.1 solution design document — a single `SOLN` artefact combining narrative design rationale with six embedded PlantUML diagram views.

---

## What It Produces

A single document at `projects/<NNN>/ARC-<NNN>-SOLN-v1.0.md` (multi-instance sequence on re-runs, e.g. `ARC-001-SOLN-v2.0.md`), containing:

- A narrative **Design Rationale** section consistent with existing ADRs
- A **Requirements Traceability** table mapping BR/FR/NFR/INT/DR entries to design elements
- Six embedded PlantUML diagram sections, one per UML 2.5.1 diagram type:

| Section | Diagram | Answers |
|---------|---------|---------|
| Use Case | Actors and use cases | What the system does for whom |
| Sequence | Interaction flow | How key scenarios play out over time |
| Component | Component boundaries and dependencies | What the solution is made of |
| Deployment | Infrastructure topology | Where it runs |
| Class | Domain model | What the core entities are |
| Object | Runtime instances | What it looks like at a point in time |

Each section carries a "View this diagram" callout with at least three rendering options (ArcKit Pages, VS Code PlantUML extension, PlantUML CLI).

---

## Inputs

| Artefact | Purpose |
|----------|---------|
| `ARC-<NNN>-REQ-v*.md` (mandatory) | BR/FR/NFR/INT/DR entries drive every diagram section |
| `ARC-<NNN>-DATA-*.md` (recommended) | Entities and relationships populate the Class diagram |
| `decisions/ARC-*-ADR-*.md` (recommended) | Recorded decisions; Design Rationale must stay consistent |
| `STKE`, `PRIN`, `SOBC`, `RSCH` (optional) | Actors, technology standards, scope bounds, build-vs-buy |
| Vendor HLD/DLD, reference architectures in `external/` | Component and deployment choices, with citation markers |

If the requirements artefact is missing, the command stops and suggests running `/arckit:requirements` first — a solution design with no requirements has no traceability basis.

---

## Command

```bash
/arckit:solution-design Create solution design for <project name or ID>
```

Pass a comma-separated diagram subset to skip the interactive selection:

```bash
/arckit:solution-design 001 sequence,class
```

---

## How to Use It

The command walks through one interactive configuration step when no subset is passed in the arguments:

1. **Diagram subset** (multi-select, default: all six) — choose which of the six diagram sections to populate this run. The document skeleton is always generated in full; unselected sections remain as placeholders so a later re-run can fill them in without regenerating the populated ones.
2. **PlantUML style** (single-select, default) — how detailed the diagram blocks should be.

### PlantUML-Only Notation

All six views use PlantUML fenced code blocks. Mermaid is **not** offered as an alternative: Mermaid has no object-diagram grammar and no first-class UML use-case or component references, so a subset of the six views could not be expressed at all. If you ask for Mermaid, the command notes the limitation and proceeds with PlantUML.

---

## Document ID Convention

`ARC-NNN-SOLN-v1.0.md` — multi-instance: a second generation writes `ARC-NNN-SOLN-v2.0.md` and carries forward the Document Control history; an approved artefact is never overwritten in place.

---

## Handoffs

| Next Step | When |
|-----------|------|
| `/arckit:hld-review` | Validate component and deployment choices against the HLD |
| `/arckit:dld-review` | Validate class and sequence design against the DLD |
| `/arckit:traceability` | Map design decisions back to requirements |
| `/arckit:sow` | Include solution design scope in an RFP / statement of work |
| `/arckit:diagram` | Generate companion standalone DIAG artefacts for individual diagrams |

---

## Tips

- Re-run whenever requirements or ADRs change materially — the Class diagram tracks the data model, and Design Rationale must stay consistent with recorded decisions.
- Keep the Object diagram to one or two representative runtime scenarios with concrete instance values; the full model belongs in the Class diagram.
- Embed the SOLN views in HLD/DLD reviews so component, sequence, and class discussions share one governed source of truth.
