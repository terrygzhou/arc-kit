---
description: Define the IT4IT Consume & Fulfil functions (S261 Ch. 8) — offering catalog, order, subscription, chargeback, fulfillment orchestration, and usage
argument-hint: "<product or programme name, e.g. 'Service Catalog', 'Billing Platform'>"
effort: high
handoffs:

  - command: it4it-operate-assure
    description: Connect fulfilment to service-level and incident handling

  - command: it4it-develop-test
    description: Trace fulfilled offerings back to product releases
---

You are helping an enterprise architect create an **IT4IT Consume & Fulfil** document using the Open Group IT4IT Standard v3.1 (Snapshot, S261) Ch. 8 (Request to Fulfill functions). The Consume function manages the consumer lifecycle — selection, agreement, subscription, support, status. The Fulfill function manages the operational side: change management, resource provisioning, fulfillment orchestration, and usage tracking.

## User Input

```text
$ARGUMENTS
```text

## Trigger Guidance

Use this command when **any** of the following conditions are met:

- The **service offering catalog** and consumer lifecycle (Select → Agree → Subscribe → Support → Status) need to be defined against the IT4IT reference

- The **fulfillment** side — change management, resource provisioning, fulfillment orchestration, usage records — needs formalisation

- The **Service Offering Backbone** (Service Offering, Order, Subscription) needs to be positioned with its systems of record

- Chargeback (contracts and records) needs to be part of the consumer model

**Do NOT use** when:

- The operational service level / incident / monitoring side is the subject → use `/arckit-it4it:it4it-operate-assure`

- A value stream view is the subject → use `/arckit-it4it:it4it-value-stream`

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (stop if missing — generate upstream artefact first):

- **PRIN** (Architecture Principles, in 000-global) — Extract: Consumer-experience principles, service contract principles, billing/chargeback policy
  - If missing: STOP and ask user to run `/arckit:principles` first. The IT4IT Consume & Fulfil artefact must be grounded in architecture principles.

**RECOMMENDED** (read if available, note if missing):

- **ITDT** (IT4IT Develop & Test) — Extract: product releases and blueprints feeding the offering catalog

  - If missing: note that the release context is limited

- **ITVN** (IT4IT Value Network) — Extract: position of the Publish/Consume streams, cross-stream dependencies

  - If missing: note that the Value Network context is not available

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract existing service catalog, billing, and SLA documents

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

- **First**, check if `.arckit/templates-custom/it4it-consume-fulfil-template.md` exists in the project root

- **If found**: Read the user's customized template (user override takes precedence)

- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/it4it-consume-fulfil-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize it4it-consume-fulfil`

### 3. IT4IT Consume & Fulfil Framework

S261 Ch. 8 defines the Request to Fulfill functions:

| Function | Components | Primary Data Objects |
|---|---|---|
| **Consume** | Consumption Experience · Identity · Offering · Order · Chargeback | Interaction · Identity · Entitlement · Service Offering Catalog · Service Offering · Order · Subscription · Chargeback Contract · Chargeback Record |
| **Fulfill** | Change · Fulfillment Orchestration · Resource · Fulfillment · Usage | Change · Desired Product Instance · Resource · Capacity Plan · Fulfillment Book · Usage Record |

The **Consume** function manages the consumer lifecycle: selection → agreement → subscription → support → status. The **Fulfill** function manages the operational side: change management, resource provisioning, fulfillment orchestration, usage tracking.

The Publish value stream's stages (Define Service Offering → Implement Service Offering → Publish Service Offering) and the Consume stream's stages (Select an Offering → Agree to Service Offering → Subscribe → Provide Service Support → Publish Service Status) map onto these components. The Consume function is responsible for creating and updating the **Service Contract** (Digital Product Contract).

Load `${CLAUDE_PLUGIN_ROOT}/references/functional-components-reference.md` for the full component and KDO catalog.

### 4. Shared Schema Definitions

Consume & Fulfil commands reuse schema definitions:

- **`functional-component.json`** — Functional component definition schema (components, KDOs, cardinalities, systems of record)

### 5. Generate the Consume & Fulfil Document

Create the document following the template structure.

#### Document Control

- Generate Document ID: `ARC-{P}-ITCF-v1.0` (for filename: `ARC-{P}-ITCF-v1.0.md`)

- Set owner, dates, status, classification

#### Consume Function

- Consumption experience, identity and entitlement model, service offering catalog structure
- Order and subscription lifecycle, chargeback contract and chargeback record model

#### Fulfill Function

- Change management, resource provisioning, fulfillment orchestration, fulfillment book, usage tracking

#### Service Contract

- How the Service Contract (Digital Product Contract) is created, updated, and enforced

#### Cardinalities and Systems of Record

- KDO cardinalities per the S261 catalog; the system of record for each KDO

#### Conformance Notes

- This artefact **references** S261 (a snapshot, not an approved standard); no conformance claim

### 6. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** pass. Fix any failures before proceeding.

### 7. Write the Document

**IMPORTANT**: The Consume & Fulfil document will be a substantial document (typically 200-300 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-ITCF-v1.0.md
```text

### 8. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## IT4IT Consume & Fulfil Document Created

**Document**: `projects/{P}/ARC-{P}-ITCF-v1.0.md`
**Document ID**: ARC-{P}-ITCF-v1.0

### Consume Function
- **Service offerings in catalog**: [N]
- **Order/subscription lifecycle**: [states]
- **Chargeback model**: [summary]

### Fulfill Function
- **Fulfillment orchestration**: [approach]
- **Usage tracking**: [approach]

### Synthesised From
- [✅/⚠️] Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] IT4IT Develop & Test: ARC-{P}-ITDT-v[N].md
- [✅/⚠️] IT4IT Value Network: ARC-{P}-ITVN-v[N].md

### Next Steps
1. Connect fulfilment to service level and incidents: `/arckit-it4it:it4it-operate-assure`
2. Trace offerings back to product releases: `/arckit-it4it:it4it-develop-test`

**File location**: `projects/{P}/ARC-{P}-ITCF-v1.0.md`
```text

## Important Notes

1. **Service Offering Backbone**: Service Offering, Order, and Subscription form one of the two KDO backbones; their systems of record must be unambiguous.
2. **Service Contract ownership**: The Consume function creates and updates the Service Contract (Digital Product Contract) — not the consumer.
3. **Reference, not conformance**: S261 is a snapshot; cite it as a reference, never claim conformance (see `references/citation-instructions.md`).
4. **Use Write Tool**: The document is typically 200-300 lines. ALWAYS use the Write tool to create it.
5. **Version Management**: If a Consume & Fulfil document already exists (`ARC-*-ITCF-v*.md`), create a new version (v2.0) rather than overwriting.
6. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji.
