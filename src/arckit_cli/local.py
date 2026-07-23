"""
ArcKit Local LLM Setup

Guided setup for running ArcKit against a local LLM. Supports:
- Ollama (default, cross-platform)
- SGLang / Docker (advanced)

Commands:
    arckit local setup      # Interactive setup wizard
    arckit local status     # Connection + config status
    arckit local models     # Available models by VRAM tier
    arckit local test       # Health-check configured LLM
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx
import platformdirs
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from arckit_cli import console as arckit_console

console = Console()


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _get_config_path() -> Path:
    return Path(platformdirs.user_config_dir("arckit")) / "config.yaml"


def _load_config() -> dict:
    path = _get_config_path()
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def _save_config(cfg: dict) -> Path:
    path = _get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(cfg, default_flow_style=False))
    return path


# ---------------------------------------------------------------------------
# Model catalogue
# ---------------------------------------------------------------------------

@dataclass
class ModelEntry:
    """A model available through Ollama or SGLang."""
    name: str                  # Display name
    ollama_tag: str          # e.g. "qwen2.5:72b" — empty if not on Ollama
    sglang_name: str         # HuggingFace path or model name for SGLang
    params: str              # e.g. "7B", "32B"
    vram_min_gb: int        # Minimum VRAM recommended
    download_size_gb: int   # Approximate download size
    description: str
    backend: str = "ollama"  # Default backend
    backends: list[str] = field(default_factory=list)


MODELS: list[ModelEntry] = [
    # ── Lightweight (CPU / low VRAM) ──
    ModelEntry(
        name="Qwen 2.5 7B",
        ollama_tag="qwen2.5:7b",
        sglang_name="Qwen/Qwen2.5-7B-Instruct-AWQ",
        params="7B",
        vram_min_gb=8,
        download_size_gb=5,
        description="Fast, runs on CPU. Good for quick tasks.",
        backends=["ollama"],
    ),
    ModelEntry(
        name="Llama 3.3 8B",
        ollama_tag="llama3.3:8b",
        sglang_name="meta-llama/Llama-3.3-8B-Instruct",
        params="8B",
        vram_min_gb=8,
        download_size_gb=5,
        description="Meta's latest 8B. Good code and instruction following.",
        backends=["ollama"],
    ),
    # ── Balanced (good quality, consumer GPUs) ──
    ModelEntry(
        name="Phi 4 14B",
        ollama_tag="phi4:14b",
        sglang_name="microsoft/Phi-4",
        params="14B",
        vram_min_gb=16,
        download_size_gb=9,
        description="Microsoft's efficient model. Strong reasoning for size.",
        backends=["ollama"],
    ),
    ModelEntry(
        name="Qwen 2.5 14B",
        ollama_tag="qwen2.5:14b",
        sglang_name="Qwen/Qwen2.5-14B-Instruct-AWQ",
        params="14B",
        vram_min_gb=16,
        download_size_gb=12,
        description="Strong general-purpose model. Good for architecture analysis.",
        backends=["ollama"],
    ),
    ModelEntry(
        name="Qwen 2.5 32B",
        ollama_tag="qwen2.5:32b",
        sglang_name="Qwen/Qwen2.5-32B-Instruct-AWQ",
        params="32B",
        vram_min_gb=24,
        download_size_gb=20,
        description="High-quality reasoning. Sweet spot for RTX 4090/5090.",
        backends=["ollama", "sglang"],
    ),
    ModelEntry(
        name="Qwen3 32B",
        ollama_tag="qwen3:32b",
        sglang_name="Qwen/Qwen3-32B",
        params="32B",
        vram_min_gb=20,
        download_size_gb=18,
        description="Latest Qwen generation. Best reasoning-to-size ratio.",
        backends=["ollama", "sglang"],
    ),
    ModelEntry(
        name="Qwen3.6 27B NVFP4",
        ollama_tag="",
        sglang_name="Qwen/Qwen3.6-27B-NVFP4",
        params="27B",
        vram_min_gb=24,
        download_size_gb=16,
        description="NVFP4 quantised. Requires SGLang for optimal throughput.",
        backend="sglang",
        backends=["sglang"],
    ),
    # ── Heavy (workstation / server) ──
    ModelEntry(
        name="Qwen 2.5 72B",
        ollama_tag="qwen2.5:72b",
        sglang_name="Qwen/Qwen2.5-72B-Instruct-AWQ",
        params="72B",
        vram_min_gb=48,
        download_size_gb=48,
        description="Top-tier quality. Needs A100/A6000 or dual GPUs.",
        backends=["ollama", "sglang"],
    ),
    ModelEntry(
        name="Llama 3.3 70B",
        ollama_tag="llama3.3:70b",
        sglang_name="meta-llama/Llama-3.3-70B-Instruct",
        params="70B",
        vram_min_gb=48,
        download_size_gb=45,
        description="Meta flagship. Best instruction following available locally.",
        backends=["ollama", "sglang"],
    ),
]


# ---------------------------------------------------------------------------
# System detection
# ---------------------------------------------------------------------------

def _get_system_info() -> dict:
    """Detect system GPU and available VRAM."""
    info: dict = {
        "os": platform.system(),
        "os_release": platform.release(),
        "arch": platform.machine(),
        "gpu": None,
        "vram_gb": 0,
        "cpu_cores": 0,
        "docker_available": False,
        "ollama_available": False,
    }

    # CPU cores
    try:
        info["cpu_cores"] = (
            len(os.sched_getaffinity(0))
            if hasattr(os, "sched_getaffinity")
            else os.cpu_count() or 1
        )
    except Exception:
        info["cpu_cores"] = 1

    # NVIDIA GPU
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            line = result.stdout.strip().split("\n")[0]
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                info["gpu"] = parts[0]
                try:
                    vram_str = parts[1].replace(" MiB", "").strip()
                    info["vram_gb"] = round(int(vram_str) / 1024)
                except ValueError:
                    pass
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Metal (Apple Silicon)
    if info["os"] == "Darwin" and info["gpu"] is None:
        info["gpu"] = "Apple Silicon"
        info["vram_gb"] = 0  # Unknown without sysctl

    # Docker
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        info["docker_available"] = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Ollama
    try:
        import shutil
        info["ollama_available"] = shutil.which("ollama") is not None
    except Exception:
        pass

    return info


# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------

def _is_ollama_running(port: int = 11434) -> bool:
    """Check if Ollama is running and accessible."""
    try:
        resp = httpx.get(f"http://127.0.0.1:{port}/api/tags", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def _ollama_list_models() -> list[dict]:
    """List models available in Ollama."""
    try:
        resp = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("models", [])
    except Exception:
        pass
    return []


def _ollama_pull(tag: str) -> bool:
    """Pull a model via `ollama pull`. Returns True on success."""
    try:
        console.print(f"\n[cyan]Pulling model: {tag}[/cyan]")
        console.print(f"[dim]This may take a while depending on download speed...[/dim]\n")

        proc = subprocess.Popen(
            ["ollama", "pull", tag],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )

        last_progress: str = ""
        for line in proc.stdout:
            text = line.decode(errors="replace").strip()
            if text:
                # Ollama output: 100%, 75%, downloading...
                if "complete" in text or "success" in text or "%" in text:
                    if text != last_progress:
                        console.print(f"[green]{text}[/green]")
                        last_progress = text

        proc.wait()
        return proc.returncode == 0
    except FileNotFoundError:
        console.print("[red]Error:[/red] ollama command not found")
        return False


def _ollama_run(model_tag: str) -> bool:
    """Run a quick test against the model. Returns True if responsive."""
    try:
        url = "http://127.0.0.1:11434/v1/chat/completions"
        resp = httpx.post(
            url,
            json={
                "model": model_tag,
                "messages": [{"role": "user", "content": "Respond with 'OK' only."}],
                "max_tokens": 10,
                "temperature": 0,
            },
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return "ok" in content.lower()
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Install helpers
# ---------------------------------------------------------------------------

def _install_ollama() -> bool:
    """Install Ollama via the official installer script."""
    os_name = platform.system()

    if os_name == "Linux":
        try:
            console.print("[cyan]Installing Ollama via official installer...[/cyan]")
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                console.print("[green]✓[/green] Ollama installed")
                return True
            else:
                console.print(f"[red]Install failed: {result.stderr[:200]}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]Install error: {e}[/red]")
            return False

    elif os_name == "Darwin":
        # Check if Homebrew is available
        try:
            brew_available = subprocess.run(
                ["brew", "--version"],
                capture_output=True,
                timeout=5,
            ).returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            brew_available = False

        if brew_available:
            console.print("[cyan]Installing Ollama via Homebrew...[/cyan]")
            result = subprocess.run(
                ["brew", "install", "ollama"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                console.print("[green]✓[/green] Ollama installed via Homebrew")
                return True

        # Fallback: instruct manual install
        console.print(
            "[yellow]Homebrew not available. Install Ollama from:[/yellow]\n"
            "  https://ollama.com/download/mac"
        )
        return False

    elif os_name == "Windows":
        console.print(
            "[yellow]Manual install required on Windows:[/yellow]\n"
            "  1. Download: https://ollama.com/download/windows\n"
            "  2. Run the installer\n"
            "  3. Re-run: arckit local setup\n"
        )
        return False

    return False


def _start_ollama_service() -> bool:
    """Start Ollama as a background service/user process."""
    os_name = platform.system()

    if os_name == "Darwin":
        # Launchctl user service
        try:
            result = subprocess.run(
                ["launchctl", "list", "com.ollama.ollama"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                console.print("[green]✓[/green] Ollama service already running")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass

        console.print("[cyan]Starting Ollama as a background service...[/cyan]")
        # Ollama installs a .plist; start it
        subprocess.Popen(["launchctl", "kick", "com.ollama.ollama"])
        return True

    if os_name == "Linux":
        # Check systemd user service
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "ollama"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                console.print("[green]✓[/green] Ollama systemd service active")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass

        # Try starting manually — user runs `ollama serve` in background
        console.print("[cyan]Starting Ollama server...[/cyan]")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True

    return False


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

def _recommend_models(system_info: dict) -> list[ModelEntry]:
    """Return models sorted by suitability for this system."""
    vram = system_info.get("vram_gb", 0)
    has_docker = system_info.get("docker_available", False)
    has_ollama = system_info.get("ollama_available", False)

    scored: list[tuple[float, ModelEntry]] = []
    for m in MODELS:
        # Score: prefer models that fit in VRAM, penalise oversize
        if vram > 0:
            if m.vram_min_gb <= vram:
                score = 10 - abs(m.vram_min_gb - vram)  # Closer = better
            else:
                score = -100  # Won't fit
        else:
            # CPU-only or unknown: prefer smaller models
            score = max(0, 10 - m.vram_min_gb)

        # Bonus if backend is available
        if m.backend == "ollama" and has_ollama:
            score += 5
        if "sglang" in m.backends and has_docker:
            score += 3

        scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]


# ---------------------------------------------------------------------------
# Typer app
# ---------------------------------------------------------------------------

local_app = typer.Typer(
    name="local",
    help="Set up and manage local LLM backends",
    add_completion=False,
)


@local_app.command()
def setup(
    backend: str = typer.Option("ollama", "--backend", help="Backend: ollama (default), sglang"),
    model: Optional[str] = typer.Option(None, "--model", help="Pre-select a model tag (Ollama tag)"),
    skip_install: bool = typer.Option(False, "--skip-install", help="Skip Ollama install if not detected"),
):
    """Interactive setup wizard for running ArcKit with a local LLM."""

    console.print(Panel(
        "[bold]ArcKit Local Setup[/bold]\n\n"
        "This wizard will:\n"
        "  1. Install a local LLM backend\n"
        "  2. Pull an AI model suited to your hardware\n"
        "  3. Configure ArcKit to use it\n\n"
        "Supported backends: Ollama (default), SGLang (Docker)\n"
        "Config stored at: ~/.config/arckit/config.yaml",
        title="🚀 Local Setup",
        border_style="bright_blue",
    ))

    # ── System detection ──
    system_info = _get_system_info()
    gpu = system_info.get("gpu", "Unknown") or "Unknown"
    vram = system_info.get("vram_gb", 0)

    console.print(f"\n[dim]System:[/dim] {system_info['os']} {system_info['arch']}")
    if vram:
        console.print(f"[dim]GPU:[/dim] {gpu} ({vram} GB VRAM)")
    else:
        console.print(f"[dim]GPU:[/dim] {gpu} (CPU mode)")
    console.print(f"[dim]CPU cores:[/dim] {system_info['cpu_cores']}")
    console.print(f"[dim]Docker:[/dim] {'✓' if system_info['docker_available'] else '✗'}")
    console.print(f"[dim]Ollama:[/dim] {'✓' if system_info['ollama_available'] else '✗'}")

    # ── Backend selection ──
    if backend == "sglang" and not system_info["docker_available"]:
        console.print("[red]Docker is not available — falling back to Ollama.[/red]")
        backend = "ollama"

    # ── Ollama setup ──
    if backend == "ollama":
        if not system_info["ollama_available"]:
            console.print("\n[yellow]Ollama not detected. Installing...[/yellow]")
            if not _install_ollama():
                if not skip_install:
                    console.print(
                        "[red]Failed to install Ollama automatically.[/red]\n"
                        "Install manually: https://ollama.com/download\n"
                        "Then re-run: arckit local setup"
                    )
                    raise typer.Exit(1)
                else:
                    console.print("[yellow]Skipping install (--skip-install).[/yellow]")
                    raise typer.Exit(1)

        # Check if running, start if not
        if not _is_ollama_running():
            console.print("[cyan]Starting Ollama server...[/cyan]")
            _start_ollama_service()
            # Wait for it to come up
            for _ in range(10):
                if _is_ollama_running():
                    break
                time.sleep(1)
            else:
                console.print("[yellow]Ollama did not respond — starting manually...[/yellow]")
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                time.sleep(3)

        if not _is_ollama_running():
            console.print("[red]Ollama is not running. Start it manually and re-run.[/red]")
            raise typer.Exit(1)

    # ── Model selection ──
    recommended = _recommend_models(system_info)
    top_recs = recommended[:6]  # Show top 6

    selected: ModelEntry | None = None

    if model:
        # User pre-selected — find matching entry
        for m in MODELS:
            if model == m.ollama_tag or model == m.name:
                selected = m
                break
        if not selected:
            console.print(f"[yellow]Model '{model}' not in catalogue, will still try to pull it.[/yellow]")
            # Create a synthetic entry
            selected = ModelEntry(
                name=model,
                ollama_tag=model,
                sglang_name=model,
                params="?",
                vram_min_gb=0,
                download_size_gb=0,
                description="User-specified model",
                backends=["ollama"],
            )

    if not selected:
        console.print("\n[cyan]Recommended models for your system:[/cyan]\n")
        table = Table(show_header=True, header_style="bold")
        table.add_column("#", style="dim")
        table.add_column("Model", style="green")
        table.add_column("Params", style="cyan")
        table.add_column("VRAM", style="yellow")
        table.add_column("Size", style="yellow")
        table.add_column("Description")

        for i, m in enumerate(top_recs, 1):
            fit = "✓" if m.vram_min_gb <= vram or vram == 0 else "⚠"
            table.add_row(
                str(i),
                m.name,
                m.params,
                f"{m.vram_min_gb} GB {fit}",
                f"{m.download_size_gb} GB",
                m.description[:50],
            )

        console.print(table)
        console.print("\n[dim]These models fit your hardware. #1 is recommended.[/dim]")

        choice = typer.prompt(
            "Select model (number)",
            type=int,
            default=1,
        )
        if 1 <= choice <= len(top_recs):
            selected = top_recs[choice - 1]
        else:
            selected = top_recs[0]

    # Safety: selected should always be set at this point
    if selected is None:
        selected = recommended[0] if recommended else MODELS[0]

    console.print(f"\n[cyan]Selected:[/cyan] [bold]{selected.name}[/bold] ({selected.params})")
    console.print(f"[dim]Description: {selected.description}[/dim]")

    # ── Pull model ──
    tag: str = selected.ollama_tag

    if backend == "ollama":
        if not tag:
            # Model not available on Ollama — suggest alternative
            console.print(
                f"[yellow]{selected.name} is not available via Ollama.\n"
                f"Switching to closest Ollama alternative...[/yellow]"
            )
            fallback = next(
                (m for m in recommended if m.ollama_tag),
                MODELS[0],
            )
            tag = fallback.ollama_tag
            selected = fallback
            console.print(f"[cyan]Using: {fallback.name} ({tag})[/cyan]")

        existing = _ollama_list_models()
        existing_names = {m.get("name", "") for m in existing}

        # Check if already pulled
        if tag in existing_names or any(tag.split(":")[0] in name for name in existing_names):
            console.print(f"[green]✓[/green] Model '{tag}' already available")
        else:
            ok = _ollama_pull(tag)
            if not ok:
                console.print("[red]Model download failed. Check connection and retry.[/red]")
                raise typer.Exit(1)

    # ── Configure ArcKit ──
    cfg = _load_config()
    if backend == "ollama":
        cfg["llm"] = {
            "provider": "openai-compatible",
            "base_url": "http://127.0.0.1:11434",
            "model": selected.ollama_tag if selected else "qwen2.5:14b",
            "api_key": "",
            "max_tokens": 128000,
            "temperature": 0.0,
        }
    else:
        cfg["llm"] = {
            "provider": "openai-compatible",
            "base_url": "http://127.0.0.1:8000",
            "model": selected.sglang_name if selected else "Qwen2.5-7B",
            "api_key": "",
            "max_tokens": 128000,
            "temperature": 0.0,
        }

    config_path = _save_config(cfg)
    console.print(f"\n[green]✓[/green] Configured ArcKit → {config_path}")
    console.print(f"  Model: {cfg['llm']['model']}")
    console.print(f"  Endpoint: {cfg['llm']['base_url']}")

    # ── Quick test ──
    model_tag = cfg["llm"]["model"]
    base_url = cfg["llm"]["base_url"]
    console.print(f"\n[cyan]Testing connection to {model_tag}...[/cyan]")

    try:
        resp = httpx.post(
            f"{base_url}/v1/chat/completions",
            json={
                "model": model_tag,
                "messages": [{"role": "user", "content": "Respond with 'OK' only."}],
                "max_tokens": 10,
            },
            timeout=60,
        )
        if resp.status_code == 200:
            content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if "ok" in content.lower():
                console.print("[bold green]✓ Local LLM is ready![/bold green]")
            else:
                console.print(f"[yellow]Response: {content.strip()}[/yellow]")
        else:
            console.print(f"[yellow]Endpoint returned {resp.status_code} — model may still be loading[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Test skipped — {e}[/yellow]")

    console.print(f"\n[dim]Next steps:[/dim]")
    console.print(f"  arckit init my-project --ai opencode")
    console.print(f"  cd my-project && arckit build --recipe strategy")


@local_app.command()
def status():
    """Show local LLM status and configuration."""

    cfg = _load_config()
    llm = cfg.get("llm", {})
    base_url = llm.get("base_url", "—")
    model = llm.get("model", "—")
    provider = llm.get("provider", "—")

    system_info = _get_system_info()
    gpu = system_info.get("gpu", "Unknown") or "Unknown"
    vram = system_info.get("vram_gb", 0)

    # Check connectivity
    connected = False
    latency_ms = "—"
    if base_url != "—" and model != "—":
        try:
            t0 = time.time()
            resp = httpx.post(
                f"{base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "OK"}],
                    "max_tokens": 1,
                },
                timeout=15,
            )
            latency_ms = f"{int((time.time() - t0) * 1000)}ms"
            connected = resp.status_code == 200
        except Exception:
            pass

    # Ollama status
    ollama_running = _is_ollama_running()

    table = Table(title="Local LLM Status")
    table.add_column("Item", style="cyan")
    table.add_column("Status")

    table.add_row("System", f"{system_info['os']} {system_info['arch']}")
    if vram:
        table.add_row("GPU", f"{gpu} ({vram} GB)")
    else:
        table.add_row("GPU", f"{gpu} (CPU)")
    table.add_row("Ollama", "✓ running" if ollama_running else "✗ not running")
    table.add_row("Docker", "✓" if system_info["docker_available"] else "✗")
    table.add_row("Config", str(_get_config_path()))
    table.add_row("Provider", str(provider))
    table.add_row("Endpoint", str(base_url))
    table.add_row("Model", str(model))
    table.add_row("Connected", "✓" if connected else "✗")
    if connected:
        table.add_row("Latency", str(latency_ms))

    console.print(table)


@local_app.command()
def models(
    backend: str = typer.Option("all", "--backend", help="Filter: ollama, sglang, all"),
    fit: bool = typer.Option(False, "--fit", help="Only show models that fit in available VRAM"),
):
    """List available models and their requirements."""

    system_info = _get_system_info()
    vram = system_info.get("vram_gb", 0)

    console.print(Panel(
        f"GPU: {system_info.get('gpu', 'Unknown') or 'Unknown'} ({vram} GB VRAM)" if vram
        else f"GPU: {system_info.get('gpu', 'Unknown') or 'Unknown'} (CPU mode)",
        title="Hardware",
    ))

    filtered = MODELS
    if backend == "ollama":
        filtered = [m for m in MODELS if "ollama" in m.backends]
    elif backend == "sglang":
        filtered = [m for m in MODELS if "sglang" in m.backends]

    if fit and vram > 0:
        filtered = [m for m in filtered if m.vram_min_gb <= vram]

    table = Table(title="Available Models")
    table.add_column("Model", style="green")
    table.add_column("Params", style="cyan")
    table.add_column("Backend", style="magenta")
    table.add_column("VRAM", style="yellow")
    table.add_column("Size", style="yellow")
    table.add_column("Description")

    for m in sorted(filtered, key=lambda m: m.vram_min_gb):
        fit_marker = "✓" if (m.vram_min_gb <= vram or vram == 0) else "⚠"
        table.add_row(
            m.name,
            m.params,
            ", ".join(m.backends) or m.backend,
            f"{m.vram_min_gb} GB {fit_marker}",
            f"{m.download_size_gb} GB",
            m.description,
        )

    console.print(table)


@local_app.command()
def test(
    model: Optional[str] = typer.Option(None, "--model", help="Override model from config"),
):
    """Health-check the configured local LLM."""

    cfg = _load_config()
    llm = cfg.get("llm", {})
    test_model = model or llm.get("model")
    base_url = llm.get("base_url", "http://127.0.0.1:11434")

    if not test_model:
        console.print("[red]No LLM configured. Run: arckit local setup[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Testing: {test_model} @ {base_url}[/cyan]")

    # Basic connectivity
    try:
        t0 = time.time()
        resp = httpx.post(
            f"{base_url}/v1/chat/completions",
            json={
                "model": test_model,
                "messages": [{"role": "user", "content": "Say 'hello world'."}],
                "max_tokens": 20,
            },
            timeout=120,
        )
        elapsed = time.time() - t0
        status = resp.status_code

        console.print(f"\n  Endpoint:  {base_url}")
        console.print(f"  Model:     {test_model}")
        console.print(f"  Status:    {'✓ OK' if status == 200 else f'✗ {status}'}")
        console.print(f"  Latency:   {elapsed*1000:.0f}ms")

        if status == 200:
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            console.print(f"  Response:  {content.strip()[:200]}")

            usage = data.get("usage", {})
            inp = usage.get("prompt_tokens", "—")
            out = usage.get("completion_tokens", "—")
            console.print(f"  Tokens:    {inp} in / {out} out")
            console.print(f"\n[bold green]✓ LLM is healthy[/bold green]")
        else:
            body = resp.text[:300]
            console.print(f"  Error body: {body}")
            console.print(f"\n[bold red]✗ LLM returned {status}[/bold red]")
    except httpx.ConnectError:
        console.print(f"[red]✗ Cannot connect to {base_url}[/red]")
        console.print("  Is the LLM server running?")
        raise typer.Exit(1)
    except httpx.TimeoutException:
        console.print(f"[yellow]Timeout connecting to {base_url}[/yellow]")
        console.print("  The model may still be loading. Wait and retry.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)