# TOGAF ADM Plugin — Web UI Solution Design

> **Status:** Draft (v0.1)
> **Author:** Terry Zhou
> **Date:** 2026-07-03
> **Target:** ArcKit TOGAF ADM overlay (`arckit-togaf-adm`)
> **Scope:** Web UI for guided ADM cycle execution with HIL (Human-in-the-Loop)

---

## 1. Problem Statement

### Current State

ArcKit TOGAF ADM is delivered as Claude Code slash commands (9 commands) with a YAML recipe (`togaf-adm-full`) defining a 13-node phase dependency graph. Users interact entirely through CLI:

```bash
/arckit:adm-preliminary "Casework modernisation"
/arckit:business-capability-map 003
/arckit:application-inventory 003
...
```

Each command triggers LLM analysis with `AskUserQuestion` prompts. Output is raw Markdown files in `projects/003/*.md`.

### Pain Points

| Problem | Impact |
|---|---|
| **No visual phase tracking** | Users cannot see which phases are complete, which are blocked |
| **Text-only HIL prompts** | `AskUserQuestion` renders as text in CLI — poor for structured input |
| **No dependency visualization** | Missing prerequisite phases require manual checking |
| **Barrier to entry** | Non-technical enterprise architects cannot use CLI effectively |
| **No progress feedback** | Users wait blindly during LLM processing |
| **Platform lock-in** | Requires Claude Code CLI — excludes Gemini/Codex/Paperclip users |

### Target State

A browser-based UI that guides users through the ADM cycle with:
- Visual phase dependency graph (green/yellow/grey/red states)
- Structured input forms per phase (dropdowns, radio buttons, sliders)
- Real-time progress streaming during LLM analysis
- Inline artifact viewer (markdown with live Mermaid diagrams)
- Persistent state across sessions (checkpoint resume)
- Accessible from any browser — no CLI required

---

## 2. Technology Analysis

### 2.1 Backend Options

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **FastAPI** | Async-native, Pydantic validation, auto OpenAPI docs, matches existing skill pattern | Requires extra dependency | ✅ Recommended |
| **Flask** | Mature ecosystem, simple | Limited async support, manual validation | ❌ Reject |
| **Starlette** | Minimal, async-native | No built-in validation, smaller ecosystem | ⚠️ Possible |
| **Node.js (Express/Hono)** | Unified with frontend build | Python-heavy project already | ❌ Reject |
| **Python stdlib only** | Zero dependencies | Manual WebSocket, no validation | ❌ Reject |

### 2.2 Frontend Options

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **HTMX + Vanilla JS** | Zero build step, server-driven, ~5KB total bundle, native SSE support | No drag-drop, limited offline | ✅ Recommended |
| **React + Vite** | Rich ecosystem, interactive DAG with `react-flow` | ~150KB bundle, requires build pipeline | ⚠️ Future upgrade |
| **SvelteKit** | Small bundle, excellent form reactivity | Smaller ecosystem | ⚠️ Possible |
| **HTMX + Jinja2** | Zero frontend code, all logic in Python | No rich interactivity | ⚠️ Simpler variant |
| **HTMX + HTWS** | WebSocket support via extension | Smaller ecosystem than SSE | ❌ Overkill |

### 2.3 Orchestration Options

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **LangGraph native** | Production DAG execution, built-in HIL `interrupt()`, checkpoint resume, error recovery | Requires understanding of LangGraph API | ✅ Recommended |
| **Custom bridge.py** | Full control over event format | Must reimplement HIL, state management, error handling (8 documented pitfalls) | ❌ Reject |
| **LangServe (LangGraph Cloud)** | Managed hosting, cloud dashboard | Per-call pricing ($0.50/1M tokens), external dependency | ❌ Reject for MVP |
| **Plain asyncio state machine** | Simple, no external deps | Manual dependency resolution, no checkpointing | ❌ Reject |

### 2.4 Transport Options

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **SSE (Server-Sent Events)** | Native HTTP streaming, HTMX built-in support, simple | One-directional (server→client) | ✅ Recommended (with POST for answers) |
| **WebSocket** | Bidirectional, real-time | Requires extension (`hx-ws`), complex connection management | ⚠️ Possible |
| **HTTP polling** | Simple to implement | Latency, server load | ❌ Reject |

---

