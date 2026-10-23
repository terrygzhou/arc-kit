## Why

ArcKit has no first-class way to produce a UML 2.5.1 solution design document with embedded, viewable diagram views. Developers currently write prose descriptions of use case, sequence, component, deployment, class, and object diagrams, but cannot produce them as inline-renderable PlantUML blocks within a single governed artefact. This gap slows software solution delivery and forces teams to maintain standalone diagram files separately from the design narrative.

## What Changes

- Add new command `/arckit:solution-design` (a.k.a. `$arckit-solution-design` on Codex) under `plugins/arckit-claude/commands/solution-design.md`
- Add new doc type `SOLN` to `doc-types.mjs`, `pages.md`, and both bash `generate-document-id.sh` copies
- Add new template `solution-design-template.md` to `plugins/arckit-claude/templates/` and `.arckit/templates/`
- Add new user guide `docs/guides/solution-design.md` (canonical) synced via `check-guide-parity.py`
- Add new reference file `plugins/arckit-claude/skills/plantuml-syntax/references/object-diagrams.md`
- Update `plantuml-syntax/SKILL.md` "ArcKit Commands Using It" table to include `/arckit:solution-design`
- Regenerate all non-Claude extensions via `scripts/converter.py`

## Capabilities

### New Capabilities

- `solution-design-uml-plugin`: A new slash command and template that generates a governed UML 2.5.1 solution design document (`ARC-NNN-SOLN-v1.0.md`) with six embedded PlantUML diagram sections (use case, sequence, component, deployment, class, object), read from existing requirements, external HLD/DLD documents, and ADR artefacts. The command is PlantUML-only (Mermaid lacks object-diagram grammar and has no UML use-case or component reference).

### Modified Capabilities

- `slash-commands`: Adds `solution-design` to the command set; its `doc-type` declaration is `SOLN`. The command frontmatter follows the `data-model.md` pattern (handoffs-bearing; `diagram.md` has no handoffs).
- `plugin-skills`: The `plantuml-syntax` skill gains a new reference file `object-diagrams.md` and an updated "ArcKit Commands Using It" table row for the new command.

## Impact

- `plugins/arckit-claude/commands/solution-design.md` — new file
- `plugins/arckit-claude/templates/solution-design-template.md` — new file
- `.arckit/templates/solution-design-template.md` — new file (dual-tree rule)
- `plugins/arckit-claude/config/doc-types.mjs` — `SOLN` added to `DOC_TYPES` and `MULTI_INSTANCE_TYPES`
- `plugins/arckit-claude/commands/pages.md` — `SOLN` row added to known-artifact-types table
- `scripts/bash/generate-document-id.sh` and `plugins/arckit-claude/scripts/bash/generate-document-id.sh` — `SOLN` added to `MULTI_INSTANCE_TYPES`
- `plugins/arckit-claude/skills/plantuml-syntax/SKILL.md` — table update
- `plugins/arckit-claude/skills/plantuml-syntax/references/object-diagrams.md` — new file
- `docs/guides/solution-design.md` — new file
- `plugins/arckit-claude/docs/guides/solution-design.md` — synced copy
- All `extensions/arckit-{codex,gemini,opencode,copilot,paperclip,vibe,kimi}/` — regenerated via converter
- `README.md`, `docs/DEPENDENCY-MATRIX.md`, `CHANGELOG.md` — documentation updates
