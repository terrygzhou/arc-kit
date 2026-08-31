# research-agents Specification

## Purpose
The ArcKit Claude Code plugin (`plugins/arckit-claude/`) exposes 29 agents under `plugins/arckit-claude/agents/` — 10 single-tier agents and 19 reader/writer subagents — that isolate heavy web/MCP research from the main conversation. This spec captures the agent frontmatter contract, the tool-allowlist hardening, the three-tier orchestrator pattern, the MCP tool naming rule, and the converter behavior that preserves the agents for non-Claude targets.

## Requirements

### Requirement: Agent Population Is 29 Agents Across Two Tiers
The system SHALL register exactly 29 agents in `plugins/arckit-claude/agents/`: 10 single-tier agents (`arckit-research`, `arckit-datascout`, `arckit-aws-research`, `arckit-azure-research`, `arckit-gcp-research`, `arckit-framework`, `arckit-gov-reuse`, `arckit-gov-code-search`, `arckit-gov-landscape`, `arckit-grants`) and 19 reader/writer subagents carrying `subagent: true` frontmatter (research, datascout, grants, gov-reuse, gov-code-search, gov-landscape, and tenders each ship a reader and a writer; `arckit-competitors-writer` ships a writer only and reuses `arckit-tenders-reader`; the three cloud-research commands share one writer, `arckit-cloud-research-writer`). Every `.md` file in `agents/` SHALL begin with `arckit-` and SHALL parse as YAML frontmatter; Claude Code registers every `.md` under `agents/` as a dispatchable agent, and a file with no frontmatter resolves to an unrestricted tool grant.

#### Scenario: 29 agent files register
- **WHEN** the `arckit` plugin loads from `plugins/arckit-claude/`
- **THEN** all 29 files in `agents/` register as dispatchable agents, of which 19 carry `subagent: true` and are not user-invocable

#### Scenario: non-agent file in agents/ is rejected
- **WHEN** a file that does not start with `arckit-` (or carries no parseable frontmatter) is placed in `agents/`
- **THEN** `scripts/check-agent-frontmatter.py` fails, because Claude Code would register it as an all-tools agent (the `READER-PATTERN.md` incident)

#### Scenario: competitors reuses the tenders reader
- **WHEN** the `/arckit:competitors` orchestrator dispatches its research tier
- **THEN** it dispatches the shared `arckit-tenders-reader` subagent and renders through `arckit-competitors-writer` — no `arckit-competitors-reader` file exists

