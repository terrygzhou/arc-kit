# TOGAF ADM Web UI — Scaffold Plan

> **Status:** Actionable scaffold plan
> **Based on:** `docs/solution_design.md`
> **Date:** 2026-07-03
> **Target:** Phase 1 (Week 1-2) — Core infrastructure + single phase proof

---

## 1. Directory Structure to Create

```
ui/
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, routes, SSE endpoints
│   ├── graph.py                     # LangGraph StateGraph compilation
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── preliminary.py          # ADM Preliminary (Phase 1 proof)
│   │   └── base.py                  # Base node template (inherited by others)
│   ├── artifact_engine.py           # Jinja2 → markdown rendering
│   ├── llm_client.py                # LLM API calls (httpx, configurable provider)
│   ├── project_store.py             # Read/write .md files to projects/
│   ├── schema.py                    # Pydantic models (Phase, State, Event)
│   ├── templates/                   # Jinja2 HTML partials
│   │   ├── index.html               # Single-page layout
│   │   ├── _phase_dag.html          # Mermaid DAG component
│   │   ├── _phase_form.html         # Dynamic form per phase
│   │   ├── _artifact_view.html      # Markdown viewer (marked.js)
│   │   └── _chat_panel.html         # HIL conversation panel
│   ├── requirements.txt
│   └── Dockerfile
├── static/
│   ├── htmx.min.js                   # Vendored or CDN link
│   ├── mermaid.min.js               # Vendored or CDN link
│   ├── marked.min.js                # Vendored or CDN link
│   ├── app.css                      # Custom styles
│   └── app.js                       # Client-side state (~150 lines)
├── docker-compose.yaml
├── README.md
└── tests/
    ├── __init__.py
    ├── test_graph.py                # LangGraph compilation test
    ├── test_sse.py                   # SSE streaming test
    └── test_nodes.py                # Phase node tests
```

---

## 2. Task Breakdown

### Task 1: Backend Scaffold (Day 1)

**Goal:** Create FastAPI app with basic routes + static file serving

**Files:**
- `ui/backend/main.py`
- `ui/backend/requirements.txt`
- `ui/backend/Dockerfile`
- `ui/static/app.css`
- `ui/static/app.js`

**Checklist:**
- [ ] Initialize FastAPI app with uvicorn
- [ ] Serve static files (nginx or FastAPI StaticFiles)
- [ ] Basic health check endpoint (`/health` → 200 OK)
- [ ] Requirements: fastapi, uvicorn, jinja2, pydantic, httpx
- [ ] Dockerfile: Python 3.11, uvicorn command

**Verify:**
```bash
cd ui/backend && python main.py  # or: uvicorn main:app --reload
curl http://localhost:8000/health  # → {"status": "ok"}
```

---

### Task 2: Schema & Data Model (Day 1-2)

**Goal:** Pydantic models for phase state, SSE events, project state

**Files:**
- `ui/backend/schema.py`

**Models to define:**

```python
# PhaseStatus enum
class PhaseStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ERROR = "error"

# PhaseState
class PhaseState(BaseModel):
    id: str
    status: PhaseStatus = PhaseStatus.PENDING
    config: dict = {}
    artifacts: dict = {}
    questions: list[dict] = []
    answers: list[dict] = []
    progress: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None

# AdmCycleState (LangGraph State)
class AdmCycleState(BaseModel):
    project_id: str
    phases: dict[str, PhaseState] = {}
    current_phase: str | None = None
    metadata: dict = {}

# SSE Event
class SSEEvent(BaseModel):
    type: str              # "phase_update", "progress", "question", "complete"
    phase: str
    timestamp: datetime
    data: dict | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
```

**Verify:**
```python
# Test model creation
state = AdmCycleState(project_id="003")
state.phases["ADMP"] = PhaseState(id="ADMP")
assert state.phases["ADMP"].status == PhaseStatus.PENDING
```

---

### Task 3: LangGraph Compilation (Day 2-3)

**Goal:** Compile recipe YAML into LangGraph StateGraph

**Files:**
- `ui/backend/graph.py`

**Implementation:**

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from schema import AdmCycleState

def load_recipe(path: str) -> dict:
    """Load togaf-adm-full.yaml recipe"""
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)

