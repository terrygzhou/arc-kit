---
description: "Phase C.2 — Data Architecture: data entities, data governance framework, data management strategy, reference/master data"
argument-hint: "<project ID or name, e.g. '001', 'data architecture landscape'>"
effort: high
handoffs:
  - command: application-rationalization
    description: "Rationalize application portfolio based on data architecture"
  - command: technology-architecture
    description: "Design technology architecture to support data architecture"
---

You are helping an enterprise architect create a **Data Architecture** document for Phase C.2 of the TOGAF Architecture Development Method (ADM). This document defines the data entities, data governance framework, data management strategy, and reference/master data landscape that supports the target enterprise architecture.

## User Input

```text
$ARGUMENTS
```

## Prerequisites: Read Foundational Artifacts

> **Note**: The ArcKit Project Context hook has already detected all projects, artifacts, external documents, and global policies. Use that context below — no need to scan directories manually.

**MANDATORY** (warn if missing):

- **BPCM** (Business Capability Map) — Extract: Capability hierarchy, data-heavy capabilities, data ownership by capability area, information needs
  - If missing: STOP and ask user to run `/arckit:business-capability-map` first. Data architecture must be grounded in business capabilities.
- **APP** (Application Inventory) — Extract: Application-to-data mappings, existing data stores, data ownership by system, technology stack for data platforms
  - If missing: STOP and ask user to run `/arckit:application-inventory` first. Data architecture requires understanding of existing data assets.
- **PRIN** (Architecture Principles, in 000-global) — Extract: Data governance principles, technology standards, security classification rules
  - If missing: STOP and ask user to run `/arckit:principles` first. Data architecture must be grounded in enterprise principles.

**RECOMMENDED** (read if available, note if missing):

- **ADMP** (Architecture Vision / Preliminary ADM) — Extract: Scope boundaries, strategic vision, success criteria
- **STRAT** (Architecture Strategy) — Extract: Strategic themes, investment priorities, data modernisation goals

### Prerequisites 1b: Read external documents and policies

- Read any **external documents** listed in the project context (`external/` files) — extract existing data models, data governance policies, data classification frameworks, data dictionaries
- Read any **enterprise standards** in `projects/000-global/external/` — extract enterprise data standards, data classification schemes, data protection policies, regulatory requirements
- If no external data docs found but they would improve the output, ask: "Do you have any existing data models, data governance policies, or data dictionaries? I can read PDFs, spreadsheets, and images directly. Place them in `projects/{project-dir}/external/` and re-run, or skip."
- **Citation traceability**: When referencing content from external documents, follow the citation instructions in `${CLAUDE_PLUGIN_ROOT}/references/citation-instructions.md`. Place inline citation markers (e.g., `[DA-C1]`) next to findings informed by source documents and populate the "External References" section in the template.

## Instructions

### 1. Identify or Create Project

Identify the target project from the hook context. If the user specifies a project that doesn't exist yet, create a new project:

1. Use Glob to list `projects/*/` directories and find the highest `NNN-*` number (or start at `001` if none exist)
2. Calculate the next number (zero-padded to 3 digits, e.g., `002`)
3. Slugify the project name (lowercase, replace non-alphanumeric with hyphens, trim)
4. Use the Write tool to create `projects/{NNN}-{slug}/README.md` with the project name, ID, and date — the Write tool will create all parent directories automatically
5. Also create `projects/{NNN}-{slug}/external/README.md` with a note to place external reference documents here
6. Set `PROJECT_ID` = the 3-digit number, `PROJECT_PATH` = the new directory path

### 2. Read Data Architecture Template

**Read the template** (with user override support):

- **First**, check if `.arckit/templates-custom/data-architecture-template.md` exists in the project root
- **If found**: Read the user's customised template (user override takes precedence)
- **If not found**: Read `${CLAUDE_PLUGIN_ROOT}/templates/data-architecture-template.md` (default)

> **Tip**: Users can customise templates with `/arckit:customize data-architecture`

### 3. Clarify Data Scope with User

Before generating the document, ask the user about the scope of the data architecture:

**AskUserQuestion**: "What is the scope of this data architecture assessment?"

- Options: `Enterprise-wide` | `Business Unit` | `Specific Domain`
- Default: `Business Unit`

### 4. Generate Data Architecture Document

Create the Data Architecture document following the template structure. Populate all sections with content derived from the available artifacts.

#### Document Control

- Generate Document ID: `ARC-{P}-DATA-v1.0` (for filename: `ARC-{P}-DATA-v1.0.md`)
- Set owner, dates, status, classification
- Review cycle: Monthly during active ADM cycle

