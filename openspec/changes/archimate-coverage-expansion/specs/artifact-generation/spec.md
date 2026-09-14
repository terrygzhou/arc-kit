# artifact-generation Delta — archimate-coverage-expansion

## ADDED Requirements

### Requirement: All ADM/OAA Artefacts Carry a Demanded PlantUML-ArchiMate Base View
Every artefact of the distribution source plugins `arckit-togaf-adm` (12) and `arckit-oaa` (5) SHALL carry exactly one demanded **base-layer** PlantUML-ArchiMate structural view, in addition to any existing Mermaid diagram. The demanded base set is the full **17-artefact** list (superseding the 7-artefact demanded set of `archimate-demanded-artefacts`). Each demanded template SHALL carry one PlantUML fenced block whose first body line is the pinned `!include <archimate/Archimate>` line (identical to the one asserted in `test_archimate_conformance.py`), and the matching command SHALL load `skills/plantuml-syntax/references/archimate.md` and fill that block when ArchiMate-representable. The per-artefact base-layer mapping is:

| Artefact | Base layer |
|---|---|
| `application-inventory` | Application |
| `application-rationalization` | Application + Capability |
| `business-capability-map` | Business / Capability |
| `technology-architecture` | Technology |
| `transition-architecture` | Capability (incremental target) |
| `adm-preliminary` | Strategy (scope / drivers) |
| `architecture-board` | Strategy (governance / capability) |
| `architecture-change` | Implementation (change increments) |
| `architecture-repository` | Structure (catalog objects) |
| `data-architecture` | Application/Technology data objects |
| `discovery` | Motivation (drivers / goals) |
| `gap-analysis` | Capability (target vs current) |
| `oaa-adm-lite` | Technology (systems real / deployment) + Application |
| `product-architecture` | Application |
| `agile-governance` | Strategy (governance capability) |
| `agile-security` | Technology / Application (security controls) |
| `agile-strategy` | Strategy (capabilities / value stream) |

An artefact whose content is thin for its mapped layer SHALL still render a minimal structural slice (≥ 1 element). A genuinely non-representable artefact SHALL render a single documented "not represented in ArchiMate" stub element, never a blank block. This SHALL be append-only and SHALL byte-preserve every existing Mermaid block and the OAA `.mmd` sidecar.

#### Scenario: a previously non-demanded artefact gains a base view
- **WHEN** the user runs `/arckit:gap-analysis`
- **THEN** the generated artefact contains its existing Mermaid block AND a PlantUML-ArchiMate base view stereotyped into the Capability layer (target vs current), with the pinned include line

#### Scenario: a non-representable artefact renders a documented stub
- **WHEN** an artefact's content cannot be mapped to its layer (e.g. `discovery` has no drivers recorded)
- **THEN** the ArchiMate block renders a single "not represented in ArchiMate" stub element with a one-line rationale, not a blank block

#### Scenario: Mermaid preservation is enforced for the full set
- **WHEN** the change is validated
- **THEN** the extended SHA-256 fixture asserts every pre-change ` ```mermaid ` block across all 17 templates (and the OAA `.mmd` sidecar) is byte-identical

### Requirement: Optional ArchiMate Diagrams — 8-Type Menu with Per-Artefact Mapping
Beyond the demanded base view, an artefact MAY carry **optional** ArchiMate diagrams. The optional set is fixed at **8 types**: **3 overlays** — Motivation, Strategy/Capability, Data-only (each adds elements *onto* the base view) — and **5 companion single-layer views** — Behavior, Structure, Physical, Implementation & Migration, Stakeholder/Requirement (each is a separate sequenced `ARCH` document, not merged into the base view). An optional diagram is included only when the artefact content supports it, per this fixed per-artefact best-fit menu:

| Artefact | Optional menu (B=Behavior, St=Structure, Ph=Physical, I=Impl/Migration, K=Stakeholder/Req, M=S/C/M as overlays: M=Motivation, S=Strategy/Cap, D=Data-only) |
|---|---|
| `application-inventory` | B, St, D, S |
| `application-rationalization` | M, S, B |
| `business-capability-map` | S, M, B, I |
| `technology-architecture` | Ph, D, St, B |
| `transition-architecture` | I, M, B |
| `adm-preliminary` | K, M, B |
| `architecture-board` | K, M, S |
| `architecture-change` | I, M |
| `architecture-repository` | St, D |
| `data-architecture` | D, St, B |
| `discovery` | K, M |
| `gap-analysis` | I, M, S, B |
| `oaa-adm-lite` | D, Ph, B, S |
| `product-architecture` | St, B, D, M, S |
| `agile-governance` | K, M, S |
| `agile-security` | M, K, S |
| `agile-strategy` | S, M, K |

Invariants that SHALL hold for every optional diagram: the pinned `!include <archimate/Archimate>` line is reused; realization edges point concrete→abstract; the element-count gate applies to the combined view (≤ 12 structural elements per layer; a Motivation overlay stays ≤ 6; exceeding the budget is resolved by reducing to the most material elements or splitting into an additional sequenced `ARCH` doc, never silently dropping); overlays are additive and SHALL NOT remove the demanded base view or any Mermaid block; companion views SHALL sequence as additional `ARCH` documents under `projects/{p}/diagrams/`. Selection SHALL mirror the shared ArchiMate intake (`/arckit:archimate` Question 2 + "Data only"); non-interactive templates default to including exactly the optional types whose supporting content is present in the artefact.

#### Scenario: a companion view sequences as a separate document
- **WHEN** `transition-architecture` content supports an Implementation & Migration companion view
- **THEN** it is emitted as an additional sequenced `ARCH` document (separate from the demanded base view), not merged into the base view, and both respect the ≤ 12 elements/layer gate

#### Scenario: an overlay is omitted when unsupported
- **WHEN** an artefact's content has no motivation, capability, or data-object content
- **THEN** those optional overlays are omitted (the base view still renders); no "not represented" error is raised

#### Scenario: budget overflow forces a split
- **WHEN** adding an optional overlay or companion element would put a single layer over 12 elements
- **THEN** the view is reduced to the most material ≤ 12 elements or split into an additional sequenced `ARCH` document; the demanded base view is unchanged

### Requirement: Companion-View Batch 1
The four highest-value companion views SHALL be present as implementation **Batch 1**: an **Implementation & Migration** companion view for `transition-architecture` and `gap-analysis`, and a **Physical** companion view for `technology-architecture` and `oaa-adm-lite`. Each SHALL be a separate sequenced `ARCH` companion document that is additive to the demanded base view, gated by the ≤ 12 elements/layer and realization-direction invariants, using the pinned include and loading `skills/plantuml-syntax/references/archimate.md`.

#### Scenario: Implementation & Migration view for a transition artefact
- **WHEN** the user runs `/arckit:transition-architecture`
- **THEN** the artefact contains its demanded Capability (incremental target) base view AND a separate Implementation & Migration companion `ARCH` view (plateaus / work packages / deliverables) with realization edges pointing concrete→abstract

#### Scenario: Physical view for a technology artefact
- **WHEN** the user runs `/arckit:technology-architecture`
- **THEN** the artefact contains its demanded Technology base view AND a separate Physical companion `ARCH` view (facilities / equipment / communication networks) additive to the base view
