"""
Post-Build Diagram Consolidation

Sweeps project markdown docs for inline PlantUML blocks (ArchiMate views
are delivered inline per the ``archimate-svg-delivery`` policy: source in
a ```plantuml fence, rendered self-contained ``.svg`` as the only new
file) and materialises them as ``.puml`` sidecars plus ``.svg`` renders
under each project folder's ``diagrams/`` directory.

This is the post-build sweep for views whose generation step deferred
SVG delivery (e.g. the pinned PlantUML jar was unavailable at
generation time, leaving the inline source with a pending/TBD SVG) —
previously those required manual extraction + rendering (EYW-348
defect f).

Graceful degradation mirrors the generation-time policy: when the
pinned jar (or Java) is unavailable the ``.puml`` source is still
written and the SVG is recorded as ``pending`` in the manifest, so a
later run (with the jar present) completes the render.

Manifest: ``projects/<proj>/diagrams/manifest.json`` records one entry
per source block (puml/svg paths, source SHA-256, status), making
re-runs idempotent.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Inline fence: ```plantuml ... ``` (ArchiMate blocks carry @startuml/@enduml)
_PLANTUML_BLOCK_RE = re.compile(r"```plantuml\s*\n(.*?)```", re.DOTALL)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
_EXTERNAL_URL_RE = re.compile(r"https?://[^\s\"'<>]+")
_W3C_PREFIXES = ("http://www.w3.org/", "https://www.w3.org/")

_RENDER_TIMEOUT_S = 120


def find_plantuml_jar(explicit: str | None = None) -> str | None:
    """Resolve the PlantUML jar to use.

    Search order:
        1. Explicit path (caller-provided, e.g. a CLI override)
        2. ``PLANTUML_JAR`` environment variable
        3. Newest ``plantuml-*.jar`` under ``~/.local/share/arckit/tools``

    Returns the jar path, or None when no candidate exists.
    """
    if explicit:
        p = Path(explicit).expanduser()
        return str(p) if p.is_file() else None
    env = os.environ.get("PLANTUML_JAR")
    if env:
        p = Path(env).expanduser()
        return str(p) if p.is_file() else None
    tools_dir = Path.home() / ".local" / "share" / "arckit" / "tools"
    candidates = sorted(tools_dir.glob("plantuml-*.jar"))
    return str(candidates[-1]) if candidates else None


def _slugify(text: str) -> str:
    """File-safe slug from free text (lowercase, hyphens)."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _nearest_heading(doc_text: str, block_start: int) -> str | None:
    """Return the text of the closest markdown heading above the block."""
    heading = None
    for match in _HEADING_RE.finditer(doc_text):
        if match.end() > block_start:
            break
        heading = match.group(1)
    return heading


def _external_refs(svg_text: str) -> list[str]:
    """Non-W3C external URLs in an SVG (self-containment audit).

    The ArchiMate SVG delivery standard allows only W3C namespace
    declarations; anything else is a self-containment violation.
    """
    refs = set()
    for match in _EXTERNAL_URL_RE.finditer(svg_text):
        url = match.group(0)
        if url.startswith(_W3C_PREFIXES):
            continue
        refs.add(url)
    return sorted(refs)


