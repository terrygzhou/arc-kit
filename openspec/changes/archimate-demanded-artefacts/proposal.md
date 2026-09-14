# ArchiMate-Demanded Artefacts — proposal

## Why

The `plantuml-archimate-adoption` change (complete) ships a first-class
`/arckit:archimate` command, an `ARCH` doc-type, and a pinned PlantUML-ArchiMate
notation reference in the core `plugins/arckit-claude` plugin. But the two
distribution **source** plugins — `plugins/arckit-togaf-adm` and
`plugins/arckit-oaa` (both in `converter.py` `PLUGIN_SOURCES`, merged into the
monolithic `extensions/*`) — still ship **zero** ArchiMate views. Seven of
their artefacts are ArchiMate-representable (business / application /
technology / capability / motivation content) yet today carry only Mermaid
(embedded fences in the ADM templates, or a `data-flow-diagram.mmd` sidecar in
OAA). This leaves a capability gap: the two plugins' artefacts never surface
ArchiMate-metamodel views, even when the subject plainly demands one.

## What Changes

Option A — **append-only, additive, no new doc-type/command**. For each of the
7 demanded artefacts, add a PlantUML-ArchiMate fenced block to the existing
template (pinned `!include <archimate/Archimate>` line, `{...}` placeholders
matching the file's existing style) and a short "fill when ArchiMate-representable"
directive to the matching command, loading the pinned notation reference
(`skills/plantuml-syntax/references/archimate.md`, shared into `extensions/*`
via the converter). Existing Mermaid blocks are left **byte-for-byte untouched**.

Demanded artefacts and their ArchiMate layer focus:

| Source plugin | Artefact (command) | Template | ArchiMate layer(s) |
|---|---|---|---|
| `arckit-togaf-adm` | `application-inventory` | `application-inventory-template.md` | Application |
| `arckit-togaf-adm` | `application-rationalization` | `rationalization-template.md` | Application + Capability |
| `arckit-togaf-adm` | `business-capability-map` | `capability-map-template.md` | Business / Capability |
| `arckit-togaf-adm` | `technology-architecture` | `tech-architecture-template.md` | Technology |
| `arckit-togaf-adm` | `transition-architecture` | `transition-architecture-template.md` | Capability (incremental target) |
| `arckit-oaa` | `oaa-adm-lite` | `oaa-adm-lite-template.md` | Technology (systems real / deployment) + Application |
| `arckit-oaa` | `product-architecture` | `product-architecture-template.md` | Application |

- **Templates**: append a `### PlantUML ArchiMate View` section with the pinned
  block to the 5 ADM + 2 OAA templates.
- **Commands**: add a one-paragraph directive (load `references/archimate.md`,
  fill the ArchiMate block when the artefact content is ArchiMate-representable,
  ≤ 12 elements/layer, realization edges concrete→abstract) to the 5 ADM +
  2 OAA commands. The 2 OAA commands that already mandate a Mermaid diagram
  keep it; ArchiMate is additive, not a replacement.
- **Conformance guard**: extend `tests/plugin/test_archimate_conformance.py`
  (or a focused new test) to assert each of the 7 templates carries the pinned
  `!include <archimate/Archimate>` line, and each of the 7 commands carries the
  ArchiMate directive + reference load.
- **Regen + changelog**: `python scripts/converter.py`, `CHANGELOG.md` entry.

## Capabilities

### Modified Capabilities
- `artifact-generation`: gains an **ArchiMate-Representable ADM/OAA Artefacts
  Carry a Demanded PlantUML-ArchiMate View** requirement (append-only template
  block + command directive; Mermaid preserved; no new doc-type).

## Non-goals

- No new command, no new doc-type, no registry change in `config/doc-types.mjs`.
- No change to the existing Mermaid blocks (embedded or the OAA `.mmd` sidecar).
- No D2 / archify sidecar changes.
- No edits to the core `plugins/arckit-claude` `/arckit:archimate` command
  (that path is unchanged).
- No Pages offline-rendering; no new hooks.
- No hand-edits of `extensions/*` — regenerated via `scripts/converter.py`.

## Impact

- Edits: 5 `plugins/arckit-togaf-adm/templates/*.md` + 5
  `plugins/arckit-togaf-adm/commands/*.md` + 2
  `plugins/arckit-oaa/templates/*.md` + 2 `plugins/arckit-oaa/commands/*.md`
  (+ 1 focused conformance test), `CHANGELOG.md`, this change's delta spec.
- Regenerated (gitignored): `extensions/*`.
