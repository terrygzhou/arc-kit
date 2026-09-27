"""
Behavioural tests for the template-driven intake interview
(openspec change: template-driven-intake).

The interview is implemented as LLM instructions, not compiled code, so a
"does it ask?" test has two layers:

  1. WIRING  — every in-scope artefact-producing command must instruct the model
     to run the shared intake block *before* it renders, and the shared block must
     carry the imperatives that make the model actually *ask* questions
     (ask-every-derived-input, one-at-a-time, optional/skippable,
     prefilled-shown-for-confirm/override, TBD-on-skip, bulk exemption).
     Non-artefact commands must NOT instruct the interview.
  2. DECISION — a faithful executable model of the shared block's algorithm
     (intake-instructions.md) run against the spec scenarios, asserting the
     ask/skip outcomes: a fresh project gets asked; a fully-prefilled template
     still surfaces every input for confirmation/override; a bulk build never
     interviews; a skipped MANDATORY input becomes a quoted TBD marker listed
     in the summary.
"""

import os
import re

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLAUDE = os.path.join(REPO_ROOT, "plugins", "arckit-claude")
COMMANDS_DIR = os.path.join(CLAUDE, "commands")
SHARED_BLOCK = os.path.join(CLAUDE, "references", "intake-instructions.md")
TEMPLATES_DIR = os.path.join(CLAUDE, "templates")

# The 15 core commands that do NOT produce an artefact (console/registry/navigator
# tier) — they must NOT carry the interview. Mirrors openspec tasks.md 2.1.
NON_ARTEFACT_CORE = {
    "build", "init", "start", "health", "trello", "pages", "score", "search",
    "navigator", "graph-report", "import-okf", "export-okf", "customize",
    "template-builder", "impact",
}

OVERLAY_DIRS = (
    os.path.join(CLAUDE, "plugins", "togaf", "adm", "commands"),
    os.path.join(CLAUDE, "plugins", "oaa", "commands"),
    os.path.join(CLAUDE, "plugins", "agent", "architecture", "commands"),
)

INSTRUCTION_PREFIX = "Run the intake interview per"
INSTRUCTION_REF = "intake-instructions.md"


def _core_artefact_commands():
    files = sorted(
        f for f in os.listdir(COMMANDS_DIR)
        if f.endswith(".md") and f[:-3] not in NON_ARTEFACT_CORE
    )
    return [os.path.join(COMMANDS_DIR, f) for f in files]


def _overlay_commands():
    out = []
    for d in OVERLAY_DIRS:
        out.extend(os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".md"))
    return out


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# 1. WIRING — the command must point at the shared block; the block must ask
# ---------------------------------------------------------------------------

def test_all_in_scope_commands_instruct_the_interview():
    in_scope = _core_artefact_commands() + _overlay_commands()
    assert len(in_scope) == 85, f"expected 85 in-scope commands, got {len(in_scope)}"
    for path in in_scope:
        body = _read(path)
        assert INSTRUCTION_PREFIX in body, f"{os.path.basename(path)}: missing 'Run the intake interview per'"
        assert INSTRUCTION_REF in body, f"{os.path.basename(path)}: does not reference intake-instructions.md"


def test_non_artefact_commands_do_not_instruct_the_interview():
    for stem in sorted(NON_ARTEFACT_CORE):
        path = os.path.join(COMMANDS_DIR, f"{stem}.md")
        assert os.path.exists(path), f"missing core command {stem}.md"
        assert INSTRUCTION_PREFIX not in _read(path), \
            f"{stem}.md is a non-artefact command but instructs the intake interview"


