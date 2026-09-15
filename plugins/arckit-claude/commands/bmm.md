---
description: Generate a BMM 1.3 Business Motivation Model (stakeholders, outcomes, drivers, goals, objectives, measures, case, strategic themes, capabilities) plus ArchiMate motivation/strategy views
argument-hint: "<model scope or companion menu, e.g. 'full model with goal ladder'>"
doc-type: BMM
effort: max
handoffs:
  - command: strategy
    description: STRAT consumes the BMM Strategic Themes into the strategy narrative
  - command: roadmap
    description: ROAD sequencing from BMM Courses of Action / Plans
  - command: sobc
    description: 5-case ↔ BMM Case section mapping (UK-regime Green Book, conditional)
  - command: archimate
    description: Motivation overlay on layer views reuses BMM elements
---

# ArcKit: Business Motivation Model (BMM 1.3)

You are an expert enterprise architect generating the project's **Business Motivation Model (BMM 1.3)** — the OMG metamodel behind BIZBOK *Strategy & Stakeholder Alignment* and ArchiMate's Motivation/Strategy tiers. One BMM model per project: `ARC-{P}-BMM-v1.0.md` at the project root, single-instance, versioned by `-vN.N`. The model answers **why this architecture is being built, for whom, under what case, and how success is measured**; the ArchiMate views emitted alongside it are *projections* of the model, never a substitute for it.

## What is a BMM Model?

BMM 1.3 models the motivation chain: **Stakeholders → Outcomes → Goals → Objectives → Measures**, with **Drivers**, **Assumptions**, a documented **Case For / Case Against**, **Impact Factors**, and the strategy chain **Strategic Themes → Capabilities → Courses of Action → Resources**. It is the upstream "case for" that STKE, SOBC, STRAT, ROAD, and BPCM artefacts otherwise re-derive locally.

## User Input

```text
$ARGUMENTS
```

## Step 1: Understand the Context

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY prerequisites** (stop-and-ask):

1. **STKE** (Stakeholder Analysis) — extract: stakeholders, their goals, business drivers. **If missing: STOP and point the user at `/arckit:stakeholders` first — the model cannot be built without them.**
2. **PRIN** (Architecture Principles, in 000-global) — extract: constraints and principles that shape the case. **If missing: STOP and point the user at `/arckit:principles`.**

**RECOMMENDED** (read if present, note if missing):

- **SOBC** (Strategic Outline Business Case) — 5-case material feeding Case For / Case Against (UK-regime Green Book mapping)
- **ROAD** (Roadmap) — Courses of Action that already exist; BMM never rewrites them, it cross-references
- **WARD** (Wardley Maps) — strategic positioning behind the themes
- **RISK** (Risk Register) — impact factors that already carry likelihood/impact scores

**OPTIONAL**: external strategy documents (`external/`) — cite them per `${CLAUDE_PLUGIN_ROOT}/references/citation-instructions.md` and record them in section 8 (Traceability → External References).

## Step 1b: Interactive Configuration

**IMPORTANT**: Ask **both** questions below in a **single AskUserQuestion call** so the user sees them together.

**Gathering rules** (apply to all questions in this section):

- Ask the most important question first; fill in secondary details from context or reasonable defaults.
- **Maximum 2 rounds of questions.** After that, pick the best option from available context.
- If still ambiguous after 2 rounds, choose the (Recommended) option and note: *"I went with [X] — easy to adjust if you prefer [Y]."*

**Question 1** — header: `Scope`, multiSelect: false
> "What scope should the BMM model cover?"

- **Full model (Recommended)**: all nine sections — motivation chain (1–6) plus strategy chain (7)
- **Motivation-only**: sections 1–6; omit the strategy chain and the [A3] strategy view
- **Strategy-only**: section 7 + traceability; motivation sections carry summary pointers to existing artefacts

A scope that omits a tier omits the corresponding base view: Motivation-only emits [A2] only; Strategy-only emits [A3] only.

**Question 2** — header: `Diagram menu`, multiSelect: true
> "Which companion views should be generated alongside the model?"

- **Base views only (Recommended)**: [A2] motivation + [A3] strategy views, sequenced ARCH documents
- **+goal ladder [O1]**: goal–objective–measure ladder view (stereotyped Objective/Measure per § BMM Projection)
- **+case & assumptions overlay [O2]**: Case For / Case Against + Assumptions + Impact Factors as an influence structure (narrative stays in [A1])
- **+alignment view [O3]**: goal/objective → theme → capability → ROAD milestone → REQ → ADR realization chain
- **+Mermaid mindmap [O4]**: extend the append-only mindmap block in section 9 of [A1]

**Skip rules**: if the user's arguments already name the scope (e.g. `/arckit:bmm motivation-only`), skip Question 1; if they already name menu items, skip Question 2; if both are specified, ask nothing.

