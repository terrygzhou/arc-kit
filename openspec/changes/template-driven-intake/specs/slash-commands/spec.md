# slash-commands Delta — template-driven-intake

## ADDED Requirements

### Requirement: Template-Driven Intake Interview Before Artefact Generation
Before rendering its artefact, every artefact-producing command (core or bundled overlay) SHALL run a template-driven intake interview: (1) resolve the *effective* template (`.arckit/templates-custom/{name}-template.{ext}` first, then the shipped default), (2) derive the inputs the artefact needs from that template's sections, its Document Control fields not resolvable from `user_config`, and the command's MANDATORY prerequisite inputs, (3) prefill each input from, in order, existing artefacts already in `projects/`, previously saved intake answers, then `user_config`, and (4) ask the user only the inputs still unknown, one question at a time, each with an explicit skip option. Answers SHALL be persisted to `projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json` (hand-editable, never rendered into artefacts themselves). Skipped MANDATORY inputs SHALL be rendered in the artefact as explicit `TBD` markers that quote the interview question, and the command's user-facing summary SHALL list all unresolved fields. Interview depth SHALL be proportional to the gap: a fully-prefilled template SHALL NOT trigger a single question. Upstream artefact dependencies (e.g. SOBC before stakeholders goals exist) are governed by the existing prerequisite gating, not by the interview.

#### Scenario: Fresh project, stakeholders command interviews before rendering
- **WHEN** the user runs `/arckit:stakeholders` on a project with no existing artefacts
- **THEN** the command reads the effective stakeholder-drivers template, derives its required inputs from the template sections, and asks the corresponding questions one at a time (each skippable) before generating `ARC-NNN-STKE-v1.0.md`

#### Scenario: Overlay commands interview against their own templates
- **WHEN** an overlay command runs — e.g. `togaf/adm`'s `data-architecture`, `oaa`'s `product-architecture`, or `agent/architecture`'s `agent-security`
- **THEN** its interview questions are derived from that overlay command's own effective template (data flows/ownership; product components and value; threat surfaces respectively), never from a shared generic question set

#### Scenario: Custom template override changes the questions
- **WHEN** `.arckit/templates-custom/{name}-template.md` exists and its sections differ from the shipped default
- **THEN** the intake interview derives its questions from the custom template, not the default

#### Scenario: Soft gate — skipped inputs become quoted TBD markers
- **WHEN** the user skips a MANDATORY intake question
- **THEN** the artefact renders that field as `TBD` with the interview question quoted next to it, and the command's summary lists it under unresolved fields; the command does not block or re-prompt beyond offering the skip

#### Scenario: Answers persist and are not re-asked
- **WHEN** the same command is re-run in the same or a later session and `projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json` contains an answer for an input
- **THEN** the saved answer is used without re-asking; editing the file changes the artefact on the next run

#### Scenario: No re-asking of inputs already present in the project
- **WHEN** an intake input is already determinable from existing `projects/` artefacts (e.g. stakeholders documented by a prior run)
- **THEN** the command prefills it from those artefacts and does not ask about it

#### Scenario: Bulk build never interviews
- **WHEN** the `arckit-build` harness dispatches a target that is an artefact-producing command
- **THEN** the subagent uses saved intake answers where available and renders `TBD` for everything unknown — no interactive questions are asked during a build

## MODIFIED Requirements

### Requirement: Command Execution Contract
The system SHALL make every artefact-producing command follow the same execution contract: check prerequisites (MANDATORY inputs are collected via the Template-Driven Intake Interview before generation — an unanswered MANDATORY input renders as an explicit `TBD` marker quoting its interview question and is flagged in the summary, never merely warned; RECOMMENDED inputs are noted when missing; OPTIONAL inputs are skipped silently), resolve the target project via the ArcKit Project Context hook or `scripts/bash/create-project.sh --json` (creating `projects/{NNN}-{slug}/` when no project matches), read the template from `.arckit/templates-custom/` first then fall back to `${CLAUDE_PLUGIN_ROOT}/templates/`, write large output with the `Write` tool to stay under the 32K output-token limit, show the user only a summary (not the full document), delegate heavy research (>10 WebSearch/WebFetch/MCP calls) to agents so that context is isolated, and declare `handoffs:` for the logical next steps.

#### Scenario: prerequisite gating
- **WHEN** `/arckit:sobc` runs and no `ARC-*-STKE-*.md` exists in the target project
- **THEN** the command stops and tells the user to run `/arckit:stakeholders` first, because every SOBC benefit MUST trace to a stakeholder goal

#### Scenario: project resolution
- **WHEN** a command is invoked for a project that does not exist yet
- **THEN** the command creates `projects/{NNN}-{slug}/README.md` and `projects/{NNN}-{slug}/external/README.md` with the Write tool and sets `PROJECT_ID`/`PROJECT_PATH`, or (in commands that list it) invokes `create-project.sh --json --force --name "<name>"` to obtain the path

#### Scenario: template override precedence
- **WHEN** `.arckit/templates-custom/<name>-template.md` exists in the project root
- **THEN** the command reads the user's customized template; otherwise it reads `${CLAUDE_PLUGIN_ROOT}/templates/<name>-template.md`

#### Scenario: MANDATORY inputs are collected, not just warned
- **WHEN** a command's effective template contains sections requiring inputs that are unavailable from project artefacts, saved intake, or `user_config`
- **THEN** the command asks the user for them (one at a time, each skippable) before generation, persists the answers, and renders any skipped input as a quoted `TBD` marker listed in the summary

#### Scenario: Write-tool isolation for large output
- **WHEN** a command generates a document longer than the model's 32K output-token budget
- **THEN** the command writes the document with the `Write` tool and shows the user only a summary (artefact path, key stats, next steps)

#### Scenario: heavy research is delegated
- **WHEN** `/arckit:research`, `/arckit:datascout`, `/arckit:tenders`, `/arckit:competitors`, `/arckit:grants`, or a `gov-*` command needs to gather evidence from the web or an MCP server
- **THEN** the slash command (orchestrator tier) dispatches a reader subagent via the `Agent` tool, validates the reader's JSON against the schema, scores deterministically, and dispatches a writer subagent to render the artefact — the main thread never calls `WebSearch`/`WebFetch` directly
