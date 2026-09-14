# artifact-generation Delta — archimate-svg-rendering-adm-oaa

## ADDED Requirements

### Requirement: ADM/OAA ArchiMate Views Are Rendered to Self-Contained SVGs
Because PlantUML does not render in GitHub markdown, every PlantUML-ArchiMate view carried by an artefact of the distribution source plugins `arckit-togaf-adm` and `arckit-oaa` — the **17 demanded base views** plus the **4 Batch-1 companion views** (Implementation & Migration for `transition-architecture` + `gap-analysis`; Physical for `technology-architecture` + `oaa-adm-lite`) — SHALL be delivered as a rendered **self-contained `.svg`**, consistent with the core `archimate-svg-delivery` policy. Each matching command directive SHALL instruct: (1) render the view offline with the pinned build (`java -jar plantuml-1.2026.8.jar -tsvg`, no public server and no URL-include path); (2) keep the inline PlantUML ArchiMate source in the artefact as the source of truth and emit the `.svg` as the **only new rendered file** for the view (no new architecture document file is created to host it); (3) verify self-containment before delivery (no `http(s)` URL other than the W3C `2000/svg` / `1999/xlink` namespace declarations, `xlink:href` limited to local `#anchors`, fully offline-openable); and (4) reference § Diagram Production Policy + § Offline Self-Contained SVG Rendering in `skills/plantuml-syntax/references/archimate.md`. Each affected template SHALL carry a delivery note stating the view is shipped as a rendered self-contained `.svg` with the inline source as source of truth. This SHALL be append-only / additive and SHALL byte-preserve every existing Mermaid block.

#### Scenario: a base view is delivered as a rendered SVG
- **WHEN** the user runs `/arckit:data-architecture` (or any of the 17 base-view commands) and the artefact's ArchiMate base view is ArchiMate-representable
- **THEN** the artefact carries the inline PlantUML-ArchiMate source (unchanged) AND the directive directs rendering that source to a self-contained `.svg` (pinned build, offline, no external URLs), with the `.svg` as the only new rendered file

#### Scenario: a companion view is also rendered to SVG
- **WHEN** the user runs `/arckit:technology-architecture`, which carries a Physical companion view
- **THEN** both the demanded Technology base view AND the Physical companion view are rendered to self-contained `.svg`s, each with its inline PlantUML source retained, and neither creates a new architecture document file

#### Scenario: an SVG self-containment violation is caught before delivery
- **WHEN** a rendered ArchiMate `.svg` would reference a non-W3C `http(s)` URL
- **THEN** the directive's self-containment check fails and the view is not delivered until the SVG is self-contained (offline-openable, local anchors only)