### Requirement: Agent Frontmatter Has A Defined Schema
The system SHALL accept only the following frontmatter fields on an agent file: `name` (required, SHALL equal the filename stem), `description` (required), `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, and `initialPrompt`. `tools` SHALL be an allowlist — only the listed tools are available to the agent; `disallowedTools` SHALL be a denylist applied first, with the allowlist then resolved against what remains. All 29 current agents SHALL declare `model: inherit` and SHALL NOT declare `color` or `permissionMode` (invalid in plugin context).

#### Scenario: required fields present
- **WHEN** an agent file ships without a `name` or `description`
- **THEN** `scripts/check-agent-frontmatter.py` fails on that file

#### Scenario: allowlist plus denylist compose
- **WHEN** an agent declares both `tools` and `disallowedTools`
- **THEN** the denylist is applied first and the allowlist is resolved against the remainder, so the effective grant is the intersection

#### Scenario: heavy-research agents pin effort and turns
- **WHEN** a single-tier heavy-research agent (e.g. `arckit-research`, `arckit-datascout`, `arckit-grants`) runs
- **THEN** it runs at the declared `effort` (`max` or `high`) bounded by its `maxTurns` (30–50), isolating >10 WebSearch/WebFetch/MCP calls from the main conversation

### Requirement: Every Agent MUST Declare A Tools Allowlist
The system SHALL require every agent file to declare a non-empty `tools:` allowlist — deny-by-default is the hardening property, and absence grants every tool in the harness, including tools added by future Claude Code versions. `scripts/check-agent-frontmatter.py` SHALL enforce this in CI (wired into `.github/workflows/lint-markdown.yml`), SHALL reject an empty or non-list `tools:` value, SHALL reject the alphabetised `description, model, name` frontmatter block that `converter.py::copy_agent_stripped()` leaves behind when accidentally run against the plugin source, and SHALL pass only when all agent files carry a valid allowlist.

#### Scenario: missing allowlist fails CI
- **WHEN** an agent file omits `tools:` (as PR #446 silently did on three agents)
- **THEN** `scripts/check-agent-frontmatter.py` exits non-zero in CI and names the file

#### Scenario: stripped-signature detection
- **WHEN** a plugin-source agent file's frontmatter is exactly `{description, model, name}`
- **THEN** the check flags it as the `copy_agent_stripped()` writeback signature and demands restoration of the Claude-only fields from git history

### Requirement: MCP Tools Resolve Only Under The Plugin Prefix
The system SHALL resolve plugin MCP tools in agent `tools:` allowlists only under the `mcp__plugin_arckit_<server>__<tool>` prefix; the bare `mcp__<server>__<tool>` form SHALL match nothing in plugin context. `scripts/check-agent-frontmatter.py` SHALL reject any allowlist entry that starts with `mcp__` but not with `mcp__plugin_`. All MCP-backed agents SHALL allowlist their server's tools under the plugin prefix (e.g. `mcp__plugin_arckit_aws-knowledge__aws___search_documentation`, `mcp__plugin_arckit_govreposcrape__search_uk_gov_code`), and every bundled MCP server SHALL set `alwaysLoad` because a deferred plugin MCP server is not injected into subagent context.

#### Scenario: bare MCP prefix rejected
- **WHEN** an agent allowlists `mcp__govreposcrape__search_uk_gov_code`
- **THEN** `scripts/check-agent-frontmatter.py` fails, instructing the author to use `mcp__plugin_arckit_govreposcrape__search_uk_gov_code`

#### Scenario: provider reader is scoped to its server
- **WHEN** `arckit-aws-research-reader` runs
- **THEN** its `tools` allowlist contains only AWS Knowledge MCP tools (`mcp__plugin_arckit_aws-knowledge__*`), so a prompt-injected instruction cannot steer it to another provider's MCP server

### Requirement: The Three-Tier Orchestrator Pattern Is Enforced Per Split
For every reader/writer split, the system SHALL implement three tiers with enforced tool boundaries: (1) the **orchestrator** lives in the slash command body (`commands/{name}.md`) and runs in the main thread where `Agent` is reliably available — it performs dispatch, validates the reader's JSON via `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-handoff.mjs` against the agent's `{name}-handoff.schema.json`, scores deterministically from a rubric YAML, and dispatches the writer; (2) the **reader** subagent (`arckit-{name}-reader.md`, `subagent: true`) gathers web/MCP evidence and returns a schema-conformant JSON object as its final message, with an allowlist containing `Read`, `Glob`, `Grep`, `WebSearch`, `WebFetch` (where relevant) and the relevant `mcp__plugin_arckit_*` tools, and containing no `Write`, `Edit`, `Bash`, or `Agent`; (3) the **writer** subagent (`arckit-{name}-writer.md`, `subagent: true`) renders the validated, scored payload into the artefact under `projects/{P}-{NAME}/research/`, with an allowlist of no more than `Read`, `Glob`, `Write`, `Edit` and no web/MCP/`Agent` tools, and SHALL render missing input fields as placeholders rather than synthesizing values.

#### Scenario: reader cannot write or recurse
- **WHEN** a reader subagent's `tools` allowlist is inspected
- **THEN** it excludes `Write`, `Edit`, `Bash`, and `Agent`, so the reader that touches untrusted external bytes can neither write an artefact nor dispatch further subagents

#### Scenario: writer renders without network
- **WHEN** a writer subagent renders a payload
- **THEN** it has no `WebSearch`, `WebFetch`, MCP, or `Agent` tools, and any missing payload field appears as a template placeholder, never as an inferred value

#### Scenario: validation failure re-dispatches once
- **WHEN** `validate-handoff.mjs` exits non-zero for a reader payload
- **THEN** the orchestrator re-dispatches the reader at most once with the quoted errors; a second failure logs a gap and continues (no infinite loop)

### Requirement: The Orchestrator Is The Slash Command, Not An Agent File
The system SHALL keep dispatch, schema-validation, and scoring logic in `commands/{name}.md` for every split command rather than in an `agents/` file, because the orchestrator role must call `Agent` and the main thread is the only tier that remains robust when a user sets `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` (nested dispatch depth defaults have changed three times in three months and any user can disable nesting). The matching `agents/arckit-{research,datascout,grants,gov-reuse,gov-code-search,gov-landscape,aws-research,azure-research,gcp-research}.md` files SHALL be treated as pre-split monoliths retained solely because `scripts/converter.py` replaces a command's body wholesale with the agent prompt when generating non-Claude targets — not as the Claude execution path.

#### Scenario: non-Claude targets inline the agent prompt
- **WHEN** `python scripts/converter.py` generates a Codex, Gemini, OpenCode, or Paperclip target for a command whose `arckit-{name}.md` monolith exists
- **THEN** the generated command's prompt body is the full agent prompt (with `## User Request` / `$ARGUMENTS` appended if absent) and the reader/writer subagents (all carrying `subagent: true`) are filtered out of that target

