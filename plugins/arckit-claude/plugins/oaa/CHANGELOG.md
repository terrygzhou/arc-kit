# Changelog

## [Unreleased]

- **MANDATORY `PRIN` hard gate on all five OAA commands.** `oaa-adm-lite`, `product-architecture`, `agile-governance`, `agile-security`, and `agile-strategy` now stop when the `000-global` `ARC-000-PRIN-v[N].md` artefact is missing (run `/arckit:principles` first) — matching the TOGAF ADM hard gate. All other OAA prerequisites remain RECOMMENDED.

- **New OAA discovery-dimension checklist (`references/intake-discovery-dimensions.md`).** Canonical D1–D10 coverage floor (vision/strategy, capabilities, stakeholders, constraints/drivers, current-state, technology, data, pain points/gaps, outcomes, axioms) loaded by every OAA intake step alongside the shared intake block: resolvable dimensions are prefilled and surfaced for confirmation/override (ask-always, answer-optional), source-less dimensions are asked grouped and skippable (skip → `TBD`), and the checklist adds no diagram or output mandate.

- `product-architecture` (C4) and `oaa-adm-lite` (flowchart) now load the Mermaid
  syntax references before reading their templates, so generated diagrams follow
  the reference syntax

- `oaa-full` post-build hooks now also regenerate the documentation site (`arckit:pages`),
  matching the other overlay recipes

- **`oaa-full`: OAGOV no longer hard-blocks on OASEC.** OASEC moved from `deps` to `optional_deps`, matching the command's own contract ("if missing: note that security context is limited") — enabling governance without security now builds instead of silently skipping. Security context is still fed to OAGOV whenever OASEC exists.

- **Removed hard-coded engagement identifiers**: `EYW-123/126/127/128` issue refs, `EYW-SAFETY-001` checklist ID, and all absolute Obsidian Vault paths are now `${user_config.*}` placeholders with sensible empty-value fallbacks

- **New userConfig keys** in `.claude-plugin/plugin.json`:

  - `organisation_name` — organisation/client name substituted into rendered artefacts
  - `project_issue_prefix` — identifier prefix for engagement/parent issue references (default `ARC`)
  - `safety_checklist_id` — safety/compliance checklist ID referenced in `governance-report.yaml` (blank → `[PENDING]` placeholder)
  - `references_dir` — directory of external reference documents; empty → organisation-specific references omitted

- **Rendering contract**: `templates/_partials/RENDERING.md` now documents placeholder substitution for all O-AA templates, not just the doc-control partial

- No breaking changes to commands or recipe; `arckit-oaa` remains standalone (depends only on `arckit` core)

## 6.7.5 (2026-08-13)

- **New standalone plugin**: Split from `arckit-togaf-adm` as `arckit-oaa`

- 5 O-AA commands: `oaa-adm-lite`, `product-architecture`, `agile-strategy`, `agile-security`, `agile-governance`

- 5 templates with `_partials` inherited from `arckit-agent-architecture` pattern

- Build recipe: `oaa-full` (strategy → product → ADM Lite → security → governance)

- References: quality-checklist, citation-instructions, O-AA C208 reference
