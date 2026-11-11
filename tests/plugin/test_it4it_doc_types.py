"""
Guard test for the IT4IT doc-type registrations (arckit-it4it overlay).

Mirrors the registration-point discipline established by the BMM and
ArchiMate conformance guards: every point that fails silently when
missed gets a guard here.

  - ITVN/ITVS/ITSF/ITDT/ITCF/ITOA in doc-types.mjs DOC_TYPES, all
    category Architecture
  - ITVS in MULTI_INSTANCE_TYPES (the only multi-instance IT4IT type:
    sequence-numbered ARC-{P}-ITVS-{NNN}); ITVN/ITSF/ITDT/ITCF/ITOA
    absent from MULTI_INSTANCE_TYPES (single-instance)
  - ITVS in MULTI_INSTANCE_TYPES in both generate-document-id.sh copies
    (parity across the .mjs set and the two bash scripts)
  - the six IT4IT codes in the /arckit:pages allow-list (dual
    registration, pages.md table rows start with `| | CODE |` at
    column 0)
  - Codex doc-types.mjs dual registration of the six codes + ITVS
  - plugin manifest shape (name/version/defaultEnabled/dependency)
  - sub-plugin copy byte-parity (commands/references/templates)
  - six command bodies carry the MANDATORY PRIN hard gate + the
    "STOP and ask" wording + the intake-interview instruction (OAA
    tone guard: no diagram or output mandate beyond the template)
"""

import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_TYPES_MJS = REPO_ROOT / "plugins" / "arckit-claude" / "config" / "doc-types.mjs"
CODEX_DOC_TYPES = REPO_ROOT / "extensions" / "arckit-codex" / "config" / "doc-types.mjs"
PAGES_CMD = REPO_ROOT / "plugins" / "arckit-claude" / "commands" / "pages.md"
GEN_ID_ROOT = REPO_ROOT / "scripts" / "bash" / "generate-document-id.sh"
GEN_ID_PLUGIN = REPO_ROOT / "plugins" / "arckit-claude" / "scripts" / "bash" / "generate-document-id.sh"
PLUGIN_MANIFEST = REPO_ROOT / "plugins" / "arckit-it4it" / ".claude-plugin" / "plugin.json"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "arckit-it4it"
SUB_PLUGIN = REPO_ROOT / "plugins" / "arckit-claude" / "plugins" / "it4it"

IT4IT_CODES = ("ITVN", "ITVS", "ITSF", "ITDT", "ITCF", "ITOA")
# ITVS is the only multi-instance IT4IT type (sequence-numbered).
MULTI_INSTANCE = {"ITVS"}