## Step 2: Load the References

Read `${CLAUDE_PLUGIN_ROOT}/references/bmm-reference.md` — the BMM 1.3 element/relationship catalogue, the BMM ↔ ArchiMate ↔ ArcKit mapping, alignment notes, and gate criteria.

Read `${CLAUDE_PLUGIN_ROOT}/skills/plantuml-syntax/references/archimate.md` — § Pinned API (include line, element and relationship macros, version pin) and § **BMM Projection** (stereotyped encodings for Objective / Measure / Strategic Theme, relationship vocabulary, legend rules, and the rendered sample fixture at `tests/fixtures/archimate/bmm/`).

- Every generated view uses the pinned include line from the reference (do not substitute other include forms without re-pinning the reference).
- 4.0-only BMM elements are **stereotyped, never faked as native**: `Objective` → `Motivation_Goal(alias, "Objective: …")`; `Measure` → `Motivation_Goal(alias, "Measure: …")`; `Strategic Theme` → `Strategy_Capability(alias, "Theme: …")` — each with a `legend` block.

## Step 3: Generate the Model [A1]

### File Location

`projects/{project_number}-{project_name}/ARC-{PROJECT_ID}-BMM-v1.0.md` — the **project root**, single-instance. BMM is not a multi-instance type: one canonical model per project, bumped to `v1.1` on regeneration instead of sequenced.

### Run the Intake Interview

- Run the intake interview per `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md` — derive required inputs from the effective template and MANDATORY prerequisites, prefill from existing sources (STKE stakeholders/outcomes, PRIN constraints, SOBC cases, RISK factors, ROAD courses of action), put **every** intake question to the user one at a time (**ask-always, answer-optional** — the interview must ask; each answer is optional and may be skipped, rendering as a `TBD` marker when skipped), and persist the answers. A previously saved or prefilled answer never waives the interview — on a re-run, a saved `.arckit/intake/` file only prefills the questions. Never collapse the interview into a single batch-confirmation question: each question is its own turn, even when fully prefilled; if no structured question tool is available, ask each question in plain text.

### Read the Template

- **First**, check if `.arckit/templates/bmm-template.md` exists in the project root
- **If found**: Read the user's customized template (user override takes precedence)
- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/bmm-template.md` (default)

> **Tip**: Users can customize templates with `/arckit:customize bmm`

### Populate the Nine Sections

1. **Stakeholders & Outcomes** — from STKE, including the stakeholder–outcome matrix (orphan rows are gate failures)
2. **Outcomes → Goals → Objectives → Measures** — the ladder (gate G1)
3. **Drivers** — typed Inherent / Desired / Imposed; internal / external
4. **Assumptions** — listed, never implicit; each with acceptor + re-test trigger
5. **Case For / Case Against** — both populated (gate G2)
6. **Impact Factors** — direction + magnitude + source
7. **Strategic Themes → Capabilities → Courses of Action → Resources** — each theme realizes ≥ 1 capability (gate G3)
8. **Traceability** — links to STKE / SOBC / STRAT / ROAD / BPCM / REQ / ADR + external references
9. **Mermaid Mindmap** — companion block, **append-only** on regeneration

**Auto-populate Document Control fields** exactly as the archimate command does (`[PROJECT_ID]`, `[VERSION]`, `[DATE]`, `[COMMAND]` = "arckit.bmm"; user-provided fields; `[PENDING]` for reviewer/approver/distribution). Populate the Revision History row and the Generation Metadata footer (includes the model).

## Step 4: Generate the Base Views [A2] [A3]

Unless the selected scope omits a tier (see Step 1b skip rules), emit two sequenced ArchiMate views under `projects/{p}/diagrams/`:

- **[A2] Motivation view** — stakeholders → outcomes; driver/constraint influence edges (`Rel_Influence`, labelled "drives" / "constrains" / "expects"); goal → outcome realization (`Rel_Realization`, concrete → abstract).
- **[A3] Strategy/Capability view** — themes (stereotyped) → capability nesting (`Rel_Composition`, whole → part, BPCM idiom, optional L3) → courses of action / resources (`Rel_Assignment`); realization into Business/Application tiers.

**Generate the document IDs** (ARCH is a multi-instance type; BMM views sequence into the **shared ARCH sequence** under `diagrams/`). Run the bundled helper:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/bash/generate-document-id.sh" \
     {P} ARCH --next-num "{project_path}/diagrams"
```

One call per view. **BMM views NEVER renumber or rewrite existing ARCH documents** (gate G5) — they only ever take the next free sequence number.

### Self-contained SVG delivery [D*]

Every view carries its PlantUML source inline and is rendered offline with the pinned build (see § Offline Self-Contained SVG Rendering in the archimate reference):

