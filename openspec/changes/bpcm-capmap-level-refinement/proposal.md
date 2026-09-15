# BPCM Capability Map — top-down, complexity-adaptive level refinement — proposal

## Why

`bpcm-capmap-archimate` added a *dedicated* ArchiMate capability-map view, but it
fixed the rendering strategy to a single partitioning rule: "the combined L1+L2
layer, split at a domain boundary when it exceeds 12 elements." That is only one
of the sensible ways to render a capability hierarchy, and it does not say how the
agent should choose between **flattening** a small model into one diagram and
**abstracting** a large model level-by-level. In practice the two regimes are
different artefacts:

- A **simple** capability model (few domains, shallow) reads best as **one**
  top-down diagram of every level.
- A **complex** capability model (many domains / deep / dense levels) is
  unreadable in one box and should be **abstracted level-by-level**: an
  **abstract** top-level overview plus **refinement** diagrams that drill down one
  L1 domain at a time.

Without an explicit, agent-applicable rule, generated BPCMs pick arbitrarily (and
the shipped `## Capability Map (ArchiMate View)` template only carries the
flattened shape), so the same BPCM can come out flat or split with no principled
choice.

## What Changes

- Add a **complexity-adaptive** rendering strategy to the BPCM capability-map
  ArchiMate view, built **top-down** (L1 at the top, `LAYOUT_TOP_DOWN()`, a
  parent always reads above its children):
  - **Simple (`E ≤ 12` total elements across all present levels) → flatten to one
    diagram** — a single top-down view of L1 → L2 → (optional L3).
  - **Complex (`E > 12`, or a single level denser than ~12) → abstract
    level-by-level, one diagram per refinement** — an **abstract** L1-only
    overview (each domain labelled with a child-count roll-up) + **refinement**
    diagrams, one **per L1 domain** (its L2 sub-hierarchy + L3 when defined),
    each gated to ≤ 12 elements/layer and split further per sub-domain if still
    dense; abstract ↔ refinement cross-linked in Linked Artifacts.
- Land the rule where agents apply it: the `business-capability-map.md` command
  directive (regime choice + top-down invariant + per-domain refinement +
  capability-domain split), the capability-map template (flattened + abstract
  overview + refinement placeholders), and the ArchiMate reference (the
  level-by-level idiom).
- All views stay additive (byte-preserve the Mermaid mindmap + realization view)
  and are delivered as self-contained `.svg` per `archimate-svg-delivery`.

## Capabilities

### Added Capabilities
(none — no new capability; a new requirement on an existing one)

### Modified Capabilities
- `artifact-generation` gains a requirement:
  - **BPCM Capability Maps Are Rendered Top-Down, Complexity-Adaptively** — the
    BPCM capability-map ArchiMate view SHALL be built top-down and SHALL select
    its diagram set from model complexity: flatten to a single diagram when the
    model is simple (`E ≤ 12`), and abstract level-by-level (abstract L1 overview
    + one refinement diagram per L1 domain, each gated to ≤ 12 and split per
    sub-domain as needed) when it is complex.

## Non-goals

- No replacement of the Mermaid mindmap, the realization view, or the flattened
  single-view shape already added by `bpcm-capmap-archimate` (that shape remains
  the simple-regime output).
- No new doc-type, slash command, or registry entry; no D2 / archify.
- No new notations beyond PlantUML-ArchiMate; the ≤ 12 gate and top-down
  invariant already established are reused, not redefined.
- No automatic re-rendering of existing shipped BPCMs; the rule applies to
  future agent-generated BPCMs (and to explicit regeneration).

## Impact

- Edits: `plugins/arckit-togaf-adm/commands/business-capability-map.md`
  (complexity-adaptive directive), `plugins/arckit-togaf-adm/templates/
  capability-map-template.md` (flattened + abstract-overview + refinement
  placeholders), `plugins/arckit-claude/skills/plantuml-syntax/references/
  archimate.md` (level-by-level idiom), 2 focused TDD guards, `CHANGELOG.md`,
  this change's delta spec.
- Regenerated (gitignored): `extensions/*`.
