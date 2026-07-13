---
description: Phase D — Technology Architecture: infrastructure, platform, network, deployment, integration architecture
argument-hint: "<project ID or name, e.g. '001', 'technology architecture landscape'>"
effort: high
handoffs:
  - command: gap-analysis
    description: Analyze gaps between current and target technology architecture
  - command: transition-architecture
    description: Plan migration from current to target technology state
---

You are helping an enterprise architect create a **Technology Architecture** document for Phase D of the TOGAF Architecture Development Method (ADM). This document defines the infrastructure, platform, network, deployment, and integration architecture that supports the target enterprise architecture.

## User Input

```text
$ARGUMENTS
```

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (warn if missing):

- **APP** (Application Inventory) — Extract: Application portfolio, existing technology stack, hosting models, infrastructure dependencies
  - If missing: STOP and ask user to run `/arckit:application-inventory` first. Technology architecture requires understanding of existing technology assets.
- **DATA** (Data Architecture) — Extract: Data platform requirements, storage needs, data processing requirements, data security classifications
  - If missing: STOP and ask user to run `/arckit:data-architecture` first. Technology architecture must support data architecture requirements.
- **PRIN** (Architecture Principles, in 000-global) — Extract: Technology standards, approved technology stack, prohibited technologies, cloud strategy
  - If missing: STOP and ask user to run `/arckit:principles` first. Technology architecture must be grounded in enterprise principles.

**RECOMMENDED** (read if available, note if missing):

- **ADMP** (Architecture Vision / Preliminary ADM) — Extract: Scope boundaries, strategic vision, success criteria
- **STRAT** (Architecture Strategy) — Extract: Strategic themes, investment priorities, technology modernisation roadmap
- **BPCM** (Business Capability Map) — Extract: Capabilities requiring technology support, performance requirements, availability requirements

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract existing technology landscape assessments, infrastructure inventories, network diagrams, cloud strategy documents
- Read any **enterprise standards** in `projects/000-global/external/` — extract technology standards, procurement policies, security baselines, approved vendor lists
- If no external technology docs found but they would improve the output, ask: "Do you have any existing technology landscape assessments, infrastructure inventories, or cloud strategy documents? I can read PDFs, spreadsheets, and images directly. Place them in `projects/{project-dir}/external/` and re-run, or skip."
- **Citation traceability**: When referencing content from external documents, follow the citation instructions in `${CLAUDE_PLUGIN_ROOT}/references/citation-instructions.md`. Place inline citation markers (e.g., `[TA-C1]`) next to findings informed by source documents and populate the "External References" section in the template.

## Instructions

### 1. Identify or Create Project

Identify the target project from the hook context. If the user specifies a project that doesn't exist yet, create a new project:

1. Use Glob to list `projects/*/` directories and find the highest `NNN-*` number (or start at `001` if none exist)
2. Calculate the next number (zero-padded to 3 digits, e.g., `002`)
3. Slugify the project name (lowercase, replace non-alphanumeric with hyphens, trim)
4. Use the Write tool to create `projects/{NNN}-{slug}/README.md` with the project name, ID, and date — the Write tool will create all parent directories automatically
5. Also create `projects/{NNN}-{slug}/external/README.md` with a note to place external reference documents here
6. Set `PROJECT_ID` = the 3-digit number, `PROJECT_PATH` = the new directory path

### 2. Read Technology Architecture Template

**Read the template** (with user override support):

