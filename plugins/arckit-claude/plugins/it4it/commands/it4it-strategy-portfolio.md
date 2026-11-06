---
description: Define the IT4IT Strategy to Portfolio functions (S261 Ch. 6) — policy, strategy, portfolio backlog, and proposal components with their key data objects
argument-hint: "<product or programme name, e.g. 'IT Portfolio', 'Digital Products Portfolio'>"
effort: high
handoffs:

  - command: it4it-develop-test
    description: Trace portfolio backlog items into the Develop function

  - command: it4it-value-stream
    description: Document the Evaluate or Explore value stream this function supports
---

You are helping an enterprise architect create an **IT4IT Strategy to Portfolio** document using the Open Group IT4IT Standard v3.1 (Snapshot, S261) Ch. 6. The Strategy to Portfolio function replaces project-based IT investment with product-based investment: the Digital Product is the business description at the heart of the function, and Portfolio Backlog Items (not projects) are the unit of funding.

## User Input

```text
$ARGUMENTS
```text

## Trigger Guidance

Use this command when **any** of the following conditions are met:

- The **policy framework** governing digital products needs to be defined (creation, review, approval, audit)

- **Portfolio strategy** (strategic themes, strategic objectives) must be aligned with business/enterprise strategy

- The **portfolio backlog** — lifecycle and visibility of Portfolio Backlog Items — needs formalisation

- **Resource plans** (funding packages over backlog items) need to be defined, with proposal states (proposed, approved, active, deferred, rejected)

**Do NOT use** when:

- The value stream view (Evaluate/Explore) is the subject instead of the functions → use `/arckit-it4it:it4it-value-stream`

- The Develop/Test functions are the subject → use `/arckit-it4it:it4it-develop-test`

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (stop if missing — generate upstream artefact first):

- **PRIN** (Architecture Principles, in 000-global) — Extract: Governance principles, decision authority, product-vs-project investment posture
  - If missing: STOP and ask user to run `/arckit:principles` first. The IT4IT Strategy to Portfolio artefact must be grounded in architecture principles.

**RECOMMENDED** (read if available, note if missing):

- **ITVN** (IT4IT Value Network) — Extract: position of Evaluate/Explore in the network, cross-stream dependencies

  - If missing: note that the Value Network context is not available

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract existing portfolio governance, investment frameworks, strategy documents

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

- **First**, check if `.arckit/templates-custom/it4it-strategy-portfolio-template.md` exists in the project root

- **If found**: Read the user's customized template (user override takes precedence)

- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/it4it-strategy-portfolio-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize it4it-strategy-portfolio`

### 3. IT4IT Strategy to Portfolio Framework

S261 Ch. 6 defines four functional components, grouped into two functions:

| Function | Components | Primary Data Objects |
|---|---|---|
| **Strategy** | Policy · Strategy · Enterprise Architecture | Policy · Strategic Theme · Strategic Objective · Architecture Roadmap Item · Architecture Blueprint · Value Stream |
| **Portfolio** | Portfolio Backlog · Proposal · Product Portfolio | Portfolio Backlog Item · Resource Plan · Digital Product |

**Policy Functional Component** — manages creation, review, approval, and audit of Policies; supports Evaluate, Explore, Integrate. Key attributes: Id · Name · Description · Applicable Geography. Key relationships: Policy ↔ Digital Product (n:m) · Policy ↔ Architecture Roadmap Item (n:m) · Policy ↔ Portfolio Backlog Item (n:m) · Policy ↔ Requirement (n:m).

**Strategy Functional Component** — manages portfolio strategy aligned with business/enterprise strategy. **Strategic Theme** = a statement of direction and priorities that summarizes Strategic Objectives. **Strategic Objective** = specific actionable goals and measurable outcomes for identified stakeholders.

**Portfolio Backlog Functional Component** — lifecycle management and visibility of Portfolio Backlog Items. Key attributes: Id · Name · Description · Prioritization · Acceptance Criteria · Related Products · Demand Profile · Cost Estimation. Key relationships: PBI ↔ Strategic Objective (n:m) · PBI ↔ Architecture Roadmap Item (n:1) · PBI ↔ Policy (n:m) · PBI ↔ Resource Plan (1:1) · PBI ↔ Digital Product (n:m) · PBI → Product Backlog Item (1:m).

**Proposal Functional Component** — manages Resource Plans (funding packages of one or more Portfolio Backlog Items). States: proposed, approved, active, deferred, rejected.

Load `${CLAUDE_PLUGIN_ROOT}/references/functional-components-reference.md` for the full component and KDO catalog.

### 4. Shared Schema Definitions

Strategy to Portfolio commands reuse schema definitions:

- **`functional-component.json`** — Functional component definition schema (components, KDOs, cardinalities, systems of record)

### 5. Generate the Strategy to Portfolio Document

Create the document following the template structure.

#### Document Control

- Generate Document ID: `ARC-{P}-ITSF-v1.0` (for filename: `ARC-{P}-ITSF-v1.0.md`)

- Set owner, dates, status, classification

#### Policy Framework

- Policy lifecycle (create → review → approve → audit), review cadence, applicability geography

#### Strategy

- Strategic themes, strategic objectives (actionable + measurable), alignment to business/enterprise strategy

#### Portfolio Backlog

- PBI lifecycle, prioritisation approach, demand profiles, cost estimation, relationship to Product Backlog Items

#### Proposal and Resource Plans

- Resource plan structure, proposal state machine (proposed → approved/active/deferred/rejected), funding commitment model

#### Cardinalities and Systems of Record

- KDO cardinalities per the S261 catalog; the system of record for each KDO

#### Conformance Notes

- This artefact **references** S261 (a snapshot, not an approved standard); no conformance claim

### 6. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** pass. Fix any failures before proceeding.

### 7. Write the Document

**IMPORTANT**: The Strategy to Portfolio document will be a substantial document (typically 200-300 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-ITSF-v1.0.md
```text

### 8. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## IT4IT Strategy to Portfolio Document Created

**Document**: `projects/{P}/ARC-{P}-ITSF-v1.0.md`
**Document ID**: ARC-{P}-ITSF-v1.0

### Policy Framework
- **Policies in scope**: [N] — review cadence: [cadence]

### Strategy
- **Strategic themes**: [N]
- **Strategic objectives**: [N] (all measurable)

### Portfolio Backlog
- **PBIs**: [N] — prioritisation: [approach]

### Proposal / Resource Plans
- **Resource plans**: [N] — states: [distribution]

### Synthesised From
- [✅/⚠️] Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] IT4IT Value Network: ARC-{P}-ITVN-v[N].md

### Next Steps
1. Trace PBIs into the Develop function: `/arckit-it4it:it4it-develop-test`
2. Document the Evaluate/Explore stream: `/arckit-it4it:it4it-value-stream`

**File location**: `projects/{P}/ARC-{P}-ITSF-v1.0.md`
```text

## Important Notes

1. **Product-based investment**: Portfolio Backlog Items — not projects — are the unit of funding. Where existing practice is project-based, flag the gap explicitly.
2. **Reference, not conformance**: S261 is a snapshot; cite it as a reference, never claim conformance (see `references/citation-instructions.md`).
3. **Cardinality is normative**: The S261 KDO cardinalities (1:1, 1:m, n:m) are the reference architecture's data contract; record deviations as gaps, not choices.
4. **Use Write Tool**: The document is typically 200-300 lines. ALWAYS use the Write tool to create it.
5. **Version Management**: If a Strategy to Portfolio document already exists (`ARC-*-ITSF-v*.md`), create a new version (v2.0) rather than overwriting.
6. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji.