#### Data Architecture Vision

- **2-3 paragraph narrative** articulating the target data architecture state
- Ground the vision in principles from PRIN (data governance, data quality, data security)
- Reference business drivers from BPCM (which capabilities drive data needs)
- If STRAT is available, align with data modernisation strategic themes

#### Data Entities Catalog

Build a comprehensive catalog of data entities:

- **Data domains**: Group entities by business domain (e.g., Customer, Product, Finance, Operations)
- **Data entities**: For each domain, list key entities with attributes, data types, and cardinality
- **Data ownership**: Map each entity to an owner (business and technical)
- **Classification**: Classify each entity (e.g., Public, Internal, Confidential, Restricted)
- **Sensitivity**: Flag sensitive data (PII, financial, health, classified)

#### Data Governance Framework

Define the data governance structure:

- **Data stewardship model**: Roles, responsibilities, RACI for data governance
- **Data quality standards**: Completeness, accuracy, consistency, timeliness, validity thresholds
- **Data classification scheme**: Categories, handling requirements, retention periods
- **Data retention policy**: Legal hold, archival, deletion schedules by data class
- **Data governance body**: Decision-making authority, escalation paths, compliance monitoring

#### Data Management Strategy

Define how data will be managed across the enterprise:

- **Data lifecycle management**: Creation, storage, processing, archiving, destruction
- **Integration patterns**: Point-to-point, hub-and-spoke, bus-based, event-driven
- **Data flow architecture**: Source systems, transformation layers, data warehouses/lakes, consumption endpoints
- **Data platform strategy**: On-premise, cloud, hybrid — storage technologies, processing engines
- **Master data management**: Golden records, reconciliation processes, data matching

#### Reference & Master Data

Define shared data definitions and master data:

- **Shared data definitions**: Standard data types, codes, enumerations across the enterprise
- **Golden records**: Authoritative sources for master entities (Customer, Product, Employee, Location)
- **Data dictionary**: Standardised field names, types, formats, valid values
- **Code sets**: Common reference data (country codes, currency codes, status codes)

#### Data Architecture Principles

Derive data-specific principles from PRIN:

- For each relevant enterprise principle, state its specific data architecture implications
- Add any data-specific principles not covered by enterprise principles
- Ensure all principles are actionable and non-contradictory

#### Mermaid Diagram — Data Domain Map

Create a Mermaid flowchart or C4-style diagram showing:

- Data domains as system boundaries
- Key data entities within each domain
- Data flows between domains and applications (from APP)
- Integration points and data sharing agreements

#### Traceability

- Link each data domain to BPCM capability areas
- Link each data entity to APP systems that produce/consume it
- Link data principles to PRIN enterprise principles
- Link data governance to compliance frameworks from external documents

### 5. UK Government Specifics

If the user indicates this is a UK Government project, include:

- **Financial Year Notation**: Use "FY 2024/25", "FY 2025/26" format
- **Spending Review Alignment**: Reference SR periods for data platform investment
- **GDS Service Standard**: Reference Discovery/Alpha/Beta/Live phases for data services
- **TCoP (Technology Code of Practice)**: Reference 13 points — particularly data security and privacy
- **NCSC CAF**: Security maturity progression for data protection
- **Cross-Government Services**: GOV.UK Pay, Notify, Design System — data sharing with shared services
- **G-Cloud/DOS**: Procurement alignment for data platform services
- **DCB (Data Capability Building)**: Government data maturity assessment framework
- **National Data Strategy**: Alignment with the UK's National Data Strategy priorities

### 6. MOD Specifics

If this is a Ministry of Defence project, include:

- **JSP 440**: Defence project management alignment for data architecture workstreams
- **Security Classifications**: OFFICIAL, SECRET, TOP SECRET data handling requirements
- **IAMM**: Information assurance maturity for data systems — minimum IAMM Level 2 for SECRET
- **JSP 936**: AI assurance — data requirements for AI/ML models (if applicable)
- **MOD Data Standard (DCMD)**: Defence data management standards
- **DSTI Data Strategy**: Alignment with Defence Science and Technology data strategy

### 7. Load Mermaid Syntax References

Read `${CLAUDE_PLUGIN_ROOT}/skills/mermaid-syntax/references/flowchart.md` for official Mermaid syntax — node shapes, edge labels, and styling options for data flow diagrams.

### 8. Quality Gate

Before writing the file, read `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` and verify all **Common Checks** plus the **DATA** per-type checks pass. Fix any failures before proceeding.

**DATA-specific quality requirements**:

