# ArcKit: The Enterprise Architecture Governance Harness

**Build better enterprise architecture through structured strategy, design, delivery, and assurance workflows.**

ArcKit is a toolkit for enterprise architects that transforms architecture governance from scattered documents into a systematic, AI-assisted workflow for:

- 🏛️ Establishing and enforcing architecture principles
- 👥 Analyzing stakeholder drivers, goals, and outcomes
- 🛡️ Risk management (HM Treasury Orange Book)
- 💼 Business case justification (HM Treasury Green Book SOBC)
- 📋 Creating comprehensive requirements documents
- 🗄️ Data modeling with ERD, GDPR compliance, and data governance
- 🔬 Technology research with build vs buy analysis (web search powered)
- ☁️ Azure-specific research using Microsoft Learn MCP for authoritative documentation
- 🗺️ Strategic planning with Wardley Mapping
- 📊 Generating visual architecture diagrams (Mermaid)
- 🤝 Managing vendor RFP and selection processes
- ✅ Conducting formal design reviews (HLD/DLD)
- 🔧 ServiceNow service management design
- 🔗 Maintaining requirements traceability
- 📎 Citation traceability for external documents (inline `[DOC-CN]` markers with source quotes)

---

## Quick Start


Three ways to run ArcKit - pick the one that fits your workflow:

1. **Claude Code plugin** - the premier experience: 75 core commands, 16 marketplace plugins, autonomous research agents, automation hooks, bundled MCP servers, automatic updates.
2. **Codex CLI** - scaffold a project with `arckit init --ai codex`, then drive ArcKit skills inside Codex.
3. **Bring Your Own LLM** - run `arckit build` recipes against any local or remote OpenAI-compatible endpoint.

### Claude Code

Claude Code is the **primary development platform** for ArcKit: all official commands, autonomous research agents, automation hooks, bundled MCP servers (AWS Knowledge, Microsoft Learn, Google Developer Knowledge, Data Commons, govreposcrape, uk-tenders), and automatic updates via the marketplace. Requires Claude Code **v2.1.219+**.

```bash
# Make sure Claude Code is on the latest version
claude install latest
```

Then in Claude Code, add the ArcKit marketplace:

```text
/plugin marketplace add terrygzhou/arc-kit
```

The marketplace ships **17 plugins** - install the core plus only the overlays you need:

```bash
# Core (75 commands - UK Government civilian + generic enterprise)
claude plugin install arckit@arc-kit

# Core + UAE federal
claude plugin install arckit arckit-uae

# Broad overlay set (UK + UAE + FR + CA + EU + AT + AU + US + UK-NHS + UK-GCloud)
claude plugin install arckit arckit-{uae,fr,ca,eu,at,au,us,uk-nhs,uk-gcloud}

# Enterprise architecture and AI agent governance overlays
claude plugin install arckit arckit-togaf-adm arckit-oaa arckit-agent-architecture
```

The `terrygzhou/arc-kit` marketplace hosts all Claude Code plugins: the `arckit` core plugin, regional overlays, sector overlays, the TOGAF ADM, O-AA (Open Agile Architecture), and AI agent architecture overlays, the `arckit-fde` tooling plugin, and the public-but-proprietary `arckit-uk-gcloud` supplier overlay. The 14 community plugins (`arckit-uae`, `arckit-fr`, `arckit-ca`, `arckit-eu`, `arckit-at`, `arckit-au`, `arckit-au-energy`, `arckit-us`, `arckit-uk-finance`, `arckit-uk-nhs`, `arckit-uk-gcloud`, `arckit-togaf-adm`, `arckit-oaa`, `arckit-agent-architecture`) require the `arckit` core plugin. `arckit-au-energy` (sector) additionally requires `arckit-au` (jurisdiction), which it composes — install with `claude plugin install arckit arckit-au arckit-au-energy`. `arckit-uk-gcloud` is a **proprietary, Claude Code only** supplier-side G-Cloud bid-authoring overlay — it is public for installation and inspection, but not MIT licensed and not distributed to the non-Claude extension formats. One **tooling plugin** — `arckit-fde` — is a lean, Claude Code only plugin with one command, `/arckit-fde:create`, that generates a brandable (white-label) Forward Deploy Engineering consulting website into `docs/` (GitHub Pages ready), with UK Public Sector and Generic market presets; no dependencies, not converted to non-Claude formats, no governance doc-types.

No project initialization is needed - the plugin provides everything. Use the commands directly:

```text
/arckit:principles Create principles for a financial services company
/arckit:requirements Build a payment processing system...
/arckit:sow Generate RFP for vendor selection
```

Updates are automatic via the marketplace - no action needed.

> **Why v2.1.219?** v2.1.219 adds **Claude Opus 5** (`claude-opus-5`), the current default Opus model, with 1M context and fast mode support — earlier clients cannot select it. The floor also carries v2.1.200's fix for project-scoped plugin loading from git worktrees and `claude agents --plugin-dir <dir>` visibility for plugin agents/skills, which makes ArcKit's branch and test-repo workflows reliable. It also carries the v2.1.198-v2.1.199 background-subagent reliability, parent error-propagation, and hook stderr-visibility fixes that matter to `/arckit:build`, reader/writer handoffs, and hook diagnosis. v2.1.197 makes Claude Sonnet 5 the default Claude Code model with native 1M context, while v2.1.172 fixed wildcard-domain `WebFetch` permission rules (`WebFetch(domain:*.gov.uk)`) that never matched subdomains on earlier clients — the exact shape ArcKit recommends for confining research-agent traffic in OFFICIAL-SENSITIVE deployments. The floor also carries forward the v2.1.156 Opus 4.8 thinking-block fix, v2.1.154 plugin `defaultEnabled: false`, v2.1.144 session-title and headless Skill tool fixes, v2.1.143 plugin dependency enforcement, v2.1.139 hook `args: string[]`, v2.1.129 monitor layout and prompt-cache fixes, v2.1.121 MCP/provenance hook unlocks, v2.1.118-v2.1.119 release/telemetry unlocks, and the earlier `/context`, Auto mode, plugin update, MCP leak, retry, and subagent working-directory fixes.

### Codex CLI

Install the ArcKit CLI:

```bash
# Install with pip
pip install git+https://github.com/terrygzhou/arc-kit.git

# Or with uv
uv tool install arckit-cli --from git+https://github.com/terrygzhou/arc-kit.git

# Or run without installing
uvx --from git+https://github.com/terrygzhou/arc-kit.git arckit init my-project
```

Scaffold a project - this creates `.agents/skills/` (auto-discovered by Codex), `.codex/agents/`, `.codex/hooks/`, `.codex/config.toml` (MCP servers + hook wiring), `.arckit/templates/`, and helper scripts:

```bash
# Create a new architecture governance project
arckit init payment-modernization --ai codex

# Minimal install (skip docs and guides)
arckit init payment-modernization --ai codex --minimal

# Or initialize in the current directory
arckit init . --ai codex
```

Start Codex and use the ArcKit skills:

```bash
cd payment-modernization
codex
```

```text
/arckit:principles Create principles for a financial services company
/arckit:requirements Build a payment processing system...
/arckit:sow Generate RFP for vendor selection
```

**Upgrading** - upgrade the CLI, then re-run `init` in place:

```bash
# Step 1: Upgrade the CLI tool
pip install --upgrade git+https://github.com/terrygzhou/arc-kit.git
# Or with uv:
uv tool upgrade arckit-cli --from git+https://github.com/terrygzhou/arc-kit.git

# Step 2: Update your existing project (re-run init in place)
cd /path/to/your-existing-project
arckit init --here --ai codex
```

This updates commands, templates, scripts, and agents while **preserving** your project data (`projects/`) and custom templates (`.arckit/templates-custom/`).

If upgrading from v0.x, you may also need to migrate legacy filenames - see the [upgrading guide](docs/guides/upgrading.md) for full details.

### Bring Your Own LLM

Run `arckit build` against any local or remote OpenAI-compatible endpoint:

```bash
# One-shot via flags (trailing /v1 is auto-stripped)
arckit build my-project --base-url http://127.0.0.1:8080 --model Qwen3.6-27B

# Persistent config (arckit config)
arckit config set llm.base_url http://127.0.0.1:8080
arckit config set llm.model Qwen3.6-27B
```

**Presets** — `arckit local setup` includes a wizard with common local endpoints (Ollama, SGLang, vLLM). SGLang on port 8080 is a built-in preset.

**Retry behaviour** — failed LLM calls retry with exponential backoff (2s → 4s → 8s) before failing the wave. Configure via `--base-url` and `--model` per-build, or persist via `arckit config`.

### OKF Interoperability

ArcKit can exchange Markdown knowledge bundles using an Open Knowledge Format-shaped frontmatter layer:

- `/arckit:export-okf` copies ArcKit `ARC-*.md` artifacts into an OKF bundle with portable `type`, `title`, `resource`, `tags`, `timestamp`, and `arckit` metadata.
- `/arckit:import-okf` scans an OKF bundle, writes `.arckit/tmp/okf-import-report.json`, and materializes safe imports as `RSCH` review notes by default.
- Native ArcKit files remain unchanged unless you explicitly enable source frontmatter stamping with `ARCKIT_OKF_FRONTMATTER=1` or `.arckit/config.json` containing `{ "okfFrontmatter": true }`.

