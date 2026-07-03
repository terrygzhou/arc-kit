"""ADM Preliminary (Phase 0) — Architecture Vision."""

import logging
from datetime import datetime, timezone
from pathlib import Path

from nodes.base import BasePhaseNode
from schema import PhaseState, PhaseStatus

logger = logging.getLogger(__name__)


class PreliminaryNode(BasePhaseNode):
    """Preliminary phase: scope, drivers, constraints, vision."""

    async def execute(self, state: dict, config: dict) -> dict:
        project_id = state["project_id"]
        phase_id = self.phase_id

        # ── 1. Mark phase in-progress ─────────────────────────────
        now = datetime.now(timezone.utc)
        phase = PhaseState(
            id=phase_id,
            status=PhaseStatus.IN_PROGRESS,
            started_at=now,
            progress=0.2,
        )
        state["phases"][phase_id] = dict(phase)
        state["current_phase"] = phase_id

        # ── 2. Load command prompt ────────────────────────────────
        cmd_file = Path(self.plugin_root) / "commands" / "adm-preliminary.md"
        if cmd_file.exists():
            system_prompt = cmd_file.read_text()
        else:
            system_prompt = "Generate an Architecture Vision document."

        # ── 3. Build user prompt from config ─────────────────────
        user_context = "\n".join(
            f"{k}: {v}"
            for k, v in [
                ("Project", state.get("project_name", project_id)),
                ("Scope", config.get("scope", "Business Unit")),
                ("Drivers", config.get("drivers", "Not specified")),
                ("Constraints", config.get("constraints", "Not specified")),
                ("Success Criteria", config.get("success_criteria", "TBD")),
            ]
            if v
        )

        # ── 4. Call LLM (real or fallback) ───────────────────────
        try:
            from llm_client import LLMClient

            client = LLMClient()
            api_key = client._api_key()
            if api_key:
                logger.info("Calling LLM for phase %s", phase_id)
                llm_output = await client.generate(
                    system=system_prompt,
                    user=user_context,
                    temperature=0.3,
                )
            else:
                logger.warning("No LLM API key set — using fallback content")
                llm_output = f"# Architecture Vision\n\nProject: {project_id}\nScope: {config.get('scope', 'TBD')}\n\n(Fallback: no LLM API key configured)\n"
        except Exception as e:
            logger.error("LLM call failed for phase %s: %s", phase_id, e)
            llm_output = (
                f"# Architecture Vision\n\n"
                f"Project: {project_id}\n\n"
                f"(LLM error: {e})\n"
            )

        # ── 5. Update progress ───────────────────────────────────
        phase.progress = 0.7

        # ── 6. Render template ────────────────────────────────────
        from artifact_engine import ArtifactEngine
        from project_store import ProjectStore

        template_file = Path(self.plugin_root) / "templates" / "adm-preliminary-template.md"

        if template_file.exists():
            engine = ArtifactEngine()
            artifact = engine.render_string(
                template_file.read_text(),
                {
                    "project_id": project_id,
                    "project_name": state.get("project_name", ""),
                    "llm_output": llm_output,
                    "scope": config.get("scope", "TBD"),
                    "drivers": config.get("drivers", ""),
                    "constraints": config.get("constraints", ""),
                    "timestamp": now.isoformat(),
                },
            )
        else:
            artifact = llm_output

        # ── 7. Persist artifact ──────────────────────────────────
        store = ProjectStore()
        filepath = store.write_artifact(project_id, phase_id, artifact)
        logger.info("Artifact saved: %s", filepath)

        # ── 8. Complete phase ────────────────────────────────────
        phase.status = PhaseStatus.COMPLETED
        phase.artifacts = {phase_id: filepath}
        phase.progress = 1.0
        phase.completed_at = datetime.now(timezone.utc)
        state["phases"][phase_id] = dict(phase)

        return state
