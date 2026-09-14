# ArchiMate Coverage Expansion — design

## Context

`archimate-demanded-artefacts` (shipped) established the 7-artefact demanded
structural-view pattern: an append-only `### PlantUML ArchiMate View` section per
template + a matching command directive, gated by `test_archimate_demanded.py`
and byte-preserved Mermaid. This change reuses that exact pattern and extends it
on three axes: breadth (8-type optional menu), coverage (17-artefact demanded
base set), and a first companion-view implementation batch.

## Goals / Non-Goals

**Goals:** full 17-artefact demanded base coverage; a fixed 8-type optional menu
with a per-artefact mapping; 4 highest-value companion views implemented;
everything append-only, byte-preserving, TDD-guarded, one reviewable edit set.

**Non-Goals:** all-8-types-for-all-17 in one batch; new commands/doc-types;
Mermaid edits; D2; core `/arckit:archimate` changes.

## Overlay vs companion (the core distinction)

- **Overlay** (Motivation / Strategy-Capability / Data-only): elements are
  appended into the base view's `{archimate_elements}` *within the budget*.
- **Companion view** (Behavior / Structure / Physical / Impl & Migration /
  Stakeholder-Requirement): a **second pinned `@startuml` block** in a
  `### PlantUML ArchiMate Companion View (<Type>)` section, emitted as a
  **separate sequenced `ARCH` document** — never merged into the base view.

## Block shapes

Companion view section (additive, after the base view):

    ```plantuml
    @startuml
    !include <archimate/Archimate>
    title {<artefact>_<type>_companion_title}
    ' Companion layer elements
    {companion_<type>_elements}
    ' Realization/relationship edges (concrete->abstract)
    {companion_<type>_relationships}
    {companion_<type>_layout}
    @enduml
    ```

## TDD Red -> Green

- **RED** — extend `tests/plugin/test_archimate_demanded.py` with three groups:
  1. all **17** ADM/OAA templates carry a base-view pinned `!include` block;
  2. the **4 Batch-1** artefacts carry a companion-view block of the right type
     (Impl/Migration for `transition-architecture` + `gap-analysis`; Physical for
     `technology-architecture` + `oaa-adm-lite`);
  3. the **13 non-demanded** commands reference `references/archimate.md` + the
     base-view fill directive; and every pre-change ` ```mermaid ` block (fixture
     extended to the 10 newly-in-scope templates) is still byte-identical.
- **GREEN** — append base-view blocks (10 new artefacts), companion blocks (4),
  and command directives (load reference; fill when ArchiMate-representable;
  ≤ 12/layer; realization concrete→abstract; split-never-drop).

## Batch ordering

- **Batch 1 (this change):** 10 new base views + 4 companion views + the 8-type
  spec mapping.
- **Batch 2 (follow-up change):** remaining optional overlays / companion views
  per the mapping table, driven by the same menu + invariants.

## Risks

- **Thin/non-representable base content** (e.g. `discovery`,
  `architecture-repository`): mitigate with the documented "not represented in
  ArchiMate" single-element stub (never a blank block).
- **Element-budget overflow** on companion views: enforce split-never-drop.
- **Fixture scope growth**: the SHA-256 pre-change Mermaid fixture gains the 10
  newly-in-scope templates; regenerate it in Task 0.1 before GREEN edits.
