"""FastAPI application — routes, SSE, and static serving."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup/shutdown."""
    logger.info("ArcKit TOGAF ADM UI starting")
    yield
    logger.info("Shutting down")


# ── App factory ───────────────────────────────────────────────────────

app = FastAPI(title="ArcKit TOGAF ADM UI", version="0.1.0", lifespan=lifespan)

# Lazy imports (avoid circular deps during module load)
def _get_store():
    from project_store import ProjectStore
    return ProjectStore(base_dir="projects")


def _get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


# ── Static files ─────────────────────────────────────────────────────

app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent.parent / "static")),
    name="static",
)


# ── Request/response models ────────────────────────────────────────

class ProjectCreate(BaseModel):
    id: str
    name: str = ""


class PhaseConfig(BaseModel):
    scope: str = "Business Unit"
    drivers: str = ""
    constraints: str = ""
    success_criteria: str = ""


class PhaseAnswer(BaseModel):
    answer: str


# ── Routes ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """Main layout."""
    templates = _get_templates()
    return templates.TemplateResponse("index.html", {})


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


# ── Project management ────────────────────────────────────────────

@app.get("/api/projects")
async def list_projects():
    """Return all projects with artifact counts."""
    store = _get_store()
    return store.list_projects()


@app.post("/api/projects")
async def create_project(body: ProjectCreate):
    """Create a new project directory."""
    store = _get_store()
    path = store.create_project(body.id, body.name)
    return {"project_id": body.id, "path": str(path)}


# ── Phase execution ───────────────────────────────────────────────

@app.post("/api/adm/{project_id}/{phase}/configure")
async def configure_phase(project_id: str, phase: str, config: PhaseConfig):
    """Submit phase configuration → triggers LLM analysis."""
    return {
        "status": "accepted",
        "message": f"Phase {phase} configuration received",
        "config": config.model_dump(),
    }


@app.post("/api/adm/{project_id}/{phase}/answer")
async def submit_answer(project_id: str, phase: str, body: PhaseAnswer):
    """Submit HIL answer → resumes analysis from checkpoint."""
    return {
        "status": "accepted",
        "answer": body.answer,
    }


@app.post("/api/adm/{project_id}/{phase}/run")
async def run_phase(project_id: str, phase: str, config: PhaseConfig):
    """Execute a single phase synchronously (scaffold proof)."""
    store = _get_store()
    plugin_root = str(Path(__file__).parent.parent.parent.parent / "plugins" / "arckit-togaf-adm")

    # Build initial state
    initial_state = {
        "project_id": project_id,
        "project_name": "",
        "phases": {},
        "current_phase": phase,
    }

    # Dispatch based on phase ID
    if phase == "ADMP":
        from nodes.preliminary import PreliminaryNode
        import asyncio

        node = PreliminaryNode(
            target={"id": "ADMP", "skill": "arckit:adm-preliminary", "args": ""},
            plugin_root=plugin_root,
        )
        result = await node.execute(initial_state, config.model_dump())
        return {
            "status": "completed",
            "phase": phase,
            "artifact_path": result["phases"].get("ADMP", {}).get("artifacts", {}).get("ADMP", ""),
        }

    raise HTTPException(status_code=400, detail=f"Phase {phase} not yet implemented")


# ── Artifact retrieval ───────────────────────────────────────────

@app.get("/api/adm/{project_id}/artifact/{artifact_type}")
async def get_artifact(project_id: str, artifact_type: str):
    """Get raw markdown content for a specific artifact type."""
    store = _get_store()
    content = store.read_artifact(project_id, artifact_type)
    if content is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {"content": content}


# ── SSE Stream (placeholder) ─────────────────────────────────────

@app.get("/api/adm/{project_id}/stream")
async def sse_stream(project_id: str):
    """SSE endpoint for real-time phase updates (scaffold)."""

    async def event_generator():
        """Yield periodic heartbeats until cancelled."""
        counter = 0
        while True:
            yield f"data: {json.dumps({'type': 'heartbeat', 'count': counter})}\n\n"
            counter += 1
            await asyncio.sleep(5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
