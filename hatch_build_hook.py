"""Hatch build hook: regenerate extensions from plugins before packaging.

Ensures pipx/git installs produce wheels with all skills/commands/agents
even though extensions/ is gitignored in the source repo.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class BuildHook:
    """Hatchling custom build hook that runs converter.py before packaging."""

    def __init__(self, root: str):
        self.root = Path(root)

    def initialize(self, version: str, **kwargs: dict) -> None:
        converter = self.root / "scripts" / "converter.py"

        if not converter.exists():
            print("[arckit] WARNING: converter.py not found, skipping extension generation")
            return

        print("[arckit] Generating extensions from plugins...")

        env = dict(__import__("os").environ)
        env["PYTHONPATH"] = str(self.root / "src")

        result = subprocess.run(
            [sys.executable, str(converter)],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode != 0:
            print(f"[arckit] ERROR: converter.py failed (exit {result.returncode})")
            if result.stdout:
                print(result.stdout[-2000:])
            if result.stderr:
                print(result.stderr[-2000:])
            raise RuntimeError(f"converter.py failed: exit {result.returncode}")

        print("[arckit] Extensions generated successfully")