def test_shared_block_carries_the_question_asking_rules():
    block = _read(SHARED_BLOCK)
    checks = {
        "puts every derived input to the user": "Put every derived input to the user" in block,
        "one at a time": "one at a time" in block,
        "prefilled value shown for confirm/override": "confirm or override" in block,
        "each question optional/skippable": "optional" in block.lower(),
        "skipped question renders a TBD marker": "TBD" in block,
        "summary lists unresolved fields": "Unresolved fields" in block,
        "bulk build exemption (no questions)": "No interactive questions are asked during a build" in block,
        "proportional 'zero when prefilled' cap removed": "zero" not in block,
        "ask-only-remainder removed": "Ask only the remainder" not in block,
        "still-unknown gating removed": "still unknown" not in block,
    }
    missing = [k for k, ok in checks.items() if not ok]
    assert not missing, f"shared block missing ask-always/optional rules: {missing}"


# ---------------------------------------------------------------------------
# 1a. WIRING — the shared block must resolve from each plugin's own runtime root
# ---------------------------------------------------------------------------
# Overlay commands (oaa, togaf/adm, agent/architecture) are shipped as their own
# sub-plugins: at runtime ${CLAUDE_PLUGIN_ROOT} is the sub-plugin's own
# directory, NOT the arckit root. Every command references
# ${CLAUDE_PLUGIN_ROOT}/references/intake-instructions.md, so each sub-plugin
# must carry its own copy — otherwise the model cannot read the interview
# algorithm and, because the interview is a soft gate, silently skips asking.

