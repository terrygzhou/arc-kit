# BPCM Capability Map in PlantUML-ArchiMate — proposal

## Why

The BPCM (`/arckit:business-capability-map`) artefact renders its capability
map (the Level 1 domains → Level 2 sub-capabilities → Level 3
detailed-capability hierarchy) exclusively as a **Mermaid mindmap**. The single
PlantUML-ArchiMate view the template carries today is a *capability→target
realization* view (`Strategy_Capability` → target components), which answers
"which target components realize which capability" — not the capability
hierarchy itself.

There is therefore no ArchiMate rendering of the capability hierarchy. Because
PlantUML does not render in GitHub markdown, and the `archimate-svg-delivery`
policy renders ArchiMate-representable views to self-contained `.svg`, the
capability map (a Strategy/Capability-tier architecture view) is
*ArchiMate-representable* but currently has no ArchiMate view and no SVG.

PlantUML-ArchiMate *can* express a capability hierarchy: nested
`Strategy_Capability` elements joined by `Rel_Composition` (whole→part
"contains") edges. This was verified by rendering a Meridian BPCM hierarchy
(L1 domains → L2 sub-capabilities) with the pinned `plantuml-1.2026.8.jar` +
local ArchiMate stdlib to a self-contained SVG (all `contains` edges present,
no non-W3C URLs).

## What Changes

- Add a **dedicated capability-map ArchiMate view** to the BPCM template +
  command, distinct from the existing realization view. It models the L1 → L2
  hierarchy as `Strategy_Capability` nodes joined by
  `Rel_Composition(L1, L2, "contains")` edges; Level 3 is optional and
  included only when the artefact defines Level 3 detail.
- The view is additive and byte-preserves the Mermaid mindmap and the existing
  realization PlantUML view; it is rendered to a self-contained `.svg` per the
  `archimate-svg-delivery` policy (pinned `plantuml-1.2026.8.jar -tsvg`,
  offline, no external URLs).
- Add a notation reference note for capability-map nesting
  (`Rel_Composition` whole→part; `Rel_Aggregation` where parts retain
  standalone existence; ≤ 12 elements/layer gate).
- No new doc-type, slash command, or registry entry.

## Capabilities

### Added Capabilities
(none — no new capability; this is a requirement on an existing one)

### Modified Capabilities
- `artifact-generation` gains a requirement:
  - **BPCM Capability Maps Are Rendered as PlantUML-ArchiMate Views** — the
    BPCM artefact of the `arckit-togaf-adm` distribution source plugin SHALL
    render its capability map (L1→L2→L3 hierarchy) as a PlantUML-ArchiMate
    Strategy-layer view (nested `Strategy_Capability` joined by
    `Rel_Composition` whole→part edges), additive to and byte-preserving the
    Mermaid mindmap, delivered as a self-contained `.svg`.

## Non-goals

- No replacement of the Mermaid mindmap or the existing realization view.
- No BPCM edits outside the BPCM template + command + ArchiMate reference +
  one focused test group; other ADM/OAA artefacts unchanged.
- No new diagram types beyond ArchiMate; no D2 / archify.
- No nesting beyond Level 3 (Level 3 optional); the ≤ 12 elements/layer gate
  still applies — above the gate, split by capability domain.

## Impact

- Edits: `plugins/arckit-togaf-adm/templates/capability-map-template.md` (new
  capability-map view block + SVG delivery note),
  `plugins/arckit-togaf-adm/commands/business-capability-map.md` (directive),
  `plugins/*/skills/plantuml-syntax/references/archimate.md` (capability-map
  nesting note), 1 focused test group, `CHANGELOG.md`, this change's delta
  spec.
- Regenerated (gitignored): `extensions/*`.
