# slash-commands Specification

## Purpose
The ArcKit Claude Code plugin exposes 75 slash commands named `/arckit:<name>` from `plugins/arckit-claude/commands/*.md`. This spec captures the command frontmatter contract, doc-type declaration rule, lifecycle status, execution contract, artifact naming, and artifact-stamping conventions that govern how a command runs and what it produces.

## Requirements

### Requirement: Commands Are Exposed From Markdown Files
The system SHALL expose every file in `plugins/arckit-claude/commands/` as a slash command `/arckit:<name>` where `<name>` is the filename stem, and the YAML frontmatter at the top of the file SHALL be the source of truth for command metadata.

#### Scenario: 75 commands ship
- **WHEN** the `arckit` plugin loads from `plugins/arckit-claude/`
- **THEN** all 75 files in `commands/` are available as `/arckit:<name>` commands

#### Scenario: command set is stable
- **WHEN** the baseline is counted
- **THEN** 75 `.md` command files exist in `plugins/arckit-claude/commands/`, each carrying the `description` and `doc-type` fields

#### Scenario: frontmatter is authoritative
- **WHEN** a command body and its frontmatter disagree about a field
- **THEN** the frontmatter value governs (e.g. `effort`, `doc-type`) and the body is treated as prose instructions

### Requirement: Frontmatter Fields Have Defined Semantics
The system SHALL interpret the following frontmatter fields on command files: `description` (required, human summary shown in the command list), `doc-type` (required — a single registered code, a `[A, B]` list when one command writes more than one governed artefact, or `none` when it writes no `ARC-*` artefact), `effort` (optional session-effort override: `low` | `medium` | `high` | `xhigh` | `max`), `keep-coding-instructions: true` (persist command body across `/compact`), `disallowed-tools` (optional tool denylist while the command is active; accepted but not yet used by any shipped command), and `handoffs` (optional list of `{command, description?, condition?}` entries for suggested next steps).

#### Scenario: required fields present
- **WHEN** a command file ships without a `description` or without a `doc-type`
- **THEN** the command violates the documented contract (`description` and `doc-type` are both required)

#### Scenario: effort override
- **WHEN** a command declares `effort: max` (18 commands, e.g. `/arckit:sobc`, `/arckit:research`, `/arckit:framework`, the `wardley.*` family)
- **THEN** the session runs that command at `max` effort on models that support it; on models without `xhigh`/`max` support, the highest supported level at or below the declared level applies

#### Scenario: field usage distributions
- **WHEN** the shipped command set is inspected
- **THEN** `description` and `doc-type` appear on every one of the 75 commands; `effort` is declared on 66 (43 `high`, 18 `max`, 3 `low`, 2 `medium`); `keep-coding-instructions: true` on 14; `handoffs:` on 33; and no command currently uses `disallowed-tools`

#### Scenario: keep-coding-instructions
- **WHEN** a long-running command (e.g. `/arckit:requirements`, `/arckit:sobc`, `/arckit:framework`, `/arckit:datascout`) declares `keep-coding-instructions: true`
- **THEN** the command body is re-injected after `/compact` or auto-compaction instead of being lost in the summary

#### Scenario: handoffs render for non-Claude targets
- **WHEN** the converter generates non-Claude targets (Codex, Gemini, OpenCode, Copilot) from a command with `handoffs:`
- **THEN** the entries are rendered as a "Suggested Next Steps" section in the generated output, while Claude keeps the structured list in frontmatter

### Requirement: Doc-Type Declaration Names What The Command Writes
The system SHALL require every command to declare in `doc-type:` the doc-type code(s) that running the command produces — a single code (`doc-type: REQ`), a `[A, B]` list when one command writes more than one governed artefact, or `none` when it writes no `ARC-*` artefact (e.g. `/arckit:search`, `/arckit:health`, `/arckit:pages`, `/arckit:build`, `/arckit:start`, `/arckit:init`). The declaration SHALL sit on the command even when the command delegates to an agent that holds the Write call (e.g. `/arckit:framework` declares `FWRK` and delegates to the `arckit-framework` agent).

#### Scenario: command writing one artefact
- **WHEN** `/arckit:requirements` runs and writes `projects/001-*/ARC-001-REQ-v1.0.md`
- **THEN** its frontmatter declares `doc-type: REQ`

#### Scenario: delegating command still declares its output
- **WHEN** `/arckit:framework` runs and the `arckit-framework` agent writes the FWRK overview document
- **THEN** the command's frontmatter still declares `doc-type: FWRK`, because the declaration names what running the command produces

#### Scenario: non-artifact command
- **WHEN** `/arckit:search`, `/arckit:health`, `/arckit:pages`, or `/arckit:build` runs
- **THEN** its frontmatter declares `doc-type: none` because it produces no `ARC-*` artefact (diagnostics, dashboard, or orchestration only)

#### Scenario: recipe target parity
- **WHEN** `scripts/check-doc-type-registry.py` runs in CI
- **THEN** every recipe `output.type` equals the `doc-type:` declared by the command that produces it, and every `ARC-*-CODE-v` filename referenced in a command or agent body resolves to a code in `DOC_TYPES`

### Requirement: Lifecycle Status Per Command
The system SHALL assign every command a lifecycle status — `live`, `beta`, `alpha`, `experimental`, or `community` — recorded in `plugins/arckit-claude/config/guide-groups.mjs` and written to `docs/manifest.json` by the `sync-guides` hook so the dashboard, llms.txt, and generated extensions display the badge without browser-side filename heuristics.

