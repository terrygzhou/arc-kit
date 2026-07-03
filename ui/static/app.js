/**
 * ArcKit TOGAF ADM UI — Client-side state management
 *
 * Handles:
 * - Phase DAG rendering (Mermaid.js)
 * - Markdown rendering (marked.js)
 * - HTMX event coordination
 * - HIL conversation panel
 */

// ── Phase state tracker ───────────────────────────────────────

const phaseStates = {};
const currentProjectId = null; // Set from URL or project selection
const currentPhaseId = null;

// ── Mermaid DAG renderer ─────────────────────────────────────

function initMermaid() {
    mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'loose',
    });
}

function renderDAG() {
    const container = document.getElementById('mermaid-dag');
    if (!container) return;

    // Build DAG definition from phase states
    let def = 'graph LR\n';

    // Status symbols
    const statusSymbols = {
        'completed': '✓',
        'in_progress': '⏳',
        'blocked': '⚠',
        'error': '✗',
        'pending': '-',
    };

    // Phase nodes
    const phases = ['PRIN', 'ADMP', 'BPCM', 'APP', 'APPR', 'GAPA', 'TRANS', 'BORD', 'ACHG', 'REPO'];
    const optional = ['ACHG', 'REPO'];

    for (const phase of phases) {
        const state = phaseStates[phase] || { status: 'pending' };
        const symbol = statusSymbols[state.status] || '-';
        const isOptional = optional.includes(phase) ? ' -.?' : '';

        def += `${phase}[${phase} ${symbol}]${isOptional}\n`;
    }

    // Dependencies
    const deps = [
        ['PRIN', 'ADMP'],
        ['ADMP', 'BPCM'],
        ['BPCM', 'APP'],
        ['APP', 'APPR'],
        ['APPR', 'GAPA'],
        ['GAPA', 'TRANS'],
        ['TRANS', 'BORD'],
        ['BORD', 'ACHG'],
        ['ACHG', 'REPO'],
    ];

    for (const [from, to] of deps) {
        const isOptional = optional.includes(to);
        def += isOptional ? `${from} -.-> ${to}` : `${from} --> ${to}`;
        def += '\n';
    }

    container.textContent = def;

    // Render Mermaid
    mermaid.run({ nodes: [container] }).catch(err => {
        console.warn('Mermaid render error:', err);
    });
}

// ── Markdown rendering ────────────────────────────────────────

function renderMarkdown(raw) {
    const viewer = document.getElementById('artifact-viewer');
    if (!viewer) return;

    viewer.innerHTML = marked.parse(raw);
    // Re-render any Mermaid diagrams in the markdown
    mermaid.run({ nodes: viewer.querySelectorAll('.mermaid') });
}

// ── HIL conversation panel ────────────────────────────────────

function addMessage(role, text) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const msg = document.createElement('div');
    msg.className = `chat-message ${role}`;
    msg.textContent = text;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

function submitAnswer() {
    const input = document.getElementById('answer-input');
    const answer = input.value.trim();
    if (!answer) return;

    // Show user message
    addMessage('user', answer);

    // Send to backend
    const projectId = currentProjectId;
    const phaseId = currentPhaseId;
    if (!projectId || !phaseId) return;

    fetch(`/api/adm/${projectId}/${phaseId}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer }),
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'accepted') {
            addMessage('llm', 'Analysis resumed...');
        }
    })
    .catch(err => {
        addMessage('llm', `Error: ${err.message}`);
    });

    input.value = '';
}

// ── Phase state update from SSE ──────────────────────────────

function updatePhaseState(event) {
    if (event.type === 'phase_update' && event.phase) {
        phaseStates[event.phase] = event.data || { status: 'in_progress' };
        renderDAG();
    }
    if (event.type === 'question' && event.phase) {
        addMessage('llm', event.data?.question || 'Please provide input.');
    }
    if (event.type === 'complete' && event.phase) {
        phaseStates[event.phase] = { status: 'completed' };
        renderDAG();
    }
}

// ── Initialization ────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initMermaid();
    renderDAG();

    // Bind submit button
    const submitBtn = document.getElementById('submit-answer');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitAnswer);
    }

    // Bind Enter key for answer input
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') submitAnswer();
        });
    }

    // HTMX: update DAG after phase panel swap
    document.body.addEventListener('htmx:afterRequest', (evt) => {
        if (evt.detail.targetId === 'phase-form-container') {
            renderDAG();
        }
    });

    // HTMX: render markdown in artifact viewer
    document.body.addEventListener('htmx:afterOnLoad', (evt) => {
        if (evt.detail.targetId === 'artifact-viewer') {
            const raw = evt.detail.xhr?.responseText;
            if (raw) {
                try {
                    const parsed = JSON.parse(raw);
                    renderMarkdown(parsed.content);
                } catch {
                    renderMarkdown(raw);
                }
            }
        }
    });
});
