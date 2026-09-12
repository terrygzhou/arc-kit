---
description: Generate ArchiMate layer views (business, application, technology, optional data and motivation) in PlantUML ArchiMate notation
argument-hint: "<layer view subject, e.g. 'claims intake business layer with realization to application'>"
doc-type: ARCH
effort: high
handoffs:
  - command: diagram
    description: Complementary C4 view — never mix C4 and ArchiMate elements in one diagram
  - command: hld-review
    description: Reflect the technology-layer view in the High-Level Design review
---

# ArcKit: ArchiMate Layer View Generation

You are an expert enterprise architect generating **ArchiMate layer views** in PlantUML ArchiMate notation (the `!include <archimate/Archimate>` standard library). Each generated view is a single-layer (plus optional Motivation overlay) architectural slice that integrates with ArcKit's governance workflow: one view per architectural layer, sequenced as `ARC-{P}-ARCH-{NNN}-v1.0` in the project's `diagrams/` directory.

## What are ArchiMate Views?

ArchiMate is an open, independent enterprise architecture modeling language that describes an enterprise across layered views (Motivation, Strategy, Business, Application, Technology, Physical, Implementation). In ArcKit, ArchiMate views are used to:

- **Communicate**: one architectural layer per view — business people see the Business layer, engineers see Application/Technology
- **Validate**: realization chains (technology → application → business → motivation) so every concrete element traces to the abstract element it realizes
- **Document**: the layer's element inventory, integration points, and NFR coverage alongside the diagram
- **Trace**: motivation (drivers, goals, constraints) down to the elements that realize them

ArchiMate views complement, and never replace, C4 diagrams (`/arckit:diagram`). C4 answers "what is in the system and how do the parts talk"; ArchiMate answers "which layer's elements realize which business or motivation elements, and why".

## User Input

```text
$ARGUMENTS
```

## Step 1: Understand the Context

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

Read existing artifacts from the project context:

1. **REQ** (Requirements) — Extract: business requirements, functional requirements, integration requirements. Identify: business processes, user actors, data requirements
2. **Vendor HLD** (`vendors/{vendor}/hld-v*.md`) — Extract: technical architecture, containers, technology choices. Identify: application components, technology nodes, integration patterns
3. **Vendor DLD** (`vendors/{vendor}/dld-v*.md`) — Extract: component specifications, API contracts, database schemas. Identify: internal component structure, logical data objects, dependencies
4. **WARD** (Wardley Map, in `wardley-maps/`) — Extract: component evolution stages, build vs buy decisions. Identify: strategic positioning, capability areas
5. **PRIN** (Architecture Principles, in 000-global) — Extract: technology standards, patterns, constraints. Identify: motivation elements (drivers, constraints, principles)

## Step 1b: Interactive Configuration

**IMPORTANT**: Ask **both** questions below in a **single AskUserQuestion call** so the user sees them together.

**Gathering rules** (apply to all questions in this section):

- Ask the most important question first; fill in secondary details from context or reasonable defaults.
- **Maximum 2 rounds of questions.** After that, pick the best option from available context.
- If still ambiguous after 2 rounds, choose the (Recommended) option and note: *"I went with [X] — easy to adjust if you prefer [Y]."*

**Question 1** — header: `Layer`, multiSelect: false
> "Which ArchiMate layer should this view cover? (One layer per view; pick 'All major layers' for one view per layer, sequenced)"

- **Business (Recommended)**: Business processes, services, events, objects, roles — best for stakeholder communication
- **Application**: Application components, services, data objects — best after HLD phase
- **Technology**: Technology nodes, systems, infrastructure — best after HLD/DLD phase
- **All major layers**: One view per layer (Business, Application, Technology), each its own sequenced `ARCH` document
- **Data only**: Logical data objects and their flows across layers

**Question 2** — header: `Motivation`, multiSelect: false
> "Should the view carry a Motivation overlay?"

- **Yes, motivation + capability (Recommended)**: Add drivers, goals, constraints (and optional capabilities) above the layer; realization edges link motivation → layer elements
- **No, structural view only**: Layer elements and their intra-layer relationships only
- **Capability map view**: Strategy-layer capabilities instead of the structural overlay

**Skip rules**: If the user's arguments already name the layer (e.g. `/arckit:archimate application layer`), skip Question 1; if they already state the motivation treatment, skip Question 2; if both are specified, ask nothing.

## Step 2: Load the Syntax Reference

Read `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/archimate.md` — Pinned API (include line, element and relationship macros, version pin), notation cheat-sheet, layer-tier ordering, realization/relationship direction rules, colour standards, element-count thresholds, and antipatterns.

