---
description: Generate a UML 2.5.1 solution design document with six embedded PlantUML diagram views
argument-hint: "<project ID or domain, e.g. '001', 'patient records'>"
doc-type: SOLN
effort: high
handoffs:
  - command: hld-review
    description: Validate component and deployment choices
  - command: dld-review
    description: Validate class and sequence design
  - command: traceability
    description: Map requirements to design elements
  - command: sow
    description: Include solution design scope in RFP
  - command: diagram
    description: Generate companion standalone DIAG artefacts for individual diagrams
---

# ArcKit: Solution Design Generation

You are an expert enterprise architect helping create a UML 2.5.1 solution design document with six embedded PlantUML diagram views: use case, sequence, component, deployment, class, and object. The document will guide component selection, deployment strategy, integration patterns, and compliance requirements, and will integrate with ArcKit's governance workflow as a `SOLN` artefact.

## What is a Solution Design?

A solution design document is a governed artefact that describes how a set of requirements will be met by a concrete architecture. It combines narrative design rationale with six UML 2.5.1 diagram views, each expressed in PlantUML:

- **Use Case**: the system's actors and the use cases they interact with, derived from functional and integration requirements
- **Sequence**: the key interaction flows between actors and components for the critical business scenarios
- **Component**: the component boundaries, dependencies, and technology choices that make up the solution
- **Deployment**: the infrastructure topology (zones, nodes, runtimes) on which the solution is deployed
- **Class**: the key domain model classes and their relationships, derived from the data model
- **Object**: the runtime object instances and their current state for representative scenarios

PlantUML is the sole notation for all six views. Mermaid is **not** offered as an alternative: Mermaid has no object-diagram grammar and no first-class UML use-case or component references. If the user explicitly requests Mermaid, note the limitation and proceed with PlantUML.

## User Input

```text
$ARGUMENTS
```

The arguments may include:

- A project ID or name (e.g. `001`, `patient-records`)
- Optionally, a comma-separated list of diagram types to populate (e.g. `sequence,class`); any omitted types remain as placeholders

## Instructions

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

1. **Read existing artifacts from the project context:**

   - Run the intake interview per `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md` — derive required inputs from the effective template and MANDATORY prerequisites, prefill from existing sources, put **every** intake question to the user one at a time (**ask-always, answer-optional** — the interview must ask; each answer is optional and may be skipped, rendering as a `TBD` marker when skipped), and persist the answers. A previously saved or prefilled answer never waives the interview — on a re-run, a saved `.arckit/intake/` file only prefills the questions, so every question is still put to the user, one at a time, to confirm, override, or skip. Never collapse the interview into a single batch-confirmation question: each question is its own turn, even when fully prefilled; if no structured question tool is available, ask each question in plain text.

   **MANDATORY** (stop if missing):
   - **REQ** (Requirements)
     - Extract: all BR (business requirements), FR (functional requirements), NFR (non-functional requirements), INT (integration requirements), DR (data requirements)
     - If missing: STOP and warn the user to run `/arckit:requirements` first — the solution design MUST be based on the requirements artefact

   **RECOMMENDED** (read if available, note if missing):
   - **STKE** (Stakeholder Analysis)
     - Extract: actors, RACI matrix, governance stakeholders
   - **PRIN** (Architecture Principles, in 000-global)
     - Extract: technology standards, patterns, constraints that shape component and deployment choices
   - **ADR** (`decisions/ARC-*-ADR-*.md`)
     - Extract: recorded architectural decisions and their rationale; the Design Rationale section must be consistent with existing ADRs
   - **DATA** (`ARC-*-DATA-*.md`)
     - Extract: entities, relationships, and attributes that drive the class diagram

   **OPTIONAL** (read if available, skip silently if missing):
   - **SOBC** (Business Case)
     - Extract: scope, benefits, and cost constraints that bound the solution
   - **RSCH** (Research Findings)
     - Extract: technology recommendations and build-vs-buy decisions
   - **HLDR** (HLD Review) / **DLDR** (DLD Review)
     - Extract: prior review findings that the solution design must address

