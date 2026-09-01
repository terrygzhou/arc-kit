# oaa-intake Delta — oaa-intake

## ADDED Requirements

### Requirement: OAA Intake Hard-Blocks On MANDATORY Prerequisites (TOGAF-Consistent)
Every Open Agile Architecture (`oaa`) overlay command — `oaa-adm-lite`, `product-architecture`, `agile-governance`, `agile-security`, `agile-strategy` — SHALL declare a **MANDATORY** prerequisite tier grounded in the `000-global` `PRIN` (Architecture Principles) artefact, with a "If missing: STOP" instruction, mirroring `togaf/adm`'s `adm-preliminary` hard gate. When the MANDATORY `PRIN` artefact is missing, the OAA command SHALL stop and prompt the user to generate it first (run `/arckit:principles`); the missing MANDATORY prerequisite artefact is a hard dependency and SHALL never be rendered as `TBD`. All other OAA prerequisites (e.g. `ADMP`, `OAPR`, `OASTR`, `OASEC`) SHALL remain **RECOMMENDED** (noted when missing, not blocking). This hard gate applies to prerequisite *artefacts*; interview *inputs* the user skips still render as quoted `TBD` markers (the soft-gate behaviour).

#### Scenario: Missing PRIN stops the OAA command
- **WHEN** the user runs `/arckit:product-architecture` and no `ARC-000-PRIN-v[N].md` exists in `000-global`
- **THEN** the command stops and asks the user to run `/arckit:principles` first; it does not render `ARC-{P}-OAPR-v1.0.md` and does not render `PRIN` as `TBD`

#### Scenario: OAA and ADM stop identically on missing PRIN
- **WHEN** the same missing-`PRIN` situation is presented to a `togaf/adm` command and to an `oaa` command
- **THEN** both stop and prompt for `PRIN` first — OAA now has the same hard-gate rigour as ADM at the foundational precondition

#### Scenario: Skipped OAA interview input still renders as quoted TBD
- **WHEN** `PRIN` exists and the user skips the oaa-adm-lite "Data classification" interview input
- **THEN** `ARC-{P}-OAAL-v1.0.md` renders `TBD — "What is the data classification / sensitivity level of the workloads in scope?"` and the summary lists it under unresolved fields without blocking

#### Scenario: OAA prerequisites other than PRIN stay soft
- **WHEN** the user runs `/arckit:agile-governance` and no `ARC-{P}-OAPR-v[N].md` (product architecture) exists
- **THEN** the command notes the missing product architecture in its summary and proceeds; only a missing `PRIN` is a hard stop

#### Scenario: Bulk build respects the OAA hard gate
- **WHEN** the `arckit-build` harness runs an OAA target on a project that has no `PRIN`
- **THEN** that target fails or is skipped with a prompt to generate `PRIN` first (TOGAF-consistent), rather than rendering a `TBD`-filled OAA artefact

### Requirement: OAA Interview Adds No Diagram Or Output Mandate
For `oaa` overlay commands the intake interview SHALL NOT introduce any diagram or output demand the OAA template does not already ask for. The interview collects only the inputs the effective OAA template already requests; OAA is outcomes-over-outputs, so the interview SHALL add no rendering requirement. The MANDATORY prerequisite hard gate is a *dependency* on an upstream artefact and is NOT a diagram or output demand, so it does not conflict with this requirement. This SHALL be preserved in both the generic shared block's §8 and its OAA sub-plugin copy.

#### Scenario: OAA interview never mandates a diagram
- **WHEN** the user runs `/arckit:agile-strategy` and answers every intake question
- **THEN** the interview asks only for the inputs the `agile-strategy` template already requests and does not require the user to commit to a diagram or output the template does not ask for

#### Scenario: Hard gate does not conflict with the tone guard
- **WHEN** `/arckit:oaa-adm-lite` stops because `PRIN` is missing
- **THEN** the stop is because of a prerequisite artefact, and the command has not demanded any diagram or output beyond the OAA template's own requests

#### Scenario: Tone guard survives the OAA sub-plugin copy
- **WHEN** the `oaa` sub-plugin — which resolves `${CLAUDE_PLUGIN_ROOT}` to its own runtime root — runs `/arckit:product-architecture`
- **THEN** it reads the OAA sub-plugin's `references/intake-instructions.md`, which still contains §8 (the OAA tone guard), so the interview still adds no diagram/output mandate

### Requirement: OAA Sub-Plugin Ships The Shared Intake Block With §8
The OAA sub-plugin's copy of the shared interview block at `plugins/arckit-claude/plugins/oaa/references/intake-instructions.md` SHALL be byte-identical to the root shared block at `plugins/arckit-claude/references/intake-instructions.md` AND SHALL retain §8 (the OAA tone guard). Each of the five OAA command bodies SHALL contain the "Run the intake interview" step positioned immediately before its template-read step, AND SHALL carry the MANDATORY `PRIN` prerequisite tier with a STOP instruction. A drift that rewrites or drops §8 in the OAA copy is a spec violation, not merely a byte difference.

#### Scenario: OAA copy is byte-identical and keeps §8
- **WHEN** the test compares `plugins/arckit-claude/plugins/oaa/references/intake-instructions.md` to the root `references/intake-instructions.md`
- **THEN** the two files are byte-identical and both contain an "## 8. OAA tone guard" section

#### Scenario: Every OAA command carries the intake step and the MANDATORY PRIN gate
- **WHEN** the test scans the five OAA command bodies (in both `plugins/arckit-oaa/commands/` and `plugins/arckit-claude/plugins/oaa/commands/`)
- **THEN** each contains the intake-interview step immediately before its "Read the template" step, and a `**MANDATORY**` tier naming `PRIN` with an "If missing: STOP" instruction

