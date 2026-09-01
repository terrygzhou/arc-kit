# Design — oaa-intake

## Context

`template-driven-intake` (still an in-flight OpenSpec change) provides the generic mechanism: one shared `references/intake-instructions.md`, one "Run the intake interview" step per artefact-producing command, persistence at `.arckit/intake/{command-stem}.json`, a soft gate for *interview inputs* with `TBD` fallback, and — critically for this change — a **MANDATORY prerequisite-artefact hard-dependency rule** (§2 / §6: a MANDATORY upstream artefact that does not exist is a hard dependency, never rendered as `TBD`; the command stops and prompts the user to generate it first).

Verified current state (this repo):

- `plugins/arckit-oaa/commands/` and `plugins/arckit-claude/plugins/oaa/commands/` each hold the same **5** OAA commands: `oaa-adm-lite`, `product-architecture`, `agile-governance`, `agile-security`, `agile-strategy`.
- Today every one declares `PRIN` as **RECOMMENDED** with "If missing: warn user to run `/arckit:principles`" — no `**MANDATORY**` tier, no STOP.
- TOGAF parity reference: `plugins/arckit-claude/plugins/togaf/adm/commands/adm-preliminary.md` declares `**MANDATORY** (stop if missing — generate upstream artefact first)` for `PRIN` with "If missing: STOP and ask user to run `/arckit:principles` first."
- Doc-type IDs: `oaa-adm-lite`→`ARC-{P}-OAAL`, `product-architecture`→`OAPR`, `agile-governance`→`OAGOV`, `agile-security`→`OASEC`, `agile-strategy`→`OASTR`.
- Both OAA intake instruction copies carry §8 (OAA tone guard).

This change decides OAA adopts the **TOGAF hard-gate model** on its foundational precondition.

## Goals / Non-Goals

- Goal: OAA hard-stops on a missing MANDATORY prerequisite artefact (`PRIN`), exactly as `togaf/adm` does — parity of rigour.
- Goal: keep OAA's outcomes-over-outputs tone guard (no diagram/output mandate from the interview) intact; the hard gate is a *dependency*, not a rendering demand.
- Goal: keep the split TOGAF already uses — hard gate on prerequisite *artefacts*, soft gate (skippable → `TBD`) on interview *inputs*.
- Non-goal: do not make the *interview questions* non-skippable (that would contradict `template-driven-intake`'s soft gate); do not add per-artefact review gates; do not add diagram/output mandates.

## Decisions

1. **New capability, not a modification.** OAA intake is a refinement of the generic mechanism. A dedicated `oaa-intake` capability keeps the OAA decision separate from `template-driven-intake`'s in-flight MODIFIED "Command Execution Contract" and archives cleanly on top of it.
2. **Hard gate = MANDATORY `PRIN`, mirroring TOGAF `adm-preliminary`.** Rather than invent a bespoke OAA gate, adopt the exact precondition TOGAF ADM already hard-stops on: the global `PRIN` (Architecture Principles). This is the single shared foundational artefact all five OAA commands already list (as RECOMMENDED) and that the `oaa-full` recipe roots every target in. Promoting it to MANDATORY makes OAA and ADM behave identically at the one point they matter most — "no architecture work without established principles." Scoped to `PRIN` only; the other OAA prerequisites (ADMP, OAPR, OASTR, OASEC, BPCM, TRANS) stay RECOMMENDED to avoid re-imposing the heavy gate-ladder OAA is designed to avoid.
3. **Artifacts hard-stop; inputs stay skippable.** The MANDATORY `PRIN` artefact is a hard dependency (STOP, never `TBD`) per the generic §2/§6 rule. Interview *inputs* (Sprint-0 dimensions, document control fields) remain skippable soft-gate questions that render as quoted `TBD`. This preserves `template-driven-intake`'s behaviour and matches TOGAF's own split.
4. **Tone guard lifted to a requirement, and confirmed compatible.** §8 already says OAA interviews add no diagram/output mandate. A prerequisite-artefact hard gate is not a diagram demand, so §8 and the hard gate coexist; the spec states both and adds a scenario proving no conflict.
5. **Copy parity guarded specifically for §8.** The OAA sub-plugin copy of the shared block must stay byte-identical to the root and retain §8; a "fix" that rewrites the OAA copy to drop §8 is a spec violation, not just a byte diff.
6. **Per-command input sets are reference sets, not fixed question lists.** The spec names the expected input *domains* each OAA template surfaces; the interview still derives from the *effective* template at runtime (a custom template changes the questions), and a test asserts the shipped defaults still surface the named domains.
7. **Sprint-0 prefill is a seeding guarantee, not a new question source.** The Sprint-0 outcome dimensions are valid prefill keys in `.arckit/intake/shared.json` / per-command intake; they make the first OAA command after onboarding start warm, under the generic precedence.
8. **A standards-coverage floor, not a fixed question list.** The interview derives questions from the *effective template PLUS* a canonical TOGAF/OAA discovery-dimension checklist (D1 vision/strategy, D2 capabilities, D3 stakeholders, D4 constraints/drivers, D5 current-state, D6 technology, D7 data, D8 pain points/gaps/risks, D9 outcome dimensions, D10 axioms). Prefill still applies (a dimension resolvable from artefacts / intake / user_config / shared.json is silent); only unresolvable dimensions are asked, grouped and skippable. This guarantees every OAA artefact is grounded in the standard's core concerns (e.g. `/arckit:product-architecture` asks current-state and pain points even though its template lacks those sections) without adding any diagram/output demand (tone guard intact). The checklist is OAA-scoped and cross-references the generic algorithm's §2 derivation.

## Risks / Trade-offs

- [Hard gate against OAA's lightweight ethos] → OAA's "Do NOT use when" already excludes heavy multi-gate enterprise programmes; this adds exactly *one* global precondition (`PRIN`), not a per-artefact gate-ladder, and adds no output mandates. It aligns OAA with ADM rather than diverging from it.
- [Bulk `arckit-build` of OAA targets without `PRIN` now fails/skips instead of rendering `TBD`] → this is the intended TOGAF-consistent behaviour; the build surfaces the missing foundation instead of silently producing scaffolded OAA artefacts. Documented in Impact.
- [Reference input sets drift from later OAA template edits] → sets are asserted against shipped defaults only; the runtime interview still tracks the effective template.
- [Byte-identity test can mask a §8 regression if §8 is dropped from the root too] → the OAA test asserts §8 is present in *both* the root and the OAA copy.
- [Ordering with unarchived `template-driven-intake`] → `oaa-intake` depends on its MANDATORY hard-dependency rule (§2/§6); archive `template-driven-intake` first, then `oaa-intake`.

## Migration Plan

Edit the five OAA command bodies (both plugin trees): move `PRIN` into a `**MANDATORY** (stop if missing — generate upstream artefact first)` tier with a TOGAF-style "If missing: STOP and ask user to run `/arckit:principles` first" line; leave other prereqs RECOMMENDED. Add the `oaa-intake` capability spec + `tests/plugin/test_oaa_intake.py`. Regenerate the seven `extensions/` targets; lint. Rollback = revert the command-body edits and delete the capability spec + test; the generic mechanism is untouched.

## Open Questions

None.