## 3. Technology Recommendation

### Stack Summary

```
Browser (HTMX + Mermaid.js + marked.js)
  │ SSE (Server-Sent Events) + POST (form submissions)
  ▼
FastAPI (thin wrapper — routes, SSE stream, static files)
  │ astream() + interrupt()
  ▼
LangGraph StateGraph (13-node ADM DAG with HIL)
  │ checkpoint resume
  ▼
SQLite (local state persistence via SqliteSaver)
```

### Dependency List

| Category | Dependencies |
|---|---|
| **Backend** | `fastapi`, `uvicorn`, `jinja2`, `pydantic`, `httpx` |
| **Orchestration** | `langgraph`, `langchain-core` |
| **Frontend** | HTMX (CDN), Mermaid.js (CDN), marked.js (CDN) |
| **Containerization** | Docker Compose (FastAPI + nginx) |
| **Storage** | SQLite (checkpoint), filesystem (`.md` artifacts) |

### Why This Stack

1. **LangGraph solves HIL** — 8 documented bridge pitfalls (state leaks, nested scrolls, flag management) eliminated by native `interrupt()` + checkpoint
2. **HTMX eliminates frontend complexity** — Server-driven UI means zero build step, matches ArcKit's "just markdown" philosophy
3. **SSE fits the workflow** — ADM phases are server-initiated events (LLM analysis complete, phase transition). User answers are occasional POST requests.
4. **Low total lines of code** — ~830 lines (backend: 500, frontend: 300, config: 30)
5. **Extensible** — Can upgrade to React + WebSocket if multi-user editing or drag-drop DAG is needed

---

## 4. Change Impact on Existing Codebase

### 4.1 Files to Create

```
ui/
├── backend/
│   ├── main.py                    # FastAPI app, routes, SSE stream
│   ├── graph.py                    # LangGraph StateGraph compilation
│   ├── nodes/                      # Phase execution nodes
│   │   ├── preliminary.py
│   │   ├── capability_map.py
│   │   ├── gap_analysis.py
│   │   └── ... (9 total)
│   ├── artifact_engine.py          # Jinja2 → markdown rendering
│   ├── llm_client.py               # LLM API calls (httpx)
│   ├── project_store.py            # Read/write .md files
│   ├── schema.py                    # Pydantic models
│   ├── templates/                   # Jinja2 HTML partials
│   │   ├── index.html
│   │   ├── _phase_dag.html
│   │   ├── _phase_form.html
│   │   ├── _artifact_view.html
│   │   └── _chat_panel.html
│   ├── requirements.txt
│   └── Dockerfile
├── static/
│   ├── htmx.min.js                 # CDN or vendored
│   ├── mermaid.min.js              # CDN or vendored
│   ├── marked.min.js               # CDN or vendored
│   ├── app.css                      # Custom styles
│   └── app.js                       # Client-side state (~150 lines)
├── docker-compose.yaml
├── README.md
└── tests/
    ├── test_graph.py
    └── test_sse.py
```

### 4.2 Files to Modify

| File | Change |
|---|---|
| `plugins/arckit-togaf-adm/recipes/togaf-adm-full.yaml` | Add `ui_config:` section with phase form definitions |
| `pyproject.toml` | Add `langgraph`, `langchain-core` to dependencies |
| `scripts/converter.py` | Add `ui` target for generating UI-compatible phase definitions |
| `docs/PLATFORM-COMPARISON.md` | Add UI platform section |
| `README.md` | Add "Web UI" section with access instructions |

### 4.3 What Does NOT Change

- **Plugin command files** (`commands/*.md`) — remain unchanged, used as LLM prompts
- **Templates** (`templates/*.md`) — remain unchanged, used by artifact engine
- **Recipe YAML** — only extended with `ui_config:` optional section
- **Existing CLI workflow** — remains fully functional alongside UI
- **Extension generation** — `scripts/converter.py` unaffected

### 4.4 Migration Path

```
Phase 1 (MVP): UI alongside CLI
  └─ UI uses same plugins/arckit-togaf-adm/ structure
  └─ CLI and UI share templates and recipes

Phase 2 (Optional): UI as primary access
  └─ CLI remains for automated/scripted workflows
  └─ UI becomes default for interactive use

Phase 3 (Future): Multi-project dashboard
  └─ Aggregate view across all ADM cycles
  └─ Team collaboration features
```

