# Design — template-driven-intake

## Context

See proposal.md for motivation. Verified current state:

- Templates contain **no machine-parseable input tokens**. `${...}` in templates appears only inside embedded IaC code blocks (CloudFormation `!Sub`, Terraform `${var.x}`); overlay templates contain none at all. Introspection is therefore an LLM-level behaviour — read the effective template's section headings, its Document Control partial markers, and the command's MANDATORY prerequisite list — not a parser.
- Command frontmatter already carries **MANDATORY / RECOMMENDED / OPTIONAL** prerequisite tiers (existing prose contract, mirrored in the `Command Execution Contract` spec requirement).
- State conventions exist: `projects/{NNN}-{slug}/.arckit/state.json` (used by `arckit-build`), custom-template precedence `.arckit/templates-custom/ > ${CLAUDE_PLUGIN_ROOT}/templates/`, and `user_config`-driven Document Control fields.
- Every artefact-producing command already reads its effective template as a numbered step (e.g. `stakeholders.md` step 2) — the intake step slots in directly before it.

## Goals / Non-Goals

- Goal: one consistent intake procedure available to ~90 command bodies without ~90 copies of prose; questions always track the *effective* template so template edits automatically change the interview.
- Non-Goal: no new input-placeholder syntax in templates (would be a template-format change and would require rewriting every template); no parser/binary; no change to `architecture-workflow` onboarding or its HARD-GATE; no hard blocking.

## Decisions

1. **Behavioural derivation, not token parsing.** Alternative: introduce `${intake.x}` placeholders in templates and a resolver. Rejected: 90+ templates would need retouching, custom overrides would need placeholder discipline, and the spec's "questions track the effective template" property survives either way — the behavioural version is strictly less invasive. The command body instructs: "before rendering, walk the effective template's sections and MANDATORY inputs; for each input you cannot prefill, interview."
2. **Shared instruction block, referenced from each command.** New file `plugins/arckit-claude/references/intake-instructions.md` (same pattern as `references/citation-instructions.md`, which commands already reference). Each artefact-producing command gains one numbered step: "Run the intake interview per `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md`" placed immediately before its template-read step. One source of truth; the 32K context cost is one line per command.
3. **Persistence at `projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json`.** Per project + per command, matching the `.arckit/` state convention. JSON (not markdown) so hand-edits are simple and a future parser can consume them; format: `{ "answers": { "<question>": "<answer>" }, "updated": "<ISO timestamp>" }`. Lives inside `.arckit/` so it inherits whatever gitignore treatment session state already gets.
4. **Prefill precedence: existing artefacts > per-command saved intake > onboarding shared intake > `user_config` > interview.** Artefacts win first because they are the most recent, deliberately-produced source of truth; a stale saved answer that contradicts a fresh artefact must lose. The onboarding shared file (`shared.json`) sits below per-command answers because triage is coarser-grained than a command's own interview.
5. **Proportionality cap.** The instruction block sets a soft budget: only inputs that are genuinely unfillable, one question at a time, each skippable; a fully-prefilled template asks zero questions. This keeps the interview an unblocking aid, not a gate — consistent with OAA's outcomes-over-outputs guard (intake never adds diagram/output demands; it only fills what the template already asks for).
6. **Bulk builds are exempt by design, not by accident.** `arckit-build` subagents run with interview disabled: saved intake only, else `TBD`. One added clause in `skills/arckit-build/SKILL.md`; the DAG/wave/state logic is untouched.
8. **Overlay sub-plugins ship their own copy of the shared block.** `citation-instructions.md` is already copied into every overlay sub-plugin's `references/`; `intake-instructions.md` initially was not. Because each overlay sub-plugin has its own runtime `${CLAUDE_PLUGIN_ROOT}`, a root-only copy made the interview unrunnable from `oaa`, `togaf/adm`, and `agent/architecture` (silently skipped). Fix: verbatim copies in each sub-plugin, guarded by a byte-identity test.

7. **Onboarding seeds, commands own.** `architecture-workflow` writes its completed triage answers to `.arckit/intake/shared.json` (merge, never clobber) and discloses it in the plan message. It gains no questions, drops none, and writes a state file — it still runs zero commands, so the HARD-GATE wording in `plugin-skills` needs no change. Per-command answers always outrank the shared seed when they conflict.

## Risks / Trade-offs

- [Question quality varies by model interpretation of the template] → the instruction block pins the derivation algorithm (sections → inputs → prefill check → ask) and requires every question to quote the template section it serves, making bad questions auditable in the summary.
- [Intake JSON drifts from a later-edited template] → the file is per command stem, not per template hash; a re-run re-derives and reconciles: answered questions persist, new sections ask fresh questions. Stale keys are harmless (unquoted answers simply don't map to any section).
- [Interview friction on repeat runs] → proportionality cap + persistence mean steady-state runs ask nothing; first run is the only cost.
- [~90 command edits create review noise] → the edit is one identical step line per file; mechanical, converter-regenerated, and lint-verified.

## Migration Plan

Additive: new references file + one step per command + one `arckit-build` clause. Rollback = revert the commit; existing `.arckit/intake/` files become inert leftovers, safe to delete.

## Open Questions

None.
