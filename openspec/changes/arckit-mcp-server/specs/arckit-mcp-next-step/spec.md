## Purpose
Defines the handoffs-graph walker: given the set of completed commands for a project, `arckit.next_step` returns the next recommended command so an agent can follow the governance workflow without memorising the handoffs.

## ADDED Requirements

### Requirement: next_step Returns The Next Command From The Handoffs Graph
The MCP server SHALL maintain the handoffs graph derived from the `handoffs:` frontmatter in each command's prompt. When `arckit.next_step` is called with a project ID and a list of completed command names, the server SHALL return the next command in the graph that has not yet been completed, along with a one-line reason.

#### Scenario: Requirements completed, data-model is next
- **WHEN** an agent calls `arckit.next_step` with `project_id: "001"` and `completed: ["requirements"]`
- **THEN** the response includes `next: "data-model"` and `reason: "DR-xxx data requirements were generated"` (or similar, derived from the handoffs condition)

#### Scenario: All core workflow commands completed
- **WHEN** an agent calls `arckit.next_step` with a `completed` list covering every reachable handoff
- **THEN** the response returns `next: null` and `reason: "All reachable handoffs completed"`

### Requirement: next_step Respects Command Conditions
Each handoff edge in the graph may carry a `condition` (e.g. `"DR-xxx data requirements were generated"`). The server SHALL only recommend a handoff whose condition is satisfied by the project state. If the condition cannot be evaluated (e.g. no artefact metadata), the handoff SHALL be omitted from the result, not assumed to be satisfied.

#### Scenario: Condition not met, handoff omitted
- **WHEN** an agent calls `arckit.next_step` with `completed: ["requirements"]` but no `DR-xxx` requirements were generated
- **THEN** the response does NOT include `data-model` as the next step

#### Scenario: Condition met, handoff included
- **WHEN** an agent calls `arckit.next_step` with `completed: ["requirements"]` and `DR-xxx` requirements were generated
- **THEN** the response includes `data-model` as the next step
