# Tasks — bpcm-capmap-archimate

## 1. TDD guard (RED)
- [x] 1.1 Extend `tests/plugin/test_archimate_demanded.py`: the BPCM template carries a marked **capability-map ArchiMate view** block (distinct from the realization view) using `Strategy_Capability` + `Rel_Composition(..., "contains")`, and the BPCM command directive names the L1→L2 whole→part rule, the Level-3-optional rule, and the ≤ 12-element split gate
- [x] 1.2 Run the extended test — RED on the capability-map-view assertions

## 2. [Template] capability-map ArchiMate view (GREEN)
- [x] 2.1 Add a `## Capability Map (ArchiMate View)` block to `plugins/arckit-togaf-adm/templates/capability-map-template.md`: nested `Strategy_Capability` L1→L2 (+ optional L3) joined by `Rel_Composition(parent, child, "contains")`; keep the existing realization view and every Mermaid block byte-preserved
- [x] 2.2 Add the self-contained `.svg` delivery note to the new view (pinned `plantuml-1.2026.8.jar -tsvg`, offline)

## 3. [Command] directive (GREEN)
- [x] 3.1 Extend `plugins/arckit-togaf-adm/commands/business-capability-map.md` with the capability-map-view directive: whole→part edge rule, Level-3-optional, the ≤ 12-element split gate, and the SVG render clause for the new view
- [x] 3.2 Add a `### Capability-Map ArchiMate Nesting` reference note to `plugins/*/skills/plantuml-syntax/references/archimate.md` (`Rel_Composition` whole→part vs `Rel_Aggregation`; ≤ 12 split threshold; L3 optional)

## 4. Conformance, regen, validate, changelog
- [x] 4.1 `python3 -m pytest tests/plugin/test_archimate_demanded.py tests/plugin/test_archimate_conformance.py -q` — GREEN
- [x] 4.2 `python3 scripts/converter.py` (regenerate `extensions/*`)
- [x] 4.3 `npx markdownlint-cli2` over the changed source files
- [x] 4.4 `openspec validate bpcm-capmap-archimate`
- [x] 4.5 `CHANGELOG.md` Unreleased entry; flip tasks `[x]`; conventional commit (regenerated `extensions/*` stay uncommitted)
