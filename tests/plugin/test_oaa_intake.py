"""
Regression tests for the `oaa-intake` OpenSpec change:

- Every OAA overlay command declares a MANDATORY `PRIN` prerequisite tier with a
  STOP instruction (TOGAF-consistent hard gate), while all other OAA
  prerequisites remain RECOMMENDED.
- The OAA copy of the shared intake block stays byte-identical to the root and
  retains §8 (the OAA tone guard: no diagram/output mandate from the interview).
- The OAA-scoped discovery-dimension checklist (D1–D10) ships in both OAA trees
  and is referenced by the intake step of every OAA command.
- Shipped default OAA templates surface the reference input domains.
"""

import os
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

OAA_SOURCES = ("plugins/arckit-oaa", "plugins/arckit-claude/plugins/oaa")

OAA_COMMANDS = (
    "oaa-adm-lite",
    "product-architecture",
    "agile-governance",
    "agile-security",
    "agile-strategy",
)

# (oaa source tree) reference input domains the shipped default templates surface,
# as representative markers (lower-case, searched case-insensitively).
REFERENCE_DOMAINS = {
    "oaa-adm-lite": [
        "jurisdiction", "workload", "use_cases", "data_classification", "latency",
        "budget", "timeline", "infrastructure", "stakeholder", "success criteria",
        "regulat", "risk", "topology", "owner",
    ],
    "product-architecture": [
        "mission", "value", "outcome", "experience", "adoption", "principle",
        "cross-functional", "epic", "adr", "wave", "compliance", "owner",
    ],
    "agile-governance": [
        "roles", "sprint review", "debt", "rubric", "compliance", "owner",
    ],
    "agile-security": [
        "security stor", "scan", "compliance-as-code", "validation", "kpi", "owner",
    ],
    "agile-strategy": [
        "technology", "product", "operating model", "organizational", "cultural",
        "team", "axiom", "resilience", "wave", "owner",
    ],
}

DIMENSIONS = tuple(f"D{i}" for i in range(1, 11))
DIM_FILE = "references/intake-discovery-dimensions.md"
SHARED_BLOCK_ROOT = "plugins/arckit-claude/references/intake-instructions.md"
SHARED_BLOCK_OAA = "plugins/arckit-oaa/references/intake-instructions.md"
TONE_GUARD_HEADING = "## 8. OAA tone guard"

# The interview must not introduce a diagram/output mandate (OAA tone guard).
DIAGRAM_MANDATE = re.compile(r"(interview|intake).{0,80}(MUST|must|requires?) (a |an |the )?(diagram|output)", re.I)


def _read(rel):
    with open(os.path.join(REPO_ROOT, rel)) as fh:
        return fh.read()


def _command_text(tree, name):
    return _read(f"{tree}/commands/{name}.md")


def _mandatory_tier(text):
    """Return the MANDATORY tier block (from the MANDATORY header to the next
    tier/section), or None if the command has no MANDATORY prerequisite tier."""
    m = re.search(r"\*\*MANDATORY\*\* \(stop if missing[^)]*\):", text)
    if not m:
        return None
    start = m.end()
    end_candidates = [text.find(anchor, start) for anchor in (
        "**RECOMMENDED**", "### Prerequisites", "## ", "\n### ")]
    ends = [e for e in end_candidates if e != -1]
    end = min(ends) if ends else len(text)
    return text[start:end]




def test_every_oaa_command_declares_mandatory_prin_gate():
    for tree in OAA_SOURCES:
        for name in OAA_COMMANDS:
            text = _command_text(tree, name)
            tier = _mandatory_tier(text)
            assert tier, f"{tree}/commands/{name}.md missing a MANDATORY prerequisite tier"
            assert "PRIN" in tier, f"{tree}/commands/{name}.md MANDATORY tier does not name PRIN"
            assert re.search(r"If missing: STOP and ask user to run `/arckit:principles` first", tier), (
                f"{tree}/commands/{name}.md MANDATORY PRIN tier missing the STOP instruction"
            )


def test_only_prin_is_mandatory_in_oaa_commands():
    for tree in OAA_SOURCES:
        for name in OAA_COMMANDS:
            text = _command_text(tree, name)
            tier = _mandatory_tier(text)
            assert tier, f"{tree}/commands/{name}.md missing a MANDATORY prerequisite tier"
            named = re.findall(r"^- \*\*([A-Z]+)\*\*", tier, re.M)
            assert named == ["PRIN"], (
                f"{tree}/commands/{name}.md MANDATORY tier must name exactly PRIN, got {named}"
            )
            # All other OAA prerequisites stay RECOMMENDED (noted when missing, not blocking).
            recommended = re.search(r"\*\*RECOMMENDED\*\* \(read if available, note if missing\):", text)
            assert recommended, f"{tree}/commands/{name}.md missing the RECOMMENDED prerequisite tier"


