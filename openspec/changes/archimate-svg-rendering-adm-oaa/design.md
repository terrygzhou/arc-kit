# ArchiMate SVG Rendering (ADM/OAA) — design

## Context

`archimate-coverage-expansion` shipped the 17-artefact demanded base set + 4
Batch-1 companion views as **inline ` ```plantuml ` source blocks** in the
ADM/OAA templates + a matching directive in each command. The core
`archimate-svg-delivery` policy (render ArchiMate-representable diagrams to a
self-contained `.svg`; inline source is the source of truth; the `.svg` is the
only new rendered file; offline / no external URLs) is wired into the core
`/arckit:archimate` command but not into these ADM/OAA directives.

## Approach (Option A — append-only directive clause, uniform)

Add ONE uniform clause to each ArchiMate-carrying command file and template:

- **Command:** a `## Render the ArchiMate view(s) to self-contained SVG(s)`
  block covering the file's base view and (where present) its companion view:
  pinned-build offline render (`plantuml-1.2026.8.jar -tsvg`), inline source kept,
  `.svg` is the only new rendered file, self-containment check, reference to
  § Offline Self-Contained SVG Rendering in `references/archimate.md`.
- **Template:** add a "Artefact delivery" bullet to each ArchiMate
  "View this diagram" note: the view is shipped as a rendered **self-contained
  `.svg`** (offline, pinned build), inline source retained.

The 4 files with both base + companion carry the single clause once, phrased to
cover "base view and any companion view".

## TDD Red -> Green

- **RED** — extend `tests/plugin/test_archimate_demanded.py`:
  - all **17 base** commands + the **4 companion** commands contain the SVG
    render clause (marker: `plantuml-1.2026.8.jar -tsvg` + `Offline
    Self-Contained SVG Rendering`).
  - all **17 base** templates + the **4 companion** templates carry the
    "self-contained `.svg`" delivery note (companion templates ≥ 2 occurrences).
- **GREEN** — append the clause / delivery note to the 17 base + 4 companion
  commands and 17 base + 4 companion templates.

## Risks

- **Duplicate delivery notes** where a file has base + companion: keep the clause
  once per command file (covers both views); in templates keep one note per
  ArchiMate section. The test enforces occurrence counts.
- **Byte-preservation:** Mermaid blocks are untouched (append-only to commands;
  template edits add a bullet inside existing sections, never Mermaid).
