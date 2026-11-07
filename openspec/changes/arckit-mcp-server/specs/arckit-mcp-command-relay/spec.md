## Purpose
Defines the progressive intake relay: each command tool returns the command's intake questions and instructions so the agent can run the LLM-driven generation in its own session, keeping the MCP as a guidance + state layer rather than an execution engine.

## ADDED Requirements

### Requirement: Command Tools Return Intake Questions And Instructions
Each per-command tool SHALL return a structured response containing:
- `intake`: an array of question objects, each with `id` (stable key), `question` (the prompt), `required` (boolean), and `hint` (optional context)
- `instructions`: a short string summarising what the command produces and where (file path)
- `gates`: the result of `arckit.check_gates` for this command + project, so the agent knows what to resolve before proceeding

The tool SHALL NOT execute the LLM generation itself. The agent (Hermes) takes the intake questions, runs the generation in its own session, and calls back to `arckit.persist_artifact` (or equivalent) to record the artefact.

#### Scenario: Agent runs a command via the MCP
- **WHEN** an agent calls `arckit_requirements` with `project_id: "001"`
- **THEN** the response contains `intake` (the intake questions), `instructions` (what to produce), and `gates` (gate status), and does NOT contain a generated requirements document

#### Scenario: Agent persists an artefact
- **WHEN** the agent calls `arckit.persist_artifact` with `project_id: "001"`, `doc_type: "REQ"`, and `content: "<markdown>"`
- **THEN** the server writes `ARC-001-REQ-v1.0.md` to the project directory (creating parent dirs if needed) and returns the file path

#### Scenario: Multi-instance type gets a sequence number
- **WHEN** the agent calls `arckit.persist_artifact` with `doc_type: "ADR"` and `project_id: "001"`
- **THEN** the server assigns the next available sequence number (e.g. `ARC-001-ADR-001-v1.0.md`) using the `MULTI_INSTANCE_TYPES` registry

#### Scenario: Non-multi-instance type does not get a sequence number
- **WHEN** the agent calls `arckit.persist_artifact` with `doc_type: "REQ"` and `project_id: "001"`
- **THEN** the server writes `ARC-001-REQ-v1.0.md` without a `-{NNN}` sequence segment
