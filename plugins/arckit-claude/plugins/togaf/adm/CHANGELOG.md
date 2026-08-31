# Changelog

## [Unreleased]

- **Backfill**: document the `discovery` (`DISC`), `data-architecture` (`DATA`), and
  `technology-architecture` (`TECH`) commands added after the 1.0.0 entry
- `togaf-adm-full` now builds DISC/DATA/TECH targets and supports per-phase `{P_<ID>}`
  project placeholders; `togaf-agent-full` composes the ADM cycle with the agent
  architecture lifecycle (requires `arckit-agent-architecture`)
- README updated: 12 commands, full doc-type code list, both recipes
- `togaf-adm-full` post-build hooks now also regenerate the documentation site
  (`arckit:pages`); all three overlay recipes now run the same
  `health` + `traceability` + `pages` post-build sequence

## 1.2.0 (2026-08-13)

- **Split O-AA commands into standalone plugin**: 5 O-AA commands
  (`oaa-adm-lite`, `product-architecture`, `agile-strategy`, `agile-security`,
  `agile-governance`) migrated to `arckit-oaa` plugin. Install `arckit-oaa`
  separately for Open Agile Architecture (C208) support.
- Remaining 9 TOGAF ADM commands unchanged.

## 1.1.0 (2026-08-12)

- **O-AA (Open Agile Architecture) extension**: 5 new agile commands
  - `oaa-adm-lite` — Maps TOGAF ADM to agile sprints (2-4 week engagement windows)
  - `product-architecture` — Product-centric architecture with cross-functional teams
  - `agile-strategy` — Dual transformation canvas (legacy modernization + greenfield innovation)
  - `agile-security` — Security embedded in sprint rhythm (threat modeling, compliance evidence)
  - `agile-governance` — Lightweight governance cadence aligned to sprint cycles
- Shared schema definitions reused across TOGAF and O-AA commands (vision.yaml, implementation-strategy.yaml)
- Cross-command handoffs wired between all O-AA commands
- Existing 9 TOGAF ADM commands unchanged

## 1.0.0 (2026-07-01)

- Initial release
- 9 ADM commands: adm-preliminary, business-capability-map, application-inventory, application-rationalization, gap-analysis, transition-architecture, architecture-board, architecture-change, architecture-repository
- 15 new doc type codes: ADMP, BPCM, APP, APPR, GAPA, TRANS, BORD, ACHG, REPO
- Build recipe: togaf-adm-full
