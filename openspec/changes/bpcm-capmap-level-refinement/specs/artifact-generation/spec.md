# artifact-generation Delta — bpcm-capmap-level-refinement

## ADDED Requirements

### Requirement: BPCM Capability Maps Are Rendered Top-Down, Complexity-Adaptively
The Business Capability Map (BPCM) capability-map ArchiMate view of the
`arckit-togaf-adm` distribution source plugin SHALL be built **top-down** (L1
domains at the top, lower levels below; `LAYOUT_TOP_DOWN()`; a parent always
reads above its children) and SHALL select its *set* of diagrams from the model's
complexity — total `Strategy_Capability` elements `E` across all present levels
(L1 + L2 [+ L3]) and the widest single level:

- **Simple (`E ≤ 12`) → flatten to one diagram:** a single top-down diagram of
  every present level (L1 → L2 → optional L3), joined whole→part by
  `Rel_Composition(parent, child, "contains")`.
- **Complex (`E > 12`, or a single level denser than ~12) → abstract
  level-by-level, one diagram per refinement:**
  1. an **abstract overview** diagram of the top level only (the L1 domains, each
     labelled with a child-count roll-up);
  2. **refinement** diagrams, one per L1 domain (its L2 sub-hierarchy and its L3
     detail when defined), each a separate sequenced `ARCH` document gated to
     ≤ 12 elements/layer; a dense refinement is split at a capability-domain /
     sub-domain boundary into a further `ARCH` document.
- Both regimes SHALL keep the view additive to and byte-preserving of the Mermaid
  mindmap and the capability→target realization view, cross-link abstract ↔
  refinement in Linked Artifacts, drop no element silently, and deliver each
  diagram as a self-contained `.svg` per the `archimate-svg-delivery` policy.

#### Scenario: simple model flattens to one diagram
- **WHEN** the BPCM capability model has ≤ 12 total elements across all present levels
- **THEN** a single top-down ArchiMate diagram flattens every present level (L1 domains containing their L2 sub-capabilities, L3 only when defined)

#### Scenario: complex model abstracts level-by-level
- **WHEN** the BPCM capability model has > 12 total elements (or a single level denser than ~12)
- **THEN** the view is an abstract L1-only overview (each domain with a child-count roll-up) plus one refinement diagram per L1 domain, each refinement gated to ≤ 12 elements/layer

#### Scenario: a dense refinement is split per sub-domain
- **WHEN** a single L1 domain's refinement exceeds 12 elements/layer
- **THEN** it is split at a capability-domain / sub-domain boundary into a further sequenced `ARCH` document; no element is silently dropped

#### Scenario: every diagram is top-down
- **WHEN** any capability-map diagram (flattened, abstract overview, or refinement) is rendered
- **THEN** L1 domains read above their L2 sub-capabilities (and L3 above them), consistent with `LAYOUT_TOP_DOWN()`

#### Scenario: regime is deterministic
- **WHEN** two agents generate the BPCM capability map for the same capability model
- **THEN** both select the same regime (simple vs complex) because it is a pure function of `E` and the widest level