def test_oaa_intake_instructions_copy_is_byte_identical_and_keeps_tone_guard():
    root = _read(SHARED_BLOCK_ROOT)
    oaa = _read(SHARED_BLOCK_OAA)
    assert oaa == root, f"{SHARED_BLOCK_OAA} diverged from the root shared reference"
    assert TONE_GUARD_HEADING in root, "root shared reference lost the §8 OAA tone guard"
    assert TONE_GUARD_HEADING in oaa, "OAA copy of the shared reference lost the §8 OAA tone guard"
    # The mirror tree must carry the same copy.
    mirror = _read("plugins/arckit-claude/plugins/oaa/references/intake-instructions.md")
    assert mirror == root, "mirror OAA intake-instructions.md diverged from the root shared reference"


def test_every_oaa_command_runs_intake_interview_before_template():
    for tree in OAA_SOURCES:
        for name in OAA_COMMANDS:
            text = _command_text(tree, name)
            intake = text.find("**Run the intake interview**:")
            template = text.find("**Read the template**")
            assert intake != -1, f"{tree}/commands/{name}.md missing the intake interview step"
            assert template != -1, f"{tree}/commands/{name}.md missing the template-read step"
            assert 0 < intake < template, (
                f"{tree}/commands/{name}.md intake interview step must sit immediately before 'Read the template'"
            )
            between = text[intake:template]
            assert DIM_FILE in between, (
                f"{tree}/commands/{name}.md intake step must load the OAA discovery-dimension checklist ({DIM_FILE})"
            )
            assert "intake-instructions.md" in between, (
                f"{tree}/commands/{name}.md intake step must reference the shared intake block"
            )


def test_discovery_dimension_checklist_ships_in_both_oaa_trees():
    for tree in OAA_SOURCES:
        rel = f"{tree}/{DIM_FILE}"
        text = _read(rel)
        for dim in DIMENSIONS:
            assert re.search(rf"^{re.escape(dim)}\b|\b{re.escape(dim)}\b", text, re.M), f"{rel} missing dimension {dim}"
        # Prefill rule: resolvable -> surfaced for confirmation/override; no source -> skippable -> TBD.
        assert "confirmation or override" in text, f"{rel} missing the ask-always prefill rule"
        assert "TBD" in text, f"{rel} missing the skipped-question TBD rendering rule"
        assert "coverage floor" in text, f"{rel} must state the checklist is a coverage floor"
        # Sprint-0 prefill seeding (5.1): dimensions resolve under the generic §3
        # precedence (artefacts > per-command intake > shared.json > user_config).
        for source in ("artefacts", "shared.json", "user_config"):
            assert source in text, f"{rel} missing prefill source {source!r}"
        assert "precedence" in text, f"{rel} must apply the generic prefill precedence"


def test_oaa_reference_domains_present_in_shipped_templates():
    for tree in OAA_SOURCES:
        for name, markers in REFERENCE_DOMAINS.items():
            text = _read(f"{tree}/templates/{name}-template.md").lower()
            for marker in markers:
                assert marker in text, f"{tree}/templates/{name}-template.md missing reference domain {marker!r}"


def test_oaa_interview_adds_no_diagram_or_output_mandate():
    """The interview must not introduce any diagram/output demand the OAA
    template does not already ask for (spec: 'OAA Interview Adds No Diagram Or
    Output Mandate'; shared block §8 tone guard)."""
    for tree in OAA_SOURCES:
        for name in OAA_COMMANDS:
            text = _command_text(tree, name)
            # The intake interview step (between the marker and the template-read step).
            intake = text.find("**Run the intake interview**:")
            template = text.find("**Read the template**")
            assert intake != -1 and template != -1, f"{tree}/commands/{name}.md missing intake step"
            step = text[intake:template]
            assert not DIAGRAM_MANDATE.search(step), (
                f"{tree}/commands/{name}.md intake step introduces a diagram/output mandate"
            )
            assert "no diagram or output mandate" in step or "adds no diagram or output mandate" in step, (
                f"{tree}/commands/{name}.md intake step must state the checklist adds no diagram/output mandate"
            )
