# governance-hooks Specification

## Purpose
The ArcKit Claude Code plugin hooks subsystem SHALL govern, protect, observe, and report on every tool interaction in an ArcKit session: gate dangerous writes (protected paths, secrets, non-conforming ARC filenames), stamp machine-derived provenance and manifest state onto artefacts, record best-effort session telemetry, re-inject filesystem-derived project context after compaction, nudge the model on traceability gaps at end-of-turn, and keep the session pinned to a known-good Claude Code version.

## Requirements

### Requirement: All hook handlers MUST use the exec form
Every hook entry registered in `hooks/hooks.json` SHALL declare `command: "node"` with a sibling `args: string[]` whose first element is `${CLAUDE_PLUGIN_ROOT}/hooks/<name>.mjs`, so the Claude Code harness execs the Node binary directly instead of parsing a shell-quoted command string.

#### Scenario: Hook entry is registered in exec form
- **WHEN** any hook entry in `hooks.json` is read by the Claude Code harness
- **THEN** its `command` field SHALL equal the string `node` and its `args` array SHALL contain exactly one element of the form `${CLAUDE_PLUGIN_ROOT}/hooks/<name>.mjs`

#### Scenario: No legacy shell-string command is used
- **WHEN** a hook entry in `hooks.json` is inspected
- **THEN** its `command` field SHALL NOT contain a space-separated argument list (e.g. `"node /path/to/x.mjs"`); all arguments SHALL be carried in the `args` array

### Requirement: Observational PostToolUse hooks MUST set continueOnBlock
Every PostToolUse hook entry in `hooks/hooks.json` SHALL declare `continueOnBlock: true` so that observational hooks (`update-manifest`, `provenance-stamp`, `telemetry`, `tidy-wardley-labels`) can never block or derail the user's turn, even if they emit a `decision: "block"` payload or fail.

#### Scenario: PostToolUse hook emits a block decision
- **WHEN** a PostToolUse hook (`update-manifest`, `provenance-stamp`, `telemetry`, or `tidy-wardley-labels`) emits `{"decision": "block"}` on stdout
- **THEN** the Claude Code harness SHALL continue the user's turn; the block decision SHALL be logged by the harness but SHALL NOT halt the conversation

#### Scenario: PreToolUse gate hook retains default block semantics
- **WHEN** a PreToolUse gate hook (`file-protection`, `secret-detection`, `validate-arc-filename`, `score-validator`, `validate-wardley-math`, `secret-file-scanner`, `allow-plugin-internals`) emits `{"decision": "block"}` on stdout
- **THEN** the Claude Code harness SHALL block the pending tool call and feed the `reason` string back to the model

### Requirement: Genuine gate hooks MUST block writes that violate policy
The PreToolUse gate hooks SHALL block writes that violate ArcKit policy. `file-protection.mjs` SHALL block `Edit`/`Write` calls whose target path matches a protected pattern (environment files, lock files, `.git/`, credential directories `/.aws/` `/.ssh/` `/.gnupg/`, known secret filenames, `*.pem` `*.key` `*.p12` `*.pfx`, private key files `id_rsa` `id_ed25519` `id_ecdsa`, token files `.npmrc` `.pypirc` `.netrc`, or filenames containing sensitive keywords such as `password`, `secret`, `token`, `credential`, `private key`, `api key`). `secret-detection.mjs` SHALL block `UserPromptSubmit` prompts that match a known secret pattern (OpenAI/Anthropic/GitHub/AWS/Notion/Atlassian/Slack/Google API keys, PEM private keys, database connection strings with embedded credentials, high-entropy key-value pairs, Bearer tokens). `validate-arc-filename.mjs` SHALL block `Write` calls under `projects/` whose target filename does not conform to the `ARC-NNN-TYPE[-NNN]-vN.N.md` naming convention for a registered doc-type code.

#### Scenario: Write to a protected path is blocked
- **WHEN** the model issues a `Write` or `Edit` tool call targeting `.env`, `package-lock.json`, `.aws/credentials`, `id_rsa`, or any file whose name contains the substring `password` (case-insensitive)
- **THEN** `file-protection.mjs` SHALL emit `{"decision": "block", "reason": "Protected: ..."}` and the tool call SHALL NOT execute

#### Scenario: Prompt containing a secret is blocked
- **WHEN** the user submits a prompt that contains a string matching `sk-[a-zA-Z0-9]{20,}` (OpenAI key), `ghp_[a-zA-Z0-9]{36}` (GitHub PAT), or `-----BEGIN RSA PRIVATE KEY-----`
- **THEN** `secret-detection.mjs` SHALL emit `{"decision": "block", "reason": "Warning: Potential secrets detected: ..."}` and the prompt SHALL NOT be processed