- Every generated diagram uses the pinned include line from the reference (do not substitute other include forms without re-pinning the reference).
- Element macros: `Category_ElementName(alias, "description")` — one category per view.
- Relationship macros: `Rel_<Type>(from, to, "label")` with optional `_Up|_Down|_Left|_Right` direction suffix.

## Step 3: Generate the View

### Element Identification

Collect elements **from the selected layer only** (plus Motivation when Question 2 selects an overlay):

| Layer | Typical elements |
|-------|------------------|
| Business | `Business_Process`, `Business_Service`, `Business_Event`, `Business_Object`, `Business_Role` |
| Application | `Application_Component`, `Application_Service`, `Application_DataObject`, `Application_Interface` |
| Technology | `Technology_Node`, `Technology_SystemSoftware`, `Technology_Device`, `Technology_Service` |
| Data | `Application_DataObject` (logical data objects) with `Rel_Flow` edges |
| Motivation overlay | `Motivation_Driver`, `Motivation_Goal`, `Motivation_Constraint`, `Strategy_Capability` |

### Realization and Direction Rules

- **Realization edges point concrete → abstract**: `Application_Component` → `Business_Service`/`Business_Process`, `Technology_Node` → `Application_Component`/`Application_Service`, `Strategy_Capability` → `Business_Process`/`Application_Service`.
- **Serving** links a service to the component that provides it: `Application_Service` → `Application_Component`.
- **Access** links an element to the data object or node it uses: `Rel_Access_r`, `Rel_Access_rw`, `Rel_Access_w`.
- Keep relationships within one layer or one layer step; a two-layer jump (Business → Technology) is an antipattern — insert the intermediate element or split the view.
- Prefer `LAYOUT_TOP_DOWN()` with layers stacked Motivation (top) → Business → Application → Technology; use `Lay_D`/`Lay_U` hidden edges for placement only.

### Colour Standards

Use the theme's named colour tokens (Business/Application/Technology, etc.) — **never hard-code layer hex colours**. Set a legend in a `legend` block for any custom notation.

### Element Count Threshold

**Maximum 12 elements per layer.** Above 12, split at natural architectural boundaries (process group, capability, or subsystem) and generate multiple sequenced views instead of one crowded diagram.

## Step 4: Generate the Output

### File Location

`projects/{project_number}-{project_name}/diagrams/ARC-{PROJECT_ID}-ARCH-{NNN}-v1.0.md`

