# Tasks — oaa-intake

## 1. Promote the PRIN prerequisite to a MANDATORY hard gate
- [x] 1.1 In each of the five OAA command bodies, move `PRIN` from the **RECOMMENDED** tier into a `**MANDATORY** (stop if missing — generate upstream artefact first)` tier with a TOGAF-style "If missing: STOP and ask user to run `/arckit:principles` first" line (wording matched to `togaf/adm`'s `adm-preliminary`)
  - `plugins/arckit-oaa/commands/`: `oaa-adm-lite.md`, `product-architecture.md`, `agile-governance.md`, `agile-security.md`, `agile-strategy.md`
  - `plugins/arckit-claude/plugins/oaa/commands/`: same five
- [x] 1.2 Leave the other OAA prerequisites (`ADMP`, `OAPR`, `OASTR`, `OASEC`, `BPCM`, `TRANS`) in RECOMMENDED (note-if-missing, non-blocking)
- [x] 1.3 Confirm doc-type IDs still match the command doc IDs (`OAAL`, `OAPR`, `OAGOV`, `OASEC`, `OASTR`)

## 2. OAA tone guard (§8) as a testable requirement
- [x] 2.1 Assert §8 ("OAA tone guard") is present in the generic shared block `plugins/arckit-claude/references/intake-instructions.md`
- [x] 2.2 Add a check that no OAA command body adds a diagram/output mandate beyond its own template's requested sections (the MANDATORY gate is a dependency, not an output demand)

## 3. OAA sub-plugin copy parity + MANDATORY gate presence
- [x] 3.1 Assert `plugins/arckit-claude/plugins/oaa/references/intake-instructions.md` is byte-identical to the root `references/intake-instructions.md`
- [x] 3.2 Assert §8 is present in **both** the root and the OAA sub-plugin copy (a drift that drops §8 must fail, not just "files differ")
- [x] 3.3 Assert all five OAA command bodies (both plugin trees) contain the intake step immediately before "Read the template" AND a `**MANDATORY**` `PRIN` tier with an "If missing: STOP" instruction
- [x] 3.4 Assert no OAA command body *silently* drops the MANDATORY `PRIN` gate

## 4. Per-command OAA input reference sets
- [x] 4.1 Encode the five reference input domains (oaa-adm-lite Sprint-0 dims; product-architecture; agile-governance; agile-security four pillars + metrics; agile-strategy) as the assertion set for the shipped default OAA templates
- [x] 4.2 Assert a fully-prefilled OAA template still surfaces every prefilled value for confirmation/override (ask-always, answer-optional; no value passes silently)

## 5. Sprint-0 prefill seeding
- [x] 5.1 Assert the Sprint-0 outcome dimensions are accepted prefill keys in `.arckit/intake/shared.json` / per-command intake with generic precedence (artefacts > per-command > shared > `user_config`)

## 6. Standards-coverage floor (TOGAF + OAA discovery-dimension checklist)
- [x] 7.1 Ship the canonical D1–D10 discovery-dimension checklist as an OAA-scoped reference (e.g. `plugins/arckit-oaa/references/intake-discovery-dimensions.md` and its `plugins/arckit-claude/plugins/oaa/references/` copy) so the shared block stays byte-identical to the root (requirement 3) — the OAA intake step SHALL load it after the shared block
- [x] 7.2 Add a regression test asserting the checklist file exists in both OAA trees, carries all ten dimensions (D1 vision/strategy, D2 capabilities, D3 stakeholders, D4 constraints/drivers, D5 current-state, D6 technology, D7 data, D8 pain points/gaps/risks, D9 outcome dimensions, D10 axioms), and states the prefill-silence rule (resolvable dimension → not asked; unresolvable → grouped, skippable)
- [x] 7.3 Confirm the checklist adds no diagram/output mandate (tone guard) and cross-reference the generic `intake-instructions.md` §2 derivation

## 7. Regenerate, test, validate, close out
- [x] 7.1 `.venv/bin/python scripts/converter.py` (regenerates all seven `extensions/` targets so the OAA hard gate is present in generated overlays)
- [x] 7.2 `.venv/bin/python -m pytest tests/plugin/test_oaa_intake.py`
- [x] 7.3 `pytest tests/codex/test_codex_extension.py`
- [x] 7.4 `npx markdownlint-cli2 "openspec/changes/oaa-intake/**/*.md"`
- [x] 7.5 `openspec validate oaa-intake`
- [x] 7.6 Confirm archive ordering: archive `template-driven-intake` first, then `oaa-intake`
- [x] 7.7 Conventional commit: `feat: make OAA intake a MANDATORY PRIN hard gate (TOGAF-consistent)`
