## 1. Policy (reference)

- [x] 1.1 Add an "ArchiMate Diagram Production Policy" section to `plugins/arckit-claude/skills/plantuml-syntax/references/archimate.md` stating: (a) use PlantUML ArchiMate when a diagram is ArchiMate-representable or when an ArchiMate diagram should be added; (b) a short "representable vs not" heuristic (layer/capability/service/component/motivation ⇒ yes; sequence/ER/gantt/timeline ⇒ no); (c) PlantUML source inline, `.svg` is the only new emitted file — verify all three points are present and the heuristic is explicit
- [x] 1.2 Document the offline self-contained SVG render step in the same reference (pinned PlantUML build, `java -jar <pinned-jar>` re-render, self-containment expectation: no external URLs, offline-openable) — verify the offline render + self-containment expectations are present and reference the pinned build already declared in the Pinned API section

## 2. Command pointer

- [x] 2.1 Add a one-line pointer to the policy from the document-generating commands that embed ArchiMate-representable diagrams (at least `commands/archimate.md` and `commands/diagram.md`), so commands apply it at generation time — verify the pointer links to `skills/plantuml-syntax/references/archimate.md`
- [x] 2.2 Confirm no existing command's non-ArchiMate diagram behaviour is altered by the pointer — verify the pointer is additive (production policy + svg-only output) and does not change Mermaid/C4 output

## 3. Gate / verification

- [x] 3.1 Add a quality-gate / review criterion: "ArchiMate-representable diagram is produced with PlantUML ArchiMate, its `.svg` is self-contained, and no new architecture document file was created (only `.svg`)" — verify the criterion exists with a PASS/FAIL slot
- [x] 3.2 Add a guard test asserting self-containment of emitted ArchiMate SVGs (no `https?://` beyond W3C namespace declarations; `xlink:href` limited to local `#anchors`) — verify `pytest` on the guard passes

## 4. Propagation

- [x] 4.1 Run `python scripts/converter.py` to propagate any command/reference edits to `extensions/*` and re-run the relevant `tests/plugin` + markdownlint subset (`SKIP_NETWORK=1 ./scripts/ci-local.sh` if available) — verify they pass
