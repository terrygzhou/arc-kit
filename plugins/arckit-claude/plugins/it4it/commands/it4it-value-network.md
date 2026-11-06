---
description: Establish the IT4IT Value Network — all seven value streams, their triggers, stakeholders, and cross-stream dependencies
argument-hint: "<product or programme name, e.g. 'Observability Stack', 'IT Portfolio'>"
effort: high
handoffs:

  - command: it4it-value-stream
    description: Drill into a single value stream (multi-instance)

  - command: it4it-strategy-portfolio
    description: Ground the Evaluate/Explore streams in portfolio functions
---

You are helping an enterprise architect create an **IT4IT Value Network** document using the Open Group IT4IT Standard v3.1 (Snapshot, S261) Ch. 5. The Value Network is the evolution of Porter's Value Chain in the IT4IT reference architecture: each value-creating activity is both consuming and value-producing to potentially many other activities simultaneously. It maps all seven value streams, their cross-stream dependencies, and the Digital Product at the centre.

## User Input

```text
$ARGUMENTS
```text

## Trigger Guidance

Use this command when **any** of the following conditions are met:

- The full **Value Network view** of an IT product portfolio or programme is required

- Cross-stream dependencies (which stream feeds which, and which KDOs are handed off) need to be made explicit

- The Digital Product backbone (Digital Product, Service Offering, System, Digital Product Contract) needs to be positioned relative to the seven streams

- An IT/ITSM target state is being defined and the Open Group reference is required

**Do NOT use** when:

- A single value stream is the subject → use `/arckit-it4it:it4it-value-stream`

- A functional group (Strategy to Portfolio, Develop & Test, Consume & Fulfil, Operate & Assure) is the subject → use the matching functional-group command

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (stop if missing — generate upstream artefact first):

- **PRIN** (Architecture Principles, in 000-global) — Extract: Governance principles, decision authority, product-vs-project investment posture
  - If missing: STOP and ask user to run `/arckit:principles` first. The IT4IT Value Network must be grounded in architecture principles.

**RECOMMENDED** (read if available, note if missing):

- **ITSF/ITDT/ITCF/ITOA** (functional group artefacts) — Extract: functional components and KDOs that participate in the streams

  - If missing: note that functional-group context is limited

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract existing ITSM frameworks, ITIL/VeriSM mappings, product portfolio definitions

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

- **First**, check if `.arckit/templates-custom/it4it-value-network-template.md` exists in the project root

- **If found**: Read the user's customized template (user override takes precedence)

- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/it4it-value-network-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize it4it-value-network`

### 3. IT4IT Value Network Framework

S261 Ch. 5 establishes the seven value streams and their integration:

| # | Value Stream | Trigger | Primary Stakeholder | Stages |
|---|---|---|---|---|
| 1 | **Evaluate** | Portfolio planning cycle | Product Portfolio Manager | Gather Influencers → Identify Gaps → Propose Investments → Define Backlog Mandates → Ensure Governance |
| 2 | **Explore** | Changed Resource Plan | Product Manager | Prioritize Backlog Items → Define Digital Product Architecture → Refine Product Backlog → Finalize Roadmap & Resource Plan |
| 3 | **Integrate** | Work pulled from Product Backlog | Product Manager + Dev Teams | Plan Product Release → Design & Develop → Build, Integrate, & Test → Accept & Publish Release |
| 4 | **Deploy** | Approved Product Release | Product Manager | Plan & Approve Deployment → Fulfill Deployment → Validate Deployment → Observe Deployment |
| 5 | **Publish** | Product Release / Portfolio decision | Catalog Manager | Define Service Offering → Implement Service Offering → Publish Service Offering |
| 6 | **Consume** | Consumer selects an offering | Consumer | Select an Offering → Agree to Service Offering → Subscribe → Provide Service Support → Publish Service Status |
| 7 | **Operate** | Detected issue / scheduled maintenance | Consumer | Detect Issue → Diagnose Issue → Resolve Issue |

**Cross-stream dependencies** (S261 Ch. 5):

- **Evaluate** ← all streams feed ideas, improvements, and demand into it
- **Explore** depends on Evaluate (qualified Portfolio Backlog Items); if the Resource Plan cannot be met, Explore changes it
- **Integrate** pulls work from the Product Backlog; also handles emergency changes / hotfixes
- **Deploy** depends on Integrate (approved releases); used by Evaluate, Publish, Operate
- **Publish** depends on Deploy (deployed releases); feeds Consume
- **Consume** depends on Publish (catalog); responsible for creating/updating the Service Contract
- **Operate** depends on Consume (Service Contract terms); feeds back to Evaluate

The **Digital Product** is the anchor entity: a bundle of Systems, Service Offerings, and Digital Product Contracts that delivers value to a consumer. The Digital Product Backbone (Digital Product, Digital Product Contract, Service Offering, System) and the Service Offering Backbone (Service Offering, Order, Subscription) are the two KDO backbones.

Load `${CLAUDE_PLUGIN_ROOT}/references/value-streams-reference.md` for the full scenario catalog and `${CLAUDE_PLUGIN_ROOT}/references/functional-components-reference.md` for the functional group mappings.

### 4. Shared Schema Definitions

Value network commands reuse schema definitions:

- **`value-stream.json`** — Value stream definition schema (per-stream trigger, stakeholder, stages, KDO flow)

- **`functional-component.json`** — Functional component definition schema (shared with the functional-group commands)

### 5. Generate the Value Network Document

Create the Value Network document following the template structure.

#### Document Control

- Generate Document ID: `ARC-{P}-ITVN-v1.0` (for filename: `ARC-{P}-ITVN-v1.0.md`)

- Set owner, dates, status, classification

#### Stream Map

- All seven streams with trigger, primary stakeholder, and stage sequence

#### Cross-Stream Dependency Map

- Every inbound/outbound handoff: source stream, target stream, handoff KDO, contract (cardinality + system-of-record obligation)

#### Digital Product Positioning

- Digital Product Backbone and Service Offering Backbone KDOs, positioned per stream

#### Scenarios in Scope

- The scenarios (from the S261 catalog) that this network view covers

#### Conformance Notes

- This artefact **references** S261 (a snapshot, not an approved standard); no conformance claim

### 6. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** pass. Fix any failures before proceeding.

### 7. Write the Document

**IMPORTANT**: The Value Network document will be a substantial document (typically 200-350 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-ITVN-v1.0.md
```text

### 8. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## IT4IT Value Network Document Created

**Document**: `projects/{P}/ARC-{P}-ITVN-v1.0.md`
**Document ID**: ARC-{P}-ITVN-v1.0

### Stream Coverage
- **Streams mapped**: 7 of 7
- **Cross-stream dependencies**: [N] handoffs identified
- **Scenarios in scope**: [N]

### Digital Product Positioning
- **Digital Product Backbone KDOs**: [N]
- **Service Offering Backbone KDOs**: [N]

### Shared Schemas
- ✅ value-stream.json → schemas/value-stream.json
- ✅ functional-component.json → schemas/functional-component.json (shared)

### Synthesised From
- [✅/⚠️] Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] Functional group artefacts: ARC-{P}-ITSF/ITDT/ITCF/ITOA-v[N].md

### Next Steps
1. Drill into a single value stream: `/arckit-it4it:it4it-value-stream <stream>`
2. Ground the Evaluate/Explore streams: `/arckit-it4it:it4it-strategy-portfolio`
3. Identify systems of record for each handoff KDO

**File location**: `projects/{P}/ARC-{P}-ITVN-v1.0.md`
```text

## Important Notes

1. **Value Network vs Value Stream**: The network is the single-integration view (one `ITVN` artefact); individual streams are multi-instance `ITVS` artefacts.
2. **Reference, not conformance**: S261 is a snapshot; cite it as a reference, never claim conformance (see `references/citation-instructions.md`).
3. **Product-based, not project-based**: The Value Network treats Portfolio Backlog Items (not projects) as the unit of funding. Where existing practices are project-based, flag the gap.
4. **Use Write Tool**: The document is typically 200-350 lines. ALWAYS use the Write tool to create it.
5. **Version Management**: If a Value Network document already exists (`ARC-*-ITVN-v*.md`), create a new version (v2.0) rather than overwriting.
6. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji.
