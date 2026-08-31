# plugin-skills Delta — template-driven-intake

## ADDED Requirements

### Requirement: Onboarding Triage Answers MUST Seed The Project Intake Store
When the `architecture-workflow` skill completes its triage questions (sector, project type, current stage, primary goal, and any deep questions asked), it SHALL persist those answers to `projects/{NNN}-{slug}/.arckit/intake/shared.json` (creating the path when missing and merging without clobbering existing keys) and SHALL state in its plan output that the answers were saved so the recommended commands will prefill from them. Artefact-producing commands' intake interviews SHALL treat `shared.json` as a prefill source with lower precedence than existing `projects/` artefacts and that command's own saved answers. Persisting answers SHALL NOT count as running a command: the HARD-GATE (no `/arckit:*` execution during onboarding) remains fully in force.

#### Scenario: Triage answers seed the shared intake file
- **WHEN** the user completes the triage questions for a new project and `architecture-workflow` outputs its recommended command plan
- **THEN** the sector, project type, stage, and goal answers are written to `projects/{NNN}-{slug}/.arckit/intake/shared.json` and the plan message notes that the answers were saved

#### Scenario: Seeded answers prefill later commands
- **WHEN** a recommended command (e.g. `/arckit:principles`) runs its intake interview after onboarding and a template input matches a seeded answer (e.g. the sector or the compliance frameworks chosen in a deep question)
- **THEN** the input is prefilled from `shared.json` and not re-asked

#### Scenario: Precedence is preserved
- **WHEN** a later run of the same command has a saved per-command answer in `.arckit/intake/{command-stem}.json` that conflicts with `shared.json`
- **THEN** the per-command answer wins; when an existing `projects/` artefact states a value, it wins over both

#### Scenario: HARD-GATE unaffected by persistence
- **WHEN** `architecture-workflow` has persisted its triage answers
- **THEN** it still has executed no `/arckit:*` command and its output remains a recommended plan only — the user decides when and what to run
