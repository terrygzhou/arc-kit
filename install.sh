#!/usr/bin/env bash
# ArcKit — one-line installer
#
#   Linux / macOS:
#     curl -fsSL https://raw.githubusercontent.com/terrygzhou/arc-kit/main/install.sh | bash
#   Windows (PowerShell):
#     irm https://raw.githubusercontent.com/terrygzhou/arc-kit/main/install.ps1 | iex
#
# What this does:
#   1. Detects your AI coding assistants (Claude Code, Codex, OpenCode,
#      GitHub Copilot, Kimi Code, Mistral Vibe, Paperclip).
#   2. Installs the ArcKit CLI (Python) — needed for the Codex / OpenCode /
#      Copilot CLI scaffolders (`arckit init`). Skipped when no CLI-based
#      assistant is present.
#   3. Prints the exact next command for every assistant you have.
#
# No other installers can do all three in one shot: the native plugins
# (Claude / Codex / Kimi / Vibe / Paperclip) are installed by their host
# tools, and only the CLI-based assistants need the Python package.
#
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
NC='\033[0;39m'
log()  { printf "${GREEN}✓${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}⚠${NC} %s\n" "$*" >&2; }
die()  { printf "${RED}✗${NC} %s\n" "$*" >&2; exit 1; }

REPO="terrygzhou/arc-kit"
CLI_PKG="arckit-cli"

# ── 1. Detect AI coding assistants ───────────────────────────────────────
has() { command -v "$1" >/dev/null 2>&1; }
declare -a DETECTED=()

has claude && DETECTED+=("claude")
has codex && DETECTED+=("codex")
has opencode && DETECTED+=("opencode")
has kimi-code && DETECTED+=("kimi")
has vibe && DETECTED+=("vibe")

# GitHub Copilot: detect the VS Code binary; Copilot is a VS Code feature
if has code || has code-insiders; then
  DETECTED+=("copilot")
fi

# Paperclip: npm global install
if has paperclip; then
  DETECTED+=("paperclip")
fi

if [[ ${#DETECTED[@]} -eq 0 ]]; then
  warn "No known AI coding assistant found on PATH."
  echo "      Detected by name: claude, codex, opencode, kimi-code, vibe, code."
  echo "      Install your favourite first (e.g. 'npm i -g @anthropic-ai/claude-code'),"
  echo "      then re-run this installer."
  echo
fi

# ── 2. Install the ArcKit CLI (only when a CLI-based assistant needs it) ──
needs_cli=0
for d in "${DETECTED[@]:-}"; do
  case "$d" in codex|opencode|copilot) needs_cli=1 ;; esac
done

if [[ "$needs_cli" -eq 1 ]]; then
  # Prerequisites for the Python install
  has python3 || die "python3 is required (install it, then re-run)"
  PY_OK=$(python3 -c 'import sys; print(sys.version_info >= (3, 11))' 2>/dev/null || echo "False")
  [[ "$PY_OK" == "True" ]] || die "Python ≥ 3.11 required (got $(python3 --version 2>&1))"

  if has uv; then
    log "Installing ArcKit CLI via uv (recommended)"
    uv tool install "${CLI_PKG}@git+https://github.com/${REPO}.git"

  elif has pipx; then
    log "Installing ArcKit CLI via pipx"
    pipx install "${CLI_PKG}@git+https://github.com/${REPO}.git"

  else
    # Try to bootstrap uv from PyPI when pip is importable
    if python3 -c 'import pip' >/dev/null 2>&1; then
      log "Bootstrapping uv from PyPI, then installing ArcKit CLI"
      python3 -m pip install --user --break-system-packages uv >/dev/null
      export PATH="${HOME}/.local/bin:${PATH}"
      uv tool install "${CLI_PKG}@git+https://github.com/${REPO}.git"
    else
      warn "No uv or pipx found — installing uv into the user site, then ArcKit CLI"
      pip install --user --break-system-packages uv
      export PATH="${HOME}/.local/bin:${PATH}"
      uv tool install "${CLI_PKG}@git+https://github.com/${REPO}.git"
    fi
  fi

  if command -v arckit >/dev/null 2>&1; then
    log "ArcKit CLI installed ✓"
  else
    local_bin="${HOME}/.local/bin"
    if [[ -d "$local_bin" && ":${PATH}:" != *":${local_bin}:"* ]]; then
      warn "Adding ~/.local/bin to PATH (persist: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc)"
      export PATH="${local_bin}:${PATH}"
    fi
    command -v arckit >/dev/null 2>&1 || die "'arckit' not found on PATH. Re-source your shell or add ~/.local/bin to PATH."
  fi
else
  log "No CLI-based assistant (Codex/OpenCode/Copilot) detected — skipping the Python CLI install."
fi

# ── 3. Per-platform next steps ────────────────────────────────────────────
echo
printf "${CYAN}Next steps for the assistants we found:${NC}\n\n"

print_next() { # $1 = label, rest = command lines
  local label="$1"; shift
  printf "  ${CYAN}%-22s${NC} %s\n" "$label" "$1"
  shift || true
  for line in "$@"; do printf "  %-23s %s\n" "" "$line"; done
}

have() { case " ${DETECTED[*]:-} " in *" $1 "*) return 0 ;; esac; return 1; }

if have claude; then
  print_next "Claude Code" \
    "claude install latest" \
    "/plugin marketplace add ${REPO}" \
    "claude plugin install arckit@arc-kit"
fi
if have codex; then
  print_next "Codex CLI" \
    "codex plugin marketplace add terrygzhou/arckit-codex" \
    "codex features enable hooks && codex features enable plugin_hooks" \
    "# or scaffold a project: arckit init my-project --ai codex"
fi
if have opencode; then
  print_next "OpenCode CLI" \
    "arckit init my-project --ai opencode   # installs .opencode/ skills"
fi
if have copilot; then
  print_next "GitHub Copilot" \
    "arckit init my-project --ai copilot   # installs .github/prompts"
fi
if have kimi; then
  print_next "Kimi Code CLI" \
    "inside the TUI: /plugins install https://github.com/terrygzhou/arckit-kimi.git"
fi
if have vibe; then
  print_next "Mistral Vibe" \
    "git clone https://github.com/terrygzhou/arckit-vibe ~/.vibe/extensions/arckit-vibe" \
    "# or symlink a checked-out copy into ~/.vibe/extensions/"
fi
if have paperclip; then
  print_next "Paperclip" \
    "npm i terrygzhou/arckit-paperclip   # via Paperclip's plugin flow"
fi

if [[ ${#DETECTED[@]} -eq 0 ]]; then
  printf "  ${YELLOW}Nothing detected — nothing else to do.${NC}\n"
  printf "  Re-run this installer after installing your assistant.\n"
fi
