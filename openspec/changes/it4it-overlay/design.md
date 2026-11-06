# Design — it4it-overlay

## Context

The IT4IT v3.1 standard (S261) is the Open Group's reference architecture for IT
product-lifecycle management: seven value streams (Evaluate, Explore, Integrate,
Deploy, Publish, Consume, Operate) supported by four functional groups
(Strategy to Portfolio, Requirement to Deploy, Request to Fulfill, Detect to
Correct) plus six supporting functions (Financial Management, GRC, Workforce
Management, Sourcing & Vendor Management, Intelligence & Reporting,
Collaboration & Communication). Each functional component owns key data
objects (KDOs); the two data backbones are the **Digital Product Backbone**
(Digital Product, Digital Product Contract, Service Offering, System) and the
**Service Offering Backbone** (Service Offering, Order, Subscription). The
metamodel is ArchiMate 3.2. IT4IT complements O-AA (C208): O-AA is the method,
IT4IT is the target state — this pairing is the Open Group's recommended
EA + agile architecture stack.

ArcKit's two closest precedents shape everything here:

- **`arckit-togaf-adm` / `arckit-oaa`** — standalone community overlay plugins
  (`plugins/arckit-<name>/`) with a matching sub-plugin copy
  (`plugins/arckit-claude/plugins/<short>/`), one recipe each, a
  stdlib-only `validate-architecture.py`, and MANDATORY-`PRIN` hard-gate
  intake posture (per the archived `2026-09-01-oaa-intake` change).
