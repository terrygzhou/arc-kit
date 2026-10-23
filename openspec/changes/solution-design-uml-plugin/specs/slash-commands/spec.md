## MODIFIED Requirements

### Requirement: Commands Are Exposed From Markdown Files
The system SHALL expose every file in `plugins/arckit-claude/commands/` as a slash command `/arckit:<name>` where `<name>` is the filename stem, and the YAML frontmatter at the top of the file SHALL be the source of truth for command metadata.

#### Scenario: 76 commands ship
- **WHEN** the `arckit` plugin loads from `plugins/arckit-claude/`
- **THEN** all 76 files in `commands/` are available as `/arckit:<name>` commands, including the new `solution-design` command

#### Scenario: 75 commands ship
- **WHEN** the `arckit` plugin loads from `plugins/arckit-claude/`
- **THEN** all 75 pre-existing files in `commands/` remain available as `/arckit:<name>` commands

#### Scenario: command set is stable
- **WHEN** the baseline is counted
- **THEN** 76 `.md` command files exist in `plugins/arckit-claude/commands/`, each carrying the `description` and `doc-type` fields

#### Scenario: frontmatter is authoritative
- **WHEN** a command body and its frontmatter disagree about a field
- **THEN** the frontmatter value governs (e.g. `effort`, `doc-type`) and the body is treated as prose instructions

### Requirement: Doc-Type Declaration Names What The Command Writes
The system SHALL require every command to declare in `doc-type:` the doc-type code(s) that running the command produces — a single code (`doc-type: REQ`), a `[A, B]` list when one command writes more than one governed artefact, or `none` when it writes no `ARC-*` artefact (e.g. `/arckit:search`, `/arckit:health`, `/arckit:pages`, `/arckit:build`, `/arckit:start`, `/arckit:init`). The declaration SHALL sit on the command even when the command delegates to an agent that holds the Write call (e.g. `/arckit:framework` declares `FWRK` and delegates to the `arckit-framework` agent).

#### Scenario: solution-design command declares SOLN
- **WHEN** `/arckit:solution-design` runs and writes `projects/{NNN}/ARC-{NNN}-SOLN-v1.0.md`
- **THEN** its frontmatter declares `doc-type: SOLN`

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
