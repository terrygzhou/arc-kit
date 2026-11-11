---
description: Map a value stream to IT4IT functional components and key data objects — trigger, stakeholder, stages, KDO flow, systems of record
argument-hint: "<value stream name, e.g. 'Integrate', 'Deploy', 'Consume'>"
effort: medium
handoffs:

  - command: it4it-value-network
    description: Roll this stream's stages into the Value Network view

  - command: it4it-strategy-portfolio
    description: Ground the stream's Evaluate/Explore stages in portfolio functions
---

You are helping an enterprise architect document one **IT4IT Value Stream** using the Open Group IT4IT Standard v3.1 (Snapshot, S261) Ch. 5. Each value stream is a sequence of value-creating activities for a discrete area of the Digital Product lifecycle — trigger, primary stakeholder, scenarios, and a stage sequence that maps onto functional components and key data objects.

## User Input

```text
$ARGUMENTS
```text

## Trigger Guidance

Use this command when **any** of the following conditions are met:

- A value stream needs to be documented: trigger, stakeholder, stage sequence, KDO flow

- A scenario of a value stream needs to be traced end-to-end (e.g. "Deploy a New Product Release Version")

- The participating functional components and key data objects of a stream must be identified

- Cross-stream handoffs (inbound/outbound KDOs) need to be made explicit

**Do NOT use** when:

- The full Value Network view is required instead of one stream → use `/arckit-it4it:it4it-value-network`

- The functional group itself (not a stream) is the subject → use the matching functional-component command (`it4it-strategy-portfolio`, `it4it-develop-test`, `it4it-consume-fulfil`, `it4it-operate-assure`)

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (stop if missing — generate upstream artefact first):

- **PRIN** (Architecture Principles, in 000-global) — Extract: Architecture principles that constrain how the value stream operates
  - If missing: STOP and ask user to run `/arckit:principles` first. The IT4IT value stream must be grounded in architecture principles.

**RECOMMENDED** (read if available, note if missing):

- **ITVN** (IT4IT Value Network) — Extract: position of this stream in the network, cross-stream dependencies

  - If missing: note that the Value Network context is not available

- **ITSF/ITDT/ITCF/ITOA** (functional group artefacts) — Extract: functional components and KDOs relevant to the stream's stages

  - If missing: note that functional-group context is limited

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract value stream definitions, ITIL/TOGAF mappings, existing process catalogs

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

- **First**, check if `.arckit/templates-custom/it4it-value-stream-template.md` exists in the project root

- **If found**: Read the user's customized template (user override takes precedence)

- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/it4it-value-stream-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize it4it-value-stream`

### 3. IT4IT Value Stream Framework

S261 Ch. 5 establishes that each value stream is documented with:

- **Scenario** — the trigger condition and use case
- **Value Stream Stage** — the sequence of activities
- **Stakeholder** — who is responsible and who is affected
- **Participating Data Objects** — which KDOs flow through the stages
- **Participating Functional Components** — which FCs support each stage

The seven value streams:

| # | Value Stream | Trigger | Primary Stakeholder |
|---|---|---|---|
| 1 | **Evaluate** | Portfolio planning cycle | Product Portfolio Manager |
| 2 | **Explore** | Changed Resource Plan | Product Manager |
| 3 | **Integrate** | Work pulled from Product Backlog | Product Manager + Dev Teams |
| 4 | **Deploy** | Approved Product Release | Product Manager |
| 5 | **Publish** | Product Release / Portfolio decision | Catalog Manager |
| 6 | **Consume** | Consumer selects an offering | Consumer |
| 7 | **Operate** | Detected issue / scheduled maintenance | Consumer |

Load `${CLAUDE_PLUGIN_ROOT}/references/value-streams-reference.md` for the full stage sequences and scenarios of all seven streams.

### 4. Shared Schema Definitions

Value stream commands reuse schema definitions:

- **`value-stream.json`** — Value stream definition schema (trigger, stakeholder, stages, KDO flow)

- **`functional-component.json`** — Functional component definition schema (shared with the functional-group commands)

### 5. Generate the Value Stream Document

Create the value stream document following the template structure.

#### Document Control

- Generate Document ID: `ARC-{P}-ITVS-{NNN}-v1.0` (for filename: `ARC-{P}-ITVS-{NNN}-v1.0.md`, where `{NNN}` is the 3-digit sequence number of this instance — use `scripts/bash/generate-document-id.sh` to derive it; `ITVS` is a multi-instance type, one artefact per value stream)

- Set owner, dates, status, classification

#### Trigger and Stakeholder

- **Trigger condition**, frequency, and upstream source
- **Primary stakeholder**, accountable role, contributing roles

#### Stage Sequence

- Numbered stages with participating functional components and KDOs in/out per stage

#### Cross-Stream Dependencies

- Inbound: which upstream stream feeds this one, handoff KDO, contract
- Outbound: which downstream stream consumes the output, handoff KDO, contract

#### Scenarios

- The stream's scenarios, marked covered / not covered in this artefact

#### Conformance Notes

- This artefact **references** S261 (a snapshot, not an approved standard); no conformance claim

### 6. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** pass. Fix any failures before proceeding.

### 7. Write the Document

**IMPORTANT**: The value stream document will be a substantial document (typically 150-250 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-ITVS-{NNN}-v1.0.md
```text

### 8. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## IT4IT Value Stream Document Created

**Document**: `projects/{P}/ARC-{P}-ITVS-{NNN}-v1.0.md`
**Document ID**: ARC-{P}-ITVS-{NNN}.1.0

### Stream Profile
- **Stream**: [name] — [scenario]
- **Trigger**: [trigger condition]
- **Primary stakeholder**: [role]
- **Stages**: [N] stages

### KDO Flow
- [N] KDOs in, [N] KDOs out
- Systems of record: [N] identified

### Shared Schemas
- ✅ value-stream.json → schemas/value-stream.json
- ✅ functional-component.json → schemas/functional-component.json (shared)

### Synthesised From
- [✅/⚠️] Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] IT4IT Value Network: ARC-{P}-ITVN-v[N].md

### Next Steps
1. Map each stage to a functional component (or run the matching functional-group command)
2. Identify systems of record for each KDO
3. Roll the stage sequence into the Value Network view

**File location**: `projects/{P}/ARC-{P}-ITVS-{NNN}-v1.0.md`
```text

## Important Notes

1. **One stream, one artefact**: `ITVS` is a multi-instance doc type — a separate sequence-numbered instance per value stream.
2. **Reference, not conformance**: S261 is a snapshot; cite it as a reference, never claim conformance (see `references/citation-instructions.md`).
3. **Use Write Tool**: The document is typically 150-250 lines. ALWAYS use the Write tool to create it.
4. **Version Management**: If a value stream instance already exists (`ARC-*-ITVS-{NNN}-v*.md` for this stream), create a new version (v2.0) rather than overwriting.
5. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji.