**Generate the document ID** (ARCH is a multi-instance type; sequence number is scoped to the project's `diagrams/` directory). Run the bundled helper:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/bash/generate-document-id.sh" \
     {P} ARCH --next-num "{project_path}/diagrams"
```

This returns the next sequenced ID, e.g. `ARC-{P}-ARCH-{NNN}-v1.0`. Use the returned value as `document_id` and take `version` (`1.0`) from it.

**Run the intake interview**:

- Run the intake interview per `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md` — derive required inputs from the effective template and MANDATORY prerequisites, prefill from existing sources, put **every** intake question to the user one at a time (**ask-always, answer-optional** — the interview must ask; each answer is optional and may be skipped, rendering as a `TBD` marker when skipped), and persist the answers. A previously saved or prefilled answer never waives the interview — on a re-run, a saved `.arckit/intake/` file only prefills the questions, so every question is still put to the user, one at a time, to confirm, override, or skip. Never collapse the interview into a single batch-confirmation question: each question is its own turn, even when fully prefilled; if no structured question tool is available, ask each question in plain text.

**Read the template** (with user override support):

- **First**, check if `.arckit/templates/archimate-template.md` exists in the project root
- **If found**: Read the user's customized template (user override takes precedence)
- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/archimate-template.md` (default)

> **Tip**: Users can customize templates with `/arckit:customize archimate`

### Auto-Populate Document Control Fields

Before completing the document, populate ALL document control fields in the header:

*Auto-populated fields*:

- `[PROJECT_ID]` → Extract from project path (e.g., "001" from "projects/001-project-name")
- `[VERSION]` → "1.0" (or increment if a previous version exists)
- `[DATE]` → Current date in YYYY-MM-DD format
- `[COMMAND]` → "arckit.archimate"

*User-provided fields*:

- `[PROJECT_NAME]` → Full project name from project metadata or user input
- `[OWNER_NAME_AND_ROLE]` → Document owner (prompt user if not in metadata)
- `[CLASSIFICATION]` → Default to `${user_config.default_classification}`; if unavailable, use "OFFICIAL" for UK Gov, "PUBLIC" otherwise (or prompt user)

*Pending fields* (leave as `[PENDING]` until manually updated): `[REVIEWER_NAME]`, `[APPROVER_NAME]`, `[DISTRIBUTION_LIST]`.

**Populate Revision History**:

```markdown
| 1.0 | {DATE} | ArcKit AI | Initial creation from `/arckit:archimate` command | [PENDING] | [PENDING] |
```

**Populate Generation Metadata Footer** (includes the model):

```markdown
**Generated by**: ArcKit `/arckit:archimate` command
**Generated on**: {DATE} {TIME} GMT
**ArcKit Version**: {VERSION}
**Project**: {PROJECT_NAME} (Project {PROJECT_ID})
**Model**: [Use actual model name, e.g. "Claude Sonnet 5 (session default)"]
**Generation Context**: [Brief note about source documents used]
```

## Step 5: ArchiMate Quality Gate

After generating the view, evaluate it against the criteria below. Report the results as part of the output:

| # | Criterion | Target | Result | Status |
|---|-----------|--------|--------|--------|
| 1 | Single-layer stereotyping | All structural elements belong to the one selected layer (plus optional Motivation overlay) | {assessment} | {PASS/FAIL} |
| 2 | Realization direction | Every `Rel_Realization` edge points concrete → abstract | {assessment} | {PASS/FAIL} |
| 3 | Element count | ≤ 12 elements per layer (see Step 3 threshold) | {count}/12 | {PASS/FAIL} |
| 4 | Labelled edges | Every relationship macro carries a label; no unlabelled edges | {assessment} | {PASS/FAIL} |
| 5 | Notation purity | No C4/C4-PlantUML elements or UML boxes mixed into the ArchiMate diagram | {assessment} | {PASS/FAIL} |
| 6 | Pinned include | The diagram block contains the pinned `!include <archimate/Archimate>` line | {assessment} | {PASS/FAIL} |
| 7 | Layout consistency | One layout direction; layers stacked in tier order; no cross-layer noise | {assessment} | {PASS/FAIL} |
| 8 | Legend for custom notation | Any custom notation is documented in a `legend` block | {assessment} | {PASS/FAIL} |
| 9 | Inventory traceability | Every diagram element appears in the Element Inventory and every relationship in the traceability table | {assessment} | {PASS/FAIL} |

### Remediation by Criterion

| Failed # | Remediation Steps |
|----------|------------------|
| 1 (Single-layer stereotyping) | Move out-of-layer elements to their own view; keep the Motivation overlay as the only second layer |
| 2 (Realization direction) | Flip the edge: realization always runs concrete → abstract (application → business, technology → application) |
| 3 (Element count) | Split the view at natural boundaries; emit additional sequenced `ARCH` views and cross-link them in Linked Artifacts |
| 4 (Labelled edges) | Add a one-line label to every `Rel_*` call; move detail to the traceability table |
| 5 (Notation purity) | Strip C4 macros or raw UML rectangles; express the same elements with the layer's ArchiMate macros |
| 6 (Pinned include) | Restore the pinned include line from `skills/plantuml-syntax/references/archimate.md` |
| 7 (Layout consistency) | Apply `LAYOUT_TOP_DOWN()`; reorder declarations in tier order; remove edges that jump two layer steps |
| 8 (Legend) | Add a `legend` block mapping custom notation to plain-English meaning |
| 9 (Inventory traceability) | Regenerate the Element Inventory and Layer & Realization Traceability tables from the diagram source |

### Iterative Review Loop

1. Generate the view code
2. Evaluate all 9 criteria in the quality gate table
3. If any criterion fails: apply the corresponding remediation, regenerate, re-evaluate all 9 criteria
4. Repeat up to **3 iterations**
5. If criteria still fail after 3 iterations, document accepted trade-offs and proceed

## Step 6: Integration with ArcKit Workflow

- **Before**: If the selected layer has no supporting artifact (Business view without REQ; Application/Technology view without HLD), say so and recommend `/arckit:requirements` or `/arckit:hld-review` first — the view can still be generated, flagged as *draft, unverified*.
- **After**:
  - Record the new `ARCH` artifact in the project manifest (the manifest hook does this on write).
  - Link sibling views (other `ARCH` documents in `diagrams/`) and the C4 companion (`ARC-{P}-DIAG-*.md`) in Linked Artifacts.
  - Handoff: C4 complement → `command: diagram`; technology-layer review → `command: hld-review`.

## Antipatterns (never emit)

- Cross-layer noise: a Business element connected directly to a Technology element (two layer steps)
- Unlabelled relationship edges
- Mixing C4-PlantUML and ArchiMate elements in one diagram
- Hard-coded hex layer colours instead of theme colour tokens
- A "kitchen-sink" view: more than one structural layer, or more than 12 elements per layer
