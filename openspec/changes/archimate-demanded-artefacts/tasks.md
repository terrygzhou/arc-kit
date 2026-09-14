# Tasks — archimate-demanded-artefacts

## 0. Baseline snapshot (enables the "Mermaid preserved" diff assertion)
- [x] 0.1 Record a pre-change SHA-256 of every existing ` ```mermaid ` block in the 5 ADM templates (the only tracked Mermaid source), save under `tests/plugin/fixtures/archimate-demanded/prechange_mermaid_blocks.json`. (The OAA `data-flow-diagram.mmd` is a runtime deliverable generated into `projects/`, not a tracked source file, so it is not snapshot-able.)
- [x] 0.2 Note the pinned include line string from `tests/plugin/test_archimate_conformance.py` to reuse verbatim

## 1. TDD guard (RED)
- [x] 1.1 Add `tests/plugin/test_archimate_demanded.py` asserting, per artefact:
      - ADM templates `application-inventory`, `rationalization`, `capability-map`, `tech-architecture`, `transition-architecture` each contain a PlantUML block whose first body line is the pinned `!include <archimate/Archimate>`
      - OAA templates `oaa-adm-lite`, `product-architecture` carry the same block
      - the 5 ADM + 2 OAA commands each reference `skills/plantuml-syntax/references/archimate.md` and instruct filling the ArchiMate block when ArchiMate-representable
      - every pre-change ` ```mermaid ` block hash from Task 0.1 is still present (byte-identical)
- [x] 1.2 Run the new test — RED on the "block present" assertions (nothing added yet)

## 2. arckit-togaf-adm templates (GREEN)
- [x] 2.1 `plugins/arckit-togaf-adm/templates/application-inventory-template.md`: append a `### PlantUML ArchiMate View` section (Application layer) — Mermaid blocks untouched
- [x] 2.2 `.../rationalization-template.md`: append ArchiMate View (Application + Capability)
- [x] 2.3 `.../capability-map-template.md`: append ArchiMate View (Business / Capability)
- [x] 2.4 `.../tech-architecture-template.md`: append ArchiMate View (Technology)
- [x] 2.5 `.../transition-architecture-template.md`: append ArchiMate View (Capability, incremental target)

## 3. arckit-oaa templates (GREEN)
- [x] 3.1 `plugins/arckit-oaa/templates/oaa-adm-lite-template.md`: append ArchiMate View (Technology systems real / deployment + Application); keep the `data-flow-diagram.mmd` deliverable row
- [x] 3.2 `.../product-architecture-template.md`: append ArchiMate View (Application layer); keep the C4 component diagram

## 4. arckit-togaf-adm commands (GREEN)
- [x] 4.1 Add the ArchiMate directive (load `references/archimate.md`; fill block when ArchiMate-representable; ≤ 12 elements/layer; realization concrete→abstract) to `application-inventory.md`, `application-rationalization.md`, `business-capability-map.md`, `technology-architecture.md`, `transition-architecture.md`

## 5. arckit-oaa commands (GREEN)
- [x] 5.1 Add the same ArchiMate directive to `oaa-adm-lite.md` and `product-architecture.md`, explicitly noting the existing Mermaid deliverable is retained (additive, not replacement)

## 6. Conformance (GREEN)
- [x] 6.1 Re-run `tests/plugin/test_archimate_demanded.py` — GREEN
- [x] 6.2 Re-run `tests/plugin/test_archimate_conformance.py` — still GREEN (no regression)

## 7. Regen, test, validate, changelog
- [x] 7.1 `python scripts/converter.py` (regenerate `extensions/*`, incl. the merged ADM/OAA archimate views)
- [x] 7.2 `python3 -m pytest tests/plugin/test_archimate_demanded.py tests/plugin/test_archimate_conformance.py tests/plugin/test_commands_structure.py -q`
- [x] 7.3 `npx markdownlint-cli2` over the changed files
- [x] 7.4 `openspec validate archimate-demanded-artefacts`
- [x] 7.5 `CHANGELOG.md` Unreleased entry; conventional commit staging: 7 templates + 7 commands + new test + `openspec/changes/archimate-demanded-artefacts/` + CHANGELOG (regenerated `extensions/*` stay uncommitted)
