# Tasks — intake-authoritative-questions

## 1. Shared algorithm: authoritative question lists + ask-always/answer-optional
- [x] 1.1 In `plugins/arckit-claude/references/intake-instructions.md`: reframe the intro as **ask-always, answer-optional** (asking mandatory; each answer optional → `TBD`), preserving the soft-gate/never-blocks semantics
- [x] 1.2 Add the §2 **authoritative question lists** rule: a template's `## Intake Interview Questions` block is authoritative and MUST be asked (additive to template-derived inputs); OAA uses `intake-discovery-dimensions.md` as its floor
- [x] 1.3 Propagate byte-identically: core → 3 Claude overlays (`sync-shared-assets.py` for 15 community plugins) → `extensions/*` (`converter.py`); assert all 26 copies share one md5

## 2. TOGAF ADM command text parity (TDD)
- [x] 2.1 Add `tests/plugin/test_adm_intake_ask_always.py` asserting every intake TOGAF ADM command (both trees, floor ≥24) carries `ask-always` and `answer-optional` — run RED
- [x] 2.2 Reword the "Run the intake interview" step in the 12 TOGAF ADM commands (`plugins/arckit-togaf-adm/commands/` + `plugins/arckit-claude/plugins/togaf/adm/commands/` mirrors) to the `ask-always, answer-optional` framing — run GREEN

## 3. Regenerate, test, validate
- [x] 3.1 `python3 scripts/converter.py` (regenerate `extensions/*`)
- [x] 3.2 `python3 -m pytest tests/plugin/test_adm_intake_ask_always.py tests/plugin/test_intake_interview.py tests/plugin/test_template_intake_questions.py tests/plugin/test_oaa_intake.py tests/codex/test_codex_extension.py -q`
- [ ] 3.3 `npx markdownlint-cli2` over the changed files (network-gated in sandbox; run where available)
- [x] 3.4 `openspec validate intake-authoritative-questions`
- [ ] 3.5 Conventional commit: `feat: state ask-always/answer-optional in ADM commands and wire in template intake questions` — stage this OpenSpec change + the 24 ADM command files + the new test (+ regenerated `extensions/*` if tracked)
