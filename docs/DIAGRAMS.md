# ArcKit Diagrams

Diagram sidecars for ArcKit artefacts (`projects/<id>/diagrams/`), built on a
three-layer stack:

| Layer | Tool | Role |
| --- | --- | --- |
| Authoring corpus | D2 (`.d2` sidecars + rendered `svg/`) | Canonical, versioned, CI-linted diagrams. One sidecar per artefact version. |
| Interactive showcase | archify (`.workflow.json` -> `.workflow.html`) | Rich interactive HTML for selected diagrams (guided views, trace motion, export). |
| Inline artefact diagrams | Mermaid (in `ARC-*.md`) | Quick inline visuals; also the only tool for `gantt`, `quadrantChart`, and `pie` charts. |

## Layout & Naming

Sidecars live in `projects/<id>/diagrams/` and mirror the Artefact ID with the
same version:

```text
projects/000-global/diagrams/
  arc-000-tech-v1.0.d2                 # D2 source for ARC-000-TECH-v1.0
  arc-000-tech-v1.0.workflow.json       # archify spec (optional showcase)
  arc-000-tech-v1.0.workflow.html       # archify delivered HTML
  svg/
    arc-000-tech-v1.0.svg               # D2 render (commit the SVG)
```

- Sidecar name = lowercase artefact ID: `arc-NNN-TYPE-vN.N.<ext>`.
- When the artefact is re-versioned, add a new sidecar; do not overwrite an old
  version's sidecar.
- D2 sources are hand-authored; the `svg/` renders and archify `.html` files
  are generated output. Keep them next to their sources so readers can open
  the deliverable without a toolchain. Note: `projects/` is gitignored, so
  the sidecar tree is local-only; the corpus conventions and checks live in
  the tracked repo (`docs/DIAGRAMS.md`, `scripts/diagrams.sh`).

## ArchiMate Semantics in D2

D2 has no native ArchiMate metamodel, so ArchiMate-style diagrams are encoded
as an idiom:

- **Lenses are layer containers**: one D2 container per ArchiMate layer
  (e.g. `infra`, `platform`, `apps`), each with its own `style.fill` for
  visual separation.
- **Realization is an edge**: a cross-layer edge labeled
  `"X realize Y capabilities"` (purple stroke) connects the higher layer to
  the one it realizes, instead of ArchiMate's dashed realization arrow.
- **Relationships are labeled edges**: integration/cooperation
  relationships become `a -> b: "label"` edges.

Reference idiom: `projects/000-global/diagrams/arc-000-tech-v1.0.d2`.

**Generated ArchiMate views are not D2 sidecars.** `/arckit:archimate` writes
PlantUML ArchiMate-notation layer views to
`projects/{p}/diagrams/ARC-NNN-ARCH-NNN-v1.0.md` (pinned
`!include <archimate/Archimate>`), one view per layer. The D2 idiom above
remains hand-authored sidecars only: do not convert generated `ARC-*-ARCH-*`
artifacts into D2, and do not author ArchiMate views in D2.

## Quality Bar

- Every `.d2` sidecar must compile (CI via `./scripts/diagrams.sh check`).
- archify specs must pass `archify validate` at the default quality
  (`standard`); delivered HTML must pass `archify check`.
- A showcase is optional per artefact: ship an archify spec only when the
  interactive version adds value (multi-lane workflows, guided views).
- Honest reporting: if archify cannot reach `professional` quality
  (e.g. an unresolvable edge crossing), deliver at `standard` and note the
  limitation in the README index, never claim a quality that was not
  achieved.

## Commands

```bash
./scripts/diagrams.sh check    # validate every diagram sidecar (CI)
./scripts/diagrams.sh render   # .d2 -> svg/ and archify .json -> .html
```

Environment overrides: `D2_BIN`, `ARCHIFY_BIN`
(default `~/.codex/skills/archify/bin/archify.mjs`), `ARCHIFY_QUALITY`
(default `standard`).

Missing toolchains cause a `SKIP` notice, never a build failure — CI can wire
`check` into `scripts/ci-local.sh` safely.

## Caveats: Old D2 Builds

Local toolchains may ship a pre-2023 `d2` (v0.8.x):

- No `d2 check` subcommand — `diagrams.sh` detects this with a probe and
  falls back to compile-only linting (throwaway render).
- No `near`/`constraints` keywords and no `shape` style keyword.
- Node labels use the inline idiom `id: "label" { style: {...} }`.
- `direction` values are `up`/`down`/`left`/`right`.

Write sidecars targeting the oldest installed build so they compile both
locally and in CI.
