# artifact-generation Delta — archimate-demanded-artefacts

## ADDED Requirements

### Requirement: ArchiMate-Representable ADM/OAA Artefacts Carry a Demanded PlantUML-ArchiMate View
The distribution source plugins `arckit-togaf-adm` and `arckit-oaa` SHALL give each ArchiMate-representable artefact a demanded **PlantUML-ArchiMate** view, in addition to any existing Mermaid diagram. The demanded set is fixed: `application-inventory`, `application-rationalization`, `business-capability-map`, `technology-architecture`, `transition-architecture` (in `arckit-togaf-adm`) and `oaa-adm-lite`, `product-architecture` (in `arckit-oaa`). Each demanded template SHALL carry exactly one PlantUML block whose first body line is the pinned `!include <archimate/Archimate>` line (PlantUML 1.2026.8, identical to the one asserted in `test_archimate_conformance.py`), and the matching command SHALL load `skills/plantuml-syntax/references/archimate.md` and SHALL fill that block when the artefact content is ArchiMate-representable, stereotyping elements into the artefact's mapped layer (Application / Business-Capability / Technology / Capability-incremental), observing the `ARCH` quality gate (≤ 12 elements per layer, realization edges point concrete→abstract, no unlabelled cross-layer edges). This SHALL be append-only: no new command and no new doc-type are introduced, and the pre-existing Mermaid blocks (ADM template fences, and the OAA `data-flow-diagram.mmd` sidecar) SHALL remain byte-for-byte present.

#### Scenario: ADM capability artefact gains an ArchiMate view
- **WHEN** the user runs `/arckit:business-capability-map`
- **THEN** the generated `capability-map` artefact contains its existing Mermaid mindmap/flowchart/quadrant blocks **and** a PlantUML-ArchiMate block (pinned include line) stereotyped into the Business/Capability layer

#### Scenario: OAA product artefact keeps its C4 and adds ArchiMate
- **WHEN** the user runs `/arckit:product-architecture`
- **THEN** the artefact retains the Mermaid C4 component diagram AND gains a PlantUML-ArchiMate Application-layer view; the Mermaid deliverable is not removed

#### Scenario: OAA data-flow artefact keeps its .mmd sidecar
- **WHEN** the user runs `/arckit:oaa-adm-lite`
- **THEN** the `data-flow-diagram.mmd` Mermaid deliverable is still produced and an additive PlantUML-ArchiMate Technology (systems real / deployment) view is present in the template

#### Scenario: Non-representable artefacts are untouched
- **WHEN** the user runs an ADM/OAA artefact not in the demanded set (e.g. `architecture-board`, `discovery`, `agile-governance`)
- **THEN** no PlantUML-ArchiMate block is added and no Mermaid block is altered

#### Scenario: Mermaid preservation is enforced
- **WHEN** the change is validated
- **THEN** `test_archimate_demanded.py` asserts every pre-change ` ```mermaid ` block (and the OAA `.mmd` sidecar) is byte-identical, so the additive edit cannot silently mutate kept Mermaid

#### Scenario: No registry or command change
- **WHEN** the change is applied
- **THEN** `config/doc-types.mjs` is unchanged, no new slash command is created, and `tests/plugin/test_archimate_conformance.py` still passes

### Requirement: ArchiMate-Representable Artefacts May Carry Optional ArchiMate Overlay Views
Beyond the demanded base-layer view, a demanded ArchiMate artefact MAY carry one or more **optional** ArchiMate overlay views. The optional set is fixed: **Motivation overlay** (drivers / goals / constraints), **Strategy-Capability overlay** (capabilities that realize the layer), and **Data-only view** (logical data objects and their cross-layer flows). Each optional overlay is additive to the demanded base view and is included only when the artefact content supports it:

- **Motivation overlay** when the artefact names at least one driver, goal, or constraint;
- **Strategy-Capability overlay** when it names at least one capability or strategy element;
- **Data-only view** when it defines at least one logical data object or cross-layer data flow.

When an overlay's supporting content is absent, that overlay is omitted and the artefact renders its demanded base view only (no error).

Overlay selection SHALL mirror the shared ArchiMate intake (`/arckit:archimate` Question 2: Motivation yes / no / capability-map, and the "Data only" option). A demanded template that cannot run the interactive interview SHALL default to including exactly the overlays whose supporting content is present in the artefact, and SHALL otherwise render the structural base view only.

When an optional overlay is included, the demanded base view SHALL remain present (an overlay never replaces or removes it), the pinned `!include <archimate/Archimate>` line SHALL be reused, realization edges SHALL still point concrete→abstract, and the `ARCH` element-count gate SHALL apply to the combined view: an overlay that would push a single layer above 12 elements SHALL be reduced to the most material ≤ 12 elements or split into an additional sequenced `ARCH` document — never silently dropped.

#### Scenario: Motivation overlay added when drivers are present
- **WHEN** a demanded `business-capability-map` artefact names drivers or goals
- **THEN** the generated PlantUML-ArchiMate view includes a Motivation overlay above the Business/Capability base layer with realization edges pointing base elements to the motivation elements, and the base layer view remains present

#### Scenario: optional overlay omitted when unsupported
- **WHEN** a demanded `application-inventory` artefact carries no motivation, capability, or data-object content
- **THEN** only the demanded structural Application-layer view is generated; no overlay block is emitted and no "not represented" error is raised

#### Scenario: element-count gate forces a split
- **WHEN** adding a Strategy-Capability overlay would put the combined view over 12 elements in a single layer
- **THEN** the overlay is reduced to the most material ≤ 12 elements or split into an additional sequenced `ARCH` document; the demanded base view is unchanged

#### Scenario: overlays are additive, never replacing demanded views
- **WHEN** an optional overlay is generated
- **THEN** the demanded base-layer ArchiMate view and all pre-existing Mermaid blocks remain byte-for-byte present

#### Scenario: non-representable artefacts get no overlay
- **WHEN** the artefact is not ArchiMate-representable (not in the demanded set)
- **THEN** no demanded view and no optional overlay are added
