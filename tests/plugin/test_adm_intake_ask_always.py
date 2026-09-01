"""
TOGAF ADM commands must state the intake principle explicitly:
ask-always (the interview MUST ask every question) / answer-optional (each
answer is skippable -> TBD). The OAA commands already phrase this; the ADM
commands must carry the same framing in their step-2 "Run the intake
interview" bullet so the principle is visible in the command text, not only in
the shared block.
"""

import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# The two TOGAF ADM trees that must agree: the shipped Claude mirror and the
# standalone source the converter reads to build the extensions.
ADM_COMMAND_DIRS = (
    "plugins/arckit-claude/plugins/togaf/adm/commands",
    "plugins/arckit-togaf-adm/commands",
)

MARKER = "Run the intake interview per"


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def test_adm_intake_commands_are_ask_always_answer_optional():
    checked = 0
    for rel in ADM_COMMAND_DIRS:
        d = os.path.join(REPO_ROOT, rel)
        assert os.path.isdir(d), f"missing TOGAF ADM command dir: {rel}"
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md"):
                continue
            text = _read(os.path.join(d, name))
            if MARKER not in text:
                continue  # non-intake command; nothing to check
            checked += 1
            label = f"{rel}/{name}"
            assert "ask-always" in text, (
                f"{label}: intake bullet missing 'ask-always' framing"
            )
            assert "answer-optional" in text, (
                f"{label}: intake bullet missing 'answer-optional' framing"
            )
    # floor: all 12 ADM commands reference intake, across both trees = 24
    assert checked >= 24, f"expected >=24 intake ADM commands checked, got {checked}"