---

## 5. Risks & Mitigations

### 5.1 Technical Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **LangGraph learning curve** | Medium — team unfamiliar with framework | Use proven pattern from `websocket-workflow-ui` skill; start with single phase |
| **SSE browser compatibility** | Low — all modern browsers support SSE | Fallback to HTTP polling if needed |
| **LLM API rate limits** | Medium — concurrent phase runs may hit limits | Implement request queuing; config for rate limits |
| **Large artifact streaming** | Low — markdown files are typically <50KB | Chunk SSE responses; virtual scroll for large artifacts |
| **SQLite concurrent writes** | Low — single-user tool | Accept limitation; upgrade to PostgreSQL if multi-user needed |

### 5.2 Product Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **Scope creep** | High — feature requests will expand | Strict MVP scope: 3 views (DAG, form, viewer). Nothing else. |
| **Platform fragmentation** | Medium — users may prefer CLI over UI | Keep CLI functional; UI is additive, not replacement |
| **Maintenance burden** | Medium — new codebase to maintain | Co-locate with existing project; share templates/recipes |
| **User abandonment** | Medium — enterprise users may not adopt | Target power users first (consultants, EA leads) |

### 5.3 Security Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **API key exposure** | Critical — LLM credentials in browser | All LLM calls happen server-side; browser never sees keys |
| **Local file access** | Low — project files in `projects/` | Path traversal protection; only serve from configured directory |
| **CSRF/XSS** | Medium — user-supplied markdown | Sanitize markdown output; CSP headers via nginx |

---

## 6. Solution Design

### 6.1 Architecture Overview

```
┌───────────────────────────────────────────────────────┐
│  Browser (any device, any OS)                      │
│                                                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐   │
│  │ Phase DAG │  │ Phase Form   │  │ Artifact View │   │
│  │ (Mermaid) │  │ (HTMX swap)  │  │ (marked.js)   │   │
│  └──────────┘  └──────────────┘  └───────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Conversation Panel (HIL Q&A, live during run)  │  │
│  └─────────────────────────────────────────────────┘  │
└──────────┬───────────────────────────────────────────┘
           │ SSE (stream) + POST (answers/config)
           │
┌──────────▼───────────────────────────────────────────┐
│  FastAPI (uvicorn)                                   │
│                                                       │
│  /              → index.html (nginx static)           │
│  /api/adm/:id/stream  → SSE phase stream              │
│  /api/adm/:id/config  → POST phase configuration      │
│  /api/adm/:id/answer  → POST HIL answer               │
│  /api/adm/:id/artifact/:type → GET markdown content   │
│  /api/projects       → GET project list               │
└──────────┬───────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────┐
│  LangGraph StateGraph                                │
│                                                       │
│  Nodes: PRIN → ADMP → BPCM → APP → APPR → GAPA      │
│        → TRANS → BORD → ACHG (optional)              │
│        → REPO (optional)                              │
│                                                       │
│  HIL Points: interrupt() at each phase config        │
│  Checkpoint: SqliteSaver per project thread         │
└──────────┬───────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────┐
│  Storage                                               │
│  ├─ SQLite checkpoint (in-memory or file)            │
│  └─ Filesystem: projects/{NNN}-{slug}/*.md           │
└───────────────────────────────────────────────────────┘
```

### 6.2 Data Model

#### Phase State (LangGraph `State`)

```python
class PhaseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ERROR = "error"

class PhaseState(BaseModel):
    id: str                           # e.g., "ADMP", "BPCM"
    status: PhaseStatus
    config: dict                      # User-selected options (scope, weighting)
    artifacts: dict                   # Generated artifacts {type: content}
    questions: list[dict]             # HIL questions asked
    answers: list[dict]              # User responses
    progress: float                   # 0.0–1.0 progress percentage
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None

class AdmCycleState(BaseModel):
    project_id: str
    phases: dict[str, PhaseState]    # phase_id → PhaseState
    current_phase: str | None
    metadata: dict                    # project name, description, etc.
```

#### SSE Event Schema

```python
class SSEEvent(BaseModel):
    type: str                         # "phase_update", "progress", "question", "complete"
    phase: str
    timestamp: datetime
    data: dict | None                 # Phase-specific data

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
```

### 6.3 UI Components

