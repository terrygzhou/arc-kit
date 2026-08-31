# ArcKit O-AA Plugin — Command / Artefact / Axiom / TOGAF-ADM Mapping

**Status:** DRAFT v1.0 — architecture review artefact (EyWALink EA practice, EYW-214)
**Date:** 2026-08-24
**Sources inspected:** `plugins/arckit-oaa/` (v6.7.5 + Unreleased), `plugins/arckit-claude/` (core, bundled `plugins/oaa` mirror, `config/doc-types.mjs`), `plugins/arckit-togaf-adm/`, `extensions/arckit-paperclip/` (`src/data/commands.json`, templates, doc-type registry), C208 HTML package (`Obsidian Vault/o-aa/html/`, build 2022-10-12, C208 + Technical Corrigendum U221), and the O-AA study notes (`Obsidian Vault/o-aa/study-note.md`).

This document maps the **O-AA (Open Agile Architecture, C208) overlay** in ArcKit across four dimensions:

1. which **tool commands** exist on each target surface,
2. which **generated artefacts** (doc-type codes, filenames, YAML schemas) they produce,
3. which of the **16 published O-AA axioms** (C208 Ch. 9) each command owns or cites,
4. how the O-AA sprint model relates to **TOGAF ADM phases** (C182).

> Framing note: C208 defines **no ADM cycle**. The sprint↔ADM mapping below is an
> **ArcKit convention over TOGAF ADM (C182)** — this is stated explicitly in the plugin's
> own `references/oaa-reference.md`, and is the correct reading.

---

## 1. Plugin inventory (what "the oaa plugin" actually is)

| Surface | Location | Content |
|---|---|---|
| **Canonical overlay** | `plugins/arckit-oaa/` | 5 commands, 5 templates + `_partials`, `oaa-full` recipe, references (16-axiom table, quality checklist, citation instructions), `userConfig` keys, V6.7.5 |
| **Bundled mirror** | `plugins/arckit-claude/plugins/oaa/` | Same plugin shipped inside the core marketplace bundle. Differs only in cross-command namespace prefixes (`/arckit-oaa:`, `/arckit-togaf-adm:` vs bare `/arckit:`) |
| **Paperclip extension** | `extensions/arckit-paperclip/` | 5 OAA commands present in `src/data/commands.json` (`arckit-oaa-adm-lite`, `arckit-product-architecture`, `arckit-agile-strategy`, `arckit-agile-security`, `arckit-agile-governance`) of 173 total; OAA templates and doc-type codes present; plain `${KEY}` placeholders instead of `user_config` substitution |
| **Sibling TOGAF overlay** | `plugins/arckit-togaf-adm/` | 13 commands covering ADM Preliminary…Phase H + Repository; `togaf-adm-full` and `togaf-agent-full` recipes |
| **Core foundation** | `plugins/arckit-claude/commands/` | Foundation commands the OAA recipe depends on: `principles` (PRIN), `requirements` (REQ), `stakeholders` (STKE), plus `backlog` (BKLG), `strategy` (STRAT), `roadmap` (ROAD), `adr` (ADR), `health`, `traceability` (TRAC), `risk` (RISK) |

Provenance: `arckit-oaa` was **split from `arckit-togaf-adm` at v6.7.5 (2026-08-13)**. Unreleased changes add a CI axiom-integrity guard (`scripts/check_oaa_axioms.py`, wired via `tests/plugin/test_oaa_axiom_guard.py`), real C208 coordinates in command/template headers, and `user_config.*` placeholder de-hard-coding.

### Doc-type codes (single source of truth: `config/doc-types.mjs`)

| Code | Name | Category | Filename pattern |
|---|---|---|---|
| `OASTR` | Agile Strategy | Planning | `ARC-{P}-OASTR-vN.N.md` |
| `OAPR` | Product Architecture | Architecture | `ARC-{P}-OAPR-vN.N.md` |
| `OAAL` | O-AA ADM Lite | Architecture | `ARC-{P}-OAAL-vN.N.md` |
| `OASEC` | Agile Security | Governance | `ARC-{P}-OASEC-vN.N.md` |
| `OAGOV` | Agile Governance | Governance | `ARC-{P}-OAGOV-vN.N.md` |

