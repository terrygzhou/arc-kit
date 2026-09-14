# ArchiMate Coverage Expansion — proposal

## Why

The `archimate-demanded-artefacts` change (shipped, `d0438ff3`) gives **7 of 17**
ADM/OAA artefacts a demanded PlantUML-ArchiMate *structural* view. Three gaps
remain:

1. **Breadth** — the optional-ArchiMate requirement locks only **3 overlays**
   (Motivation / Strategy-Capability / Data-only). The pinned stdlib supports
   **5 more** single-layer companion views (Behavior, Structure, Physical,
   Implementation & Migration, Stakeholder/Requirement) — none addressed.
2. **Coverage** — the **10 artefacts outside the demanded set** ship no ArchiMate
   view at all (Mermaid-only or none), even when their subject is plainly
   ArchiMate-representable.
3. **Nothing optional/companion is implemented yet** — only the 7 structural
   base views exist.

## What Changes

Three coordinated items, all **append-only** and **byte-preserving** for Mermaid:

- **[Breadth] Optional 8-type menu.** Extend the optional-ArchiMate requirement to
  all 8 types: 3 overlays (Motivation, Strategy/Capability, Data-only) + 5
  companion single-layer views (Behavior, Structure, Physical, Implementation &
  Migration, Stakeholder/Requirement). The overlay-vs-companion distinction and a
  fixed per-artefact best-fit mapping are defined in the spec.
- **[Coverage] Demanded base set 7 → 17.** Every ADM/OAA artefact (12 ADM + 5 OAA)
  carries a demanded base-layer structural PlantUML-ArchiMate view, with a
  per-artefact layer mapping. Non-representable content renders a documented stub,
  never a blank.
- **[Batch 1] Priority companion views.** Implement the 4 highest-value companion
  views first: **Implementation & Migration** for `transition-architecture` +
  `gap-analysis`; **Physical** for `technology-architecture` + `oaa-adm-lite`.

## Capabilities

### Modified Capabilities
- `artifact-generation` gains three requirements:
  - **All ADM/OAA Artefacts Carry a Demanded PlantUML-ArchiMate Base View**
    (full 17-artefact set; per-artefact layer mapping; documented-stub rule)
  - **Optional ArchiMate Diagrams — 8-Type Menu with Per-Artefact Mapping**
    (overlays + companion views, invariants, selection rule)
  - **Companion-View Batch 1** (Impl/Migration × 2, Physical × 2)

## Non-goals

- No new command / doc-type / registry change (companion views reuse the `ARCH`
  multi-instance doc-type, the pinned include, and `references/archimate.md`).
- No Mermaid edits (byte-preserved), no D2 / archify changes, no core
  `/arckit:archimate` edits.
- No hand-edits of `extensions/*` — regenerated via `scripts/converter.py`.
- Not all 8 optional types for all 17 artefacts in one shot: the menu is
  **defined + mapped**; Batch 1 implements 4 companion views. Remaining
  overlays/companions are a follow-up change.

## Impact

- Edits: 7 additional ADM + 3 additional OAA templates + commands (base views,
  [Coverage]); 4 template/command pairs (Batch 1 companion views); 1 focused
  test; `CHANGELOG.md`; this change's delta spec.
- Regenerated (gitignored): `extensions/*`.