#### Phase DAG (Mermaid)

```html
<div id="phase-dag" hx-swap="innerHTML" hx-swap-oob="true">
  <pre class="mermaid">
    graph LR
    PRIN[PRIN ✓] --> ADMP[ADMP ✓]
    ADMP --> BPCM[BPCM ✓]
    BPCM --> APP[APP ✓]
    APP --> APPR[APPR ✓]
    APPR --> GAPA[GAPA ⏳]
    GAPA --> TRANS[TRANS -]
    TRANS --> BORD[BORD -]
    BORD --> ACHG[ACHG ?]
  </pre>
</div>
```

**Status legend:**
- `✓` (green) = completed
- `⏳` (yellow) = in progress
- `-` (grey) = pending
- `⚠` (red) = blocked (missing prerequisite)
- `?` (dotted) = optional

#### Phase Form

```html
<form id="phase-form"
      hx-post="/api/adm/003/gapa/configure"
      hx-swap="innerHTML"
      hx-target="#phase-panel"
      hx-indicator="#progress-indicator">

  <div class="form-group">
    <label>Scope</label>
    <select name="scope">
      <option>Enterprise-wide</option>
      <option selected>Business Unit</option>
      <option>Project-specific</option>
    </select>
  </div>

  <div class="form-group">
    <label>Gap severity weighting</label>
    <div class="radio-group">
      <input type="radio" name="weighting" value="balanced"> Balanced
      <input type="radio" name="weighting" value="strategic" checked> Strategic Risk
      <input type="radio" name="weighting" value="operational"> Operational Speed
    </div>
  </div>

  <div class="form-group">
    <label>Include baselines</label>
    <label><input type="checkbox" name="baselines" value="BPCM" checked> BPCM</label>
    <label><input type="checkbox" name="baselines" value="APP" checked> APP</label>
    <label><input type="checkbox" name="baselines" value="STRAT"> STRAT</label>
    <label><input type="checkbox" name="baselines" value="PRIN"> PRIN</label>
  </div>

  <button type="submit">Run Analysis</button>
  <div id="progress-indicator" class="htmx-indicator">Loading...</div>
</form>
```

#### Artifact Viewer

```html
<div id="artifact-viewer"
     hx-get="/api/adm/003/artifact/GAPA"
     hx-trigger="click from:[data-artifact='GAPA']"
     hx-swap="innerHTML"
     hx-indicator="#artifact-progress">
  <!-- Markdown renders here via marked.js -->
  <div class="markdown-content" id="markdown-output"></div>
</div>

<script>
  // HTMX afterSwap hook: render markdown
  document.body.addEventListener('htmx:afterRequest', (evt) => {
    if (evt.target.id === 'artifact-viewer') {
      const raw = evt.detail.xhr.responseText;
      document.getElementById('markdown-output').innerHTML =
        marked.parse(raw);
      // Render Mermaid diagrams
      mermaid.run({ nodes: document.querySelectorAll('.mermaid') });
    }
  });
</script>
```

#### HIL Conversation Panel

```html
<div id="chat-panel"
     hx-trigger="sse:phase-update"
     sse-source="/api/adm/003/stream"
     hx-swap="beforeend">
  <!-- Live events stream here -->
</div>

<!-- Event template (server-rendered) -->
<div class="event-item event-question">
  <div class="event-header">
    <span class="event-type">🤖 LLM</span>
    <span class="event-time">14:23:45</span>
  </div>
  <div class="event-body">
    I see your BPCM has 3 capability domains. Should I scope
    the gap analysis to all three, or focus on specific domains?
  </div>
  <div class="event-actions">
    <button hx-post="/api/adm/003/answer"
            hx-vals='{"answer": "All domains"}'
            hx-target="#chat-panel">
      All domains
    </button>
    <button hx-post="/api/adm/003/answer"
            hx-vals='{"answer": "Case Management only"}'
            hx-target="#chat-panel">
      Case Management only
    </button>
    <input type="text" name="custom" placeholder="Other...">
  </div>
</div>
```

