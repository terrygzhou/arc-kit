"""
Guard test for plugins/arckit-oaa/validate-architecture.py — the OAA
shared architecture schema gate (EYW-324 F2 / EYW-335).

Unit-level: the embedded minimal JSON-Schema validator must flag each
defect class (type mismatch, missing required, bad enum, disallowed
additional property, bad array item) and pass clean content.

Integration-level: all 9 shipped schemas load and validate; the gate
passes on the checked-out repo; doc references to schemas/<name> in the
OAA plugin (canonical + Claude mirror) resolve to shipped files; the
local CI gate line is wired.
"""

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANON_PLUGIN = REPO_ROOT / "plugins" / "arckit-oaa"
MIRROR_PLUGIN = REPO_ROOT / "plugins" / "arckit-claude" / "plugins" / "oaa"

SCHEMA_NAMES = [
    "vision.json",
    "implementation-strategy.json",
    "product-architecture.json",
    "strategy-canvas.json",
    "security-backlog.json",
    "compliance-evidence.json",
    "governance-cadence.json",
    "threat-model.yaml",
    "change-request.yaml",
]


def _load_validator(path):
    spec = importlib.util.spec_from_file_location(
        "validate_architecture_" + path.parent.name, path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator(CANON_PLUGIN / "validate-architecture.py")


def test_nine_schemas_ship_in_both_trees():
    for tree in (CANON_PLUGIN, MIRROR_PLUGIN):
        for name in SCHEMA_NAMES:
            assert (tree / "schemas" / name).is_file(), f"{tree.name}: missing {name}"
        assert (tree / "validate-architecture.py").is_file(), f"{tree.name}: missing validator"


def test_all_schemas_load():
    for name in SCHEMA_NAMES:
        schema, err = VALIDATOR.load_schema(name)
        assert schema is not None, f"{name}: {err}"
        assert "type" in schema, f"{name}: no top-level type"


def test_embedded_validator_flags_type_error():
    errors = VALIDATOR.validate("nope", {"type": "integer", "minimum": 1})
    assert any("expected type" in e for e in errors)


def test_embedded_validator_flags_missing_required():
    errors = VALIDATOR.validate({}, {"type": "object", "required": ["a"]})
    assert any("missing required" in e for e in errors)


def test_embedded_validator_flags_bad_enum():
    errors = VALIDATOR.validate(
        {"sprint": 1}, {"type": "object", "properties": {"sprint": {"type": "integer", "minimum": 1}}}
    )
    assert errors == []
    errors = VALIDATOR.validate(
        0, {"type": "integer", "minimum": 1}
    )
    assert any("below minimum" in e for e in errors)


def test_embedded_validator_flags_additional_property():
    schema = {
        "type": "object",
        "required": ["a"],
        "additionalProperties": False,
        "properties": {"a": {"type": "string"}},
    }
    errors = VALIDATOR.validate({"a": "ok", "b": "x"}, schema)
    assert any("additional property" in e for e in errors)


def test_embedded_validator_flags_bad_array_item():
    schema = {
        "type": "object",
        "properties": {
            "items": {"type": "array", "minItems": 1, "items": {"type": "string"}}
        }
    }
    assert VALIDATOR.validate({"items": ["ok"]}, schema) == []
    errors = VALIDATOR.validate({"items": [42]}, schema)
    assert any("expected type" in e for e in errors)


def test_embedded_validator_flags_min_items_and_min_length():
    schema = {
        "type": "object",
        "properties": {
            "names": {"type": "array", "minItems": 2},
            "label": {"type": "string", "minLength": 1},
        }
    }
    errors = VALIDATOR.validate({"names": ["only"], "label": ""}, schema)
    assert any("fewer than minItems" in e for e in errors)
    assert any("shorter than minLength" in e for e in errors)


def test_valid_and_corrupt_fixtures_per_schema():
    for name, fixtures in VALIDATOR.SELF_TEST_FIXTURES.items():
        schema, err = VALIDATOR.load_schema(name)
        assert schema is not None, f"{name}: {err}"
        assert VALIDATOR.validate(fixtures["valid"], schema) == [], f"{name}: valid fixture rejected"
        assert VALIDATOR.validate(fixtures["corrupt"], schema), f"{name}: corrupt fixture accepted"


def test_gate_passes_on_checked_out_repo():
    assert VALIDATOR.main(["gate"]) == 0


def test_self_test_passes():
    assert VALIDATOR.main(["self-test"]) == 0


def test_artifact_mode_usage_and_validation(tmp_path):
    good = tmp_path / "vision.json"
    good.write_text('{"vision": {"scope": {"ai_workload_type": "RAG pipeline"}}}')
    bad = tmp_path / "vision-bad.json"
    bad.write_text('{"vision": {"scope": {"ai_workload_type": "flux"}}}')
    assert VALIDATOR.main([str(good), "--phase", "vision"]) == 0
    assert VALIDATOR.main([str(bad), "--phase", "vision"]) == 1
    assert VALIDATOR.main([str(good)]) == 2
    assert VALIDATOR.main([str(good), "--phase", "nonsense"]) == 2


def test_drift_subcommand(tmp_path):
    baseline = tmp_path / "base.json"
    baseline.write_text('{"version": "1.0", "model": "sglang"}')
    deployed = tmp_path / "deployed.json"
    deployed.write_text('{"version": "2.0", "model": "vllm"}')
    assert VALIDATOR.main(["drift", str(baseline), str(deployed), "--ignore", "version"]) == 1
    assert VALIDATOR.main(["drift", str(baseline), str(baseline)]) == 0
    assert VALIDATOR.main(["drift", str(baseline)]) == 2


def test_doc_schema_references_resolve():
    """Every schemas/<name> mention in OAA plugin markdown resolves to a shipped file."""
    reference = re.compile(r"schemas/([A-Za-z0-9][A-Za-z0-9._-]*)")
    problems = []
    for tree in (CANON_PLUGIN, MIRROR_PLUGIN):
        for md in sorted(tree.rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            for name in set(reference.findall(text)):
                if not (CANON_PLUGIN / "schemas" / name).is_file():
                    problems.append(f"{md.relative_to(REPO_ROOT)}: schemas/{name} does not exist")
    assert not problems, "\n".join(problems)


def test_dangling_schema_promises_removed():
    """The four template-only schema names no longer promise validation."""
    dangling = {
        "business-architecture.json",
        "data-architecture.json",
        "technology-architecture.json",
        "compliance-mapping.json",
    }
    for tree in (CANON_PLUGIN, MIRROR_PLUGIN):
        for md in sorted(tree.rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            leftover = dangling & set(re.findall(r"schemas/([A-Za-z0-9.-]+)", text))
            assert not leftover, f"{md.relative_to(REPO_ROOT)}: dangling schema refs {sorted(leftover)}"


def test_ci_local_gate_wired():
    ci_local = (REPO_ROOT / "scripts" / "ci-local.sh").read_text(encoding="utf-8")
    assert 'python3 plugins/arckit-oaa/validate-architecture.py gate' in ci_local