# D5: IT4IT commands add no diagram or output mandate beyond the template.
# Guard: positive diagram mandates ("create a plantuml diagram",
# "the diagram below", "diagram in §"). The negation "no diagram or
# output mandate" in the shared intake-instructions block is allowed.
_TONE_GUARD_MANDATE_RE = re.compile(
    r"create a (?:plantuml|archimate|diagram)\b"
    r"|the diagram (?:below|in)"
    r"|diagram must",
    re.IGNORECASE,
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def mjs_doc_types(path: Path) -> dict[str, dict[str, str]]:
    """Parse the DOC_TYPES object literal into {code: {name, category}}.

    Each entry is a single- or multi-line `'CODE': { name: '...', category: '...' }`
    entry. We pull out the code key plus the name/category fields that follow it
    up to the next code key or the end of the object.
    """
    text = read(path)
    match = re.search(r"export\s+const\s+DOC_TYPES\s*=\s*\{(.*?)\n\};", text, re.DOTALL)
    assert match, f"DOC_TYPES object not found in {path}"
    body = match.group(1)
    result: dict[str, dict[str, str]] = {}
    # Split on the code-key lines: a line that starts with an optional indent,
    # a quoted code, and a colon.
    key_re = re.compile(r"^\s*['\"]([A-Z0-9-]+)['\"]\s*:", re.MULTILINE)
    keys = list(key_re.finditer(body))
    for i, key_match in enumerate(keys):
        code = key_match.group(1)
        end = keys[i + 1].start() if i + 1 < len(keys) else len(body)
        chunk = body[key_match.start():end]
        name_m = re.search(r"name\s*:\s*['\"]([^'\"]+)['\"]", chunk)
        cat_m = re.search(r"category\s*:\s*['\"]([^'\"]+)['\"]", chunk)
        result[code] = {
            "name": name_m.group(1) if name_m else "",
            "category": cat_m.group(1) if cat_m else "",
        }
    return result


def mjs_multi_instance(path: Path) -> set[str]:
    match = re.search(
        r"export\s+const\s+MULTI_INSTANCE_TYPES\s*=\s*new\s+Set\(\s*\[(.*?)\]\s*\)",
        read(path),
        re.DOTALL,
    )
    assert match, f"MULTI_INSTANCE_TYPES set not found in {path}"
    body = re.sub(r"//[^\n]*", "", match.group(1))
    return set(re.findall(r"['\"]([A-Z0-9-]+)['\"]", body))


def bash_multi_instance(path: Path) -> set[str]:
    match = re.search(r'^MULTI_INSTANCE_TYPES="([^"]*)"', read(path), re.MULTILINE)
    assert match, f"MULTI_INSTANCE_TYPES assignment not found in {path}"
    return set(c.strip() for c in match.group(1).split() if c.strip())


def pages_allow_list(path: Path) -> set[str]:
    """Codes appearing as a `| | CODE |` row in the pages.md table."""
    return set(
        re.findall(r"^\|\s*\|\s*([A-Z0-9-]+)\s*\|", read(path), re.MULTILINE)
    )


def test_all_six_it4it_codes_in_doc_types():
    doc_types = mjs_doc_types(DOC_TYPES_MJS)
    for code in IT4IT_CODES:
        assert code in doc_types, f"{code} missing from doc-types.mjs DOC_TYPES"
        assert doc_types[code]["category"] == "Architecture", (
            f"{code} category is {doc_types[code]['category']!r}, expected 'Architecture'"
        )
        assert doc_types[code]["name"], f"{code} has an empty name in DOC_TYPES"


def test_all_six_it4it_codes_in_codex_doc_types():
    doc_types = mjs_doc_types(CODEX_DOC_TYPES)
    for code in IT4IT_CODES:
        assert code in doc_types, f"{code} missing from Codex doc-types.mjs DOC_TYPES"
        assert doc_types[code]["category"] == "Architecture", (
            f"{code} Codex category is {doc_types[code]['category']!r}, expected 'Architecture'"
        )


def test_itvs_is_the_only_multi_instance_it4it():
    multi = mjs_multi_instance(DOC_TYPES_MJS)
    it4it_in_multi = MULTI_INSTANCE & multi
    assert it4it_in_multi == MULTI_INSTANCE, (
        f"IT4IT multi-instance codes in doc-types.mjs: {sorted(it4it_in_multi)}, "
        f"expected {sorted(MULTI_INSTANCE)}"
    )
    # The single-instance codes must NOT be multi-instance.
    for code in ("ITVN", "ITSF", "ITDT", "ITCF", "ITOA"):
        assert code not in multi, f"{code} should be single-instance but is in MULTI_INSTANCE_TYPES"


def test_itvs_multi_instance_in_codex():
    multi = mjs_multi_instance(CODEX_DOC_TYPES)
    assert "ITVS" in multi, "ITVS missing from Codex MULTI_INSTANCE_TYPES"
    for code in ("ITVN", "ITSF", "ITDT", "ITCF", "ITOA"):
        assert code not in multi, f"{code} should not be multi-instance in Codex"


def test_itvs_in_both_bash_generators():
    for label, path in (("root", GEN_ID_ROOT), ("plugin", GEN_ID_PLUGIN)):
        multi = bash_multi_instance(path)
        assert "ITVS" in multi, f"{label} generate-document-id.sh: ITVS missing from MULTI_INSTANCE_TYPES"
        for code in ("ITVN", "ITSF", "ITDT", "ITCF", "ITOA"):
            assert code not in multi, f"{label} generate-document-id.sh: {code} should not be multi-instance"


def test_bash_multi_instance_parity_with_mjs():
    """The two bash copies and the .mjs set agree on the IT4IT multi-instance set."""
    mjs_multi = mjs_multi_instance(DOC_TYPES_MJS)
    for label, path in (("root", GEN_ID_ROOT), ("plugin", GEN_ID_PLUGIN)):
        bash_multi = bash_multi_instance(path)
        it4it_mjs = MULTI_INSTANCE & mjs_multi
        it4it_bash = MULTI_INSTANCE & bash_multi
        assert it4it_mjs == it4it_bash, (
            f"{label} generate-document-id.sh IT4IT multi-instance drift: "
            f"mjs={sorted(it4it_mjs)} bash={sorted(it4it_bash)}"
        )


def test_all_six_it4it_codes_in_pages_allow_list():
    allow = pages_allow_list(PAGES_CMD)
    for code in IT4IT_CODES:
        assert code in allow, f"{code} missing from the /arckit:pages allow-list"


# ---------------------------------------------------------------------------
# 2. Plugin manifest + sub-plugin byte-parity + PRIN hard gate + tone guard
# ---------------------------------------------------------------------------


def test_it4it_plugin_manifest_shape():
    manifest = json.loads(read(PLUGIN_MANIFEST))
    assert manifest["name"] == "arckit-it4it"
    assert manifest["version"] == "6.11.0"
    assert manifest.get("defaultEnabled") is False
    # dependencies is a list of {name, version} objects (manifest schema).
    dep = next(d for d in manifest["dependencies"] if d["name"] == "arckit")
    assert dep["version"] == "=6.11.0"
    for key in ("default_classification", "organisation_name", "project_issue_prefix", "references_dir"):
        assert key in manifest["userConfig"], f"userConfig missing {key}"


def test_it4it_sub_plugin_is_byte_identical():
    for dirpart in ("commands", "references", "templates"):
        src_files = sorted(p.relative_to(PLUGIN_ROOT / dirpart) for p in (PLUGIN_ROOT / dirpart).rglob("*") if p.is_file())
        sub_files = sorted(p.relative_to(SUB_PLUGIN / dirpart) for p in (SUB_PLUGIN / dirpart).rglob("*") if p.is_file())
        assert src_files == sub_files, f"{dirpart}: file set differs between plugin and sub-plugin mirror"
        for rel in src_files:
            assert (PLUGIN_ROOT / dirpart / rel).read_bytes() == (SUB_PLUGIN / dirpart / rel).read_bytes(), (
                f"{dirpart}/{rel} diverged from the sub-plugin mirror"
            )


def _it4it_commands() -> list[Path]:
    return sorted(PLUGIN_ROOT.joinpath("commands", "it4it-value-network.md").parent.glob("it4it-*.md"))


def test_all_six_it4it_commands_carry_mandatory_prin_gate():
    cmd_dir = PLUGIN_ROOT / "commands"
    cmds = sorted(cmd_dir.glob("it4it-*.md"))
    assert len(cmds) == 6, f"expected six IT4IT commands in {cmd_dir}, got {len(cmds)}"
    for cmd in cmds:
        body = read(cmd)
        assert "MANDATORY" in body, f"{cmd.name}: missing MANDATORY tier"
        assert re.search(r"MANDATORY", body, re.IGNORECASE)
        # The PRIN prerequisite must name the doc-type code and instruct the user to run /arckit:principles.
        assert "PRIN" in body, f"{cmd.name}: MANDATORY tier does not name PRIN"
        assert "/arckit:principles" in body, f"{cmd.name}: does not instruct the user to run /arckit:principles"
        assert "STOP" in body, f"{cmd.name}: missing the STOP-and-ask hard-gate wording"
        # Intake instruction must reference the shared block.
        assert "Run the intake interview per" in body, f"{cmd.name}: missing the intake-interview instruction"
        assert "intake-instructions.md" in body, f"{cmd.name}: does not reference intake-instructions.md"


def test_it4it_commands_carry_no_diagram_or_output_mandate():
    """D5: IT4IT commands add no diagram or output mandate beyond the template.

    Guards positive diagram/output mandates ("create a plantuml diagram",
    "the diagram below", "diagram must …"). The negation "no diagram or
    output mandate" in the shared intake block and discovery-dimension
    checklist is allowed — it states the D5 posture, not a mandate.
    """
    for cmd in _it4it_commands():
        body = read(cmd)
        m = _TONE_GUARD_MANDATE_RE.search(body)
        assert m is None, (
            f"{cmd.name}: tone-guard violation — IT4IT commands must not "
            f"mandate a diagram or specific output beyond the template "
            f"(design decision D5); found: {m.group(0)!r}"
        )
