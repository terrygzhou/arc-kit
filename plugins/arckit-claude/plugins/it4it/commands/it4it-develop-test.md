---
description: Define the IT4IT Develop & Test functions (S261 Ch. 7) — product backlog, requirement, design, pipeline, build, release composition, and test/defect components
argument-hint: "<product or programme name, e.g. 'Observability Stack'>"
effort: high
handoffs:

  - command: it4it-strategy-portfolio
    description: Trace this function's product backlog items back to portfolio backlog items

  - command: it4it-consume-fulfil
    description: Connect deployed releases to service offerings and fulfillment
---

You are helping an enterprise architect create an **IT4IT Develop & Test** document using the Open Group IT4IT Standard v3.1 (Snapshot, S261) Ch. 7 (Requirement to Deploy functions). The Develop function covers the full SDLC from product backlog through build packages to release composition; the Test function covers test cases, test plans, and defects.

## User Input

```text
$ARGUMENTS
```text

## Trigger Guidance

Use this command when **any** of the following conditions are met:

- The **Develop function** (product backlog, requirement, product design, source control, pipeline, build package, release composition) needs to be defined against the IT4IT reference

- The **Test function** (test case, test plan, defect) needs to be formalised as an IT4IT function

- The Integrate value stream's stages (Plan Product Release → Design & Develop → Build, Integrate, & Test → Accept & Publish Release) need mapping to functional components

- CI/CD pipeline shape, build package structure, or release composition rules need a vendor-neutral reference

**Do NOT use** when:

- The portfolio layer (PBI, resource plans) is the subject → use `/arckit-it4it:it4it-strategy-portfolio`

- A value stream view is the subject → use `/arckit-it4it:it4it-value-stream`

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (stop if missing — generate upstream artefact first):

- **PRIN** (Architecture Principles, in 000-global) — Extract: Delivery principles, quality gates, pipeline guardrails
  - If missing: STOP and ask user to run `/arckit:principles` first. The IT4IT Develop & Test artefact must be grounded in architecture principles.

**RECOMMENDED** (read if available, note if missing):

- **ITSF** (IT4IT Strategy to Portfolio) — Extract: portfolio backlog items, product associations feeding this function

  - If missing: note that the portfolio context is limited

- **ITVN** (IT4IT Value Network) — Extract: position of the Integrate stream, cross-stream dependencies

  - If missing: note that the Value Network context is not available

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract existing SDLC definitions, CI/CD standards, testing standards

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

- **First**, check if `.arckit/templates-custom/it4it-develop-test-template.md` exists in the project root

- **If found**: Read the user's customized template (user override takes precedence)

- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/it4it-develop-test-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize it4it-develop-test`

### 3. IT4IT Develop & Test Framework

S261 Ch. 7 defines the Requirement to Deploy functions:

| Function | Components | Primary Data Objects |
|---|---|---|
| **Develop** | Product Backlog · Requirement · Product Design · Source Control · Pipeline · Build Package · Release Composition | Product Backlog Item · Requirement · Product Design · Capacity Model · Source · Pipeline · Build Package · Product Release · Product Release Blueprint |
| **Test** | Test · Defect | Test Case · Test Plan · Defect |

The **Develop** function covers the full SDLC from backlog through build packages to release composition. The **Pipeline** component covers CI/CD. The **Build Package** is the deployable unit. **Release Composition** combines build packages into a Product Release.

The **Test** function formalises test cases and test plans against requirements, and the defect lifecycle that closes the loop.

The Integrate value stream's stages map onto these components: Plan Product Release (Product Backlog) → Design & Develop (Product Design, Source Control) → Build, Integrate, & Test (Pipeline, Build Package, Test, Defect) → Accept & Publish Release (Release Composition, Product Release Blueprint).

Load `${CLAUDE_PLUGIN_ROOT}/references/functional-components-reference.md` for the full component and KDO catalog.

### 4. Shared Schema Definitions

Develop & Test commands reuse schema definitions:

- **`functional-component.json`** — Functional component definition schema (components, KDOs, cardinalities, systems of record)

### 5. Generate the Develop & Test Document

Create the document following the template structure.

#### Document Control

- Generate Document ID: `ARC-{P}-ITDT-v1.0` (for filename: `ARC-{P}-ITDT-v1.0.md`)

- Set owner, dates, status, classification

#### Develop Function

- Product backlog structure, requirement traceability, product design approach
- Source control model, pipeline (CI/CD) shape, build package rules
- Release composition: how build packages combine into a Product Release, the Product Release Blueprint

#### Test Function

- Test case / test plan model, test-to-requirement traceability, defect lifecycle

#### Quality Gates

- Gates at each Integrate stage, exit criteria per gate

#### Cardinalities and Systems of Record

- KDO cardinalities per the S261 catalog; the system of record for each KDO

#### Conformance Notes

- This artefact **references** S261 (a snapshot, not an approved standard); no conformance claim

### 6. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** pass. Fix any failures before proceeding.

### 7. Write the Document

**IMPORTANT**: The Develop & Test document will be a substantial document (typically 200-300 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-ITDT-v1.0.md
```text

### 8. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## IT4IT Develop & Test Document Created

**Document**: `projects/{P}/ARC-{P}-ITDT-v1.0.md`
**Document ID**: ARC-{P}-ITDT-v1.0

### Develop Function
- **Pipeline stages**: [N] — build package rules: [summary]
- **Release composition**: [approach]

### Test Function
- **Test model**: [summary] — defect lifecycle: [states]

### Quality Gates
- **Gates at Integrate stages**: [N]

### Synthesised From
- [✅/⚠️] Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] IT4IT Strategy to Portfolio: ARC-{P}-ITSF-v[N].md
- [✅/⚠️] IT4IT Value Network: ARC-{P}-ITVN-v[N].md

### Next Steps
1. Connect deployed releases to service offerings: `/arckit-it4it:it4it-consume-fulfil`
2. Trace product backlog items back to the portfolio: `/arckit-it4it:it4it-strategy-portfolio`

**File location**: `projects/{P}/ARC-{P}-ITDT-v1.0.md`
```text

## Important Notes

1. **Build Package is the deployable unit**: Release Composition combines build packages into a Product Release; the Product Release Blueprint records the composition.
2. **Reference, not conformance**: S261 is a snapshot; cite it as a reference, never claim conformance (see `references/citation-instructions.md`).
3. **Vendor-neutral**: Pipeline and build tooling choices are non-normative extensions; the reference defines the data contract, not the tools.
4. **Use Write Tool**: The document is typically 200-300 lines. ALWAYS use the Write tool to create it.
5. **Version Management**: If a Develop & Test document already exists (`ARC-*-ITDT-v*.md`), create a new version (v2.0) rather than overwriting.
6. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji.
