# slash-commands Delta — intake-ask-always

## MODIFIED Requirements

### Requirement: Template-Driven Intake Interview Before Artefact Generation
Before rendering its artefact, every artefact-producing command (core or bundled overlay) SHALL run a template-driven intake interview: (1) resolve the *effective* template (`.arckit/templates-custom/{name}-template.{ext}` first, then the shipped default), (2) derive the inputs the artefact needs from that template's sections, its Document Control fields not resolvable from `user_config`, and the command's MANDATORY prerequisite inputs, (3) prefill each input from, in order, existing artefacts already in `projects/`, previously saved intake answers, then `user_config`, and (4) put **every** derived input to the user for their input, one question at a time — prefilled where available so the user can confirm or override the value — with each question **optional** and skippable. Answers SHALL be persisted to `projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json` (hand-editable, never rendered into artefacts themselves). A skipped question SHALL be rendered in the artefact as an explicit `TBD` marker that quotes the interview question, and the command's user-facing summary SHALL list all unresolved fields. The interview SHALL surface **every** derived input (prefilled where available) rather than only the unknown ones: a fully-prefilled template still presents each prefilled value for the user to confirm or override, and no question is mandatory. Interview depth is bounded only by the set of *derived* inputs — the template remains the ceiling; the interview SHALL NOT invent inputs the template does not ask for. Upstream artefact dependencies (e.g. SOBC before stakeholders goals exist) are governed by the existing prerequisite gating, not by the interview.

#### Scenario: Fresh project, stakeholders command interviews before rendering
- **WHEN** the user runs `/arckit:stakeholders` on a project with no existing artefacts
- **THEN** the command reads the effective stakeholder-drivers template, derives its required inputs from the template sections, and puts each derived input to the user one at a time (each optional and skippable) before generating `ARC-NNN-STKE-v1.0.md`

#### Scenario: Overlay commands interview against their own templates
- **WHEN** an overlay command runs — e.g. `togaf/adm`'s `data-architecture`, `oaa`'s `product-architecture`, or `agent/architecture`'s `agent-security`
- **THEN** its interview questions are derived from that overlay command's own effective template (data flows/ownership; product components and value; threat surfaces respectively), never from a shared generic question set

#### Scenario: Overlay sub-plugins resolve the shared interview block from their own root
- **WHEN** an overlay sub-plugin (`oaa`, `togaf/adm`, or `agent/architecture`) — which at runtime has its own `${CLAUDE_PLUGIN_ROOT}` distinct from the `arckit` root — runs an artefact-producing command
- **THEN** the command's reference to `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md` resolves to a copy of the shared block shipped inside that sub-plugin (kept byte-identical to the root `references/intake-instructions.md`), so the model can read and run the interview instead of silently skipping it

#### Scenario: Custom template override changes the questions
- **WHEN** `.arckit/templates-custom/{name}-template.md` exists and its sections differ from the shipped default
- **THEN** the intake interview derives its questions from the custom template, not the default

#### Scenario: Fully-prefilled template still surfaces each value for confirmation
- **WHEN** every derived input for an artefact can be prefilled from project artefacts, saved intake, or `user_config`
- **THEN** the interview still presents each prefilled value to the user to confirm or override, one at a time; no prefilled value passes silently, and the user may confirm it or skip the question (which renders as a `TBD` marker)

#### Scenario: Soft gate — skipped inputs become quoted TBD markers
- **WHEN** the user skips any intake question (whether the input was prefilled or unknown)
- **THEN** the artefact renders that field as `TBD` with the interview question quoted next to it, and the command's summary lists it under unresolved fields; the command does not block or re-prompt beyond offering the skip

#### Scenario: Answers persist and are not re-asked
- **WHEN** the same command is re-run in the same or a later session and `projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json` contains an answer for an input
- **THEN** the saved answer is prefilled and offered for confirmation or override without being re-asked as a blank; editing the file changes the artefact on the next run

#### Scenario: No re-asking of inputs already present in the project
- **WHEN** an intake input is already determinable from existing `projects/` artefacts (e.g. stakeholders documented by a prior run)
- **THEN** the command prefills it from those artefacts and offers the prefilled value to the user to confirm or override rather than re-deriving it as a blank question

#### Scenario: Bulk build never interviews
- **WHEN** the `arckit-build` harness dispatches a target that is an artefact-producing command
- **THEN** the subagent uses saved intake answers where available and renders `TBD` for everything unknown — no interactive questions are asked during a build
