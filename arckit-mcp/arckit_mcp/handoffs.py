"""Generated handoff graph.

DO NOT EDIT BY HAND. This file is regenerated from the ``handoffs:``
frontmatter in the command markdown under
``plugins/arckit-{claude,oaa,it4it,togaf-adm}/commands/`` by
``scripts/generate-mcp-handoffs.py``.

Shape: ``HANDOFFS[command] = [(target, condition_text, condition_code), ...]``.
``condition_text`` is ``""`` when the handoff has no condition;
``condition_code`` is the doc-type code the condition references
when detectable, else ``""``.
"""

from __future__ import annotations


HANDOFFS: dict = {
    "arckit-claude/adr": [
        ("hld-review", "", ""),
        ("diagram", "", ""),
        ("traceability", "", ""),
    ],
    "arckit-claude/archimate": [
        ("diagram", "", ""),
        ("hld-review", "", ""),
    ],
    "arckit-claude/aws-research": [
        ("diagram", "", ""),
        ("devops", "", ""),
        ("finops", "", ""),
        ("adr", "", ""),
    ],
    "arckit-claude/azure-research": [
        ("diagram", "", ""),
        ("devops", "", ""),
        ("finops", "", ""),
        ("adr", "", ""),
    ],
    "arckit-claude/backlog": [
        ("trello", "", ""),
        ("traceability", "", ""),
    ],
    "arckit-claude/bmm": [
        ("strategy", "", ""),
        ("roadmap", "", ""),
        ("sobc", "", ""),
        ("archimate", "", ""),
    ],
    "arckit-claude/competitors": [
        ("research", "", ""),
        ("score", "", ""),
        ("risk", "", ""),
    ],
    "arckit-claude/data-model": [
        ("hld-review", "", ""),
        ("dld-review", "", ""),
        ("sow", "", ""),
        ("traceability", "", ""),
    ],
    "arckit-claude/datascout": [
        ("data-model", "", ""),
        ("research", "", ""),
        ("adr", "", ""),
        ("dpia", "", ""),
        ("diagram", "", ""),
        ("traceability", "", ""),
    ],
    "arckit-claude/framework": [
        ("glossary", "", ""),
        ("maturity-model", "", ""),
    ],
    "arckit-claude/gcp-research": [
        ("diagram", "", ""),
        ("devops", "", ""),
        ("finops", "", ""),
        ("adr", "", ""),
    ],
    "arckit-claude/glossary": [
        ("data-model", "", ""),
    ],
    "arckit-claude/gov-code-search": [
        ("gov-reuse", "", ""),
        ("research", "", ""),
        ("adr", "", ""),
    ],
    "arckit-claude/gov-landscape": [
        ("gov-reuse", "", ""),
        ("framework", "", ""),
        ("wardley", "", ""),
    ],
    "arckit-claude/gov-reuse": [
        ("research", "", ""),
        ("adr", "", ""),
        ("requirements", "", ""),
    ],
    "arckit-claude/grants": [
        ("sobc", "", ""),
        ("plan", "", ""),
        ("risk", "", ""),
        ("adr", "", ""),
    ],
    "arckit-claude/impact": [
        ("traceability", "Impact analysis revealed traceability gaps", ""),
        ("health", "Impacted documents may be stale", ""),
        ("conformance", "Impact includes architecture design documents", ""),
    ],
    "arckit-claude/maturity-model": [
        ("roadmap", "", ""),
        ("strategy", "", ""),
    ],
    "arckit-claude/requirements": [
        ("data-model", "DR-xxx data requirements were generated", ""),
        ("research", "", ""),
        ("risk", "", ""),
        ("dpia", "", ""),
    ],
    "arckit-claude/research": [
        ("wardley", "", ""),
        ("sobc", "", ""),
        ("sow", "", ""),
        ("hld-review", "", ""),
        ("tenders", "UK government procurement context", ""),
    ],
    "arckit-claude/risk": [
        ("sobc", "", ""),
        ("requirements", "", ""),
        ("secure", "", ""),
        ("tenders", "UK government procurement context", ""),
    ],
    "arckit-claude/roadmap": [
        ("backlog", "", ""),
        ("plan", "", ""),
    ],
    "arckit-claude/score": [
        ("evaluate", "No EVAL artifact exists for the project", ""),
        ("sow", "Vendor selection complete, ready for procurement", ""),
        ("competitors", "UK government procurement context", ""),
    ],
    "arckit-claude/search": [
        ("health", "Search revealed potentially stale artifacts", ""),
        ("traceability", "Search included requirement IDs", ""),
        ("impact", "User wants to understand change blast radius", ""),
    ],
    "arckit-claude/sobc": [
        ("requirements", "", ""),
        ("roadmap", "", ""),
        ("tenders", "UK government procurement context", ""),
    ],
    "arckit-claude/solution-design": [
        ("hld-review", "", ""),
        ("dld-review", "", ""),
        ("traceability", "", ""),
        ("sow", "", ""),
        ("diagram", "", ""),
    ],
    "arckit-claude/sow": [
        ("evaluate", "", ""),
        ("dos", "", ""),
    ],
    "arckit-claude/stakeholders": [
        ("requirements", "", ""),
        ("risk", "", ""),
        ("sobc", "", ""),
    ],
    "arckit-claude/strategy": [
        ("requirements", "", ""),
        ("roadmap", "", ""),
        ("diagram", "", ""),
    ],
    "arckit-claude/template-builder": [
        ("customize", "User wants to customize an existing template rather than build a new one", ""),
    ],
    "arckit-claude/tenders": [
        ("sobc", "", ""),
        ("risk", "", ""),
        ("research", "", ""),
    ],
    "arckit-claude/wardley": [
        ("roadmap", "", ""),
        ("strategy", "", ""),
        ("research", "Custom-Built components identified that need market research", ""),
        ("wardley.doctrine", "", ""),
        ("wardley.gameplay", "", ""),
        ("wardley.climate", "", ""),
    ],
    "arckit-claude/wardley.climate": [
        ("wardley.gameplay", "", ""),
        ("wardley", "Climate analysis reveals evolution velocity changes", ""),
    ],
    "arckit-claude/wardley.doctrine": [
        ("wardley", "Doctrine gaps affect component positioning or strategy", ""),
        ("wardley.gameplay", "", ""),
    ],
    "arckit-claude/wardley.gameplay": [
        ("roadmap", "", ""),
        ("strategy", "", ""),
        ("wardley.climate", "Climate assessment not yet performed", ""),
    ],
    "arckit-claude/wardley.value-chain": [
        ("wardley", "", ""),
        ("wardley.doctrine", "Value chain reveals organizational capability gaps", ""),
    ],
    "arckit-it4it/it4it-consume-fulfil": [
        ("it4it-operate-assure", "", ""),
        ("it4it-develop-test", "", ""),
    ],
    "arckit-it4it/it4it-develop-test": [
        ("it4it-strategy-portfolio", "", ""),
        ("it4it-consume-fulfil", "", ""),
    ],
    "arckit-it4it/it4it-operate-assure": [
        ("it4it-consume-fulfil", "", ""),
        ("it4it-value-stream", "", ""),
    ],
    "arckit-it4it/it4it-strategy-portfolio": [
        ("it4it-develop-test", "", ""),
        ("it4it-value-stream", "", ""),
    ],
    "arckit-it4it/it4it-value-network": [
        ("it4it-value-stream", "", ""),
        ("it4it-strategy-portfolio", "", ""),
    ],
    "arckit-it4it/it4it-value-stream": [
        ("it4it-value-network", "", ""),
        ("it4it-strategy-portfolio", "", ""),
    ],
    "arckit-oaa/agile-governance": [
        ("oaa-adm-lite", "", ""),
        ("agile-security", "", ""),
    ],
    "arckit-oaa/agile-security": [
        ("agile-governance", "", ""),
        ("agile-strategy", "", ""),
    ],
    "arckit-oaa/agile-strategy": [
        ("agile-security", "", ""),
        ("agile-governance", "", ""),
    ],
    "arckit-oaa/oaa-adm-lite": [
        ("product-architecture", "", ""),
        ("agile-strategy", "", ""),
        ("agile-security", "", ""),
        ("agile-governance", "", ""),
    ],
    "arckit-oaa/product-architecture": [
        ("agile-strategy", "", ""),
        ("agile-security", "", ""),
    ],
    "arckit-togaf-adm/adm-preliminary": [
        ("business-capability-map", "", ""),
        ("gap-analysis", "", ""),
    ],
    "arckit-togaf-adm/application-inventory": [
        ("application-rationalization", "", ""),
        ("gap-analysis", "", ""),
    ],
    "arckit-togaf-adm/application-rationalization": [
        ("gap-analysis", "", ""),
        ("transition-architecture", "", ""),
    ],
    "arckit-togaf-adm/architecture-board": [
        ("architecture-change", "", ""),
    ],
    "arckit-togaf-adm/architecture-change": [
        ("transition-architecture", "", ""),
        ("gap-analysis", "", ""),
    ],
    "arckit-togaf-adm/architecture-repository": [
        ("adm-preliminary", "", ""),
    ],
    "arckit-togaf-adm/business-capability-map": [
        ("gap-analysis", "", ""),
        ("application-inventory", "", ""),
    ],
    "arckit-togaf-adm/data-architecture": [
        ("application-rationalization", "", ""),
        ("technology-architecture", "", ""),
    ],
    "arckit-togaf-adm/discovery": [
        ("gap-analysis", "", ""),
        ("application-rationalization", "", ""),
    ],
    "arckit-togaf-adm/gap-analysis": [
        ("transition-architecture", "", ""),
        ("architecture-board", "", ""),
    ],
    "arckit-togaf-adm/technology-architecture": [
        ("gap-analysis", "", ""),
        ("transition-architecture", "", ""),
    ],
    "arckit-togaf-adm/transition-architecture": [
        ("architecture-board", "", ""),
        ("architecture-change", "", ""),
    ],
}