def _plugin_root_of(path):
    """Innermost enclosing directory that contains a .claude-plugin/ dir."""
    d = os.path.dirname(path)
    while True:
        if os.path.isdir(os.path.join(d, ".claude-plugin")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def test_intake_reference_resolves_in_every_plugin_root():
    for path in _core_artefact_commands() + _overlay_commands():
        root = _plugin_root_of(path)
        assert root is not None, f"{path}: no enclosing .claude-plugin root found"
        ref = os.path.join(root, "references", "intake-instructions.md")
        assert os.path.isfile(ref), (
            f"{os.path.basename(path)} runs as plugin rooted at {root}, but its "
            "intake reference does not resolve: " + ref
        )


def test_overlay_intake_copies_match_the_shared_block():
    root_block = _read(SHARED_BLOCK)
    for d in OVERLAY_DIRS:
        ref = os.path.normpath(os.path.join(d, "..", "references", "intake-instructions.md"))
        assert os.path.isfile(ref), f"overlay sub-plugin missing its intake copy: {ref}"
        assert _read(ref) == root_block, f"overlay intake copy diverged from root shared block: {ref}"


# ---------------------------------------------------------------------------
# 1b. WIRING — MANDATORY prerequisite tier: header wording must match its bodies
# ---------------------------------------------------------------------------

# The TOGAF ADM overlay lives in two trees that must agree: the shipped Claude
# mirror (what the plugin serves) and the standalone source the converter reads
# to build the 7 extensions. Both carry the 10 ADM commands, so both are checked.
ADM_COMMAND_DIRS = (
    os.path.join(CLAUDE, "plugins", "togaf", "adm", "commands"),
    os.path.join(REPO_ROOT, "plugins", "arckit-togaf-adm", "commands"),
)

_MAND_HEADER_RE = re.compile(
    r"^(#{0,4}\s*)\**MANDATORY\**\s*(?:\((?P<paren>[^)]*)\))?\s*:?\s*$",
    re.IGNORECASE,
)
_NEXT_TIER_RE = re.compile(
    r"^#{1,4}\s*(?:\**)(RECOMMENDED|OPTIONAL)\**", re.IGNORECASE
)
_STOP_RE = re.compile(r"\bSTOP\b", re.IGNORECASE)


def _mandatory_tier(body):
    """Return (header_paren, item_bodies) for a command's MANDATORY tier.

    ``header_paren`` is the text inside the tier header's parentheses (empty when
    there is none). ``item_bodies`` is the list of ``If missing: ...`` strings
    belonging to items in that tier. Returns None when the command has no
    MANDATORY prerequisite tier.
    """
    lines = body.splitlines()
    start = None
    paren = ""
    for i, line in enumerate(lines):
        m = _MAND_HEADER_RE.match(line.strip())
        if m:
            start = i
            paren = (m.group("paren") or "").strip()
            break
    if start is None:
        return None
    bodies = []
    for line in lines[start + 1:]:
        s = line.strip()
        if _NEXT_TIER_RE.match(s) or s.startswith("## "):
            break  # next prerequisite tier or a new section ends the MANDATORY tier
        m = re.search(r"If missing:\s*(.+)$", s)
        if m:
            bodies.append(m.group(1).strip())
    return paren, bodies


def test_mandatory_tier_header_matches_item_instructions():
    """A MANDATORY tier whose items say 'If missing: STOP …' is a hard
    dependency: its header must read 'stop if missing …', never
    'warn if missing' (the warn-vs-STOP contradiction from EYW-268).
    Conversely, a header that promises a stop must be backed by a STOP item.
    """
    checked = 0
    for d in ADM_COMMAND_DIRS:
        assert os.path.isdir(d), f"missing TOGAF ADM command dir: {d}"
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md"):
                continue
            tier = _mandatory_tier(_read(os.path.join(d, name)))
            if tier is None:
                continue  # no MANDATORY prerequisite tier (e.g. discovery, arch-change)
            paren, bodies = tier
            header_lower = paren.lower()
            header_says_stop = "stop if missing" in header_lower
            header_says_warn = "warn if missing" in header_lower
            any_stop_item = any(_STOP_RE.search(b) for b in bodies)
            label = f"{os.path.basename(d)}/{name}"
            if any_stop_item:
                assert header_says_stop, (
                    f"{label}: items say STOP but header is {paren!r} "
                    f"(should say 'stop if missing …')"
                )
                assert not header_says_warn, (
                    f"{label}: items say STOP but header says 'warn if missing' "
                    f"— warn/STOP contradiction"
                )
            else:
                assert not header_says_stop, (
                    f"{label}: header promises 'stop if missing' but no item body says STOP"
                )
            checked += 1
    # floor: the 10 ADM commands that hard-stop on a prerequisite artefact exist
    # in each of the two trees.
    assert checked >= 10, f"expected >=10 MANDATORY tiers across both trees, checked {checked}"


def test_mandatory_tier_coverage_is_symmetric_across_trees():
    """The two ADM trees must agree on WHICH commands carry a MANDATORY tier,
    so the header fix cannot drift between the plugin and the converter source."""
    counts = {}
    for d in ADM_COMMAND_DIRS:
        counts[os.path.basename(os.path.dirname(d))] = sum(
            1
            for n in os.listdir(d)
            if n.endswith(".md") and _mandatory_tier(_read(os.path.join(d, n))) is not None
        )
    assert len(set(counts.values())) == 1, f"MANDATORY-tier command count differs across trees: {counts}"


# ---------------------------------------------------------------------------
# 2. DECISION — executable model of the shared block's algorithm
# ---------------------------------------------------------------------------

class IntakeInterview:
    """Deterministic model of plugins/arckit-claude/references/intake-instructions.md.

    Inputs are declared MANDATORY / RECOMMENDED / OPTIONAL. Section inputs and
    Document Control fields are the *required inputs*; a Document Control field
    that `user_config` can answer is a prefill-candidate, not a question.
    Prefill precedence (intake-instructions.md §3):
        existing artefacts > per-command intake > shared intake > user_config.
    """

    def __init__(self, user_config=None):
        self.user_config = dict(user_config or {})

    def derive(self, section_inputs, doc_control_fields, mandatory_prereqs,
               doc_control_resolvable_from_config):
        """Which inputs the effective template actually needs (§2)."""
        inputs = dict(section_inputs)
        inputs.update(doc_control_fields)
        inputs.update(mandatory_prereqs)
        # A Document Control field user_config answers is a prefill-candidate.
        for field in doc_control_resolvable_from_config:
            if field in inputs and field in self.user_config:
                inputs.pop(field)
        return inputs

    def _resolve_prefill(self, key, artefacts, per_command, shared):
        for source in (artefacts, per_command, shared, self.user_config):  # §3 precedence
            if key in source:
                return source[key]
        return None

    def interview(self, derived, artefacts, per_command, shared, skips=(),
                  bulk_build=False):
        """Return (questions_asked, answers, unresolved_tbd, summary_lines)."""
        if bulk_build:  # "Bulk builds" — interview disabled
            answers, tbd, summary = {}, [], []
            for key in derived:
                val = self._resolve_prefill(key, artefacts, per_command, shared)
                if val is None:
                    tbd.append(key)
                    summary.append(f"| {key} | TBD |")
            return 0, answers, tbd, summary

        answers, tbd, questions, summary = {}, [], [], []
        for key in derived:
            # §4: surface EVERY derived input (ask-always, answer-optional)
            questions.append(key)
            if key in skips:                      # user skipped -> quoted TBD marker
                tbd.append(key)
                answers[key] = None
                summary.append(f'| {key} | TBD — "{key}" |')
                continue
            prefilled = self._resolve_prefill(key, artefacts, per_command, shared)
            if prefilled is not None:
                # prefilled value is surfaced for confirm/override; keep the default
                answers[key] = prefilled
        return len(questions), answers, tbd, summary


# A slice of the real stakeholder-drivers-template.md's required inputs.
STAKEHOLDERS = {
    "section_inputs": {
        "project_name": "Stakeholder Identification",
        "internal_stakeholders": "Stakeholder Identification",
        "external_stakeholders": "Stakeholder Identification",
        "alignment_score": "Executive Summary",
    },
    "doc_control_fields": {
        "document_owner": "Document Control",
        "review_date": "Document Control",
    },
    "mandatory_prereqs": {
        "project_stage": "MANDATORY prerequisite",
    },
    # user_config can answer the review date cadence, so it is a prefill-candidate.
    "doc_control_resolvable_from_config": ["review_date"],
}


def _derived():
    cfg = {"review_date": "quarterly"}
    ii = IntakeInterview(user_config=cfg)
    return ii, ii.derive(
        STAKEHOLDERS["section_inputs"],
        STAKEHOLDERS["doc_control_fields"],
        STAKEHOLDERS["mandatory_prereqs"],
        STAKEHOLDERS["doc_control_resolvable_from_config"],
    )


def test_fresh_project_asks_questions():
    """Core guarantee: with nothing prefilled, the interview DOES ask."""
    ii, derived = _derived()
    n, _ans, tbd, _sum = ii.interview(derived, artefacts={}, per_command={}, shared={})
    # 3 sections + project_stage + document_owner (review_date answered by user_config)
    assert n > 0, "fresh project must trigger at least one interview question"
    assert set(tbd) == set()  # nothing skipped yet
    assert n == len(derived), f"expected {len(derived)} questions on a fresh project, got {n}"


def test_fully_prefilled_template_still_surfaces_every_input():
    """§4 ask-always: even a fully-prefilled template surfaces every input."""
    ii, derived = _derived()
    n, a, _t, _s = ii.interview(derived,
                                  artefacts={k: "x" for k in derived},
                                  per_command={}, shared={})
    assert n == len(derived), f"every derived input is surfaced even when fully prefilled, got {n}"
    assert all(v == "x" for v in a.values()), "prefilled values are carried for confirm/override"


def test_partial_prefill_still_surfaces_every_input():
    ii, derived = _derived()
    prefilled = {k: "v" for k in list(derived)[: len(derived) - 1]}
    n, _a, _t, _s = ii.interview(derived, artefacts=prefilled, per_command={}, shared={})
    assert n == len(derived), f"every derived input is surfaced regardless of prefill, got {n}"


def test_user_config_resolvable_field_is_not_asked():
    ii, derived = _derived()
    assert "review_date" not in derived, "user_config-resolvable Doc Control field must be a prefill-candidate, not a question"


def test_precedence_higher_source_wins():
    ii = IntakeInterview(user_config={"project_stage": "config-stage"})
    derived = {"project_stage": "MANDATORY prerequisite"}
    n, answers, _t, _s = ii.interview(
        derived,
        artefacts={}, per_command={"project_stage": "per-command"},
        shared={"project_stage": "shared"},
    )
    assert n == 1, "the single derived input is surfaced to the user"
    assert answers["project_stage"] == "per-command", "per-command intake must beat shared and user_config"


def test_bulk_build_never_interviews_renders_tbd():
    ii, derived = _derived()
    n, _a, tbd, summary = ii.interview(derived, artefacts={}, per_command={}, shared={},
                                       bulk_build=True)
    assert n == 0, "bulk build must ask no interactive questions"
    assert len(tbd) == len(derived), "unknowns in a bulk build must render as TBD"
    assert all("TBD" in line for line in summary)


def test_skipped_mandatory_becomes_quoted_tbd_in_summary():
    ii, derived = _derived()
    key = "project_stage"  # a MANDATORY prerequisite
    n, _a, tbd, summary = ii.interview(
        derived, artefacts={}, per_command={}, shared={}, skips={key})
    assert key in tbd, "skipped MANDATORY input must be recorded as unresolved"
    assert any(key in line and "TBD" in line and '"' in line for line in summary), \
        "the skipped MANDATORY input must appear as a quoted TBD in the summary"


def test_reference_template_exists():
    """The template the interview derives from actually ships in the plugin."""
    assert os.path.exists(os.path.join(TEMPLATES_DIR, "stakeholder-drivers-template.md"))


# ---------------------------------------------------------------------------
# 1c. WIRING — standalone user-input questions must flow through the interview
#      (EYW-271)
# ---------------------------------------------------------------------------
# Bundled-overlay artefact commands must not hard-gate user input via a
# standalone out-of-band step (a dedicated AskUserQuestion / "Interactive
# Configuration" / "gather key parameters" step). Decision inputs (scope /
# weighting / parameter choices) are fields on the effective template and are
# asked ONLY through the template-driven intake interview (skippable ->
# TBD/default). The MANDATORY prerequisite *artefact* hard stops
# ("If missing: STOP...") stay hard and are untouched.

STANDALONE_OVERLAY_COMMAND_DIRS = (
    os.path.join(REPO_ROOT, "plugins", "arckit-togaf-adm", "commands"),
    os.path.join(REPO_ROOT, "plugins", "arckit-oaa", "commands"),
    os.path.join(REPO_ROOT, "plugins", "arckit-agent-architecture", "commands"),
)

# A numbered step whose title names a standalone user-input gate: the defect
# class removed in EYW-271 ("### 3. AskUserQuestion: ...",
# "### 4. Interactive Configuration", "gather key parameters").
_GATE_HEADING_RE = re.compile(
    r"^###\s+\d+\.\s+.*"
    r"(?:AskUserQuestion|Interactive Configuration|gather key parameters|ask the user)",
    re.MULTILINE | re.IGNORECASE,
)


def _all_bundled_overlay_commands():
    out = []
    for d in OVERLAY_DIRS + STANDALONE_OVERLAY_COMMAND_DIRS:
        out.extend(os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".md"))
    return out


