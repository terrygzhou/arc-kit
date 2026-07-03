"""Project file store — CRUD for ADM cycle artifacts on the filesystem."""

from pathlib import Path
from typing import Any


class ProjectStore:
    """Read/write `.md` artifacts under `projects/{project_id}/`."""

    def __init__(self, base_dir: str = "projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ── Project management ──────────────────────────────────────────

    def list_projects(self) -> list[dict[str, Any]]:
        """Return metadata for every directory under base_dir."""
        projects = []
        for dirpath in sorted(self.base_dir.glob("*")):
            if not dirpath.is_dir():
                continue
            artifacts = self._list_artifacts(dirpath)
            projects.append(
                {
                    "id": dirpath.name,
                    "name": dirpath.name.replace("-000-global", "Global"),
                    "path": str(dirpath),
                    "artifact_count": len(artifacts),
                    "artifacts": artifacts,
                }
            )
        return projects

    def create_project(self, project_id: str, name: str = "") -> Path:
        """Ensure project directory exists."""
        slug = self._slugify(name) if name else project_id
        dirpath = self.base_dir / f"{project_id}-{slug}"
        dirpath.mkdir(parents=True, exist_ok=True)
        # Placeholder for external documents
        (dirpath / "external").mkdir(exist_ok=True)
        readme = dirpath / "README.md"
        if not readme.exists():
            readme.write_text(f"# {name or project_id}\n")
        return dirpath

    # ── Artifact I/O ────────────────────────────────────────────────

    def read_artifact(self, project_id: str, artifact_type: str) -> str | None:
        """Read the latest artifact of a given type (e.g. ADMP, BPCM)."""
        pattern = f"ARC-{project_id}-{artifact_type}-*.md"
        matches = sorted(self._glob(project_id, pattern), reverse=True)
        if matches:
            return matches[0].read_text()
        return None

    def write_artifact(
        self, project_id: str, artifact_type: str, content: str, version: str = "1.0"
    ) -> str:
        """Write artifact markdown. Returns the absolute file path."""
        dirpath = self.base_dir / project_id
        dirpath.mkdir(parents=True, exist_ok=True)
        filename = f"ARC-{project_id}-{artifact_type}-v{version}.md"
        (dirpath / filename).write_text(content)
        return str(dirpath / filename)

    # ── Internals ─────────────────────────────────────────────────

    @staticmethod
    def _slugify(name: str) -> str:
        return "".join(c if c.isalnum() or c == "-" else "-" for c in name.lower()).strip("-")

    def _glob(self, project_id: str, pattern: str) -> list[Path]:
        """Search both `{project_id}-*` and bare `{project_id}/`."""
        results = list((self.base_dir / project_id).glob(pattern))
        # Also check slugified subdirs
        for dirpath in self.base_dir.glob(f"{project_id}-*"):
            results.extend(dirpath.glob(pattern))
        return results

    def _list_artifacts(self, dirpath: Path) -> list[str]:
        out: list[str] = []
        for f in sorted(dirpath.glob("ARC-*.md")):
            out.append(f.stem)
        return out
