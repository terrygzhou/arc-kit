# artifact-generation Specification

## Purpose
ArcKit generates every governance artefact from registered templates and a central doc-type registry, so that artefact names are predictable, writes of unregistered codes are blocked at the gate, and the dashboard / graph-report / regime routing all agree on one list of codes. This spec captures the template-driven generation contract, the doc-type registry as single source of truth, the dual-registration rule, multi-instance sequencing, subdirectory routing, type/extension matching, regime classification partials, and the HIGH-severity feed into the Compliance Readiness scorecard.

## Requirements

### Requirement: Generation Is Template-Driven
The system SHALL never generate a governance artefact freeform: every artefact-producing command SHALL read its registered template (`.arckit/templates-custom/<name>-template.md` first, falling back to `${CLAUDE_PLUGIN_ROOT}/templates/<name>-template.md`), fill the template's placeholders, and write the result. The `<!-- DOC-CONTROL-HEADER -->` marker in the template SHALL be resolved via `templates/_partials/RENDERING.md`, not hand-written.

#### Scenario: template read before write
- **WHEN** `/arckit:stakeholders` is about to write `ARC-001-STKE-v1.0.md`
- **THEN** it has read `stakeholder-drivers-template.md` (custom override if present, else the plugin default) and resolved the `<!-- DOC-CONTROL-HEADER -->` marker via the partial before writing

#### Scenario: freeform artefacts are not produced
- **WHEN** a command has no registered template for the doc-type it claims to write
- **THEN** the command has no conforming name to fall back to and the write is blocked by the filename gate (see the registry requirement), so freeform artefacts cannot ship

### Requirement: Doc-Type Registry Is The Single Source Of Truth
The system SHALL treat `plugins/arckit-claude/config/doc-types.mjs` as the single source of truth for doc-type codes: every code a command writes MUST be a key in `DOC_TYPES` (with `name`, `category`, and optional `extension`, `regime`, `severity`). `scripts/generate-document-id.mjs` SHALL import `KNOWN_TYPES`, `MULTI_INSTANCE_TYPES`, and `SUBDIR_MAP` from this file (one copy, nothing to keep in sync) and SHALL reject an unregistered doc-type code rather than emit a name that the write gate will block. `validate-arc-filename.mjs` SHALL block (with a model-visible `decision: 'block'` reason listing the valid codes) any `Write` of an `ARC-*` file whose type code is not in `KNOWN_TYPES`.

#### Scenario: unregistered code is rejected at generation
- **WHEN** a command asks `generate-document-id.mjs` for a name with an unregistered code (e.g. `GLOS`)
- **THEN** the script exits non-zero with a usage/registry error instead of emitting `ARC-001-GLOS-v1.0.md`

#### Scenario: unregistered code is blocked at the write gate
- **WHEN** a `Write` targets `projects/001-*/ARC-001-FOOBAR-v1.0.md` and `FOOBAR` is not in `DOC_TYPES`
- **THEN** `validate-arc-filename.mjs` emits `{decision: 'block', reason: "ArcKit: Unknown document type code 'FOOBAR' ... Valid codes: ..."}` so the model can self-correct, and the write does not happen

#### Scenario: registered code normalises and passes
- **WHEN** a `Write` targets a conforming `ARC-NNN-<CODE>[-NNN]-vN.N.md` under `projects/` with a registered code
- **THEN** `validate-arc-filename.mjs` auto-corrects zero-padding, version format, project-ID mismatch, and subdirectory placement, then passes the write through

### Requirement: Dual Registration For Dashboard Visibility
The system SHALL require a doc-type code to be registered in BOTH `config/doc-types.mjs` (`DOC_TYPES`) AND the `/arckit:pages` allow-list (the "Only include these known artifact types" table inside `commands/pages.md`) for the code to appear on the rendered dashboard sidebar. `scripts/check-doc-type-registry.py` SHALL enforce this parity in CI: a code in `DOC_TYPES` missing from the pages table, or a code in the pages table missing from `DOC_TYPES`, is an error.

#### Scenario: code missing from pages table is flagged
- **WHEN** a new code is added to `DOC_TYPES` but not to the pages known-types table
- **THEN** `check_pages_parity` fails CI with "`DOC_TYPES` has '<code>' but the known-artifact-types table does not -- /arckit:pages will omit it from the dashboard sidebar"