def test_no_standalone_user_input_gates_in_bundled_overlays():
    for path in _all_bundled_overlay_commands():
        body = _read(path)
        m = _GATE_HEADING_RE.search(body)
        assert m is None, (
            f"{path}: numbered step '{m.group(0).strip()}' hard-gates user input "
            "outside the intake interview"
        )
        assert "**AskUserQuestion**" not in body, (
            f"{path}: standalone AskUserQuestion tool reference remains"
        )


# The decision inputs moved from the removed hard gates into the effective
# templates: template file -> (field, ...) declared inside its
# "### Intake questions (...)" section.
ADM_TEMPLATE_FIELDS = {
    "adm-preliminary-template.md": ("Engagement scope",),
    "application-inventory-template.md": ("Inventory scope",),
    "capability-map-template.md": ("Capability depth",),
    "data-architecture-template.md": ("Data scope",),
    "gap-analysis-template.md": ("Gap severity weighting",),
    "tech-architecture-template.md": ("Technology scope",),
    "transition-architecture-template.md": ("Transition waves",),
    "architecture-change-template.md": ("Change type", "Priority", "ADM Re-Entry"),
}
AGENT_TEMPLATE_FIELDS = {
    "agent-design-template.md": ("Architecture pattern", "Agent scope"),
}

