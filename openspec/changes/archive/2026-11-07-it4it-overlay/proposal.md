## Why

The Open Group IT4IT Standard v3.1 (Snapshot, S261, 12 October 2026) is now the Open Group's recommended reference architecture for managing IT as product-based investment: seven integrated value streams (Evaluate, Explore, Integrate, Deploy, Publish, Consume, Operate), functional components, key data objects, and an ArchiMate 3.2 metamodel. It is the direct successor to IT4IT 3.0 (C221, expired) and complements O-AA (C208) — O-AA is the method; IT4IT is the target state for IT product-lifecycle management.

ArcKit has first-class overlays for TOGAF ADM and O-AA but no way to produce IT4IT-aligned artefacts. Teams doing IT service-catalog, product-portfolio, or deployment-pipeline design currently have no governed command, template, doc-type, or reference to anchor against. This change adds a new community overlay plugin `arckit-it4it` — structured exactly like `arckit-togaf-adm` and `arckit-oaa` (standalone plugin + sub-plugin copy in the core tree) — so IT4IT v3.1 value-stream and functional-component modelling is as governed and reproducible as ADM or OAA work.

Source material: the Enterprise Architecture Lead's full-text study of S261 (`Eywalink/reference/it4it/eyw-740-it4it-standard-study.md`) plus the C221 standard text.

## What Changes

New standalone overlay plugin `plugins/arckit-it4it/` (plus its overlay copy `plugins/arckit-claude/plugins/it4it/`), modelled on `arckit-togaf-adm` and `arckit-oaa`:

- **6 commands**, one per IT4IT modelling task, mapped to the seven value streams and functional groups:
  - `it4it-value-network` — Value Network: the full set of relationships across all value-creating functions (top-level map; trigger/stakeholder/stages for all seven value streams).
  - `it4it-value-stream` — Value Stream documentation for one of the seven streams (scenario, stages, stakeholders, participating data objects and functional components) — multi-instance artefact.
  - `it4it-strategy-portfolio` — Strategy to Portfolio functions (Ch 6): Policy, Strategy, Portfolio Backlog, Proposal/Resource Plan functional components + data objects.
  - `it4it-develop-test` — Requirement to Deploy functions (Ch 7): Develop (Product Backlog, Requirement, Product Design, Source Control, Pipeline, Build Package, Release Composition) + Test components.
  - `it4it-consume-fulfil` — Request to Fulfill functions (Ch 8): Consume (Consumption Experience, Identity, Offering, Order, Chargeback) + Fulfill (Change, Fulfillment Orchestration, Resource, Fulfillment, Usage).
  - `it4it-operate-assure` — Detect to Correct functions (Ch 9): Support (Service Level, Incident, Problem, Knowledge) + Assure (Configuration, Monitoring, Event, Diagnostics & Remediation), plus Supporting Functions (Ch 10) cross-reference.
- **1 recipe** `it4it-full.yaml` — a build pipeline wiring core `PRIN` → the six commands in dependency order.
- **6 templates** (one per command) and **references** (IT4IT citation-instructions, quality-checklist, value-stream reference, functional-component reference, intake-discovery-dimensions adapted for IT4IT).
- **Schemas** for machine-checkable artefacts (value-stream, functional-component maps) + a stdlib `validate-architecture.py` validator mirroring OAA's.
- **New doc-type codes** registered in `plugins/arckit-claude/config/doc-types.mjs` (IT4IT family, see design.md for code choices) + dual registration in the two `generate-document-id.sh` copies where multi-instance.
- **Registration**: `PLUGIN_SOURCES` entry in `scripts/converter.py`; `.claude-plugin/marketplace.json` entry; sub-plugin copy under `plugins/arckit-claude/plugins/it4it/` (commands/references/templates sync targets per `sync-shared-assets.py`).
- **Intake posture**: same hard-gate MANDATORY prerequisite model as TOGAF `togaf/adm` and OAA — every IT4IT command hard-stops on a missing MANDATORY global artefact (`PRIN`), never renders it as `TBD`; the interview itself stays a soft gate (skipped interview inputs render as quoted `TBD`). IT4IT tone: reference-architecture posture — the commands document conforming artefacts and add no diagram/output mandate beyond the template's own sections.

Non-goals: no changes to the generic `template-driven-intake` mechanism; no new core-plugin command; no vendor-specific refinements (IT4IT is vendor-neutral by design; vendor extensions are out of scope); no ArchiMate model file generation (the metamodel is referenced, not emitted — ArchiMate output remains the separate `/arckit:archimate` path); IT4IT 3.1 is a Snapshot — artefacts carry a "reference, not conformance" citation posture, and commands cite S261 explicitly rather than claiming standard conformance.

## Capabilities

### New Capabilities

- `it4it-intake`: the IT4IT overlay plugin — six governed commands, one recipe, templates/references/schemas/validator, doc-type registration, converter + marketplace + sub-plugin registration, and the MANDATORY-`PRIN` hard-gate intake posture consistent with TOGAF ADM and OAA.

### Modified Capabilities

<!-- none — the generic mechanism lives in `template-driven-intake`; this change ships a new overlay, it does not change the base mechanism -->

## Impact

- New: `plugins/arckit-it4it/` (plugin tree: `.claude-plugin/plugin.json`, `VERSION`, `CHANGELOG.md`, `README.md`, `commands/`, `templates/`, `recipes/`, `references/`, `schemas/`, `validate-architecture.py`) and `plugins/arckit-claude/plugins/it4it/` (overlay copy: commands, references, templates).
- `plugins/arckit-claude/config/doc-types.mjs`: new IT4IT code entries.
- `scripts/bash/generate-document-id.sh` + `plugins/arckit-claude/scripts/bash/generate-document-id.sh`: multi-instance registration for any IT4IT multi-instance code (`check-multi-instance-parity.py` enforces three-way parity).
- `plugins/arckit-claude/commands/pages.md`: allow-list table rows for the new codes (dual-registration test).
- `scripts/converter.py`: `plugins/arckit-it4it` added to `PLUGIN_SOURCES` (community position, before core).
- `.claude-plugin/marketplace.json`: `arckit-it4it` entry.
- `scripts/sync-shared-assets.py`: `plugins/arckit-it4it` must carry its own copies of shared partials/references (not in `SYNC_EXEMPT_PLUGINS`).
- Regenerate all seven `extensions/` targets via `python scripts/converter.py`.
- Regression tests: `tests/plugin/test_it4it_intake.py` (command bodies carry MANDATORY `PRIN` gate + intake step; doc-type codes resolve; recipe sanity; sub-plugin copy parity).
- CI gates: `check-doc-type-registry.py`, `check-doctype-collisions.py` (unique codes), `check-recipies.py`, `check-multi-instance-parity.py`, `check-references.py`, `check-shared-asset-sync` all green before merge.
