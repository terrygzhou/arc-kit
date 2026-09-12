# PlantUML ArchiMate Adoption — proposal

## Why

ArcKit's only ArchiMate coverage today is a hand-written D2 idiom
(`docs/DIAGRAMS.md`: layer containers, purple realization edges). That
corpus is local-only (`projects/` is gitignored), hand-authored, and
opt-in — none of the generated-artefact workflow produces it. Meanwhile
`/arckit:diagram` covers C4/sequence/deployment/data-flow but offers no
way to generate ArchiMate-metamodel views (business / application /
technology layers, realization edges, motivation/capability elements).

PlantUML ships native (experimental) ArchiMate support
(https://plantuml.com/archimate-diagram) plus a stdlib include. PlantUML
is already a first-class output format of `/arckit:diagram`, ArcKit
Pages already renders ` ```plantuml ` blocks, and the `plantuml-syntax`
reference skill exists — so adoption cost is a command, a template, a
skill reference, and a doc-type code.

## What Changes

- **API spike (gates everything).** PlantUML ArchiMate is experimental
  and the exact stdlib surface (include line, element types,
  relationship functions, minimum PlantUML version) is not yet pinned in
  this repo. Task 0 pins it into a new
  `skills/plantuml-syntax/references/archimate.md` "Pinned API" section
  with a rendered sample; a stated fallback (C4-PlantUML with
  ArchiMate-flavoured stereotypes) covers the case where the native
  support proves insufficient.
- **New command `/arckit:archimate`** (`commands/archimate.md`,
  `doc-type: ARCH`, `effort: high`): generates ArchiMate views in
  PlantUML ArchiMate notation, reusing diagram.md's intake-interview and
  quality-gate machinery. Output: `ARC-NNN-ARCH-NNN-v1.0.md` under
  `projects/{p}/diagrams/`.
- **New doc-type `ARCH`**: registered in `config/doc-types.mjs`
  (`DOC_TYPES` + `MULTI_INSTANCE_TYPES` + `SUBDIR_MAP` → `diagrams`)
  and the `/arckit:pages` known-artifact-types table (dual registration
  enforced by `scripts/check-doc-type-registry.py`).
- **New template `archimate-template.md`** (mirrors
  `architecture-diagram-template.md` structure: PlantUML block, element
  inventory, layer/realization traceability, generation footer).
- **Skill reference**: `archimate.md` (notation, layer-tier ordering,
  realization-direction rules, colour standards, element thresholds,
  antipatterns) + `SKILL.md` mapping-table row + `**/ARC-*-ARCH-*.md`
  path glob on `plantuml-syntax`.
- **Quality checklist**: new `ARCH` per-type section in all tracked
  `quality-checklist.md` copies (lockstep via `sync-shared-assets.py`).
- **Docs mapping**: `docs/DIAGRAMS.md` gains a pointer — generated path
  is PlantUML ArchiMate; the D2 idiom remains for hand-authored
  sidecars only.
- **Guard**: new `tests/plugin/test_archimate_conformance.py`
  (registry parity, template include line, command frontmatter,
  checklist section presence).

## Capabilities

### Modified Capabilities
- `slash-commands`: command count 75 → 76; new
  **ArchiMate View Command Contract** requirement.

### New Capabilities (deltas)
- `artifact-generation`: gains **ArchiMate Artefact Registration (ARCH)**
  (dual registration, multi-instance sequencing under `diagrams/`,
  template-driven generation from `archimate-template.md`).
- `plugin-skills`: gains **ArchiMate Notation Reference Ships Inside
  plantuml-syntax** (pinned-API reference file, SKILL.md mapping row,
  paths glob).

## Non-goals

- No Mermaid ArchiMate option (no such notation exists in Mermaid);
  ArchiMate output is PlantUML-only.
- No changes to the D2/archify sidecar pipeline in `docs/DIAGRAMS.md`
  beyond the mapping pointer; the D2 idiom stays for hand-authored
  sidecars.
- No change to how Pages renders PlantUML (public-server dependency and
  offline pre-rendering are a separate follow-up change).
- No new hooks; no C4-mode changes to `/arckit:diagram`.
- No hand-edits of `extensions/*` — regenerated via
  `scripts/converter.py`.
- Pre-existing `doc-type` frontmatter gaps in `diagram.md` / `dfd.md`
  are flagged, not fixed here.

## Impact

- New: 1 command, 1 template, 1 skill reference, 1 pytest file,
  rendered sample fixture.
- Edits: `config/doc-types.mjs`, `commands/pages.md` table,
  `skills/plantuml-syntax/SKILL.md`, `docs/DIAGRAMS.md`, all tracked
  `quality-checklist.md` copies (+ `sync-shared-assets` lockstep),
  `CHANGELOG.md`, this change's delta specs.
- Regenerated (gitignored): `extensions/*`.