2. **Identify the target project**:
   - Use the **ArcKit Project Context** (above) to find the project matching the user's input (by name or number)
   - If no match, create a new project:
     1. Use Glob to list `projects/*/` directories and find the highest `NNN-*` number (or start at `001` if none exist)
     2. Calculate the next number (zero-padded to 3 digits, e.g., `002`)
     3. Slugify the project name (lowercase, replace non-alphanumeric with hyphens, trim)
     4. Use the Write tool to create `projects/{NNN}-{slug}/README.md` with the project name, ID, and date — the Write tool will create all parent directories automatically
     5. Also create `projects/{NNN}-{slug}/external/README.md` with a note to place external reference documents here
     6. Set `PROJECT_ID` = the 3-digit number, `PROJECT_PATH` = the new directory path

3. **Read external documents and policies**:
   - Read any **external documents** listed in the project context (`external/` files) — extract reference architectures, integration patterns, deployment constraints, existing component topologies
   - Read any **vendor HLD/DLD** documents (`vendors/{vendor}/hld-v*.md`, `vendors/{vendor}/dld-v*.md`) — extract component boundaries, technology choices, data store definitions, API contracts. These are external documents and do not need to be ArcKit-generated.
   - Read any **enterprise standards** in `projects/000-global/external/` — extract enterprise architecture blueprints, reference deployment patterns, cross-project integration maps
   - If no external docs exist but they would improve the solution design, ask: "Do you have any reference architectures, vendor HLD/DLD documents, or deployment diagrams? I can read PDFs, images, and Markdown directly. Place them in `projects/{project-dir}/external/` and re-run, or skip."
   - **Citation traceability**: When referencing content from external documents, follow the citation instructions in `${CLAUDE_PLUGIN_ROOT}/references/citation-instructions.md`. Place inline citation markers (e.g., `[PP-C1]`) next to findings informed by source documents and populate the "External References" section in the template.

4. **Interactive configuration** (skip when diagram types are named in the arguments):

   If the user supplied diagram types in the arguments (e.g. `/arckit:solution-design 001 sequence,class`), skip the questions below and use that subset directly.

   Otherwise, ask **both** questions in a **single AskUserQuestion call** so the user sees them together:

   **Question 1 — Diagram subset** (multi-select, default: all six):
   Which of the six UML diagram types should be populated in this run? Unselected types are kept as placeholders in the document.

   - Use Case (default selected)
   - Sequence (default selected)
   - Component (default selected)
   - Deployment (default selected)
   - Class (default selected)
   - Object (default selected)

   **Question 2 — PlantUML style** (single-select, default):
   How detailed should the PlantUML blocks be?

   - Default — one representative scenario per diagram, standard PlantUML style
   - Detailed — multiple scenarios, extended interactions, and deployment variants
   - Minimal — a single, tightly focused diagram per type

   **Gathering rules** (apply to all questions in this section):

   - Ask the most important question first; fill in secondary details from context or reasonable defaults.
   - **Maximum 2 rounds of questions.** After that, pick the best option from available context.
   - If still ambiguous after 2 rounds, choose the (Recommended) option and note: *"I went with [X] — easy to adjust if you prefer [Y]."*

   If the user answers Question 1 with a **single** type, or explicitly asks for companion standalone diagram artefacts, also write one `ARC-{PROJECT_ID}-DIAG-{NNN}-v1.0.md` per populated diagram type to `projects/{PROJECT_ID}/diagrams/` using `bash .arckit/scripts/bash/generate-document-id.sh --next-num projects/{PROJECT_ID}/diagrams ARC-{PROJECT_ID}-DIAG` for the next available DIAG sequence.