def _render_puml(puml: Path, jar: str, java: str) -> bool:
    """Render ``puml`` to a sibling ``.svg`` with the pinned jar.

    ``-tsvg`` is mandatory: PlantUML's default output is PNG, so without
    it the ``.svg`` sidecar is never produced and the sweep's success
    check (``svg_path.is_file()``) silently fails, deferring every
    render to a later run (gloryev EYW-345 incident).
    """
    svg = puml.with_suffix(".svg")
    try:
        proc = subprocess.run(
            [java, "-jar", jar, "-tsvg", str(puml)],
            capture_output=True,
            text=True,
            timeout=_RENDER_TIMEOUT_S,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return proc.returncode == 0 and svg.is_file()


def _load_manifest(manifest_path: Path) -> dict:
    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": 1, "blocks": {}}


def consolidate_project_diagrams(
    project_root: Path,
    plantuml_jar: str | None = None,
) -> dict:
    """Sweep ``projects/**/*.md`` for inline PlantUML blocks and
    materialise ``.puml`` + ``.svg`` sidecars under each project's
    ``diagrams/`` folder.

    Args:
        project_root: Root of the arckit project (contains ``projects/``).
        plantuml_jar: Explicit jar path; None → standard search order.

    Returns:
        Summary dict: docs_scanned, blocks_found, puml_written,
        rendered, pending, unchanged, external_refs ({svg: [urls]}).
    """
    summary: dict = {
        "docs_scanned": 0,
        "blocks_found": 0,
        "puml_written": 0,
        "rendered": 0,
        "pending": 0,
        "unchanged": 0,
        "external_refs": {},
        # Linking step (EYW-345): docs_without_blocks counts scanned
        # docs that gained no sidecars (coverage gaps, e.g. ADMP/BPCM/
        # STKE types without ArchiMate views); stale_folders lists
        # project subdirs that hold .md artefacts but zero inline
        # PlantUML blocks (per-phase folders left stale by a clobbered
        # build); orphaned counts sidecars whose source document has
        # been deleted since the last run.
        "docs_without_blocks": 0,
        "stale_folders": [],
        "orphaned": 0,
        # duplicate_sidecars: sidecar names that materialised in more than
        # one diagrams/ folder (canonical + stale per-phase build split).
        # Surfaced so the build summary can disambiguate which generation
        # is canonical instead of leaving two silent duplicates.
        "duplicate_sidecars": {},
    }

    projects_dir = Path(project_root) / "projects"
    if not projects_dir.is_dir():
        return summary

    jar = find_plantuml_jar(plantuml_jar)
    java = shutil.which("java")
    can_render = bool(jar and java)

    # Detect project subdirs (stale per-phase folders, e.g. 001-DATA-bar)
    # that hold artefacts but no inline PlantUML blocks — a sign that an
    # older build with clobbered {P_<ID>} values wrote into them, while
    # the canonical folder is the one the current build actually uses.
    _folders_with_blocks: set[Path] = set()
    _all_project_folders: set[Path] = set()
    for md in projects_dir.rglob("*.md"):
        # Walk up to the first subdir of projects/ that contains this doc.
        folder = md.parent
        while folder != projects_dir and folder.is_dir():
            _all_project_folders.add(folder)
            folder = folder.parent
    # (folders_with_blocks gets populated during the main loop below;
    #  the stale check runs after)

    # Sidecar names materialised per diagrams/ folder, for the cross-folder
    # duplicate report below (heading-derived names are uniform across the
    # demanded template sections, so canonical + stale builds collide).
    _sidecar_names: dict[str, list[str]] = {}

    for doc in sorted(projects_dir.rglob("*.md")):
        try:
            doc_text = doc.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        blocks = list(_PLANTUML_BLOCK_RE.finditer(doc_text))
        if not blocks:
            # Track docs without inline PlantUML blocks for the coverage
            # report — the build summary can surface types that never
            # got a diagram (e.g. ADMP/BPCM/STKE in the gloryev incident).
            summary["docs_without_blocks"] += 1
            continue
        summary["docs_scanned"] += 1
        summary["blocks_found"] += len(blocks)
        _folders_with_blocks.add(doc.parent)

        diagrams_dir = doc.parent / "diagrams"
        manifest_path = diagrams_dir / "manifest.json"
        manifest = _load_manifest(manifest_path)
        manifest.setdefault("blocks", {})

        changed = False
        for index, match in enumerate(blocks, start=1):
            source = match.group(1).strip()
            if not source:
                continue
            key = f"{doc.relative_to(projects_dir)}#block-{index}"

            heading = _nearest_heading(doc_text, match.start())
            base_name = _slugify(heading) if heading else doc.stem
            if not base_name:
                base_name = f"{doc.stem}-diagram-{index}"
            # Deduplicate: a different source already owns this name.
            name = base_name
            suffix = 2
            existing_owner = manifest["blocks"].get(key)
            while True:
                candidate = diagrams_dir / f"{name}.puml"
                owner = None
                for other_key, entry in manifest["blocks"].items():
                    if other_key != key and entry.get("puml") == f"{name}.puml":
                        owner = other_key
                        break
                if owner is None or owner == key:
                    break
                name = f"{base_name}-{suffix}"
                suffix += 1

            puml_path = diagrams_dir / f"{name}.puml"
            svg_path = puml_path.with_suffix(".svg")
            sha = _sha256(source)
            entry = manifest["blocks"].get(key)

            # Idempotent re-run: unchanged source with a rendered SVG.
            if (
                entry
                and entry.get("sha256") == sha
                and entry.get("status") == "rendered"
                and svg_path.is_file()
            ):
                summary["unchanged"] += 1
                manifest["blocks"][key] = {
                    **entry,
                    "status": "rendered",
                    "source_doc": str(doc.relative_to(projects_dir)),
                }
                continue

            diagrams_dir.mkdir(parents=True, exist_ok=True)
            puml_path.write_text(source + "\n", encoding="utf-8")
            summary["puml_written"] += 1

            if can_render:
                ok = _render_puml(puml_path, jar, java)
                if ok:
                    summary["rendered"] += 1
                    entry_status = "rendered"
                    svg_refs = _external_refs(svg_path.read_text(encoding="utf-8"))
                    if svg_refs:
                        summary["external_refs"][str(svg_path)] = svg_refs
                else:
                    entry_status = "pending"
                    summary["pending"] += 1
            else:
                entry_status = "pending"
                summary["pending"] += 1

            manifest["blocks"][key] = {
                "name": name,
                "puml": f"{name}.puml",
                "svg": f"{name}.svg",
                "sha256": sha,
                "status": entry_status,
                "source_doc": str(doc.relative_to(projects_dir)),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            changed = True

        if changed:
            manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
            manifest["jar"] = jar
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
        # Record this doc's sidecar names under its diagrams folder so the
        # cross-folder duplicate report below can catch the canonical +
        # stale per-phase build split (uniform heading-derived names).
        folder_key = str(diagrams_dir.relative_to(project_root))
        names_here = _sidecar_names.setdefault(folder_key, [])
        for entry in manifest["blocks"].values():
            puml_name = entry.get("puml")
            if puml_name and puml_name not in names_here:
                names_here.append(puml_name)

    # A folder is "stale" when it holds .md files but none of them
    # contributed an inline PlantUML block — i.e. it was left behind by
    # a prior build that used clobbered {P_<ID>} values.
    stale = sorted(
        str(f.relative_to(project_root))
        for f in _all_project_folders
        if f not in _folders_with_blocks
        and any(f.glob("*.md"))
    )
    summary["stale_folders"] = stale

    # Orphaned sidecars: entries in the manifest whose source document
    # no longer exists.
    orphaned_count = 0
    for doc in projects_dir.rglob("manifest.json"):
        diagrams_dir = doc.parent
        try:
            manifest = json.loads(doc.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for _key, entry in manifest.get("blocks", {}).items():
            src_doc = entry.get("source_doc")
            if src_doc:
                src_path = projects_dir / src_doc
                if not src_path.is_file():
                    orphaned_count += 1
    summary["orphaned"] = orphaned_count

    # Cross-folder duplicate report: a sidecar name present in more than
    # one diagrams/ folder (e.g. canonical + stale per-phase split).
    name_to_folders: dict[str, list[str]] = {}
    for folder, names in _sidecar_names.items():
        for n in names:
            name_to_folders.setdefault(n, []).append(folder)
    summary["duplicate_sidecars"] = {
        n: sorted(folders)
        for n, folders in sorted(name_to_folders.items())
        if len(folders) > 1
    }

    return summary
