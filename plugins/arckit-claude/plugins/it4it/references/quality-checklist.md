# IT4IT Quality Checklist

Run before writing any `arckit-it4it` artefact. Fix failures before writing.

## Common Checks (all six commands)

- [ ] **Document ID present**: filename and in-document ID use the correct
      doc-type code (`ITVN`, `ITVS`, `ITSF`, `ITDT`, `ITCF`, `ITOA`) and
      version (`v1.0` first, `v2.0`+ on re-run).
- [ ] **PRIN gate passed**: the MANDATORY Architecture Principles artefact
      (in `000-global`) was read and its principles/governance/investment
      posture extracted. If absent, the command must have stopped.
- [ ] **Conformance phrasing**: the artefact references S261 as a reference
      architecture; no conformance claim is made. The Conformance Notes
      section states S261 is a snapshot, not an approved standard.
- [ ] **Multi-instance (ITVS only)**: one artefact per value stream,
      sequence-numbered `ARC-{P}-ITVS-{NNN}-v1.0.md`.
- [ ] **Product-based posture**: funding units are Portfolio Backlog Items,
      not projects. Project-based gaps are flagged explicitly.
- [ ] **Systems of record**: every handoff KDO names its authoritative system.
- [ ] **Cardinality recorded**: KDO cardinalities are recorded per the S261
      catalog; deviations are recorded as gaps.
- [ ] **Markdown escaping**: `<` / `>` comparisons have a trailing space
      (e.g. `< 3 seconds`, `> 99.9% uptime`).
- [ ] **Template chosen**: user-customised template in
      `.arckit/templates-custom/` takes precedence over the default.
- [ ] **Version bump**: if an artefact of the same doc-type already exists,
      a new version is created rather than overwriting.

## Value-Network-Specific Checks

- [ ] All seven value streams are present (or explicitly marked out of scope).
- [ ] Every cross-stream dependency names source, target, handoff KDO, and
      contract (cardinality + system of record).
- [ ] The Digital Product backbone and Service Offering backbone KDOs are
      positioned per stream.
- [ ] The Operate → Evaluate feedback loop is recorded.

## Functional-Group-Specific Checks

- [ ] Each functional component lists its primary KDOs.
- [ ] State machines (e.g. proposal states) are explicit.
- [ ] Quality gates (Develop & Test) name entry/exit criteria per gate.
- [ ] Runbooks (Operate & Assure) name their remediation boundary.
