"""Tests for arckit_cli.config — path resolution, load/save, and error handling."""

import os
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from arckit_cli import local  # noqa: E402
from arckit_cli.config import ConfigError, load_config, resolve_config_path, save_config  # noqa: E402


@pytest.fixture(autouse=True)
def isolate_config(tmp_path, monkeypatch):
    """Redirect cwd and the global config dir into tmp_path for every test."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "arckit_cli.config.DEFAULT_GLOBAL_CONFIG_DIR", tmp_path / "global"
    )


def _project_path(tmp_path):
    return tmp_path / ".arckit" / "config.yaml"


def _global_path(tmp_path):
    return tmp_path / "global" / "config.yaml"


def test_load_missing_returns_empty(tmp_path):
    assert load_config() == {}
    assert resolve_config_path() is None


def test_load_project_dot_dir(tmp_path):
    p = _project_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text("llm:\n  base_url: http://proj:1\n")
    assert load_config() == {"llm": {"base_url": "http://proj:1"}}
    assert resolve_config_path() == p


def test_load_root_arckit_yaml(tmp_path):
    p = tmp_path / "arckit.yaml"
    p.write_text("llm:\n  model: root-model\n")
    assert load_config() == {"llm": {"model": "root-model"}}
    assert resolve_config_path() == p


def test_project_takes_precedence_over_global(tmp_path):
    proj = _project_path(tmp_path)
    proj.parent.mkdir(parents=True)
    proj.write_text("llm:\n  model: model-a\n")
    glo = _global_path(tmp_path)
    glo.parent.mkdir(parents=True)
    glo.write_text("llm:\n  model: model-b\n")
    assert load_config() == {"llm": {"model": "model-a"}}
    assert resolve_config_path() == proj


def test_save_writes_to_resolved_project_path(tmp_path):
    """P0-1 regression: save must target the project file that load reads."""
    proj = _project_path(tmp_path)
    proj.parent.mkdir(parents=True)
    proj.write_text("llm:\n  model: old\n")

    cfg = load_config()
    cfg["llm"]["base_url"] = "http://new:2"
    p = save_config(cfg)

    assert p == proj
    data = yaml.safe_load(proj.read_text())
    assert data["llm"]["base_url"] == "http://new:2"
    assert data["llm"]["model"] == "old"
    assert not _global_path(tmp_path).exists()


def test_save_creates_global_when_no_project(tmp_path):
    p = save_config({"llm": {"model": "x"}})
    assert p == _global_path(tmp_path)
    assert p.exists()
    assert yaml.safe_load(p.read_text()) == {"llm": {"model": "x"}}
    assert oct(p.stat().st_mode & 0o777) == "0o600"
    assert oct(p.parent.stat().st_mode & 0o777) == "0o700"


def test_save_override_path(tmp_path):
    """An explicit override is written directly (even if it does not exist
    yet), and never falls back to the global file."""
    custom = tmp_path / "sub" / "custom.yaml"
    p = save_config({"llm": {"model": "custom"}}, str(custom))
    assert p == custom
    assert yaml.safe_load(custom.read_text()) == {"llm": {"model": "custom"}}
    assert not _global_path(tmp_path).exists()


def test_save_override_missing_path_keeps_global(tmp_path):
    """Saving to a bogus override must not clobber the global config."""
    glo = _global_path(tmp_path)
    glo.parent.mkdir(parents=True)
    glo.write_text("llm:\n  model: keep-me\n")

    p = save_config({"llm": {"model": "x"}}, str(tmp_path / "nowhere.yaml"))
    assert p == tmp_path / "nowhere.yaml"
    assert p.exists()
    assert yaml.safe_load(glo.read_text()) == {"llm": {"model": "keep-me"}}


def test_load_invalid_yaml_raises(tmp_path):
    p = _project_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text("llm: [unclosed\n")
    with pytest.raises(ConfigError, match="Invalid YAML"):
        load_config()


def test_load_non_mapping_raises(tmp_path):
    p = _project_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text("- a\n- b\n")
    with pytest.raises(ConfigError, match="mapping"):
        load_config()


def test_load_empty_returns_empty(tmp_path):
    p = _project_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text("")
    assert load_config() == {}


def test_cli_config_set_writes_project_file(tmp_path):
    """P0-1 regression (user-visible): `arckit config set` writes the project file."""
    from typer.testing import CliRunner

    from arckit_cli import config_app

    proj = _project_path(tmp_path)
    proj.parent.mkdir(parents=True)
    proj.write_text("llm:\n  model: old\n")

    runner = CliRunner()
    result = runner.invoke(config_app, ["set", "llm.model", "new-model"])
    assert result.exit_code == 0, result.output

    data = yaml.safe_load(proj.read_text())
    assert data["llm"]["model"] == "new-model"
    assert not _global_path(tmp_path).exists()


# ---------------------------------------------------------------------------
# local.py — config helpers and the double-run setup regression
# ---------------------------------------------------------------------------


def test_local_load_returns_full_config(tmp_path):
    """_load_config must return the whole mapping, not just the llm block."""
    p = _project_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text("llm:\n  model: m1\n")

    loaded = local._load_config()
    assert loaded.get("llm", {}).get("model") == "m1"


def test_local_setup_twice_does_not_nest_llm(tmp_path):
    """Two setup-equivalent save runs must not duplicate/nest the llm block.

    Pins the pre-existing bug where local._load_config() returned the inner
    ``llm`` sub-dict, so a second ``arckit local setup`` run nested a duplicate
    ``llm`` block inside the previous top-level llm keys (reviewer finding 5).
    """
    p = _project_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text(
        "llm:\n"
        "  provider: openai-compatible\n"
        "  base_url: http://a:1\n"
        "  model: m1\n"
        "  api_key: ''\n"
        "  max_tokens: 100\n"
        "  temperature: 0.1\n"
    )

    for url, model in (("http://a:1", "m1"), ("http://b:2", "m2")):
        # Mirror setup()'s flow: load full config, replace the llm block, save
        cfg = local._load_config()
        llm = cfg.get(local.CONFIG_KEY, {})
        assert llm.get("model") in ("m1", "m2"), "prefill should see previous model"
        cfg[local.CONFIG_KEY] = {
            "provider": "openai-compatible",
            "base_url": url,
            "model": model,
            "api_key": "",
            "max_tokens": 200,
            "temperature": 0.2,
        }
        local._save_config(cfg)

    data = load_config()
    assert set(data.keys()) == {local.CONFIG_KEY}, (
        f"unexpected top-level keys: {data.keys()}"
    )
    assert data[local.CONFIG_KEY]["model"] == "m2"
    assert data[local.CONFIG_KEY]["base_url"] == "http://b:2"
    raw = yaml.safe_load(p.read_text())
    assert "llm" not in raw[local.CONFIG_KEY], "llm block must not be nested inside itself"


def test_local_get_config_path_points_at_project_file(tmp_path):
    """The displayed 'Config stored at' path must match the real read/write target."""
    p = _project_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text("llm:\n  model: m\n")

    assert local._get_config_path() == p


# ---------------------------------------------------------------------------
# P0-3 CLI-level error handling and remaining edge pins
# ---------------------------------------------------------------------------


def test_cli_config_list_corrupt_config_exits_clean(tmp_path):
    """Malformed project config: CLI reports 'Config error' and exits 1, no traceback."""
    from typer.testing import CliRunner

    from arckit_cli import config_app

    proj = _project_path(tmp_path)
    proj.parent.mkdir(parents=True)
    proj.write_text("llm: [unclosed\n")

    runner = CliRunner()
    result = runner.invoke(config_app, ["list"])
    assert result.exit_code == 1, result.output
    assert "Config error" in result.output
    assert "Traceback" not in result.output


@pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses file permissions")
def test_load_unreadable_file_raises(tmp_path):
    proj = _project_path(tmp_path)
    proj.parent.mkdir(parents=True)
    proj.write_text("llm:\n  model: m\n")
    os.chmod(proj, 0o000)
    try:
        with pytest.raises(ConfigError, match="Cannot read"):
            load_config()
    finally:
        os.chmod(proj, 0o644)


def test_empty_project_file_still_targets_project_for_save(tmp_path):
    """An empty (but present) project file must not fall through to global for save."""
    proj = _project_path(tmp_path)
    proj.parent.mkdir(parents=True)
    proj.write_text("")
    glo = _global_path(tmp_path)
    glo.parent.mkdir(parents=True)
    glo.write_text("llm:\n  model: global-model\n")

    assert resolve_config_path() == proj
    p = save_config({"llm": {"model": "x"}})
    assert p == proj
    assert yaml.safe_load(glo.read_text()) == {"llm": {"model": "global-model"}}