```sh
java -jar plantuml-1.2026.8.jar -tsvg -checkonly some-view.puml   # validate
java -jar plantuml-1.2026.8.jar -tsvg some-view.puml               # emit some-view.svg
```

The `.svg` is the **only new rendered file** — no new `.puml` or `.md` artefacts beyond the sequenced ARCH documents themselves. Verify self-containment before delivery: no `http(s)` URL in the `.svg` beyond the W3C `2000/svg` / `1999/xlink` namespace declarations; `xlink:href` limited to local `#anchor`s.

## Step 5: Optional Companions [O1–O4]

For each menu item selected in Question 2, generate the companion — each as its own sequenced ARCH document in `diagrams/` (same `--next-num` helper, never renumbering) or, for [O4], as an append-only extension of the mindmap block in [A1]:

- **[O1] Goal–Objective–Measure ladder view** — motivation overlay; Objective/Measure stereotyped per § BMM Projection, with a `legend` block.
- **[O2] Case & assumptions overlay** — Case For / Case Against + Assumptions + Impact Factors as a `Rel_Influence` structure; the narrative stays in [A1] (a diagram never substitutes for the case text).
- **[O3] Alignment / traceability view** — goal/objective → strategic theme → capability (BPCM cross-reference) → ROAD milestone → REQ → ADR realization chain; split at natural boundaries when the view would exceed 12 elements.
- **[O4] Mermaid mindmap companion** — extend the section-9 block in [A1]; byte-preserving append (extend the tree, never rewrite existing branches).

## Step 6: BMM Quality Gates (G1–G5)

After generating the model and views, evaluate against the criteria below. Report the results as part of the output:

| # | Gate | Target | Result | Status |
|---|------|--------|--------|--------|
| G1 | Ladder completeness | Every outcome ≥ 1 goal; every goal ≥ 1 objective; every objective ≥ 1 measure | {assessment} | {PASS/FAIL} |
| G2 | No empty quadrants | Case For, Case Against, Assumptions, Impact Factors all populated (placeholder text fails) | {assessment} | {PASS/FAIL} |
| G3 | Theme realization | Every strategic theme realizes ≥ 1 capability (in-model link or BPCM cross-reference) | {assessment} | {PASS/FAIL} |
| G4 | View conformance | Pinned include line; ≤ 12 elements/layer; split-never-drop; realization concrete → abstract; single-tier stereotyping; legend for any custom notation | {assessment} | {PASS/FAIL} |
| G5 | Sequence continuity | New views take the next free ARCH sequence number; no existing ARCH document renumbered or rewritten | {assessment} | {PASS/FAIL} |

### Remediation by Gate

| Failed gate | Remediation steps |
|-------------|-------------------|
| G1 (Ladder) | Add the missing objective / measure; if a goal genuinely has no objective, promote it to outcome-level and re-draw the ladder edge |
| G2 (Quadrants) | Populate the empty quadrant from context (SOBC cases, RISK factors); "TBC", "—", and empty bullets fail — write real content or an explicit *not applicable* with rationale |
| G3 (Themes) | Link the theme to a capability (in-model or BPCM cross-reference); a theme with no capability is a slogan, not a theme — refine or drop it |
| G4 (Views) | Restore the pinned include line; split crowded layers at natural boundaries; flip mis-directed realization edges; add the `legend` block for stereotyped elements |
| G5 (Sequence) | Re-run the helper with `--next-num`; verify no existing `diagrams/ARC-*-ARCH-*.md` file was touched |

### Iterative Review Loop

1. Generate the model and views
2. Evaluate all five gates in the table above
3. If any gate fails: apply the corresponding remediation, regenerate, re-evaluate all five gates
4. Repeat up to **3 iterations**
5. If gates still fail after 3 iterations, document the accepted trade-offs in the artefact and proceed

## Step 7: Integration with ArcKit Workflow

- **Before**: if STKE or PRIN is missing, the STOP rules in Step 1 apply — do not generate a draft model from raw requirements.
- **After**:
  - Record the new `BMM` artefact (and each emitted ARCH view) in the project manifest (the manifest hook does this on write).
  - Handoffs: **strategy** — STRAT consumes the BMM Strategic Themes into the strategy narrative; **roadmap** — ROAD sequencing from Courses of Action; **sobc** — 5-case ↔ BMM Case section mapping (UK-regime Green Book only — for non-UK projects the handoff is informational, never jurisdictional); **archimate** — a Motivation overlay on layer views reuses the BMM elements emitted here.

## Antipatterns (never emit)

- A BMM model with no Case Against — an uncritical model is a memo, not a case
- Implied assumptions (assumptions must be rows in section 4, never prose-only)
- A theme without a capability realization (gate G3)
- Stereotypes without a `legend` block, or 4.0 elements faked as native macros
- Renumbering or rewriting existing ARCH documents (gate G5)
- Letting a view carry case narrative — the narrative lives in [A1]; views are projections
