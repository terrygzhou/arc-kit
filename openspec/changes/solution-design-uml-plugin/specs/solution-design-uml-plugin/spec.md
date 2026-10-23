## Purpose

Defines the `/arckit:solution-design` command: a governed UML 2.5.1 solution design document generator that produces a single `ARC-NNN-SOLN-v1.0.md` artefact with six embedded PlantUML diagram sections (use case, sequence, component, deployment, class, object), sourced from requirements, external HLD/DLD documents, and ADR artefacts.

## ADDED Requirements

### Requirement: Solution Design Command Generates a SOLN Artefact
When the user invokes `/arckit:solution-design <project ID>`, the command SHALL produce a governed solution design document at `projects/{NNN}/ARC-{NNN}-SOLN-v1.0.md` containing narrative design rationale and six embedded PlantUML diagram sections. The document SHALL be written using the Write tool (not streaming output) to avoid 32K token truncation.

#### Scenario: Command runs on a valid project
- **WHEN** the user runs `/arckit:solution-design 001` and the project `001` exists with at least one `ARC-001-REQ-v*.md` artefact
- **THEN** the command writes `projects/001*/ARC-001-SOLN-v1.0.md` containing all six UML diagram sections and a narrative design rationale section

#### Scenario: Requirements artefact is missing
- **WHEN** the user runs `/arckit:solution-design 001` and no `ARC-001-REQ-v*.md` artefact exists
- **THEN** the command warns the user that a requirements artefact is required and suggests running `/arckit:requirements` first, and does NOT write the SOLN document

### Requirement: SOLN Artefact Contains Six Embedded PlantUML Diagram Sections
The generated SOLN document SHALL contain six distinct sections, one per UML 2.5.1 diagram type, each with a fenced `plantuml` code block: (1) Use Case, (2) Sequence, (3) Component, (4) Deployment, (5) Class, (6) Object. Each section SHALL be populated from the relevant source artefacts and SHALL include a "View this diagram" callout listing at least: ArcKit Pages, VS Code PlantUML extension, and the PlantUML CLI command.

#### Scenario: All six sections are present
- **WHEN** the SOLN document is opened
- **THEN** it contains six `plantuml`-fenced code blocks, one for each of: use case, sequence, component, deployment, class, and object diagram types

#### Scenario: Each diagram section has a view callout
- **WHEN** a diagram section is rendered
- **THEN** the text "View this diagram" appears immediately below the plantuml block, with at least three viewing methods listed

### Requirement: Diagram Subset Is User-Configurable
The command SHALL present an interactive question allowing the user to select which of the six UML diagram types to generate in a single run (multi-select). The document skeleton SHALL always be generated in full; only the unselected diagram sections SHALL remain as placeholders. The default selection SHALL be all six types.

#### Scenario: User selects a subset
- **WHEN** the user selects only "sequence" and "class" in response to the diagram subset question
- **THEN** the generated document contains populated sequence and class diagram blocks, and the remaining four sections contain placeholder text indicating they were not selected for this run

#### Scenario: User passes subset in arguments
- **WHEN** the user runs `/arckit:solution-design 001 sequence,class`
- **THEN** the diagram subset question is skipped and only sequence and class diagram blocks are populated

### Requirement: PlantUML Is the Sole Notation
All diagram blocks in the SOLN document SHALL use the `plantuml` fenced code block notation. The command SHALL NOT offer Mermaid as an alternative notation. If the user explicitly requests Mermaid, the command SHALL note that Mermaid lacks object-diagram grammar and UML use-case/component references, and proceed with PlantUML.

#### Scenario: Mermaid is requested
- **WHEN** the user runs `/arckit:solution-design 001 mermaid` or explicitly asks for Mermaid output
- **THEN** the command notes the limitation (no object-diagram grammar in Mermaid) and generates all diagram blocks in PlantUML

#### Scenario: Default notation
- **WHEN** the user does not specify a notation
- **THEN** all diagram blocks are generated in PlantUML

### Requirement: SOLN Doc Type Is Registered
The `SOLN` code SHALL be registered in `doc-types.mjs` under `DOC_TYPES` (with a display name and `Architecture` category) and in `MULTI_INSTANCE_TYPES` (in both `doc-types.mjs` and both bash `generate-document-id.sh` copies). A corresponding row SHALL be added to the known-artifact-types table in `pages.md`. The `solution-design` command frontmatter SHALL declare `doc-type: SOLN`.