def compile_graph(recipe_path: str) -> StateGraph:
    """Compile recipe YAML into LangGraph StateGraph"""
    recipe = load_recipe(recipe_path)
    
    graph = StateGraph(AdmCycleState)
    
    # Register nodes from targets
    for target in recipe["targets"]:
        graph.add_node(target["id"], run_phase_node(target))
    
    # Wire dependencies as edges
    for target in recipe["targets"]:
        for dep in target.get("deps", []):
            graph.add_edge(dep, target["id"])
    
    # Compile with SQLite checkpoint for HIL
    checkpointer = SqliteSaver.from_conn_string(":memory:")
    return graph.compile(checkpointer=checkpointer)
```

**Verify:**
```python
graph = compile_graph("plugins/arckit-togaf-adm/recipes/togaf-adm-full.yaml")
assert graph is not None
# Graph should have 13 nodes
```

---

### Task 4: Phase Node Template (Day 3-4)

**Goal:** Base node template that all phases inherit

**Files:**
- `ui/backend/nodes/base.py`
- `ui/backend/nodes/preliminary.py`

**Base node template:**

```python
class PhaseNode:
    def __init__(self, target: dict):
        self.target = target
        self.phase_id = target["id"]
        self.skill = target["skill"]
        self.args = target["args"]
    
    async def execute(self, state: AdmCycleState, config: dict) -> dict:
        """Execute a single ADM phase"""
        # 1. Read command prompt from plugin
        prompt = read_command_prompt(self.phase_id)
        
        # 2. Read template
        template = read_template(self.phase_id)
        
        # 3. Read prerequisites (other artifacts)
        prereqs = read_prerequisites(self.target["deps"], state)
        
        # 4. Call LLM with prompt + prereqs + user config
        result = await llm_generate(prompt, prereqs, config)
        
        # 5. Render template with result
        artifact = render_template(template, result)
        
        # 6. Save artifact to projects/
        save_artifact(self.phase_id, artifact, state.project_id)
        
        return {
            self.phase_id: PhaseState(
                id=self.phase_id,
                status=PhaseStatus.COMPLETED,
                artifacts={self.phase_id: artifact},
                progress=1.0
            )
        }
```

**Preliminary phase (first concrete implementation):**

```python
from nodes.base import PhaseNode

class PreliminaryNode(PhaseNode):
    async def execute(self, state, config):
        # ADM Preliminary: Architecture Vision
        result = await super().execute(state, config)
        # Add HIL question before generation
        question = {
            "question": "What is the scope of this ADM engagement?",
            "options": ["Enterprise-wide", "Business Unit", "Project-specific"]
        }
        # interrupt() for user response
        user_scope = interrupt(
            question=question,
            resume_on="scope"
        )
        config["scope"] = user_scope
        return result
```

**Verify:**
```python
node = PreliminaryNode({"id": "ADMP", "skill": "arckit:adm-preliminary"})
# Test node initialization
assert node.phase_id == "ADMP"
```

---

### Task 5: LLM Client (Day 4-5)

**Goal:** Configurable LLM API client (OpenAI/Anthropic/local)

**Files:**
- `ui/backend/llm_client.py`

**Implementation:**

```python
class LLMClient:
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.client = self._init_client(provider)
    
    def _init_client(self, provider: str):
        if provider == "openai":
            return OpenAI()
        elif provider == "anthropic":
            return Anthropic()
        # Add more providers
    
    async def generate(self, prompt: str, system: str = "") -> str:
        """Generate response from LLM"""
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        # ... other providers
```

**Verify:**
```python
client = LLMClient(provider="openai")
result = await client.generate("Hello")
assert "Hello" in result
```

---

### Task 6: Artifact Engine (Day 5-6)

**Goal:** Jinja2 template → markdown rendering

**Files:**
- `ui/backend/artifact_engine.py`

**Implementation:**

```python
from jinja2 import Environment, FileSystemLoader

class ArtifactEngine:
    def __init__(self, template_dir: str):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render(self, template_name: str, context: dict) -> str:
        """Render a markdown template with context"""
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_from_string(self, template_str: str, context: dict) -> str:
        """Render a raw template string"""
        template = self.env.from_string(template_str)
        return template.render(**context)
