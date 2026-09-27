"""EYW-348: local-LLM build resilience + post-build diagram consolidation.

Covers the arckit CLI 6.10.1 defects observed on the gloryev build
(EYW-345):

* (a) configurable tool-iteration cap (default 96, config + env override)
* (b) a target with a declared output only completes when the artifact
      exists on disk
* (f) post-build PlantUML diagram sweep (puml sidecars + svg renders,
      idempotent, graceful degradation, self-containment audit)

Defects (c) and (d) live in build-command closures (``_get_dep_file_path``
and ``_derive_p_placeholders``) that need the full build context; they are
exercised by the manual resume scenarios recorded in the issue thread.
"""

import asyncio
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from arckit_cli.llm import (
    LLMConfig,
    resolve_config,
    execute_target,
)
from arckit_cli.recipe import Target
import arckit_cli.diagrams as diagrams


def _config(**kwargs) -> LLMConfig:
    base = dict(
        provider="openai-compatible",
        base_url="http://127.0.0.1:8080",
        model="test-model",
        api_key="",
    )
    base.update(kwargs)
    return LLMConfig(**base)


def _target(output=None, target_id="ADMP") -> Target:
    return Target(
        id=target_id,
        skill="arckit-test-skill",
        args="",
        output=output if output is not None else {},
        deps=[],
    )


def _skill_file(tmp_path: Path) -> Path:
    skill = tmp_path / "SKILL.md"
    skill.write_text("# Test skill\nProduce the artifact.\n", encoding="utf-8")
    return skill


def _llm_response(content=None, tool_calls=None, total_tokens=10):
    message = {}
    if content is not None:
        message["content"] = content
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return {"choices": [{"message": message}], "usage": {"total_tokens": total_tokens}}


def _tool_call(name, args, call_id="call-1"):
    return {
        "id": call_id,
        "function": {"name": name, "arguments": json.dumps(args)},
    }


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# (a) Tool-iteration cap — resolve_config
# ---------------------------------------------------------------------------

def test_resolve_config_cap_default_is_96(monkeypatch, tmp_path):
    monkeypatch.setenv("ARCKIT_MAX_TOOL_ITERATIONS", "")
    monkeypatch.chdir(tmp_path)
    with patch("arckit_cli.llm._load_config", return_value={}):
        cfg = resolve_config(cli_base_url="http://127.0.0.1:8080", cli_model="m")
    assert cfg.max_tool_iterations == 96


def test_resolve_config_cap_from_config_file(monkeypatch, tmp_path):
    monkeypatch.setenv("ARCKIT_MAX_TOOL_ITERATIONS", "")
    monkeypatch.chdir(tmp_path)
    with patch(
        "arckit_cli.llm._load_config",
        return_value={"llm": {"max_tool_iterations": 42}},
    ):
        cfg = resolve_config(cli_base_url="http://127.0.0.1:8080", cli_model="m")
    assert cfg.max_tool_iterations == 42


def test_resolve_config_cap_env_overrides_config(monkeypatch, tmp_path):
    monkeypatch.setenv("ARCKIT_MAX_TOOL_ITERATIONS", "99")
    monkeypatch.chdir(tmp_path)
    with patch(
        "arckit_cli.llm._load_config",
        return_value={"llm": {"max_tool_iterations": 42}},
    ):
        cfg = resolve_config(cli_base_url="http://127.0.0.1:8080", cli_model="m")
    assert cfg.max_tool_iterations == 99


def test_resolve_config_cap_invalid_env_falls_back(monkeypatch, tmp_path):
    monkeypatch.setenv("ARCKIT_MAX_TOOL_ITERATIONS", "not-a-number")
    monkeypatch.chdir(tmp_path)
    with patch(
        "arckit_cli.llm._load_config",
        return_value={"llm": {"max_tool_iterations": 42}},
    ):
        cfg = resolve_config(cli_base_url="http://127.0.0.1:8080", cli_model="m")
    assert cfg.max_tool_iterations == 42


# ---------------------------------------------------------------------------
# (a)/(b) execute_target — cap enforcement + declared-output gate
# ---------------------------------------------------------------------------

