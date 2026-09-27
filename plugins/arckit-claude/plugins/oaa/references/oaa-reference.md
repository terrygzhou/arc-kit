# O-AA Standard (C208) Reference

Open Agile Architecture (O-AA) C208 is the standard for agile enterprise architecture, providing sprint-based, product-driven architecture delivery methods. This reference summarizes the chapters relevant to ArcKit O-AA commands.

## Axioms and Principles

O-AA is built on 16 axioms that define agile architecture practice. Key axioms for ArcKit:

O-AA is built on the 16 axioms defined in C208 Ch. 9 (§9.1–§9.16). `oaa-adm-lite` applies axioms 1–10 to the ADM Lite mapping; the remaining axioms anchor the other commands:

| # | Axiom (C208 Ch. 9) | Applied by |
|---|---|---|
| 1 | Customer Experience Focus | oaa-adm-lite |
| 2 | Outside-In Thinking | oaa-adm-lite |
| 3 | Rapid Feedback Loops | oaa-adm-lite |
| 4 | Touchpoint Orchestration | oaa-adm-lite |
| 5 | Value Stream Alignment | oaa-adm-lite |
| 6 | Autonomous Cross-Functional Teams | oaa-adm-lite |
| 7 | Authority, Responsibility, and Accountability Distribution | oaa-adm-lite |
| 8 | Loosely-Coupled Systems | oaa-adm-lite |
| 9 | Modular Data Platform | oaa-adm-lite |
| 10 | Simple Common Operating Principles | oaa-adm-lite |
| 11 | Partitioning Over Layering | product-architecture |
| 12 | Organization Mirroring Architecture | agile-governance |
| 13 | Organizational Leveling | agile-governance |
| 14 | Bias for Change | agile-strategy |
| 15 | Project to Product Shift | product-architecture |
| 16 | Secure by Design | agile-security |

Key axioms for the domain commands:

- **Axiom 11 (Partitioning Over Layering)** and **Axiom 15 (Project to Product Shift)** — `product-architecture`: architecture is organized around product domains, not technical layers
- **Axiom 12 (Organization Mirroring Architecture)** and **Axiom 13 (Organizational Leveling)** — `agile-governance`: organization and architecture co-evolve; governance operates at sprint velocity with lightweight evidence
- **Axiom 14 (Bias for Change)** — `agile-strategy`: strategy and architecture co-evolve; late changes are welcome, not defects
- **Axiom 16 (Secure by Design)** — `agile-security`: security is embedded in every sprint, not gated at phase boundaries

## Chapter 11 — Agile Strategy

Covers dual transformation strategy for enterprise architecture:

- **Legacy Modernization Track**: Incremental evolution of existing architecture through sprint-based improvements

- **Greenfield Innovation Track**: New architecture built from scratch for new capabilities

- **Strategy Canvas**: Visual mapping of current state, target state, and transformation path

- **Portfolio Alignment**: Architecture investments mapped to business outcomes and strategic priorities

Used by: `agile-strategy` command (OASTR doc type)

## Chapter 14 — Product Architecture

Defines product-centric architecture approach:

- **Product Mission**: Clear outcome definition and value proposition

- **Cross-Functional Teams**: Roles and responsibilities organized around product domains

- **Backlog-Driven Delivery**: Architecture components derived from product backlog items

- **Value Stream Mapping**: End-to-end flow from stakeholder need to delivered value

- **Product vs System View**: Distinguishing product-centric (outcome-focused) from system-centric (component-focused) architecture

Used by: `product-architecture` command (OAPR doc type)

## Security (Ch. 4.6 + Axiom 16 + G216)

Embeds security into agile architecture delivery:

- **Security Backlog**: Security requirements treated as backlog items, prioritized alongside features

- **Threat Modeling Per Sprint**: Each sprint includes threat modeling for the features being delivered

- **Continuous Compliance**: Compliance evidence collected continuously, not at gate reviews

- **Security Controls Assessment**: Controls assessed in continuous model rather than phase-gate checkpoints

- **Residual Risk Documentation**: Documenting remaining risk after sprint-level mitigations

Used by: `agile-security` command (OASEC doc type)

## Chapter 8 — Agile Governance

Lightweight governance aligned to sprint cycles:

- **Sprint-Aligned Governance**: Review gates per sprint or release, not quarterly architecture boards

- **Minimal Artefacts**: Maximum 2 governance artefacts per sprint cycle

- **Lightweight Compliance Evidence**: Streamlined evidence collection that doesn't slow delivery

- **Change Management at Sprint Velocity**: Architecture change requests processed within sprint cadence

- **Architecture Review Gates**: Lightweight reviews embedded in sprint ceremonies

Used by: `agile-governance` command (OAGOV doc type)

## ADM Lite Mapping (ArcKit convention over TOGAF ADM, C182)

Maps the traditional TOGAF ADM cycle to agile sprint delivery. ADM Lite is an ArcKit convention, not a C208 chapter range — C208 defines no ADM cycle:

- **Sprint Windows**: 2–4 week engagement windows per ADM phase

- **Backlog-Driven ADM**: Each ADM phase broken into user stories and backlog items

- **Sprint Review Outputs**: Architecture artefacts produced and reviewed each sprint

- **Stakeholder Cadence**: Engagement rhythms aligned to sprint cycles

Used by: `oaa-adm-lite` command (OAAL doc type)

## Official Source

Open Agile Architecture: https://openagilearchitecture.com
