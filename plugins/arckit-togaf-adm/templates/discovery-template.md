---
title: "Current State Discovery"
phase: "Preliminary"
type: "DISC"
project: "{{ project }}"
---

# Current State Assessment

## Intake Interview Questions

The template-driven intake interview asks the questions below before rendering this
artefact. Every question below is always put to the user for their input, one
question at a time, and is prefilled where answerable from existing artefacts,
saved intake, onboarding data, or organisation config so the user can confirm or
override it. Each question is **optional**: a skipped question renders as a
`TBD` marker in the artefact. Sources: TOGAF Standard, 10th Edition
(discovery dimensions per ADM phase) and the O-AA / agentic outcome dimensions below.

### Intake questions (TOGAF 10 — current-state discovery)

- **Business context:** What is the strategic direction, and what are the key drivers and the current operating model?
- **Capability state:** Which capabilities exist today, at what maturity, and which are obsolete or legacy?
- **Application landscape:** Which applications exist, who owns them, and which are deprecated or planned for retirement?
- **Data state:** Which data systems exist, who owns the data, and what classification levels apply?
- **Technology baseline:** Which infrastructure, platforms, and hosting environments are in use?
- **Constraints:** What legacy dependencies, compliance requirements, and budget limits constrain any future state?
- **Pain points:** Where are the most acute operational, data, or technology problems today?

**Project:** {{ project }}
**Generated:** {{ now }}

## Application Landscape

<!-- List existing applications with status -->

| Application | Owner | Status | Lifecycle | Cloud/On-Prem |
|-------------|-------|--------|-----------|---------------|
| | | Active/Deprecated | | |

## Data Inventory

<!-- List data systems, ownership, classification -->

| Data System | Type | Owner | Classification | Platform |
|-------------|------|-------|----------------|----------|
| | | | Public/Internal/Restricted | |

## Technology Stack

<!-- List infrastructure, platforms, hosting -->

| Component | Type | Version | Owner | Status |
|-----------|------|---------|-------|--------|
| | | | | |

## Business Capabilities

<!-- Map current capabilities to applications/systems -->

| Capability | Level | Supporting Systems | Gaps |
|------------|-------|-------------------|------|
| | Strategic/Tactical/Operational | | |

## Known Constraints

- Legacy dependencies:
- Compliance requirements:
- Budget/timeline limits:
