# Tasks — bmm-adoption

## 0. BMM projection spike (gates tasks 2–5)
- [x] 0.1 Extract the BMM 1.3 element/relationship catalogue (from the OMG spec PDF) and draft `plugins/arckit-claude/references/bmm-reference.md`: element table, relationship table, mapping tables (BMM ↔ ArchiMate Motivation/Strategy tiers ↔ ArcKit doc-types STKE/SOBC/STRAT/ROAD/BPCM/ARCH), BIZBOK S&SA + Green-Book alignment notes, gate criteria G1–G5
- [x] 0.2 Render BMM-projection samples with the pinned PlantUML 1.2026.8 jar: (a) stakeholder → outcome + driver influence, (b) goal → capability realization + capability nesting (`Rel_Composition`), (c) stereotyped Objective/Measure/Strategic Theme with legend; save `.puml` + committed SVGs under `tests/fixtures/archimate/bmm/`
- [x] 0.3 Record the stereotyped encodings and relationship vocabulary (`Rel_Influence`, `Rel_Realization`, `Rel_Composition`, `Rel_Flow`, legend-defined "contributes to") in a scratch note that becomes `references/archimate.md` § BMM Projection; confirm no required edge is unexpressible (fallback: legend-defined custom edge)

## 1. TDD guard (RED)
- [x] 1.1 Add `tests/plugin/test_bmm_conformance.py`: `BMM` present in `DOC_TYPES` (category Planning) and the `commands/pages.md` known-artifact-types table, ABSENT from `MULTI_INSTANCE_TYPES`/`SUBDIR_MAP` (single-instance root-level); `commands/bmm.md` frontmatter (`doc-type: BMM`, `effort: max`, handoffs strategy/roadmap/sobc/archimate, intake-interview bullet present); `templates/bmm-template.md` exists with pipeline sections A1 (all 9 sections + 14-field Document Control + generation footer) and no unresolved placeholders; `references/bmm-reference.md` exists with mapping tables; `references/archimate.md` carries a `## BMM Projection` section + `tests/fixtures/archimate/bmm/` fixture; `SKILL.md` mapping row; every tracked `quality-checklist.md` copy carries a `BMM` section; `docs/guides/bmm.md` exists; 77 `.md` files in `commands/`
- [x] 1.2 Run the new test — RED on every assertion (nothing exists yet); this is the red baseline

## 2. Doc-type registration (GREEN)
- [x] 2.1 `config/doc-types.mjs`: add `'BMM': { name: 'Business Motivation Model', category: 'Planning' }` to `DOC_TYPES` only (no `MULTI_INSTANCE_TYPES`, no `SUBDIR_MAP`)
- [x] 2.2 `commands/pages.md`: add the `BMM` row to the known-artifact-types table
- [x] 2.3 `python3 scripts/check-doc-type-registry.py` + `python3 scripts/check_doctype_collisions.py` + `python3 scripts/check-multi-instance-parity.py` — GREEN

## 3. Command + template + reference (GREEN)
- [x] 3.1 Author `plugins/arckit-claude/commands/bmm.md`: context reads (STKE + PRIN MANDATORY — stop-and-ask if missing; SOBC/ROAD/WARD/RISK RECOMMENDED; external strategy docs with citation markers per `references/citation-instructions.md`); intake interview in ONE call, max 2 rounds (Q1 model scope — full/motivation-only/strategy-only; Q2 companion menu multiSelect — base-only recommended, +goal ladder / +case & assumptions overlay / +alignment view / +Mermaid mindmap; skip rules when arguments name scope/menu); load `references/bmm-reference.md` + `skills/plantuml-syntax/references/archimate.md` § BMM Projection; generation per design § Artefact Pipeline (Stage 1 [A1] → Stage 2 [A2]/[A3] sequenced ARCH docs via `generate-document-id.mjs --next-num`, never renumbering existing sequences; Stage 3 selected companions; [D*] self-contained SVG delivery clause — pinned `plantuml-1.2026.8` jar, offline, no non-local URLs); gates G1–G5 with the 3-iteration remediation loop; handoffs (strategy, roadmap, sobc with UK-regime condition, archimate)
- [x] 3.2 Author `plugins/arckit-claude/templates/bmm-template.md`: pipeline sections 1–9 (stakeholders & outcomes + matrix, ladder, drivers, assumptions, case for/against, impact factors, themes→capabilities→courses of action→resources, traceability + external references, Mermaid mindmap companion block), canonical 14-field Document Control + generation footer
- [x] 3.3 Finalise `plugins/arckit-claude/references/bmm-reference.md` (from 0.1/0.3)
- [x] 3.4 Re-run `tests/plugin/test_bmm_conformance.py` — GREEN for template/command/reference assertions

## 4. Diagram layer (append-only)
- [x] 4.1 `skills/plantuml-syntax/references/archimate.md`: add `## BMM Projection` section (stereotyped encodings, relationship vocabulary, legend rules, sample-fixture link) — append-only; extend the SHA-256 byte-preservation fixture (archimate-demanded-artefacts pattern) so all pre-existing Mermaid/content stays byte-identical
- [x] 4.2 `skills/plantuml-syntax/SKILL.md`: mapping-table row (BMM motivation/strategy views → `references/archimate.md` § BMM Projection); verify the existing `**/ARC-*-ARCH-*.md` glob already covers BMM-carrying views (no new glob needed — assert in the conformance test)

## 5. Quality checklist + docs lockstep
- [x] 5.1 Add the `BMM -- Business Motivation Model` section (G1–G5 criteria, pinned include line, legend-for-custom-notation, single-tier stereotyping) to the canonical `references/quality-checklist.md`; propagate with `python3 scripts/sync-shared-assets.py` then `--check`; post-edit grep asserts the section in every tracked copy
- [x] 5.2 Append-only traceability clauses in `strategy.md` (STRAT consumes BMM Strategic Themes when present) and `sobc.md` (5-case ↔ BMM Case section mapping, UK-regime note) — byte-preserve existing content
- [x] 5.3 `docs/guides/bmm.md` + guides index; `docs/llms.txt` command entry; `docs/OAA-PLUGIN-MAPPING.md` pointer (BMM ↔ OASTR / ADM `discovery` motivation views); verify `check-guide-parity.py` + `check-guide-site-links.py`
- [x] 5.4 `npx markdownlint-cli2` over all changed `.md` files

## 6. Regenerate, test, validate
- [x] 6.1 `python scripts/converter.py` (regenerate all 7 `extensions/*` targets incl. new Codex skill `arckit-bmm`); commit regenerated trees (lockstep policy, cf. `ba8f576f`)
- [x] 6.2 `python3 -m pytest tests/plugin/test_bmm_conformance.py tests/plugin/test_commands_structure.py tests/codex/test_codex_extension.py -q` (+ relevant `tests/plugin/*.mjs`)
- [x] 6.3 `SKIP_NETWORK=1 ./scripts/ci-local.sh` — all steps green
- [x] 6.4 `openspec validate bmm-adoption`

## 7. Release
- [x] 7.1 `CHANGELOG.md` Unreleased entry (house style: pipeline stages, registration, BMM-projection rule, guards, OpenSpec `bmm-adoption`)
- [x] 7.2 `./scripts/bump-version.sh 6.10.0`
- [x] 7.3 Conventional commit staging: command + template + reference + archimate.md § BMM Projection + SKILL.md + doc-types.mjs + pages.md + checklist copies + strategy/sobc clauses + docs + new test + `openspec/changes/bmm-adoption/` + CHANGELOG + regenerated `extensions/*`