#### Scenario: monolith still registers as a Claude agent
- **WHEN** the `arckit-research` monolith is inspected on a Claude session
- **THEN** it is still a dispatchable agent and MUST retain its `tools:` allowlist, even though the `/arckit:research` command's orchestrator logic — not the monolith — is the Claude execution path

#### Scenario: monoliths are not deleted or re-homed
- **WHEN** a maintainer proposes moving orchestrator logic into `agents/arckit-{name}.md`
- **THEN** the pattern reference (READER-PATTERN.md) forbids it: re-homed orchestrators would stop working silently for users with spawn depth 1, while keeping the orchestrator on the main thread costs nothing

### Requirement: Cloud-Research Splits Share A Writer And Schema But Not Readers
The system SHALL implement the three cloud-research commands (`/arckit:aws-research`, `/arckit:azure-research`, `/arckit:gcp-research`) against one shared handoff schema (`schemas/cloud-research-handoff.schema.json`, because their artefact templates are structurally identical) and one shared writer subagent (`arckit-cloud-research-writer`, which holds no network tools and therefore isolates nothing between providers), while each command SHALL retain its own reader subagent (`arckit-aws-research-reader`, `arckit-azure-research-reader`, `arckit-gcp-research-reader`) allowlisting only that provider's MCP server.

#### Scenario: three readers, one writer
- **WHEN** the three cloud orchestrators run
- **THEN** each dispatches its own provider-scoped reader and the single `arckit-cloud-research-writer`, which renders AWRS, AZRS, or GCRS artefacts under `projects/{P}-{NAME}/research/`

#### Scenario: schema shared across providers
- **WHEN** any of the three cloud readers returns its payload
- **THEN** the orchestrator validates it against the same `cloud-research-handoff.schema.json`, the way `gov-repo-handoff.schema.json` is shared by `gov-code-search` and `gov-landscape`

### Requirement: Agents Are Claude Code Only; Non-Claude Targets Inline The Prompt
The system SHALL treat agents as a Claude Code-only capability: the converter SHALL strip Claude-only agent fields (`effort`, `initialPrompt`, `maxTurns`, `disallowedTools`, `tools`) via `copy_agent_stripped()` and SHALL filter out every `subagent: true` file for non-Claude targets, because Codex, Gemini, OpenCode, and Copilot runtimes cannot dispatch subagents. Where a non-Claude target needs an agent's capability, the generated command SHALL inline the full agent prompt so the structural reader/orchestrator/writer isolation is unavailable and the command prompt's Guardrails section is the only protection.

#### Scenario: Claude-only fields stripped
- **WHEN** the converter copies an agent file to a non-Claude extension
- **THEN** `effort`, `initialPrompt`, `maxTurns`, `disallowedTools`, and `tools` are removed from the frontmatter and only the prompt body (plus surviving `name`/`description`/`model`) is emitted

#### Scenario: subagents never reach non-Claude targets
- **WHEN** the converter builds a Codex skill, Gemini extension, OpenCode command, or Copilot prompt
- **THEN** no `arckit-*-reader` or `arckit-*-writer` (or any `subagent: true` file) appears in that target, and any command backed by an agent monolith carries the inlined agent prompt instead
