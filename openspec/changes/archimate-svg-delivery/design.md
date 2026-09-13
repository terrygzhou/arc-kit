# Design — ArchiMate Diagram Production (PlantUML → self-contained SVG)

## Context

Document-generating slash commands (`plugins/arckit-claude/commands/*.md`) keep their current behaviour. Their embedded diagrams default to Mermaid / C4; the ArchiMate path already exists — a pinned notation reference `skills/plantuml-syntax/references/archimate.md` (ArchiMate stdlib, pinned PlantUML 1.2026.8; `!include <archimate/Archimate>` resolved from the jar's bundled stdlib, offline, no graphviz needed for ArchiMate views). A rendered reference ships at `tests/fixtures/archimate/three-layer.{puml,svg}`. This change adds a *production policy*: route ArchiMate-representable diagrams onto PlantUML ArchiMate → self-contained SVG, without churning existing artifacts or creating new architecture documents. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Represent ArchiMate-representable diagrams (and any ArchiMate diagram worth *adding*) with PlantUML ArchiMate, rendered to a self-contained `.svg`.
- Keep the PlantUML source inline in the document; emit the `.svg` as the only new file.
- Leave all existing command/document behaviour and all non-ArchiMate diagrams unchanged.

**Non-Goals:**
- No restructuring or editing of existing artifacts for their own sake.
- No change to how non-ArchiMate diagrams (sequence/ER/gantt/timeline/C4/Mermaid flow) are produced.
- No new doc-type; no public-server or IDE dependency; no new architecture document files.

## Decisions

**1. The rule is a generation-time judgment, not a filename gate.**
"ArchiMate-representable" is an architectural judgment (layer / capability / service / component / motivation structure, with realization → yes; timing / sequence / data-model / gantt / timeline → no). Enforce it in a review / quality-gate step, not a hard filename/write gate.
- *Alternatives*: always-ArchiMate (too broad — most diagram types have no ArchiMate equivalent) or never-ArchiMate (status quo). Rejected.

**2. Source inline in the document; only the `.svg` is emitted as a file.**
The ArchiMate PlantUML source lives in an inline ```` ```plantuml ```` block in the document being generated; the rendered `.svg` is the only new file. This matches "no new architecture files, except svg."
- *Alternative*: a `.puml` sidecar file (an extra new file not in scope). Rejected; a `.puml` may be used as a transient render input but is not a retained deliverable.

**3. Self-contained SVG standard.**
No `http(s)` URL other than W3C namespace declarations; `xlink:href` limited to local `#anchors`; opens offline in any browser. Verifiable statically (grep for external `https?://` + audit `xlink:href`).
- *Why*: makes "offline, zero-dependency" true and checkable without a network.

**4. Offline rendering with graceful degradation.**
Render with the pinned PlantUML build (`java -jar <pinned-jar>`; offline). If the jar is unavailable, generation does **not** block: the inline source is still written and the SVG is marked `TBD`/pending-render.
- *Why*: a missing tool must not break document generation.

**5. No change to existing artifacts or non-ArchiMate paths.**
The policy applies only at generation time, to ArchiMate-representable diagrams. Nothing about existing documents, templates, or Mermaid/C4 output changes.

## Risks / Trade-offs

- **"Representable" is subjective / inconsistent** → Mitigation: a short decision heuristic in the reference (structural/capability/service/component/motivation ⇒ ArchiMate; timing/sequence/ER/gantt/timeline ⇒ not). Where it's genuinely an ArchiMate view, use it; otherwise leave the diagram on its current mechanism.
- **Rendering jar unavailable (CI / headless)** → Mitigation: decision 4 (graceful degradation; source always written, SVG marked pending).
- **SVG drifts from source / re-rendered with a different build** → Mitigation: inline source is the record; a pinned build is declared in the reference; re-render is a documented offline command.
- **Accidentally creating a new arch document** → Mitigation: the output constraint (only `.svg`) is a spec requirement and a gate criterion.

## Migration Plan

This is a policy, not a data migration:
1. Record the policy + heuristic + self-contained-SVG/offline-render guidance in `skills/plantuml-syntax/references/archimate.md`.
2. Add a one-line pointer from the document-generating commands to the policy (archimate / diagram / others that embed ArchiMate-representable diagrams).
3. Add a quality-gate / review criterion: ArchiMate-representable diagram uses PlantUML; SVG is self-contained; no new architecture document file created (only `.svg`).
4. Add a guard test for SVG self-containment on emitted ArchiMate SVGs.
No rollback data to protect; reverting removes the policy text/gate and restores status-quo behaviour.

## Open Questions

- Whether a transient `.puml` render input is ever acceptable vs. strict "svg-only new files" (currently spec'd as svg-only retained output; safely deferrable).
- Whether to auto-detect "ArchiMate-representable" or rely on the architect's judgment (currently: judgment + heuristic, enforced at the gate; deferrable).
