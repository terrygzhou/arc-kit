# ArcKit: The Enterprise Architecture Governance Harness

[![GitHub Stars](https://img.shields.io/github/stars/tractorjuice/arc-kit?style=flat&logo=github)](https://github.com/tractorjuice/arc-kit/stargazers)
[![License: MIT](https://img.shields.io/github/license/tractorjuice/arc-kit)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/terrygzhou/arc-kit)](https://github.com/terrygzhou/arc-kit/releases)

**Build better enterprise architecture through structured strategy, design, delivery, and assurance workflows.**

ArcKit is a toolkit for enterprise architects that transforms architecture governance from scattered documents into a systematic, AI-assisted workflow for principles, stakeholder analysis, risk management, business cases, requirements, data modeling, technology research, strategic planning, vendor procurement, design reviews, and compliance.

## Quick Start

### Installation

**Claude Code** (premier experience — install plugin, requires **v2.1.172+**):

```bash
claude install latest
# In Claude Code:
/plugin marketplace add tractorjuice/arckit-claude
```

Install overlays as needed:
```bash
# Core (75 commands — UK Government + generic enterprise)
claude plugin install arckit@arckit-claude
# Regional + sector overlays
claude plugin install arckit arckit-{uae,fr,ca,eu,at,au,us,uk-nhs,uk-gcloud}
# Enterprise architecture + AI agent governance
claude plugin install arckit arckit-togaf-adm arckit-agent-architecture
```

**CLI** (Copilot, Codex, OpenCode):
```bash
pipx install arckit-cli  # or: uv tool install arckit-cli
arckit init my-project --ai copilot  # or --ai codex / --ai opencode
```

**Gemini CLI**:
```bash
gemini extensions install https://github.com/tractorjuice/arckit-gemini
```

**One-liner** (auto-detects pipx → uv → pip --user):
```bash
curl -fsSL https://raw.githubusercontent.com/terrygzhou/arc-kit/main/install.sh | bash
```

**Latest Release**: [v6.2.1](https://github.com/terrygzhou/arc-kit/releases/tag/v6.2.1)

### Initialize a Project

```bash
# Claude Code / Gemini: no init needed — plugins/extensions provide everything
arckit init my-project --ai copilot  # or --ai codex / --ai opencode
cd my-project && code .  # then use /arckit-* commands in Copilot Chat
```

### Upgrading

```bash
# CLI: upgrade tool + re-init project
pipx upgrade arckit-cli
cd /path/to/project && arckit init --here --ai copilot
# Claude Code: automatic via marketplace
# Gemini: gemini extensions update arckit
```

### CLI Build

Run a full recipe-driven ADM cycle from the terminal:

```bash
arckit build my-project --recipe togaf-adm-full
```

Interactive wave prompts will capture `{P}`, `{NAME}`, `{DISC_SCOPE}`, and per-phase overrides. Subsequent runs resume from the last wave:

```bash
arckit build my-project --recipe togaf-adm-full --resume
```

Key flags:

| Flag | Purpose |
|------|---------|
| `--recipe <name>` | Recipe name or YAML path (default: `togaf-adm-full`) |
| `--plan` | Dry run — print wave plan, do not execute |
| `--resume` | Resume from last incomplete wave |
| `--target <ID>` | Build only this target and its dependencies |
| `--refresh <ID>` | Force-rebuild this target and downstream |
| `--parallel N` | Max concurrent LLM calls per wave (default: 4) |
| `--no-commit` | Skip per-wave git commits |
| `--base-url URL` | Override LLM base URL |
| `--model NAME` | Override LLM model |

Placeholder inheritance: `{P}` is captured once at the ADMP wave; each phase gets `{P_<ID>}` auto-derived (e.g. `{P_BPCM}` → `"{P}-BPCM"`) and can be overridden independently.

---

## Platform Support

| Platform | Claude Code | Gemini CLI | Copilot | Codex/OpenCode | Vibe |
|----------|------------|-----------|---------|----------------|------|
| macOS | ✅ | ✅ | ✅ | ✅ | ✅ |
| Linux | ✅ | ✅ | ✅ | ✅ | ✅ |
| Windows (WSL2) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Windows (native) | ✅ | ✅ | ✅ | Partial | ✅ |

---

## OKF Interoperability

ArcKit can exchange Markdown knowledge bundles using an Open Knowledge Format layer:
- `/arckit:export-okf` — copy ARC artifacts to OKF bundle with metadata
- `/arckit:import-okf` — import OKF bundle, materialise as RSCH review notes
- Enable source frontmatter: `ARCKIT_OKF_FRONTMATTER=1`

---

## The ArcKit Workflow

ArcKit guides you through the enterprise architecture lifecycle:

### Phase 0-4: Foundation & Strategy
| Command | Purpose |
|---------|---------|
| `/arckit:plan` | Project plan with timeline, phases, gates, Mermaid diagrams |
| `/arckit:principles` | Enterprise architecture principles (cloud, security, tech standards) |
| `/arckit:stakeholders` | Stakeholder drivers, goals, and measurable outcomes |
| `/arckit:risk` | Risk register (HM Treasury Orange Book) — 6 categories, 4Ts response |
| `/arckit:sobc` | Strategic Outline Business Case (Green Book 5-case model) |

### Phase 5: Requirements & Data
| Command | Purpose |
|---------|---------|
| `/arckit:requirements` | Comprehensive requirements with acceptance criteria |
| `/arckit:platform-design` | Multi-sided platform strategy (8 canvases) |
| `/arckit:data-model` | Data model with ERD, GDPR compliance, data governance |
| `/arckit:dpia` | Data Protection Impact Assessment (UK GDPR Article 35) |
| `/arckit:datascout` | External data source discovery and evaluation |

### Phase 6-7: Research & Strategy
| Command | Purpose |
|---------|---------|
| `/arckit:research` | Technology research with build vs buy analysis |
| `/arckit:grants` | UK government grants, funding, and accelerator programmes |
| `/arckit:wardley` | Strategic Wardley Maps for architecture decisions |
| `/arckit:roadmap` | Multi-year architecture roadmap with governance |
| `/arckit:strategy` | Executive-level Architecture Strategy synthesis |
| `/arckit:adr` | Architecture Decision Records (MADR v4.0) |

### Phase 8-10: Procurement, Design, Delivery
| Command | Purpose |
|---------|---------|
| `/arckit:sow` | Statement of Work / RFP document |
| `/arckit:dos` | Digital Outcomes and Specialists procurement 🇬🇧 |
| `/arckit:gcloud-search` | G-Cloud service search with live marketplace 🇬🇧 |
| `/arckit:gcloud-clarify` | G-Cloud gap analysis and supplier clarification 🇬🇧 |
| `/arckit:evaluate` | Vendor evaluation framework and scoring |
| `/arckit:hld-review` | High-Level Design review |
| `/arckit:dld-review` | Detailed Design review |
| `/arckit:backlog` | Prioritised product backlog with sprint planning |
| `/arckit:trello` | Export backlog to Trello |
| `/arckit:servicenow` | ServiceNow service management design |

### Phase 12-16: Traceability, Quality, Publishing
| Command | Purpose |
|---------|---------|
| `/arckit:traceability` | Requirements traceability matrix |
| `/arckit:analyze` | Comprehensive governance quality analysis |
| `/arckit:story` | Project story with timeline and governance achievements |
| `/arckit:presentation` | MARP slide deck from project artifacts |
| `/arckit:pages` | Documentation site with Mermaid rendering |

---

## Plugin Overlays

### TOGAF ADM (`arckit-togaf-adm`) [COMMUNITY]

Enterprise Architecture Development Method — 12 commands (10 required + 2 optional) covering the full ADM cycle:

| Command | Phase | Description |
|---------|-------|-------------|
| `/arckit:discovery` | DISC | Current-state baseline (business context, capabilities, applications, data, technology, constraints) |
| `/arckit:adm-preliminary` | Preliminary | Architecture vision, scope, drivers |
| `/arckit:business-capability-map` | Phase A | Business capability hierarchy |
| `/arckit:application-inventory` | Phase B | Application catalog with strategic fit |
| `/arckit:data-architecture` | Phase C.2 | Data entities, governance, reference/master data |
| `/arckit:technology-architecture` | Phase D | Technology stack, platforms, infrastructure |
| `/arckit:application-rationalization` | Phase C | Keep/merge/replace/retire decisions |
| `/arckit:gap-analysis` | Phase E | Current vs target gap matrix |
| `/arckit:transition-architecture` | Phase F | Work packages, migration waves |
| `/arckit:architecture-board` | Phase G | Board charter, compliance scorecard |
| `/arckit:architecture-change` | Phase H | Change requests, ADM re-entry _(optional)_ |
| `/arckit:architecture-repository` | Repository | Patterns, standards, reference architectures _(optional)_ |

Install: `claude plugin install arckit arckit-togaf-adm`

### AI Agent Architecture (`arckit-agent-architecture`) [COMMUNITY]

6 commands for autonomous AI agent governance, design, and security:

| Command | Description |
|---------|-------------|
| `/arckit:agent-inventory` | Agent catalog with capabilities, security classification |
| `/arckit:agent-design` | Agent architecture spec — patterns, tools, memory |
| `/arckit:agent-governance` | Oversight models, approval workflows, audit |
| `/arckit:agent-integration` | Multi-agent orchestration, contracts |
| `/arckit:agent-security` | Sandboxing, permissions, injection defences |
| `/arckit:agent-maturity` | 5×5 maturity model for agent programs |

Install: `claude plugin install arckit arckit-agent-architecture`
Combined recipe: `claude agent recipes/togaf-agent-full.yaml`

### UAE Federal (`arckit-uae`)

AI governance (Charter, Autonomy Tiers), procurement (Federal Decree-Law 11/2023), and cloud residency. Commands chain from principles through procurement.

### G-Cloud Bid Authoring (`arckit-uk-gcloud`) [PROPRIETARY]

10 commands for UK Government supplier bid authoring: supplier profile, service design, SDD lots, declaration, pricing, security, competitor benchmark, review, and submission pack.
Install: `claude plugin install arckit arckit-uk-gcloud`

### EU & French Government (`arckit-fr`, `arckit-eu`)

17 commands covering GDPR, EU AI Act, NIS2, DORA, CRA, DSA, Data Act, ANSSI hygiene, SecNumCloud, EBIOS Risk Manager, French public procurement, and algorithm transparency.

---

## Why ArcKit?

**Problem**: Traditional enterprise architecture suffers from scattered documents, inconsistent governance, manual vendor evaluation, lost traceability, and stale documentation.

**Solution**: Template-driven quality, systematic workflows, AI assistance, enforced traceability, and Git-based version control.

---

## Supported AI Assistants

| Assistant | Support | Notes |
|-----------|---------|-------|
| [Claude Code](https://www.anthropic.com/claude-code) | ✅ Premier | Primary platform — plugin with agents, hooks, MCP servers |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | ✅ Full | Extension with commands and MCP servers |
| [GitHub Copilot](https://github.com/features/copilot) | ✅ Core | Prompt files, custom agents, repo-wide instructions |
| [OpenAI Codex CLI](https://chatgpt.com/features/codex) | ✅ Core | CLI with commands and templates |
| [OpenCode CLI](https://opencode.net/cli) | ✅ Core | CLI with commands and templates |

Claude Code provides unique capabilities: parallel `/arckit:build` harness, autonomous research agents (10 agents), session hooks (auto-detect, context injection, filename correction, MCP auto-allow), and per-command stop hooks (output validation).

---

## Project Structure

```text
my-project/
├── .arckit/
│   ├── scripts/          # Automation scripts
│   ├── templates/        # Default templates (refreshed by arckit init)
│   └── templates-custom/ # Your customizations (preserved)
├── projects/
│   ├── 000-global/       # Global principles
│   └── 001-project/      # Project artifacts (ARC-NNN-TYPE-vN.N.md)
├── .agents/skills/       # Codex CLI skills
├── .codex/               # Codex agents + config
├── .github/              # Copilot prompts + agents
└── .opencode/            # OpenCode commands
```

---

## Plugin Footprint

- **Always-on per session**: ~10,042 tokens (73 command-skills + 5 utility skills + 16 agents)
- **On-invoke**: ~250 to ~60K tokens per command (most 5–10K range)
- Utility skills use `paths:` globs to scope always-on cost to relevant projects
- Community overlays add their own always-on baseline — install only what you need

---

## Token Limit Troubleshooting

If you see: `API Error: Claude's response exceeded the 32000 output token maximum`

- **Team/Enterprise plans**: `export CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000`
- **All plans**: Use Write tool strategy — `/arckit:requirements but write directly to file using Write tool, show me only a summary`
- High-risk commands: `/arckit:sobc`, `/arckit:requirements`, `/arckit:data-model`, `/arckit:sow`
- Research commands run as autonomous agents (separate context windows)

See full guide: [docs/TOKEN-LIMITS.md](docs/TOKEN-LIMITS.md)

---

## Documentation

- Lifecycle visuals: [docs/WORKFLOW-DIAGRAMS.md](docs/WORKFLOW-DIAGRAMS.md), [docs/DEPENDENCY-MATRIX.md](docs/DEPENDENCY-MATRIX.md)
- Core guides: [docs/guides/principles.md](docs/guides/principles.md), [docs/guides/requirements.md](docs/guides/requirements.md), [docs/guides/procurement.md](docs/guides/procurement.md), [docs/guides/design-review.md](docs/guides/design-review.md)
- Traceability: [docs/guides/traceability.md](docs/guides/traceability.md)
- DDaT Role Guides: [docs/guides/roles/](docs/guides/roles/) — 18 guides mapping commands to UK DDaT roles

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

**Priority areas**: Enterprise tool integrations (Jira, Azure DevOps), additional AI agent support, template improvements, documentation, ServiceNow API integration.

---

## Support & License

- **Issues**: [GitHub Issues](https://github.com/tractorjuice/arc-kit/issues)
- **Releases**: [GitHub Releases](https://github.com/tractorjuice/arc-kit/releases)
- **Latest**: [v6.2.1](https://github.com/tractorjuice/arc-kit/releases/tag/v6.2.1)

MIT License — see [LICENSE](LICENSE).
> **Exception:** `plugins/arckit-uk-gcloud/` is proprietary (not MIT).

<p align="center">
  <strong>Built with ❤️ for enterprise architects who want systematic, AI-assisted governance.</strong>
</p>