#### Scenario: every registry code is on the dashboard
- **WHEN** `check_pages_parity` passes in CI
- **THEN** every code in `DOC_TYPES` has a row in the pages known-artifact-types table, so no generated artefact is silently dropped from the sidebar

#### Scenario: ghost code in pages table is flagged
- **WHEN** the pages known-types table lists a code that is not in `DOC_TYPES`
- **THEN** `check_pages_parity` fails CI with "known-artifact-types table lists '<code>', which is not in DOC_TYPES"

#### Scenario: silent omission without the guard
- **WHEN** a code is registered only in `DOC_TYPES` and the manifest hook records it correctly
- **THEN** the `/arckit:pages` scanner silently omits it from the dashboard sidebar (the failure mode the dual-registration guard exists to prevent)

### Requirement: Multi-Instance Types Require Sequence Numbers
The system SHALL define `MULTI_INSTANCE_TYPES` in `config/doc-types.mjs` as the single set of doc-type codes that require a `-NNN-` sequence segment in the filename (e.g. `ADR`, `DIAG`, `DFD`, `WARD`, `DMC`, `RSCH`, `AWRS`, `AZRS`, `GCRS`, `DSCT`, `TNDR`, `CMPT`, `WGAM`, `WCLM`, `WVCH`, `GOVR`, `GCSR`, `GLND`, `GRNT`, `CDAU`). `generate-document-id.mjs` SHALL allocate the next sequence via `--next-num DIR` (scanning `DIR` for existing `ARC-{PID}-{TYPE}-{NNN}-*.md` and starting at `001` if none exist), and `validate-arc-filename.mjs` SHALL assign the next sequence and move the file to the correct subdirectory when a multi-instance write is missing one.

#### Scenario: next sequence allocated
- **WHEN** `generate-document-id.mjs 001 ADR --filename --next-num ./decisions` runs and `decisions/` already holds `ARC-001-ADR-001-v1.0.md` and `ARC-001-ADR-002-v1.0.md`
- **THEN** it returns `ARC-001-ADR-003-v1.0.md`

#### Scenario: missing sequence is corrected at the gate
- **WHEN** a `Write` targets `projects/001-*/ARC-001-ADR-v1.0.md` (no sequence, but `ADR` is multi-instance)
- **THEN** `validate-arc-filename.mjs` assigns the next sequence number and moves the file to `decisions/`

#### Scenario: single-instance type gets no sequence
- **WHEN** a `Write` targets `ARC-001-REQ-v1.0.md` and `REQ` is not in `MULTI_INSTANCE_TYPES`
- **THEN** no `-NNN-` segment is added and the filename passes unchanged (subject to the other normalisations)

### Requirement: Subdirectory Routing
The system SHALL route artefacts into per-type subdirectories via `SUBDIR_MAP` in `config/doc-types.mjs`: `ADR`→`decisions/`, `DIAG`/`DFD`→`diagrams/`, `WARD`/`WDOC`/`WGAM`/`WCLM`/`WVCH`→`wardley-maps/`, `RSCH`/`AWRS`/`AZRS`/`GCRS`/`DSCT`/`TNDR`/`CMPT`/`GOVR`/`GCSR`/`GLND`/`GRNT`→`research/`, `DMC`→`data-contracts/`, `CDAU`→`audits/`, `FWRK`→`framework/`. `generate-document-id.mjs --relpath` SHALL prefix the resolved subdirectory, and `validate-arc-filename.mjs` SHALL move a misrouted write into the correct subdirectory.

#### Scenario: ADR routed to decisions
- **WHEN** `/arckit:adr` writes its first decision for project 001
- **THEN** the artefact lands at `projects/001-*/decisions/ARC-001-ADR-001-v1.0.md`

#### Scenario: research family routed to research
- **WHEN** `/arckit:research` (RSCH), `/arckit:tenders` (TNDR), or `/arckit:competitors` (CMPT) writes its artefact for project 001
- **THEN** each lands under `projects/001-*/research/` with its multi-instance sequence

#### Scenario: types without a subdirectory stay at project root
- **WHEN** `/arckit:requirements` (REQ) or `/arckit:stakeholders` (STKE) writes its artefact
- **THEN** the file is placed at the project root (`projects/001-*/ARC-001-REQ-v1.0.md`) because neither code has a `SUBDIR_MAP` entry