- **First**, check if `.arckit/templates-custom/tech-architecture-template.md` exists in the project root
- **If found**: Read the user's customised template (user override takes precedence)
- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/tech-architecture-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize technology-architecture`

### 3. Clarify Technology Scope with User

Before generating the document, ask the user about the scope of the technology architecture:

**AskUserQuestion**: "What is the scope of this technology architecture assessment?"

- Options: `Enterprise-wide` | `Business Unit` | `Specific Platform`
- Default: `Business Unit`

### 4. Generate Technology Architecture Document

Create the Technology Architecture document following the template structure. Populate all sections with content derived from the available artifacts.

#### Document Control

- Generate Document ID: `ARC-{P}-TECH-v1.0` (for filename: `ARC-{P}-TECH-v1.0.md`)
- Set owner, dates, status, classification
- Review cycle: Monthly during active ADM cycle

#### Technology Architecture Vision

- **2-3 paragraph narrative** articulating the target technology state
- Ground the vision in principles from PRIN (technology standards, cloud strategy, security)
- Reference business drivers from BPCM (which capabilities drive technology needs)
- If STRAT is available, align with technology modernisation strategic themes

#### Infrastructure Architecture

Define the physical and virtual infrastructure:

- **Compute**: Server types, virtualisation strategy, edge computing, HPC requirements
- **Storage**: Block, file, object storage — capacity planning, tiering strategy
- **Networking**: LAN/WAN, SDN, network segmentation, bandwidth requirements
- **Hosting Model**: Cloud (public/private), on-premise, hybrid — rationale and decision criteria
- **Infrastructure as Code**: Automation approach (Terraform, Ansible, CloudFormation)
- **Capacity Planning**: Current capacity, projected growth, scaling strategy

#### Platform Architecture

Define the software platforms and middleware:

- **Middleware**: API gateways, service meshes, message brokers, ESB
- **Containers & Orchestration**: Container runtimes, Kubernetes vs. managed K8s, service mesh
- **CI/CD Pipeline**: Build, test, deployment automation, environment promotion
- **Observability**: Logging, monitoring, alerting, APM (Application Performance Monitoring)
- **Platform Services**: Identity provider, configuration management, secret management
- **Developer Platform**: Self-service capabilities, inner-loop tooling, sandbox environments

#### Integration Architecture

Define how systems communicate:

- **API Design**: REST, GraphQL, gRPC — standards, versioning, governance
- **Messaging Patterns**: Synchronous vs. asynchronous, event-driven architecture
- **EAI Patterns**: Enterprise Service Bus, API-led connectivity, event-driven integration
- **Data Integration**: ETL, ELT, CDC (Change Data Capture), streaming
- **Protocol Standards**: HTTP/2, gRPC, AMQP, MQTT, SNMP
- **Integration Security**: mTLS, OAuth2, API key management, rate limiting
- **Service Registry & Discovery**: Dynamic service location, health checks

#### Deployment Architecture

Define how systems are deployed and operated:

- **Environments**: Dev, Test, Staging, Production — isolation and promotion strategy
- **Regions & Availability**: Geographic distribution, multi-region vs. single-region
- **High Availability**: Active-active, active-passive, failover strategy, RTO/RPO targets
- **Disaster Recovery**: Backup strategy, replication, recovery testing cadence
- **Scaling**: Horizontal vs. vertical, auto-scaling policies, capacity thresholds
- **Release Cadence**: Deployment frequency, blue-green vs. canary vs. rolling

#### Technology Standards

Define the approved and prohibited technology stack:

- **Approved Technologies**: Curated list of approved platforms, frameworks, databases
- **Prohibited Technologies**: Technologies that are not permitted (with rationale)
- **Evaluation Process**: Criteria and process for adding new technologies
- **Upgrade Policy**: Lifecycle management, supported versions, EOL tracking
- **Vendor Strategy**: Multi-vendor vs. preferred vendor, licence management

#### Mermaid Diagram — Technology Landscape

Create a Mermaid flowchart or deployment diagram showing:

- Infrastructure layers (compute, storage, network)
- Platform services and their relationships
- Application deployment targets
- Integration patterns and data flows
- Security boundaries and trust zones

#### Traceability

- Link technology decisions to APP (application technology stack)
- Link platform design to DATA (data architecture requirements)
- Link technology standards to PRIN (enterprise technology principles)
- Link deployment strategy to STRAT (technology modernisation goals)
- Link infrastructure to BPCM (capability performance requirements)

### 5. UK Government Specifics

If the user indicates this is a UK Government project, include:

- **Financial Year Notation**: Use "FY 2024/25", "FY 2025/26" format
- **Spending Review Alignment**: Reference SR periods for technology investment
- **GDS Service Standard**: Reference Discovery/Alpha/Beta/Live phases for technology services
- **TCoP (Technology Code of Practice)**: Reference 13 points — particularly standard technology, security by design
- **NCSC CAF**: Cyber Assessment Framework — security maturity progression for technology platforms
- **Cross-Government Services**: GOV.UK Pay, Notify, Design System — platform interoperability
- **G-Cloud/DOS**: G-Cloud procurement framework alignment for technology services
- **CloudFirst Policy**: Mandate for cloud-first procurement decisions
- **Open Standards**: Government preference for open standards and interoperability

### 6. MOD Specifics

If this is a Ministry of Defence project, include:

- **JSP 440**: Defence project management alignment for technology workstreams
- **Defiance Programme**: MOD Cloud Programme — cloud adoption status and requirements
- **Security Classifications**: OFFICIAL, SECRET, TOP SECRET infrastructure requirements
- **IAMM**: Information assurance maturity for technology platforms — minimum IAMM Level 2 for SECRET systems
- **JSP 936**: AI assurance — technology requirements for AI/ML infrastructure (if applicable)
- **SSE**: Single Source Estate compliance for commercial technology tools
- **MOD Data Centre Programme**: Data centre consolidation and modernisation alignment
- **Network Architecture**: MOD network strategy — DCS, JWICS, ACDS segregation

### 7. Load Mermaid Syntax References

Read `${CLAUDE_PLUGIN_ROOT}/skills/mermaid-syntax/references/flowchart.md` for official Mermaid syntax — node shapes, edge labels, and styling options for deployment diagrams.

### 8. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** plus the **TECH** per-type checks pass. Fix any failures before proceeding.

**TECH-specific quality requirements**:

- Infrastructure architecture covers compute, storage, networking, and hosting model
- Platform architecture addresses middleware, containers, CI/CD, and observability
- Integration architecture defines APIs, messaging, and security patterns
- Deployment architecture specifies environments, HA, DR, and scaling
- Technology standards include approved stack and prohibited technologies
- Mermaid technology landscape diagram is present

### 9. Write the Technology Architecture File

**IMPORTANT**: The Technology Architecture document will be a substantial document (typically 250-400 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-TECH-v1.0.md
```

