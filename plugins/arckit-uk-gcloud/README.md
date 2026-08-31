# ArcKit — UK G-Cloud Supplier Bid Overlay

**PROPRIETARY — not covered by the repository MIT licence. EXPERIMENTAL.**
All outputs are draft bid artefacts: they require review by the supplier's
bid/compliance team before submission to Crown Commercial Service.

11 slash commands and the `uk-gcloud-submission` build recipe that drive a
G-Cloud 14 Digital Marketplace submission end to end (supplier-side):

| Command | Doc Type | Description |
|---------|----------|-------------|
| `/arckit-uk-gcloud:supplier-profile` | `SUPP` | Create or update a reusable supplier profile for G-Cloud submissions |
| `/arckit-uk-gcloud:declaration` | `DECL` | Supplier declaration for the G-Cloud framework |
| `/arckit-uk-gcloud:service-design` | `SVCD` | Design a new cloud service offering for the G-Cloud marketplace |
| `/arckit-uk-gcloud:sdd-lot2` | `SDD` | Service Definition Document — Lot 2 (Cloud Software / SaaS), the default lot |
| `/arckit-uk-gcloud:sdd-lot1` | `SDD` | Service Definition Document — Lot 1 (Cloud Hosting / IaaS / PaaS) |
| `/arckit-uk-gcloud:sdd-lot3` | `SDD` | Service Definition Document — Lot 3 (Cloud Support) |
| `/arckit-uk-gcloud:pricing` | `PRIC` | G-Cloud pricing document for a service |
| `/arckit-uk-gcloud:security` | `SECA` | NCSC Cloud Security Principles assertions and evidence |
| `/arckit-uk-gcloud:gcloud-competitors` | `GCMP` | Benchmark a service against Digital Marketplace rivals |
| `/arckit-uk-gcloud:review` | `GCRV` | Completeness review of the submission before CCS hand-off |
| `/arckit-uk-gcloud:submission-pack` | — | Bundle all approved documents into the CCS submission pack |

Doc-type codes: `SUPP`, `DECL`, `SVCD`, `SDD`, `PRIC`, `SECA`, `GCMP`, `GCRV`.

Recipe: `uk-gcloud-submission` (supplier profile → declaration → service design → SDD → pricing → NCSP assertions → competitor benchmark → review-ready submission). The default lot is Lot 2 (SaaS); override the SDD target to `arckit:sdd-lot1` or `arckit:sdd-lot3` via a project-level `.arckit/recipes/uk-gcloud-submission.yaml`.

The plugin also bundles three reference skills: `gcloud-framework`, `cloud-security`, and `sfia-skills`.

## Requires arckit core plugin

```bash
claude plugin install arckit arckit-uk-gcloud
```

On Claude Code v2.1.143+, `claude plugin disable arckit` will refuse with a copy-pasteable disable-chain hint while `arckit-uk-gcloud` is enabled. Without `arckit` (core), the recipe will not resolve foundation commands (`arckit:principles`, `arckit:requirements`, etc.) and `validate-arc-filename` will not recognise G-Cloud doc-type codes (`SUPP`, `DECL`, `SVCD`, `SDD`, `PRIC`, `SECA`, `GCMP`, `GCRV`).

## Scope

**In scope**: Supplier-side G-Cloud 14 bid authoring — supplier profile, framework declaration, service design, Service Definition Documents (all three lots), pricing, NCSP security assertions, competitor benchmarking, submission review and packaging.

**Out of scope**: Buyer-side (CCS) evaluation, frameworks other than G-Cloud, contract negotiation.

## Maintainer

© 2026 Mark Craddock — proprietary overlay, governed by the plugin's proprietary licence file (not the repository MIT licence). EXPERIMENTAL.
