## Why

ArcKit's document-generating slash commands keep working as they do today, but their embedded diagrams default to Mermaid / C4. Where a diagram **can be represented in the ArchiMate metamodel** — or where an **additional ArchiMate view should be added** to a document — it should be produced with **PlantUML ArchiMate**, rendered to a self-contained SVG, rather than with Mermaid. This has to happen *without* churning the existing artifacts and *without* spawning new architecture documents.

## What Changes

- **ArchiMate production policy (additive, non-breaking):** when a command generates a document, if a diagram in it can be represented in ArchiMate, or an additional ArchiMate diagram should be added, that diagram SHALL be produced with **PlantUML ArchiMate** notation (pinned `!include <archimate/Archimate>` stdlib) and rendered to a **self-contained SVG**.
- **Output constraint:** this work SHALL NOT create new architecture *document* files for a diagram. The ArchiMate PlantUML source is carried **inline** in the document being generated, and the **only new file emitted is the rendered `.svg`**.
- **Existing behaviour unchanged:** every command continues to generate documents and its non-ArchiMate diagrams (sequence, ER, gantt, timeline, C4, Mermaid flowcharts, …) exactly as before; the policy only governs ArchiMate-representable diagrams.

No **BREAKING** changes: nothing existing is modified or removed; the policy only redirects ArchiMate-representable diagrams onto PlantUML ArchiMate and constrains new outputs to `.svg`.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `artifact-generation`: adds an **ArchiMate Diagram Production Policy** requirement — use PlantUML ArchiMate when a diagram is ArchiMate-representable or when adding an ArchiMate diagram; render to a **self-contained SVG**; do not create new architecture document files (inline source, `.svg` is the only new emitted file); the SVG self-containment rule.
- `slash-commands`: adds a **Commands Follow The ArchiMate Diagram Production Policy** requirement — every document-generating command applies the policy, and otherwise keeps its existing document/diagram behaviour unchanged.

## Impact

- A generation-time policy, enforced by review / quality-gate (a new criterion), not by a hard filename gate — "ArchiMate-representable" is an architect judgment, not something a filename check can decide.
- No new doc-type; no new architecture document files; the only new rendered output is `.svg` (plus the inline PlantUML source in the document).
- No changes to existing artifacts. Non-ArchiMate diagram generation is untouched.
