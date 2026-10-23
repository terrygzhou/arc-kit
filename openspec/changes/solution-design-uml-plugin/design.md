## Context

See `proposal.md` for motivation. Key constraints that shape this design:

- **Doc-type registration is a hard prerequisite.** `validate-arc-filename.mjs` blocks any write of an `ARC-NNN-SOLN-*.md` file unless `SOLN` is in the `KNOWN_TYPES` registry (`doc-types.mjs`). The TNDR/CMPT and GRNT incidents (#712, 2026-07) show this is a silent, blocking failure with no fallback name.
- **Three-way `MULTI_INSTANCE_TYPES` parity.** `SOLN` must appear in `doc-types.mjs`, `scripts/bash/generate-document-id.sh`, and `plugins/arckit-claude/scripts/bash/generate-document-id.sh`. `check-multi-instance-parity.py` enforces this in CI.
- **Dual-tree template rule.** The template must exist in both `plugins/arckit-claude/templates/` and `.arckit/templates/`; `rewrite_paths` in `converter.py` handles the path rewrite for Codex targets.
- **Codex is a first-class target.** The generated Codex skill must be invocable as `$arckit-solution-design`; the converter's `copy_reference_skills` automatically picks up new `plantuml-syntax/references/` files without manifest changes.
- **PlantUML-only.** Mermaid has no object-diagram grammar and no UML use-case or UML component reference in the `mermaid-syntax` skill. Offering Mermaid as a fallback would produce a degraded, inconsistent document.

## Goals / Non-Goals

**Goals:**
- A single governed SOLN artefact with six embedded PlantUML diagram sections
- Full doc-type registration so the artefact is unblocked by `validate-arc-filename.mjs`
- Codex CLI skill that is self-contained (no orchestrator, no agent delegation)
- New `object-diagrams.md` reference closing the gap in the `plantuml-syntax` skill
- CI gates (`check-doc-type-registry.py`, `check-multi-instance-parity.py`) pass before merge

**Non-Goals:**
- Mermaid output for any diagram type (explicitly excluded — see Decision 1)
- A standalone `arckit-uml` plugin (the command extends the core plugin — see Decision 2)
- Automatic HLD/DLD generation (HLD/DLD remain external documents)
- Multi-SOLN versioning in a single project run (subsequent runs overwrite `v1.0`; version bumping is a separate workflow)

## Decisions

### Decision 1: PlantUML is the sole notation

**Chosen:** PlantUML for all six diagram types. No Mermaid option.

**Rationale:**
- Mermaid has no object-diagram grammar (confirmed: no `objectDiagram.md` reference in `mermaid-syntax` skill).
- Mermaid's `mermaid-syntax` skill has no UML use-case reference (`userJourney.md` is a journey diagram, not a UML use-case diagram) and no UML component reference (`block.md` and `architecture.md` are C4-flavoured, not UML component diagrams with ports).
- The existing viewing/export workflow for PlantUML is already in ArcKit (`architecture-diagram-template.md` "View this diagram" section, `styling-guide.md`).
- Offering Mermaid for a subset and PlantUML for the rest would produce an inconsistent document; a single-notation document is cleaner for reviewers.

**Alternatives considered:**
- *PlantUML primary + Mermaid fallback for 4 of 6 types*: Rejected — the mixed-notation document is confusing and the Mermaid fallback is weaker than the proposal's table suggested (use-case and component are both ⚠️, not ✅).
- *User chooses notation per-run*: Rejected — the same document would render differently depending on the user's choice, breaking the "one governed artefact" invariant.

### Decision 2: Extension of core `arckit` plugin, not a standalone `arckit-uml` plugin

**Chosen:** `plugins/arckit-claude/commands/solution-design.md`.

**Rationale:**
- The six UML views are the natural next step after `/arckit:diagram`; a separate plugin duplicates the 71+ command core and adds marketplace clutter.
- The `fde` tooling-plugin model is for standalone white-label output — UML views are a standard part of the ArcKit delivery workflow.
- All shared infrastructure (doc-type registry, template dual-tree rule, converter pipeline, `plantuml-syntax` skill) is in the core plugin.

**Alternatives considered:**
- *Standalone `arckit-uml` plugin*: Rejected — the command file, template, and reference would need to be duplicated or symlinked across two plugin trees, and the converter would need a new target. The `fde` plugin precedent is for white-label output, not for extending the core workflow.

### Decision 3: `SOLN` is multi-instance

**Chosen:** `SOLN` added to `MULTI_INSTANCE_TYPES` in all three places; filenames use `ARC-NNN-SOLN-v1.0.md` (single instance per version) but the registration allows for future `ARC-NNN-SOLN-001-v1.0.md` if the team produces multiple solution designs per project.

**Rationale:**
- `SOLN` is parallel to `REQ`, `HLD`, `DLD`, `DIAG` in the ARC namespace (per D3 in the proposal).
- Multi-instance registration is cheap (one string addition in three places) and the `generate-document-id.sh` script already handles it. The current `v1.0` filename pattern is what the command produces; the multi-instance capability is a registration safety net.
- `DES` was rejected as a code because it is too generic in the ARC namespace.

**Alternatives considered:**
- *Single-instance `SOLN`*: Would require a future migration if a team ever produces two solution designs for one project. The multi-instance registration avoids that migration.

### Decision 4: New `object-diagrams.md` reference file

**Chosen:** `plugins/arckit-claude/skills/plantuml-syntax/references/object-diagrams.md`.

**Rationale:**
- Verified by grep: `class-diagrams.md` contains no object/instance content.
- A dedicated file is more discoverable than a section embedded in `class-diagrams.md`, which would mix two diagram types in one reference.
- The converter's `copy_reference_skills` function automatically picks up new files in `references/` — no manifest change needed.

**Alternatives considered:**
- *Add "## Object Diagrams" section to `class-diagrams.md`*: Rejected — less discoverable, mixes two diagram types, and would require a `class-diagrams.md` edit that affects every existing user of that reference.

### Decision 5: Command frontmatter mirrors `data-model.md`, not `diagram.md`

**Chosen:** Frontmatter pattern: `description`, `argument-hint`, `effort: high`, `doc-type: SOLN`, `handoffs:`.

**Rationale:**
- `diagram.md` has no `handoffs:` key and no `doc-type:` key — it's a different command shape.
- `data-model.md` is the closest analogue: it declares `doc-type: DATA`, `effort: high`, and a `handoffs:` list. The `solution-design` command is the same shape.
- The `doc-type: SOLN` declaration is required by the `slash-commands` spec (every command must declare what it writes).

**Alternatives considered:**
- *Mirror `diagram.md`*: Rejected — `diagram.md` lacks `doc-type` and `handoffs`, which are both required or expected for this command.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| `SOLN` not registered before the command is written | Registration is a hard prerequisite in the task checklist — the command is not merged until `check-doc-type-registry.py` and `check-multi-instance-parity.py` both pass. |
| PlantUML object diagram syntax is poorly documented | The new `object-diagrams.md` reference MUST be written with a worked example and tested with the PlantUML CLI before the template is committed. |
| 32K token truncation on the SOLN document | The command body explicitly instructs the Write tool (not streaming output); the six diagram blocks are generated one at a time. |
| GitHub does not render PlantUML inline | The guide and template both state the viewing workflow (ArcKit Pages, PlantUML server, VS Code, CLI) — same as `/arckit:diagram`'s PlantUML output. |
| Drift between `docs/guides/` and `plugins/arckit-claude/docs/guides/` | `check-guide-parity.py --sync` is run as part of the task checklist; CI gate catches future drift. |

## Migration Plan

No migration required. This is a purely additive change:
- New command file, template, guide, and reference are all new files.
- The `SOLN` doc-type registration is additive (new key in existing maps).
- All seven non-Claude extensions are regenerated via `converter.py` — no manual editing of generated files.
- Rollback: delete the new files and revert the `doc-types.mjs`, `pages.md`, and bash script changes; regenerate extensions.

## Open Questions

- **Q1**: Should the SOLN document include a "View this diagram" callout that references a specific PlantUML server URL, or should it remain tool-agnostic (ArcKit Pages / VS Code / CLI only)? *Deferrable — the template can use the same tool-agnostic pattern as `architecture-diagram-template.md`.*
- **Q2**: Should the command accept a `--mermaid` flag that explicitly rejects and explains why, or silently coerce to PlantUML? *Deferrable — the spec says "note the limitation and proceed with PlantUML"; the exact UX copy can be refined during implementation.*
