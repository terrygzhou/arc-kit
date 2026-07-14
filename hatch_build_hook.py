"""Hatch build hook: regenerate extensions from plugins before packaging.

This ensures pipx/git installs produce wheels with all skills, commands, and agents
even though extensions/ is gitignored in the source repo.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class GenerateExtensions(BuildHookInterface):
    """Runs scripts/converter.py during sdist/wheel build."""

    def initialize(self, version: str, build_data: dict) -> None:
        converter = self.root / "scripts" / "converter.py"

        if not converter.exists():
            print("[arckit] WARNING: converter.py not found, skipping extension generation")
            return

        print("[arckit] Generating extensions from plugins...")

        result = subprocess.run(
            [sys.executable, str(converter)],
            cwd=str(self.root),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"[arckit] ERROR: converter.py failed (exit {result.returncode})")
            if result.stdout:
                print(result.stdout[-2000:])
            if result.stderr:
                print(result.stderr[-2000:])
            raise RuntimeError(f"converter.py failed: exit {result.returncode}")

        print("[arckit] Extensions generated successfully")