# The defaults the former hard gates applied; the interview now applies them
# when a question is skipped. (Agent scope and ADM Re-Entry are skippable
# with no default / multi-select, so they carry no default.)
_FIELD_DEFAULTS = {
    "Engagement scope": "Business Unit",
    "Inventory scope": "All applications",
    "Capability depth": "Level 3",
    "Data scope": "Business Unit",
    "Gap severity weighting": "Balanced",
    "Technology scope": "Business Unit",
    "Transition waves": "3 waves",
    "Change type": "Evolutionary",
    "Priority": "Medium",
}


def _template_intake_section(path):
    """The template's '### Intake questions (...)' body, up to the next H2."""
    body = _read(path)
    m = re.search(r"^### Intake questions[^\n]*\n(.*?)(?=^## )",
                  body, re.DOTALL | re.MULTILINE)
    return m.group(1) if m else ""


def test_moved_decision_inputs_live_in_the_effective_templates():
    specs = (
        (os.path.join(CLAUDE, "plugins", "togaf", "adm", "templates"), ADM_TEMPLATE_FIELDS),
        (os.path.join(REPO_ROOT, "plugins", "arckit-togaf-adm", "templates"), ADM_TEMPLATE_FIELDS),
        (os.path.join(CLAUDE, "plugins", "agent", "architecture", "templates"), AGENT_TEMPLATE_FIELDS),
        (os.path.join(REPO_ROOT, "plugins", "arckit-agent-architecture", "templates"), AGENT_TEMPLATE_FIELDS),
    )
    for tdir, fields_by_file in specs:
        for filename, fields in fields_by_file.items():
            path = os.path.join(tdir, filename)
            assert os.path.isfile(path), f"missing template {path}"
            section = _template_intake_section(path)
            assert section, f"{filename}: no '### Intake questions' section found"
            for field in fields:
                m = re.search(r"^.*\*\*" + re.escape(field) + r":\*\*.*$",
                              section, re.MULTILINE)
                assert m, f"{filename}: decision input '{field}' not declared in the intake section"
                line = m.group(0).replace("`", "")
                if field in _FIELD_DEFAULTS:
                    assert "Options:" in line, f"{filename}: '{field}' lost its options"
                    assert f"(default: {_FIELD_DEFAULTS[field]})" in line, \
                        f"{filename}: '{field}' lost its default"


