# Tasks — archimate-svg-rendering-adm-oaa

## 1. TDD guard (RED)
- [x] 1.1 Extend `tests/plugin/test_archimate_demanded.py`: all **17 base** + **4 companion** commands carry the SVG-render clause (`plantuml-1.2026.8.jar -tsvg` + `Offline Self-Contained SVG Rendering`); all **17 base** templates carry a "self-contained `.svg`" delivery note (companion templates ≥ 2)
- [x] 1.2 Run the extended test — RED on the SVG-delivery assertions

## 2. [Commands] SVG-render clause (GREEN)
- [x] 2.1 Append a `## Render the ArchiMate view(s) to self-contained SVG(s)` clause to all **17 base-view** commands (`arckit-togaf-adm` + `arckit-oaa`)
- [x] 2.2 Ensure the **4 companion-view** commands (transition-architecture, gap-analysis, technology-architecture, oaa-adm-lite) cover their companion view in the same clause

## 3. [Templates] delivery note (GREEN)
- [x] 3.1 Add an "Artefact delivery: self-contained `.svg`" bullet to the "View this diagram" section of all **17 base** templates
- [x] 3.2 Add the same delivery bullet to the **4 companion** template sections (Impl/Migration × 2, Physical × 2)

## 4. Conformance, regen, validate, changelog
- [x] 4.1 `python3 -m pytest tests/plugin/test_archimate_demanded.py tests/plugin/test_archimate_conformance.py -q` — GREEN
- [x] 4.2 `python3 scripts/converter.py` (regenerate `extensions/*`)
- [x] 4.3 `npx markdownlint-cli2` over the changed source files
- [x] 4.4 `openspec validate archimate-svg-rendering-adm-oaa`
- [x] 4.5 `CHANGELOG.md` Unreleased entry; flip tasks `[x]`; conventional commit (regenerated `extensions/*` stay uncommitted)
