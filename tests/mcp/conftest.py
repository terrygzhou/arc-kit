"""Conftest for the arckit-mcp pytest suite.

Adds the ``arckit-mcp`` package directory to ``sys.path`` so the test suite
can import the pure functions from ``arckit_mcp.server`` without an editable
install.
"""

import sys
from pathlib import Path

# arckit-mcp/ lives at the repo root next to tests/.
_ROOT = Path(__file__).resolve().parents[2]
_pkg = _ROOT / "arckit-mcp"
if str(_pkg) not in sys.path:
    sys.path.insert(0, str(_pkg))
