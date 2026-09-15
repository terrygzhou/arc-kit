# Tasks — bpcm-capmap-level-refinement

## 1. TDD guard (RED → GREEN)
- [x] 1.1 Extend `tests/plugin/test_archimate_demanded.py`: the BPCM command names the top-down invariant + the simple(flatten)/complex(abstract + per-domain refinement) regimes + the 12-element threshold; the BPCM template carries the flattened + `{capmap_overview*}` + `{capmap_refinement*}` placeholders
- [x] 1.2 Run the extended tests — GREEN (and the pre-existing BPCM capmap guards stay green)

## 2. [Command] complexity-adaptive directive
- [x] 2.1 `plugins/arckit-togaf-adm/commands/business-capability-map.md`: state the top-down invariant, the regime threshold (`E ≤ 12` flatten vs `E > 12` abstract + per-L1-domain refinement), the capability-domain/sub-domain split gate, and the SVG render clause

## 3. [Template] regime placeholders
- [x] 3.1 `plugins/arckit-togaf-adm/templates/capability-map-template.md`: add the complexity-adaptive regime note + an abstract-overview block (`{capmap_overview_domains}`) + a per-domain refinement block (`{capmap_refinement_domain}`, `{capmap_refinement_edges}`)

## 4. [Reference] level-by-level idiom
- [x] 4.1 `plugins/arckit-claude/skills/plantuml-syntax/references/archimate.md`: add the top-down complexity-adaptive rendering note (simple flatten vs complex abstract + per-domain refinement, ≤ 12 gate)

## 5. Conformance, regen, validate, changelog
- [x] 5.1 `python3 -m pytest tests/plugin/test_archimate_demanded.py tests/plugin/test_archimate_conformance.py -q` — GREEN
- [x] 5.2 `python3 scripts/converter.py` (regenerate `extensions/*`, gitignored)
- [x] 5.3 `SKIP_NETWORK=1 ./scripts/ci-local.sh` (offline markdown/cross-ref/diagram checks)
- [x] 5.4 `openspec validate bpcm-capmap-level-refinement`
- [x] 5.5 `CHANGELOG.md` Unreleased entry; flip these tasks `[x]`; conventional commit (regenerated `extensions/*` stay uncommitted)
