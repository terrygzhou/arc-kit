# Intake Interview Instructions

Every artefact-producing ArcKit command runs a template-driven intake interview
before it renders its artefact. The template is the single source of truth for
*what the artefact needs*; this file pins the algorithm so every command — core
and bundled overlay (`togaf/adm`, `oaa`, `agent/architecture`) — interviews
against the *effective* template rather than a hard-coded question list.

The interview is a **soft gate**. It collects input; it never blocks a command,
never adds diagram or output demands the template does not already ask for, and
asks zero questions when every input is already prefilled.

## When to run

Run this step immediately before the command's "Read the template" step, after
the target project is resolved. If the command is executing as a bulk `arckit-build`
target, do **not** interview (see [Bulk builds](#bulk-builds)).

## 1. Resolve the effective template

Determine the template the artefact will actually be rendered from:

1. If `.arckit/templates-custom/{name}-template.{ext}` exists in the project
   root, that is the effective template (the user's override wins).
2. Otherwise use the shipped default `${CLAUDE_PLUGIN_ROOT}/templates/{name}-template.{ext}`.

Derive interview questions from the **effective** template, never from the
default, so that a customised template changes the questions automatically.

## 2. Derive the required inputs

Walk the effective template and collect every input the artefact needs:

- **Section inputs** — each substantive section heading implies the content the
  user must supply to fill it (its entities, decisions, owners, rationale).
- **Document Control fields** — the metadata fields the template declares in its
  Document Control table / header that are *not* resolvable from `user_config`
  (fields `user_config` can answer are prefill-candidates, not questions).
- **MANDATORY prerequisite inputs** — the inputs the command's MANDATORY
  prerequisite tier declares must be present before generation.

Group related items so that one question can collect a coherent set (e.g. all
Document Control metadata) rather than one question per leaf.

## 3. Prefill, in precedence order

Before asking anything, resolve each derived input from the highest-precedence
source that provides it:

1. **Existing `projects/` artefacts** — values already present in artefacts in
   the target project (the most recent, deliberately-produced source of truth).
2. **This command's saved intake** — `projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json`.
3. **Onboarding shared intake** — `projects/{NNN}-{slug}/.arckit/intake/shared.json`
   (seeded by the `architecture-workflow` skill; coarser-grained than a command's
   own answers, so it sits below per-command answers).
4. **`user_config`** — organisation defaults.

A lower-precedence source never overrides a higher one; if sources conflict,
the higher-precedence value wins.

## 4. Ask only the remainder, one at a time

For each input still unknown after prefilling:

- Ask **one question at a time** in the user's language, and **quote the
  template section or Document Control field the question serves** so the
  question is auditable in the summary.
- Offer an explicit **skip** option on every question.
- A fully-prefilled template asks **zero** questions — interview depth is
  proportional to the actual gap. Never pad with questions the template does
  not need.

Do not re-ask an input already answered by a higher-precedence source.

## 5. Persist answers

Persist the collected answers for this command to
`projects/{NNN}-{slug}/.arckit/intake/{command-stem}.json` (create the path when
missing; merge without clobbering answers the user already set):

```json
{
  "answers": { "<question>": "<answer>" },
  "updated": "<ISO-8601 timestamp>"
}
```

- `{command-stem}` is the command's slug (e.g. `stakeholders`, `data-architecture`).
- The file is hand-editable JSON. Editing it changes the artefact on the next
  run. It is never rendered into an artefact itself.
- Do not persist the onboarding shared file from a command; that file is owned
  by the `architecture-workflow` skill.

## 6. Render skipped MANDATORY inputs as TBD markers

An input the user skipped that was MANDATORY renders in the artefact as an
explicit `TBD` marker with the interview question quoted next to it, e.g.:

```text
| Document Owner | TBD — "Who is the accountable owner of this artefact?" |
```

- Never silently omit a MANDATORY input and never merely warn about it.
- RECOMMENDED missing inputs are noted when absent; OPTIONAL inputs are skipped
  silently.

## 7. Report unresolved fields in the summary

The command's user-facing summary (not the full artefact) SHALL list every
unresolved field — each `TBD` marker and the question that produced it — under
an "Unresolved fields" heading, so the user sees exactly what to fill in.

## 8. OAA tone guard

For `oaa` overlay commands the interview must **not** introduce any diagram or
output mandate. It collects only the inputs the OAA template already asks for;
OAA is outcomes-over-outputs, and the interview adds no rendering demand.

## Bulk builds

The `arckit-build` harness runs artefact-producing commands as non-interactive
subagent targets. In that mode the intake interview is **disabled**: the subagent
uses saved `.arckit/intake/` answers where available and renders `TBD` for every
unknown. No interactive questions are asked during a build.
