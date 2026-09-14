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
