# OAA Shared Architecture Schemas

Shared JSON Schemas (draft-07) for the Open Agile Architecture (O-AA)
track. Each OAA command (`oaa-adm-lite`, `agile-strategy`,
`agile-security`, `agile-governance`, `product-architecture`) writes
structured artifacts (vision, strategy canvas, security backlog, and so
on) and validates them against the schema listed in its
"Artifact Validation" section.

## Shipped schemas

| Schema | Validated by |
|---|---|
| `vision.json` | `/arckit:oaa-adm-lite`, `/arckit:product-architecture`, `/arckit:agile-strategy` (Sprint 0 vision) |
| `implementation-strategy.json` | `/arckit:oaa-adm-lite` (Sprint 3 waves) |
| `product-architecture.json` | `/arckit:product-architecture`, `/arckit:agile-strategy` |
| `strategy-canvas.json` | `/arckit:agile-strategy` (canvas) |
| `security-backlog.json` | `/arckit:agile-security` (per-sprint) |
| `threat-model.yaml` | `/arckit:agile-security` (per-sprint STRIDE) |
| `compliance-evidence.json` | `/arckit:agile-security`, `/arckit:agile-governance` (per-sprint) |
| `governance-cadence.json` | `/arckit:agile-governance` (Sprint 4+) |
| `change-request.yaml` | `/arckit:agile-governance`, traditional Architecture Change |

`threat-model.yaml` and `change-request.yaml` are JSON Schemas written
in YAML, matching the schema file names declared in the OAA command
docs; the others are JSON.

## Validation

The validator ships in this plugin root:

```sh
python3 validate-architecture.py vision.yaml --phase vision
python3 validate-architecture.py security-backlog-sprint-1.yaml --phase security
python3 validate-architecture.py threat-model-sprint-1.yaml --phase threats
python3 validate-architecture.py governance-cadence.yaml --phase governance
python3 validate-architecture.py change-request.yaml --phase change
python3 validate-architecture.py strategy-canvas.yaml --phase canvas
python3 validate-architecture.py product-architecture.yaml --phase product
python3 validate-architecture.py implementation-strategy.yaml --phase strategy
python3 validate-architecture.py compliance-evidence-sprint-1.yaml --phase evidence
```

`--schema FILE` validates against an arbitrary schema file instead of a
phase. `drift BASELINE DEPLOYED [--ignore DOTTED.PATH ...]` diffs a
deployed config against a baseline, and `self-test` / `gate` exercise
the built-in validator (used by the local CI gate). The validator is
standard-library only; YAML artifacts and the two YAML schemas need
PyYAML installed.

Exit codes: `0` valid / no drift, `1` invalid / drift / gate failure,
`2` usage error.
