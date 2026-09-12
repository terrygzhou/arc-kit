# Tasks — plantuml-archimate-adoption

## 0. API spike (network required; gates tasks 1–6)
- [x] 0.1 Fetch `https://plantuml.com/archimate-diagram` + the ArchiMate stdlib source (include path, element types per layer, relationship functions, colour library); record findings in a scratch note
- [x] 0.2 Render a three-layer sample (business process → application component realization + logical data object + one technology node) with the pinned PlantUML version; save `.puml` + rendered SVG under `tests/fixtures/archimate/`
- [x] 0.3 Write the Pinned API section of `plugins/arckit-claude/skills/plantuml-syntax/references/archimate.md` (include line, element/relationship surface, minimum version, public-URL length behaviour, notation decision: native ArchiMate vs C4-PlantUML fallback per design)
- [x] 0.4 If native support is insufficient for the required relationship types: switch to the fallback notation and re-run 0.2/0.3 (decision recorded in the Pinned API section)

## 1. TDD guard (RED)
- [x] 1.1 Add `tests/plugin/test_archimate_conformance.py`: `ARCH` present in `DOC_TYPES` + `MULTI_INSTANCE_TYPES` + `SUBDIR_MAP` → `diagrams`; `archimate-template.md` exists and carries the pinned `!include` line and no unresolved `{placeholder}`; `commands/archimate.md` frontmatter has `doc-type: ARCH` + `effort: high`; every tracked `quality-checklist.md` copy carries an `ARCH` section; `docs/DIAGRAMS.md` maps the generated path to `/arckit:archimate`
- [x] 1.2 Run the new test — RED on every assertion (nothing exists yet); this is the red baseline

## 2. Doc-type registration (GREEN)
- [x] 2.1 `config/doc-types.mjs`: add `'ARCH'` to `DOC_TYPES` (name: `ArchiMate View`, category `Architecture`), to `MULTI_INSTANCE_TYPES`, and `SUBDIR_MAP` (`'ARCH': 'diagrams'`)
- [x] 2.2 `commands/pages.md`: add the `ARCH` row to the known-artifact-types table
- [x] 2.3 `python3 scripts/check-doc-type-registry.py` — GREEN

## 3. Command + template (GREEN)
- [x] 3.1 Author `plugins/arckit-claude/commands/archimate.md`: context read (REQ/HLD/DLD/WARD per diagram.md Step 1 patterns), intake (Q1 layers + data, Q2 motivation/capability — single AskUserQuestion call, max 2 rounds), load `references/archimate.md`, generation instructions, ArchiMate quality-gate table (per design: single-layer stereotyping, realization direction, ≤ 12 elements/layer) with the 3-iteration remediation loop, output to `projects/{p}/diagrams/` via `generate-document-id.mjs 001 ARCH --next-num`
- [x] 3.2 Author `plugins/arckit-claude/templates/archimate-template.md` mirroring `architecture-diagram-template.md` structure: PlantUML block (pinned include line), Element Inventory, Layer & Realization Traceability table, Integration Points, NFR Coverage, Linked Artifacts, canonical 14-field Document Control + generation footer
- [x] 3.3 Re-run `tests/plugin/test_archimate_conformance.py` — GREEN for the template/command assertions

## 4. Skill reference + SKILL.md
- [x] 4.1 Complete `references/archimate.md` beyond § Pinned API: notation cheat-sheet, layer-tier ordering rules, realization/relationship direction rules, colour standards, element-count thresholds, antipatterns (cross-layer noise, unlabelled edges, mixing C4 + ArchiMate elements in one diagram)
- [x] 4.2 `skills/plantuml-syntax/SKILL.md`: mapping-table row (ArchiMate layer views → `references/archimate.md`) + add `**/ARC-*-ARCH-*.md` to the skill's `paths:` globs

## 5. Quality checklist (lockstep)
- [x] 5.1 Add the `ARCH -- ArchiMate View` section (single-layer stereotyping, realization direction, ≤ 12 elements/layer, pinned include line, legend for custom notation) to the canonical `plugins/arckit-claude/references/quality-checklist.md`
- [x] 5.2 Propagate to all tracked copies: `python3 scripts/sync-shared-assets.py` then `--check`; post-edit grep asserts the `ARCH` section exists in every tracked copy

## 6. Docs mapping
- [x] 6.1 `docs/DIAGRAMS.md`: under "ArchiMate Semantics in D2", add the mapping pointer (generated path = `/arckit:archimate` → `ARC-NNN-ARCH-NNN-v1.0.md` in PlantUML ArchiMate notation; D2 idiom remains hand-authored sidecars only)

## 7. Regenerate, test, validate
- [x] 7.1 `python scripts/converter.py` (regenerate `extensions/*`, incl. new Codex skill `arckit-archimate`)
- [x] 7.2 `python3 -m pytest tests/plugin/test_archimate_conformance.py tests/plugin/test_commands_structure.py tests/codex/test_codex_extension.py -q`
- [x] 7.3 `npx markdownlint-cli2` over the changed files
- [x] 7.4 `openspec validate plantuml-archimate-adoption`
- [x] 7.5 `CHANGELOG.md` Unreleased entry; conventional commit staging: command + template + reference + SKILL.md + doc-types.mjs + pages.md + checklist copies + docs/DIAGRAMS.md + new test + `openspec/changes/plantuml-archimate-adoption/` + CHANGELOG (regenerated `extensions/*` stay uncommitted)
