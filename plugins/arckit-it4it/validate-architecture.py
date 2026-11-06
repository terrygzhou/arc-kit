#!/usr/bin/env python3
"""ArcKit IT4IT architecture artifact validator.

Validates IT4IT architecture artifacts (value streams and functional
components) against the shared JSON Schemas shipped in
plugins/arckit-it4it/schemas/.

Stdlib-only: ships an embedded minimal JSON-Schema (draft-07) validator
covering exactly the keyword subset used by the shipped schemas
(type, required, properties, additionalProperties, items, enum, const,
minimum, maximum, minItems, maxItems, minLength, maxLength). No
third-party dependencies; YAML artifacts/schemas are handled via PyYAML
when available, with a clear error (or skip in self-test/gate) when it
is not installed.

Usage:
  validate-architecture.py ARTIFACT [--phase PHASE | --schema SCHEMA_FILE]
  validate-architecture.py drift BASELINE DEPLOYED [--ignore DOTTED.PATH ...]
  validate-architecture.py self-test
  validate-architecture.py gate

Exit codes: 0 ok, 1 validation/drift/gate failure, 2 usage error.
"""

from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMAS_DIR = os.path.join(_HERE, "schemas")

PHASE_SCHEMAS = {
    "value-stream": "value-stream.json",
    "functional-component": "functional-component.json",
}

ALL_SCHEMAS = list(PHASE_SCHEMAS.values())


def _load_yaml_module():
    try:
        import yaml  # type: ignore

        return yaml
    except ImportError:
        return None