Use the Write tool with the complete content following the template structure.

### 10. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## Technology Architecture Created

**Document**: `projects/{P}/ARC-{P}-TECH-v1.0.md`
**Document ID**: ARC-{P}-TECH-v1.0

### Technology Architecture Scope
- **Scope**: [Enterprise-wide / Business Unit / Specific Platform]
- **Hosting Model**: [Cloud / On-Premise / Hybrid]
- **Infrastructure Layers**: [N] layers defined

### Platform Architecture
- **Middleware**: [Component 1], [Component 2], [Component 3]
- **Containers**: [Runtime] with [Orchestrator]
- **CI/CD**: [Pipeline approach] — [N] environments
- **Observability**: [Logging] + [Monitoring] + [APM]

### Integration Architecture
- **API Standards**: [Style] with [governance approach]
- **Messaging**: [Pattern] — [broker/platform]
- **Protocols**: [N] protocol standards defined
- **Integration Security**: [Approach]

### Deployment Architecture
- **Environments**: [N] environments (Dev → Test → Staging → Prod)
- **Availability**: [Strategy] — RTO: [X], RPO: [Y]
- **Disaster Recovery**: [Strategy] — tested every [period]
- **Scaling**: [Approach] — [thresholds]

### Technology Standards
- **Approved technologies**: [N] technologies in approved stack
- **Prohibited technologies**: [N] technologies explicitly prohibited
- **Upgrade policy**: [Policy approach]

### Synthesised From
- ✅ Application Inventory: ARC-{P}-APP-v[N].md
- ✅ Data Architecture: ARC-{P}-DATA-v[N].md
- ✅ Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] Architecture Vision: ARC-{P}-ADMP-v[N].md
- [✅/⚠️] Architecture Strategy: ARC-{P}-STRAT-v[N].md

### Next Steps
1. Review Technology Architecture with Technology Board / Architecture Board
2. Perform gap analysis against current state: `/arckit:gap-analysis`
3. Plan migration to target technology state: `/arckit:transition-architecture`
4. Validate technology standards with procurement

### Traceability
- [N] technology decisions linked to [N] application requirements (APP)
- [N] platform components designed for [N] data architecture requirements (DATA)
- [N] technology standards derived from [N] enterprise principles (PRIN)
- [N] deployment patterns aligned with [N] strategic themes (STRAT)

**File location**: `projects/{P}/ARC-{P}-TECH-v1.0.md`
```

## Important Notes

1. **Evidence-Based Technology Selection**: This document must be grounded in existing application inventory (APP) and data architecture (DATA). Do not invent technology stacks without evidence from source artifacts.

2. **Standards Drive Consistency**: Technology standards are the mechanism that prevents technology sprawl. Define approved stacks early and reference them in all downstream decisions.

3. **Use Write Tool**: The technology architecture document is typically 250-400 lines. ALWAYS use the Write tool to create it. Never output the full content in chat.

4. **Mandatory Prerequisites**: APP and DATA are mandatory prerequisites. Technology architecture without understanding of existing applications and data requirements is disconnected from reality. PRIN is mandatory for principle alignment.

5. **Deployment Drives Resilience**: High availability and disaster recovery are not afterthoughts — they must be designed into the deployment architecture from the start. Define RTO/RPO targets explicitly.

6. **Traceability is Critical**: Every technology decision must trace back to source documents. This ensures the technology architecture is grounded in business needs, not technology preference.

7. **Integration with Other Commands**:
   - **Input**: Requires APP (technology baseline), DATA (data platform requirements), PRIN (technology principles)
   - **Output**: Feeds `/arckit:gap-analysis` (current vs. target gaps), `/arckit:transition-architecture` (migration planning)

8. **Version Management**: If a technology architecture document already exists (`ARC-*-TECH-v*.md`), create a new version (v2.0) rather than overwriting. Track technology architecture evolution across ADM cycles.

9. **TOGAF Alignment**: This document maps to TOGAF ADM Phase D (Technology Architecture) outputs: Technology infrastructure, platform services, integration technology, deployment topology, and technology standards.

10. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji