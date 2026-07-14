#!/usr/bin/env bash
# ArcKit CLI — One-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/terrygzhou/arc-kit/main/install.sh | bash
#
# Auto-detects: uv (recommended) → pipx → pip --user

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { printf "${GREEN}✓${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}⚠${NC} %s\n" "$*" >&2; }
die()  { printf "${RED}✗${NC} %s\n" "$*" >&2; exit 1; }

# ── Prerequisites ──────────────────────────────────────────────────────────
command -v git >/dev/null 2>&1  || die "git is required"
command -v python3 >/dev/null 2>&1 || die "python3 is required"

PY_OK=$(python3 -c 'import sys; print(sys.version_info >= (3, 11))' 2>/dev/null || echo "False")
[[ "$PY_OK" == "True" ]] || die "Python ≥ 3.11 required (got $(python3 --version 2>&1))"

# ── Install ────────────────────────────────────────────────────────────────
if command -v uv >/dev/null 2>&1; then
  log "Installing via uv (recommended)"
  uv tool install arckit-cli

elif command -v pipx >/dev/null 2>&1; then
  log "Installing via pipx"
  pipx install arckit-cli

else
  warn "Neither uv nor pipx found — using pip --user"
  # --break-system-packages required on PEP 668 distros (Debian/Ubuntu/Pop!_OS)
  pip install --user --break-system-packages arckit-cli

  local_bin="${HOME}/.local/bin"
  if [[ -d "$local_bin" && ":${PATH}:" != *":${local_bin}:"* ]]; then
    warn "Adding ~/.local/bin to PATH (persist: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc)"
    export PATH="${local_bin}:${PATH}"
  fi
fi

# ── Verify ─────────────────────────────────────────────────────────────────
if command -v arckit >/dev/null 2>&1; then
  log "arckit installed ✓"
  log "Get started:  arckit init my-project"
  log "Existing dir: cd my-project && arckit init . --ai codex"
else
  die "'arckit' not found on PATH. Re-source your shell or add ~/.local/bin to PATH."
fi