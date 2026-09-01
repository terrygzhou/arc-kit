# Changelog

## [Unreleased]

- Diagram-emitting commands now load the Mermaid syntax references before reading
  their templates, so generated diagrams follow the reference syntax: `agent-design`
  (flowchart, C4), `agent-maturity` (gantt, quadrant chart), `agent-security`
  (flowchart, mindmap), `agent-governance` (flowchart), `agent-integration`
  (sequence diagram), `agent-inventory` (flowchart)

- `agent-architecture` post-build hooks now include `arckit:traceability`
  (requirements traceability matrix) alongside `arckit:health` and `arckit:pages`,
  matching the other overlay recipes

## 1.0.0 (2026-07-01)

- Initial release
- 6 agent architecture commands: agent-inventory, agent-design, agent-governance, agent-integration, agent-security, agent-maturity
- 6 new doc type codes: AAGI, AAGR, AAOV, AAIN, AASE, AAMT
- Build recipe: agent-architecture
