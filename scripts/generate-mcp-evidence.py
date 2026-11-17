#!/usr/bin/env python3
"""Generate framework evidence tool-group modules for arckit-mcp.

Each framework plugin (arckit-oaa, arckit-it4it, arckit-togaf-adm,
arckit-agent-architecture, and future community overlays) declares an
optional ``mcp-evidence.json`` manifest at its plugin root. This script
reads every manifest, validates it, and emits one Python module per
framework under the generated ``arckit_mcp/frameworks/`` package in the
sibling arckit-mcp repo:

* ``arckit_mcp/frameworks/__init__.py`` — the registry:
  ``FRAMEWORK_TOOLS[short_name] = [tool dicts]`` (name, description,
  arguments JSON-schema), ``FRAMEWORK_MODULES`` (the module names to
  import), and the shared helpers the tool bodies rely on
  (``load_schema``, ``SchemaError``, ``SCHEMAS``).
* ``arckit_mcp/frameworks/<short_name>.py`` — per-framework module with
  the tool callables, importable on their own for unit tests.
* ``arckit_mcp/frameworks/SCHEMAS.json`` — the union of every schema
  file referenced by any manifest, embedded as a plain dict keyed by
  schema filename. This is the only schema data the generated modules
  carry: tool bodies load schemas from the ``SCHEMAS`` dict in
  ``__init__.py`` instead of resolving files, so the MCP server works
  from any install location.

The manifest format (``plugins/<plugin>/mcp-evidence.json``)::

    {
      "framework": "oaa",
      "description": "Open Agile Architecture evidence tools",
      "tools": [
        {
          "name": "oaa_check_compliance",
          "description": "Validate a sprint compliance-evidence file",
          "arguments": { "type": "object", "properties": { ... }, "required": [...] },
          "schema": "compliance-evidence.json",
          "impl": "def oaa_check_compliance(evidence): ..."
        }
      ]
    }

Manifest invariants enforced at generation time:

* ``framework`` must be a safe short name: ``[a-z][a-z0-9-]*`` — it
  becomes the module filename (``-`` is allowed in module names only
  for this generated package; the registry key keeps it as-is).
* ``tools`` must be a non-empty list; each ``name`` must be a valid
  Python identifier, unique within the manifest, and prefixed with the
  framework short name (``-`` → ``_``, or ``-``-stripped) so tool names
  stay globally unique across frameworks.
* ``arguments`` must be a JSON-schema object with ``type: "object"``.
* ``schema``, when present, must name a file under the plugin's
  ``schemas/`` directory (validated relative to the manifest's location)
  and be parseable as JSON.
* ``impl`` must be a syntactically valid single top-level Python
  function definition whose name matches the tool's ``name``
  (compiled with ``ast.parse``).

Usage:
    python scripts/generate-mcp-evidence.py [output-dir]

    The optional argument overrides the default output location (the
    ``arckit_mcp/frameworks`` package in the sibling arckit-mcp repo).
    The ARCKIT_MCP_ROOT env var also overrides the sibling-repo root.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path
from pprint import pformat


def _python_literal(obj: object, sort_keys: bool = True) -> str:
    """Render a Python object as a safe, deterministic Python literal.

    Uses pprint.pformat with a sort_keys-aware dump: keys of dicts are
    sorted, and every value is repr()-ed by pprint, so True/False/None
    stay valid Python identifiers and string values are quoted safely.
    This avoids the fragility of string-replacing JSON booleans.
    """
    # Sort keys at every level for deterministic output.
    def _sort(o):
        if isinstance(o, dict):
            return {k: _sort(o[k]) for k in sorted(o)}
        if isinstance(o, list):
            return [_sort(v) for v in o]
        return o

    return pformat(_sort(obj), sort_dicts=True, width=78, compact=False)

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

# Framework plugins that may ship an mcp-evidence.json manifest.
FRAMEWORK_PLUGIN_DIRS = [
    PLUGINS_DIR / name
    for name in (
        "arckit-oaa",
        "arckit-it4it",
        "arckit-togaf-adm",
        "arckit-agent-architecture",
    )
]

SHORT_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ManifestError(Exception):
    pass


def _default_out_dir() -> Path:
    root = Path(os.environ.get("ARCKIT_MCP_ROOT", REPO_ROOT.parent / "arckit-mcp"))
    return root / "arckit_mcp" / "frameworks"


def validate_manifest(manifest: dict, plugin_dir: Path) -> None:
    """Validate one mcp-evidence.json; raise ManifestError on any breach."""
    fw = manifest.get("framework")
    if not isinstance(fw, str) or not SHORT_NAME_RE.match(fw):
        raise ManifestError(
            f"{plugin_dir.name}/mcp-evidence.json: 'framework' must match "
            f"[a-z][a-z0-9-]* (got {fw!r})"
        )
    if not isinstance(manifest.get("description"), str) or not manifest["description"]:
        raise ManifestError(
            f"{plugin_dir.name}/mcp-evidence.json: 'description' must be a "
            f"non-empty string"
        )
    tools = manifest.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ManifestError(
            f"{plugin_dir.name}/mcp-evidence.json: 'tools' must be a non-empty list"
        )

    prefixes = {fw.replace("-", "_"), fw.replace("-", "")}
    seen: set[str] = set()
    for i, tool in enumerate(tools):
        if not isinstance(tool, dict):
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}] must be an object"
            )
        name = tool.get("name")
        if not isinstance(name, str) or not IDENT_RE.match(name):
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].name must be a "
                f"Python identifier (got {name!r})"
            )
        if not any(name.startswith(p) for p in prefixes):
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].name {name!r} "
                f"must start with {sorted(prefixes)} so tool names stay unique "
                f"across frameworks"
            )
        if name in seen:
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: duplicate tool name {name!r}"
            )
        seen.add(name)

        desc = tool.get("description")
        if not isinstance(desc, str) or not desc:
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].description "
                f"must be a non-empty string"
            )
        args = tool.get("arguments")
        if not isinstance(args, dict) or args.get("type") != "object":
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].arguments must be "
                f"a JSON-schema object with type 'object'"
            )
        impl = tool.get("impl")
        if not isinstance(impl, str) or not impl.strip():
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].impl must be a "
                f"non-empty Python function definition string"
            )
        try:
            tree = ast.parse(impl)
        except SyntaxError as e:
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].impl ({name}) "
                f"is not valid Python: {e}"
            ) from e
        if (
            len(tree.body) != 1
            or not isinstance(tree.body[0], ast.FunctionDef)
            or tree.body[0].name != name
        ):
            raise ManifestError(
                f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].impl must be a "
                f"single top-level `def {name}(...)` whose name matches "
                f"tools[{i}].name"
            )

        schema = tool.get("schema")
        if schema is not None:
            if not isinstance(schema, str):
                raise ManifestError(
                    f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].schema must "
                    f"be a string filename (got {type(schema).__name__})"
                )
            spath = plugin_dir / "schemas" / schema
            if not spath.is_file():
                raise ManifestError(
                    f"{plugin_dir.name}/mcp-evidence.json: tools[{i}].schema "
                    f"{schema!r} not found under {plugin_dir.name}/schemas/"
                )
            try:
                json.loads(spath.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise ManifestError(
                    f"{plugin_dir.name}/mcp-evidence.json: schema {schema!r} is not "
                    f"valid JSON: {e}"
                ) from e


def collect() -> list[tuple[Path, dict, Path]]:
    """Return (manifest_path, manifest, plugin_dir) tuples for every manifest."""
    found: list[tuple[Path, dict, Path]] = []
    for plugin_dir in FRAMEWORK_PLUGIN_DIRS:
        manifest_path = plugin_dir / "mcp-evidence.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ManifestError(f"{manifest_path}: manifest must be a JSON object")
        validate_manifest(manifest, plugin_dir)
        found.append((manifest_path, manifest, plugin_dir))
    # Deterministic order: by framework short name.
    found.sort(key=lambda t: t[1]["framework"])
    return found


def render_framework_module(manifest: dict, plugin_dir: Path) -> str:
    """Render arckit_mcp/frameworks/<fw>.py for one framework."""
    fw = manifest["framework"]
    lines: list[str] = [
        f'"""Generated {manifest["description"]}',
        "",
        "DO NOT EDIT BY HAND. This module is generated by arc-kit "
        "scripts/generate-mcp-evidence.py from "
        f"{plugin_dir.name}/mcp-evidence.json and the plugin's schemas/ directory.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import json",
        "",
        "from arckit_mcp.frameworks import SCHEMAS, SchemaError, load_schema",
        "",
        "",
    ]

    # Tool callables — rendered verbatim from the manifest's impl strings
    # (each is a single top-level def, so no re-indentation needed).
    for tool in manifest["tools"]:
        lines.append(tool["impl"].rstrip())
        lines.append("")

    # TOOLS registry: name -> (callable, description, arguments schema, schema file).
    lines.append("TOOLS: dict = {")
    for tool in manifest["tools"]:
        schema_file = json.dumps(tool.get("schema", ""))
        lines.append(
            f"    {json.dumps(tool['name'])}: ("
            f"{tool['name']}, {json.dumps(tool['description'])}, "
            f"{json.dumps(tool['arguments'])}, {schema_file}),"
        )
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_init(manifests: list[tuple[Path, dict, Path]], schemas: dict[str, dict]) -> str:
    """Render arckit_mcp/frameworks/__init__.py — the registry."""
    lines: list[str] = [
        '"""Generated framework tool-group registry.',
        "",
        "DO NOT EDIT BY HAND. This package is generated by arc-kit",
        "scripts/generate-mcp-evidence.py from the mcp-evidence.json",
        "manifests in plugins/arckit-{oaa,it4it,togaf-adm,agent-architecture}/.",
        "",
        "The arckit-mcp server walks FRAMEWORK_TOOLS at startup and",
        "registers each tool via mcp.add_tool, dispatching to the",
        "matching framework module (FRAMEWORK_MODULES). SCHEMAS holds",
        "the union of every schema file any manifest references, so",
        "tools work from any install location without touching the",
        "plugin tree.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import json",
        "",
        "class SchemaError(Exception):",
        '    """Raised when a tool input fails its JSON schema, or the schema is missing."""',
        "",
        # SCHEMAS is embedded as a real Python literal (not a JSON string)
        # so the module imports without a json.loads() round-trip at import
        # time. We serialise each value with repr() which produces valid
        # Python literals (True/False/None) and sorts keys for determinism.
        "SCHEMAS: dict = " + _python_literal(schemas),
        "",
        "def load_schema(name: str):",
        "    \"\"\"Fetch a schema by filename; raise SchemaError if absent.\"\"\"",
        "    if name in SCHEMAS:",
        "        return SCHEMAS[name]",
        "    raise SchemaError(f'schema {name!r} not found in SCHEMAS')",
        "",
    ]

    # FRAMEWORK_MODULES: short_name -> module name (importable as
    # arckit_mcp.frameworks.<name>).
    lines.append("FRAMEWORK_MODULES: dict = {")
    for _, manifest, _ in manifests:
        lines.append(f"    {json.dumps(manifest['framework'])}: {json.dumps(manifest['framework'])},")
    lines.append("}")
    lines.append("")

    # FRAMEWORK_TOOLS: short_name -> [tool dicts].
    lines.append("FRAMEWORK_TOOLS: dict = {")
    for _, manifest, _ in manifests:
        entries = []
        for tool in manifest["tools"]:
            entries.append(
                "        {\n"
                f"            'name': {json.dumps(tool['name'])},\n"
                f"            'description': {json.dumps(tool['description'])},\n"
                f"            'arguments': {json.dumps(tool['arguments'])},\n"
                f"            'schema': {json.dumps(tool.get('schema', ''))},\n"
                "        },"
            )
        lines.append(f"    {json.dumps(manifest['framework'])}: [")
        lines.extend(entries)
        lines.append("    ],")
    lines.append("}")
    lines.append("")

    # Dispatch helper the server uses to invoke a tool by (framework, name).
    lines.extend(
        [
            "def call_tool(framework: str, name: str, arguments: dict):",
            '    """Invoke a framework tool by (framework, tool_name).',
            "",
            "    Imports the framework module on demand so importing this",
            "    package stays cheap, and every tool body is reachable",
            "    without the server hard-coding framework names.",
            "    \"\"\"",
            "    import importlib",
            "",
            "    module = importlib.import_module(f'arckit_mcp.frameworks.{framework}')",
            "    entry = module.TOOLS.get(name)",
            "    if entry is None:",
            "        raise KeyError(f'tool {name!r} not found in framework {framework!r}')",
            "    callable_, _description, _args_schema, _schema_file = entry",
            "    return callable_(**arguments)",
            "",
        ]
    )
    return "\n".join(lines)


