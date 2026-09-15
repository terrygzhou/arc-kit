# BPCM Capability Map — top-down, complexity-adaptive level refinement — design

## Context

`bpcm-capmap-archimate` established that a BPCM capability hierarchy is
ArchiMate-representable: nested `Strategy_Capability` joined by
`Rel_Composition(parent, child, "contains")` (whole→part), `LAYOUT_TOP_DOWN()`,
rendered to a self-contained `.svg` (pinned `plantuml-1.2026.8.jar -tsvg`). It
also fixed one partitioning rule ("split the combined L1+L2 layer at a domain
boundary when it exceeds 12"). What is missing is a *strategy for choosing how
many diagrams to emit and at which level to abstract*, driven by the model's
complexity.

**Evidence (render-verified):** the hospitality BPCM (4 L1 + 15 L2 = 19 elements,
no L3) rendered both (a) a flattened single 19-node top-down diagram and (b) a
domain-split pair, each to a self-contained SVG with all `contains` edges
present and no non-W3C URLs — confirming both regimes are producible with the
pinned toolchain.

## Approach

Introduce a single complexity threshold and two rendering regimes, always
top-down:

- **Measure** the model: `E` = total `Strategy_Capability` elements across all
  present levels (L1 + L2 [+ L3]); note the widest single level.
- **Simple (`E ≤ 12`)** → emit ONE diagram flattening every present level
  (the shape already templated in `bpcm-capmap-archimate`).
- **Complex (`E > 12`, or a single level > ~12)** → emit a layered-abstraction
  set:
  1. **Abstract overview** — top level only (L1 domains), each labelled with a
     child-count roll-up;
  2. **Refinement** — one diagram per L1 domain (its L2 sub-hierarchy + L3 when
     defined); each refinement is a separate sequenced `ARCH` document gated to
     ≤ 12 elements/layer; a dense refinement is **split** at a
     capability-domain / sub-domain boundary into a further `ARCH` document.
- **Invariants (both regimes):** top-down layout; whole→part
  `Rel_Composition` edges; additive to the Mermaid mindmap + realization view;
  self-contained `.svg` delivery; nothing silently dropped; abstract ↔
  refinement cross-linked.

## Decisions

- **Threshold = 12 total elements** (reuses the established per-layer gate as
  the "fits in one box" figure). `E ≤ 12` → flatten; `E > 12` → abstract +
  per-domain refinement. The per-layer gate still caps every individual diagram.
- **Abstract = L1-only roll-up**, not L1+L2 — the overview must be glanceable;
  the L2/L3 detail belongs in refinement diagrams. Child counts appear as labels,
  not boxes, keeping the overview small.
- **Refinement is per L1 domain** (level-by-level drill-down), the classic
  capability-domain detail pattern; a dense domain drills further to L3 /
  sub-domain.
- **The 12 cap applies per diagram**, so a complex model always ends in
  diagrams each ≤ 12 — the split guarantee from `bpcm-capmap-archimate` is
  preserved, now applied to each refinement.
- **Agent-applicable & deterministic:** the regime is a pure function of `E` and
  the widest level, so two agents generating the same BPCM make the same choice.
- **No new notation / doc-type / command / registry entry**; reuses the ArchiMate
  stdlib, the `.svg` delivery clause, and the existing template block (which is
  simply the simple-regime output; two further blocks template the complex regime).
