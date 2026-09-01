# Tasks — oaa-intake

## 1. Promote the PRIN prerequisite to a MANDATORY hard gate
- [ ] 1.1 In each of the five OAA command bodies, move `PRIN` from the **RECOMMENDED** tier into a `**MANDATORY** (stop if missing — generate upstream artefact first)` tier with a TOGAF-style "If missing: STOP and ask user to run `/arckit:principles` first" line (wording matched to `togaf/adm`'s `adm-preliminary`)
  - `plugins/arckit-oaa/commands/`: `oaa-adm-lite.md`, `product-architecture.md`, `agile-governance.md`, `agile-security.md`, `agile-strategy.md`
  - `plugins/arckit-claude/plugins/oaa/commands/`: same five
- [ ] 1.2 Leave the other OAA prerequisites (`ADMP`, `OAPR`, `OASTR`, `OASEC`, `BPCM`, `TRANS`) in RECOMMENDED (note-if-missing, non-blocking)
- [ ] 1.3 Confirm doc-type IDs still match the command doc IDs (`OAAL`, `OAPR`, `OAGOV`, `OASEC`, `OASTR`)

## 2. OAA tone guard (§8) as a testable requirement
- [ ] 2.1 Assert §8 ("OAA tone guard") is present in the generic shared block `plugins/arckit-claude/references/intake-instructions.md`
- [ ] 2.2 Add a check that no OAA command body adds a diagram/output mandate beyond its own template's requested sections (the MANDATORY gate is a dependency, not an output demand)

## 3. OAA sub-plugin copy parity + MANDATORY gate presence
- [ ] 3.1 Assert `plugins/arckit-claude/plugins/oaa/references/intake-instructions.md` is byte-identical to the root `references/intake-instructions.md`
- [ ] 3.2 Assert §8 is present in **both** the root and the OAA sub-plugin copy (a drift that drops §8 must fail, not just "files differ")
- [ ] 3.3 Assert all five OAA command bodies (both plugin trees) contain the intake step immediately before "Read the template" AND a `**MANDATORY**` `PRIN` tier with an "If missing: STOP" instruction
- [ ] 3.4 Assert no OAA command body *silently* drops the MANDATORY `PRIN` gate

## 4. Per-command OAA input reference sets
- [ ] 4.1 Encode the five reference input domains (oaa-adm-lite Sprint-0 dims; product-architecture; agile-governance; agile-security four pillars + metrics; agile-strategy) as the assertion set for the shipped default OAA templates
- [ ] 4.2 Assert a fully-prefilled OAA template triggers zero interview questions (proportionality cap holds for OAA)

## 5. Sprint-0 prefill seeding
- [ ] 5.1 Assert the Sprint-0 outcome dimensions are accepted prefill keys in `.arckit/intake/shared.json` / per-command intake with generic precedence (artefacts > per-command > shared > `user_config`)

## 6. Standards-coverage floor (TOGAF + OAA discovery-dimension checklist)
- [ ] 7.1 Ship the canonical D1–D10 discovery-dimension checklist as an OAA-scoped reference (e.g. `plugins/arckit-oaa/references/intake-discovery-dimensions.md` and its `plugins/arckit-claude/plugins/oaa/references/` copy) so the shared block stays byte-identical to the root (requirement 3) — the OAA intake step SHALL load it after the shared block
- [ ] 7.2 Add a regression test asserting the checklist file exists in both OAA trees, carries all ten dimensions (D1 vision/strategy, D2 capabilities, D3 stakeholders, D4 constraints/drivers, D5 current-state, D6 technology, D7 data, D8 pain points/gaps/risks, D9 outcome dimensions, D10 axioms), and states the prefill-silence rule (resolvable dimension → not asked; unresolvable → grouped, skippable)
- [ ] 7.3 Confirm the checklist adds no diagram/output mandate (tone guard) and cross-reference the generic `intake-instructions.md` §2 derivation

## 7. Regenerate, test, validate, close out
- [ ] 7.1 `.venv/bin/python scripts/converter.py` (regenerates all seven `extensions/` targets so the OAA hard gate is present in generated overlays)
- [ ] 7.2 `.venv/bin/python -m pytest tests/plugin/test_oaa_intake.py`
- [ ] 7.3 `pytest tests/codex/test_codex_extension.py`
- [ ] 7.4 `npx markdownlint-cli2 "openspec/changes/oaa-intake/**/*.md"`
- [ ] 7.5 `openspec validate oaa-intake`
- [ ] 7.6 Confirm archive ordering: archive `template-driven-intake` first, then `oaa-intake`
- [ ] 7.7 Conventional commit: `feat: make OAA intake a MANDATORY PRIN hard gate (TOGAF-consistent)`
