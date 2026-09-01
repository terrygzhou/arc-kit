## Context

The intake interview is implemented as LLM instructions, not code: every
artefact command defers to one shared block, `references/intake-instructions.md`.
A prior change (`2026-09-01-intake-ask-always`) moved the shared block to
ask-always/answer-optional, but (a) it never wired in the template's
`## Intake Interview Questions` block, and (b) it did not put the framing into the
TOGAF ADM *command text* (OAA commands already carry it).

## Goals / Non-Goals

**Goals:** guarantee the curated question block is always asked; make
ask-always/answer-optional explicit in every overlay command's text.

**Non-Goals:** restructure which inputs are derived; add hard blocking; change
prefill precedence or the bulk-build exemption.

## Decisions

- **Centralize the principle in the shared block, and state it in command text.**
  Editing the shared block alone is enough for *behavior* (every command defers
  to it); stating it in the ADM command text gives parity with OAA and makes the
  principle visible where a model reads the specific command. Both are done.
- **Template question block = authoritative, additive.** The block's questions
  are asked *in addition to* template-derived inputs, not instead of them — so a
  customised template still drives the derived set.
- **TDD the command-text change** with a focused test that asserts the
  `ask-always` / `answer-optional` tokens in every intake ADM command (both trees).

## Risks / Trade-offs

- Over-asking: authoritative + derived could double up questions. Mitigated by
  grouping and by the existing "skip → `TBD`" per-question escape hatch.
- 24 near-duplicate command files: a find/replace drift risk; the new test pins
  all 24 to the required tokens.
