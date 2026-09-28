"""_render_puml must emit SVG (not PNG) so the sweep's .svg sidecars
are actually produced by the pinned jar.

Regression guard for the gloryev incident: the sweep's success check
looked for ``<file>.svg`` but the jar invocation had no ``-tsvg``
flag — PlantUML's default output is PNG, so every render silently
"failed" and SVG delivery was deferred to a post-build sweep that
could never complete.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import arckit_cli.diagrams as diagrams


def test_render_puml_invokes_jar_with_svg_format(tmp_path, monkeypatch):
    puml = tmp_path / "view.puml"
    puml.write_text("@startuml\n@enduml\n", encoding="utf-8")

    captured: dict = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        puml.with_suffix(".svg").write_text("<svg/>", encoding="utf-8")

        class _P:
            returncode = 0

        return _P()

    monkeypatch.setattr(diagrams.subprocess, "run", fake_run)

    ok = diagrams._render_puml(puml, "fake.jar", "/usr/bin/java")

    assert ok, "render should report success when the jar exits 0 and writes .svg"
    cmd = captured["cmd"]
    # Full invocation: java -jar <jar> -tsvg <file.puml>
    expected = ["/usr/bin/java", "-jar", "fake.jar", "-tsvg", str(puml)]
    assert cmd == expected, (
        "must pass -tsvg — without it PlantUML writes PNG (its default) "
        "and the .svg sidecar is never produced"
    )
