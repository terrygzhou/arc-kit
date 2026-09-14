# ArchiMate-Demanded Artefacts — design

## Context

`plantuml-archimate-adoption` (complete) established the pinned PlantUML-ArchiMate
notation reference (`plugins/arckit-claude/skills/plantuml-syntax/references/archimate.md`)
and the `/arckit:archimate` command. This change does **not** touch that path. It
instead reaches the two distribution source plugins `plugins/arckit-togaf-adm` and
`plugins/arckit-oaa`, which are members of `converter.py` `PLUGIN_SOURCES` and are
merged into the monolithic `extensions/*`. Those plugins currently contain no
ArchiMate view; this adds the demanded ones, append-only.

## Goals / Non-Goals

**Goals:** the 7 ArchiMate-representable ADM/OAA artefacts carry a demanded
PlantUML-ArchiMate view; Mermaid blocks preserved; a static conformance guard;
single, reviewable set of template/command edits.

**Non-Goals:** new command/doc-type; Mermaid edits; D2; core `/arckit:archimate`
changes; Pages offline rendering; hook additions.

## Decisions

- **Append-only "Option A" block.** Each affected template gains a
  `### PlantUML ArchiMate View` section containing exactly one PlantUML fenced
  block:

      ```plantuml
      @startuml
      !include <archimate/Archimate>
      title {<arctefact>_title}
      ' Elements
      {archimate_elements}
      ' Relationships (realization concrete->abstract; serving/flow/access)
      {archimate_relationships}
      ' Layout constraints (hidden placement edges)
      {archimate_layout}
      @enduml
      ```

    The `{...}` tokens follow the file's existing placeholder style. The pinned
    `!include <archimate/Archimate>` line matches the one already verified in
    `tests/plugin/test_archimate_conformance.py` (PlantUML 1.2026.8).

- **Command directive, not a new mode.** Each affected command gets a short
  paragraph (mirroring the existing "Load Mermaid Syntax References" step style):
  read `skills/plantuml-syntax/references/archimate.md`; when the artefact
  content is ArchiMate-representable, fill the ArchiMate block with the mapped
  layer's elements (see table in proposal). For the two OAA commands that already
  mandate a Mermaid diagram (product-architecture C4; oaa-adm-lite
  `data-flow-diagram.mmd`), the Mermaid deliverable stays; the ArchiMate view is
  additive and coexists.

- **Layer mapping is per-artefact, not freeform.** Each artefact's directive names
  its ArchiMate layer focus (Application / Business-Capability / Technology /
  Capability-incremental). This keeps generated views single-layer-stereotyped,
  consistent with the `ARCH` quality gate (≤ 12 elements/layer, realization
  concrete→abstract, no unlabelled cross-layer edges).

- **Reference is shared via the converter.** The source ADM/OAA plugin dirs do
  not each carry a local `references/archimate.md`; the command references the
  canonical `skills/plantuml-syntax/references/archimate.md`, which the converter
  already merges into every `extensions/*`. No duplicate reference is added.

- **Conformance is static (no renderer in CI).** PlantUML (java/network) cannot
  run in CI. The guard asserts, per affected file: the pinned include line is
  present; the command carries the reference load + "ArchiMate-representable"
  fill instruction; Mermaid blocks are byte-identical to pre-change (diff
  assertion). Rendered sample stays in the existing `tests/fixtures/archimate/`.

## Risks / Trade-offs

- **Experimental PlantUML ArchiMate API.** Same mitigation as the adoption
  change: pinned version + committed rendered fixture; no new API surface is
  introduced here (reuses the pinned include line).
- **Block bloat.** 7 artefacts each gain one block; the ≤ 12/layer gate and
  "single-layer stereotyping" keep views small and the public-URL length within
  the Pages bound.
- **Mermaid-block preservation risk.** Guarded by the diff assertion in the
  conformance test so a careless edit cannot silently mutate the kept Mermaid.
- **Two OAA artefacts now carry two notations.** Explicitly additive by design;
  documented in the command directive so the model does not drop the Mermaid
  deliverable.
