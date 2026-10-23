## MODIFIED Requirements

### Requirement: plantuml-syntax Skill Ships Progressive-Disclosure Material
The `plantuml-syntax` skill SHALL ship reference files under `references/` covering all diagram types used by shipped ArcKit commands. The SKILL.md body SHALL contain a table mapping diagram types to reference files and the ArcKit commands that use them.

#### Scenario: object-diagrams reference is present
- **WHEN** `plugins/arckit-claude/skills/plantuml-syntax/references/` is inspected
- **THEN** `object-diagrams.md` exists and covers PlantUML object diagram syntax: instance declarations, `<<stereotype>>`, object-to-object links, and attribute state

#### Scenario: SKILL.md table includes solution-design for object diagrams
- **WHEN** the `plantuml-syntax/SKILL.md` "Supported Diagram Types" table is read
- **THEN** the Object Diagram row lists `object-diagrams.md` as the reference and `/arckit:solution-design` in the "ArcKit Commands Using It" column

#### Scenario: SKILL.md table includes solution-design for UML diagram types
- **WHEN** the `plantuml-syntax/SKILL.md` "Supported Diagram Types" table is read
- **THEN** the Use Case, Sequence, Class, Component, and Deployment rows each list `/arckit:solution-design` in the "ArcKit Commands Using It" column, in addition to any existing commands

#### Scenario: converter picks up new reference file
- **WHEN** `python scripts/converter.py` is run
- **THEN** `object-diagrams.md` is copied to `extensions/arckit-codex/skills/plantuml-syntax/references/` and all other non-Claude extension variants, with no manifest changes required
