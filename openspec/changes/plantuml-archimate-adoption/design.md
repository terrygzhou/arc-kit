# PlantUML ArchiMate Adoption — design

## Context

ArcKit's ArchiMate surface today: `docs/DIAGRAMS.md` documents a D2 idiom
(one container per ArchiMate layer, cross-layer "realize" edges, purple
strokes) used only in hand-authored sidecars — and `scripts/diagrams.sh`
is the only consumer. Nothing in the command/template/CI pipeline
generates ArchiMate views. PlantUML's experimental ArchiMate support
(`plantuml.com/archimate-diagram`, stdlib include) is the first native
ArchiMate tooling in the stack, and PlantUML is already a first-class
`/arckit:diagram` format with Pages rendering (`pages-template.html`
hex-encodes ` ```plantuml ` blocks to the public server).

Constraint: this environment has no network access, so the exact
PlantUML ArchiMate API (stdlib include path, element/relationship
functions, minimum version) is **not yet verified in-repo**. The design
treats that as an explicit gating spike rather than guessing.

## Goals / Non-Goals

**Goals:** a template-driven, checklist-gated generated path for
ArchiMate-metamodel views; pinned, verifiable PlantUML ArchiMate API;
single-source doc-type registration; honest mapping between the
generated path and the D2 idiom.

**Non-Goals:** Mermaid ArchiMate; D2/archify pipeline changes; Pages
offline-rendering; C4-mode edits; hook additions.

## Decisions

- **Dedicated command, not a `diagram.md` mode.** ArchiMate is a
  different metamodel (layered business/application/technology/data/
  motivation elements + typed relationships), not a C4 level. Repo
  pattern is one command per diagram family (`diagram`, `dfd`,
  `wardley`), and `diagram.md` is already 1332 lines. New command:
  `/arckit:archimate`, writing a new code `ARCH` (kept distinct from
  `DIAG` so the C4-flavoured DIAG checklist entry stays accurate; both
  route to the `diagrams/` subdir).
- **Spike-first with a stated fallback.** Task 0 pins the API into
  `references/archimate.md` § Pinned API (include line, element types
  per layer, relationship functions — realization/serving/aggregation/
  composition/association/assignment/derivation — colours include,
  minimum PlantUML version, public-URL length behaviour) and renders a
  three-layer sample (business → application realization + data
  object) committed as a test fixture. If the spike shows native
  support is insufficient (e.g. motivation-layer elements or required
  relationship types are missing), the fallback is C4-PlantUML with
  ArchiMate-flavoured custom stereotypes: same command, same `ARCH`
  code, different notation reference. The pinned-API section records
  which notation was chosen.
- **Reuse diagram.md machinery, don't fork it.** Intake interview (max
  2 rounds: Q1 layer selection — business / application / technology /
  combined + optional data; Q2 motivation/capability inclusion),
  quality-gate table (ArchiMate-specific criteria: every element
  stereotyped into exactly one layer, realization edges point from the
  more concrete layer to the more abstract one, no unlabelled
  cross-layer edges, ≤ 12 elements per layer), and the 3-iteration
  remediation loop are copied with ArchiMate-specific criteria,
  consistent with per-command self-containment in this repo.
- **Dual registration of `ARCH`.** `doc-types.mjs`
  (`DOC_TYPES` + `MULTI_INSTANCE_TYPES` + `SUBDIR_MAP['diagrams']`)
  **and** the `pages.md` known-artifact-types table;
  `check-doc-type-registry.py` already enforces both directions, and
  `generate-document-id.mjs` gives `--next-num` sequencing for
  `ARC-NNN-ARCH-NNN-v1.0.md`.
- **New command carries `doc-type: ARCH` frontmatter.** The spec makes
  `doc-type` required; note that `diagram.md`/`dfd.md` currently lack
  the field (pre-existing gap, out of scope here).
- **Static tests, no renderer in CI.** CI cannot run PlantUML
  (java/network). Guard: pytest asserts registry parity, template
  include-line matches the pinned API, command frontmatter, and
  checklist section presence. Rendered sample fixture documents the
  known-good shape for humans.
- **Checklist stays the 31-copy lockstep rule.** New `ARCH` section
  added to the canonical copy and propagated with
  `scripts/sync-shared-assets.py`, verified by `--check`.
- **Docs mapping, not replacement.** `docs/DIAGRAMS.md` keeps the D2
  idiom but gains a pointer: "generated path = `/arckit:archimate` →
  `ARC-NNN-ARCH-NNN-v1.0.md` (PlantUML ArchiMate); the D2 idiom is
  hand-authored sidecars only."

## Risks / Trade-offs

- **Experimental API churn.** PlantUML ArchiMate is marked
  experimental; pinned-version rendering fixture catches regressions
  visually; fallback decision rule is pre-committed (above).
- **Command count in slash-commands spec (75 → 76)** is a spec-level
  change; expressed as a MODIFIED requirement delta, not a silent edit.
- **Public-server URL length limit** for large ArchiMate diagrams in
  Pages: mitigated by the ≤ 12-per-layer element threshold; noted in
  the reference; offline pre-rendering deferred (follow-up change).
- **31-copy checklist propagation** can miss a variant — same
  mitigation as the ADM change: `sync-shared-assets.py --check`
  lockstep + post-edit grep.