### 6.4 State Machine Design

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Phase: PRIN│◄─── User fills form → POST /config
                    └──────┬──────┘
                           │ (config submitted)
                           ▼
                    ┌─────────────┐
                    │  LLM Analysis│── SSE: progress updates
                    │  (astream)  │── SSE: question (HIL)
                    └──────┬──────┘
                           │ (user answers via POST /answer)
                           ▼
                    ┌─────────────┐
                    │ HIL:        │── Resume analysis
                    │ interrupt() │
                    └──────┬──────┘
                           │ (complete)
                           ▼
                    ┌─────────────┐
                    │ Artifact    │── SSE: phase complete
                    │ generated  │── SSE: next phase available
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Next phase? │── Yes → repeat
                    └──────┬──────┘
                           │ No
                           ▼
                    ┌─────────────┐
                    │   COMPLETE  │
                    └─────────────┘
```

### 6.5 API Contract

#### Project Management

```
GET /api/projects                    → List all ADM cycles
POST /api/projects                   → Create new cycle
GET /api/projects/:id                → Get cycle state (phases, status)
```

#### Phase Execution

```
POST /api/adm/:project_id/:phase/configure
  Body: { scope: "...", weighting: "...", baselines: [...] }
  Response: 202 Accepted, starts phase execution

GET /api/adm/:project_id/:phase/status
  Response: { status: "in_progress", progress: 0.67, ... }
```

#### Streaming

```
GET /api/adm/:project_id/:phase/stream
  Response: text/event-stream (SSE)
  Events:
    - phase_update: { phase: "GAPA", status: "in_progress" }
    - progress: { phase: "GAPA", progress: 0.45 }
    - question: { phase: "GAPA", question: "...", options: [...] }
    - complete: { phase: "GAPA", artifact: "ARC-003-GAPA-v1.0.md" }
```

#### HIL Answers

```
POST /api/adm/:project_id/:phase/answer
  Body: { answer: "All domains" }
  Response: 200 OK, resumes analysis
```

#### Artifacts

```
GET /api/adm/:project_id/artifact/:type
  Response: Raw markdown content

GET /api/adm/:project_id/download/:type
  Response: File download (ARC-003-GAPA-v1.0.md)
```

### 6.6 Docker Compose Configuration

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./ui/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./projects:/app/projects:rw
      - ./plugins/arckit-togaf-adm:/app/plugin:ro
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=sqlite:///app/data/checkpoint.db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./ui/static:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
    restart: unless-stopped
```

### 6.7 Directory Structure (Final)

```
arc-kit/
├── ui/
│   ├── backend/
│   │   ├── main.py                 # FastAPI app
│   │   ├── graph.py                # LangGraph compilation
│   │   ├── nodes/                  # Phase execution nodes
│   │   ├── artifact_engine.py      # Jinja2 → markdown
│   │   ├── llm_client.py           # LLM API calls
│   │   ├── project_store.py        # File I/O
│   │   ├── schema.py               # Pydantic models
│   │   ├── templates/              # Jinja2 HTML
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── static/
│   │   ├── htmx.min.js
│   │   ├── mermaid.min.js
│   │   ├── marked.min.js
│   │   ├── app.css
│   │   └── app.js
│   ├── docker-compose.yaml
│   ├── README.md
│   └── tests/
├── plugins/arckit-togaf-adm/       # Unchanged (commands, templates)
├── scripts/converter.py            # Extended with ui target
├── pyproject.toml                  # Added langgraph deps
└── docs/solution_design.md         # This document
```

---

## 7. Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)

| Task | Output |
|---|---|
| Scaffold FastAPI + LangGraph | `backend/main.py`, `graph.py` |
| Implement single phase (ADMP) as proof | End-to-end CLI → LLM → artifact |
| SSE streaming setup | `/stream` endpoint working |
| Basic HTMX layout | `index.html` with phase form + artifact viewer |

### Phase 2: All Phases + HIL (Week 3-4)

| Task | Output |
|---|---|
| Remaining 8 phase nodes | All phases executable |
| HIL conversation panel | Live Q&A working |
| Phase DAG visualization | Mermaid graph with status colors |
| Artifact download | `GET /artifact/:type` working |

### Phase 3: Polish (Week 5-6)

| Task | Output |
|---|---|
| Progress indicators | Progress bar, phase status colors |
| Project management | Multi-project selector |
| Responsive design | Mobile-friendly layout |
| Error handling | User-friendly error messages |
| Documentation | `ui/README.md` with setup guide |

### Phase 4: Extensions (Future)

