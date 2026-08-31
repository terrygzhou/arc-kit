# Tasks — template-driven-intake

## 1. Shared instruction block
- [x] 1.1 Create `plugins/arckit-claude/references/intake-instructions.md`: derivation algorithm (effective template → sections + MANDATORY inputs + unresolvable Document Control fields → prefill check against `projects/` artefacts, `.arckit/intake/{stem}.json`, `.arckit/intake/shared.json`, `user_config` → ask remainder one at a time, each with skip), persistence format (`projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json` and shared seed `shared.json`, `{answers, updated}`), precedence (artefacts > per-command > shared > `user_config`), TBD-marker format (`TBD` + quoted question), summary reporting of unresolved fields, proportionality cap (zero questions when fully prefilled), and the bulk-build exemption clause

## 2. Core commands
- [x] 2.1 Inventory core artefact-producing commands: 75 core commands total; subtract the 15 non-artefact commands (`build`, `init`, `start`, `health`, `trello`, `pages`, `score`, `search`, `navigator`, `graph-report`, `import-okf`, `export-okf`, `customize`, `template-builder`, `impact`) to get 60 artefact-producing. Working check: `ls plugins/arckit-claude/commands/*.md | grep -vE '/(build|init|start|health|trello|pages|score|search|navigator|graph-report|import-okf|export-okf|customize|template-builder|impact)\.md$' | wc -l` → `60`. (There is no `doc-type:` frontmatter to grep; artefact-producing commands are those that read a template or write an `ARC-*` file.)
- [x] 2.2 Insert the intake step ("Run the intake interview per `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md`") immediately before each command's template-read step; renumber subsequent steps

## 3. Overlay commands
- [x] 3.1 Same step in every command under `plugins/arckit-claude/plugins/togaf/adm/commands/`
- [x] 3.2 Same step in every command under `plugins/arckit-claude/plugins/oaa/commands/` (interview must not add diagram/output mandates — OAA tone guard)
- [x] 3.3 Same step in every command under `plugins/arckit-claude/plugins/agent/architecture/commands/`

## 4. Skill changes
- [x] 4.1 Add one clause to `plugins/arckit-claude/skills/arckit-build/SKILL.md`: bulk targets never run the interactive intake; they consume saved `.arckit/intake/` answers and render `TBD` for unknowns
- [x] 4.2 Add the seed step to `plugins/arckit-claude/skills/architecture-workflow/SKILL.md`: after triage completes, merge answers into `projects/{NNN}-{slug}/.arckit/intake/shared.json` (create path, never clobber existing keys) and note the save in the plan output; HARD-GATE wording untouched

## 5. Regenerate and validate
- [x] 5.1 `.venv/bin/python scripts/converter.py` (regenerates all seven `extensions/` targets)
- [x] 5.2 Spot-check generated outputs: intake step survives conversion in `extensions/arckit-codex` (and one other target); `${CLAUDE_PLUGIN_ROOT}` paths remain target-appropriate
- [x] 5.3 `pytest tests/codex/test_codex_extension.py`
- [x] 5.4 `npx markdownlint-cli2 "**/*.md"` (or scoped to changed paths)
- [x] 5.5 Parity check: every artefact-producing command (core + the 3 overlay plugins named) contains the intake step; no `doc-type: none` command does

## 6. Close out
- [x] 6.1 `openspec validate template-driven-intake`
- [x] 6.2 Conventional commit: `feat: add template-driven intake interview to artefact-producing commands`