### Platform Support

| Platform | Claude Code Plugin | GitHub Copilot | Codex / OpenCode CLI | Mistral Vibe | Kimi Code CLI |
|----------|-------------------|----------------|---------------------|--------------|----------------|
| macOS | Full support | Full support | Full support | Full support | Full support |
| Linux | Full support | Full support | Full support | Full support | Full support |
| Windows (WSL2) | Full support | Full support | Full support | Full support | Full support |
| Windows (native) | Full support | Full support | Partial | Full support | Full support |

**Windows users**: The Claude Code plugin, GitHub Copilot prompt files, Mistral Vibe extension, and Kimi Code CLI extension work natively on all platforms. For Codex CLI / OpenCode CLI on native Windows (without WSL), some commands containing inline bash snippets may require [Git Bash](https://git-scm.com/downloads/win) or [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install). We recommend WSL2 for the best experience.

---

## What it costs (plugin footprint)

Token cost of installing the `arckit` core plugin in a Claude Code session, captured from `claude plugin details arckit` on v2.1.143+:

- **Always-on per session: ~10,042 tokens** — added to every session's system context, covering the 75 command-skills + 5 utility skills (`architecture-workflow`, `arckit-build`, `mermaid-syntax`, `plantuml-syntax`, `wardley-mapping`) + 19 agent descriptors. Hooks (10 events) and MCP servers (6) are harness-resolved at runtime and not counted.
- **On-invoke: ~250 to ~60K tokens per command** — paid only when a specific skill or agent fires. Most commands are in the 5–10K range.

### On-invoke cost by command

Costs are estimates from the Claude Code tokenizer and may differ from actual usage. Use this table to budget research-heavy multi-command sessions.

| Tier | Range | Commands |
|------|-------|----------|
| Lightweight | <2K | `start`, `init`, `build`, `search`, `impact`, `navigator`, `graph-report`, `framework`, `gov-landscape`, `aws-research`, `azure-research`, `gcp-research` |
| Standard | 2–7K | `customize`, `score`, `principles`, `mermaid-syntax`, `plantuml-syntax`, `architecture-workflow`, `datascout`, `tenders`, `competitors`, `evaluate`, `hld-review`, `mlops`, `devops`, `finops`, `research`, `tcop`, `wardley-mapping`, `template-builder`, `glossary`, `dld-review`, `traceability`, `stakeholders`, `presentation`, `dfd`, `operationalize`, `requirements`, `maturity-model`, `data-model`, `gov-reuse`, `strategy`, `presentation`, `atrs`, `gov-code-search`, `READER-PATTERN` |
| Heavy | 7–15K | `wardley.value-chain`, `gcloud-clarify`, `ai-playbook`, `sow`, `sobc`, `risk`, `secure`, `dpia`, `dos`, `mod-secure`, `plan`, `conformance`, `roadmap`, `health`, `wardley.doctrine`, `wardley.gameplay`, `pages`, `servicenow`, `gcloud-search`, `principles-compliance`, `story`, `wardley`, `wardley.climate`, `data-mesh-contract`, `platform-design`, `adr`, `arckit-build`, `grants` |
| Research-heavy | 15–25K | `service-assessment`, `analyze`, `backlog`, `diagram` |
| Specialist | >25K | `jsp-936` (~60K — MOD JSP 936 AI assurance, defence-only) |

### Trimming the footprint

- The five utility skills already use `paths:` globs to scope their always-on cost to relevant projects (`mermaid-syntax` only loads under `*.mmd`, `wardley-mapping` under WARD artefacts, etc.). The 75 command-skills are listed but not described in detail in the always-on context — the full prompt only loads on invocation.
- Community overlays (`arckit-uae`, `arckit-fr`, `arckit-ca`, `arckit-eu`, `arckit-at`, `arckit-au`, `arckit-au-energy`, `arckit-us`, `arckit-uk-finance`, `arckit-uk-nhs`, `arckit-togaf-adm`, `arckit-oaa`, `arckit-agent-architecture`) are independent plugins — install only the jurisdictions / sectors you need. Each adds its own always-on baseline. `arckit-uk-finance`, `arckit-uk-nhs`, and `arckit-au-energy` are **sector** overlays (`arckit-au-energy` layers the energy sector on the `arckit-au` jurisdiction baseline); the rest are jurisdiction-based.
- Heavy commands (`jsp-936`, `analyze`, `diagram`, `backlog`) are on-invoke only; the always-on cost is unaffected by which heavy commands exist.

To measure your own session footprint, run `/context all` (Claude Code v2.1.139+) for per-skill token estimates against your active model.

---

## Why ArcKit?

### Problem: Architecture Governance is Broken

Traditional enterprise architecture suffers from:

- ❌ Scattered documents across tools (Word, Confluence, PowerPoint)
- ❌ Inconsistent governance enforcement
- ❌ Manual vendor evaluation with bias
- ❌ Lost traceability between requirements and design
- ❌ Stale documentation that doesn't match reality

### Solution: Structured, AI-Assisted Governance

ArcKit provides:

- ✅ **Template-Driven Quality**: Comprehensive templates ensure nothing is forgotten
- ✅ **Systematic Workflows**: Clear processes from requirements → procurement → design review
- ✅ **AI Assistance**: Let AI handle document generation, you focus on decisions
- ✅ **Enforced Traceability**: Automatic gap detection and coverage analysis
- ✅ **Version Control**: Git-based workflow for all architecture artifacts

---

## TOGAF ADM Overlay (`arckit-togaf-adm`) [COMMUNITY]

Enterprise Architecture Development Method — 9 commands covering the full ADM cycle.

| Command | Doc Type | Phase | Description |
|---------|----------|-------|-------------|
| `/arckit:adm-preliminary` | ADMP | Preliminary | Architecture vision, scope, drivers, constraints |
| `/arckit:business-capability-map` | BPCM | Phase A | Business capability hierarchy, value streams, maturity |
| `/arckit:application-inventory` | APP | Phase C | Application catalog with strategic fit scoring |
| `/arckit:application-rationalization` | APPR | Phase C | Keep/merge/replace/retire decisions |
| `/arckit:gap-analysis` | GAPA | Phase E | Capability gap matrix, workstream mapping |
| `/arckit:transition-architecture` | TRANS | Phase F | Work packages, migration waves, acceptance criteria |
| `/arckit:architecture-board` | BORD | Phase G | Board charter, compliance scorecard, governance |
| `/arckit:architecture-change` | ACHG | Phase H | Change requests, ADM cycle re-entry |
| `/arckit:architecture-repository` | REPO | Repository | Patterns, standards, reference architectures |

**Install:** `claude plugin install arckit arckit-togaf-adm`
**Recipe:** `togaf-adm-full` — full ADM cycle via build recipe

---

## O-AA Overlay (`arckit-oaa`) [COMMUNITY]

Open Agile Architecture (C208) — sprint-based, product-driven architecture delivery. 5 commands that compress the ADM cycle into 2–4 week engagement windows.

| Command | Doc Type | C208 Chapter | Description |
|---------|----------|-------------|-------------|
| `/arckit:oaa-adm-lite` | `OAAL` | Ch 1–9 | Maps TOGAF ADM cycle to agile sprints with backlog-driven delivery |
| `/arckit:product-architecture` | `OAPR` | Ch 12 | Product-centric architecture — cross-functional teams, value streams, backlog-driven |
| `/arckit:agile-strategy` | `OASTR` | Ch 10 | Dual transformation canvas — legacy modernization + greenfield innovation |
| `/arckit:agile-security` | `OASEC` | Ch 17 | Security as backlog items — per-sprint threat modeling, continuous compliance |
| `/arckit:agile-governance` | `OAGOV` | Ch 18 | Sprint-aligned governance — lightweight review gates, max 2 artefacts per sprint |

**Install:** `claude plugin install arckit arckit-oaa`
**Recipe:** `oaa-full` — strategy → product → ADM Lite → security → governance pipeline
**Requires:** `arckit` core plugin (recipe resolves `arckit:principles`, `arckit:requirements`, `arckit:stakeholders`)

---

## AI Agent Architecture Overlay (`arckit-agent-architecture`) [COMMUNITY]

Governance, design, and security for autonomous AI agent programs — 6 commands.

| Command | Doc Type | Description |
|---------|----------|-------------|
| `/arckit:agent-inventory` | AAGI | Agent catalog with capabilities, security classification |
| `/arckit:agent-design` | AAGR | Agent architecture spec — patterns, tools, memory, orchestration |
| `/arckit:agent-governance` | AAOV | Oversight models, approval workflows, audit, compliance |
| `/arckit:agent-integration` | AAIN | Multi-agent orchestration, contracts, shared state |
| `/arckit:agent-security` | AASE | Sandboxing, permissions, injection defences, output validation |
| `/arckit:agent-maturity` | AAMT | 5×5 maturity model for agent programs |

**Install:** `claude plugin install arckit arckit-agent-architecture`
**Recipe:** `agent-architecture` — full agent architecture lifecycle via build recipe

### Combined Recipe: `togaf-agent-full`

For organisations adopting both enterprise architecture and AI agent governance:

```bash
claude agent recipes/togaf-agent-full.yaml
```

---

## The ArcKit Workflow

ArcKit guides you through the enterprise architecture lifecycle:

### Phase 0: Project Planning

**`/arckit:plan`** → Create project plan with timeline, phases, and gates

Visualize your entire project delivery:

- GDS Agile Delivery phases (Discovery → Alpha → Beta → Live)
- Mermaid Gantt chart with timeline, dependencies, and milestones
- Workflow diagram showing gates and decision points
- Tailored timeline based on project complexity
- Integration of all ArcKit commands into schedule
- Gate approval criteria for governance

### Phase 1: Establish Governance

**`/arckit:principles`** → Create enterprise architecture principles

Define your organisation's architecture standards:

- Cloud strategy (AWS/Azure/GCP)
- Security frameworks (Zero Trust, compliance)
- Technology standards
- FinOps and cost governance

### Phase 2: Stakeholder Analysis

**`/arckit:stakeholders`** → Analyze stakeholder drivers, goals, and outcomes

**Do this BEFORE business case** to understand who cares about the project and why:

- Identify all stakeholders (internal and external)
- Document underlying drivers (strategic, operational, financial, compliance, risk, personal)
- Map drivers to SMART goals
- Map goals to measurable outcomes
- Create Stakeholder → Driver → Goal → Outcome traceability
- Identify conflicts and synergies
- Define engagement and communication strategies

### Phase 3: Risk Assessment

**`/arckit:risk`** → Create comprehensive risk register (Orange Book)

**Do this BEFORE business case** to identify and assess risks systematically:

- Follow HM Treasury Orange Book 2023 framework
- Identify risks across 6 categories (Strategic, Operational, Financial, Compliance, Reputational, Technology)
- Assess inherent risk (before controls) and residual risk (after controls)
- Apply 4Ts response framework (Tolerate, Treat, Transfer, Terminate)
- Link every risk to stakeholder from RACI matrix
- Monitor risk appetite compliance
- Feed into SOBC Management Case Part E

### Phase 4: Business Case Justification

**`/arckit:sobc`** → Create Strategic Outline Business Case (SOBC)

**Do this BEFORE requirements** to justify investment and secure approval:

- Use HM Treasury Green Book 5-case model (Strategic, Economic, Commercial, Financial, Management)
- Analyze strategic options (Do Nothing, Minimal, Balanced, Comprehensive)
- Map benefits to stakeholder goals (complete traceability)
- Provide high-level cost estimates (Rough Order of Magnitude)
- Economic appraisal (ROI range, payback period)
- Procurement and funding strategy
- Governance and risk management (uses risk register)
- Enable go/no-go decision BEFORE detailed requirements work

### Phase 5: Define Requirements

**`/arckit:requirements`** → Document comprehensive requirements

Create detailed requirements **informed by stakeholder goals** (if SOBC approved):

- Business requirements with rationale
- Functional requirements with acceptance criteria
- Non-functional requirements (performance, security, scalability, compliance)
- Integration requirements (upstream/downstream systems)
- Data requirements (DR-xxx)
- Success criteria and KPIs

### Phase 5.3: Platform Strategy Design (Optional - for Multi-Sided Platforms)

**`/arckit:platform-design`** → Design multi-sided platform strategy using Platform Design Toolkit

Use this phase when designing **ecosystem-based platforms** (Government as a Platform, marketplaces, data platforms):

- **Ecosystem Canvas**: Map supply side, demand side, supporting entities with relationship diagrams
- **Entity-Role Portraits**: Deep dive into 3-5 key entities (context, pressures, goals, gains)
- **Motivations Matrix**: Identify synergies and conflicts across entities with mitigation strategies
- **Transactions Board**: Design 10-20 transactions with cost reduction analysis (search, information, negotiation, coordination, enforcement)
- **Learning Engine Canvas**: 5+ services that help participants improve (data, feedback loops, network effects)
- **Platform Experience Canvas**: Journey maps with business model and unit economics
- **MVP Canvas**: Liquidity bootstrapping strategy to solve chicken-and-egg problem
- **Platform Design Canvas**: Synthesize all 8 canvases into cohesive platform strategy
- **UK Government Context**: Aligns with Government as a Platform (GaaP), TCoP Point 8 (share/reuse), Digital Marketplace

**Use Cases**: NHS appointment booking, local authority data marketplaces, training procurement platforms, citizen services portals

### Phase 5.5: Data Modeling

**`/arckit:data-model`** → Create comprehensive data model with ERD

Create data model based on Data Requirements (DR-xxx):

- Visual Entity-Relationship Diagram (ERD) using Mermaid
- Detailed entity catalog with attributes, types, validation rules
- PII identification and GDPR/DPA 2018 compliance
- Data governance matrix (business owners, stewards, custodians)
- CRUD matrix showing component access patterns
- Data integration mapping (upstream sources, downstream consumers)
- Data quality framework with measurable metrics
- Requirements traceability (DR-xxx → Entity → Attribute)

### Phase 5.7: Data Protection Impact Assessment

**`/arckit:dpia`** → Generate [DPIA](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/) for UK GDPR Article 35 compliance

**MANDATORY for high-risk processing** - assess privacy risks before technology selection:

- ICO 9-criteria automated screening (sensitive data, large scale, vulnerable subjects, AI/ML, etc.)
- Auto-populated from data model (entities, PII, special category data, lawful basis)
- Risk assessment focused on impact on individuals (privacy harm, discrimination)
- Data subject rights implementation checklist (SAR, deletion, portability)
- Children's data assessment (age verification, parental consent)
- AI/ML algorithmic processing assessment (bias, explainability, human oversight)
- ICO prior consultation flagging for high residual risks
- International transfer safeguards (SCCs, BCRs, adequacy decisions)
- Bidirectional links to risk register (DPIA-xxx risk IDs)
- Links mitigations to Secure by Design security controls

### Phase 5.8: Data Source Discovery

**`/arckit:datascout`** → Discover external data sources

Discover and evaluate external data sources to fulfil project data requirements:

- Data needs extraction from DR/FR/INT/NFR requirements
- UK Government open data portals (data.gov.uk, ONS, NHS Digital, Companies House, OS Data Hub)
- Commercial API providers and data marketplaces
- Free/freemium APIs and open source datasets
- Weighted evaluation scoring (Requirements Fit, Data Quality, License & Cost, API Quality, Compliance, Reliability)
- Gap analysis for unmet data needs
- Data model impact assessment (new entities, attributes, sync strategy)
- Requirements traceability (every DR-xxx mapped to a source or flagged as gap)
- TCoP Point 10 compliance (Make Better Use of Data)

### Phase 6: Technology Research

**`/arckit:research`** → Research technology, services, and products

Research available solutions to meet requirements with build vs buy analysis:

- Dynamic category detection from requirements (authentication, payments, databases, etc.)
- Commercial SaaS options with pricing, reviews, and ratings (WebSearch)
- Open source alternatives with GitHub stats and community maturity
- UK Government GOV.UK platforms (One Login, Pay, Notify, Forms)
- Digital Marketplace suppliers (G-Cloud, DOS)
- Total Cost of Ownership (TCO) comparison (3-year)
- Build vs Buy vs Adopt recommendations
- Vendor shortlisting for deeper evaluation
- Integration with Wardley mapping (evolution positioning)
- Feeds into SOBC Economic Case (cost data, options analysis)

### Phase 6.5: Grants & Funding Research

**`/arckit:grants`** → Research UK government grants, charitable funding, and accelerator programmes

Identify and evaluate funding opportunities with eligibility scoring:

- UK Innovate UK grants and R&D funding (e.g. Smart Grants, KTP, SBRI)
- UK Research and Innovation (UKRI) funding calls
- Charitable foundations and philanthropic funding (e.g. National Lottery Heritage Fund, Wellcome Trust)
- Accelerator and incubator programmes (e.g. DCMS, DSIT-backed cohorts)
- EU Horizon Europe successor funding open to UK entities
- Eligibility scoring matrix against project requirements and stakeholder profile
- Application timeline, deadlines, and award values
- Strategic fit assessment (alignment with project goals and public sector context)
- Outputs a structured GRNT funding opportunity register

### Phase 7: Strategic Planning with Wardley Mapping

**`/arckit:wardley`** → Create strategic Wardley Maps

Visualize strategic positioning with:

- Component evolution analysis (Genesis → Custom → Product → Commodity)
- Build vs Buy decision framework
- Vendor comparison and procurement strategy
- UK Government Digital Marketplace mapping
- Evolution predictions and strategic gameplay

### Phase 7.5: Strategic Roadmap

**`/arckit:roadmap`** → Create multi-year architecture roadmap

Create strategic roadmap for multi-year transformation programs:

- **Multi-year timeline**: 3-5 year roadmap with Mermaid Gantt chart aligned to financial years (FY 2024/25, etc.)
- **Strategic themes**: Cloud migration, data modernization, security & compliance, DevOps transformation
- **Capability evolution**: Maturity progression from L1 (Initial) to L5 (Optimized) over time
- **Investment planning**: CAPEX/OPEX budget by financial year, ROI projections, benefits realization
- **Governance framework**: ARB monthly, Programme Board monthly, Steering Committee quarterly
- **Service Standard gates**: Alpha/Beta/Live assessment milestones (UK Government)
- **Dependencies**: Mermaid flowchart showing initiative sequencing and critical path
- **Success metrics**: Cloud adoption %, technical debt reduction, deployment frequency, time to market
- **Traceability**: Links roadmap themes to stakeholder drivers, architecture principles, requirements
- **UK Government specifics**: Spending Review alignment, TCoP compliance timeline, NCSC CAF progression

**Use this when**: You have a multi-year transformation program with multiple initiatives running in parallel. Roadmaps are strategic (multi-year, multi-initiative, executive communication) vs project plans which are tactical (single initiative, detailed tasks, team execution).

**Roadmap feeds into**: `/arckit:plan` for detailed phase execution, `/arckit:sobc` for investment business case, `/arckit:backlog` for prioritized user stories, `/arckit:strategy` for executive-level synthesis.

### Phase 7.6: Architecture Strategy Synthesis

**`/arckit:strategy`** → Synthesise strategic artifacts into executive-level Architecture Strategy

Create a comprehensive Architecture Strategy document that synthesises multiple strategic artifacts into a single coherent narrative:

- **Strategic vision**: 2-3 paragraphs articulating the transformation vision and success definition
- **Strategic drivers**: Summarised from stakeholder analysis with external drivers (regulatory, market, technology)
- **Guiding principles**: Key principles with strategic implications, compliance summary
- **Current state assessment**: Technology landscape, capability maturity baseline (L1-L5), technical debt, SWOT
- **Target state vision**: Future architecture, capability maturity targets, architecture vision diagram
- **Technology evolution**: Build vs buy decisions, technology radar (Adopt/Trial/Assess/Hold) from Wardley maps
- **Strategic themes**: 3-5 investment themes with objectives, initiatives, success criteria, principles alignment
- **Delivery roadmap summary**: Timeline, phases, milestones from roadmap artifact
- **Investment summary**: CAPEX/OPEX, NPV, IRR, payback period, benefits realisation from SOBC
- **Strategic risks**: Top risks with heat map, assumptions, constraints from risk register
- **Success metrics**: KPIs with baselines and year-over-year targets
- **Governance model**: Forums, decision rights, review cadence
- **Traceability**: Driver → Goal → Outcome → Theme → Principle → KPI chain

**Use this when**: You have multiple strategic artifacts (principles, stakeholders, wardley, roadmap, sobc) and need to create a single executive-level document that synthesises them into a coherent strategy. Ideal for Strategy Board presentations, executive briefings, or stakeholder communication.

**Unique requirement**: This is the only ArcKit command with TWO mandatory inputs (principles AND stakeholders). Strategy cannot be created without understanding both the decision framework and the stakeholder drivers.

**Strategy feeds into**: `/arckit:requirements` for detailed requirements, `/arckit:roadmap` for expanded timeline, `/arckit:plan` for project delivery.

### Phase 7.7: Architecture Decision Records

**`/arckit:adr`** → Document architectural decisions

Create Architecture Decision Records (ADRs) following MADR v4.0 format enhanced with UK Government requirements:

- **Decision metadata**: Sequential numbering (ADR-001, ADR-002), status (Proposed/Accepted/Superseded), escalation level (Team/Cross-team/Department/Cross-government)
- **Stakeholder RACI**: Deciders (accountable), Consulted (SMEs, two-way), Informed (one-way communication)
- **Context and problem statement**: Why this decision is needed, business/technical/regulatory drivers
- **Decision drivers**: Technical forces (performance, security, scalability), business forces (cost, time), compliance forces (GDS Service Standard, TCoP, NCSC, UK GDPR)
- **Options analysis**: Minimum 2-3 options plus "Do Nothing" baseline, each with pros/cons, cost (CAPEX/OPEX/TCO), GDS Service Standard impact, Wardley evolution stage
- **Y-Statement**: Structured justification - "In the context of X, facing Y, we decided for Z to achieve A, accepting B"
- **Consequences**: Positive (benefits, capabilities), Negative (trade-offs, technical debt), Neutral (training, infrastructure), Risks and mitigations
- **Validation**: How implementation will be verified (design reviews, code reviews, testing, monitoring)
- **Traceability**: Links to requirements, principles, stakeholders, research, Wardley maps, diagrams, risk register
- **UK Government specifics**: Escalation levels (Team → Cross-team → Department → Cross-government), governance forums (ARB, TDA, Programme Board), Service Standard/TCoP compliance documentation

**Use this when**: Making significant architectural decisions that affect system structure, quality attributes, or behavior - technology choices (databases, frameworks, cloud services), integration patterns, security approaches, deployment strategies, data management.

**ADR feeds into**: `/arckit:diagram` (architecture diagrams reflect decisions), `/arckit:hld-review` and `/arckit:dld-review` (reviews verify decisions implemented), `/arckit:traceability` (decisions are key traceability artifacts).

### Phase 8: Vendor Procurement (if needed)

**`/arckit:sow`** → Generate Statement of Work (RFP)

Create RFP-ready documents with:

- Scope of work and deliverables
- Technical requirements
- Vendor qualifications
- Evaluation criteria
- Contract terms

**`/arckit:dos`** → Digital Outcomes and Specialists (DOS) procurement 🇬🇧

For UK public sector organizations needing custom development:

- Generate DOS-compliant procurement documentation
- Extract requirements from project artifacts (BR/FR/NFR/INT/DR)
- Essential vs desirable skills from requirements
- Success criteria (technology-agnostic)
- Evaluation framework (40% Technical, 30% Team, 20% Quality, 10% Value)
- Audit-ready documentation for Digital Marketplace

**`/arckit:gcloud-search`** → G-Cloud service search with live marketplace search 🇬🇧

For UK public sector organizations needing off-the-shelf cloud services:

- Generate G-Cloud requirements document
- **Live Digital Marketplace search** using WebSearch
- Find actual services with suppliers, prices, features, links
- Service comparison table with recommendations
- Shortlist top 3-5 matching services
- Links to Digital Marketplace guidance (gov.uk)

**`/arckit:gcloud-clarify`** → G-Cloud service validation and gap analysis 🇬🇧

Validate G-Cloud services and generate supplier clarification questions:

- **Systematic gap analysis** (MUST/SHOULD requirements vs service descriptions)
- Detect gaps: ✅ Confirmed, ⚠️ Ambiguous, ❌ Not mentioned
- Generate prioritised questions (🔴 Critical / 🟠 High / 🔵 Medium / 🟢 Low)
- Risk assessment matrix for each service
- Email templates for supplier engagement
- Evidence requirements specification
- Next steps checklist

**`/arckit:evaluate`** → Create vendor evaluation framework

Set up systematic scoring:

- Technical evaluation criteria (100 points)
- Cost evaluation methodology
- Reference check templates
- Decision matrix

**`/arckit:evaluate`** (compare mode) → Compare vendor proposals

Side-by-side analysis of:

- Technical approaches
- Cost breakdowns
- Risk assessments
- Value propositions

### Phase 9: Design Review

**`/arckit:hld-review`** → Review High-Level Design

Validate designs against:

- Architecture principles compliance
- Requirements coverage
- Security and compliance
- Scalability and resilience
- Operational readiness

**`/arckit:dld-review`** → Review Detailed Design

Implementation-ready validation:

- Component specifications
- API contracts (OpenAPI)
- Database schemas
- Security implementation
- Test strategy

### Phase 10: Sprint Planning

**`/arckit:backlog`** → Generate prioritised product backlog

Transform requirements into sprint-ready user stories:

- Convert requirements (BR/FR/NFR/INT/DR) to GDS-format user stories
- Multi-factor prioritization (MoSCoW + risk + value + dependencies)
- Organise into sprint plan with capacity balancing
- Generate traceability matrix (requirements → stories → sprints)
- Export to Jira/Azure DevOps (CSV) or custom tools (JSON)
- **Time savings**: 75%+ (4-6 weeks → 3-5 days)

**When to run**: After HLD approval, before Sprint 1 (Alpha → Beta transition)

### Phase 10.5: Backlog Export

**`/arckit:trello`** → Export product backlog to Trello

Push your backlog directly to Trello for sprint execution:

- Create Trello board with sprint-based lists (Product Backlog + per-sprint + In Progress + Done)
- Cards with priority labels, story points, and acceptance criteria checklists
- Colour-coded labels by MoSCoW priority and requirement type
- Rate-limit-aware Trello API integration
- Requires `TRELLO_API_KEY` and `TRELLO_TOKEN` environment variables

**When to run**: After `/arckit:backlog` generates the product backlog (requires JSON export)

### Phase 11: ServiceNow Service Management Design

**`/arckit:servicenow`** → Generate ServiceNow service design

Bridge architecture to operations:

- CMDB design (derived from architecture diagrams)
- SLA definitions (derived from NFRs)
- Incident management design
- Change management plan
- Monitoring and alerting plan
- Service transition plan

### Phase 12: Traceability

**`/arckit:traceability`** → Generate traceability matrix

Ensure complete coverage:

- Requirements → Design mapping
- Design → Test mapping
- Gap analysis and orphan detection
- Change impact tracking

### Phase 13: Quality Assurance

**`/arckit:analyze`** → Comprehensive governance quality analysis

Periodically assess governance quality across all artifacts:

- Architecture principles compliance
- Requirements coverage and traceability
- Stakeholder alignment verification
- Risk management completeness
- Design review quality
- Documentation completeness and quality
- Gap identification and recommendations

**When to use**: Run periodically (before milestones, design reviews, or procurement decisions) to identify gaps and ensure governance standards are maintained.

### Phase 14: Compliance Assessment (UK Government)

For UK Government and public sector projects:

**`/arckit:service-assessment`** → [GDS Service Standard](https://www.gov.uk/service-manual/service-assessments) assessment preparation

Prepare for mandatory GDS Service Standard assessments:

- Analyze evidence against all 14 Service Standard points
- Identify gaps for alpha, beta, or live assessments
- Generate RAG (Red/Amber/Green) ratings and overall readiness score
- Provide actionable recommendations with priorities and timelines
- Include assessment day preparation guidance
- Map ArcKit artifacts to Service Standard evidence requirements

Run at end of Discovery (for alpha prep), mid-Beta (for beta prep), or before Live to ensure readiness.

**`/arckit:tcop`** → [Technology Code of Practice](https://www.gov.uk/guidance/the-technology-code-of-practice) assessment

Assess compliance with all 13 TCoP points:

- Point 1: Define user needs
- Point 2: Make things accessible
- Point 3: Be open and use open source
- Point 4: Make use of open standards
- Point 5: Use cloud first
- Point 6: Make things secure
- Point 7: Make privacy integral
- Point 8: Share, reuse and collaborate
- Point 9: Integrate and adapt technology
- Point 10: Make better use of data
- Point 11: Define your purchasing strategy
- Point 12: Meet the Digital Spend Controls
- Point 13: Define your responsible AI use

**`/arckit:secure`** → UK Government Secure by Design assessment

Security compliance assessment:

- NCSC Cloud Security Principles
- NCSC Cyber Assessment Framework (CAF)
- Cyber Essentials / Cyber Essentials Plus
- UK GDPR and DPA 2018 compliance
- Security architecture review
- Threat modeling

**`/arckit:ai-playbook`** → [UK Government AI Playbook](https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government) compliance (for AI systems)

Responsible AI assessment:

- AI ethics principles
- Transparency and explainability
- Fairness and bias mitigation
- Data governance for AI
- Human oversight mechanisms
- Impact assessment

**`/arckit:atrs`** → [Algorithmic Transparency Recording Standard](https://www.gov.uk/government/collections/algorithmic-transparency-recording-standard-hub)

Generate ATRS record for algorithmic decision-making:

- Algorithm details and logic
- Purpose and use case
- Data sources and data quality
- Performance metrics and monitoring
- Impact assessment and mitigation

**For MOD Projects**:

**`/arckit:mod-secure`** → MOD Secure by Design assessment

MOD-specific security compliance:

- JSP 440 (Defence Project & Programme Management)
- Information Assurance Maturity Model (IAMM)
- MOD Security clearances and vetting
- STRAP classification handling
- Security Operating Procedures (SyOPs)
- Supplier attestation requirements

**`/arckit:jsp-936`** → [MOD JSP 936](https://www.gov.uk/government/publications/jsp-936-dependable-artificial-intelligence-ai-in-defence-part-1-directive) AI Assurance Documentation

For defence projects using AI/ML systems:

- JSP 936 (Dependable Artificial Intelligence in Defence)
- 5 Ethical Principles (Human-Centricity, Responsibility, Understanding, Bias & Harm Mitigation, Reliability)
- 5 Risk Classification Levels (Critical to Minor)
- 8 AI Lifecycle Phases (Planning to Quality Assurance)
- Approval pathways (2PUS/Ministerial → Defence-Level → TLB-Level)
- RAISOs and Ethics Manager governance
- Human-AI teaming strategy and continuous monitoring

### Phase 14.5: Compliance Assessment (EU and French Government)

ArcKit includes commands for EU regulatory compliance and French public sector governance. These commands are applicable to organisations operating in the EU or under French jurisdiction — whether public sector or private.

#### EU Regulations

**`/arckit:eu-rgpd`** → GDPR compliance assessment (Regulation 2016/679)

Assess personal data processing obligations:

- Legal basis determination (consent, contract, legitimate interest, legal obligation)
- Data subject rights implementation (access, erasure, portability, objection)
- CNIL registration and DPO obligations (France)
- Cross-border transfer safeguards (SCCs, BCRs, adequacy decisions)
- Integration with DPIA (`/arckit:dpia`) for high-risk processing

**`/arckit:eu-ai-act`** → EU AI Act compliance (Regulation 2024/1689)

Assess AI system obligations under the EU's risk-based AI framework:

- Risk classification (unacceptable / high-risk / limited-risk / minimal)
- High-risk system obligations: conformity assessment, CE marking, EUDB registration
- GPAI model obligations for providers of general-purpose AI
- Human oversight, transparency, and fundamental rights impact assessment
- Prohibited practices (social scoring, real-time biometric surveillance)

**`/arckit:eu-nis2`** → NIS2 Directive compliance (Directive 2022/2555)

Assess cybersecurity obligations for essential and important entities:

- Sector classification (Annex I Essential vs Annex II Important)
- OIV/OSE designation under French transposition (LPM/LCEN)
- Governance, risk management, and incident reporting obligations
- Supply chain security and vulnerability disclosure
- ANSSI notification timeline (24h → 72h → 30-day final report)

**`/arckit:eu-dora`** → DORA compliance (Regulation 2022/2554) for financial entities

Digital Operational Resilience Act obligations for banks, insurers, and investment firms:

- ICT risk management framework (5 pillars)
- Major ICT-related incident classification and reporting (4h → 72h → monthly final)
- TLPT (Threat-Led Penetration Testing) requirements for significant institutions
- Third-party ICT provider management and critical provider designation
- Contractual requirements for ICT service agreements

**`/arckit:eu-cra`** → Cyber Resilience Act compliance (Regulation 2024/2847)

Mandatory cybersecurity requirements for products with digital elements (hardware + software):

- Product classification (Default / Important Class I / Critical Class II)
- 12 Annex I Part I security-by-design requirements
- SBOM in SPDX or CycloneDX format (mandatory)
- Vulnerability Disclosure Policy and 24h ENISA reporting
- Conformity assessment route (internal control vs notified body)
- Full application deadline: 11 December 2027

**`/arckit:eu-dsa`** → EU Digital Services Act compliance (Regulation 2022/2065)

Tiered obligations for online intermediary services:

- Provider classification (mere conduit / hosting / platform / VLOP / VLOSE)
- VLOP/VLOSE designation threshold: 45M monthly active EU users
- Content moderation, recommender system transparency, advertising obligations
- ARCOM as French Digital Services Coordinator (DSC)
- Systemic risk assessment and independent audit for VLOPs

**`/arckit:eu-data-act`** → EU Data Act compliance (Regulation 2023/2854)

Data sharing obligations for connected products and cloud providers:

- Role determination: manufacturer / data holder / DAPS / public sector body
- User data access rights (Chapter II) and B2B sharing (Chapter III)
- Cloud switching obligations (Chapter VI) — egress fee elimination by September 2027
- International data transfer restrictions (Article 27)
- Application date: 12 September 2025


---

### Phase 15: Project Story & Reporting

**`/arckit:story`** → Generate comprehensive project story

Create narrative historical record with complete timeline analysis:

- **Timeline Analysis**: 4 visualization types (Gantt chart, linear flowchart, detailed table, phase duration pie chart)
- **Timeline Metrics**: Project duration, velocity, phase analysis, critical path identification
- **Complete Timeline**: All events from git log or file modification dates with days-from-start
- **8 Narrative Chapters**: Foundation → Business Case → Requirements → Research → Procurement → Design → Delivery → Compliance
- **Traceability Demonstration**: End-to-end chains with Mermaid diagrams showing stakeholder → goals → requirements → stories → sprints
- **Governance Achievements**: Showcase compliance (TCoP, Service Standard, NCSC CAF), risk management, decision rationale
- **Strategic Context**: Wardley Map insights, build vs buy decisions, vendor selection rationale
- **Lessons Learned**: Pacing analysis, timeline deviations, recommendations for future projects
- **Comprehensive Appendices**: Artifact register, chronological activity log, DSM, command reference, glossary

**When to use**: At project milestones or completion to create shareable story for stakeholders, leadership, or portfolio reporting. Perfect for demonstrating systematic governance and ArcKit workflow value.

**`/arckit:presentation`** → Generate MARP slide deck from project artifacts

Create presentation slides from existing architecture artifacts:

- **MARP Format**: Markdown-based slides with `---` separators — exports to PDF, PPTX, or HTML
- **Focus Modes**: Executive (board-level), Technical (architecture detail), Stakeholder (benefits-focused), Procurement (RFP briefings)
- **Artifact-Driven**: Reads all available project artifacts and extracts key content into slides
- **Mermaid Diagrams**: Gantt charts, C4 diagrams, pie charts, and quadrant charts embedded natively
- **Configurable**: Choose slide count (6-8, 10-12, 15-20) and MARP theme (default, gaia, uncover)
- **Doc type code**: `PRES`

**When to use**: Before governance boards, stakeholder briefings, gate reviews, or quarterly portfolio presentations. Run after creating most project artifacts for the richest slide deck.

### Phase 16: Documentation Publishing

**`/arckit:pages`** → Generate documentation site

Publish all project documentation as an interactive website:

- **Static Site Generation**: Generates `docs/index.html` and `docs/manifest.json` — deployable to any static host (GitHub Pages, Netlify, Vercel, S3, etc.)
- **Mermaid Diagram Rendering**: All architecture diagrams render inline with mermaid.js
- **Project Navigation**: Sidebar with collapsible project tree, document categories, and version badges — documents with multiple versions show an inline dropdown selector
- **GOV.UK Styling**: Professional government design system styling
- **Document Index**: Manifest.json provides programmatic access to all artifacts
- **LLM Discovery**: Generates `docs/llms.txt` ([llmstxt.org](https://llmstxt.org/) format) so LLM agents and crawlers can index every artifact, guide, and project. Hand-curated `docs/llms.txt` files (without the ArcKit generation marker) are preserved on re-runs

**When to use**: When you want to share project documentation with stakeholders via a professional web interface, or to create a portfolio view of all architecture artifacts.

---

## Supported AI Assistants

| Assistant | Support | Notes |
|-----------|---------|-------|
| [Claude Code](https://www.anthropic.com/claude-code) | ✅ Premier | **Primary platform.** Plugin with agents, hooks, MCP servers, and auto-updates |
| [GitHub Copilot](https://github.com/features/copilot) | ✅ Core | VS Code prompt files, custom agents, and repo-wide instructions (`arckit init --ai copilot`) |
| [OpenAI Codex CLI](https://chatgpt.com/features/codex) | ✅ Core | CLI with commands and templates. ChatGPT Plus/Pro/Enterprise ([Setup Guide](.codex/README.md)) |
| [OpenCode CLI](https://opencode.net/cli) | ✅ Core | CLI with commands and templates |

> **Platform Support**: ArcKit is developed and tested on **Linux**. Windows has limited support — hooks (session init, project context, filename validation, MCP auto-allow) require bash and jq which are not available on stock Windows. For the best experience on Windows, use a **devcontainer** or **WSL2**.

### Why Claude Code?

Claude Code is the **primary development platform** for ArcKit and provides capabilities not available in other formats:

| Feature | Claude Code | Copilot | Codex / OpenCode |
|---------|:-----------:|:-------:|:----------------:|
| 75 cross-AI slash commands | ✅ | ✅ | ✅ |
| `/arckit:build` parallel build harness (Claude-only — depends on parallel `Agent` dispatch) | ✅ | — | — |
| Templates & scripts | ✅ | ✅ | ✅ |
| Bundled MCP servers (AWS, Azure, GCP, DataCommons, govreposcrape, uk-tenders) | ✅ | — | Manual setup |
| **Autonomous research agents** (10 agents for research, datascout, cloud research, gov code discovery, grants, framework) | ✅ | ✅ (10 agents) | — |
| **SessionStart hook** (auto-detect version + projects) | ✅ | — | — |
| **UserPromptSubmit hook** (project context injection on every prompt) | ✅ | — | — |
| **PreToolUse hook** (ARC filename auto-correction) | ✅ | — | — |
| **PermissionRequest hook** (auto-allow MCP documentation tools) | ✅ | — | — |
| **Per-command Stop hooks** (output validation, e.g. Wardley Map math checks) | ✅ | — | — |
| Wardley Mapping skill (with Pinecone MCP book corpus) | ✅ | — | — |
| Mermaid Syntax Reference skill (23 diagram types + config) | ✅ | — | ✅ |
| Automatic marketplace updates | ✅ | Manual reinstall | Manual reinstall |
| Zero-config installation | ✅ | `arckit init` required | `arckit init` required |

**Agents** run research-heavy commands (market research, data source discovery, cloud service evaluation) in isolated context windows, keeping the main conversation clean and enabling dozens of WebSearch/WebFetch/MCP calls without context bloat.

**Hooks** provide automated governance: filenames are auto-corrected to ArcKit conventions, project context is injected into every prompt so commands know what artifacts exist, MCP tools are auto-approved, and generated outputs like Wardley Maps are validated for mathematical consistency before being finalized.

GitHub Copilot provides all 75 official commands as prompt files and 10 custom agents but lacks hooks and MCP servers. Codex CLI and OpenCode CLI provide core command functionality but require manual setup and `arckit init` scaffolding.

### Why Commands, Not Skills

Claude Code automatically exposes ArcKit commands as **skills** (they appear in the skills list and can be matched by natural language). ArcKit intentionally uses **slash commands** rather than standalone skills because:

- **Deliberate invocation required** — Every command generates a heavyweight governance document (requirements spec, risk register, DPIA, etc.). Auto-triggering from conversational intent would waste significant time and tokens.
- **Dependency ordering** — Commands follow a deliberate sequence (principles → stakeholders → requirements → data-model → etc.). Skills that auto-trigger could run out of order.
- **User input via `$ARGUMENTS`** — Most commands accept context from the user (project name, scope, constraints). The command system handles this with `$ARGUMENTS` substitution.
- **Best of both worlds** — Since Claude Code exposes commands as skills automatically, users get explicit `/arckit:requirements` invocation AND natural language matching when Claude recognises intent — no restructuring needed.

### Using with GitHub Copilot

For GitHub Copilot users in VS Code, ArcKit commands are delivered as prompt files and custom agents:

```bash
# Install and create project (3 steps, zero config)
pip install git+https://github.com/terrygzhou/arc-kit.git
arckit init my-project --ai copilot
cd my-project && code .

# Then use ArcKit commands in Copilot Chat
/arckit-principles Create principles for financial services
/arckit-stakeholders Analyze stakeholders for cloud migration
/arckit-requirements Create comprehensive requirements
```

This creates `.github/prompts/arckit-*.prompt.md`, `.github/agents/arckit-*.agent.md` (10 custom agents), and `.github/copilot-instructions.md` (repo-wide context).

### Using with Codex CLI

For OpenAI Codex CLI users, ArcKit commands are delivered as skills and auto-discovered:

```bash
# Install and create project (3 steps, zero config)
pip install git+https://github.com/terrygzhou/arc-kit.git
arckit init my-project --ai codex
cd my-project && codex

# Then use ArcKit skills
$arckit-principles Create principles for financial services
$arckit-stakeholders Analyze stakeholders for cloud migration
$arckit-requirements Create comprehensive requirements
```

See [.codex/README.md](.codex/README.md) for full Codex CLI setup and usage.

## Template Customization

Customize ArcKit templates without modifying defaults:

```bash
# Inside your AI assistant
/arckit:customize requirements   # Copy requirements template for editing
/arckit:customize all            # Copy all templates
/arckit:customize list           # See available templates
```

**How it works:**

- Default templates live in `.arckit/templates/` (refreshed by `arckit init`)
- Your customizations go in `.arckit/templates-custom/` (preserved across updates)
- Commands automatically check for custom templates first, falling back to defaults

**Common customizations:**

- Add organization-specific document control fields
- Include mandatory compliance sections (ISO 27001, PCI-DSS)
- Add department-specific approval workflows
- Customize UK Government classification banners

---

## Complete Command Reference

Core ArcKit commands with maturity status.

### Status Legend

| Status | Description |
|--------|-------------|
| 🟢 **Live** | Production-ready, extensively tested |
| 🔵 **Beta** | Feature-complete, actively refined |
| 🟠 **Alpha** | Working, limited testing |
| 🟣 **Experimental** | New in v0.11.x, early adopters |

### Foundation

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:init`  |  Initialize ArcKit project structure with numbered project directories and global artifacts  |  🟢 Live  |
|  `/arckit:start`  |  Get oriented with ArcKit — check project status, explore available commands, and choose your next step  |  🟢 Live  |
|  `/arckit:plan`  |  Create project plan with timeline, phases, gates, and Mermaid diagrams  |  🟢 Live  |
|  `/arckit:principles`  |  Create or update enterprise architecture principles  |  🟢 Live  |
|  `/arckit:build`  |  Bulk-build ArcKit artefacts in parallel via subagent-orchestrated waves with resumable state (Claude-only)  |  🔵 Beta  |

### Interoperability

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:export-okf`  |  Export ArcKit project artifacts as an OKF Markdown bundle without changing source ARC files  |  🔵 Beta  |
|  `/arckit:import-okf`  |  Import an OKF Markdown bundle into ArcKit as reviewable research notes with a JSON report  |  🔵 Beta  |

### Strategic Context

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:stakeholders`  |  Analyze stakeholder drivers, goals, and measurable outcomes  |  🟢 Live  |
|  `/arckit:risk`  |  Create comprehensive risk register following HM Treasury Orange Book principles  |  🟢 Live  |
|  `/arckit:sobc`  |  Create Strategic Outline Business Case (SOBC) using UK Government Green Book 5-case model  |  🟢 Live  |

### Requirements & Data

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:requirements`  |  Create comprehensive business and technical requirements  |  🟢 Live  |
|  `/arckit:data-model`  |  Create comprehensive data model with entity relationships, GDPR compliance, and data governance  |  🟢 Live  |
|  `/arckit:data-mesh-contract`  |  Create federated data product contracts for mesh architectures with SLAs, governance, and interoperability guarantees  |  🟠 Alpha  |
|  `/arckit:dpia`  |  Generate [Data Protection Impact Assessment (DPIA)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/) for UK GDPR Article 35 compliance  |  🔵 Beta  |

### Research & Strategy

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:platform-design`  |  Create platform strategy using Platform Design Toolkit (8 canvases for multi-sided ecosystems)  |  🟣 Experimental  |
|  `/arckit:research`  |  Research technology, services, and products to meet requirements with build vs buy analysis  |  🔵 Beta  |
|  `/arckit:grants`  |  Research UK government grants, charitable funding, and accelerator programmes with eligibility scoring  |  🟣 Experimental  |
|  `/arckit:wardley`  |  Create strategic Wardley Maps for architecture decisions and build vs buy analysis  |  🟣 Experimental  |
|  `/arckit:wardley.value-chain`  |  Decompose user needs into value chains for Wardley Mapping  |  🟣 Experimental  |
|  `/arckit:wardley.doctrine`  |  Assess organizational doctrine maturity (4 phases, 40+ principles)  |  🟣 Experimental  |
|  `/arckit:wardley.gameplay`  |  Analyze strategic plays from 60+ gameplay patterns  |  🟣 Experimental  |
|  `/arckit:wardley.climate`  |  Assess 32 climatic patterns affecting mapped components  |  🟣 Experimental  |
|  `/arckit:strategy`  |  Synthesise strategic artifacts into executive-level Architecture Strategy document  |  🔵 Beta  |
|  `/arckit:roadmap`  |  Create strategic architecture roadmap with multi-year timeline, capability evolution, and governance  |  🔵 Beta  |
|  `/arckit:framework`  |  Transform architecture artifacts into a structured, reusable framework with principles, patterns, and implementation guidance  |  🔵 Beta  |
|  `/arckit:adr`  |  Document architectural decisions with options analysis and traceability  |  🔵 Beta  |

### Cloud Research (MCP)

These commands use [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers to access authoritative cloud provider documentation in real-time. The Claude Code plugin bundles both MCP servers automatically. Codex and OpenCode users need to install them separately.

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:azure-research`  |  Research Azure services and architecture patterns using [Microsoft Learn MCP](https://www.npmjs.com/package/@anthropic/mcp-server-microsoft-docs)  |  🟣 Experimental  |
|  `/arckit:aws-research`  |  Research AWS services and architecture patterns using [AWS Knowledge MCP](https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server)  |  🟣 Experimental  |
|  `/arckit:gcp-research`  |  Research Google Cloud services and architecture patterns using [Google Developer Knowledge MCP](https://developerknowledge.googleapis.com/mcp)  |  🟣 Experimental  |

### Data Source Discovery

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:datascout`  |  Discover external data sources (APIs, datasets, open data portals) to fulfil project requirements  |  🟣 Experimental  |

> **Note**: The Google Developer Knowledge MCP requires an API key (`GOOGLE_API_KEY` environment variable). See the [GCP Research guide](docs/guides/gcp-research.md) for setup instructions.

### Procurement Market Intelligence

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:tenders`  |  Procurement market intelligence — award-value benchmarks, top suppliers, incumbency and concentration, from the UK Tenders MCP  |  🟣 Experimental  |
|  `/arckit:competitors`  |  Competitor landscape — rival suppliers, awarded-value market share, head-to-head and concentration, from the UK Tenders MCP  |  🟣 Experimental  |

> **Note**: `/arckit:tenders` and `/arckit:competitors` both use the bundled `uk-tenders` MCP server (keyless, deferred) via the shared `arckit-tenders-reader` subagent. Data: ~677,000 UK contracting processes across FTS, Contracts Finder, Public Contracts Scotland, Sell2Wales, and eTendersNI; nightly refresh; best-effort availability (no formal SLA). `/arckit:tenders` outputs a `TNDR` artefact (market-wide benchmarks, incumbency, concentration). `/arckit:competitors` outputs a `CMPT` artefact (rival-supplier landscape, market-share ranking, head-to-head).

### Government Code Discovery

These commands use the [govreposcrape MCP](https://github.com/MHCLG/govreposcrape-mcp) server to search 24,500+ UK government repositories. The Claude Code plugin bundles the MCP server automatically. No API key required.

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:gov-code-search`  |  Search 24,500+ UK government repositories using natural language  |  🟣 Experimental  |
|  `/arckit:gov-landscape`  |  Map the UK government code landscape for a domain  |  🟣 Experimental  |
|  `/arckit:gov-reuse`  |  Discover reusable UK government code before building from scratch  |  🟣 Experimental  |

### Procurement

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:sow`  |  Generate Statement of Work (SOW) / RFP document for vendor procurement  |  🟢 Live  |
|  `/arckit:dos`  |  Generate Digital Outcomes and Specialists (DOS) procurement documentation for UK Digital Marketplace  |  🟣 Experimental  |
|  `/arckit:gcloud-search`  |  Find G-Cloud services on UK Digital Marketplace with live search and comparison  |  🟣 Experimental  |
|  `/arckit:gcloud-clarify`  |  Analyze G-Cloud service gaps and generate supplier clarification questions  |  🟣 Experimental  |
|  `/arckit:evaluate`  |  Create vendor evaluation framework and score vendor proposals  |  🟢 Live  |
|  `/arckit:score`  |  Score vendor proposals with structured storage, side-by-side comparison, sensitivity analysis, and audit trail  |  🔵 Beta  |

### Design & Architecture

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:diagram`  |  Generate architecture diagrams using Mermaid for visual documentation  |  🟢 Live  |
|  `/arckit:dfd`  |  Generate Yourdon-DeMarco Data Flow Diagrams (DFDs) with structured analysis notation  |  🟣 Experimental  |
|  `/arckit:hld-review`  |  Review High-Level Design (HLD) against architecture principles and requirements  |  🔵 Beta  |
|  `/arckit:dld-review`  |  Review Detailed Design (DLD) for implementation readiness  |  🔵 Beta  |

### Operations

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:backlog`  |  Generate prioritised product backlog from ArcKit artifacts - convert requirements to user stories, organise into sprints  |  🔵 Beta  |
|  `/arckit:trello`  |  Export product backlog to Trello - create board, lists, cards with labels and checklists from backlog JSON  |  🟣 Experimental  |
|  `/arckit:servicenow`  |  Create comprehensive ServiceNow service design with CMDB, SLAs, incident management, and change control  |  🔵 Beta  |
|  `/arckit:devops`  |  Create DevOps strategy with CI/CD pipelines, IaC, container orchestration, and developer experience  |  🟣 Experimental  |
|  `/arckit:mlops`  |  Create MLOps strategy with model lifecycle, training pipelines, serving, monitoring, and governance  |  🟣 Experimental  |
|  `/arckit:finops`  |  Create FinOps strategy with cloud cost management, optimization, governance, and forecasting  |  🟣 Experimental  |
|  `/arckit:operationalize`  |  Create operational readiness pack with support model, runbooks, DR/BCP, on-call, and handover documentation  |  🟣 Experimental  |
|  `/arckit:traceability`  |  Generate requirements traceability matrix from requirements to design to tests  |  🟢 Live  |

### Quality & Governance

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:analyze`  |  Perform comprehensive governance quality analysis across architecture artifacts  |  🔵 Beta  |
|  `/arckit:principles-compliance`  |  Assess compliance with architecture principles and generate scorecard with evidence, gaps, and recommendations  |  🟢 Live  |
|  `/arckit:story`  |  Generate comprehensive project story with timeline analysis, traceability, and governance achievements  |  🟢 Live  |
|  `/arckit:presentation`  |  Generate MARP slide deck from project artifacts for governance boards and stakeholder briefings  |  🔵 Beta  |
|  `/arckit:conformance`  |  Assess architecture conformance — ADR decision implementation, cross-decision consistency, architecture drift, technical debt, and custom constraint rules  |  🔵 Beta  |
|  `/arckit:health`  |  Scan projects for stale research, forgotten ADRs, unresolved review conditions, orphaned requirements, missing traceability, and version drift  |  🔵 Beta  |
|  `/arckit:impact`  |  Analyse blast radius of changes — reverse dependency tracing  |  🟣 Experimental  |
|  `/arckit:search`  |  Search across all project artifacts by keyword, document type, or requirement ID  |  🔵 Beta  |
|  `/arckit:navigator`  |  Project-level GPS — show coverage against the essential ArcKit baseline, surface DRAFT/stale/orphan artifacts, and recommend the next slash command to run  |  🟢 Live  |
|  `/arckit:graph-report`  |  Governance metrics dashboard — coverage by category, cross-reference density, compliance readiness, and project comparison across all working projects  |  🟢 Live  |
|  `/arckit:customize`  |  Copy templates to `.arckit/templates-custom/` for customization (preserved across updates)  |  🟢 Live  |
|  `/arckit:maturity-model`  |  Generate capability maturity model with current-state assessment, target-state definition, and improvement roadmap  |  🔵 Beta  |
|  `/arckit:template-builder`  |  Create new document templates through interactive interview — generates community-origin templates, guides, and optional shareable bundles  |  🟠 Alpha  |


### Documentation & Publishing

| Command | Description | Status |
|---------|-------------|--------|
|  `/arckit:glossary`  |  Generate comprehensive project glossary with terms, definitions, acronyms, and cross-references  |  🔵 Beta  |
|  `/arckit:pages`  |  Generate documentation site with Mermaid diagram support  |  🟠 Alpha  |

---

## Wardley Mapping for Strategic Architecture

ArcKit uses Wardley Maps to expose the strategic position of every component before you commit to a solution. The `/arckit:wardley` command produces ready-to-visualise maps that:

- Trace user needs through the supporting value chain so gaps and duplicated effort are obvious.
- Plot evolution from Genesis → Commodity to reveal when to build, buy, reuse, or retire capabilities.
- Feed procurement, vendor evaluation, and design reviews with shared situational awareness.

Maps are emitted in the Open Wardley Map format — paste them straight into [https://create.wardleymaps.ai](https://create.wardleymaps.ai) for a visual view. Full example outputs live in the public demos such as `arckit-test-project-v3-windows11` (enterprise OS rollout strategy) and `arckit-test-project-v14-scottish-courts` (GenAI platform strategy).

---

## Architecture Diagrams with Mermaid

**ArcKit generates visual architecture diagrams using Mermaid for clear technical communication.**

### What are Architecture Diagrams?

Architecture diagrams visualize system structure, interactions, and deployment for:

- **Technical Communication**: Share architecture with stakeholders
- **Design Documentation**: Document current and future state
- **Vendor Evaluation**: Compare vendor technical approaches
- **UK Government Compliance**: Visualize Cloud First, GOV.UK services, PII handling

### Diagram Types

ArcKit supports 6 essential diagram types based on the C4 Model and enterprise architecture best practices:

| Diagram Type | Level | Purpose | When to Use |
|--------------|-------|---------|-------------|
| **C4 Context** | Level 1 | System in context with users and external systems | After requirements, to show system boundaries |
| **C4 Container** | Level 2 | Technical containers and technology choices | After HLD, for vendor review |
| **C4 Component** | Level 3 | Internal components within a container | After DLD, for implementation |
| **Deployment** | Infrastructure | Cloud resources and network topology | Cloud First compliance, cost estimation |
| **Sequence** | Interaction | API flows and request/response patterns | Integration requirements, API design |
| **Data Flow** | Data | How data moves, PII handling, GDPR compliance | UK GDPR, DPIA requirements |

Use `/arckit:diagram` directly, or supply an explicit type such as `context`, `container`, `sequence`, or `dataflow`. Outputs bundle component inventories with Wardley evolution tags, built-in GOV.UK compliance scaffolding (Notify, Pay, Design System), Cloud First network patterns, GDPR annotations, and traceability back to requirements and tests. For full examples, browse the diagram folders in `arckit-test-project-v3-windows11` and `arckit-test-project-v14-scottish-courts`.

## ServiceNow Service Management Design

ArcKit turns architecture artefacts into an operations-ready ServiceNow pack. The `/arckit:servicenow` command builds:

- CMDB hierarchies, SLAs, and change risk straight from requirements, diagrams, and Wardley Maps.
- ITIL-aligned runbooks covering incident, change, monitoring, and transition activities.
- UK government extras such as GDS Service Standard, Technology Code of Practice, and GOV.UK Pay/Notify dependencies when relevant.

For full outputs, explore the public demos (for example `arckit-test-project-v3-windows11`) where the generated ServiceNow design files and checklists are published end-to-end.

---

## Documentation

Key references live in `docs/` and top-level guides:

- Quick tour: [docs/index.html](docs/index.html) mirrors the public landing page.
- Lifecycle visuals: [WORKFLOW-DIAGRAMS.md](docs/WORKFLOW-DIAGRAMS.md) and [DEPENDENCY-MATRIX.md](docs/DEPENDENCY-MATRIX.md) cover command flow and relationships.
- Core guides: [docs/guides/principles.md](docs/guides/principles.md), [docs/guides/requirements.md](docs/guides/requirements.md), [docs/guides/procurement.md](docs/guides/procurement.md), [docs/guides/design-review.md](docs/guides/design-review.md).
- Traceability: [docs/guides/traceability.md](docs/guides/traceability.md) documents end-to-end coverage patterns.
- **DDaT Role Guides**: [docs/guides/roles/](docs/guides/roles/) — 18 guides mapping ArcKit commands to [UK Government DDaT Capability Framework](https://ddat-capability-framework.service.gov.uk/) roles (Enterprise Architect, Solution Architect, Product Manager, etc.).

---

## Comparison to Other Tools

| Feature | ArcKit | Sparx EA | Ardoq | LeanIX | Confluence |
|---------|--------|----------|-------|--------|------------|
| **AI-Assisted** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Wardley Mapping** | ✅ | ❌ | ⚠️ Limited | ❌ | ❌ |
| **Version Control** | ✅ Git | ❌ | ❌ | ❌ | ⚠️ Limited |
| **Vendor RFP** | ✅ | ❌ | ❌ | ❌ | ⚠️ Manual |
| **Design Review Gates** | ✅ | ⚠️ Manual | ❌ | ❌ | ⚠️ Manual |
| **Traceability** | ✅ Automated | ⚠️ Manual | ✅ | ⚠️ Limited | ❌ |
| **Cost** | Free | $$$$ | $$$$ | $$$$ | $$ |
| **Learning Curve** | Low | High | Medium | Medium | Low |

---

## Requirements

- **Python 3.11+**
- **Git** (optional but recommended)
- **AI Coding Agent**: [Claude Code](https://www.anthropic.com/claude-code) v2.1.219+ (via plugin), [OpenCode CLI](https://opencode.net/cli) (via CLI), or [OpenAI Codex CLI](https://chatgpt.com/features/codex) (via CLI)
- **uv** for package management: [Install uv](https://docs.astral.sh/uv/)

---

## Installation from Source

```bash
# Clone the repository
git clone https://github.com/terrygzhou/arc-kit.git
cd arc-kit

# Install in development mode
pip install -e .

# Run the CLI
arckit init my-project
```

---

## Documentation

Full guidance lives in `docs/` and the static site.

- Quick tour: [docs/index.html](docs/index.html) (mirrors the public landing page).
- Core guides: [docs/guides/principles.md](docs/guides/principles.md), [docs/guides/requirements.md](docs/guides/requirements.md), [docs/guides/procurement.md](docs/guides/procurement.md), [docs/guides/design-review.md](docs/guides/design-review.md).
- Reference packs: [WORKFLOW-DIAGRAMS.md](docs/WORKFLOW-DIAGRAMS.md) and [DEPENDENCY-MATRIX.md](docs/DEPENDENCY-MATRIX.md) cover lifecycle visualisations and the command dependency matrix.
- Traceability: [docs/guides/traceability.md](docs/guides/traceability.md) documents end-to-end requirements coverage.

## Relationship to Spec Kit

ArcKit is inspired by [Spec Kit](https://github.com/github/spec-kit) but targets a different audience:

| | Spec Kit | ArcKit |
|---|----------|--------|
| **Audience** | Product Managers, Developers | Enterprise Architects, Procurement |
| **Focus** | Feature development (0→1 code generation) | Architecture governance & vendor management |
| **Workflow** | Spec → Plan → Tasks → Code | Requirements → RFP → Design Review → Traceability |
| **Output** | Working code | Architecture documentation & governance |

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we need help**:

- Integration with enterprise tools (Jira, Azure DevOps)
- Additional AI agent support
- Template improvements based on real-world usage
- Documentation and examples
- ServiceNow API integration for automated CI creation

---

## Tips

### Continuous Governance Monitoring

Use the `/loop` command to run health checks on a recurring interval during long architecture sessions:

```bash
/loop 30m /arckit:health SEVERITY=HIGH
```

This runs `/arckit:health` every 30 minutes, surfacing stale research, forgotten ADRs, and unresolved review conditions as they appear.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/terrygzhou/arc-kit/issues)
- **Releases**: [GitHub Releases](https://github.com/terrygzhou/arc-kit/releases)
- **Latest Version**: [v6.7.5](https://github.com/terrygzhou/arc-kit/releases/tag/v6.7.5)

---

## License

MIT License - see [LICENSE](LICENSE) for details.

> **Exception:** the `plugins/arckit-uk-gcloud/` overlay is **proprietary** (not MIT) — see [`plugins/arckit-uk-gcloud/LICENSE`](plugins/arckit-uk-gcloud/LICENSE).

---

## Acknowledgements

ArcKit is inspired by the methodology and patterns from [Spec Kit](https://github.com/github/spec-kit), adapted for enterprise architecture governance workflows.

---

<p align="center">
  <img src="docs/assets/ArcKit_Logo_Horizontal_Dark.svg" alt="ArcKit" height="40">
</p>

<p align="center">
  <strong>Built with ❤️ for enterprise architects who want systematic, AI-assisted governance.</strong>
</p>