- Data entities catalog contains at least 3 data domains with entities
- Data governance framework includes stewardship model, quality standards, classification, and retention
- Data management strategy covers lifecycle, integration patterns, and data flows
- Reference & master data section includes at least one shared data definition
- Data architecture principles section has at least 3 principles derived from PRIN
- Mermaid data domain diagram is present

### 9. Write the Data Architecture File

**IMPORTANT**: The Data Architecture document will be a substantial document (typically 250-400 lines). You MUST use the Write tool to create the file, NOT output the full content in chat.

Create the file at:

```text
projects/{P}/ARC-{P}-DATA-v1.0.md
```

Use the Write tool with the complete content following the template structure.

### 10. Show Summary to User

After writing the file, show a concise summary (NOT the full document):

```markdown
## Data Architecture Created

**Document**: `projects/{P}/ARC-{P}-DATA-v1.0.md`
**Document ID**: ARC-{P}-DATA-v1.0

### Data Architecture Scope
- **Scope**: [Enterprise-wide / Business Unit / Specific Domain]
- **Data Domains**: [N] domains identified
- **Data Entities**: [N] entities catalogued

### Data Governance
- **Stewardship Model**: [Defined / Partial / Placeholder]
- **Quality Standards**: [N] standards defined
- **Classification Scheme**: [N] data classes

### Data Management
- **Lifecycle Stages**: [Creation → Storage → Processing → Archiving → Destruction]
- **Integration Patterns**: [Pattern 1], [Pattern 2], [Pattern 3]
- **Master Data Entities**: [N] golden records identified

### Reference & Master Data
- **Shared Definitions**: [N] standard definitions
- **Code Sets**: [N] reference datasets

### Data Architecture Principles
- **Principles derived from PRIN**: [N]
- **Data-specific principles**: [N]

### Synthesised From
- ✅ Business Capability Map: ARC-{P}-BPCM-v[N].md
- ✅ Application Inventory: ARC-{P}-APP-v[N].md
- ✅ Architecture Principles: ARC-000-PRIN-v[N].md
- [✅/⚠️] Architecture Vision: ARC-{P}-ADMP-v[N].md
- [✅/⚠️] Architecture Strategy: ARC-{P}-STRAT-v[N].md

### Next Steps
1. Review Data Architecture with Data Governance Board / Architecture Board
2. Validate data entities with domain data owners
3. Design technology architecture to support data platforms: `/arckit:technology-architecture`
4. Rationalise application portfolio based on data architecture: `/arckit:application-rationalization`

### Traceability
- [N] data domains mapped to [N] business capabilities (BPCM)
- [N] data entities linked to [N] applications (APP)
- [N] data principles derived from [N] enterprise principles (PRIN)

**File location**: `projects/{P}/ARC-{P}-DATA-v1.0.md`
```

## Important Notes

1. **Business-Grounded Data Architecture**: This document must be grounded in business capabilities (BPCM) and existing application inventory (APP). Do not invent data entities without evidence from source artifacts.

2. **Governance First**: Data governance is the foundation — without stewardship, quality, and classification, the data architecture has no operational meaning. Define governance before technical details.

3. **Use Write Tool**: The data architecture document is typically 250-400 lines. ALWAYS use the Write tool to create it. Never output the full content in chat.

4. **Mandatory Prerequisites**: BPCM and APP are mandatory prerequisites. Data architecture without understanding of business capabilities and existing data assets is speculative. PRIN is mandatory for principle alignment.

5. **Reference Data is Foundation**: Master data and reference data are the backbone of enterprise data interoperability. Define shared definitions early to prevent siloed data models.

6. **Traceability is Critical**: Every data entity, governance rule, and principle must trace back to source documents. This ensures the data architecture is grounded in evidence, not assumptions.

7. **Integration with Other Commands**:
   - **Input**: Requires BPCM (business capabilities), APP (application/data assets), PRIN (principles)
   - **Output**: Feeds `/arckit:technology-architecture` (platform design), `/arckit:application-rationalization` (portfolio decisions)

8. **Version Management**: If a data architecture document already exists (`ARC-*-DATA-v*.md`), create a new version (v2.0) rather than overwriting. Track data architecture evolution across ADM cycles.

9. **TOGAF Alignment**: This document maps to TOGAF ADM Phase C.2 (Data Architecture) outputs: Data entities, data security, interoperability, migration constraints, and data architecture requirements.

10. **Markdown escaping**: When writing less-than or greater-than comparisons, always include a space after `<` or `>` (e.g., `< 3 seconds`, `> 99.9% uptime`) to prevent markdown renderers from interpreting them as HTML tags or emoji