#### Scenario: Non-conforming ARC filename is blocked
- **WHEN** the model issues a `Write` tool call targeting `projects/001-foo/ARC-1-XYZ-v1.0.md` (unregistered doc-type `XYZ` or non-3-digit project ID)
- **THEN** `validate-arc-filename.mjs` SHALL emit `{"decision": "block", "reason": "ArcKit: Unknown document type code 'XYZ' ..."}` and the tool call SHALL NOT execute

### Requirement: Provenance stamping MUST append a machine-stamped Build Provenance block
`provenance-stamp.mjs` (PostToolUse, `Write|Edit` against `projects/**`) SHALL append a `## Build Provenance` block delimited by `<!-- arckit-provenance:start -->` / `<!-- arckit-provenance:end -->` markers to every ArcKit artefact file matching `ARC-\d{3}-.+-v\d+(\.\d+)?\.md` under `projects/`. The block SHALL contain only harness-derived fields the model cannot self-report: Requested Effort (from the invoking command's YAML frontmatter `effort:`), Effective Effort (computed by the silent-downgrade matrix in `provenance-model.mjs`), Build context (Recipe / Wave / Target / Topic) when run via `/arckit:build` (sourced from `projects/{P}/.arckit/state.json`), and a Stamped-at ISO 8601 timestamp. The block SHALL be idempotent: re-running on the same file SHALL replace the existing block in place rather than append a duplicate. When no effort or build context is available, the hook SHALL skip stamping entirely (no empty block).

#### Scenario: Artefact written via /arckit:requirements receives a provenance block
- **WHEN** the model writes `projects/001-foo/ARC-001-REQ-v1.0.md` via the `Write` tool and the file's footer contains `AI Model: Opus 5` and the invoking command declares `effort: max`
- **THEN** `provenance-stamp.mjs` SHALL append a `## Build Provenance` block containing `Requested Effort: max`, `Effective Effort: max` (or a downgraded value with a note if the model does not support `max`), and a `Stamped at` ISO timestamp, delimited by the `arckit-provenance` markers

#### Scenario: Re-writing the same artefact replaces the provenance block
- **WHEN** `provenance-stamp.mjs` fires a second time on an artefact that already contains a `<!-- arckit-provenance:start -->...<!-- arckit-provenance:end -->` block
- **THEN** the hook SHALL replace the existing block in place; the file SHALL contain exactly one `## Build Provenance` section

#### Scenario: Non-ArcKit file edit is not stamped
- **WHEN** the model issues an `Edit` tool call on a file outside `projects/` or on a file whose name does not match `ARC-\d{3}-.+-v\d+(\.\d+)?\.md`
- **THEN** `provenance-stamp.mjs` SHALL exit silently without modifying the file

### Requirement: PostCompact MUST re-inject filesystem-derived project context
`postcompact-rehydrate.mjs` (PostCompact) SHALL re-inject the same project context the `UserPromptSubmit` hook produces, so that dynamic filesystem-derived state (`projects/` inventory, ARC artefact listings including subdirectories, vendor profiles, external documents, global policies) is not lost in the `/compact` or auto-compaction summary. The hook SHALL reuse `buildProjectContext` from `project-context-builder.mjs` (the same builder used by `arckit-context.mjs` and `inject-agent-context.mjs`) and SHALL emit the context via `hookSpecificOutput.additionalContext` with `hookEventName: "PostCompact"`. When no `projects/` directory exists at the repo root, the hook SHALL emit an empty JSON object `{}` and exit.

#### Scenario: PostCompact re-injects project context after /compact
- **WHEN** the user issues `/compact` in a repo containing `projects/001-foo/ARC-001-REQ-v1.0.md` and `projects/001-foo/decisions/ARC-001-ADR-001-v1.0.md`
- **THEN** `postcompact-rehydrate.mjs` SHALL emit `hookSpecificOutput.additionalContext` containing a listing of both artefacts and the project inventory, so the model retains the active project state after compaction

#### Scenario: PostCompact in a repo without projects/ is silent
- **WHEN** `postcompact-rehydrate.mjs` fires in a working directory that does not contain a `projects/` subdirectory
- **THEN** the hook SHALL emit `{}` on stdout and SHALL NOT emit `additionalContext`

### Requirement: SessionStop nudge MUST be version-gated and suppressible
`session-learner.mjs` (Stop / StopFailure) SHALL, on a normal `Stop`, emit at most one end-of-turn nudge via `hookSpecificOutput.additionalContext` when this session's git-committed artefacts left a curated traceability-chain gap (e.g. `REQ` created but no `TRAC` matrix on disk for the same project; `STKE` created but no `REQ`; `REQ` created but no `DATA`; `ADR` recorded but no `DIAG`). The nudge decision SHALL be made by the pure `selectNudge` function in `session-nudge.mjs`, which SHALL return the first matching rule in priority order with ascending project number as the tiebreaker. The nudge SHALL be suppressed in all of the following cases: the session ended in `StopFailure`; the `ARCKIT_NO_NUDGE` environment variable is set; no ARC artefact was touched this session; the detected Claude Code client version (read from `.arckit/memory/.cc-version`) is below `2.1.163` or the file is absent/unparseable. All nudge logic SHALL run after the session-summary writes and SHALL be wrapped so that a nudge failure can never break the summary writes.

#### Scenario: REQ created without TRAC triggers a nudge
- **WHEN** a session commits `ARC-001-REQ-v1.0.md` to `projects/001-foo/` and no `ARC-001-TRAC-v*.md` file exists anywhere under that project directory, and the client version in `.arckit/memory/.cc-version` is `2.1.234`
- **THEN** `session-learner.mjs` SHALL emit `hookSpecificOutput.additionalContext` suggesting `/arckit:traceability` to close the traceability gap

#### Scenario: Nudge is suppressed on StopFailure
- **WHEN** the session ends in `StopFailure` (API error, rate limit, or auth failure)
- **THEN** `session-learner.mjs` SHALL record the failure in `sessions.md` but SHALL NOT emit any `hookSpecificOutput.additionalContext` nudge

#### Scenario: Nudge is suppressed below the version gate
- **WHEN** `.arckit/memory/.cc-version` contains `2.1.150` (below `2.1.163`) and the session left a `REQ`-without-`TRAC` gap
- **THEN** `session-learner.mjs` SHALL NOT emit a nudge; the Stop hook SHALL exit silently on the nudge path (older clients treat Stop `additionalContext` as a hook error)

#### Scenario: Nudge is suppressed when ARCKIT_NO_NUDGE is set
- **WHEN** the `ARCKIT_NO_NUDGE` environment variable is set to a non-empty value and the session left a traceability gap
- **THEN** `session-learner.mjs` SHALL NOT emit a nudge

### Requirement: SessionStart version check MUST persist the client version and warn on drift
`version-check.mjs` (SessionStart) SHALL detect the running Claude Code client version (via the `$CLAUDE_CODE_VERSION` env var if set, otherwise by invoking `claude --version` with a 2-second timeout) and SHALL persist it to `.arckit/memory/.cc-version` when the working directory is an ArcKit project (contains `.arckit/` or `projects/`). The hook SHALL emit a version warning via `hookSpecificOutput.additionalContext` when the detected client version is below `2.1.234` (the overall minimum-version floor). The hook SHALL also check for a newer ArcKit plugin release via the GitHub API (`https://api.github.com/repos/terrygzhou/arc-kit/releases/latest`, 3-second timeout) and emit an update-available warning when the local plugin `VERSION` file is behind. All version-detection and network failures SHALL be swallowed silently; the hook SHALL exit `0` in all cases.

#### Scenario: Client version below floor triggers a warning
- **WHEN** the detected Claude Code client version is `2.1.200` (below `2.1.234`)
- **THEN** `version-check.mjs` SHALL emit `hookSpecificOutput.additionalContext` containing a `## Claude Code Version Warning` section listing the features that depend on `v2.1.234+` and the `claude update` instruction

#### Scenario: Client version is persisted for the Stop-hook nudge gate
- **WHEN** `version-check.mjs` fires at SessionStart in an ArcKit project and the detected client version is `2.1.234`
- **THEN** the file `.arckit/memory/.cc-version` SHALL contain the string `2.1.234` so that `session-learner.mjs` can read it later for the nudge version gate

#### Scenario: Network failure during update check is silent
- **WHEN** the GitHub API request in `version-check.mjs` times out or returns a non-200 status
- **THEN** the hook SHALL NOT emit an update-available warning and SHALL exit `0` silently (or with only the client-version warning if one fired)

### Requirement: Hook entries MUST support the if: field for narrow triggering
Individual hook entries in `hooks/hooks.json` SHALL support an `if:` field using Claude Code permission-rule syntax to narrow the set of tool invocations that trigger the hook, avoiding unnecessary Node process spawns. The `if:` value SHALL be a permission rule such as `"Write(/projects/**)"` (fires only for `Write` calls whose resolved path is under `<project-root>/projects/`) or `"Write(/projects/**/vendors/scores.json)"` (fires only for that exact path). Path patterns SHALL follow gitignore semantics. When the `if:` condition does not match the current tool invocation, the hook SHALL NOT be spawned.

#### Scenario: Write to a non-projects path does not trigger validate-arc-filename
- **WHEN** the model issues a `Write` tool call targeting `docs/README.md` (outside `projects/`)
- **THEN** the `validate-arc-filename` hook entry (which carries `if: "Write(/projects/**)"`) SHALL NOT be spawned; no Node process SHALL be started for that hook

#### Scenario: Write to a projects path triggers validate-arc-filename
- **WHEN** the model issues a `Write` tool call targeting `projects/001-foo/ARC-001-REQ-v1.0.md`
- **THEN** the `validate-arc-filename` hook SHALL be spawned and SHALL validate the filename against the `ARC-NNN-TYPE-vN.N.md` convention

### Requirement: A background stale-artifact monitor MUST be declared in plugin.json
The ArcKit plugin manifest (`.claude-plugin/plugin.json`) SHALL declare a background monitor named `stale-artifact-scan` under the `experimental.monitors` key. The monitor SHALL run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/bash/detect-stale-artifacts.sh` with `when: "always"` (i.e. at session start). The monitor SHALL emit one stdout line per artefact whose Document Control `Next Review Date` is in the past, or whose `Status` is `DRAFT` and whose `Last Modified` date is more than 30 days in the past, and SHALL exit silently when the working directory does not contain a `projects/` directory. The monitor's stdout lines SHALL be delivered to the session as in-session notifications.

#### Scenario: Stale artefact is reported at session start
- **WHEN** a session starts in a repo containing `projects/001-foo/ARC-001-REQ-v1.0.md` whose `Next Review Date` is `2025-01-01` (in the past) and the current date is after that
- **THEN** the `stale-artifact-scan` monitor SHALL emit the line `[ArcKit monitor] STALE: projects/001-foo/ARC-001-REQ-v1.0.md — review overdue since 2025-01-01` as a session notification

#### Scenario: Monitor is silent in a non-ArcKit repo
- **WHEN** a session starts in a working directory that does not contain a `projects/` subdirectory
- **THEN** `detect-stale-artifacts.sh` SHALL exit `0` with no stdout output; no monitor notification SHALL be delivered

#### Scenario: DRAFT artefact unchanged for more than 30 days is reported
- **WHEN** an artefact under `projects/` has `Status: DRAFT` and `Last Modified` more than 30 days before the current date, and its `Next Review Date` is not in the past
- **THEN** the `stale-artifact-scan` monitor SHALL emit a `[ArcKit monitor] STALE: ... — DRAFT unchanged since <date>` line for that artefact

### Requirement: Platform hook capabilities available but not yet used
The following Claude Code platform hook capabilities SHALL remain declared-but-unused in the ArcKit plugin baseline (tracked on issue #522 for future adoption): (1) `SessionStart` hooks MAY return `hookSpecificOutput.sessionTitle` to name the session and `reloadSkills: true` to re-scan skill directories (Claude Code v2.1.152+); ArcKit SHALL NOT emit these fields from any SessionStart hook in the baseline. (2) The `MessageDisplay` event (Claude Code v2.1.152+) MAY be used to transform or hide assistant text as it is displayed; ArcKit SHALL NOT register any `MessageDisplay` hook in the baseline. The baseline SHALL document these capabilities in `hooks/README.md` as available-but-not-yet-used.

#### Scenario: No SessionStart hook emits sessionTitle or reloadSkills
- **WHEN** any ArcKit SessionStart hook (`arckit-session.mjs`, `version-check.mjs`, `v5-migration-banner.mjs`, `notify-stale-artifacts.mjs`) emits output on stdout
- **THEN** the JSON payload SHALL NOT contain `hookSpecificOutput.sessionTitle` or `hookSpecificOutput.reloadSkills`

#### Scenario: No MessageDisplay hook is registered
- **WHEN** `hooks/hooks.json` is inspected for a `MessageDisplay` key
- **THEN** the `hooks` object SHALL NOT contain a `MessageDisplay` entry
