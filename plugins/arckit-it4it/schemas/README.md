# arckit-it4it Schemas

JSON Schema definitions for the `arckit-it4it` plugin. These are shared,
vendor-neutral structures for IT4IT artefacts. Reference-only — the Open
Group IT4IT Standard v3.1 (Snapshot, S261) is a snapshot, not an approved
standard; no conformance claim is made.

## value-stream.json

One value stream of the IT4IT Value Network (S261 Ch. 5). Used by
`/arckit-it4it:it4it-value-stream` (multi-instance — one per stream).

- **`stream`** — one of the seven S261 streams (Evaluate … Operate)
- **`trigger` / `stakeholder` / `stages`** — the stream's trigger, owner, and
  ordered stage sequence
- **`cross_stream`** — inbound/outbound handoff KDOs and their contracts
- **`system_of_record`** — KDO → authoritative system map

## functional-component.json

A capability unit controlling specific KDOs (S261 Ch. 6–10). Shared across
the four functional-group commands
(`it4it-strategy-portfolio`, `it4it-develop-test`, `it4it-consume-fulfil`,
`it4it-operate-assure`).

- **`function`** — one of the S261 function groups
- **`components`** — in-scope functional components and their primary KDOs
- **`cardinalities`** — KDO relationship cardinalities (deviations recorded
  as `gap`, not choices)
- **`states`** — lifecycle state machines (e.g. proposal states)
- **`quality_gates`** — entry/exit criteria (Develop & Test only)

## Notes

- Schemas describe the **reference data contract**, not tooling. Vendor
  tooling choices (pipeline, catalog, monitoring) are non-normative
  extensions and are recorded in prose, not here.
- `conformance_notes` is required so the rendered artefact states S261 is
  referenced, never claimed as a conformance target.