def test_execute_target_cap_exhaustion_fails(tmp_path):
    skill = _skill_file(tmp_path)
    target = _target(output={"path": "out/ARC-001-ADMP-v1.0.md"})
    config = _config(max_tool_iterations=3)
    read_call = _tool_call("Read", {"path": "does-not-exist.md"})
    response = _llm_response(tool_calls=[read_call])

    async def run():
        with patch("arckit_cli.llm.call_llm", new=AsyncMock(return_value=response)):
            return await execute_target(target, config, tmp_path, skill, {})

    result = asyncio.run(run())
    assert result.status == "failed"
    assert "exceeded 3 iterations" in result.error
    assert result.tool_calls_count == 3
    assert result.output_sha256 is None


def test_execute_target_stop_without_declared_artifact_fails(tmp_path):
    skill = _skill_file(tmp_path)
    target = _target(output={"path": "out/ARC-001-ADMP-v1.0.md"})
    config = _config(max_tool_iterations=3)

    async def run():
        # Model stops immediately (no tool calls) without producing the file.
        with patch("arckit_cli.llm.call_llm", new=AsyncMock(
            return_value=_llm_response(content="done.")
        )):
            return await execute_target(target, config, tmp_path, skill, {})

    result = asyncio.run(run())
    assert result.status == "failed"
    assert "declared output artifact was not found" in result.error


def test_execute_target_stop_with_declared_artifact_succeeds(tmp_path):
    skill = _skill_file(tmp_path)
    target = _target(output={"path": "out/ARC-001-ADMP-v1.0.md"})
    artifact = tmp_path / "out" / "ARC-001-ADMP-v1.0.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("artifact content", encoding="utf-8")
    config = _config(max_tool_iterations=3)

    async def run():
        with patch("arckit_cli.llm.call_llm", new=AsyncMock(
            return_value=_llm_response(content="done.")
        )):
            return await execute_target(target, config, tmp_path, skill, {})

    result = asyncio.run(run())
    # Pre-execution shortcut: the file already existed, so the target is
    # closed as success via the skip path (no hash computed on shortcut).
    assert result.status == "success"
    assert result.output_path == str(artifact)


def test_execute_target_write_then_stop_succeeds(tmp_path):
    skill = _skill_file(tmp_path)
    target = _target(output={"path": "out/ARC-001-ADMP-v1.0.md"})
    config = _config(max_tool_iterations=3)
    write_call = _tool_call(
        "Write", {"path": "out/ARC-001-ADMP-v1.0.md", "content": "written"}
    )

    async def run():
        llm = AsyncMock(side_effect=[
            _llm_response(tool_calls=[write_call]),
            _llm_response(content="done."),
        ])
        with patch("arckit_cli.llm.call_llm", new=llm):
            return await execute_target(target, config, tmp_path, skill, {})

    result = asyncio.run(run())
    assert result.status == "success"
    assert result.output_path == str(tmp_path / "out" / "ARC-001-ADMP-v1.0.md")
    assert result.output_sha256 == _sha256_bytes(b"written")


def test_execute_target_no_declared_output_succeeds_without_artifact(tmp_path):
    skill = _skill_file(tmp_path)
    target = _target(output={})
    config = _config(max_tool_iterations=3)

    async def run():
        with patch("arckit_cli.llm.call_llm", new=AsyncMock(
            return_value=_llm_response(content="analysis complete")
        )):
            return await execute_target(target, config, tmp_path, skill, {})

    result = asyncio.run(run())
    assert result.status == "success"
    assert result.output_path is None


# ---------------------------------------------------------------------------
# (f) Post-build diagram consolidation
# ---------------------------------------------------------------------------

def _project_with_blocks(tmp_path: Path) -> Path:
    proj = tmp_path / "projects" / "001-Foo"
    proj.mkdir(parents=True)
    doc = proj / "ARC-001-ADMP-v1.0.md"
    doc.write_text(
        "# Architecture Design Model\n\n"
        "## Views\n\n"
        "```plantuml\n@startuml\nrectangle \"App\"\n@enduml\n```\n\n"
        "## Components\n\n"
        "```plantuml\n@startuml\ncomponent \"DB\"\n@enduml\n```\n\n",
        encoding="utf-8",
    )
    (proj / "notes.md").write_text("# No diagrams here\n", encoding="utf-8")
    return proj