def _all_intake_copies():
    """The shared block plus every shipped copy (community plugins and the
    nested bundled-overlay sub-plugin copies)."""
    copies = [SHARED_BLOCK]
    plugins_root = os.path.join(REPO_ROOT, "plugins")
    for entry in sorted(os.listdir(plugins_root)):
        ref = os.path.join(plugins_root, entry, "references", "intake-instructions.md")
        if os.path.isfile(ref):
            copies.append(ref)
    for d in OVERLAY_DIRS:
        ref = os.path.normpath(os.path.join(d, "..", "references", "intake-instructions.md"))
        copies.append(ref)
    return copies


def test_all_intake_copies_document_decision_inputs_as_interview_inputs():
    """Every intake-instructions.md copy stays byte-identical to the shared
    block and makes explicit that scope / weighting / parameter decisions
    are interview inputs (soft, skippable) — so the model does not
    reintroduce a standalone hard-gate question."""
    copies = _all_intake_copies()
    assert len(copies) >= 15, f"expected at least 15 intake copies, got {len(copies)}"
    bodies = [_read(p) for p in copies]
    assert all(b == bodies[0] for b in bodies), "intake-instructions copies diverged"
    assert "Decision inputs" in bodies[0], \
        "shared intake block no longer documents decision inputs as interview inputs"
