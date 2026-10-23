## 1. Doc-Type Registration (hard prerequisite — must complete before the command is written)

- [ ] 1.1 Add `SOLN` to the `DOC_TYPES` map in `plugins/arckit-claude/config/doc-types.mjs` with `{ name: 'Solution Design', category: 'Architecture' }` and add `'SOLN'` to the `MULTI_INSTANCE_TYPES` set; verify by running `python3 -c "import importlib.util; m=importlib.util.spec_from_file_location('d','plugins/arckit-claude/config/doc-types.mjs')"` is not applicable (ESM) — instead run `grep "SOLN" plugins/arckit-claude/config/doc-types.mjs` and confirm both entries are present
- [ ] 1.2 Add `SOLN` to the `MULTI_INSTANCE_TYPES` string in `scripts/bash/generate-document-id.sh` (line ~85) and in `plugins/arckit-claude/scripts/bash/generate-document-id.sh` (equivalent line); verify by running `python3 scripts/check-multi-instance-parity.py` and confirming it passes
- [ ] 1.3 Add a `SOLN` row under the Architecture category in the known-artifact-types table in `plugins/arckit-claude/commands/pages.md` (pattern `ARC-*-SOLN-*.md`, display name `Solution Design`); verify by running `python3 scripts/check-doc-type-registry.py` and confirming it passes
- [ ] 1.4 Run both `python3 scripts/check-doc-type-registry.py` and `python3 scripts/check-multi-instance-parity.py`; verify both exit 0

## 2. New Reference: `object-diagrams.md`

- [ ] 2.1 Write `plugins/arckit-claude/skills/plantuml-syntax/references/object-diagrams.md` covering: PlantUML object syntax (`object "Name" as ID <<stereotype>>`), instance-to-instance links (`ID1 --> ID2 : label`), attribute state display, and a worked example of an order/checkout scenario; verify the example renders without syntax errors by copying the `@startuml`…`@enduml` block to a temp `.puml` file and running `java -jar plantuml.jar temp.puml` (or the locally available PlantUML CLI)
- [ ] 2.2 Confirm the new file is picked up by the converter by running `python scripts/converter.py` and then `ls extensions/arckit-codex/skills/plantuml-syntax/references/` to confirm `object-diagrams.md` is present; verify no manifest changes were required

## 3. New Template: `solution-design-template.md`

- [ ] 3.1 Create `plugins/arckit-claude/templates/solution-design-template.md` with: Document Control header (prose placeholder matching existing template style, NOT `<!-- DOC-CONTROL-HEADER -->`), Revision History table, Overview section, six diagram sections (Use Case, Sequence, Component, Deployment, Class, Object) each with a `plantuml`-fenced placeholder block and a "View this diagram" callout (ArcKit Pages / VS Code / CLI), Design Rationale section, Requirements Traceability table (BR/FR/NFR/INT/DR → design element), and External References section; verify by opening the file and confirming all ten sections are present
- [ ] 3.2 Copy the template to `.arckit/templates/solution-design-template.md` (dual-tree rule); verify both files exist and are identical (`diff plugins/arckit-claude/templates/solution-design-template.md .arckit/templates/solution-design-template.md` exits 0)

## 4. New Command: `solution-design.md`

- [ ] 4.1 Create `plugins/arckit-claude/commands/solution-design.md` with frontmatter: `description` (UML 2.5.1 solution design), `argument-hint: "<project ID, e.g. '001'>"`, `effort: high`, `doc-type: SOLN`, `handoffs:` (traceability, diagram, hld-review); verify by `grep "doc-type" plugins/arckit-claude/commands/solution-design.md` returning `SOLN`
- [ ] 4.2 Write the command body following the `data-model.md` interactive pattern (max 2 question rounds): Q1 diagram subset (multi-select, default all six), Q2 notation confirmation (PlantUML-only — if user requests Mermaid, note the limitation and proceed with PlantUML); include the pre-check step that uses the ArcKit Project Context hook (NOT `create-project.sh --json`) to verify the project exists and has `ARC-NNN-REQ`; include the read-project-context step that reads `ARC-NNN-REQ` (mandatory), external HLD/DLD documents (`vendors/{vendor}/hld-v*.md` / `vendors/{vendor}/dld-v*.md`), `ARC-NNN-ADR-*`, and `ARC-NNN-DATA-*`; verify by reading the file and confirming: no `create-project.sh` reference, no `ARC-NNN-HLD`/`ARC-NNN-DLD` reference, HLD/DLD are referenced as external vendor documents
- [ ] 4.3 Add the "Generate document with Write tool" step (32K limit rule) writing to `projects/NNN/ARC-NNN-SOLN-v1.0.md` using `${CLAUDE_PLUGIN_ROOT}/templates/solution-design-template.md`; verify by `grep "Write tool" plugins/arckit-claude/commands/solution-design.md`
- [ ] 4.4 Add the "Generate companion DIAG artefacts" step (off by default, on when user requests or Q1 subset is a single type) using `generate-document-id.sh --next-num`; verify by `grep "DIAG" plugins/arckit-claude/commands/solution-design.md`