All five codes are registered in `doc-types.mjs` **and** in the `/arckit:pages` dashboard allow-list (`commands/pages.md`) — the dual-registry drift warned about in the registry header is currently clean for OAA. Names are enforced by the `validate-arc-filename` hook; an unrecognised code blocks the write (see #712 in registry comments).

---

## 2. Command ↔ generated-artefact map

| Command (Claude) | Command (Paperclip) | Doc type / artefact file | Primary C208 content | Shared YAML schemas declared |
|---|---|---|---|---|
| `/arckit-oaa:oaa-adm-lite` | `arckit-oaa-adm-lite` | `ARC-{P}-OAAL-v1.0.md` | Part 1 Core (Ch. 3–9); sprint↔ADM map = ArcKit convention over C182 | `vision.yaml`, `business-architecture.yaml`, `data-architecture.yaml`, `technology-architecture.yaml`, `implementation-strategy.yaml`, `governance-report.yaml`, `change-request.yaml` |
| `/arckit-oaa:product-architecture` | `arckit-product-architecture` | `ARC-{P}-OAPR-v1.0.md` | Ch. 14 Product Architecture (syllabus domain 7) | `product-architecture.json`, `vision.yaml`, `implementation-strategy.yaml` |
| `/arckit-oaa:agile-strategy` | `arckit-agile-strategy` | `ARC-{P}-OASTR-v1.0.md` | Ch. 11 Agile Strategy + Ch. 3 Dual Transformation (syllabus domain 2) | `strategy-canvas.json` (O-AA specific), `product-architecture.json`, `vision.yaml`, `implementation-strategy.yaml` |
| `/arckit-oaa:agile-security` | `arckit-agile-security` | `ARC-{P}-OASEC-v1.0.md` | Ch. 4.6 Security by Design + Axiom 16 + G216 Security Playbook (syllabus domain 9) | `security-backlog.json`, `threat-model.yaml`, `compliance-evidence.json`, `vision.yaml` |
| `/arckit-oaa:agile-governance` | `arckit-agile-governance` | `ARC-{P}-OAGOV-v1.0.md` | Ch. 8 Agile Governance | `governance-cadence.json`, `change-request.yaml`, `compliance-evidence.json`, `vision.yaml` |

Foundation artefacts consumed by all OAA commands (produced by core, stored in `projects/000-global/`):

| Foundation command | Artefact | Role in OAA workflow |
|---|---|---|
| `/arckit:principles` | `ARC-000-PRIN-v1.0.md` | Guardrails / decision framework feeding every OAA sprint |
| `/arckit:requirements` | `ARC-{P}-REQ-v1.0.md` | Backlog seed for architecture stories |
| `/arckit:stakeholders` | `ARC-{P}-STKE-v1.0.md` | Stakeholder concern→compliance mapping (Sprint 0) |

Artefact location rule: `projects/{NNN}-{slug}/ARC-{P}-{TYPE}-v1.0.md` (version bumped, never overwritten); multi-instance types (e.g. `ADR`) use sequence numbers and subdirectories per `SUBDIR_MAP` in `doc-types.mjs` (`ADR` → `decisions/`).

Handoff chain declared in command frontmatter:
`oaa-adm-lite → product-architecture / agile-strategy / agile-security / agile-governance`; `product-architecture → agile-strategy / agile-security`; `agile-strategy → agile-security / agile-governance`; `agile-security → agile-governance / agile-strategy`; `agile-governance → oaa-adm-lite / agile-security` (cycle closure).

---

## 3. Sprint ↔ TOGAF ADM phase relationship

The `oaa-adm-lite` command compresses the full ADM cycle into sprint windows (2–4 week engagement windows):

| Sprint | TOGAF ADM phase(s) | OAA focus | Key output (schema-validated YAML) | TOGAF-overlay equivalent (traditional track) |
|---|---|---|---|---|
| Sprint 0 | Preliminary + A | Vision, stakeholders, scope, regulatory baseline | `vision.yaml` | `/arckit:adm-preliminary` → `ADMP`; `/arckit:business-capability-map` → `BPCM` |
| Sprint 1 | B + C (part) | Business + Data architecture | `business-architecture.yaml`, `data-architecture.yaml` | `/arckit:data-architecture` → `DATA` (Phase C.2) |
| Sprint 2 | C (part) + D | Technology architecture | `technology-architecture.yaml` | `/arckit:technology-architecture` → `TECH`; `/arckit:application-inventory` → `APP`; `/arckit:application-rationalization` → `APPR` |
| Sprint 3 | E + F | Implementation waves / transition | `implementation-strategy.yaml` | `/arckit:gap-analysis` → `GAPA`; `/arckit:transition-architecture` → `TRANS` |
| Sprint 4+ | G + H | Governance + change management (ongoing) | `governance-report.yaml`, `change-request.yaml` | `/arckit:architecture-board` → `BORD`; `/arckit:architecture-change` → `ACHG`; `/arckit:architecture-repository` → `REPO` |

Structural differences between the two tracks:

- **Granularity:** traditional track = one document per ADM concern (13 commands, 9 doc types); OAA track = one planning document (`OAAL`) that carries five sprints, each emitting schema-validated YAML, plus four specialist documents. OAA has *no dedicated Phase B/C/D command* — business/data/tech architecture are sprint deliverables inside `OAAL`.
- **Cadence & governance:** quarterly architecture boards (`BORD`) vs sprint review panels (3–5 members, `OAGOV`); stage-gate re-entry vs sprint-velocity change requests (both tracks share the `change-request.yaml` schema).
- **Shared foundation:** both recipes (`oaa-full`, `togaf-adm-full`) start from the same core commands (`principles` → `requirements`/`stakeholders`) and end with the same `post_build_hooks`: `arckit:health` + `arckit:traceability`.
- **Shared schemas:** `vision.yaml` (↔ `adm-preliminary`) and `implementation-strategy.yaml` (↔ `transition-architecture`) are declared shared so artefacts stay interchangeable regardless of track — the intended "enterprise baseline via TOGAF, capability execution via OAA" combination.
- **Selection rule (per plugin READMEs):** use `arckit-togaf-adm` when a full regulatory audit trail, 50+ stakeholder gates, or >4-week current-state assessment is required; use `arckit-oaa` when the hard timeline is under 8 weeks, the culture is sprint-driven, or it is a first engagement needing a rapid architecture vision.

### `oaa-full` recipe (executable form of the above)

```text
PRIN ─┬→ REQ ─┬→ OASTR ─┐
      │       └→ STKE ─┼→ OAPR ─→ OAAL ─┬→ OASEC (optional)
      └────────────────┘    (deps:      └→ OAGOV (optional)
                 PRIN+OAPR+REQ+STKE)        (deps: OAAL + OASEC)
post-build: arckit:health, arckit:traceability
```

`OASEC` and `OAGOV` are `optional_targets` (default off).

---

## 4. Axiom coverage matrix (C208 Ch. 9, 16 axioms)

Primary ownership is per the plugin README coverage table and command bodies; "secondary" = cited only in a template (per-sprint alignment block) or reference. Verified by full-text grep across `arckit-oaa/{commands,templates,references}`.

| # | Axiom | Primary owner (command) | Secondary citations | Artefact carrying it | Where it lands in TOGAF ADM | Coverage |
|---|---|---|---|---|---|---|
| 1 | Customer Experience Focus | — | `OAAL` template (Sprint 0) | `vision.yaml` outcome targets | Phase A | Incidental |
| 2 | Outside-In Thinking | — | `OAAL` template (Sprint 0) | `vision.yaml` (customer-needs scope) | Phase A | Incidental |
| 3 | Rapid Feedback Loops | `oaa-adm-lite` | `OAAL` template (Sprint 3) | `OAAL` document itself — sprints *are* the loop | All phases (P…H) — the engine of the whole convention | ✅ owned |
| 3↔ADM | | | | | | |
| 4 | Touchpoint Orchestration | — | none | — | Phases B/C (application/customer touchpoints) | ❌ gap |
| 5 | Value Stream Alignment | `oaa-adm-lite` | `agile-strategy` + templates | `business-architecture.yaml` value streams w/ SLAs | Phase B | ✅ owned (×2) |
| 6 | Autonomous Cross-Functional Teams | `oaa-adm-lite`, `product-architecture` | `agile-strategy` template | team composition table in `OAPR` | Phase G (org model) / cross-cutting | ✅ owned |
| 7 | Authority, Responsibility & Accountability Distribution | `agile-governance` | `OAAL` template (Sprint 4) | decision-authority matrix in `OAGOV` | Phase G | ✅ owned |
| 8 | Loosely-Coupled Systems | — | none | — | Phases C/D | ❌ gap |
| 9 | Modular Data Platform | `oaa-adm-lite` | `OAAL` template (Sprint 1) | `data-architecture.yaml` (domain-owned datasets) | Phase C | ✅ owned |
| 10 | Simple Common Operating Principles | — | `OAAL` template (Sprint 2) | `technology-architecture.yaml` (standard APIs) | Phase D | Incidental |
| 11 | Partitioning Over Layering | `oaa-adm-lite` | `quality-checklist` (OAAL traceability), `citation-instructions` | `OAAL` document; also the organising principle of the whole plugin | Phases B/C/D (market/capability/domain partitioning) | ✅ owned |
| 12 | Organization Mirroring Architecture (Inverse Conway) | `agile-strategy` | `OAAL` template; `oaa-reference` | operating-model section of `OASTR` | Phase A principles + Phase G | ✅ owned |
| 13 | Organizational Leveling (teams ≤10–12) | — | none | — | Phase G | ❌ gap |
| 14 | Bias for Change | `oaa-adm-lite` | `OAAL` template (Sprint 3); `citation-instructions` | living-artefact policy in `OAAL` | Phase H | ✅ owned |
| 15 | Project to Product Shift | `product-architecture` | `oaa-adm-lite` notes; `agile-strategy` + `product-architecture` templates | `OAPR` document (product as organising principle) | Phase E portfolio + Phase G | ✅ owned (×2) |
| 16 | Secure by Design (→ G216) | `agile-security` | `oaa-reference`, `citation-instructions` | `OASEC` document, `compliance-evidence.json`, per-sprint threat model | Phase D security + all phases (DevSecOps) | ✅ owned |

**Coverage summary:** 11 of 16 axioms are owned by at least one command; 3 (A1, A2, A10) appear only incidentally in the `OAAL` template; 3 (A4 Touchpoint Orchestration, A8 Loosely-Coupled Systems, A13 Organizational Leveling) are **not cited anywhere** in the OAA plugin. Note A4 and A13 have natural homes in `agile-strategy`/`product-architecture` (journey/touchpoint design, team sizing), and A8 in the Sprint 2 technology work — cheap to close if axiom coverage is a quality target.

Citation integrity is machine-enforced: `scripts/check_oaa_axioms.py` (run OK on 2026-08-24, 37 files checked) validates that every `Axiom N` citation uses a published 1–16 number and matches the published name, and keeps the 16-axiom table in `oaa-reference.md` in sync.

---

## 5. Verification findings (from "check the oaa plugin")

Checked against the C208 HTML package table of contents (authoritative chapter map: Ch. 3 Dual Transformation, Ch. 4 Architecture Development, Ch. 5 Intentional Architecture, Ch. 6 Continuous Refactoring, Ch. 7 Agile Transformation, Ch. 8 Agile Governance, Ch. 9 Axioms, Ch. 10 Building Blocks Overview, Ch. 11 Agile Strategy, Ch. 12 Agile Organization, Ch. 13 Experience Design, Ch. 14 Product Architecture, Ch. 15 Journey Mapping, Ch. 16 Lean Value Stream Mapping, Ch. 17 Operations Architecture, Ch. 18 Data Information & AI, Ch. 19 Event Storming, Ch. 20 DDD Strategic Patterns, Ch. 21 Software Architecture, Ch. 22 Software Defined Infrastructure).

| # | Severity | Finding | Evidence |
|---|---|---|---|
| F1 | P1 | **Stale C208 chapter citations in `references/quality-checklist.md`.** The Unreleased axiom-correction pass fixed commands/templates/references but left the checklist: OAPR "Chapter 12 (Product Architecture)" → should be **Ch. 14** (Ch. 12 is Agile Organization); OASTR "Chapter 10 (Strategy)" → **Ch. 11** (Ch. 10 is Building Blocks Overview); OASEC "Chapter 17 (Security)" → C208 has **no security building-block chapter** — it is Ch. 4.6 + Axiom 16 + G216 (Ch. 17 is Operations Architecture); OAGOV "Chapter 18 (Governance)" → **Ch. 8** (Ch. 18 is Data, Information & AI). The CI guard `check_oaa_axioms.py` checks axiom numbers/names only, not chapter numbers, so these survive. | `plugins/arckit-oaa/references/quality-checklist.md` lines 52, 64, 78, 92 vs `o-aa/html/Part1.html`/`Part2.html` TOC |
| F2 | P1 | **Declared shared schemas do not exist.** OAA commands reference `schemas/vision.json`, `implementation-strategy.json`, `product-architecture.json`, `strategy-canvas.json`, `security-backlog.json`, `compliance-evidence.json`, `governance-cadence.json`, `threat-model.yaml`, `change-request.yaml` and instruct validation via `python validate-architecture.py … --phase …`. None of these files exist anywhere in the repo; the core plugin's `schemas/` contains only handoff schemas and scoring rubrics. Schema-validation is therefore aspirational — the quality gate that would make OAA "executable" is missing. | `find` across repo; `plugins/arckit-claude/schemas/` contents; `oaa-adm-lite.md` §5/Next Steps |
| F3 | P2 | **Recipe description drift in README.** README says `oaa-full` = "6 phases: strategy → product → ADM Lite → security → governance + optional maturity"; the recipe actually has 8 targets (PRIN/REQ/STKE + OASTR/OAPR/OAAL + optional OASEC/OAGOV) and post-build hooks `health` + `traceability` — there is no "maturity" target. | `plugins/arckit-oaa/README.md` vs `recipes/oaa-full.yaml` |
| F4 | P2 | **Namespace drift between canonical and bundled copies.** `plugins/arckit-oaa` cross-references bare `/arckit:adm-preliminary` etc.; the bundled mirror `plugins/arckit-claude/plugins/oaa` uses `/arckit-togaf-adm:…` / `/arckit-oaa:…`. Correct only if the target surface's plugin set matches; the converter doesn't currently normalise this, and a command run on a surface where the overlay commands live in the core namespace would emit non-resolvable handoffs. | `diff plugins/arckit-claude/plugins/oaa/commands/oaa-adm-lite.md plugins/arckit-oaa/commands/oaa-adm-lite.md` |
| F5 | P3 | **No OAA usage guides.** `docs/guides/` holds 216 per-command guides for core + TOGAF commands but none for the 5 OAA commands, even though all 5 ship on the Paperclip extension. | `docs/guides/` listing |
| F6 | P3 | **Axiom coverage gaps (A4, A8, A13).** See §4 matrix — touchpoint orchestration, loosely-coupled systems, and organizational leveling have no owning command. Deliberate scoping is fine, but the gap should be declared in `oaa-reference.md` rather than left implicit. | grep matrix §4 |
| — | OK | Axiom number/name integrity (16/16, 37 files), doc-type registry ↔ pages allow-list parity, Paperclip command parity (5/5 in `src/data/commands.json`), generated fixture `test-oaa-dummy/` (REQ/STKE/OASTR/OAPR/OAAL all present and schema-shaped) | `check_oaa_axioms.py` run 2026-08-24: OK |

---

## 6. Recommendations (EA lead, in priority order)

1. **Fix F1 chapter citations** in `quality-checklist.md` (4 lines), then extend `check_oaa_axioms.py` to also assert C208 chapter-number ↔ chapter-name pairs so this class of drift is caught in CI.
2. **Close F2 either direction:** either ship the 9 shared schemas + a real `validate-architecture.py` (turns the OAA "quality gate" from prose into an executable gate — aligns with the Executable Enterprise Architecture pillar), or downgrade the commands' language from "validate against schema X" to "structure per template Y". Recommend the former; `vision.json` and `implementation-strategy.json` are the two with cross-track (TOGAF ↔ OAA) value.
3. **Fix F3** (README recipe description) and **F4** (have the converter normalise cross-plugin namespaces per target surface, mirroring the doc-type dual-registry lesson).
4. **Declare or close F6:** add one-line axiom hooks for A4/A8/A13 in `agile-strategy` (A4, A13) and Sprint 2 (A8), or add an explicit "axioms intentionally out of scope" note to `oaa-reference.md`.
5. **Add 5 OAA guides** to `docs/guides/` (P3, content mostly derivable from the command prompts already written here).

---

*Prepared by: Enterprise Architecture Lead (EyWALink). Companion to `Obsidian Vault/o-aa/study-note.md` (C208 full-text study, §4.10 axioms, §5 building blocks).*
