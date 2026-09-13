# artifact-generation (delta)

## ADDED Requirements

### Requirement: ArchiMate Diagram Production Policy
When a command generates a document, if a diagram in that document can be represented using the ArchiMate metamodel, or if an additional ArchiMate diagram should be added to the document, that diagram SHALL be produced using **PlantUML ArchiMate** notation (the pinned `!include <archimate/Archimate>` standard library) and rendered to a **self-contained SVG**. Diagrams that cannot be represented in ArchiMate SHALL be produced by their existing mechanism unchanged; this policy governs only ArchiMate-representable diagrams.

This production work SHALL NOT create new architecture *document* files for a diagram. The ArchiMate PlantUML source SHALL be carried inline within the document being generated, and the **only new file emitted SHALL be the rendered `.svg`**.

#### Scenario: an ArchiMate-representable diagram is produced with PlantUML
- **WHEN** a command generates a document that contains a diagram that can be expressed as an ArchiMate layer view
- **THEN** that diagram is produced with PlantUML ArchiMate notation and rendered to a self-contained `.svg`, with the PlantUML source carried inline in the document

#### Scenario: no new architecture document files are created
- **WHEN** an ArchiMate diagram is produced for a document
- **THEN** no new `ARC-*.md` (or other architecture document) file is created for it, the PlantUML source is inline in the document, and the only new file emitted is the `.svg`

#### Scenario: a non-ArchiMate diagram is left to its existing mechanism
- **WHEN** a diagram in a generated document cannot be represented in ArchiMate (e.g., a sequence, ER, gantt, or timeline diagram)
- **THEN** it is produced by the document's existing mechanism (e.g., Mermaid / C4) unchanged, and this policy does not force it into ArchiMate

### Requirement: ArchiMate SVG Is Self-Contained
The `.svg` rendered for an ArchiMate diagram SHALL be self-contained: it SHALL open offline in any browser with no network fetch, and SHALL contain no `http(s)` URL other than W3C XML namespace declarations, with all `xlink:href` references limited to local `#anchors` within the same file.

#### Scenario: the SVG opens offline
- **WHEN** a rendered ArchiMate `.svg` is opened offline in a browser
- **THEN** it renders without any network request, and the file contains no external `http(s)` URLs beyond W3C namespace declarations, with `xlink:href` values limited to local `#anchors`
