---
description: Discovery — current-state baseline across strategy, capabilities, applications, data, and technology
argument-hint: "<project ID or name, e.g. '001', 'discovery scope'>"
effort: high
handoffs:
  - command: gap-analysis
    description: Score current vs target gaps from the discovery baseline
  - command: application-rationalization
    description: Consolidate, retire, or replace applications from the current-state inventory
---

# Discovery: Current State Assessment

Capture the existing enterprise state — business strategy, capabilities, operations,
applications, data systems, and technology platforms — to establish a baseline for gap
analysis and rationalization.

## Inputs

- `PRIN` — Architectural principles that constrain discovery
- `{DISC_SCOPE}` — Scope of systems to inventory (e.g., "enterprise applications",
  "cloud infrastructure", "all enterprise systems")

## Output

`DISC.md` — Current state inventory covering:

1. **Business Context** — Strategy, vision, key initiatives, organizational structure
2. **Capability Assessment** — Current business capabilities, maturity levels, gaps vs strategy
3. **Application Landscape** — Existing applications, ownership, lifecycle status
4. **Data Inventory** — Databases, data flows, data ownership
5. **Technology Stack** — Infrastructure, platforms, hosting environments
6. **Known Constraints** — Legacy dependencies, compliance requirements, budget limits

## Process

1. **Run the intake interview**: Run the intake interview per `${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md` — derive required inputs from the structure below (the effective template) and MANDATORY prerequisites, prefill from existing sources, ask only what remains unknown (one question at a time, each skippable), and persist answers.
2. **Render `DISC.md`** following the structure below; render any skipped MANDATORY input as a quoted `TBD` marker and list it under "Unresolved fields" in the summary.

## Structure

```markdown
## Current State Assessment

### Business Context
- [Strategic direction, key drivers, organizational model]
- [Current operating model: processes, decision rights, governance]

### Capability Assessment
- [Current capability map with maturity ratings]
- [Capabilities aligned to strategic goals vs legacy/obsolete]

### Application Landscape
- [List existing applications with status: active, deprecated, planned]

### Data Inventory
- [List data systems, ownership, classification]

### Technology Stack
- [List infrastructure, platforms, hosting]

### Known Constraints
- [Legacy dependencies, compliance requirements, budget limits]
```

## Interview Questions (TOGAF 10 — current-state discovery)

The intake interview for this command asks the questions below before rendering
`DISC.md`. Questions already answerable from existing artefacts, saved intake,
onboarding data, or organisation config are **not** asked; a skipped question
renders as a `TBD` marker in the artefact.

- **Business context:** What is the strategic direction, and what are the key drivers and the current operating model?
- **Capability state:** Which capabilities exist today, at what maturity, and which are obsolete or legacy?
- **Application landscape:** Which applications exist, who owns them, and which are deprecated or planned for retirement?
- **Data state:** Which data systems exist, who owns the data, and what classification levels apply?
- **Technology baseline:** Which infrastructure, platforms, and hosting environments are in use?
- **Constraints:** What legacy dependencies, compliance requirements, and budget limits constrain any future state?
- **Pain points:** Where are the most acute operational, data, or technology problems today?

## Dependencies

- Requires `PRIN` — discovery is scoped by architectural principles
- Feeds into: `BPCM` (target capability design), `APP` (current vs target inventory),
  `DATA` (current data state), `TECH` (current technology baseline),
  `GAPA` (current vs target gap)
