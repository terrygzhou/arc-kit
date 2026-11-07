# it4it-intake Specification

## Purpose
Governs the IT4IT overlay plugin (`arckit-it4it`): how the overlay ships
(standalone tree plus sub-plugin copy), the six intake commands and their
doc-type registration, the MANDATORY `PRIN` hard gate on every command,
the no-diagram-mandate tone guard (S261 snapshot citation, no conformance
claims), the `it4it-full` bulk-build recipe's core-first dependency order,
and the CI-enforced schema validator gate.

## Requirements

### Requirement: IT4IT Overlay Plugin Ships As A Standalone Overlay With A Sub-Plugin Copy

The IT4IT overlay SHALL ship as a standalone community plugin at
`plugins/arckit-it4it/` (with `.claude-plugin/plugin.json`, `VERSION`,
`CHANGELOG.md`, `README.md`, `commands/`, `templates/`, `recipes/`,
`references/`, `schemas/`, and `validate-architecture.py`) AND as a
sub-plugin copy at `plugins/arckit-claude/plugins/it4it/` (commands,
references, templates) — the same two-tree pattern as `arckit-oaa` and
`arckit-togaf-adm`. The plugin manifest SHALL depend on `arckit =6.11.0`, be
`defaultEnabled: false`, and carry the standard `userConfig` fields
(`default_classification`, `organisation_name`, `project_issue_prefix`,
`references_dir`).

#### Scenario: Plugin manifest is well-formed

- **WHEN** the test loads `plugins/arckit-it4it/.claude-plugin/plugin.json`
- **THEN** it parses as JSON, has `name: arckit-it4it`, `version: 6.11.0`,
  `defaultEnabled: false`, a dependency on `arckit` pinned `=6.11.0`, and the
  four standard `userConfig` keys

#### Scenario: Sub-plugin copy exists in the core tree

- **WHEN** the test lists `plugins/arckit-claude/plugins/it4it/`
- **THEN** it contains the same six command files, the reference files, and
  the template files as the standalone tree, each byte-identical to its
  standalone counterpart (except files declared in `sync-shared-assets.py`
  `LOCAL_OVERRIDES`, which only need to exist)

### Requirement: The Six IT4IT Commands Are Registered, Governed, And Doc-Type-Resolving

The overlay SHALL ship six commands — `it4it-value-network` (`ITVN`),
`it4it-value-stream` (`ITVS`), `it4it-strategy-portfolio` (`ITSF`),
`it4it-develop-test` (`ITDT`), `it4it-consume-fulfil` (`ITCF`), and
`it4it-operate-assure` (`ITOA`) — each writing a governed artefact
`ARC-{P}-<CODE>-v1.0.md` (or `ARC-{P}-ITVS-{NNN}-v1.0.md` for the
multi-instance value-stream command). Every code SHALL be registered in
`plugins/arckit-claude/config/doc-types.mjs` (category `Architecture`, no
regime tag), present in the `pages.md` allow-list table, and referenced by
the command's frontmatter. No command SHALL write a code that is missing
from the registry.

#### Scenario: A command's doc-type code resolves against the registry

- **WHEN** `check-doc-type-registry.py` runs after the plugin lands
- **THEN** every `output.type` in `plugins/arckit-it4it/recipes/*.yaml` and
  every `ARC-{PID}-{CODE}-v` filename named in the six command bodies
  resolves to a code defined in `doc-types.mjs`

#### Scenario: The multi-instance value-stream code is registered three times

- **WHEN** `check-multi-instance-parity.py` runs
- **THEN** `ITVS` appears in `doc-types.mjs`'s `MULTI_INSTANCE_TYPES`,
  `scripts/bash/generate-document-id.sh`, and
  `plugins/arckit-claude/scripts/bash/generate-document-id.sh`

### Requirement: IT4IT Intake Hard-Blocks On MANDATORY Prerequisites (TOGAF-And-OAA-Consistent)

Every IT4IT command SHALL declare a **MANDATORY** prerequisite tier grounded
in the `000-global` `PRIN` (Architecture Principles) artefact, with an "If
missing: STOP and ask user to run `/arckit:principles` first" instruction,
mirroring `togaf/adm`'s `adm-preliminary` and the OAA overlay's hard gate.
A missing MANDATORY prerequisite artefact SHALL stop the command; it is a
hard dependency and SHALL never be rendered as `TBD`. All other
prerequisites (e.g. an existing `ITVN` value-network map for
`it4it-value-stream`) SHALL remain **RECOMMENDED** (noted when missing,
non-blocking). Interview inputs the user skips SHALL still render as quoted
`TBD` markers (generic `template-driven-intake` behaviour).