def test_diagrams_no_jar_writes_puml_pending(tmp_path, monkeypatch):
    proj = _project_with_blocks(tmp_path)
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)

    summary = diagrams.consolidate_project_diagrams(tmp_path)

    assert summary["docs_scanned"] == 1
    assert summary["blocks_found"] == 2
    assert summary["puml_written"] == 2
    assert summary["rendered"] == 0
    assert summary["pending"] == 2
    diagrams_dir = proj / "diagrams"
    assert (diagrams_dir / "views.puml").is_file()
    assert (diagrams_dir / "components.puml").is_file()
    manifest = json.loads((diagrams_dir / "manifest.json").read_text())
    assert len(manifest["blocks"]) == 2
    assert all(b["status"] == "pending" for b in manifest["blocks"].values())


def test_diagrams_rendered_with_svg_and_external_refs(tmp_path, monkeypatch):
    proj = _project_with_blocks(tmp_path)
    monkeypatch.setattr(
        diagrams, "find_plantuml_jar", lambda explicit=None: "fake.jar"
    )
    monkeypatch.setattr(diagrams.shutil, "which", lambda name: "/usr/bin/java")

    def fake_render(puml, jar, java):
        svg = puml.with_suffix(".svg")
        svg.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<a href="http://example.com/leak">x</a></svg>',
            encoding="utf-8",
        )
        return True

    monkeypatch.setattr(diagrams, "_render_puml", fake_render)

    summary = diagrams.consolidate_project_diagrams(tmp_path)

    assert summary["rendered"] == 2
    assert summary["pending"] == 0
    assert "http://example.com/leak" in summary["external_refs"][
        str(proj / "diagrams" / "views.svg")
    ]


def test_diagrams_rerun_idempotent(tmp_path, monkeypatch):
    _project_with_blocks(tmp_path)
    monkeypatch.setattr(
        diagrams, "find_plantuml_jar", lambda explicit=None: "fake.jar"
    )
    monkeypatch.setattr(diagrams.shutil, "which", lambda name: "/usr/bin/java")

    def fake_render(puml, jar, java):
        puml.with_suffix(".svg").write_text("<svg/>", encoding="utf-8")
        return True

    monkeypatch.setattr(diagrams, "_render_puml", fake_render)

    first = diagrams.consolidate_project_diagrams(tmp_path)
    assert first["rendered"] == 2
    second = diagrams.consolidate_project_diagrams(tmp_path)
    assert second["rendered"] == 0
    assert second["unchanged"] == 2
    assert second["puml_written"] == 0


def test_diagrams_two_blocks_same_heading_get_suffix(tmp_path, monkeypatch):
    proj = tmp_path / "projects" / "001-Foo"
    proj.mkdir(parents=True)
    (proj / "doc.md").write_text(
        "## Views\n"
        "```plantuml\n@startuml\na\n@enduml\n```\n"
        "```plantuml\n@startuml\nb\n@enduml\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(diagrams, "find_plantuml_jar", lambda explicit=None: None)

    diagrams.consolidate_project_diagrams(tmp_path)

    diagrams_dir = proj / "diagrams"
    assert (diagrams_dir / "views.puml").is_file()
    assert (diagrams_dir / "views-2.puml").is_file()


def test_diagrams_no_projects_dir_is_noop(tmp_path):
    summary = diagrams.consolidate_project_diagrams(tmp_path)
    assert summary["docs_scanned"] == 0
    assert summary["blocks_found"] == 0


def test_find_plantuml_jar_explicit_and_env(tmp_path, monkeypatch):
    jar = tmp_path / "plantuml-1.2026.8.jar"
    jar.write_text("zip")
    assert diagrams.find_plantuml_jar(str(jar)) == str(jar)
    assert diagrams.find_plantuml_jar(str(tmp_path / "missing.jar")) is None
    monkeypatch.setenv("PLANTUML_JAR", str(jar))
    assert diagrams.find_plantuml_jar() == str(jar)
    monkeypatch.setenv("PLANTUML_JAR", str(tmp_path / "nope.jar"))
    assert diagrams.find_plantuml_jar() is None