#### Scenario: SOLN is in the doc-type registry
- **WHEN** `plugins/arckit-claude/config/doc-types.mjs` is inspected
- **THEN** `SOLN` appears in the `DOC_TYPES` map with a display name and `Architecture` category, and in the `MULTI_INSTANCE_TYPES` set

#### Scenario: SOLN is in both bash script copies
- **WHEN** `scripts/bash/generate-document-id.sh` and `plugins/arckit-claude/scripts/bash/generate-document-id.sh` are inspected
- **THEN** both contain `SOLN` in their `MULTI_INSTANCE_TYPES` string

#### Scenario: SOLN is in the pages dashboard table
- **WHEN** `plugins/arckit-claude/commands/pages.md` known-artifact-types table is inspected
- **THEN** a row for `SOLN` appears under the Architecture category

#### Scenario: CI gates pass
- **WHEN** `python3 scripts/check-doc-type-registry.py` and `python3 scripts/check-multi-instance-parity.py` are run
- **THEN** both pass without error

### Requirement: Command Reads From Existing Artefacts and External Documents
The command SHALL read `ARC-NNN-REQ` (mandatory), external HLD/DLD documents (`vendors/{vendor}/hld-v*.md` / `vendors/{vendor}/dld-v*.md`, recommended), `ARC-NNN-ADR-*` (recommended), and `ARC-NNN-DATA-*` (recommended) to populate the diagram sections and narrative content. The command SHALL NOT require HLD/DLD to be ArcKit-generated artefacts — they are external documents.

#### Scenario: Requirements drive use case and sequence sections
- **WHEN** the SOLN document is generated from a project with `ARC-001-REQ-v1.0.md`
- **THEN** the use case diagram section is populated with actors and use cases derived from functional requirements, and the sequence diagram section is populated with lifelines derived from integration requirements

#### Scenario: HLD drives component and deployment sections
- **WHEN** an external HLD document (`vendors/{vendor}/hld-v*.md`) exists for the project
- **THEN** the component diagram section is populated with container/component boundaries from the HLD, and the deployment diagram section is populated with infrastructure zones and cloud resources

#### Scenario: Data model drives class section
- **WHEN** an `ARC-001-DATA-v*.md` artefact exists for the project
- **THEN** the class diagram section is populated with domain classes, attributes, and relationships derived from the data model

### Requirement: Companion DIAG Artefacts Are Optional
The command SHALL write companion standalone diagram artefacts at `projects/{NNN}/diagrams/ARC-{NNN}-DIAG-{NNN}-v1.0.md` (next available DIAG sequence) only when explicitly requested by the user or when the diagram subset question is answered with a single type. The DIAG artefact SHALL use the next available DIAG sequence number via `generate-document-id.sh --next-num`.

#### Scenario: DIAG artefact generated on request
- **WHEN** the user explicitly asks for companion DIAG artefacts during the interactive configuration
- **THEN** one `ARC-{NNN}-DIAG-{NNN}-v1.0.md` file is written to `projects/{NNN}/diagrams/` for each populated diagram type, using the next available DIAG sequence

#### Scenario: No DIAG artefacts by default
- **WHEN** the user does not request companion DIAG artefacts and the subset is more than one type
- **THEN** no DIAG artefact files are written; the SOLN document is the sole output

### Requirement: Template Carries Document Control and Traceability Sections
The SOLN template SHALL include: Document Control header, Revision History table, Overview section, six diagram sections (Use Case, Sequence, Component, Deployment, Class, Object), Design Rationale section, Requirements Traceability section, and External References section. The Requirements Traceability section SHALL map BR/FR/NFR/INT/DR requirement IDs to specific design elements.

#### Scenario: Template has all required sections
- **WHEN** the SOLN document skeleton is generated
- **THEN** it contains the Document Control header, Revision History table, Overview, six named diagram sections, Design Rationale, Requirements Traceability (with a BR/FR/NFR/INT/DR → design element mapping table), and External References sections

### Requirement: Handoffs Are Declared in Frontmatter
The `solution-design` command frontmatter SHALL declare `handoffs` for at least: `traceability` (map design decisions back to requirements), `diagram` (generate companion standalone C4/DIAG artefacts), and `hld-review` (validate the solution design against the HLD). The handoffs SHALL render as a "Suggested Next Steps" section in all non-Claude targets.

#### Scenario: Handoffs render in Codex skill
- **WHEN** the Codex target (`extensions/arckit-codex/skills/arckit-solution-design/SKILL.md`) is generated by `scripts/converter.py`
- **THEN** a "Suggested Next Steps" section appears in the skill body listing `traceability`, `diagram`, and `hld-review` with their descriptions
