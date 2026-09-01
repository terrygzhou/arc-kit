# Tasks — intake-ask-always

## 1. Reword the shared interview algorithm (§3/§4) to ask-always/optional
- [x] 1.1 In `references/intake-instructions.md`: change the §3/§4 behaviour from "ask only the remainder / a fully-prefilled template asks zero questions" to "put every derived input to the user one at a time, prefilled where available so it can be confirmed or overridden; each question is optional and may be skipped → skipped renders a `TBD` marker"
  - Edit the 4 source copies identically:
    - `plugins/arckit-claude/references/intake-instructions.md` (root)
    - `plugins/arckit-oaa/references/intake-instructions.md`
    - `plugins/arckit-togaf-adm/references/intake-instructions.md`
    - `plugins/arckit-agent-architecture/references/intake-instructions.md`
- [x] 1.2 Regenerate the 3 `arckit-claude` mirror copies via `python3 scripts/sync-claude-plugin-layout.py`
- [x] 1.3 Assert all 7 copies are byte-identical (existing invariant; keep the OAA §8 tone guard intact in every copy)

## 2. Extend the ask-always/optional wording to the agent/architecture overlay
(OAA 5 and TOGAF ADM 12 templates + commands already carry the wording from prior commits.)
- [x] 2.1 In `plugins/arckit-agent-architecture/templates/*-template.md` (6 templates): reword the intake-interview intro from "are **not** asked" to the ask-always/optional wording
- [x] 2.2 In `plugins/arckit-agent-architecture/commands/*.md` (6 commands): reword the "Run the intake interview" step bullet from "ask only what remains unknown" to "put every intake question to the user one at a time (each optional/skippable; skipped → `TBD`)"
- [x] 2.3 Regenerate the `plugins/arckit-claude/plugins/agent/architecture/` mirrors via the sync script

## 3. Add a cross-plugin regression test
- [x] 3.1 New `tests/plugin/test_intake_ask_always.py` asserting:
  - the shared `intake-instructions.md` no longer contains "ask only what remains unknown" / "asks zero questions when every input is already prefilled" and DOES contain the ask-always/optional wording
  - every OAA / TOGAF ADM / agent-architecture template + command (source + `arckit-claude` mirror) uses the ask-always/optional wording (no stale "are **not** asked" / "ask only what remains unknown" phrasing remains in any of the three overlays)
  - all 7 `intake-instructions.md` copies are byte-identical

## 4. Regenerate, test, validate, close out
- [x] 4.1 `python3 scripts/sync-claude-plugin-layout.py`
- [x] 4.2 `python3 -m pytest tests/plugin tests/codex -q`
- [x] 4.3 `npx -y markdownlint-cli2` over the changed templates/commands/references (source + mirrors)
- [x] 4.4 `openspec validate intake-ask-always`
- [x] 4.5 Conventional commit: `feat: make intake interview ask-always but optional (all overlays)` — stage the OpenSpec change + the shared reference (7 copies) + agent-architecture templates/commands (+ mirrors) + the new test