def load_data_file(path):
    """Load a .json or .yaml/.yml data/schema file into Python objects."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    lower = path.lower()
    if lower.endswith(".json"):
        return json.loads(text)
    if lower.endswith((".yaml", ".yml")):
        yaml_mod = _load_yaml_module()
        if yaml_mod is None:
            raise SystemExit(
                "error: %s is a YAML file but PyYAML is not installed. "
                "Install it with: pip install pyyaml" % path
            )
        return yaml_mod.safe_load(text)
    # Fall back: try JSON, then YAML.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        yaml_mod = _load_yaml_module()
        if yaml_mod is None:
            raise SystemExit(
                "error: could not parse %s (not valid JSON and PyYAML not "
                "installed)" % path
            )
        return yaml_mod.safe_load(text)


def _type_ok(value, type_name):
    if type_name == "object":
        return isinstance(value, dict)
    if type_name == "array":
        return isinstance(value, list)
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name == "boolean":
        return isinstance(value, bool)
    if type_name == "null":
        return value is None
    return True


def validate(instance, schema, path="$"):
    """Validate instance against schema; return a list of error strings.

    Covers the keyword subset used by the shipped IT4IT schemas.
    """
    errors = []
    schema_type = schema.get("type")
    if schema_type is not None:
        wanted = schema_type if isinstance(schema_type, list) else [schema_type]
        if not any(_type_ok(instance, t) for t in wanted):
            errors.append(
                "%s: expected type %s, got %s"
                % (path, schema_type, type(instance).__name__)
            )
            return errors
    if "enum" in schema and instance not in schema["enum"]:
        errors.append("%s: value not in enum %r" % (path, schema["enum"]))
    if "const" in schema and instance != schema["const"]:
        errors.append("%s: value not equal to const %r" % (path, schema["const"]))
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(
                "%s: string shorter than minLength %d" % (path, schema["minLength"])
            )
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(
                "%s: string longer than maxLength %d" % (path, schema["maxLength"])
            )
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append("%s: %r below minimum %r" % (path, instance, schema["minimum"]))
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append("%s: %r above maximum %r" % (path, instance, schema["maximum"]))
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(
                "%s: %d items, fewer than minItems %d"
                % (path, len(instance), schema["minItems"])
            )
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(
                "%s: %d items, more than maxItems %d" % (path, len(instance), schema["maxItems"])
            )
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, element in enumerate(instance):
                errors.extend(validate(element, item_schema, "%s[%d]" % (path, index)))
    if isinstance(instance, dict):
        for required_key in schema.get("required", []):
            if required_key not in instance:
                errors.append("%s: missing required property %r" % (path, required_key))
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = "%s.%s" % (path, key)
            if key in properties:
                errors.extend(validate(value, properties[key], child_path))
            elif additional is False:
                errors.append("%s: additional property not allowed" % child_path)
            elif isinstance(additional, dict):
                errors.extend(validate(value, additional, child_path))
    return errors


def diff_dicts(baseline, deployed, path="$", ignore=()):
    """Recursive dict diff. Returns a list of human-readable drift entries.

    A key ignored via --ignore (dotted path) is skipped on the baseline
    side.
    """
    def is_ignored(current_path):
        parts = current_path.lstrip("$").strip(".").split(".") if current_path != "$" else []
        # Dotted paths from --ignore are relative (no leading '$').
        rel = ".".join(parts)
        for ignore_path in ignore:
            if rel == ignore_path or (rel and rel.startswith(ignore_path + ".")):
                return True
        return False

    drift = []
    if not isinstance(baseline, dict) or not isinstance(deployed, dict):
        if baseline != deployed:
            drift.append("%s: %r changed to %r" % (path, baseline, deployed))
        return drift
    for key in sorted(set(baseline) | set(deployed)):
        child = "%s.%s" % (path, key)
        if is_ignored(child):
            continue
        if key not in deployed:
            drift.append("%s: present in baseline (%r), missing in deployed" % (child, baseline[key]))
        elif key not in baseline:
            drift.append("%s: missing in baseline, present in deployed (%r)" % (child, deployed[key]))
        else:
            drift.extend(diff_dicts(baseline[key], deployed[key], child, ignore))
    return drift


# ---------------------------------------------------------------------------
# Self-test fixtures: one valid + one corrupt fixture per shipped schema.
# ---------------------------------------------------------------------------

SELF_TEST_FIXTURES = {
    "value-stream.json": {
        "valid": {
            "id": "ARC-002-ITVS-001-v1.0",
            "stream": "Deploy",
            "scenario": "Release to production environment",
            "trigger": {
                "condition": "All quality gates passed in Test",
                "frequency": "per release train",
                "source_stream": "Integrate",
            },
            "stakeholder": {
                "primary": "Deployment Manager",
                "accountable_role": "Release Manager",
                "contributing_roles": ["Operations", "QA"],
            },
            "stages": [
                {
                    "name": "Prepare release",
                    "functional_components": ["Release Planning"],
                    "kdo_in": ["Deployment Plan"],
                    "kdo_out": ["Deployment Release"],
                }
            ],
            "cross_stream": [
                {
                    "direction": "inbound",
                    "stream": "Integrate",
                    "handoff_kdo": "Deployment Package",
                    "contract": "1:1, SoR: artifact repository",
                }
            ],
            "scenarios": ["Release to production environment"],
            "system_of_record": {"Deployment Plan": "release manager tool"},
            "conformance_notes": "S261 referenced as a reference architecture; no conformance claim.",
        },
        "corrupt": {
            "id": "ARC-002-ITVS-001-v1.0",
            "stream": "Transmute",  # not in the seven-stream enum
            "trigger": {"condition": "x"},
            "stakeholder": {"primary": "ops"},
            "stages": [],  # minItems 1 violated
        },
    },
    "functional-component.json": {
        "valid": {
            "id": "ARC-002-ITSF-v1.0",
            "function": "Portfolio",
            "components": [
                {
                    "name": "Portfolio Planning",
                    "purpose": "balance the candidate value streams",
                    "primary_kdos": ["Value Stream Proposal"],
                    "key_attributes": ["priority", "business value"],
                }
            ],
            "key_data_objects": ["Value Stream Proposal", "Business Capability"],
            "cardinalities": [
                {
                    "left": "Value Stream Proposal",
                    "right": "Business Capability",
                    "cardinality": "n:m",
                    "gap": "S261 does not mandate a fixed cardinality here",
                }
            ],
            "states": ["Draft", "Approved", "Funded", "Retired"],
            "system_of_record": {"Value Stream Proposal": "portfolio board"},
            "conformance_notes": "S261 referenced as a reference architecture; no conformance claim.",
        },
        "corrupt": {
            "id": "ARC-002-ITSF-v1.0",
            "function": "Black Magic",  # not in the function-group enum
            "components": [],  # minItems 1 violated
        },
    },
}


def schema_path(name):
    return os.path.join(SCHEMAS_DIR, name)


def load_schema(name):
    """Return (schema_dict_or_None, error_or_None). None + no error means
    YAML schema whose loader is unavailable."""
    path = schema_path(name)
    if not os.path.exists(path):
        return None, "schema not found: %s" % name
    try:
        data = load_data_file(path)
    except SystemExit as exc:
        return None, str(exc).replace("error: ", "")
    if not isinstance(data, dict):
        return None, "schema %s did not parse to an object" % name
    if "type" not in data:
        return None, "schema %s is missing its top-level 'type'" % name
    return data, None


def run_self_test(quiet=False):
    """Run embedded validator self-test against all shipped schemas."""
    failures = []
    checked = 0
    for name, fixtures in SELF_TEST_FIXTURES.items():
        schema, err = load_schema(name)
        if schema is None:
            if err.startswith("PyYAML"):
                if not quiet:
                    print("SKIP %s (PyYAML unavailable)" % name)
                continue
            failures.append("schema check %s: %s" % (name, err))
            continue
        if not quiet:
            print("OK   %s (schema loads and is structurally valid)" % name)
        checked += 1
        valid_errors = validate(fixtures["valid"], schema)
        if valid_errors:
            failures.append(
                "%s: valid fixture rejected: %s" % (name, "; ".join(valid_errors[:3]))
            )
        corrupt_errors = validate(fixtures["corrupt"], schema)
        if not corrupt_errors:
            failures.append("%s: corrupt fixture was NOT rejected" % name)
    if not quiet:
        print(
            "self-test: %d/%d schemas checked, %d failure(s)"
            % (checked, len(SELF_TEST_FIXTURES), len(failures))
        )
    for failure in failures:
        print("FAIL %s" % failure)
    return len(failures) == 0


def run_gate():
    """CI gate: load + sanity-check all 2 shipped schemas, run self-test."""
    print("gate: loading %d shipped schemas from %s" % (len(ALL_SCHEMAS), SCHEMAS_DIR))
    for name in ALL_SCHEMAS:
        schema, err = load_schema(name)
        if schema is None and err and err.startswith("PyYAML"):
            print("SKIP %s (%s; gate stays green offline)" % (name, err.split(".")[0]))
        elif schema is None:
            print("FAIL %s: %s" % (name, err))
            return 1
        else:
            print("OK   %s" % name)
    ok = run_self_test(quiet=False)
    print("gate: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def print_errors(artifact, errors):
    print("INVALID %s" % artifact)
    for error in errors:
        print("  - %s" % error)


def cmd_artifact(rest):
    artifact = None
    phase = None
    schema_file = None
    positional = []
    i = 0
    while i < len(rest):
        arg = rest[i]
        if arg == "--phase":
            i += 1
            if i >= len(rest):
                print("error: --phase needs a value (one of: %s)" % ", ".join(PHASE_SCHEMAS))
                return 2
            phase = rest[i]
        elif arg == "--schema":
            i += 1
            if i >= len(rest):
                print("error: --schema needs a file path")
                return 2
            schema_file = rest[i]
        elif arg.startswith("--phase="):
            phase = arg.split("=", 1)[1]
        elif arg.startswith("--schema="):
            schema_file = arg.split("=", 1)[1]
        else:
            positional.append(arg)
        i += 1
    if positional:
        artifact = positional[0]
        if len(positional) > 1:
            print("error: unexpected extra argument %r" % positional[1])
            return 2
    if artifact is None:
        print(
            "error: missing ARTIFACT argument.\n"
            "usage: validate-architecture.py ARTIFACT [--phase PHASE | --schema SCHEMA_FILE]"
        )
        return 2
    if phase and schema_file:
        print("error: use either --phase or --schema, not both")
        return 2
    if phase:
        if phase not in PHASE_SCHEMAS:
            print(
                "error: unknown phase %r (expected one of: %s)"
                % (phase, ", ".join(PHASE_SCHEMAS))
            )
            return 2
        schema, err = load_schema(PHASE_SCHEMAS[phase])
        schema_name = PHASE_SCHEMAS[phase]
    elif schema_file:
        schema_name = os.path.basename(schema_file)
        try:
            schema = load_data_file(schema_file)
        except (OSError, SystemExit) as exc:
            print("error: cannot load schema %s: %s" % (schema_file, exc))
            return 2
        err = None
    else:
        print(
            "error: no --phase given; pass --phase PHASE or --schema SCHEMA_FILE.\n"
            "phases: %s" % ", ".join(PHASE_SCHEMAS)
        )
        return 2
    if schema is None:
        print("error: %s" % err)
        return 2
    try:
        data = load_data_file(artifact)
    except (OSError, SystemExit) as exc:
        print("error: cannot load artifact %s: %s" % (artifact, exc))
        return 2
    errors = validate(data, schema)
    if errors:
        print_errors(artifact, errors)
        print("INVALID %s (schema: %s)" % (artifact, schema_name))
        return 1
    print("VALID %s (schema: %s)" % (artifact, schema_name))
    return 0


def _parse_ignores(rest):
    ignores = []
    i = 0
    positional = []
    while i < len(rest):
        arg = rest[i]
        if arg == "--ignore":
            i += 1
            if i >= len(rest):
                return None
            ignores.append(rest[i])
        elif arg.startswith("--ignore="):
            ignores.append(arg.split("=", 1)[1])
        else:
            positional.append(arg)
        i += 1
    return ignores, positional


def cmd_drift(rest):
    parsed = _parse_ignores(rest)
    if parsed is None:
        print("error: --ignore needs a dotted path")
        return 2
    ignores, positional = parsed
    if len(positional) != 2:
        print(
            "usage: validate-architecture.py drift BASELINE DEPLOYED "
            "[--ignore DOTTED.PATH ...]"
        )
        return 2
    baseline_path, deployed_path = positional
    try:
        baseline = load_data_file(baseline_path)
        deployed = load_data_file(deployed_path)
    except (OSError, SystemExit) as exc:
        print("error: cannot load drift input: %s" % exc)
        return 2
    drift = diff_dicts(baseline, deployed, ignore=ignores)
    if drift:
        print("DRIFT %s vs %s (%d entry/entries)" % (baseline_path, deployed_path, len(drift)))
        for entry in drift:
            print("  - %s" % entry)
        return 1
    print("NO DRIFT %s vs %s" % (baseline_path, deployed_path))
    return 0


USAGE = """usage: validate-architecture.py ARTIFACT [--phase PHASE | --schema SCHEMA_FILE]
       validate-architecture.py drift BASELINE DEPLOYED [--ignore DOTTED.PATH ...]
       validate-architecture.py self-test
       validate-architecture.py gate

phases: %s
""" % ", ".join(PHASE_SCHEMAS)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    command, rest = args[0], args[1:]
    if command == "self-test":
        if rest:
            print("error: self-test takes no arguments")
            return 2
        return 0 if run_self_test() else 1
    if command == "gate":
        if rest:
            print("error: gate takes no arguments")
            return 2
        return run_gate()
    if command == "drift":
        return cmd_drift(rest)
    return cmd_artifact(args)


if __name__ == "__main__":
    sys.exit(main())
