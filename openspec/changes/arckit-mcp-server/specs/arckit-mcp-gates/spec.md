## Purpose
Defines the prerequisite gate checking logic shared with the plugin: MANDATORY gates hard-stop (missing artefact = stop), RECOMMENDED gates note-and-continue, OPTIONAL gates are silently skipped. The MCP gate logic mirrors the existing gate tiers in each command's prompt.

## ADDED Requirements

### Requirement: MANDATORY Gates Hard-Stop
When `arckit.check_gates` is called for a command that has MANDATORY prerequisite artefacts, any missing MANDATORY artefact SHALL be returned with `status: "open"` and the calling agent SHALL be instructed to resolve the gate before proceeding. The MCP SHALL NOT render a MANDATORY gate as `TBD` — the artefact must exist before the command's intake begins.

#### Scenario: Missing PRIN blocks OAA command
- **WHEN** an agent calls `arckit.check_gates` for `oaa-adm-lite` and `ARC-000-PRIN-v1.0.md` does not exist
- **THEN** the response lists `PRIN` as `status: "open"` with `tier: "MANDATORY"` and the `intake` response includes a `gate_blocked: true` flag

#### Scenario: PRIN present allows OAA command to proceed
- **WHEN** an agent calls `arckit.check_gates` for `oaa-adm-lite` and `ARC-000-PRIN-v1.0.md` exists
- **THEN** the response lists `PRIN` as `status: "closed"` and `gate_blocked: false`

### Requirement: MANDATORY Gates Are Consistent Across OAA, IT4IT, And TOGAF-ADM Overlays
The MANDATORY gate logic SHALL be identical across the three overlays where it applies:
- OAA: `PRIN` is MANDATORY for all five commands
- IT4IT: `PRIN` is MANDATORY for all six commands
- TOGAF-ADM: `ADMP` is MANDATORY for all six commands (the ADM Preliminary artefact is the prerequisite)

A missing MANDATORY gate SHALL produce the same stop behaviour in all three overlays: the agent is told to generate the prerequisite first, and no artefact is written.

#### Scenario: IT4IT stops on missing PRIN
- **WHEN** an agent calls `arckit.check_gates` for `it4it-value-network` and `ARC-000-PRIN-v1.0.md` does not exist
- **THEN** the response lists `PRIN` as `status: "open"`, `tier: "MANDATORY"`, and `gate_blocked: true`

#### Scenario: TOGAF-ADM stops on missing ADMP
- **WHEN** an agent calls `arckit.check_gates` for `adm-architecture-definition` and no `ARC-{P}-ADMP-v[N].md` exists
- **THEN** the response lists `ADMP` as `status: "open"`, `tier: "MANDATORY"`, and `gate_blocked: true`

### Requirement: RECOMMENDED And OPTIONAL Gates Are Non-Blocking
RECOMMENDED gates SHALL be noted in the response (the artefact is missing) but SHALL NOT block the command's intake. OPTIONAL gates SHALL be silently skipped — their absence SHALL NOT appear in the gate response.

#### Scenario: Missing RECOMMENDED artefact does not block
- **WHEN** an agent calls `arckit.check_gates` for `requirements` and no `ARC-{P}-SOBC-v[N].md` exists
- **THEN** the response lists `SOBC` as `status: "open"`, `tier: "RECOMMENDED"`, and `gate_blocked: false`

#### Scenario: Missing OPTIONAL artefact is not listed
- **WHEN** an agent calls `arckit.check_gates` for `requirements` and no `ARC-{P}-PLAN-v[N].md` exists
- **THEN** the response does NOT include `PLAN` in the gate list (OPTIONAL gates are omitted)
