# ADM Artefact Conformance — proposal

## Why

The 2026-09-02 conformance review of `test-adm-australian-post` project
`001-australian-post-digital-transformation` (ADMP generated 6.7.5, BPCM
generated 6.8.0) found the generated artefacts drifting from the quality
checklist in three structural ways, all traceable to the shipped templates
and reference docs:

1. **Document Control under-provision.** The quality checklist (common check
   #1) requires **14** Document Control fields, but 8 of the 11 shipped ADM
   templates carry only 7-field tables (or, for `architecture-change` /
   `architecture-repository`, a non-standard subset). A template that lists a
   subset guarantees the artefacts rendered from it fail check #1 — the
   ADMP in project 001 does exactly that, and its generation footer is
   missing the `Model` field (check #7).
2. **Revision-history columns disagree.** Checklist common check #6 lists
   `Version, Date, Author, Changes, Approved By, Approval Date`; every
   template and both generated artefacts use
   `Version, Date, Author, Description, Reviewer, Approver`. The checklist
   copy (31 tracked plugin copies + 1 autoresearch doc copy) is the
   outlier.
3. **Unrenderable template diagrams.** 8 template copies across
   `capability-map`, `gap-analysis`, `application-inventory` and
   `agent-maturity` ship mermaid `quadrantChart` blocks that fail to parse:
   `x-axis__` / `y-axis__` typos, a bare-comma coordinate form
   (`"C1.1.1": 0.8, 0.3`), and a comma-separated point form
   (`"Design", [0.3, 0.4]`).
4. **Intake provenance gaps.** The ADMP intake JSON records no provenance
   for the fields the remediated artefact now carries (Document Type, Last
   Modified, Review Cycle, Next Review Date, Distribution) and has no audit
   entries for the agent-derived content sections (§2.1/§2.2, §5, §7,
   §11); the BPCM intake JSON stores its provenance under a non-standard
   key (`document_control_provenance`) instead of `prefill_provenance`.

## What Changes

- **ADM template Document Control expansion (both trees).** The 10 ADM
  templates with a Document Control table
  (`plugins/arckit-claude/plugins/togaf/adm/templates/` + the
  `plugins/arckit-togaf-adm/templates/` mirror) now enumerate all 14
  checklist fields. `discovery-template.md` (DISC) is excluded — it renders
  through the `{{ }}` placeholder path and carries no Document Control
  section.
- **Revision-history column standardisation.** Checklist common check #6 in
  all 31 tracked `quality-checklist.md` copies plus
  `scripts/autoresearch/program.md` now lists
  `Version, Date, Author, Description, Reviewer, Approver`, matching the
  templates and the generated artefacts. Generated `extensions/*` copies are
  regenerated, not hand-edited.
- **Template mermaid validity.** `quadrantChart` axis lines and plot-point
  lines in the 4 affected templates (8 copies incl. the
  `agent-architecture` mirror) are corrected to valid mermaid syntax.
- **TDD guard.** New `tests/plugin/test_adm_doc_control_conformance.py`
  asserts (a) every ADM template with a Document Control section lists all
  14 fields in both trees, (b) no `x-axis__` / `y-axis__` typo and no
  comma-form plot points in ADM/agent template mermaid blocks, (c) the
  revision-history header is the canonical six-column form, (d) checklist
  check #6 names the canonical columns.
- **Project 001 remediation (gitignored test fixtures, not committed).**
  ADMP Document Control expanded to 14 fields + `Model` footer line +
  remediation revision row; both intake JSONs gain the missing
  `prefill_provenance` entries (BPCM key renamed); `README.md` artefact
  table gains the BPCM row.

## Capabilities

### Modified Capabilities
- `artifact-generation`: gains two requirements —
  **Document Control And Generation Footer Conformance** (templates list the
  full 14-field table; canonical revision-history columns; footer includes
  `Model`) and **Shipped Templates Are Renderable Conforming Examples**
  (template mermaid blocks parse as shipped).

## Non-goals

- No DISC (discovery) template change — different rendering path, no
  Document Control section; flagged for a future change.
- No OAA template audit — checklist #1 also binds OAA artefacts, but this
  change scopes to the ADM templates implicated by the review.
- No interview-flow, prefill-precedence, or hook changes.
- No editing of gitignored `extensions/*` or `.venv` copies — regenerated
  only.

## Impact

- 20 ADM template files (10 x 2 trees), 2 `agent-maturity` template files,
  32 tracked reference/doc files (31 `quality-checklist.md` + 1
  `scripts/autoresearch/program.md`), 1 new pytest file, 1
  `CHANGELOG.md` entry.
- Project 001 test fixtures (gitignored): ADMP artefact, two intake JSONs,
  `README.md`.
- Regenerated (gitignored): `extensions/*` via `scripts/converter.py`.