```

**Verify:**
```python
engine = ArtifactEngine("plugins/arckit-togaf-adm/templates")
result = engine.render("adm-preliminary-template.md", {"project_id": "003"})
assert "Architecture Vision" in result
```

---

### Task 7: Project Store (Day 6-7)

**Goal:** Read/write `.md` files to `projects/` directory

**Files:**
- `ui/backend/project_store.py`

**Implementation:**

```python
from pathlib import Path

class ProjectStore:
    def __init__(self, base_dir: str = "projects"):
        self.base_dir = Path(base_dir)
    
    def list_projects(self) -> list[dict]:
        """List all project directories"""
        projects = []
        for dir in self.base_dir.glob("*"):
            if dir.is_dir():
                projects.append({
                    "id": dir.name,
                    "path": str(dir),
                    "artifacts": self._list_artifacts(dir)
                })
        return projects
    
    def read_artifact(self, project_id: str, artifact_type: str) -> str | None:
        """Read a specific artifact file"""
        pattern = f"ARC-{project_id}-{artifact_type}-*.md"
        files = list(self.base_dir.glob(f"{project_id}/*{pattern}"))
        if files:
            return files[0].read_text()
        return None
    
    def write_artifact(self, project_id: str, artifact_type: str, content: str):
        """Write artifact to projects/ directory"""
        dir = self.base_dir / project_id
        dir.mkdir(parents=True, exist_ok=True)
        filename = f"ARC-{project_id}-{artifact_type}-v1.0.md"
        (dir / filename).write_text(content)
        return str(dir / filename)
```

**Verify:**
```python
store = ProjectStore("projects")
store.write_artifact("003", "ADMP", "# Test content")
content = store.read_artifact("003", "ADMP")
assert content == "# Test content"
```

---

### Task 8: FastAPI Routes (Day 8-9)

**Goal:** Complete route implementations

**Files:**
- `ui/backend/main.py` (expand Task 1)

**Routes:**

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

# Project management
@app.get("/api/projects")
async def list_projects():
    return store.list_projects()

@app.post("/api/projects")
async def create_project(body: dict):
    # Create project directory
    return {"project_id": body["id"]}

# Phase execution
@app.post("/api/adm/{project_id}/{phase}/configure")
async def configure_phase(project_id: str, phase: str, config: dict):
    # Start phase execution via LangGraph
    thread_id = f"{project_id}:{phase}"
    async def stream():
        async for event in graph.astream(
            AdmCycleState(project_id=project_id, current_phase=phase),
            config={"configurable": {"thread_id": thread_id}}
        ):
            yield f"event: phase_update\ndata: {json.dumps(event)}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")

@app.post("/api/adm/{project_id}/{phase}/answer")
async def submit_answer(project_id: str, phase: str, answer: str):
    # Resume after HIL interrupt
    thread_id = f"{project_id}:{phase}"
    async def stream():
        async for event in graph.astream(
            None,  # Resume from checkpoint
            config={"configurable": {"thread_id": thread_id}},
            interrupt_kwargs={"answer": answer}
        ):
            yield f"event: phase_update\ndata: {json.dumps(event)}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")

# Artifact retrieval
@app.get("/api/adm/{project_id}/artifact/{artifact_type}")
async def get_artifact(project_id: str, artifact_type: str):
    content = store.read_artifact(project_id, artifact_type)
    return content or {}

# SSE Stream endpoint
@app.get("/api/adm/{project_id}/stream")
async def stream_events(project_id: str, request: Request):
    async def event_generator():
        # Monitor phase state and emit SSE
        while True:
            state = checkpoint.get_state(project_id)
            yield f"data: {json.dumps(state)}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Verify:**
```bash
curl http://localhost:8000/api/projects  # → []
curl http://localhost:8000/api/health    # → {"status": "ok"}
```

---

### Task 9: Frontend — HTML Layout (Day 10-11)

**Goal:** Single-page layout with DAG, form, and artifact viewer

**Files:**
- `ui/backend/templates/index.html`
- `ui/backend/templates/_phase_dag.html`
- `ui/backend/templates/_phase_form.html`
- `ui/backend/templates/_artifact_view.html`
- `ui/backend/templates/_chat_panel.html`

**Main layout (`index.html`):**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ArcKit — TOGAF ADM</title>
  <link rel="stylesheet" href="/app.css">
  <script src="/htmx.min.js"></script>
  <script src="/mermaid.min.js"></script>
  <script src="/marked.min.js"></script>
</head>
<body>
  <div class="container">
    <header>
      <h1>ArcKit — TOGAF ADM</h1>
      <div id="project-selector">
        <button hx-get="/api/projects" hx-swap="innerHTML" hx-target="#project-list">
          Load Projects
        </button>
        <div id="project-list"></div>
      </div>
    </header>

    <main>
      <aside id="phase-dag">
        <!-- Mermaid DAG rendered here -->
      </aside>

      <section id="phase-panel">
        <!-- Dynamic form per phase -->
      </section>

      <aside id="artifact-viewer">
        <!-- Markdown artifact viewer -->
      </aside>
    </main>

    <footer id="chat-panel">
      <!-- HIL conversation -->
    </footer>
  </div>
  <script src="/app.js"></script>
</body>
</html>
```