#### Scenario: Missing PRIN stops an IT4IT command

- **WHEN** the user runs `/arckit:it4it-value-stream` and no
  `ARC-000-PRIN-v[N].md` exists in `000-global`
- **THEN** the command stops and asks the user to run
  `/arckit:principles` first; it does not render `ARC-{P}-ITVS-NNN-v1.0.md`
  and does not render `PRIN` as `TBD`

#### Scenario: Recommended prerequisites stay soft

- **WHEN** the user runs `/arckit:it4it-value-stream` and no `ITVN`
  value-network map exists
- **THEN** the command notes the missing value-network map in its summary and
  proceeds; only a missing `PRIN` is a hard stop

#### Scenario: Bulk build respects the IT4IT hard gate

- **WHEN** the `arckit-build` harness runs the `it4it-full` recipe on a
  project that has no `PRIN`
- **THEN** the first target (`PRIN` via `arckit:principles`) is generated
  first by the recipe; a manual run of any IT4IT target on a
  `PRIN`-less project fails or is skipped with a prompt to generate `PRIN`
  first, rather than rendering a `TBD`-filled artefact

### Requirement: The IT4IT Interview Adds No Diagram Or Output Mandate (Reference-Architecture Tone Guard)

For `it4it` overlay commands the intake interview SHALL NOT introduce any
diagram or output demand the IT4IT template does not already ask for. The
interview collects only the inputs the effective IT4IT template requests.
The MANDATORY prerequisite hard gate is a *dependency* on an upstream
artefact and is NOT a diagram or output demand, so it does not conflict with
this requirement. No command SHALL emit ArchiMate model files (ArchiMate
output remains the `/arckit:archimate` path); the commands document
conforming reference artefacts only.

#### Scenario: An IT4IT interview never mandates a diagram

- **WHEN** the user runs `/arckit:it4it-value-network` and answers every
  intake question
- **THEN** the interview asks only for the inputs the `it4it-value-network`
  template already requests and does not require the user to commit to a
  diagram or output the template does not ask for

#### Scenario: Snapshot status forbids conformance claims

- **WHEN** any rendered IT4IT artefact cites the standard
- **THEN** it cites "The Open Group IT4IT Standard, Version 3.1
  (Snapshot), S261, 12 October 2026" as a *reference* and contains no
  statement claiming IT4IT conformance (S261 is a Snapshot, not an
  approved standard)

### Requirement: The IT4IT Recipe Wires Core-First Dependency Order

`plugins/arckit-it4it/recipes/it4it-full.yaml` SHALL wire
`PRIN` (via `arckit:principles`) → `ITVN` → `ITVS` → `ITSF` → `ITDT` →
`ITCF` → `ITOA`, with deps resolving to earlier target IDs, an acyclic
graph, and no wave wider than the concurrent-subagent cap. Target `output`
entries SHALL use registered doc-type codes. The recipe SHALL pass
`scripts/check_recipes.py`.

#### Scenario: The recipe passes the sanity linter

- **WHEN** `python3 scripts/check_recipes.py` runs
- **THEN** `it4it-full.yaml` parses, has unique target IDs, every `deps:`
  entry resolves, the graph is acyclic, and no wave exceeds the cap

### Requirement: The IT4IT Validator Gate Is CI-Enforced

`plugins/arckit-it4it/validate-architecture.py` SHALL be stdlib-only (an
embedded minimal JSON-Schema validator, with PyYAML optional and
gracefully-skipped when absent) and SHALL provide a `gate` mode that
load-checks every shipped schema and runs a self-test, exiting non-zero on
failure. The gate SHALL be registered in `scripts/ci-local.sh` and the
`lint-markdown` GitHub Actions workflow exactly as
`plugins/arckit-oaa/validate-architecture.py gate` is.

#### Scenario: The gate runs clean on a fresh checkout

- **WHEN** `python3 plugins/arckit-it4it/validate-architecture.py gate`
  runs
- **THEN** every shipped schema loads, the self-test passes, and the exit
  code is 0 (with PyYAML absent, YAML schemas are skipped with a notice and
  the gate stays green offline)
