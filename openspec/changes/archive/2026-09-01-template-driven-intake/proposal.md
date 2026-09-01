## Why

Artefact-producing commands today "warn on MANDATORY missing inputs" — a warning that still renders a template full of sections the user cannot fill. The template itself is the authoritative source of *what input the artefact needs* (its sections, Document Control fields, and the command's MANDATORY prerequisite inputs), but nothing ever interviews the user against it. Result: users run `/arckit:*` (including overlay commands such as `togaf/adm`, `oaa`, and `agent/architecture`) with insufficient input and get scaffolding rather than artefacts.

## What Changes

- New requirement under `slash-commands`: **Template-Driven Intake Interview** — before generating its artefact, every artefact-producing command (core and bundled overlay) SHALL derive interview questions from the *effective* template (user override wins) plus its MANDATORY prerequisite inputs and unresolvable Document Control fields, prefill from existing `projects/` artefacts and saved answers, then ask the remaining questions one at a time with an explicit skip option on every question (soft gate).
- Skipped MANDATORY inputs SHALL render as explicit `TBD` markers quoting the interview question in the artefact, and the command's summary SHALL list unresolved fields.
- Answers SHALL persist to `projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json` so neither re-runs nor new sessions re-ask; the `architecture-workflow` onboarding triage additionally seeds a shared `projects/{NNN}-{slug}/.arckit/intake/shared.json` so the first command after onboarding starts warm.
- Non-interactive paths (the `arckit-build` bulk harness) SHALL NOT interview; they consume saved intake and fall back to `TBD`.
- Implementation mechanism: one shared instruction block (`references/intake-instructions.md`) plus a step in every artefact-producing command body, plus a seed step in the `architecture-workflow` skill; the command frontmatter, templates, doc-type registry, and artifact naming are untouched.
- Modified requirement: **Command Execution Contract** — "warn on MANDATORY missing inputs" becomes "collect MANDATORY inputs via the template-driven intake interview; unanswered ones surface as `TBD` and are flagged in the summary".

Non-goals: no new bundled skill (the five-skill pin in `plugin-skills` stands), no new slash command, no changes to *which* questions `architecture-workflow` asks or to its HARD-GATE (it gains only answer persistence — writing state is not running a command), no template format changes (no new input-placeholder syntax is introduced), no hard blocking of any command.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `slash-commands`: gains the Template-Driven Intake Interview requirement; the Command Execution Contract's prerequisite handling changes from warn-only to collect-via-interview (soft gate).
- `plugin-skills`: `architecture-workflow` gains one behaviour — persisting its completed triage answers into the project intake store so later commands prefill from them; its question flow and HARD-GATE are unchanged.

## Impact

- Spec: `openspec/specs/slash-commands/spec.md` (1 ADDED requirement, 1 MODIFIED requirement).
- New shared file: `plugins/arckit-claude/references/intake-instructions.md`.
- Command bodies: one intake step added to every artefact-producing command (core `commands/*.md` with `doc-type: != none`, plus overlay commands under `plugins/arckit-claude/plugins/{togaf/adm,oaa,agent/architecture}/commands/`).
- Runtime state: new `projects/{NNN}-{slug}/.arckit/intake/` directory (gitignored alongside `.arckit/` session state).
- Generated targets: all seven converter outputs regenerate; no converter logic change (command bodies are the source of truth).
- `arckit-build` skill gains one clause: bulk targets use saved intake, never interview.
- `architecture-workflow` skill (`skills/architecture-workflow/SKILL.md`): gains the seed-persistence step; regenerated into all seven targets like every other skill.
