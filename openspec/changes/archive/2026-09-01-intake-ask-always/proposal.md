## Why

Today the template-driven intake interview is a *proportional* soft gate: it asks
only the inputs still unknown after prefilling, and a fully-prefilled template
asks zero questions. As a result the user is never shown — nor asked to confirm
or correct — the values the plugin already knew. For standards-driven overlays
(TOGAF ADM, OAA, agent architecture) this is a real gap: discovery dimensions
(business vision, current state, pain points, capabilities, technology) that a
command *should* put to the user for confirmation silently pass as prefilled
assumptions, so generated artefacts can encode unexamined input.

## What Changes

- Change the intake interview from "ask only the unknown" to **ask-always,
  answer-optional**: every derived input is put to the user for their input, one
  question at a time, prefilled where available so it can be confirmed or
  overridden; each question is optional/skippable, and a skipped question renders
  as a `TBD` marker.
- This applies uniformly to every artefact-producing command — core and each
  bundled overlay (`togaf/adm`, `oaa`, `agent/architecture`) — because they all
  share one interview algorithm (`references/intake-instructions.md`).
- The proportional-depth cap ("a fully-prefilled template asks zero questions")
  is removed; a fully-prefilled interview still surfaces every value for
  confirmation/override.
- Non-interactive paths (`arckit-build`) are unchanged: they still never
  interview and render `TBD` for unknowns.

## Capabilities

### Modified Capabilities
- `slash-commands`: the **Template-Driven Intake Interview Before Artefact
  Generation** requirement changes clause (4) from "ask the user only the inputs
  still unknown" to "put every derived input to the user (prefilled,
  confirmable/overridable, optional)"; the "interview depth SHALL be proportional
  to the gap / a fully-prefilled template SHALL NOT trigger a question" cap is
  replaced with "every derived input is surfaced for the user to confirm or
  override."

### New Capabilities
<!-- none -->

## Non-goals

- No change to *which* inputs are derived (still the effective template +
  MANDATORY prerequisite inputs + unresolvable Document Control fields).
- No change to prefill precedence (artefacts > per-command intake > shared
  intake > `user_config`).
- No hard gate: the interview still never blocks; a skipped question → `TBD`.
- No diagram/output mandate (the OAA tone guard, §8, stays intact).
- The `arckit-build` bulk path is unchanged (no interactive interview).

## Impact

- Spec: `openspec/specs/slash-commands/spec.md` (1 MODIFIED requirement).
- Shared file: `references/intake-instructions.md` §3/§4 reworded (root + all 7
  byte-identical copies).
- Command bodies: the "Run the intake interview" step bullet in every overlay
  command reworded to "put every intake question to the user … each optional /
  skippable" (OAA 5 + TOGAF ADM 12 + agent/architecture 6, plus their
  `arckit-claude` mirrors).
- Templates: the intake-interview intro in every overlay template reworded
  (OAA 5 + TOGAF ADM 12 + agent/architecture 6, plus mirrors). OAA and TOGAF ADM
  were already reworded in prior commits; this change extends the same policy to
  `agent/architecture` and the shared reference, and adds a regression test.
- New regression test `tests/plugin/test_intake_ask_always.py`.
