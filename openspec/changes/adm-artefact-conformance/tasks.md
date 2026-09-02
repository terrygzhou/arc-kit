# Tasks — adm-artefact-conformance

## 1. TDD guard (RED)
- [x] 1.1 Add `tests/plugin/test_adm_doc_control_conformance.py`: 14-field DC tables in every ADM template that has a Document Control section (both trees); no `x-axis__`/`y-axis__` and no comma-form quadrantChart points (ADM + agent-architecture trees); canonical revision-history header; checklist check #6 names the canonical six columns
- [x] 1.2 Run the new test — RED on the 14-field, axis-typo, and checklist-column assertions; GREEN expected only for the revision-history header guard

## 2. ADM template Document Control expansion (GREEN)
- [x] 2.1 Expand the 7-field DC tables to the 14 canonical fields in `adm-preliminary`, `application-inventory`, `architecture-board`, `capability-map`, `data-architecture`, `gap-analysis` (keep `Severity Weighting`), `tech-architecture` templates — in BOTH `plugins/arckit-claude/plugins/togaf/adm/templates/` and `plugins/arckit-togaf-adm/templates/`
- [x] 2.2 `architecture-change`: add `Version` + `Review Cycle` rows, rename `Review Date` → `Next Review Date` (both trees)
- [x] 2.3 `architecture-repository`: add `Document Type` / `Version` / `Last Modified`, rename `Standard ID` → `Document ID`, `Created` → `Created Date`, `Next Review` → `Next Review Date`, drop the duplicate Owner row (both trees)
- [x] 2.4 `rationalization` + `transition-architecture`: rename `Created` → `Created Date` for naming parity (both trees)
- [x] 2.5 Re-run the new test — GREEN

## 3. Template mermaid fixes
- [x] 3.1 Fix `x-axis__`/`y-axis__` → `x-axis`/`y-axis` in `capability-map`, `gap-analysis`, `application-inventory` (both togaf trees) and `agent-maturity-template.md` (claude + `arckit-agent-architecture` mirror)
- [x] 3.2 Capability-map: `"C1.1.1": 0.8, 0.3` / `"C2.1.1": 0.3, 0.8` → array form; application-inventory: correct the `%%` format comment; agent-maturity: `"Design", [0.3, 0.4]`-style points → `"Design": [0.3, 0.4]` (5 points)

## 4. Revision-history column standardisation
- [x] 4.1 Reword checklist common check #6 to `Version, Date, Author, Description, Reviewer, Approver` in all 31 tracked `quality-checklist.md` copies + `scripts/autoresearch/program.md`
- [x] 4.2 `python3 scripts/sync-shared-assets.py --check` (lockstep guard); grep asserts zero remaining old-column lines in tracked files

## 5. Project 001 remediation (gitignored test fixtures)
- [x] 5.1 `ARC-001-ADMP-v1.0.md`: 14-field Document Control (values mirror BPCM; `Last Modified` = 2026-09-02; `Next Review Date` from the former `Review Date` row), add `**Model**: Codex (OpenAI)` footer line, add remediation revision-history row
- [x] 5.2 `.arckit/intake/adm-preliminary.json`: `prefill_provenance` entries for Document Type, Last Modified, Review Cycle, Next Review Date, Distribution + audit entries for agent-derived §2.1/§2.2, §5, §7, §11; extend `conformance_remediation.recorded`
- [x] 5.3 `.arckit/intake/business-capability-map.json`: rename `document_control_provenance` → `prefill_provenance`; add `document_control.last_modified`, `sec6-principle-alignment`, `sec4-heatmap-coordinates` entries
- [x] 5.4 `README.md`: add the BPCM row to the artefact table; note both intake JSONs

## 6. Regenerate, test, validate
- [x] 6.1 `python3 scripts/converter.py` (regenerate `extensions/*`)
- [x] 6.2 `python3 -m pytest tests/plugin/test_adm_doc_control_conformance.py tests/plugin/test_adm_intake_ask_always.py tests/plugin/test_intake_interview.py tests/plugin/test_template_intake_questions.py tests/plugin/test_oaa_intake.py tests/codex/test_codex_extension.py -q`
- [x] 6.3 Structural re-check of the edited ADMP artefact (fence balance, table pipe-counts) + `python3 -c json.load` on both intake JSONs
- [x] 6.4 `npx markdownlint-cli2` over the changed files (run escalated: 0 issues expected; `!openspec/**` excluded by repo config)
- [x] 6.5 `openspec validate adm-artefact-conformance`
- [x] 6.6 `CHANGELOG.md` Unreleased entry; conventional commit staging: 20 ADM templates + 2 agent-maturity templates + 32 checklist/doc files + new pytest + `openspec/changes/adm-artefact-conformance/` + CHANGELOG (regenerated `extensions/*` and project-001 fixtures stay uncommitted)