- **The 2026-07 `GLOS`/`FWRK` incidents (#712)** — doc-type codes written by
  commands but missing from `doc-types.mjs` got hard-blocked by the
  `validate-arc-filename.mjs` PreToolUse hook with no fallback name. Every
  new code must be registered before the commands that reference it ship.

## Decisions

### D1: Standalone overlay plugin, not a core-plugin extension

`plugins/arckit-it4it/` + `plugins/arckit-claude/plugins/it4it/`, mirroring
`arckit-oaa` / `arckit-togaf-adm`. IT4IT is a separate standard from TOGAF
and O-AA with its own value-stream/functional-component vocabulary — a
standalone plugin keeps the 74-command core clean and lets IT4IT artefacts
opt in via `enable_community_overlays = true`.

### D2: Six commands, one per modelling task

| Command | Doc code | Coverage | Multi-instance |
|---|---|---|---|
| `it4it-value-network` | `ITVN` | Value Network: all seven value streams — trigger, stakeholder, stages, cross-stream dependencies | single |
| `it4it-value-stream` | `ITVS` | One value stream in depth: scenario, stages, stakeholder, participating KDOs + functional components | **yes** (`ITVS-001`) |
| `it4it-strategy-portfolio` | `ITSF` | Ch 6: Policy, Strategy, Portfolio Backlog, Proposal/Resource Plan | single |
| `it4it-develop-test` | `ITDT` | Ch 7: Develop (Product Backlog, Requirement, Product Design, Source Control, Pipeline, Build Package, Release Composition) + Test | single |
| `it4it-consume-fulfil` | `ITCF` | Ch 8: Consume + Fulfill functional components and KDOs | single |
| `it4it-operate-assure` | `ITOA` | Ch 9: Support + Assure, plus Ch 10 Supporting Functions cross-reference | single |

Rationale: one command per functional group means one template, one intake
scope, and one doc-type per artefact. `ITVS` is multi-instance because a
project documents up to seven value streams (the code is sequence-numbered
`ARC-{P}-ITVS-001-v1.0.md` … `-007-`).

Code-choice note: `IT4IT` is not a valid code (registry regex is
`[A-Z][A-Z0-9_-]*` — digits allowed but the 4+1 shape is unusual and collides
visually with the version string); the `IT`-prefixed family keeps all codes
grouped and greppable. `ITVN`/`ITVS`/`ITSF`/`ITDT`/`ITCF`/`ITOA` are all
new — verified absent from `doc-types.mjs`.

### D3: Doc-type registration is the blocking prerequisite

All six codes register in `plugins/arckit-claude/config/doc-types.mjs`
(category `Architecture`, no `regime` tag — IT4IT is vendor- and
jurisdiction-neutral). `ITVS` also joins `MULTI_INSTANCE_TYPES` in three
places (`doc-types.mjs`, `scripts/bash/generate-document-id.sh`,
`plugins/arckit-claude/scripts/bash/generate-document-id.sh`) — enforced by
`check-multi-instance-parity.py`. Every code also gets an allow-list row in
`plugins/arckit-claude/commands/pages.md` (dual-registration test).

### D4: MANDATORY `PRIN` hard gate; interview stays a soft gate

Same posture as TOGAF ADM and OAA (archived `oaa-intake`): every IT4IT
command declares `PRIN` (Architecture Principles, `000-global`) as
**MANDATORY** with "If missing: STOP and ask user to run
`/arckit:principles` first" — a missing MANDATORY prerequisite artefact is a
hard dependency, never rendered as `TBD`. All other prerequisites (e.g. an
existing `ITVN` value-network map for the per-stream `ITVS` command) stay
**RECOMMENDED** (noted when missing, non-blocking). Skipped interview inputs
still render as quoted `TBD` markers (generic `template-driven-intake`).

### D5: Reference-architecture tone guard

IT4IT commands SHALL add no diagram or output mandate beyond their template's
own sections. The tone is *conforming-reference documentation*: artefacts
state the KDOs, cardinalities, and data flows of a conforming solution and
cite S261 explicitly. No ArchiMate model files are emitted (ArchiMate output
remains the `/arckit:archimate` path). Because S261 is a Snapshot, not an
approved standard, citation-instructions.md carries a "reference, not
conformance" rule: artefacts may cite S261 as a reference but SHALL NOT
claim IT4IT conformance.

### D6: Sub-plugin copy + shared-asset sync

`plugins/arckit-claude/plugins/it4it/` carries its own copies of commands,
references, and templates (commands resolve `${CLAUDE_PLUGIN_ROOT}` against
the sub-plugin's runtime root, as OAA/TOGAF do). `plugins/arckit-it4it/` is
**not** in `sync-shared-assets.py`'s `SYNC_EXEMPT_PLUGINS` — it must carry
copies of `templates/_partials/` and `references/` it references. Any file
the IT4IT commands customise (e.g. `references/citation-instructions.md`
with the S261 row) is added to `LOCAL_OVERRIDES` exactly as OAA's three
files are.

### D7: One recipe, core-anchored

`plugins/arckit-it4it/recipes/it4it-full.yaml` wires
`PRIN` (core `arckit:principles`) → `ITVN` → `ITVS` (multi-instance) →
`ITSF` → `ITDT` → `ITCF` → `ITOA`, mirroring `oaa-full.yaml`'s
core-anchored pattern. Recipe sanity (`check_recipes.py`): unique target IDs,
deps resolve, acyclic, wave width under the concurrency cap.

### D8: Validator mirrors OAA's

Stdlib-only `plugins/arckit-it4it/validate-architecture.py` with embedded
draft-07 subset validator, a `gate` mode that load-checks all shipped
schemas and runs a self-test, and a `drift` mode. Shipped schemas cover the
machine-checkable artefacts (value-stream map, functional-component map).
Registered in `ci-local.sh` / the lint-markdown workflow exactly as
`plugins/arckit-oaa/validate-architecture.py gate` is.

## Goals / Non-Goals

**Goals:** six governed IT4IT v3.1 modelling commands; full doc-type
registration so `validate-arc-filename.mjs` never blocks; TOGAF/OAA-consistent
hard-gate intake; one buildable recipe; CI gates green.

**Non-Goals:** no ArchiMate model file generation; no vendor refinements
(non-normative in the standard); no conformance claims (Snapshot status);
no changes to `template-driven-intake`; no new core-plugin commands.