**Phase form partial (`_phase_form.html`):**

```html
<form id="phase-form"
      hx-post="/api/adm/{{ project_id }}/{{ phase }}/configure"
      hx-swap="innerHTML"
      hx-target="#phase-panel"
      hx-indicator="#progress-indicator">

  <h2>{{ phase_title }}</h2>
  <p class="phase-description">{{ phase_description }}</p>

  <div class="form-group">
    <label>Scope</label>
    <select name="scope">
      <option>Enterprise-wide</option>
      <option selected>Business Unit</option>
      <option>Project-specific</option>
    </select>
  </div>

  <button type="submit">Run Analysis</button>
  <div id="progress-indicator" class="htmx-indicator">Loading...</div>
</form>
```

**Verify:**
```bash
curl http://localhost:8000/  # → HTML response
# Open in browser, verify HTMX loads
```

---

### Task 10: Frontend — JS Logic (Day 11-12)

**Goal:** Client-side state management + Mermaid rendering

**Files:**
- `ui/static/app.js`

**Implementation:**

```javascript
// Phase state tracker
const phaseStates = {};

// HTMX afterRequest: update DAG visualization
document.body.addEventListener('htmx:afterRequest', (evt) => {
  const data = evt.detail.xhr?.responseText;
  if (data && evt.target.id === 'phase-panel') {
    updatePhaseState(JSON.parse(data));
    renderDAG();
  }
});

// Mermaid DAG renderer
function renderDAG() {
  const dagDiv = document.getElementById('phase-dag');
  let mermaidDef = 'graph LR\n';
  
  for (const [id, state] of Object.entries(phaseStates)) {
    const status = state.status === 'completed' ? '✓' :
                  state.status === 'in_progress' ? '⏳' : '-';
    mermaidDef += `${id}[${id} ${status}] `;
  }
  
  // Wire dependencies (simplified — full DAG from recipe)
  mermaidDef += 'ADMP --> BPCM --> APP --> APPR --> GAPA --> TRANS --> BORD --> ACHG --> REPO';
  
  dagDiv.innerHTML = `<pre class="mermaid">${mermaidDef}</pre>`;
  mermaid.run({ nodes: dagDiv.querySelectorAll('.mermaid') });
}

// Markdown renderer (marked.js)
function renderMarkdown(raw) {
  const viewer = document.getElementById('artifact-viewer');
  viewer.innerHTML = marked.parse(raw);
  // Render any Mermaid diagrams in markdown
  mermaid.run({ nodes: viewer.querySelectorAll('.mermaid') });
}

// Phase state update
function updatePhaseState(data) {
  phaseStates[data.phase] = data;
  renderDAG();
}
```

**Verify:**
```bash
# Open browser DevTools → Network tab → verify SSE events
# Verify Mermaid renders in #phase-dag
```

---

### Task 11: Docker Compose (Day 12-13)

**Goal:** Docker Compose configuration for development

**Files:**
- `ui/docker-compose.yaml`
- `ui/nginx.conf`

