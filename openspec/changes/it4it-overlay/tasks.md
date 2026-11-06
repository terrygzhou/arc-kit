## 1. Doc-Type Registration (blocking prerequisite — #712 pattern)

- [x] 1.1 Register six IT4IT codes in `plugins/arckit-claude/config/doc-types.mjs` (`ITVN`, `ITVS`, `ITSF`, `ITDT`, `ITCF`, `ITOA`), category `Architecture`, no regime tag
- [x] 1.2 Add `ITVS` to `MULTI_INSTANCE_TYPES` in `doc-types.mjs`
- [x] 1.3 Add `ITVS` to `MULTI_INSTANCE_TYPES` in `scripts/bash/generate-document-id.sh`
- [x] 1.4 Add `ITVS` to `MULTI_INSTANCE_TYPES` in `plugins/arckit-claude/scripts/bash/generate-document-id.sh`
- [x] 1.5 Add allow-list table rows for all six codes to `plugins/arckit-claude/commands/pages.md`
- [x] 1.6 Run `python3 scripts/check-doc-type-registry.py` + `check-doctype-collisions.py` + `check-multi-instance-parity.py` — all green

## 2. Standalone Plugin Tree (`plugins/arckit-it4it/`)

- [x] 2.1 Create `plugins/arckit-it4it/.claude-plugin/plugin.json` (name `arckit-it4it`, version `6.11.0`, `defaultEnabled: false`, dependency `arckit =6.11.0`, `userConfig`: `default_classification`/`organisation_name`/`project_issue_prefix`/`references_dir`)
- [x] 2.2 Create `plugins/arckit-it4it/VERSION` (`6.11.0`) and `CHANGELOG.md` + `README.md`
- [x] 2.3 Author `plugins/arckit-it4it/commands/it4it-value-network.md` — frontmatter (description, argument-hint, effort, handoffs), MANDATORY `PRIN` gate + "STOP and ask user to run `/arckit:principles`", intake step, template read, `output` = `ARC-{P}-ITVN-v1.0.md`
- [x] 2.4 Author `plugins/arckit-it4it/commands/it4it-value-stream.md` — MANDATORY `PRIN` + RECOMMENDED `ITVN`; multi-instance output `ARC-{P}-ITVS-{NNN}-v1.0.md` (sequence-numbered, one per value stream)
- [x] 2.5 Author `plugins/arckit-it4it/commands/it4it-strategy-portfolio.md` (Ch 6) — MANDATORY `PRIN`, output `ARC-{P}-ITSF-v1.0.md`
- [x] 2.6 Author `plugins/arckit-it4it/commands/it4it-develop-test.md` (Ch 7) — MANDATORY `PRIN`, output `ARC-{P}-ITDT-v1.0.md`
- [x] 2.7 Author `plugins/arckit-it4it/commands/it4it-consume-fulfil.md` (Ch 8) — MANDATORY `PRIN`, output `ARC-{P}-ITCF-v1.0.md`
- [x] 2.8 Author `plugins/arckit-it4it/commands/it4it-operate-assure.md` (Ch 9 + Ch 10 Supporting Functions cross-reference) — MANDATORY `PRIN`, output `ARC-{P}-ITOA-v1.0.md`
- [x] 2.9 Author six templates in `plugins/arckit-it4it/templates/` (one per command) + `templates/_partials/` copies for shared blocks referenced via `${CLAUDE_PLUGIN_ROOT}`
- [x] 2.10 Author `plugins/arckit-it4it/references/`: `citation-instructions.md` (S261 "reference, not conformance" rule), `quality-checklist.md`, `intake-instructions.md`, `intake-discovery-dimensions.md`, `value-streams-reference.md` (seven streams — scenario, trigger, stages, stakeholders), `functional-components-reference.md`
- [x] 2.11 Author `plugins/arckit-it4it/schemas/`: `value-stream.json`, `functional-component.json` (+ `README.md`)
- [x] 2.12 Author `plugins/arckit-it4it/validate-architecture.py` (stdlib-only, embedded draft-07 subset, `gate`/`self-test`/`drift` modes) mirroring OAA's
- [x] 2.13 Author `plugins/arckit-it4it/recipes/it4it-full.yaml` — `PRIN` → `ITVN` → `ITVS` → `ITSF` → `ITDT` → `ITCF` → `ITOA`

## 3. Sub-Plugin Copy (`plugins/arckit-claude/plugins/it4it/`)

- [x] 3.1 Copy commands, references, templates into `plugins/arckit-claude/plugins/it4it/` (byte-identical except `LOCAL_OVERRIDES` files)
- [x] 3.2 Register `plugins/arckit-it4it` in `sync-shared-assets.py` sync targets (NOT in `SYNC_EXEMPT_PLUGINS`); add any customised file to `LOCAL_OVERRIDES`
- [x] 3.3 Run `python3 scripts/sync-shared-assets.py --check` (or equivalent verify) to confirm parity

## 4. Converter + Marketplace Registration

- [x] 4.1 Add `"plugins/arckit-it4it"` to `PLUGIN_SOURCES` in `scripts/converter.py` (community position, before core)
- [x] 4.2 Add `arckit-it4it` entry to `.claude-plugin/marketplace.json`
- [x] 4.3 Regenerate all seven extension targets: `python3 scripts/converter.py`
- [x] 4.4 Verify `extensions/arckit-codex/commands/` now includes the six `arckit.it4it-*` command files and no registry collision was produced

## 5. Tests

- [x] 5.1 Author `tests/plugin/test_it4it_doc_types.py` (11 tests) — six codes in `doc-types.mjs` + Codex dual registration; `ITVS` multi-instance parity across .mjs, both bash generators, and Codex; six codes in `/arckit:pages` allow-list; plugin manifest shape; sub-plugin byte-parity; MANDATORY `PRIN` hard gate in all six command bodies; D5 tone guard (no diagram/output mandate beyond template). Companion: `tests/plugin/test_it4it_validate_architecture.py` (15 tests) covers validator `gate`/`self-test`/`drift`/artifact modes.
- [x] 5.2 Run `python3 -m pytest tests/plugin/test_it4it_doc_types.py tests/plugin/test_it4it_validate_architecture.py -q` — green
- [x] 5.3 Run the full CI gate set: `check-doc-type-registry.py`, `check-doctype-collisions.py`, `check-multi-instance-parity.py`, `check-recipies.py`, `check-references.py`, `sync-shared-assets.py --check`, `plugins/arckit-it4it/validate-architecture.py gate` — all green

## 6. CI Wiring

- [x] 6.1 Register `plugins/arckit-it4it/validate-architecture.py gate` in `scripts/ci-local.sh` (mirrors OAA's registration: OAA's gate + axioms live in `ci-local.sh` but NOT in any workflow file — IT4IT follows the same pattern; `ci-local.sh:46`)
- [x] 6.2 Confirm `.github/workflows/codex-plugin.yml` picks up the new plugin via `plugins/**` path trigger; local equivalent: `python3 scripts/converter.py` + `python3 -m pytest tests/codex/test_codex_extension.py -q` (38 passed). `PLUGIN_COMMAND_DIRS` in `tests/codex/test_codex_extension.py` updated to include `plugins/arckit-it4it/commands`
