## Why

The intake interview is now ask-always/answer-optional, but two things still let
the *asking* get skipped in practice:

1. **The template's own question block was not wired in.** Every overlay template
   (TOGAF ADM, OAA, agent/architecture) carries an authoritative
   `## Intake Interview Questions` section (e.g. capability-map's *"Which
   business capabilities exist today…?"*), but the shared algorithm
   (`references/intake-instructions.md` §2) only derives questions from
   "substantive section headings" — a meta block like the questions section is
   not one of those. So a faithful reading under-asks: it derives table-filling
   prompts and may lean on the ADMP scope instead of putting the curated
   capability question to the user.
2. **The principle was not visible in the command text.** The OAA commands state
   "ask-always, answer-optional" explicitly, but the 12 TOGAF ADM commands still
   read "each question is optional and may be skipped," which a model can read as
   "I may skip the interview."

## What Changes

- **Authoritative question lists (shared algorithm).** `intake-instructions.md`
  §2 gains an explicit rule: if the effective template carries an
  `## Intake Interview Questions` section, every question in that block is
  authoritative and MUST be put to the user (prefilled where available,
  skippable), *in addition to* the template-derived inputs. OAA commands use
  `intake-discovery-dimensions.md` (D1–D10) as their asked-always coverage floor.
- **Ask-always/answer-optional stated in the TOGAF ADM command text.** Each ADM
  command's "Run the intake interview" step now carries the
  `ask-always, answer-optional` framing (the asking is mandatory; each answer is
  optional → `TBD`), matching the OAA commands.

## Capabilities

### Modified Capabilities
- `slash-commands`: the **Template-Driven Intake Interview Before Artefact
  Generation** requirement gains an *authoritative question lists* clause — the
  template's `## Intake Interview Questions` block (or, for OAA, the
  discovery-dimension floor) is authoritative and MUST be asked alongside
  template-derived inputs; and it states the interview is **ask-always,
  answer-optional** (the asking is mandatory, each answer is optional).

### New Capabilities
<!-- none -->

## Non-goals

- No change to *which* template inputs are derived, or to prefill precedence.
- No hard gate: the interview still never blocks; a skipped answer → `TBD`.
- No diagram/output mandate (the OAA §8 tone guard stays intact).
- No change to the `arckit-build` bulk path (still no interactive interview).

## Impact

- Shared file: `plugins/arckit-claude/references/intake-instructions.md` §intro
  (ask-always/answer-optional reframe) + §2 (authoritative-question-lists rule);
  propagated to all byte-identical copies (core, 3 Claude overlays, 15 community
  plugins) and regenerated `extensions/*`.
- Command bodies: the "Run the intake interview" step in the 12 TOGAF ADM
  commands (source `plugins/arckit-togaf-adm/` + the `arckit-claude` mirror),
  plus regenerated extensions.
- Spec: `openspec/specs/slash-commands/spec.md` (1 MODIFIED requirement).
- New regression test `tests/plugin/test_adm_intake_ask_always.py`.
