"""
The shipped ADM templates must stay a conforming example of the quality
checklist: every template with a Document Control section lists the full
14-field table, the revision-history table uses the canonical six columns,
and the mermaid quadrantChart blocks in the ADM / agent-maturity templates
parse as shipped (no x-axis__/y-axis__ typos, no comma-form plot points).

RED on the 14-field table, the axis typos, and the checklist wording; GREEN
only for the revision-history header guard (already canonical in every
template).
"""

import glob
import os
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ADM_TEMPLATE_DIRS = (
    "plugins/arckit-claude/plugins/togaf/adm/templates",
    "plugins/arckit-togaf-adm/templates",
)

# Canonical order per checklist common check #1.
CANONICAL_DOC_CONTROL_FIELDS = (
    "Document ID",
    "Document Type",
    "Project",
    "Classification",
    "Status",
    "Version",
    "Created Date",
    "Last Modified",
    "Review Cycle",
    "Next Review Date",
    "Owner",
    "Reviewed By",
    "Approved By",
    "Distribution",
)

CANONICAL_REVISION_HISTORY_HEADER = "| Version | Date | Author | Description | Reviewer | Approver |"

# Templates whose quadrantChart blocks must be renderable as shipped, plus
# the agent-maturity mirror in the agent-architecture plugin.
MERMAID_TEMPLATE_GLOBS = (
    "plugins/arckit-claude/plugins/togaf/adm/templates/*-template.md",
    "plugins/arckit-togaf-adm/templates/*-template.md",
    "plugins/arckit-claude/plugins/agent/architecture/templates/agent-maturity-template.md",
    "plugins/arckit-agent-architecture/templates/agent-maturity-template.md",
)

CHECKLIST_GLOBS = (
    "plugins/arckit-*/references/quality-checklist.md",
    "plugins/arckit-claude/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/*/references/quality-checklist.md",
    "plugins/arckit-claude/plugins/*/*/*/references/quality-checklist.md",
    "plugins/arckit-togaf-adm/references/quality-checklist.md",
    "scripts/autoresearch/program.md",
)


def _read(rel):
    with open(os.path.join(REPO_ROOT, rel), "r", encoding="utf-8") as fh:
        return fh.read()


def _dc_field_rows(text):
    """Field names (row 1 cells) of the Document Control table, in order."""
    rows = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("|") and "Document Control" in line:
            continue
        if not line.startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not in_table:
            if cells[:2] == ["Field", "Value"]:
                in_table = True
            continue
        if cells[0] in ("---", ":---", "---:"):
            continue
        rows.append(cells[0].strip("*` "))
    return rows


def test_doc_control_tables_are_14_field_in_both_trees():
    checked = 0
    for rel in ADM_TEMPLATE_DIRS:
        for path in sorted(glob.glob(os.path.join(REPO_ROOT, rel, "*-template.md"))):
            text = _read(path)
            if "## Document Control" not in text:
                continue  # discovery-template.md renders via {{ }} placeholders
            checked += 1
            fields = _dc_field_rows(text)
            missing = [f for f in CANONICAL_DOC_CONTROL_FIELDS if f not in fields]
            assert not missing, (
                f"{os.path.relpath(path, REPO_ROOT)}: Document Control table is "
                f"missing checklist fields {missing} (found {fields})"
            )
    assert checked >= 20, f"expected >= 20 ADM Document Control tables, checked {checked}"


def test_mermaid_quadrant_charts_have_valid_axis_lines():
    checked = 0
    for pattern in MERMAID_TEMPLATE_GLOBS:
        for path in sorted(glob.glob(os.path.join(REPO_ROOT, pattern))):
            text = _read(path)
            assert "x-axis__" not in text, f"{os.path.relpath(path, REPO_ROOT)}: 'x-axis__' typo"
            assert "y-axis__" not in text, f"{os.path.relpath(path, REPO_ROOT)}: 'y-axis__' typo"
            checked += 1
    assert checked >= 8, f"expected >= 8 mermaid-checked templates, checked {checked}"


def test_mermaid_quadrant_chart_points_use_array_form():
    bad = re.compile(
        r'^\s*"[\w .&/-]+":\s*\d*\.?\d+\s*,\s*\d*\.?\d+\s*$'  # "C1.1.1": 0.8, 0.3
    )
    bad_list = re.compile(r'^\s*"[^"]+",\s*\[')  # "Design", [0.3, 0.4]
    checked = 0
    for pattern in MERMAID_TEMPLATE_GLOBS:
        for path in sorted(glob.glob(os.path.join(REPO_ROOT, pattern))):
            for line in _read(path).splitlines():
                rel = os.path.relpath(path, REPO_ROOT)
                if bad.match(line):
                    raise AssertionError(f"{rel}: comma-form plot point: {line.strip()!r}")
                if bad_list.match(line):
                    raise AssertionError(f"{rel}: comma-separated point form: {line.strip()!r}")
            checked += 1
    assert checked >= 8, f"expected >= 8 mermaid-checked templates, checked {checked}"


def test_revision_history_header_is_canonical_six_column():
    checked = 0
    for rel in ADM_TEMPLATE_DIRS:
        for path in sorted(glob.glob(os.path.join(REPO_ROOT, rel, "*-template.md"))):
            text = _read(path)
            if "## Document Control" not in text:
                continue
            checked += 1
            assert CANONICAL_REVISION_HISTORY_HEADER in text, (
                f"{os.path.relpath(path, REPO_ROOT)}: revision-history table must use "
                f"the canonical columns {CANONICAL_REVISION_HISTORY_HEADER}"
            )
    assert checked >= 20, f"expected >= 20 revision-history tables, checked {checked}"


def test_checklists_name_the_canonical_six_revision_columns():
    old = re.compile(r"Version, Date, Author, Changes, Approved By, Approval Date")
    new = re.compile(r"Version, Date, Author, Description, Reviewer, Approver")
    checked = 0
    seen = set()
    for pattern in CHECKLIST_GLOBS:
        for path in sorted(glob.glob(os.path.join(REPO_ROOT, pattern))):
            rel = os.path.relpath(path, REPO_ROOT)
            if rel in seen:
                continue
            text = _read(path)
            if "Revision History" not in text:
                continue
            seen.add(rel)
            checked += 1
            assert not old.search(text), f"{rel}: legacy revision-history columns"
            assert new.search(text), f"{rel}: canonical revision-history columns missing"
    assert checked >= 32, (
        f"expected >= 32 checklist/program copies, checked {checked} "
        f"({sorted(seen) if checked else 'none'})"
    )
