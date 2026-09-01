"""
Regression tests: the template-driven intake interview is *ask-always,
answer-optional* across the shared reference and every artefact-producing overlay
(togaf/adm, oaa, agent/architecture).

The policy (OpenSpec change `intake-ask-always`) is: every derived input is put
to the user one at a time, prefilled where available to confirm/override, each
question optional/skippable -> a skipped question renders a `TBD` marker. This
test guards the inversion against silently reverting to "ask only the unknown /
a fully-prefilled template asks zero questions".
"""

import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# The 7 byte-identical copies of the shared interview algorithm.
REFS = (
    "plugins/arckit-claude/references/intake-instructions.md",
    "plugins/arckit-oaa/references/intake-instructions.md",
    "plugins/arckit-togaf-adm/references/intake-instructions.md",
    "plugins/arckit-agent-architecture/references/intake-instructions.md",
    "plugins/arckit-claude/plugins/oaa/references/intake-instructions.md",
    "plugins/arckit-claude/plugins/togaf/adm/references/intake-instructions.md",
    "plugins/arckit-claude/plugins/agent/architecture/references/intake-instructions.md",
)

# Positive ask-always wording and stale proportional wording.
REF_POSITIVE = "Put every derived input to the user, one at a time"
REF_STALE = (
    "ask only what remains unknown",
    "asks zero questions when every input is already prefilled",
    "Ask only the remainder",
)

# (source tree, sub-plugin mirror tree) for each overlay.
OVERLAYS = (
    ("plugins/arckit-oaa", "plugins/arckit-claude/plugins/oaa"),
    ("plugins/arckit-togaf-adm", "plugins/arckit-claude/plugins/togaf/adm"),
    ("plugins/arckit-agent-architecture", "plugins/arckit-claude/plugins/agent/architecture"),
)

TEMPLATE_POSITIVE = "Every question below is always put to the user"
TEMPLATE_STALE = "are **not** asked"
COMMAND_POSITIVE = ("put **every** intake question",
                    "Every question below is always put to the user")
COMMAND_STALE = "ask only what remains unknown"


def _read(rel):
    with open(os.path.join(REPO_ROOT, rel)) as fh:
        return fh.read()


def _listing(rel_dir, suffix):
    d = os.path.join(REPO_ROOT, rel_dir)
    return sorted(f for f in os.listdir(d) if f.endswith(suffix))


def test_shared_reference_is_ask_always():
    for rel in REFS:
        text = _read(rel)
        assert REF_POSITIVE in text, f"{rel} missing ask-always wording"
        for stale in REF_STALE:
            assert stale not in text, f"{rel} still has stale wording: {stale!r}"


def test_all_seven_shared_reference_copies_are_byte_identical():
    root = _read(REFS[0])
    for rel in REFS[1:]:
        assert _read(rel) == root, f"{rel} diverged from the root shared reference"


def test_every_overlay_template_is_ask_always():
    for src, mirror in OVERLAYS:
        for tree in (src, mirror):
            for name in _listing(tree + "/templates", "-template.md"):
                text = _read(f"{tree}/templates/{name}")
                assert TEMPLATE_POSITIVE in text, f"{tree}/templates/{name} missing ask-always wording"
                assert TEMPLATE_STALE not in text, f"{tree}/templates/{name} still has stale 'not asked' wording"


def test_every_overlay_command_is_ask_always():
    for src, mirror in OVERLAYS:
        for tree in (src, mirror):
            for name in _listing(tree + "/commands", ".md"):
                text = _read(f"{tree}/commands/{name}")
                assert COMMAND_STALE not in text, f"{tree}/commands/{name} still has stale 'ask only what remains unknown' wording"
                assert any(p in text for p in COMMAND_POSITIVE), (
                    f"{tree}/commands/{name} missing ask-always wording"
                )