### Requirement: Type/Extension Matching
The system SHALL enforce that the file extension matches the type code's registered `extension` (default `.md`): the `/arckit:pages` scanner and the filename gate SHALL reject `ARC-001-DECK-v1.0.md` (DECK is registered as `.html`) and `ARC-001-REQ-v1.0.html` (REQ is `.md`) as type/extension mismatches.

#### Scenario: DECK must be HTML
- **WHEN** an executive-deck artefact is produced
- **THEN** its filename is `ARC-001-DECK-v1.0.html` and a `.md` variant is rejected as a mismatch

#### Scenario: markdown types must be .md
- **WHEN** a `Write` targets `ARC-001-REQ-v1.0.html`
- **THEN** the type/extension mismatch is rejected (REQ is registered with the default `.md` extension)

### Requirement: Regime Classification Partials
The system SHALL select the Document Control classification partial per artefact via `REGIME_PARTIALS` in `config/doc-types.mjs` (one partial per regime: `UK`/`MOD`/`EU`→`document-control-uk.md`, `AT`→`-at`, `AU`→`-au`, `CA`→`-ca`, `FR`→`-fr`, `NL`→`-nl`, `UAE`→`-uae`, `US`→`-us`). Regimes in `UK_FALLBACK_BY_DESIGN` (`UK`, `MOD`, `EU`) SHALL name the UK partial as the default outcome of the user-config chain rather than a hard route, so a non-UK-configured entity running a UK-regime command keeps its own classification ladder. `scripts/tests/test-regime-registration.mjs` SHALL enforce that a regime in the fallback set maps to the UK partial and a regime outside it maps to `document-control-<lowercased regime>.md`.

#### Scenario: UK-regime artefact uses the UK ladder
- **WHEN** a UK-regime artefact (e.g. `TCOP`, `AIPB`, `ATRS`, `DPIA`) renders its Document Control header
- **THEN** the `document-control-uk.md` partial is inlined with `${user_config.organisation_name}` and `${user_config.default_classification}` substituted

#### Scenario: fallback regime defers to user config
- **WHEN** a UAE-configured entity runs a UK-regime command
- **THEN** the regime routing does not hard-route to the UK ladder; the artefact falls through to the user-config chain and keeps the UAE classification ladder

#### Scenario: CI pins the partial mapping
- **WHEN** `test-regime-registration.mjs` runs
- **THEN** every regime in `UK_FALLBACK_BY_DESIGN` maps to `document-control-uk.md` and every other regime maps to its own `document-control-<regime>.md`, so pointing e.g. `CA` at the Australian ladder fails

### Requirement: HIGH Severity Feeds The Compliance Readiness Scorecard
The system SHALL mark a doc-type `severity: 'HIGH'` in `DOC_TYPES` to indicate it counts toward the Compliance Readiness scorecard in `/arckit:graph-report`. HIGH-severity coverage SHALL be computed per regime (via `HIGH_SEVERITY_BY_REGIME`, with `UNIVERSAL` for regime-less types such as `RISK`, `TRAC`, `PRIN-COMP`, `CONF`) so a single-regime project is not penalised for missing another regime's HIGH-severity artefacts, and the dashboard SHALL surface which HIGH-severity types are present versus missing per project.

#### Scenario: per-regime HIGH-severity bucketing
- **WHEN** `HIGH_SEVERITY_BY_REGIME` is derived from `DOC_TYPES`
- **THEN** regime-less HIGH types (`RISK`, `TRAC`, `PRIN-COMP`, `CONF`) bucket under `UNIVERSAL` and regime-tagged HIGH types (e.g. `TCOP`/`AIPB`/`ATRS`/`DPIA`/`SVCASS` under `UK`, `SECD-MOD`/`JSP936` under `MOD`) bucket under their regime

#### Scenario: scorecard surfaces gaps
- **WHEN** `/arckit:graph-report` renders the Compliance Readiness section for a project
- **THEN** it lists which HIGH-severity doc types for that project's regime are present and which are missing (e.g. the 12-code list `TCOP, SECD, SECD-MOD, DPIA, SVCASS, RISK, TRAC, CONF, PRIN-COMP, AIPB, ATRS, JSP936`), so the architect can decide which gaps to close

#### Scenario: single-regime project not over-penalised
- **WHEN** a UAE-only project is scored
- **THEN** only the HIGH-severity types relevant to its regime count, so it is not penalised for missing UK Gov artefacts it was never expected to produce
