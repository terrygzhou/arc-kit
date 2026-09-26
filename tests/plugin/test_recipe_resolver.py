"""Tests for the recipe resolver user-plugin-dir search path (step 4c).

Verifies the user_data_dir('arckit')/plugins/arckit-*/recipes/ search path:
regression without a user plugin dir, happy-path resolution, project-override
precedence, and the FileNotFoundError "Searched:" list. platformdirs and
Path.home are monkeypatched; the real user data dir is never touched.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import arckit_cli  # noqa: E402
from arckit_cli import resolve_recipe_path  # noqa: E402


class _FakePlatformdirs:
    """Stand-in for the platformdirs module attribute used by resolve_recipe_path."""

    def __init__(self, user_data: Path) -> None:
        self._user_data = user_data

    def user_data_dir(self, name: str) -> str:
        assert name == "arckit"
        return str(self._user_data)


@pytest.fixture()
def fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    return home


@pytest.fixture()
def user_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data = tmp_path / "user-data"
    data.mkdir()
    monkeypatch.setattr(arckit_cli, "platformdirs", _FakePlatformdirs(data))
    return data


def _make_recipe(base: Path, *parts: str, name: str) -> Path:
    recipe_dir = base.joinpath(*parts)
    recipe_dir.mkdir(parents=True, exist_ok=True)
    file = recipe_dir / f"{name}.yaml"
    file.write_text("steps: []\n")
    return file


def test_no_user_plugin_dir_is_regression(tmp_path: Path, fake_home: Path, user_data: Path):
    """No plugins/ under the user data dir -> every existing search path behaves as before."""
    project = tmp_path / "project"
    project.mkdir()

    override = _make_recipe(project, ".arckit", "recipes", name="alpha")
    assert resolve_recipe_path("alpha", project) == override

    plugin = _make_recipe(project, "plugins", "arckit-comm", "recipes", name="beta")
    assert resolve_recipe_path("beta", project) == plugin

    skill = _make_recipe(project, "plugins", "arckit-comm", "skills", "sk", "recipes", name="gamma")
    assert resolve_recipe_path("gamma", project) == skill

    local_script = _make_recipe(project, "scripts", "recipes", name="delta")
    assert resolve_recipe_path("delta", project) == local_script

    with pytest.raises(FileNotFoundError) as excinfo:
        resolve_recipe_path("missing", project)
    assert "user plugin:" not in str(excinfo.value)


def test_user_plugin_recipe_resolves(tmp_path: Path, fake_home: Path, user_data: Path):
    project = tmp_path / "project"
    project.mkdir()

    plugin_recipe = _make_recipe(user_data, "plugins", "arckit-userplug", "recipes", name="epsilon")
    assert resolve_recipe_path("epsilon", project) == plugin_recipe


def test_project_override_beats_user_plugin(tmp_path: Path, fake_home: Path, user_data: Path):
    project = tmp_path / "project"
    override = _make_recipe(project, ".arckit", "recipes", name="zeta")
    _make_recipe(user_data, "plugins", "arckit-userplug", "recipes", name="zeta")

    assert resolve_recipe_path("zeta", project) == override


def test_user_plugin_beats_local_scripts(tmp_path: Path, fake_home: Path, user_data: Path):
    project = tmp_path / "project"
    user_recipe = _make_recipe(user_data, "plugins", "arckit-userplug", "recipes", name="eta")
    _make_recipe(project, "scripts", "recipes", name="eta")

    assert resolve_recipe_path("eta", project) == user_recipe


def test_searched_list_includes_user_plugin_path(tmp_path: Path, fake_home: Path, user_data: Path):
    project = tmp_path / "project"
    project.mkdir()
    _make_recipe(user_data, "plugins", "arckit-userplug", "recipes", name="other")

    with pytest.raises(FileNotFoundError) as excinfo:
        resolve_recipe_path("epsilon", project)

    message = str(excinfo.value)
    expected = user_data / "plugins" / "arckit-userplug" / "recipes" / "epsilon.yaml"
    assert "user plugin:" in message
    assert str(expected) in message
