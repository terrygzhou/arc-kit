# IT4IT Intake Discovery Dimensions

Canonical discovery-dimension floor for `arckit-it4it` intake. Used in
addition to the template-derived questions. Adds **no diagram or output
mandate** (design decision D5).

## Dimensions

| Dimension | Source (prefill from) | Skippable? |
|---|---|---|
| **Digital Product** (anchor KDO bundle) | `.arckit/intake/`, `shared.json`, PRIN | yes |
| **Product-vs-project posture** | PRIN (000-global) | no — MANDATORY gate |
| **Stream / function scope** | template argument-hint, existing IT4IT artefacts | yes |
| **Scenarios in scope (S261 catalog)** | `shared.json`, prior IT4IT artefacts | yes |
| **Stakeholder / accountable role** | `user_config.organisation_name`, PRIN | yes |
| **KDO systems of record** | `shared.json`, external docs | yes |
| **Cardinality deviations (gaps)** | `shared.json`, external docs | yes |
| **Feedback loop (Operate → Evaluate)** | ITVN, ITOA artefacts | yes |

## Resolution Order

For each dimension, resolve in this order before asking:

1. Existing artefact (PRIN, ITVN, ITSF, ITDT, ITCF, ITOA) in the project
2. `.arckit/intake/` saved answers
3. `user_config` (organisation, classification, prefix, references dir)
4. `shared.json` / external reference documents
5. Otherwise → ask as a grouped, skippable question (skip → `TBD`)

A dimension resolved from 1–4 is surfaced **prefilled** for
confirmation/override (ask-always, answer-optional). A dimension with no
source is asked; a skipped answer renders a `TBD` marker.
