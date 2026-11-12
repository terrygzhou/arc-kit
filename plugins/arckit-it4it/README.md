# ArcKit — IT4IT (S261) Overlay

6 slash commands for the Open Group IT4IT Standard v3.1 (Snapshot, S261) —
the vendor-neutral reference architecture for managing the business of IT as
product-based investment. The Digital Product is the anchor; seven value
streams run the lifecycle; functional components and key data objects define
the target architecture:

| Command | Doc Type | Description |
|---------|----------|-------------|
| `/arckit-it4it:it4it-value-network` | `ITVN` | The Value Network — all seven value streams, cross-stream dependencies |
| `/arckit-it4it:it4it-value-stream` | `ITVS` | One value stream (multi-instance: `ARC-{P}-ITVS-{NNN}-v1.0.md`) |
| `/arckit-it4it:it4it-strategy-portfolio` | `ITSF` | Strategy to Portfolio — policy, strategy, portfolio backlog, proposal |
| `/arckit-it4it:it4it-develop-test` | `ITDT` | Develop & Test — backlog, design, pipeline, build, release composition |
| `/arckit-it4it:it4it-consume-fulfil` | `ITCF` | Consume & Fulfil — offering catalog, order, subscription, fulfillment |
| `/arckit-it4it:it4it-operate-assure` | `ITOA` | Operate & Assure — service level, incident/problem, monitoring, runbooks |

**Official standard:** <https://pubs.opengroup.org/it4it/3.1/snapshot>
(IT4IT v3.1 Snapshot, S261, 12 October 2026 — a snapshot, not an approved
standard: artefacts reference it, they do not claim conformance.)

## Relationship to O-AA

IT4IT complements Open Agile Architecture (C208): O-AA is the method,
IT4IT is the target state for IT product lifecycle management. Use
`arckit-oaa` for *how to develop and evolve* architecture, and
`arckit-it4it` for *what the IT/ITSM target architecture looks like*.

## Requires arckit core plugin

```bash
claude plugin install arckit
claude plugin install arckit-it4it
claude plugin enable arckit-it4it   # if it shows as disabled (community plugins install disabled by default)
```

Without `arckit` (core), `validate-arc-filename` will not recognise
IT4IT doc-type codes (`ITVN`, `ITVS`, `ITSF`, `ITDT`, `ITCF`, `ITOA`).

## Configuration (userConfig)

| Key | Default | Purpose |
|-----|---------|---------|
| `default_classification` | `PUBLIC` | Default document classification |
| `organisation_name` | *(empty)* | Organisation name in document control blocks |
| `project_issue_prefix` | `ARC` | Issue prefix for engagement references |
| `references_dir` | *(empty)* | Directory of external reference documents |

## Prerequisites

MANDATORY for every command: `PRIN` (Architecture Principles, `000-global`).
RECOMMENDED: `ITVN` for value-stream commands; the functional-component
commands (`ITSF`, `ITDT`, `ITCF`, `ITOA`) recommend `ITVN` where available.

## Shared schemas

`schemas/value-stream.json` and `schemas/functional-component.json`
(draft-07) — see `schemas/README.md` for validation via
`python3 validate-architecture.py`.

## Full receipt: `it4it-full` recipe

`recipes/it4it-full.yaml` is the IT4IT "full receipt" — the canonical set of
six targets (`PRIN`, `ITVN`, `ITSF`, `ITDT`, `ITCF`, `ITOA`) with their
dependency edges, ready to hand to the `arckit-build` orchestrator:

```bash
/arckit:build 001 --recipe it4it-full
```

Each command's "Show Summary to User" block is the receipt line for its own
target; the build harness's post-build hooks (`arckit:health`,
`arckit:traceability`, `arckit:pages`) plus the `## Build Provenance` stamp on
every artefact together form the build receipt. `ITVS` is deliberately
excluded from the full set — it is a multi-instance doc type and is run on
demand per value stream.
