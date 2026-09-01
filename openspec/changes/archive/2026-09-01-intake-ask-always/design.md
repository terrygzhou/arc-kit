# Design — intake-ask-always

## Context

`template-driven-intake` (archived 2026-09-01) established the generic
algorithm: one shared `references/intake-instructions.md`, one "Run the intake
interview" step per artefact-producing command, persistence at
`.arckit/intake/{command-stem}.json`, and a soft gate for interview inputs with a
`TBD` fallback. Its §4 pins the behaviour as *proportional*: "Ask only the
remainder, one at a time … a fully-prefilled template asks zero questions." This
change reverses that single decision.

The policy is already reworded in the OAA and TOGAF ADM templates/commands
(prior commits `feat: make OAA intake questions ask-always but optional` and
`feat: make TOGAF ADM intake questions ask-always but optional`). This change
generalizes it to the whole shared mechanism: the shared reference (§3/§4), the
remaining `agent/architecture` overlay, and a cross-plugin regression test.

## Goals / Non-Goals

- Goal: every derived intake input is surfaced to the user for their input (one
  at a time), prefilled where available for confirm/override; each question is
  optional/skippable → a skipped question renders `TBD`.
- Goal: apply it uniformly to core + every overlay through the shared reference,
  so a single source of truth governs every command.
- Non-goal: no hard gate; no change to *which* inputs are derived or to prefill
  precedence; no diagram/output mandate; the `arckit-build` bulk path is
  unchanged.

## Decisions

1. **Policy lives in the shared reference + the requirement, not per command.**
   Every command points at one shared `intake-instructions.md`, so rewording
   §3/§4 there — kept byte-identical across all 7 copies (root + 3 sub-plugin
   sources + 3 `arckit-claude` mirrors) — is the single source of truth. The
   command step-bullets and template intros restate the same policy for the
   model that reads them.
2. **"Ask-always" is bounded by "derived inputs."** We ask every *derived* input
   (effective-template sections + MANDATORY prerequisite inputs + unresolvable
   Document Control fields), never invented extras. The proportional cap is
   removed, but "never pad with questions the template does not need" stands —
   the template is still the ceiling.
3. **Prefill becomes "confirm/override," not "silent."** A prefilled value is
   presented and the user confirms or overrides; they may still skip → `TBD`.
   This is the only behavioural inversion.
4. **The requirement is MODIFIED, not a new capability.** Post-archive of
   `template-driven-intake` the requirement lives in the main
   `slash-commands` spec, so a MODIFIED delta on that requirement is the clean
   vehicle (no duplicate/competing requirement).
5. **Regression test asserts the wording across all three overlays + the shared
   reference**, so "ask only the unknown / fully-prefilled → zero questions"
   cannot silently return.

## Risks / Trade-offs

- [Longer interviews for fully-prefilled projects] → each question is a single
  confirm/override step; the value is that prefilled (possibly wrong)
  assumptions are now examined. The bulk `arckit-build` path is unaffected.
- [Inverts a shipped decision] → deliberate and tracked as a MODIFIED
  requirement; the shared reference + requirement are the single sources, so no
  forked behaviour.
- [Byte-identical shared-reference invariant] → edit the 4 source copies
  identically, regenerate the 3 `arckit-claude` mirrors via
  `scripts/sync-claude-plugin-layout.py`, and assert all 7 copies stay
  byte-identical (existing invariant, also asserted by the OAA test).
