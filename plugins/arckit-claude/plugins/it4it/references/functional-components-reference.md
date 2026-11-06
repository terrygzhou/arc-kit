# IT4IT Functional Components Reference

Full S261 Ch. 6–10 functional-component catalog: the Strategy to Portfolio,
Develop & Test, Consume & Fulfil, and Operate & Assure functions with their
components, key data objects, and KDO cardinalities. Commands and templates
pull from this file.

Source: The Open Group IT4IT Standard v3.1 (Snapshot, S261), Ch. 6–10.
Reference only — not a conformance claim.

## 1. Strategy to Portfolio (Ch. 6)

Replaces project-based IT investment. The Digital Product KDO is the business
description at the heart of the function.

| Function | Components | Primary Data Objects |
|---|---|---|
| **Strategy** | Policy · Strategy · Enterprise Architecture | Policy · Strategic Theme · Strategic Objective · Architecture Roadmap Item · Architecture Blueprint · Value Stream |
| **Portfolio** | Portfolio Backlog · Proposal · Product Portfolio | Portfolio Backlog Item · Resource Plan · Digital Product |

### Policy component

Purpose: manages creation, review, approval, and audit of Policies. Supports
Evaluate, Explore, Integrate. Key attributes: Id · Name · Description ·
Applicable Geography.
Cardinalities: Policy ↔ Digital Product (n:m) · Policy ↔ Architecture Roadmap
Item (n:m) · Policy ↔ Portfolio Backlog Item (n:m) · Policy ↔ Requirement (n:m).

### Strategy component

Purpose: manages creation and maintenance of portfolio strategy aligned with
business/enterprise strategy.

- **Strategic Theme** = a statement of direction and priorities that
  summarises Strategic Objectives, providing business context for portfolio
  decision-making.
- **Strategic Objective** = specific actionable goals and measurable outcomes
  for identified stakeholders.

### Portfolio Backlog component

Purpose: lifecycle management and visibility of Portfolio Backlog Items,
grouped into collections of work and prioritised.
Key attributes: Id · Name · Description · Prioritization · Acceptance Criteria ·
Related Products · Demand Profile · Cost Estimation.
Cardinalities: PBI ↔ Strategic Objective (n:m) · PBI ↔ Architecture Roadmap
Item (n:1) · PBI ↔ Policy (n:m) · PBI ↔ Resource Plan (1:1) · PBI ↔ Digital
Product (n:m) · PBI → Product Backlog Item (1:m).

### Proposal component

Purpose: manages Resource Plans (packages of one or more Portfolio Backlog
Items with funding). **Resource Plan** = the funding and resource commitment
for a package of Portfolio Backlog Items.
States: `proposed` · `approved` · `active` · `deferred` · `rejected`.

## 2. Develop & Test / Requirement to Deploy (Ch. 7)

| Function | Components | Primary Data Objects |
|---|---|---|
| **Develop** | Product Backlog · Requirement · Product Design · Source Control · Pipeline · Build Package · Release Composition | Product Backlog Item · Requirement · Product Design · Capacity Model · Source · Pipeline · Build Package · Product Release · Product Release Blueprint |
| **Test** | Test · Defect | Test Case · Test Plan · Defect |

The Develop function covers the full SDLC from backlog through build packages
to release composition. Pipeline covers CI/CD. Build Package is the deployable
unit. Release Composition combines build packages into a Product Release.

## 3. Consume & Fulfil / Request to Fulfill (Ch. 8)

| Function | Components | Primary Data Objects |
|---|---|---|
| **Consume** | Consumption Experience · Identity · Offering · Order · Chargeback | Interaction · Identity · Entitlement · Service Offering Catalog · Service Offering · Order · Subscription · Chargeback Contract · Chargeback Record |
| **Fulfill** | Change · Fulfillment Orchestration · Resource · Fulfillment · Usage | Change · Desired Product Instance · Resource · Capacity Plan · Fulfillment Book · Usage Record |

Consume manages the consumer lifecycle: selection → agreement → subscription →
support → status. Fulfill manages the operational side: change management,
resource provisioning, fulfillment orchestration, usage tracking.

## 4. Operate & Assure / Detect to Correct (Ch. 9)

| Function | Components | Primary Data Objects |
|---|---|---|
| **Support** | Service Level · Incident · Problem · Knowledge | Service Contract · KPI · Incident · Problem · Knowledge Item |
| **Assure** | Configuration · Monitoring · Event · Diagnostics & Remediation | Actual Product Instance · Service Monitor · Log · Event · Runbook |

Support covers service level, incident, problem, and knowledge management.
Assure covers configuration, monitoring, event handling, and
diagnostics/remediation with runbooks.

## 5. Supporting Functions (Ch. 10)

| Function | Description |
|---|---|
| **Financial Management** | Cost Modeling (Cost Model KDO) · Investment (Budget Item KDO) |
| **Governance, Risk, & Compliance** | GRC across all value streams |
| **Workforce Management** | Capacity planning for people |
| **Sourcing & Vendor Management** | Vendor lifecycle, procurement |
| **Intelligence & Reporting** | Analytics, dashboards, service reporting |
| **Collaboration & Communication** | Stakeholder communication, service status publishing |

## KDO Backbones (Ch. 11)

- **Digital Product Backbone**: Digital Product · Digital Product Contract ·
  Service Offering · System
- **Service Offering Backbone**: Service Offering · Order · Subscription

The **Digital Product** is the anchor entity: a bundle of Systems, Service
Offerings, and Contracts that delivers value to a consumer. All other KDOs
(Policy, Requirement, Release, Incident, Change) relate back to it.

## Metamodel Note (Ch. 11)

The IT4IT metamodel uses **ArchiMate 3.2** and is exchangeable via the
ArchiMate Model Exchange File Format. Hierarchy: Value Network → Value Stream
→ Functional Group → Functional Component → Key Data Object → System of
Record → Relationships (1:1, 1:m, n:m). Vendor refinements are
non-normative extensions.
