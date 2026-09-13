# slash-commands (delta)

## ADDED Requirements

### Requirement: Commands Follow The ArchiMate Diagram Production Policy
Every document-generating slash command SHALL apply the ArchiMate Diagram Production Policy (see the `artifact-generation` spec): when generating a document, if a diagram can be represented in ArchiMate, or an additional ArchiMate diagram should be added, it SHALL be produced with PlantUML ArchiMate and rendered to a self-contained SVG; the command SHALL NOT create a new architecture document file for the diagram (PlantUML source inline, only the `.svg` emitted). Commands SHALL otherwise continue to generate documents and their non-ArchiMate diagrams exactly as before.

#### Scenario: a command producing an ArchiMate-representable diagram uses PlantUML
- **WHEN** `/arckit:<name>` generates a document whose diagram is ArchiMate-representable
- **THEN** the command produces that diagram with PlantUML ArchiMate and a self-contained `.svg`, without creating a new architecture document file

#### Scenario: existing command behaviour is unchanged for non-ArchiMate diagrams
- **WHEN** a command generates a document whose diagrams are not ArchiMate-representable
- **THEN** the command produces them with its existing mechanism and behaviour, unchanged
