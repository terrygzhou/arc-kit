# ArcKit TOGAF ADM Web UI

> Web interface for guided TOGAF ADM cycle execution.

## Quick Start

```bash
# 1. Install dependencies
cd ui/backend && pip install -r requirements.txt

# 2. Run locally (requires projects/ directory)
uvicorn main:app --reload --port 8000

# 3. Open browser
open http://localhost:8000
```

## Docker Deploy

```bash
# Build and run
docker compose up --build

# Access at http://localhost
```

## Architecture

```
Browser (HTMX + Mermaid + marked.js)
  │ SSE + POST
  ▼
FastAPI (routes, static serving)
  │ astream() + interrupt()
  ▼
LangGraph StateGraph (13-node ADM DAG)
  │ checkpoint
  ▼
SQLite + filesystem (.md artifacts)
```

## Dependencies

| Category | Packages |
|---|---|
| Backend | fastapi, uvicorn, jinja2, pydantic, httpx, langgraph |
| Frontend | HTMX (CDN), Mermaid.js (CDN), marked.js (CDN) |
| Config | docker compose, nginx |

## File Layout

```
ui/
├── backend/               # FastAPI app
│   ├── main.py             # Routes + SSE
│   ├── graph.py            # LangGraph compilation
│   ├── nodes/              # Phase execution nodes
│   ├── schema.py           # Pydantic models
│   ├── templates/          # Jinja2 HTML
│   └── requirements.txt
├── static/                 # Frontend assets
├── tests/                  # pytest tests
├── docker-compose.yaml
└── nginx.conf
```

## Running Tests

```bash
cd ui
PYTHONPATH=backend pytest tests/ -v
```

## Status

**M1 (backend scaffold):** ✅ Complete
**M2 (single phase proof):** In progress — ADMP node scaffolded
**M3-M6:** Planned