5. **Read the template** (with user override support):
   - **First**, check if `.arckit/templates/solution-design-template.md` exists in the project root
   - **If found**: Read the user's customized template (user override takes precedence)
   - **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/solution-design-template.md` (default)

   > **Tip**: Users can customize templates with `/arckit:customize solution-design`

6. **Generate the solution design document**:

   Populate the template sections as follows. The full skeleton is always generated; only the diagram types not selected in Step 4 are left as placeholders with the note *"Not selected for this run — re-run `/arckit:solution-design` with this diagram type included."*

   **A. Document Control and Revision History**:
   - Resolve the Document Control header per the template's `<!-- DOC-CONTROL-HEADER -->` comment
   - Fill Revision History with version v1.0, today's date, author `ArcKit AI`, changes `Initial creation from /arckit:solution-design command`, Approved By / Approval Date `PENDING`

   **B. Overview**:
   - 2–3 sentences describing the problem this solution addresses and the scope of the design
   - List of key constraints and assumptions from PRIN, SOBC, and external documents (with citation markers where applicable)

   **C. Use Case Diagram** (PlantUML):
   - Actors derived from STKE and REQ (FR/INT)
   - Use cases named after functional requirements (FR-xxx) and integration points (INT-xxx)
   - `<<include>>` / `<<extend>>` relationships where requirements compose or specialise
   - Reference `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/use-case-diagrams.md` for syntax

   **D. Sequence Diagram** (PlantUML):
   - Lifelines: one actor plus one participant per component from the Component Diagram
   - Messages for the critical FR/INT scenarios, with response arrows and key data passed
   - `alt` / `loop` fragments for conditional and repeated flows
   - Reference `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/sequence-diagrams.md` for syntax

   **E. Component Diagram** (PlantUML):
   - Components (application, API, event, data stores) with technology labels
   - External systems as `cloud` or `actor` nodes; integration protocols on the arrows
   - Boundaries from the external HLD/DLD and PRIN; cite the source for each non-trivial choice
   - Reference `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/component-diagrams.md` for syntax

   **F. Deployment Diagram** (PlantUML):
   - `node` / `rectangle` nesting for regions, zones, and networks
   - `artifact` for runtimes and data stores placed on the right nodes
   - Cite deployment constraints (data residency, availability) from NFR-SEC and external documents
   - Reference `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/deployment-diagrams.md` for syntax

   **G. Class Diagram** (PlantUML):
   - Domain classes derived from the DATA artefact entities (one class per entity, attributes from the entity catalog, relationships from the ERD)
   - Cardinality on every association; `«entity»` / `«service»` stereotypes where useful
   - If no DATA artefact exists, derive a minimal class model from DR-xxx requirements and flag it as *draft, unverified*
   - Reference `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/class-diagrams.md` for syntax

   **H. Object Diagram** (PlantUML):
   - Runtime instances of the key classes for one representative scenario (e.g. "a patient record mid-lifecycle")
   - `object` declarations with `<<class>>` stereotypes and current field values
   - Only one or two scenarios — object diagrams illustrate state, not the full model
   - Object diagrams are a PlantUML-only notation (Mermaid has no object-diagram grammar). Read `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/object-diagrams.md` before writing the Object Diagram section, and check `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/common-syntax-errors.md` for common gotchas

   **I. Design Rationale**:
   - For each major decision (component choices, deployment targets, integration patterns), state the decision, the alternatives considered, and why the chosen option was selected
   - Cross-reference any existing ADRs; flag conflicts for the user to resolve
   - Every decision that derives from an external document carries its citation marker

   **J. Requirements Traceability**:
   - A table mapping BR / FR / NFR / INT / DR requirement IDs to the design elements that satisfy them (component, sequence, use case, class, or deployment node)
   - Flag requirements with no mapping as open items

   **K. Summary**:
   - Solution scope, key design decisions, component count, integration points, deployment targets, open questions

   **L. External References**:
   - Document Register, Citations, and Unreferenced Documents tables per the template, populated from Step 3

7. **Write the document using the Write tool**:
   - **First**, use Glob to check for existing `projects/{PROJECT_ID}/ARC-{PROJECT_ID}-SOLN-v*.md` files
   - If none exist, write to `projects/{PROJECT_ID}/ARC-{PROJECT_ID}-SOLN-v1.0.md`
   - If one or more exist, read the latest version and increment the sequence: write to `ARC-{PROJECT_ID}-SOLN-v2.0.md` (or the next unused sequence), copying forward the Document Control history and adding a new Revision History row
   - Use the **Write tool** to save the document — never stream the full document to the conversation (32K output token limit)
   - After writing, record the new `SOLN` artefact in the project manifest (the manifest hook does this on write)

8. **Show a summary only**:

   Present a concise summary — not the full document:

   ```text
   ## Solution Design Summary

   **Project**: {PROJECT_NAME} ({PROJECT_ID})
   **Document**: `ARC-{PROJECT_ID}-SOLN-v1.0.md`
   **Diagram types populated**: [list, e.g. Use Case, Sequence, Component]
   **Diagram types as placeholders**: [list, or "none"]

   **Key design decisions**:
   - [Decision 1] — [rationale, with citation if from an external doc]
   - [Decision 2] — [rationale]

   **Statistics**:
   - Actors: [N]
   - Use cases: [N]
   - Components: [N]
   - Deployment nodes: [N]
   - Domain classes: [N]
   - Requirements mapped: [N] BR / [N] FR / [N] NFR / [N] INT / [N] DR
   - Unmapped requirements: [N]

   **What's in the Document**:
   - Use Case Diagram
   - Sequence Diagram
   - Component Diagram
   - Deployment Diagram
   - Class Diagram
   - Object Diagram
   - Design Rationale
   - Requirements Traceability
   - External References

   ### Next Steps

   - Review `ARC-{PROJECT_ID}-SOLN-v1.0.md` for full diagram detail
   - Run `/arckit:hld-review` to validate component and deployment choices
   - Run `/arckit:traceability` to map requirements to design elements
   - Run `/arckit:diagram` to generate standalone C4/DIAG companions if needed
   ```

## Common Gotchas

- **PlantUML-only notation**: All six diagram blocks MUST use fenced `plantuml` code blocks. If the user asks for Mermaid, explain that Mermaid has no object-diagram grammar and no UML use-case or component references, and proceed with PlantUML. Do not offer Mermaid as an alternative.

- **Unselected diagram types are placeholders, not omissions**: The document skeleton is always generated in full — all six sections appear. Only the unselected types carry the "Not selected for this run" placeholder note, so a later re-run can fill them in without regenerating the populated ones.

- **Requirements artefact is MANDATORY**: Do not generate a SOLN document without an `ARC-{PROJECT_ID}-REQ-v*.md` artefact. If it is missing, stop and suggest `/arckit:requirements`. A solution design without requirements has no traceability basis.

- **Object diagrams are state, not model**: The Object Diagram shows one or two representative runtime scenarios with concrete instance values. Do not use it to dump the full class inventory — that belongs in the Class Diagram. If the project has no runtime scenarios yet, note the assumption and pick one critical FR scenario as the exemplar.

- **Citation markers on every external-sourced decision**: Component choices, deployment constraints, and integration patterns taken from vendor HLD/DLD or external documents need inline citation markers (`[DOC_ID-CN]`) and a row in the External References table. Unattributed external content breaks the governance chain that `/arckit:traceability` depends on.

- **Existing SOLN files must be read before writing**: Run the Glob for `ARC-{PROJECT_ID}-SOLN-v*.md` before the Write. If a v1.0 already exists, write v2.0 and carry forward the Document Control history — never overwrite an approved artefact in place.

## Output

The command produces:

- `projects/{PROJECT_ID}/ARC-{PROJECT_ID}-SOLN-v1.0.md` (or next sequence) — the governed SOLN document with all six PlantUML diagram sections, Design Rationale, Requirements Traceability, and External References
- Optionally, `projects/{PROJECT_ID}/diagrams/ARC-{PROJECT_ID}-DIAG-{NNN}-v1.0.md` companion artefacts — only when the user requested standalone DIAG artefacts or selected a single diagram type
