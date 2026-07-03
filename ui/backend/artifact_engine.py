"""Jinja2-based markdown artifact renderer."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, BaseLoader


class ArtifactEngine:
    """Render TOGAF templates with LLM-generated content."""

    def __init__(self, template_dir: str | None = None):
        if template_dir and Path(template_dir).exists():
            self.env = Environment(
                loader=FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            self.env = Environment(
                loader=BaseLoader(),
                trim_blocks=True,
                lstrip_blocks=True,
            )

    def render(self, template_name: str, context: dict) -> str:
        """Render a named template from the template directory."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_string(self, template_text: str, context: dict) -> str:
        """Render an in-memory template string."""
        template = self.env.from_string(template_text)
        return template.render(**context)

    def render_command(self, command_file: Path, context: dict) -> str:
        """Render a command .md file as LLM system prompt."""
        return command_file.read_text()
