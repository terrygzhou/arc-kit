# Tasks — archimate-coverage-expansion

## 0. Baseline snapshot (enables Mermaid byte-preservation for the new scope)
- [x] 0.1 Extend `tests/plugin/fixtures/archimate-demanded/prechange_mermaid_blocks.json` to record the current ` ```mermaid ` blocks of the **10 newly-in-scope** ADM/OAA templates (7 ADM + 3 OAA) so byte-preservation is enforced when base views are added
- [x] 0.2 Note the pinned include line + the companion-view block shape (from `design.md`) to reuse verbatim

## 1. TDD guard (RED)
- [x] 1.1 Extend `tests/plugin/test_archimate_demanded.py` with three groups:
      - all **17** ADM/OAA templates carry a base-view pinned `!include <archimate/Archimate>` block
      - the **4 Batch-1** artefacts carry a companion-view block of the right type (Impl/Migration for `transition-architecture` + `gap-analysis`; Physical for `technology-architecture` + `oaa-adm-lite`)
      - the **13 non-demanded** commands reference `skills/plantuml-syntax/references/archimate.md` + a base-view fill directive
      - every pre-change ` ```mermaid ` block hash from Task 0.1 is still byte-identical
- [x] 1.2 Run the extended test — RED on the base-view and companion-view assertions

## 2. [Coverage] base views for the 10 non-demanded artefacts (GREEN)
- [x] 2.1 ADM `adm-preliminary`: append base-view block (Strategy layer) + command directive
- [x] 2.2 ADM `architecture-board`: append base-view block (Strategy / governance) + directive
- [x] 2.3 ADM `architecture-change`: append base-view block (Implementation increments) + directive
- [x] 2.4 ADM `architecture-repository`: append base-view block (Structure / catalog) + directive
- [x] 2.5 ADM `data-architecture`: append base-view block (Application/Technology data objects) + directive
- [x] 2.6 ADM `discovery`: append base-view block (Motivation) + directive (documented-stub rule)
- [x] 2.7 ADM `gap-analysis`: append base-view block (Capability target vs current) + directive
- [x] 2.8 OAA `agile-governance`: append base-view block (Strategy / governance capability) + directive
- [x] 2.9 OAA `agile-security`: append base-view block (Technology / Application security controls) + directive
- [x] 2.10 OAA `agile-strategy`: append base-view block (Strategy / value stream) + directive

## 3. [Batch 1] companion views (GREEN)
- [x] 3.1 `transition-architecture` + `gap-analysis`: append an **Implementation & Migration** companion-view block (plateaus / work packages / deliverables) + directive
- [x] 3.2 `technology-architecture` + `oaa-adm-lite`: append a **Physical** companion-view block (facilities / equipment / communication networks) + directive
- [x] 3.3 Command directives for the 4: companion views are separate sequenced `ARCH` docs (not merged into the base view); ≤ 12/layer; realization concrete→abstract; split-never-drop

## 4. [Breadth] spec mapping (spec-only, no code)
- [x] 4.1 The 8-type optional menu + per-artefact mapping + overlay/companion distinction + invariants are captured in `specs/artifact-generation/spec.md` (this change) — no template/command edits here

## 5. Conformance, regen, validate, changelog
- [x] 5.1 `python3 -m pytest tests/plugin/test_archimate_demanded.py tests/plugin/test_archimate_conformance.py -q` — GREEN
- [x] 5.2 `python3 scripts/converter.py` (regenerate `extensions/*`, incl. merged base + companion views)
- [x] 5.3 `npx markdownlint-cli2` over the changed source files
- [x] 5.4 `openspec validate archimate-coverage-expansion`
- [x] 5.5 `CHANGELOG.md` Unreleased entry; conventional commit staging: 10 base-view templates + commands, 4 companion-view templates + commands, extended test + fixture, `openspec/changes/archimate-coverage-expansion/`, CHANGELOG (regenerated `extensions/*` stay uncommitted)
