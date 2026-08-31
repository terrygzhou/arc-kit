"""
ArcKit Configuration Resolver

Centralized configuration loading for LLM and other settings.
Prioritizes project-level config over global user config.

``load_config()`` resolves the config file (explicit override, then
project-level, then global) and parses it. ``save_config()`` writes back to
that same resolved path, so config readers and writers always agree on the
file they use.
"""

from pathlib import Path

import platformdirs
import yaml

DEFAULT_GLOBAL_CONFIG_DIR = Path(platformdirs.user_config_dir("arckit"))
DEFAULT_CONFIG_FILENAME = "config.yaml"


class ConfigError(Exception):
    """Raised when the ArcKit config file is unreadable or malformed."""


def get_global_config_path() -> Path:
    """Return the path to the global user config file.

    Platform-dependent (via platformdirs):
    - Linux:   ~/.config/arckit/config.yaml
    - macOS:   ~/Library/Application Support/arckit/config.yaml
    - Windows: %AppData%\\arckit\\config.yaml
    """
    return DEFAULT_GLOBAL_CONFIG_DIR / DEFAULT_CONFIG_FILENAME

def resolve_config_path(config_override: str | None = None) -> Path | None:
    """
    Resolve the configuration file path.

    Order of precedence:
    1. Explicit --config flag
    2. Project-level config (.arckit/config.yaml or arckit.yaml)
    3. Global user config (platformdirs-dependent, e.g.
       ~/.config/arckit/config.yaml on Linux)
    """
    if config_override:
        p = Path(config_override)
        if p.is_file():
            return p
        return None

    cwd = Path.cwd()

    # Check project-level configs
    project_cfg = cwd / ".arckit" / "config.yaml"
    root_cfg = cwd / "arckit.yaml"

    if project_cfg.is_file():
        return project_cfg
    if root_cfg.is_file():
        return root_cfg

    # Fallback to global
    global_cfg = get_global_config_path()
    if global_cfg.is_file():
        return global_cfg

    return None

def load_config(config_override: str | None = None) -> dict:
    """Load the resolved configuration file into a dictionary.

    Args:
        config_override: Explicit config file path (skips resolution).

    Returns:
        The parsed config mapping, or an empty dict when no config file
        exists or the file is empty.

    Raises:
        ConfigError: The file cannot be read, is not valid YAML, or does not
            contain a YAML mapping at the top level.
    """
    path = resolve_config_path(config_override)
    if path is None:
        return {}

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Cannot read config file {path}: {exc}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in config file {path}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(
            f"Config file {path} must contain a YAML mapping at the top level"
        )
    return data


def save_config(cfg: dict, config_override: str | None = None) -> Path:
    """Save the configuration dict to the resolved config file.

    Without an override, writes to the same file load_config() would read:
    the project-level config when one exists, otherwise the global user
    config file. An explicit override is written directly (parents created)
    and never falls back to the global file.

    Args:
        cfg: Configuration mapping to persist.
        config_override: Explicit config file path (skips resolution).

    Returns:
        The path of the file that was written.
    """
    if config_override:
        path = Path(config_override)
    else:
        path = resolve_config_path()
        if path is None:
            path = get_global_config_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(yaml.dump(cfg, default_flow_style=False), encoding="utf-8")
    path.chmod(0o600)
    return path
