<#
ArcKit cross-platform installer (Windows PowerShell).

One-liner (Windows PowerShell 5+):
    irm https://raw.githubusercontent.com/terrygzhou/arc-kit/main/install.ps1 | iex

What this script does:
  1. Detect which AI assistants are on this machine by looking for their CLIs
     on PATH: claude, codex, opencode, kimi-code, vibe, code (Copilot CLI
     host), paperclip.
  2. Install the ArcKit CLI (Python) only when a CLI-based assistant
     (codex / opencode / copilot) is present - those are the assistants that
     scaffold projects with "arckit init".
  3. Print per-assistant next-step commands.

The Python CLI install chain tries uv first, then pipx, then a plain pip
fallback, installing arckit-cli from the git source:
    git+https://github.com/terrygzhou/arc-kit.git

For the macOS / Linux / WSL equivalent one-liner, see install.sh.
#>

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

function Write-Log {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Die {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Has-Command {
    param([string]$Name)
    return ((Get-Command $Name -ErrorAction SilentlyContinue) -ne $null)
}

# ---------------------------------------------------------------------------
# 1. Detect installed AI assistants
# ---------------------------------------------------------------------------

Write-Log "Detecting installed AI assistants..."
$Detected = @()

if (Has-Command "claude")      { $Detected += "claude"      }
if (Has-Command "codex")       { $Detected += "codex"       }
if (Has-Command "opencode")    { $Detected += "opencode"    }
if (Has-Command "kimi-code")   { $Detected += "kimi"        }
if (Has-Command "vibe")        { $Detected += "vibe"        }

# GitHub Copilot: detected via the VS Code / VS Code Insiders CLI host,
# since the Copilot extension is a VS Code feature, not a standalone CLI.
if ((Has-Command "code") -or (Has-Command "code-insiders")) { $Detected += "copilot" }

if (Has-Command "paperclip")   { $Detected += "paperclip"   }

$needsCli = $false
if ($Detected -contains "codex" -or $Detected -contains "opencode" -or $Detected -contains "copilot") {
    $needsCli = $true
}

# ---------------------------------------------------------------------------
# 2. Install the ArcKit CLI (Python) - only when a CLI-based assistant exists
# ---------------------------------------------------------------------------

if ($needsCli) {
    Write-Log "CLI-based assistant detected - installing ArcKit CLI..."

    # Python prerequisite
    if (-not (Has-Command "python")) {
        Write-Die "Python is required but was not found. Install Python 3.11+ from https://www.python.org/downloads/"
    }

    $spec = "arckit-cli@git+https://github.com/terrygzhou/arc-kit.git"

    $installed = $false
    if (Has-Command "uv") {
        Write-Log "Installing ArcKit CLI via uv (recommended)"
        & uv tool install $spec
        if ($LASTEXITCODE -eq 0) { $installed = $true }
    }

    if (-not $installed -and (Has-Command "pipx")) {
        Write-Log "Installing ArcKit CLI via pipx"
        & pipx install $spec
        if ($LASTEXITCODE -eq 0) { $installed = $true }
    }

    if (-not $installed) {
        Write-Log "Installing ArcKit CLI via pip (user site)"
        & python -m pip install --user $spec
        if ($LASTEXITCODE -ne 0) {
            Write-Die "Could not install the ArcKit CLI. Install uv or pipx, or run: python -m pip install $spec"
        }
    }

    Write-Log "ArcKit CLI installed"

    # Make sure the user site bin is on PATH so "arckit" is callable
    $userBin = [System.IO.Path]::Combine($env:USERPROFILE, ".local", "bin")
    if (Test-Path $userBin) {
        $userBinInPath = $false
        foreach ($p in ($env:PATH -split [System.IO.Path]::PathSeparator)) {
            if ($p -eq $userBin) { $userBinInPath = $true; break }
        }
        if (-not $userBinInPath) {
            $env:PATH = "$userBin;" + $env:PATH
            Write-Warn "Added $userBin to PATH for this session (persist: add it to your user PATH in the System Environment Variables dialog)"
        }
    }

    # Verify
    if (-not (Has-Command "arckit")) {
        Write-Die "ArcKit CLI installed but 'arckit' was not found on PATH. Open a new PowerShell session and try again."
    }
}
else {
    Write-Warn "No CLI-based assistant (codex / opencode / copilot) detected - skipping Python CLI install."
}

# ---------------------------------------------------------------------------
# 3. Per-assistant next steps
# ---------------------------------------------------------------------------

if ($Detected.Count -eq 0) {
    Write-Warn "No supported AI assistant detected on this machine."
    Write-Warn "Install one of: Claude Code, Codex CLI, OpenCode CLI, GitHub Copilot, Kimi Code, Mistral Vibe, or Paperclip."
    Write-Warn "The ArcKit extensions are still available via their native channels (see below)."
}

function Print-Next {
    param([string]$Assistant, [string[]]$Lines)
    $indent = " "
    $width = 20
    $label = $Assistant.PadRight($width)
    Write-Host ""
    Write-Host "$indent$label" -NoNewline -ForegroundColor Cyan
    Write-Host $Lines[0]
    for ($i = 1; $i -lt $Lines.Count; $i++) {
        Write-Host (" " * ($width + 1)) + $Lines[$i]
    }
}

if ($Detected.Count -gt 0) {
    Write-Host ""
    Write-Host "Next steps for the assistants we found:" -ForegroundColor Cyan
}

if ($Detected -contains "claude") {
    Print-Next "Claude Code" @(
        "claude install latest"
        "/plugin marketplace add terrygzhou/arc-kit"
        "claude plugin install arckit@arc-kit")
}
if ($Detected -contains "codex") {
    Print-Next "Codex CLI" @(
        "codex plugin marketplace add terrygzhou/arckit-codex"
        "codex features enable hooks && codex features enable plugin_hooks"
        "# or scaffold a project: arckit init my-project --ai codex")
}
if ($Detected -contains "opencode") {
    Print-Next "OpenCode CLI" @(
        "arckit init my-project --ai opencode   # installs .opencode/ skills")
}
if ($Detected -contains "copilot") {
    Print-Next "GitHub Copilot" @(
        "arckit init my-project --ai copilot   # installs .github/prompts")
}
if ($Detected -contains "kimi") {
    Print-Next "Kimi Code" @(
        "Inside the Kimi Code TUI, run:"
        "/plugins install https://github.com/terrygzhou/arckit-kimi.git")
}
if ($Detected -contains "vibe") {
    Print-Next "Mistral Vibe" @(
        "Copy or symlink the extension into the Vibe extensions dir, e.g.:"
        "Copy-Item -Recurse .\<cloned repo>\extensions\arckit-vibe $env:USERPROFILE\.vibe\extensions\")
}
if ($Detected -contains "paperclip") {
    Print-Next "Paperclip" @(
        "npm i -g terrygzhou/arckit-paperclip")
}

# ---------------------------------------------------------------------------
# 4. Footer
# ---------------------------------------------------------------------------

Write-Host ""
if ($Detected.Count -eq 0) {
    Write-Warn "Nothing else to do - no assistants detected and no CLI install was required."
}
else {
    Write-Log "Done. Restart your assistant and start an ArcKit session."
}