| Task | Output |
|---|---|
| Multi-project dashboard | Aggregate view across cycles |
| Export/import | JSON/YAML cycle export |
| Team collaboration | Multi-user editing (WebSocket upgrade) |
| React upgrade | Interactive DAG with `react-flow` |

---

## 8. Success Criteria

| Metric | Target |
|---|---|
| **Barrier to entry** | Non-technical EA can start ADM cycle in <5 minutes |
| **Phase completion rate** | >90% of users complete full ADM cycle (vs. <30% CLI) |
| **Load time** | <2s initial page load |
| **LLM response time** | <30s per phase (network-dependent) |
| **Bundle size** | <50KB total (CDN cached) |
| **Lines of code** | <1000 total |

---

## 9. Open Questions

| Question | Status |
|---|---|
| LLM provider integration (OpenAI vs Anthropic vs local)? | Configurable via env var |
| Authentication for multi-user deployment? | Basic auth via nginx (Phase 3) |
| Mobile support scope? | Responsive layout, no native app |
| Integration with existing ArcKit CLI workflow? | CLI and UI share same plugin structure |
| Plugin marketplace distribution? | Docker image + standalone deploy |

---

## 10. References

- `plugins/arckit-togaf-adm/recipes/togaf-adm-full.yaml` — Recipe definition
- `plugins/arckit-togaf-adm/commands/*.md` — Command definitions (9 files)
- `plugins/arckit-togaf-adm/templates/*.md` — Templates (9 files)
- `docs/plans/2026-07-01-arckit-togaf-adm-agent-architecture.md` — Architecture plan
- `docs/articles/2026-07-01-arckit-togaf-adm.md` — Product article
- `docs/PLATFORM-COMPARISON.md` — Platform comparison table
- `websocket-workflow-ui` skill — Proven WebSocket bridge pattern
- `hermes-dashboard-config` skill — Dashboard deployment pattern

---

## Appendix A: Mermaid Phase DAG Template

```mermaid
graph LR
    subgraph Foundation
      PRIN[PRIN<br>Principles]
    end

    subgraph Scope
      ADMP[ADMP<br>Architecture Vision]
      BPCM[BPCM<br>Business Capability Map]
    end

    subgraph Inventory
      APP[APP<br>Application Inventory]
      APPR[APPR<br>Application Rationalization]
    end

    subgraph Analysis
      GAPA[GAPA<br>Gap Analysis]
      TRANS[TRANS<br>Transition Architecture]
    end

    subgraph Governance
      BORD[BORD<br>Architecture Board]
      ACHG[ACHG<br>Architecture Change]
      REPO[REPO<br>Architecture Repository]
    end

    PRIN --> ADMP
    ADMP --> BPCM
    BPCM --> APP
    APP --> APPR
    APPR --> GAPA
    GAPA --> TRANS
    TRANS --> BORD
    BORD --> ACHG -.optional.
    ACHG --> REPO -.optional.

    style PRIN fill:#90EE90
    style ADMP fill:#90EE90
    style BPCM fill:#90EE90
    style APP fill:#90EE90
    style APPR fill:#90EE90
    style GAPA fill:#FFD700
    style TRANS fill:#D3D3D3
    style BORD fill:#D3D3D3
    style ACHG fill:#D3D3D3,stroke-dasharray: 5 5
    style REPO fill:#D3D3D3,stroke-dasharray: 5 5
```

## Appendix B: Sample Form Definitions (YAML)

```yaml
ui_config:
  phases:
    ADMP:
      title: "Architecture Vision"
      description: "Define scope, drivers, constraints, and success criteria"
      form:
        - name: scope
          type: select
          options:
            - Enterprise-wide
            - Business Unit
            - Project-specific
          default: "Business Unit"
        - name: drivers
          type: textarea
          label: "Key business drivers"
          required: true
        - name: constraints
          type: textarea
          label: "Known constraints"
        - name: success_criteria
          type: textarea
          label: "Success criteria"
      llm_questions:
        - prompt: "Should I include regulatory compliance drivers in the architecture vision?"
          options: ["Yes", "No", "Specify later"]
    BPCM:
      title: "Business Capability Map"
      form:
        - name: depth
          type: select
          options: [1, 2, 3]
          label: "Capability hierarchy depth"
        - name: value_streams
          type: textarea
          label: "Value stream descriptions"
```
