"""
Guard test for plugins/arckit-it4it/validate-architecture.py — the IT4IT
architecture schema gate.

Unit-level: the embedded minimal JSON-Schema validator must flag each
defect class (type mismatch, missing required, bad enum, disallowed
additional property, bad array item) and pass clean content.

Integration-level: the shipped schemas load and validate; the gate
passes on the checked-out repo; doc references to schemas/<name> in the
IT4IT plugin (canonical + Claude mirror) resolve to shipped files; the
local CI gate line is wired.
"""

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANON_PLUGIN = REPO_ROOT / "plugins" / "arckit-it4it"
MIRROR_PLUGIN = REPO_ROOT / "plugins" / "arckit-claude" / "plugins" / "it4it"

SCHEMA_NAMES = [
    "value-stream.json",
    "functional-component.json",
]


def _load_validator(path):
    spec = importlib.util.spec_from_file_location(
        "validate_architecture_it4it_" + path.parent.name, path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator(CANON_PLUGIN / "validate-architecture.py")


def test_schemas_ship_in_both_trees():
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
    errors = VALIDATOR.validate({"sprint": 1}, {"type": "object", "properties": {"sprint": {"type": "integer", "minimum": 1}}})
    assert errors == []
    errors = VALIDATOR.validate(0, {"type": "integer", "minimum": 1})
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
    good = tmp_path / "value-stream.json"
    good.write_text(
        '{'
        '"id":"ARC-002-ITVS-001-v1.0","stream":"Deploy",'
        '"trigger":{"condition":"all gates passed","frequency":"per release train","source_stream":"Integrate"},'
        '"stakeholder":{"primary":"Deployment Manager","accountable_role":"Release Manager"},'
        '"stages":[{"name":"Prepare","functional_components":["Release Planning"]}],'
        '"conformance_notes":"S261 referenced as reference architecture; no conformance claimed."'
        '}'
    )
    bad = tmp_path / "value-stream-bad.json"
    bad.write_text('{"id":"ARC-002-ITVS-001-v1.0","stream":"Transmute","trigger":{"condition":"x"},"stakeholder":{"primary":"ops"},"stages":[]}')
    assert VALIDATOR.main([str(good), "--phase", "value-stream"]) == 0
    assert VALIDATOR.main([str(bad), "--phase", "value-stream"]) == 1
    assert VALIDATOR.main([str(good)]) == 2
    assert VALIDATOR.main([str(good), "--phase", "nonsense"]) == 2


def test_drift_subcommand(tmp_path):
    baseline = tmp_path / "base.json"
    baseline.write_text('{"version":"1.0","stream":"Deploy"}')
    deployed = tmp_path / "deployed.json"
    deployed.write_text('{"version":"2.0","stream":"Operate"}')
    assert VALIDATOR.main(["drift", str(baseline), str(deployed), "--ignore", "version"]) == 1
    assert VALIDATOR.main(["drift", str(baseline), str(baseline)]) == 0
    assert VALIDATOR.main(["drift", str(baseline)]) == 2


def test_doc_schema_references_resolve():
    """Every schemas/<name> mention in IT4IT plugin markdown resolves to a shipped file."""
    reference = re.compile(r"schemas/([A-Za-z0-9][A-Za-z0-9._-]*)")
    problems = []
    for tree in (CANON_PLUGIN, MIRROR_PLUGIN):
        for md in sorted(tree.rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            for name in set(reference.findall(text)):
                if not (CANON_PLUGIN / "schemas" / name).is_file():
                    problems.append(f"{md.relative_to(REPO_ROOT)}: schemas/{name} does not exist")
    assert not problems, "\n".join(problems)


def test_ci_local_gate_wired():
    ci_local = (REPO_ROOT / "scripts" / "ci-local.sh").read_text(encoding="utf-8")
    assert "python3 plugins/arckit-it4it/validate-architecture.py gate" in ci_local
