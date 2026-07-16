# Discovery: Current State Assessment

Capture the existing enterprise state — applications, data systems, technology
platforms, and business capabilities — to establish a baseline for gap analysis
and rationalization.

## Inputs

- `PRIN` — Architectural principles that constrain discovery
- `{DISC_SCOPE}` — Scope of systems to inventory (e.g., "enterprise applications",
  "cloud infrastructure", "all enterprise systems")

## Output

`DISC.md` — Current state inventory covering:

1. **Application Landscape** — Existing applications, ownership, lifecycle status
2. **Data Inventory** — Databases, data flows, data ownership
3. **Technology Stack** — Infrastructure, platforms, hosting environments
4. **Business Capabilities** — Current capability map with coverage gaps

## Structure

```
## Current State Assessment

### Application Landscape
- [List existing applications with status: active, deprecated, planned]

### Data Inventory
- [List data systems, ownership, classification]

### Technology Stack
- [List infrastructure, platforms, hosting]

### Business Capabilities
- [Map current capabilities to applications/systems]

### Known Constraints
- [Legacy dependencies, compliance requirements, budget limits]
```

## Dependencies

- Requires `PRIN` — discovery is scoped by architectural principles
- Feeds into: `APP` (current vs target inventory), `DATA` (current data state),
  `TECH` (current technology baseline), `GAPA` (current vs target gap)