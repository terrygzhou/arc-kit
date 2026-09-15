# artifact-generation Delta — bpcm-capmap-archimate

## ADDED Requirements

### Requirement: BPCM Capability Maps Are Rendered as PlantUML-ArchiMate Views
The Business Capability Map (BPCM) artefact of the distribution source plugin
`arckit-togaf-adm` SHALL render its capability map — the Level 1 capability
domains, Level 2 sub-capabilities, and (when the artefact defines Level 3
detail) Level 3 detailed capabilities — as a dedicated **PlantUML-ArchiMate
Strategy/Capability view**, in addition to the Mermaid mindmap. The view SHALL:

- model each Level 1 domain and Level 2 sub-capability as a `Strategy_Capability`
  element, and Level 3 detailed capabilities as nested `Strategy_Capability`
  elements (only when the artefact defines Level 3 detail);
- join parent to child with a whole→part edge — `Rel_Composition(parent, child,
  "contains")` by default (or `Rel_Aggregation` where a sub-capability retains
  standalone existence) — so the hierarchy reads top-down (L1 domain containing
  its L2 sub-capabilities);
- be additive and byte-preserve the existing Mermaid mindmap AND the BPCM's
  existing capability→target realization PlantUML view;
- respect the ≤ 12 elements/layer gate: when a single L1+L2 layer exceeds 12
  elements the map SHALL be split at a natural capability-domain boundary into
  additional sequenced `ARCH` documents (cross-linked in Linked Artifacts) —
  never silently dropped;
- be delivered as a rendered **self-contained `.svg`** per the
  `archimate-svg-delivery` policy (pinned `plantuml-1.2026.8.jar -tsvg`,
  offline, no non-W3C `http(s)` URL, `xlink:href` limited to local `#anchors`;
  the inline PlantUML source is the source of truth and the `.svg` is the only
  new rendered file).

#### Scenario: capability map rendered as an ArchiMate view
- **WHEN** the user runs `/arckit:business-capability-map` for a project
- **THEN** the generated BPCM carries a PlantUML-ArchiMate capability-map view whose `Strategy_Capability` L1 domains contain their L2 sub-capabilities via `Rel_Composition(..., "contains")` edges, in addition to the unchanged Mermaid mindmap

#### Scenario: whole→part edge direction is parent→child
- **WHEN** a Level 1 domain "Policy & Underwriting" contains sub-capability "Decisioning"
- **THEN** the edge is `Rel_Composition("Policy & Underwriting", "Decisioning", "contains")` (whole→part, L1→L2), never the reverse

#### Scenario: level 3 included only when defined
- **WHEN** the artefact defines Level 3 detailed capabilities, each L3 element is a nested `Strategy_Capability` under its L2 parent
- **WHEN** it does not define Level 3 detail, no L3 elements are emitted and no error is raised

#### Scenario: hierarchy above the 12-element gate is split
- **WHEN** a single L1+L2 capability layer names more than 12 elements
- **THEN** the map is split at a capability-domain boundary into an additional sequenced `ARCH` document (cross-linked in Linked Artifacts); the Mermaid mindmap and the existing realization view are unchanged

#### Scenario: SVG self-containment is verified
- **WHEN** the capability-map `.svg` is rendered
- **THEN** it contains no `http(s)` URL other than the W3C `2000/svg` / `1999/xlink` namespace declarations and `xlink:href` limited to local `#anchors`, and it opens and renders fully offline