**docker-compose.yaml:**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ../projects:/app/projects:rw
      - ../plugins/arckit-togaf-adm:/app/plugin:ro
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=sqlite:///app/data/checkpoint.db
      - TEMPLATE_DIR=/app/plugin/templates
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./static:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
    restart: unless-stopped
```

**Verify:**
```bash
cd ui && docker compose up --build
curl http://localhost/health  # → {"status": "ok"}
```

---

### Task 12: Tests (Day 13-14)

**Goal:** Unit tests for core components

**Files:**
- `ui/tests/test_graph.py`
- `ui/tests/test_sse.py`
- `ui/tests/test_nodes.py`

**Test structure:**

```python
# test_graph.py
def test_compile_graph():
    graph = compile_graph("plugins/arckit-togaf-adm/recipes/togaf-adm-full.yaml")
    assert graph is not None
    # Verify 13 nodes
    nodes = graph.get_graph().nodes
    assert len(nodes) == 13

def test_graph_edges():
    graph = compile_graph("plugins/arckit-togaf-adm/recipes/togaf-adm-full.yaml")
    edges = graph.get_graph().edges
    # Verify key dependencies
    assert ("ADMP", "BPCM") in edges

# test_nodes.py
def test_preliminary_node():
    node = PreliminaryNode({"id": "ADMP", "skill": "arckit:adm-preliminary"})
    assert node.phase_id == "ADMP"

# test_sse.py
def test_sse_stream():
    # Verify SSE event format
    event = SSEEvent(type="phase_update", phase="ADMP")
    assert event.type == "phase_update"
```

**Verify:**
```bash
cd ui && python -m pytest tests/ -v
```

---

## 3. Execution Order

```
Week 1:
  Day 1:   Task 1 (backend scaffold) + Task 2 (schema)
  Day 2:   Task 3 (LangGraph compilation)
  Day 3:   Task 4 (base node + preliminary node)
  Day 4-5: Task 5 (LLM client) + Task 6 (artifact engine)
  Day 6:   Task 7 (project store)
  Day 7:   Task 8 (FastAPI routes) + Task 9 (HTML layout)
  Day 8:   Task 10 (JS logic) + integration test
  Day 9:   Task 11 (Docker) + Task 12 (tests)
  Day 10:  Polish + documentation

Week 2:
  Days 11-14: Remaining 8 phases (8 more node files)
  Days 15-16: HIL conversation panel + integration
  Days 17-18: Polish + error handling
  Days 19-20: Documentation + Docker deployment guide
```

---

## 4. Acceptance Criteria

| Milestone | Criteria |
|---|---|
| **M1: Backend scaffold** | FastAPI app serves health check, static files |
| **M2: Single phase proof** | `/arckit:adm-preliminary` works via UI → artifact generated |
| **M3: All phases** | All 9 phases executable via UI |
| **M4: HIL working** | Questions stream via SSE, answers via POST resume analysis |
| **M5: Docker ready** | `docker compose up` → fully working application |
| **M6: Tests passing** | `pytest` → 100% pass on core components |

---

## 5. Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LangGraph `interrupt()` API changes | Medium | Medium | Abstract via `nodes/base.py` interface |
| SSE browser compatibility | Low | Medium | Fallback to HTTP polling |
| LLM rate limits during testing | High | Low | Use cached responses for unit tests |
| Template path resolution in Docker | Medium | Medium | Use volume mount for plugin templates |
| Mermaid.js rendering large DAGs | Low | Low | Limit to 13 nodes — fits easily |

---

## 6. Success Metrics

| Metric | Target |
|---|---|
| **Total lines of code** | <1000 (backend: 700, frontend: 200, tests: 100) |
| **Dependencies** | 6 Python packages, 3 CDN libs |
| **Container image size** | <500MB (Python base ~400MB) |
| **Test coverage** | 80%+ on core components |
| **Time to first artifact** | <5 minutes from UI load |

---

## Appendix: File Contents Checklist

Each file listed above needs:
1. ✅ Created with correct path
2. ✅ Imports resolved (no missing imports)
3. ✅ Type hints (Pydantic/Python 3.11+)
4. ✅ Error handling (try/except, HTTP 500 fallback)
5. ✅ Logging (structured logging for each operation)
6. ✅ Documentation (docstrings, inline comments for complex logic)
