"""
Regression tests: TOGAF 10-aligned intake interview questions embedded in the
artefact-producing templates of the togaf/adm, oaa, and agent/architecture
overlays, plus the inline DISC structure of /arckit:discovery.

Each template carries a top-level "## Intake Interview Questions" section so the
template-driven intake interview (references/intake-instructions.md §2) derives
its question list from the effective template. The sub-plugin mirrors under
plugins/arckit-claude/plugins/** must carry the same section.
"""

import os
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SECTION = "## Intake Interview Questions"

# (source tree template dir, sub-plugin mirror template dir)
PAIRS = (
    ("plugins/arckit-togaf-adm/templates",
     "plugins/arckit-claude/plugins/togaf/adm/templates"),
    ("plugins/arckit-oaa/templates",
     "plugins/arckit-claude/plugins/oaa/templates"),
    ("plugins/arckit-agent-architecture/templates",
     "plugins/arckit-claude/plugins/agent/architecture/templates"),
)

DISCOVERY_COMMANDS = (
    "plugins/arckit-togaf-adm/commands/discovery.md",
    "plugins/arckit-claude/plugins/togaf/adm/commands/discovery.md",
)


def template_names(rel):
    d = os.path.join(REPO_ROOT, rel)
    return sorted(
        f for f in os.listdir(d)
        if f.endswith("-template.md")
    )


@pytest.mark.parametrize("source_rel,mirror_rel", PAIRS)
def test_every_overlay_template_embeds_intake_questions(source_rel, mirror_rel):
    for name in template_names(source_rel):
        src = open(os.path.join(REPO_ROOT, source_rel, name)).read()
        assert SECTION in src, f"{source_rel}/{name} missing intake questions"
        mirror = open(os.path.join(REPO_ROOT, mirror_rel, name)).read()
        assert SECTION in mirror, f"{mirror_rel}/{name} missing intake questions"


@pytest.mark.parametrize("rel", DISCOVERY_COMMANDS)
def test_discovery_command_embeds_intake_questions(rel):
    text = open(os.path.join(REPO_ROOT, rel)).read()
    assert "## Interview Questions (TOGAF 10" in text, rel


def test_intake_questions_are_a_question_list():
    """The embedded section must actually contain questions (bullet list)."""
    src_rel, mirror_rel = PAIRS[0][0], PAIRS[0][1]
    for rel in (src_rel, mirror_rel):
        for name in template_names(rel):
            text = open(os.path.join(REPO_ROOT, rel, name)).read()
            idx = text.index(SECTION)
            section = text[idx:idx + 4000]
            assert "- " in section, f"{rel}/{name} intake section has no bullet questions"