## 5. Update `plantuml-syntax` SKILL.md Table

- [ ] 5.1 Update the "ArcKit Commands Using It" column in `plugins/arckit-claude/skills/plantuml-syntax/SKILL.md`: add `/arckit:solution-design` to the Use Case, Sequence, Class, Component, and Deployment rows; add a new Object Diagram row with `object-diagrams.md` as the reference and `/arckit:solution-design` in the commands column; verify by `grep -c "solution-design" plugins/arckit-claude/skills/plantuml-syntax/SKILL.md` returning 6

## 6. New Guide: `docs/guides/solution-design.md`

- [ ] 6.1 Write `docs/guides/solution-design.md` covering: purpose, the six supported diagram types (table), when to use the command, argument examples (including the `sequence,class` subset syntax), PlantUML-only rationale (Mermaid lacks object-diagram grammar and UML use-case/component reference), viewing/export instructions (ArcKit Pages, PlantUML server, VS Code, CLI — note GitHub does not render PlantUML inline), link to `/arckit:diagram` for standalone C4 artefacts, and a worked excerpt of a generated SOLN document; verify by opening the file and confirming all sections are present
- [ ] 6.2 Run `python3 scripts/check-guide-parity.py --sync` to copy the guide into `plugins/arckit-claude/docs/guides/`; verify by `diff docs/guides/solution-design.md plugins/arckit-claude/docs/guides/solution-design.md` exiting 0

## 7. Regenerate Extensions and Run CI Gates

- [ ] 7.1 Run `python scripts/converter.py` to regenerate all seven non-Claude extensions; verify by checking that `extensions/arckit-codex/skills/arckit-solution-design/SKILL.md` and `extensions/arckit-codex/skills/arckit-solution-design/agents/openai.yaml` both exist and that the SKILL.md contains a "Suggested Next Steps" section listing traceability, diagram, and hld-review
- [ ] 7.2 Run `pytest tests/codex/test_codex_extension.py` and confirm it passes (it imports the converter and validates the generated Codex structure, now covering the new skill)
- [ ] 7.3 Run `./scripts/ci-local.sh` (or `SKIP_NETWORK=1 ./scripts/ci-local.sh`) and confirm all gates pass, including `check-doc-type-registry.py` and `check-multi-instance-parity.py`

## 8. Documentation and Release Artifacts

- [ ] 8.1 Add `/arckit:solution-design` to the command index in `README.md` (command list section); verify by `grep "solution-design" README.md`
- [ ] 8.2 Update `docs/DEPENDENCY-MATRIX.md`: add a `solution-design` row showing its dependencies (requirements M, HLD/DLD external R, ADR R, data-model R) and dependent commands (traceability, hld-review, diagram); verify by opening the file and confirming the row is present
- [ ] 8.3 Add a `CHANGELOG.md` entry under the next release heading describing the new command, the `SOLN` doc-type registration, the new `object-diagrams.md` reference, and the updated `plantuml-syntax` SKILL.md table; verify by `grep "solution-design" CHANGELOG.md`
- [ ] 8.4 Run `./scripts/bump-version.sh` to bump to the next patch version; verify the version string in `plugins/arckit-claude/.claude-plugin/plugin.json` and other version-bearing files was updated

## 9. Final Verification

- [ ] 9.1 Test in a test repo: run `/arckit:solution-design 001` on a real project with an existing `ARC-001-REQ` artefact; verify all six diagram sections are populated with `plantuml`-fenced blocks, the "View this diagram" callout appears under each section, and no 32K truncation occurred
- [ ] 9.2 Test companion DIAG artefact generation: run `/arckit:solution-design 001` with the user requesting DIAG artefacts; verify one `ARC-001-DIAG-NNN-v1.0.md` file is written to `projects/001/diagrams/` with the correct next sequence number
- [ ] 9.3 Test the Codex target: scaffold a test repo with `arckit init test-solution --ai codex --no-git`; confirm `.agents/skills/arckit-solution-design/SKILL.md` exists, is invocable as `$arckit-solution-design`, and that the `plantuml-syntax` skill's `references/` folder includes `object-diagrams.md`
- [ ] 9.4 Run `python3 scripts/check-guide-parity.py` (verify no drift) and `npx markdownlint-cli2 "**/*.md"` (Markdown style gate); verify both pass
- [ ] 9.5 Commit with conventional `feat:` prefix and open PR against `main`
