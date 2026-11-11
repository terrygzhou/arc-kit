# Changelog

## [6.11.0]

- **New `arckit-it4it` overlay plugin.** Six commands for the Open Group
  IT4IT Standard v3.1 (Snapshot, S261) — the reference architecture for
  managing the business of IT as product-based investment:

  | Command | Doc Type | Description |
  |---|---|---|
  | `it4it-value-network` | `ITVN` | The Value Network — all seven value streams, cross-stream dependencies |
  | `it4it-value-stream` | `ITVS` | One value stream (multi-instance, sequence-numbered) |
  | `it4it-strategy-portfolio` | `ITSF` | Strategy to Portfolio functions (S261 Ch. 6) |
  | `it4it-develop-test` | `ITDT` | Develop & Test functions — Requirement to Deploy (S261 Ch. 7) |
  | `it4it-consume-fulfil` | `ITCF` | Consume & Fulfil functions — Request to Fulfill (S261 Ch. 8) |
  | `it4it-operate-assure` | `ITOA` | Operate & Assure functions — Detect to Correct (S261 Ch. 9) + Supporting Functions cross-reference (Ch. 10) |

- `ITVS` registered as a multi-instance doc type (sequence-numbered
  instances, one per value stream).
- MANDATORY `PRIN` gate on every command; all other prerequisites
  RECOMMENDED (posture of `oaa-intake`).
- **Reference, not conformance**: S261 is a snapshot, not an approved
  standard — artefacts cite the standard as a reference and do not claim
  conformance (see `references/citation-instructions.md`).

## [Unreleased]