def build(out_dir: Path) -> tuple[int, int, int]:
    """Generate the frameworks package under out_dir; return counts."""
    manifests = collect()

    # Union of schema files across all manifests, keyed by filename.
    schemas: dict[str, dict] = {}
    for _, manifest, plugin_dir in manifests:
        for tool in manifest["tools"]:
            schema = tool.get("schema")
            if schema:
                schemas[schema] = json.loads(
                    (plugin_dir / "schemas" / schema).read_text(encoding="utf-8")
                )

    out_dir.mkdir(parents=True, exist_ok=True)
    total_tools = 0
    for _, manifest, plugin_dir in manifests:
        fw = manifest["framework"]
        module_src = render_framework_module(manifest, plugin_dir)
        (out_dir / f"{fw}.py").write_text(module_src, encoding="utf-8")
        total_tools += len(manifest["tools"])

    (out_dir / "__init__.py").write_text(
        render_init(manifests, schemas), encoding="utf-8"
    )
    # SCHEMAS.json sidecar: a plain-JSON dump so non-Python tooling can
    # diff schema drift without importing the package.
    (out_dir / "SCHEMAS.json").write_text(
        json.dumps(schemas, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return len(manifests), total_tools, len(schemas)


def main() -> None:
    out_dir = _default_out_dir()
    if len(sys.argv) > 1:
        out_dir = Path(sys.argv[1])
    n_fw, n_tools, n_schemas = build(out_dir)
    try:
        display = out_dir.relative_to(REPO_ROOT)
    except ValueError:
        display = out_dir
    print(
        f"generated {display}: "
        f"{n_fw} framework module(s), {n_tools} tool(s), {n_schemas} schema(s)"
    )


if __name__ == "__main__":
    main()
