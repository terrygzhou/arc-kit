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

## Structure

```
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

## Dependencies

- Requires `PRIN` — discovery is scoped by architectural principles
- Feeds into: `BPCM` (target capability design), `APP` (current vs target inventory),
  `DATA` (current data state), `TECH` (current technology baseline),
  `GAPA` (current vs target gap)