# OAA Discovery-Dimension Checklist (D1–D10)

This checklist is the **OAA-scoped canonical discovery-dimension floor** for the intake
interview. It supplements — it does not replace — the shared block's §2 template-derived
questions in `intake-instructions.md`: every OAA command's interview covers the inputs its
effective template requests **plus** these canonical dimensions, so every OAA artefact is
grounded in the standard's core concerns even when a particular template section is thin
or absent.

## Canonical Dimensions

| # | Dimension | TOGAF source | OAA source |
| --- | --- | --- | --- |
| D1 | Business vision & strategy | ADM-P / Phase A | OAA strategic intent |
| D2 | Business capabilities | Phase B / capability map | OAA capability map |
| D3 | Stakeholders & goals | ADM-A / stakeholder management | OAA engagement |
| D4 | Constraints & drivers (jurisdiction, regulatory, budget, timeline) | ADM-A drivers / constraints | OAA constraints |
| D5 | Current-state (As-Is) architecture | Phase B / C / D "current" | OAA digital-dimension `current_state` |
| D6 | Technology landscape (current + target) | Phase C / D | OAA enabling technologies / infrastructure |
| D7 | Data architecture & classification | Phase C (data) | OAA data principles |
| D8 | Pain points, gaps & risks | Phase E gap analysis | OAA `capability_gaps` / resilience |
| D9 | OAA outcome dimensions (Value / Outcome / Experience / Adoption) | — | OAA outcome model |
| D10 | OAA axioms alignment | — | O-AA axioms |

## Prefill Rule (ask-always, answer-optional)

For each dimension, apply the shared block's §3 precedence (existing `projects/`
artefacts > per-command saved intake > onboarding `shared.json` > `user_config`):

- **Resolvable by prefill** — surface the value prefilled to the user for
  confirmation or override, one at a time; the user may confirm it or override it.
  A prefilled dimension is *never silenced* and never passes without being surfaced.
- **No source available** — ask the dimension as a grouped, skippable question.
  A skipped question renders as a `TBD` marker (shared block §6) and is reported
  under "Unresolved fields" (§7).

## Scope Guard

- This checklist is a **coverage floor in addition to** the template-derived
  questions; it adds **no** diagram or output mandate (shared block §8, OAA tone
  guard). It asks only for information the OAA template already asks for or that
  grounds it; it never requires the user to commit to a diagram or output the
  OAA template does not request.
- It is OAA-scoped. TOGAF/ADM overlay commands keep their own question derivation;
  this file is loaded only by OAA commands.
- The MANDATORY `PRIN` artefact hard gate is a dependency on an upstream artefact,
  not a dimension in this checklist and not an interview input.