#### Scenario: status is centralised
- **WHEN** `sync-guides.mjs` runs for `/arckit:pages`
- **THEN** each top-level guide in the manifest carries `category`, `section`, optional `pack`, and `status` sourced from `guide-groups.mjs`, not from the command file

#### Scenario: mixed maturity coexist
- **WHEN** the plugin loads
- **THEN** `live` commands (e.g. `requirements`, `stakeholders`, `sobc`, `principles`, `data-model`, `diagram`, `risk`, `traceability`), `beta` commands (e.g. `research`, `adr`, `backlog`, `roadmap`, `strategy`), `alpha` commands (e.g. `data-mesh-contract`), and `experimental` commands (e.g. `init`, `datascout`, `gov-reuse`, `gov-code-search`, `gov-landscape`, `grants`, `dfd`, `framework`, `platform-design`, the `wardley.*` family) are all present with their respective badges

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

### Requirement: Artifact Naming And Requirement ID Conventions
The system SHALL name every generated artefact `ARC-{PID}-{TYPE}[-{SEQ}]-v{MAJOR}.{MINOR}.md` where `PID` is the zero-padded 3-digit project number, `TYPE` is the registered doc-type code, `SEQ` (when present) is a zero-padded sequence for multi-instance types (e.g. `ARC-001-ADR-001-v1.0.md`), and `VERSION` is `vMAJOR.MINOR`. Requirement IDs inside a requirements artefact SHALL use the prefixes `BR-xxx` (Business), `FR-xxx` (Functional), `NFR-xxx` (Non-Functional, with sub-tags such as `NFR-P`, `NFR-SEC`), `INT-xxx` (Integration), and `DR-xxx` (Data); the numeric suffix is 1–3 digits so both `BR-1` and `BR-001` are valid.

#### Scenario: single-instance artefact
- **WHEN** `/arckit:requirements` writes its artefact for project 001
- **THEN** the file is `projects/001-*/ARC-001-REQ-v1.0.md`

#### Scenario: multi-instance artefact
- **WHEN** `/arckit:adr` writes its first decision for project 001
- **THEN** the file is `projects/001-*/decisions/ARC-001-ADR-001-v1.0.md` (subdirectory + sequence)

#### Scenario: requirement ID prefixes
- **WHEN** a requirements artefact lists its requirements
- **THEN** each carries one of the prefixes `BR-`, `FR-`, `NFR-`, `INT-`, `DR-` followed by a 1–3 digit number

### Requirement: Document Control And Build Provenance On Every Artefact
The system SHALL require every generated artefact to begin with a **Document Control** table (14 standard fields resolved by `templates/_partials/RENDERING.md` — the partial selected by `governance_framework`/`classification_scheme`/regime, with `${user_config.organisation_name}` and `${user_config.default_classification}` substituted) followed by a **Revision History** table, and to end with the standard human-authored footer (`Generated by`, `Generated on`, `ArcKit Version`, `Project`, `AI Model`). A second machine-stamped `## Build Provenance` block SHALL be appended automatically by the `provenance-stamp.mjs` PostToolUse hook for artefacts under `projects/**` carrying fields the model cannot authoritatively self-report (build context from `.arckit/state.json`, requested effort from command frontmatter, effective effort after silent-downgrade).

#### Scenario: Document Control is partial-resolved
- **WHEN** a command reads its template and encounters the `<!-- DOC-CONTROL-HEADER -->` marker
- **THEN** it reads `${CLAUDE_PLUGIN_ROOT}/templates/_partials/RENDERING.md`, selects the partial for the current regime/user-config, inlines it at the marker, and does not hand-write the 14 standard fields

#### Scenario: standard footer present
- **WHEN** any template-driven artefact is written
- **THEN** it ends with the `Generated by / Generated on / ArcKit Version / Project / AI Model` footer block

#### Scenario: provenance is machine-stamped
- **WHEN** the `Write` or `Edit` tool writes an `ARC-NNN-*-vN.N.md` file under `projects/`
- **THEN** `provenance-stamp.mjs` appends (or idempotently replaces) a `## Build Provenance` block delimited by HTML comments; re-running on the same file does not duplicate the block

### Requirement: Citation Traceability For External Evidence
The system SHALL require that when a command reads external material — files under `external/`, `policies/`, `vendors/`, MCP server queries, or web pages fetched at runtime — it follow `${CLAUDE_PLUGIN_ROOT}/references/citation-instructions.md`: place inline citation markers (`[DOC_ID-CN]` where `DOC_ID` is the source's derived ID and `CN` is a content index) next to the findings they inform, and populate the template's **External References** (or Document Register / Citations / Unreferenced Documents) section with the full source list. WebSearch (search-only, no fetch) SHALL NOT produce citations.

#### Scenario: external document cited
- **WHEN** `/arckit:requirements` extracts acceptance criteria from `projects/001-*/external/privacy-policy.pdf`
- **THEN** it places an inline marker such as `[PP-C1]` next to the relevant requirement and lists `PP` (privacy-policy.pdf) in the External References section

#### Scenario: MCP query cited
- **WHEN** a research reader issues a query to the AWS Knowledge MCP
- **THEN** the source ID uses the fixed per-server prefix plus a sequential query index (one Source ID per unique query, not per call), and the writer passes the `citation_id` → `fetched_from_url` chain through in its payload

#### Scenario: search-only not cited
- **WHEN** a command runs `WebSearch` but does not fetch any URL
- **THEN** no citation markers are produced from that search

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