### Requirement: OAA Per-Command Interview Inputs Track Each OAA Template
The intake interview for each OAA command SHALL be derived from that command's own effective OAA template, and the shipped default templates SHALL surface the following reference input domains so the interview covers them:
- `oaa-adm-lite`: Sprint-0 outcome dimensions (jurisdiction, AI workload type, use cases, data classification, user count, latency requirement, budget, timeline, infrastructure, stakeholders, success criteria, regulatory controls, risk profile, deployment topology) plus Document Control.
- `product-architecture`: mission, outcome (value / outcome / experience / adoption), principles, team, backlog epics / ADRs, roadmap waves, embedded compliance, Document Control owner.
- `agile-governance`: distributed roles, sprint-review checklist, debt categories, quarterly health rubric, continuous compliance, Document Control owner.
- `agile-security`: the four pillars (embedded security stories, risk-based scan thresholds, compliance-as-code gates, sprint-gate validation), security-metric KPIs, Document Control framework / prerequisites.
- `agile-strategy`: digital dimension (tech / product / operating model), agile dimension (org / cultural / team), O-AA axioms, resilience mapping, wave plan, Document Control scope / owner.

The MANDATORY `PRIN` artefact is a hard dependency, not an interview input, and is not part of these reference input domains. A fully-prefilled OAA template SHALL trigger zero interview questions; the reference domains are asserted against the shipped defaults, and a custom template changes the questions.

#### Scenario: OAA interview questions come from the OAA template
- **WHEN** the user runs `/arckit:oaa-adm-lite` on a project where `PRIN` exists
- **THEN** the interview questions are derived from the `oaa-adm-lite` template's sections (Sprint-0 outcome dimensions + Document Control), never from a shared generic OAA question list

#### Scenario: Fully-prefilled OAA template asks nothing
- **WHEN** every OAA input is resolvable from existing `projects/` artefacts, saved `.arckit/intake/` answers, or `user_config`
- **THEN** the OAA command renders its artefact without asking a single question

### Requirement: OAA Sprint-0 Prefill Seeds The Intake Store
The OAA Sprint-0 outcome dimensions SHALL be valid prefill keys in the project intake store so that a first OAA command after onboarding starts warm. Onboarding answers covering jurisdiction, AI workload type, data classification, user count, latency, budget, timeline, infrastructure, stakeholders, success criteria, regulatory controls, risk profile, and deployment topology SHALL prefill OAA interview inputs where they match, following the generic precedence (existing artefacts > per-command saved intake > onboarding `shared.json` > `user_config`).

#### Scenario: Onboarding seed prefills an OAA command
- **WHEN** the user completes onboarding that records "AI workload type: LLM inference" and "data classification: confidential", then runs `/arckit:oaa-adm-lite` (with `PRIN` present)
- **THEN** the oaa-adm-lite interview prefills those two inputs from `.arckit/intake/shared.json` and does not re-ask them

### Requirement: Standard-Aligned Interview Coverage (TOGAF + OAA)
The OAA intake interview SHALL derive its questions not only from the effective template's sections but also from a **canonical TOGAF/OAA discovery-dimension checklist**, so that every OAA artefact is grounded in the standard's core concerns even when a particular template section is thin or absent. The checklist is:

| # | Dimension | TOGAF source | OAA source |
|---|---|---|---|
| D1 | Business vision & strategy | ADM-P / Phase A | OAA strategic intent |
| D2 | Business capabilities | Phase B / capability map | OAA capability map |
| D3 | Stakeholders & goals | ADM-A / stakeholder mgmt | OAA engagement |
| D4 | Constraints & drivers (jurisdiction, regulatory, budget, timeline) | ADM-A drivers/constraints | OAA constraints |
| D5 | Current-state (As-Is) architecture | Phase B/C/D "current" | OAA digital-dimension `current_state` |
| D6 | Technology landscape (current + target) | Phase C / D | OAA enabling technologies / infrastructure |
| D7 | Data architecture & classification | Phase C (data) | OAA data principles |
| D8 | Pain points, gaps & risks | Phase E gap analysis | OAA `capability_gaps` / resilience |
| D9 | OAA outcome dimensions (Value / Outcome / Experience / Adoption) | — | OAA outcome model |
| D10 | OAA axioms alignment | — | O-AA axioms |

A canonical dimension already resolvable by prefill (existing artefacts, `.arckit/intake/`, `user_config`, `shared.json`) SHALL NOT be re-asked; a dimension with no source SHALL be asked as a grouped, skippable question (rendering `TBD` if skipped). This checklist is a **coverage floor in addition to** the template-derived questions, and SHALL NOT add any diagram or output mandate (OAA tone guard).

#### Scenario: Missing current-state / pain points is still asked
- **WHEN** the user runs `/arckit:product-architecture`, whose template has no explicit "current-state" or "pain points" section
- **THEN** the interview still asks the D5 (current-state) and D8 (pain points / gaps) dimensions as grouped questions, because they are canonical TOGAF/OAA discovery concerns

#### Scenario: Prefilled canonical dimension is not re-asked
- **WHEN** business capabilities (D2) are already documented by a prior capability-map artefact in `projects/`
- **THEN** the interview prefills D2 from that artefact and does not re-ask it

#### Scenario: Standards coverage adds no diagram/output demand
- **WHEN** the interview asks the D5–D8 discovery dimensions for `/arckit:agile-strategy`
- **THEN** it asks only for the information (current/target state, technology, pain points) and does not require the user to commit to a diagram or output the OAA template does not request
