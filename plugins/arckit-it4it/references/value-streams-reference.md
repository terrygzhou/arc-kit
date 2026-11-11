# IT4IT Value Streams Reference

Full S261 Ch. 5 value-stream catalog: seven streams, their triggers, primary
stakeholders, stage sequences, cross-stream dependencies, and the complete
scenario catalog. Commands and templates pull from this file.

Source: The Open Group IT4IT Standard v3.1 (Snapshot, S261), Ch. 5.
Reference only — not a conformance claim.

## The Seven Value Streams

| # | Value Stream | Trigger | Primary Stakeholder | Stages |
|---|---|---|---|---|
| 1 | **Evaluate** | Portfolio planning cycle | Product Portfolio Manager | Gather Influencers → Identify Gaps → Propose Investments → Define Backlog Mandates → Ensure Governance |
| 2 | **Explore** | Changed Resource Plan | Product Manager | Prioritize Backlog Items → Define Digital Product Architecture → Refine Product Backlog → Finalize Roadmap & Resource Plan |
| 3 | **Integrate** | Work pulled from Product Backlog | Product Manager + Dev Teams | Plan Product Release → Design & Develop → Build, Integrate, & Test → Accept & Publish Release |
| 4 | **Deploy** | Approved Product Release | Product Manager | Plan & Approve Deployment → Fulfill Deployment → Validate Deployment → Observe Deployment |
| 5 | **Publish** | Product Release / Portfolio decision | Catalog Manager | Define Service Offering → Implement Service Offering → Publish Service Offering |
| 6 | **Consume** | Consumer selects an offering | Consumer | Select an Offering → Agree to Service Offering → Subscribe → Provide Service Support → Publish Service Status |
| 7 | **Operate** | Detected issue / scheduled maintenance | Consumer | Detect Issue → Diagnose Issue → Resolve Issue |

## Cross-Stream Dependencies

- **Evaluate** ← all streams feed ideas, improvements, and demand into it
- **Explore** depends on Evaluate (qualified Portfolio Backlog Items); if the Resource Plan cannot be met, Explore changes it
- **Integrate** pulls work from the Product Backlog; also handles emergency changes / hotfixes
- **Deploy** depends on Integrate (approved releases); used by Evaluate, Publish, Operate
- **Publish** depends on Deploy (deployed releases); feeds Consume
- **Consume** depends on Publish (catalog); responsible for creating/updating the Service Contract
- **Operate** depends on Consume (Service Contract terms); feeds back to Evaluate

## Scenario Catalog

| Value Stream | Scenarios |
|---|---|
| Evaluate | Consider a New Digital Product · Perform Digital Product Governance · Rationalize the Product Portfolio · Plan Product Portfolio Investments |
| Explore | Investigate a New Digital Product Idea · Optimize a Digital Product · Refine Digital Product Feasibility · Retire Digital Product |
| Integrate | Develop a New or Initial Product Release · Configure an Off-the-Shelf or SaaS Product · Deliver an Emergency Change or Hotfix · Update of a Vendor Product |
| Deploy | Deploy a First Product Release · Deploy a New Product Release Version · Disable or Remove Existing Product Release Instances |
| Publish | Publish a New Service Offering · Change an Existing Service Offering · Bundle Existing Service Offerings · Terminate a Service Offering |
| Consume | Order a New Desired Product Instance · Order an Instance Modification · Order an Instance Termination · Order Instance Support |
| Operate | Remediate an Identified Back-End Issue · Ensure Disaster Recovery Objectives · Remediate a Major Event or Incident · Remediate a Consumer Front-End Issue · Perform Scheduled Maintenance |

## Documentation Pattern (per stream)

Each value stream is documented with:

- **Scenario** — the trigger condition and use case
- **Value Stream Stage** — the sequence of activities
- **Stakeholder** — who is responsible and who is affected
- **Participating Data Objects** — which KDOs flow through the stages
- **Participating Functional Components** — which functional components support each stage
