# BPCM Capability Map in PlantUML-ArchiMate — design

## Context

The BPCM template renders its capability hierarchy only as a Mermaid mindmap
(`## Capability Map (Mermaid mindmap)`). Its one PlantUML-ArchiMate view is a
capability→target **realization** view (`Strategy_Capability` → target
components via `Rel_Realization`), which answers "which target component
realizes which capability" — it is not the capability hierarchy.

The ArchiMate stdlib (`!include <archimate/Archimate>`, pinned 1.2026.8)
declares `Strategy_Capability($alias, $label, $nest=0)` and the whole→part
relationship surface `Rel_Composition` / `Rel_Aggregation` (each with `_Up/_
Down/_Left/_Right` variants). A capability map is therefore expressible as
`Strategy_Capability` nodes joined by `Rel_Composition(parent, child,
"contains")` edges.

**Evidence (render-verified):** a Meridian BPCM hierarchy (3 L1 domains →
5 L2 sub-capabilities, 5 `Rel_Composition(..., "contains")` edges) rendered
cleanly with `java -jar plantuml-1.2026.8.jar -tsvg` against the local
ArchiMate stdlib into a self-contained SVG — all five `contains` labels
present, no non-W3C `http(s)` URL, offline-openable.

## Approach

Add ONE dedicated, additive ArchiMate view to the BPCM artefact (the
**capability map**), kept separate from the existing realization view.

- **Template:** a `## Capability Map (ArchiMate View)` block — nested
  `Strategy_Capability` L1 domains containing L2 sub-capabilities
  (`Rel_Composition(parent, child, "contains")`), optional L3 nesting,
  `LAYOUT_TOP_DOWN()`, and the pinned `!include <archimate/Archimate>`.
- **Command:** a directive that fills that block from the artefact's L1/L2
  (and, when defined, L3) tables, applies the whole→part rule and the
  ≤ 12 elements/layer split gate, and adds the SVG render clause.
- **Reference:** a short capability-map nesting note in
  `skills/plantuml-syntax/references/archimate.md`.
- **Delivery:** the view renders to a self-contained `.svg` per
  `archimate-svg-delivery` (pinned build, offline; inline source is the source
  of truth; the `.svg` is the only new rendered file).

## Decisions

- **Edge choice:** default to `Rel_Composition` (whole→part, parent owns
  child). Use `Rel_Aggregation` only where a sub-capability clearly retains
  standalone existence. Whole→part always points L1→L2 (never reversed).
- **Additive, byte-preserving:** the Mermaid mindmap and the existing
  capability→target realization view are untouched; the new view is appended.
- **Split gate:** when a single L1+L2 layer exceeds 12 elements, split at a
  capability-domain boundary into additional sequenced `ARCH` documents
  (cross-linked in Linked Artifacts) — never silently drop.
- **Level 3 optional:** emitted only when the artefact's Level 3 table is
  populated; otherwise omitted with no error.
- **No scope creep:** no other ADM/OAA artefact is modified.
