# ArchiMate SVG Rendering (ADM/OAA) — proposal

## Why

`archimate-coverage-expansion` (shipped, `f7650487`) gives every ADM/OAA
artefact a demanded PlantUML-ArchiMate base view (17 artefacts) plus 4 Batch-1
companion views. Those views are carried as **inline ` ```plantuml ` source
blocks** with `{plantuml_*}` / `{companion_*}` placeholder tokens. PlantUML does
**not** render in GitHub markdown, so a generated artefact that only carries the
raw source shows no diagram.

The `archimate-svg-delivery` policy (shipped, core `/arckit:archimate`) already
mandates that ArchiMate-representable diagrams be rendered to a **self-contained
`.svg`** (inline source kept as source of truth; the `.svg` is the only new
rendered file; opens offline, no external URLs). That policy is wired into the
core `archimate` command but was **never wired into the ADM/OAA base-view and
companion-view directives** — so the 17 base + 4 companion ADM/OAA views have no
SVG-rendering instruction.

## What Changes

- Wire the shipped `archimate-svg-delivery` policy into **every ArchiMate-carrying
  ADM/OAA directive**: all **17 base-view** commands/templates and the **4
  companion-view** commands/templates.
- Each directive gains a "render the ArchiMate view to a self-contained SVG"
  clause: render offline with the pinned build (`plantuml-1.2026.8.jar -tsvg`,
  no public server / URL-include), keep the inline PlantUML source as the source
  of truth, emit the `.svg` as the only new rendered file, verify self-containment
  (no non-W3C `http(s)` URLs; local `#anchor` `xlink:href` only; offline-openable).
- The "View this diagram" note in each template switches from "view via CLI /
  public server" to "delivered as a rendered self-contained `.svg` shipped with the
  artefact".

All edits are **append-only / additive** and **byte-preserve** every existing
Mermaid block; no new doc-type, command, or registry entry; no core
`/arckit:archimate` edits; `extensions/*` regenerated (gitignored).

## Capabilities

### Modified Capabilities
- `artifact-generation` gains a requirement:
  - **ADM/OAA ArchiMate Views Are Rendered to Self-Contained SVGs** — every
    ArchiMate base and companion view in the ADM/OAA distribution source plugins
    carries a directive to render it to a self-contained SVG (inline source kept;
    `.svg` the only new rendered file; offline / self-contained), consistent with
    the core `archimate-svg-delivery` policy.

## Non-goals

- No changes to the core `/arckit:archimate` command or `references/archimate.md`.
- No Mermaid edits (byte-preserved), no D2 / archify, no new diagram types.
- Not a hard filename gate: the clause is a generation-time directive, enforced by
  the focused test, not by a runtime filename check.

## Impact

- Edits: 17 ADM/OAA command files (17 base + 4 companion clauses) and their
  17 template files (base + 4 companion "View this diagram" notes); 1 focused test
  group; `CHANGELOG.md`; this change's delta spec.
- Regenerated (gitignored): `extensions/*`.
