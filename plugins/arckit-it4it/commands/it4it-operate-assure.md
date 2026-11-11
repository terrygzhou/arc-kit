---
description: Define the IT4IT Operate & Assure functions (S261 Ch. 9) plus Supporting Functions cross-reference (Ch. 10) — service level, incident/problem, knowledge, monitoring, runbooks
argument-hint: "<product or programme name, e.g. 'Platform Ops', 'Service Operations'>"
effort: high
handoffs:

  - command: it4it-consume-fulfil
    description: Trace service levels and incidents back to service contracts

  - command: it4it-value-stream
    description: Document the Operate value stream (Detect → Diagnose → Resolve)
---

You are helping an enterprise architect create an **IT4IT Operate & Assure** document using the Open Group IT4IT Standard v3.1 (Snapshot, S261) Ch. 9 (Detect to Correct functions), with a cross-reference to the Supporting Functions (Ch. 10). The Support function covers service level management, incident management, problem management, and knowledge management; the Assure function covers configuration management, monitoring, event handling, and diagnostics/remediation with runbooks.

## User Input

```text
$ARGUMENTS
```text

## Trigger Guidance

Use this command when **any** of the following conditions are met:

- The **Support function** (service level, incident, problem, knowledge) needs to be defined against the IT4IT reference

- The **Assure function** (configuration, monitoring, event, diagnostics & remediation) needs formalisation — service monitors, logs, events, runbooks

- The **Operate value stream**'s stages (Detect Issue → Diagnose Issue → Resolve Issue) need mapping to functional components

- Supporting functions (Financial Management, GRC, Workforce Management, Sourcing & Vendor Management, Intelligence & Reporting, Collaboration & Communication) need cross-referencing into the operating model

**Do NOT use** when:

- The consumer/fulfillment side is the subject → use `/arckit-it4it:it4it-consume-fulfil`

- A value stream view is the subject → use `/arckit-it4it:it4it-value-stream`

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (stop if missing — generate upstream artefact first):

- **PRIN** (Architecture Principles, in 000-global) — Extract: Operational principles, service level expectations, incident response principles
  - If missing: STOP and ask user to run `/arckit:principles` first. The IT4IT Operate & Assure artefact must be grounded in architecture principles.

**RECOMMENDED** (read if available, note if missing):

- **ITCF** (IT4IT Consume & Fulfil) — Extract: service contract terms, service offerings in scope

  - If missing: note that the service context is limited

- **ITVN** (IT4IT Value Network) — Extract: position of the Operate stream, feedback loop to Evaluate

  - If missing: note that the Value Network context is not available

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract existing ITIL/VeriSM mappings, SLO definitions, runbook libraries

## Instructions

### 1. Identify or Create Project

Identify the target project from the hook context. If the user specifies a project that doesn't exist yet, create a new project:

1. Use Glob to list `projects/*/` directories and find the highest `NNN-*` number (or start at `001` if none exist)
2. Calculate the next number (zero-padded to 3 digits, e.g., `002`)
3. Slugify the project name (lowercase, replace non-alphanumeric with hyphens, trim)
4. Use the Write tool to create `projects/{NNN}-{slug}/README.md` with the project name, ID, and date
5. Also create `projects/{NNN}-{slug}/external/README.md` with a note to place external reference documents here
6. Set `PROJECT_ID` = the 3-digit number, `PROJECT_PATH` = the new directory path

### 2. Read Template

**Run the intake interview**:

- Run the intake interview per `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md` — derive required inputs from the effective template and MANDATORY prerequisites, prefill from existing sources, put **every** intake question to the user for their input one at a time (each question is optional and may be skipped; a skipped question renders as a `TBD` marker), and persist the answers. A previously saved or prefilled answer never waives the interview — on a re-run, a saved `.arckit/intake/` file only prefills the questions, so every question is still put to the user, one at a time, to confirm, override, or skip. Never collapse the interview into a single batch-confirmation question: each question is its own turn, even when fully prefilled; if no structured question tool is available, ask each question in plain text.

- Load the discovery-dimension checklist `${CLAUDE_PLUGIN_ROOT}/references/intake-discovery-dimensions.md` and use it as the canonical coverage floor in addition to the shared block's §2 template-derived questions: a dimension resolvable from existing artefacts, `.arckit/intake/`, `user_config`, or `shared.json` is surfaced prefilled for confirmation/override (ask-always, answer-optional); a dimension with no source is asked as a grouped, skippable question (a skipped question renders a `TBD` marker); the checklist adds no diagram or output mandate.

**Read the template** (with user override support):

- **First**, check if `.arckit/templates-custom/it4it-operate-assure-template.md` exists in the project root

- **If found**: Read the user's customized template (user override takes precedence)

- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/it4it-operate-assure-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize it4it-operate-assure`

### 3. IT4IT Operate & Assure Framework

S261 Ch. 9 defines the Detect to Correct functions:

| Function | Components | Primary Data Objects |
|---|---|---|
| **Support** | Service Level · Incident · Problem · Knowledge | Service Contract · KPI · Incident · Problem · Knowledge Item |
| **Assure** | Configuration · Monitoring · Event · Diagnostics & Remediation | Actual Product Instance · Service Monitor · Log · Event · Runbook |

The **Support** function covers service level management, incident management, problem management, and knowledge management. The **Assure** function covers configuration management, monitoring, event handling, and diagnostics/remediation with runbooks.

The Operate value stream's stages map onto these components: Detect Issue (Monitoring, Event) → Diagnose Issue (Diagnostics & Remediation, Problem, Knowledge) → Resolve Issue (Runbook, Incident, Change).

**Supporting Functions cross-reference (S261 Ch. 10)**:

| Function | Description |
|---|---|
| **Financial Management** | Cost Modeling (Cost Model) · Investment (Budget Item) |
| **Governance, Risk, & Compliance** | GRC across all value streams |
| **Workforce Management** | Capacity planning for people |
| **Sourcing & Vendor Management** | Vendor lifecycle, procurement |
| **Intelligence & Reporting** | Analytics, dashboards, service reporting |
| **Collaboration & Communication** | Stakeholder communication, service status publishing |

Load `${CLAUDE_PLUGIN_ROOT}/references/functional-components-reference.md` for the full component and KDO catalog.

### 4. Shared Schema Definitions

Operate & Assure commands reuse schema definitions:

- **`functional-component.json`** — Functional component definition schema (components, KDOs, cardinalities, systems of record)

### 5. Generate the Operate & Assure Document

Create the document following the template structure.

#### Document Control

- Generate Document ID: `ARC-{P}-ITOA-v1.0` (for filename: `ARC-{P}-ITOA-v1.0.md`)

- Set owner, dates, status, classification

#### Support Function

- Service level management: KPIs against the Service Contract, SLO definitions
- Incident and problem management: lifecycle, prioritisation, knowledge capture
- Knowledge management: knowledge items, runbook linkage

#### Assure Function

- Configuration management: actual product instance inventory
- Monitoring: service monitors, logs, events
- Diagnostics & remediation: runbooks, automated remediation boundaries

#### Supporting Functions Cross-Reference

- Which Supporting Functions apply, and how they attach to this operating model

#### Cardinalities and Systems of Record

- KDO cardinalities per the S261 catalog; the system of record for each KDO

#### Conformance Notes

- This artefact **references** S261 (a snapshot, not an approved standard); no conformance claim

### 6. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** pass. Fix any failures before proceeding.

### 7. Write the Document

**IMPORTANT**: The Operate & Assure document will be a substantial document (typically 200-300 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-ITOA-v1.0.md
```text

### 8. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## IT4IT Operate & Assure Document Created

**Document**: `projects/{P}/ARC-{P}-ITOA-v1.0.md`
**Document ID**: ARC-{P}-ITOA-v1.0

### Support Function
- **KPIs / SLOs**: [N] against Service Contract
- **Incident/problem lifecycle**: [states]

### Assure Function
- **Service monitors**: [N] — runbooks: [N]
- **Automated remediation boundaries**: [summary]

### Supporting Functions
- **In scope**: [list]

### Synthesised From
- [✅/⚠️] Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] IT4IT Consume & Fulfil: ARC-{P}-ITCF-v[N].md
- [✅/⚠️] IT4IT Value Network: ARC-{P}-ITVN-v[N].md

### Next Steps
1. Document the Operate stream end-to-end: `/arckit-it4it:it4it-value-stream Operate`
2. Trace KPIs back to service contract terms: `/arckit-it4it:it4it-consume-fulfil`

**File location**: `projects/{P}/ARC-{P}-ITOA-v1.0.md`
```text

## Important Notes

1. **Feedback loop**: The Operate stream feeds back to Evaluate — operational findings become portfolio inputs. Record the handoff.
2. **Runbooks are first-class KDOs**: Diagnostics & Remediation is runbook-driven; the runbook library is part of the reference architecture, not a tooling detail.
3. **Reference, not conformance**: S261 is a snapshot; cite it as a reference, never claim conformance (see `references/citation-instructions.md`).
4. **Use Write Tool**: The document is typically 200-300 lines. ALWAYS use the Write tool to create it.
5. **Version Management**: If an Operate & Assure document already exists (`ARC-*-ITOA-v*.md`), create a new version (v2.0) rather than overwriting.
6. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji.
