"""Conftest for the arckit-mcp regression-test suite.

Adds the ``arckit-mcp`` package directory to ``sys.path`` so this suite can
import the pure functions from ``arckit_mcp.server`` without an editable
install.
"""

import sys
from pathlib import Path

# arckit-mcp/ is the directory holding the arckit_mcp/ package.
_pkg_root = Path(__file__).resolve().parents[1]
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))
