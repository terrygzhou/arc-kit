## Why

`template-driven-intake` established the generic mechanism — every artefact-producing command interviews against its effective template before rendering. What it left open is the OAA-specific posture. This change pins that posture, and it **decides OAA uses the same hard-gate model as TOGAF `togaf/adm`**: a missing MANDATORY prerequisite artefact stops the OAA command (prompting the user to generate the upstream artefact first) instead of rendering a template full of `TBD` scaffolding. That makes OAA as rigorous as ADM on its foundational precondition, while OAA's outcomes-over-outputs *tone guard* (no diagram/output mandates) stays in force.

## What Changes

New capability **`oaa-intake`** capturing the OAA-specific guarantees:

- **OAA intake hard-blocks on MANDATORY prerequisites, TOGAF-consistent.** Every one of the five OAA commands (`oaa-adm-lite`, `product-architecture`, `agile-governance`, `agile-security`, `agile-strategy`) SHALL declare a **MANDATORY** prerequisite tier grounded in the `000-global` `PRIN` (Architecture Principles) artefact — the same single foundational precondition `togaf/adm`'s `adm-preliminary` hard-stops on. A missing MANDATORY prerequisite artefact SHALL stop the command and prompt the user to generate it first; it is a hard dependency, **never** rendered as `TBD`. This is the deliberate OAA/ADM parity decision: both now hard-stop on missing `PRIN`.
- **The interview itself stays a soft gate.** Only *interview inputs* the user skips render as quoted `TBD` markers (generic `template-driven-intake` behaviour). The *hard gate* is on *prerequisite artefacts*, not on interview questions — exactly the TOGAF ADM split.
- **OAA tone guard (spec, not task note).** For `oaa` overlay commands the interview SHALL NOT introduce any diagram or output mandate. A prerequisite hard gate is a *dependency*, not a rendering demand, so it does not conflict with OAA's outcomes-over-outputs posture; the interview adds no diagram/output requirement. This lifts `intake-instructions.md` §8 to a testable requirement.
- **OAA sub-plugin copy parity.** The OAA sub-plugin's copy of the shared block at `plugins/arckit-claude/plugins/oaa/references/intake-instructions.md` SHALL remain byte-identical to the root shared block **and** retain §8. All five OAA command bodies SHALL carry the "Run the intake interview" step before their template-read step.
- **Per-command OAA interview inputs track each OAA template.** The reference input domains each OAA template surfaces (oaa-adm-lite Sprint-0 outcome dimensions; product-architecture mission/outcome/principles/team/backlog/roadmap; agile-governance roles/review/debt/health/compliance; agile-security four pillars + metrics; agile-strategy digital/agile/resilience/waves) are the reference set the interview covers; a fully-prefilled template still surfaces every value for confirmation/override (ask-always, answer-optional).
- **Sprint-0 prefill seeds the OAA intake store.** The OAA Sprint-0 outcome dimensions (jurisdiction, AI workload type, data classification, user count, latency, budget, timeline, infrastructure, stakeholders, success criteria, regulatory controls, risk profile, deployment topology) SHALL be prefillable into `.arckit/intake/` so a first OAA command after onboarding starts warm.
- **Standard-aligned interview coverage (TOGAF + OAA).** Each OAA interview SHALL derive questions from a canonical discovery-dimension checklist — D1 business vision & strategy, D2 business capabilities, D3 stakeholders & goals, D4 constraints & drivers, D5 current-state (As-Is) architecture, D6 technology landscape, D7 data & classification, D8 pain points / gaps / risks, D9 OAA outcome dimensions, D10 OAA axioms — in addition to the template's own sections. A prefilled dimension is surfaced for confirmation/override; an unresolvable dimension is asked (grouped, skippable; skip renders a TBD marker). This makes the interview standards-aligned even when a template section is thin, and adds no diagram/output mandate.

Non-goals: no change to the generic `template-driven-intake` mechanism; no new OAA command; no new OAA template fields (questions track the existing templates); no diagram/output mandates added by the interview (tone guard intact). Implementation: promote the `PRIN` prerequisite from RECOMMENDED to MANDATORY in the five OAA command bodies (both `plugins/arckit-oaa/` and `plugins/arckit-claude/plugins/oaa/`), with the TOGAF-style "If missing: STOP" instruction; other OAA prerequisites remain RECOMMENDED.

## Capabilities

### New Capabilities
- `oaa-intake`: OAA-specific intake guarantees — MANDATORY `PRIN` hard gate (TOGAF-consistent), tone guard, sub-plugin copy parity with §8, per-command input tracking, and Sprint-0 prefill seeding.

### Modified Capabilities
<!-- none — the generic mechanism lives in `template-driven-intake` (slash-commands / plugin-skills); this change is a refinement, not a base mechanism -->

## Impact

- Spec: new `openspec/specs/oaa-intake/spec.md` (5 ADDED requirements, each with WHEN/THEN scenarios).
- Implementation: edit the `PRIN` prerequisite in the five OAA command bodies (standalone `plugins/arckit-oaa/commands/*.md` and overlay `plugins/arckit-claude/plugins/oaa/commands/*.md`) from RECOMMENDED to MANDATORY with "If missing: STOP"; regenerate the seven `extensions/` targets; add OAA regression tests.
- Regression tests: `tests/plugin/test_oaa_intake.py` asserting: every OAA command declares a MANDATORY `PRIN` tier with a STOP instruction; no OAA command *silently* drops MANDATORY PRIN; the OAA sub-plugin copy is byte-identical to the root and retains §8; all five OAA command bodies carry the intake step.
- Runtime: a bulk `arckit-build` run of an OAA target without `PRIN` now fails/skips that target (TOGAF-consistent) rather than rendering with `TBD`.
- Philosophical trade-off: this adds one foundational precondition to a philosophy that is otherwise deliberately lightweight. It is scoped to the single global `PRIN` artefact, not per-artefact review gates, and adds no output mandates. See design.md.
- Dependency: assumes the generic `template-driven-intake` mechanism (shared block + per-command step + persistence + MANDATORY hard-dependency rule, §2/§6) is in place; archive `template-driven-intake` first, then `oaa-intake`.
