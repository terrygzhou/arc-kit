#!/usr/bin/env node
/**
 * Unit tests for the .arckit/templates freshness guard in the Codex hook.
 *
 * Codex skills resolve "default" templates from the workspace's
 * .arckit/templates/ materialization. When that materialization predates
 * template sections (e.g. "## Intake Interview Questions"), or is missing
 * entirely, the intake interview is silently skipped and users are never
 * asked about current state. The hook surfaces a warning in the session
 * context so the user can refresh with `arckit init --here --ai codex`.
 *
 * Hook wiring (SessionStart/UserPromptSubmit emission) is covered by
 * tests/codex/test_codex_extension.py::test_codex_hook_warns_on_stale_template_materialization
 * and the fresh-materialization variant.
 *
 * Run with: node tests/codex/test_template_freshness_guard.mjs
 */

import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative } from "node:path";
import test from "node:test";
import assert from "node:assert/strict";

import { templateFreshnessNote } from "../../extensions/arckit-codex/hooks/template-freshness.mjs";

const REFRESH_HINT = "arckit init --here --ai codex";

function makePluginFixture() {
  const root = mkdtempSync(join(tmpdir(), "arckit-plugin-"));
  const templates = join(root, "templates");
  mkdirSync(templates, { recursive: true });
  writeFileSync(
    join(templates, "gap-analysis-template.md"),
    "# Gap Analysis\n\n## Intake Interview Questions\n\n- Q: What is the current state?\n",
  );
  writeFileSync(
    join(templates, "application-inventory-template.md"),
    "# Application Inventory\n\n## Intake Interview Questions\n\n- Q: Which applications exist today?\n",
  );
  mkdirSync(join(templates, "_partials"), { recursive: true });
  writeFileSync(join(templates, "_partials", "doc-control.md"), "# Doc Control\n");
  return root;
}

function materializeWorkspace(pluginRoot, { staleFiles = [] } = {}) {
  const ws = mkdtempSync(join(tmpdir(), "arckit-workspace-"));
  const wsTemplates = join(ws, ".arckit", "templates");
  mkdirSync(wsTemplates, { recursive: true });
  const wsTemplatesRel = listFilesRecursive(join(pluginRoot, "templates"));
  for (const rel of wsTemplatesRel) {
    const source = join(pluginRoot, "templates", rel);
    const destination = join(wsTemplates, rel);
    mkdirSync(dirname(destination), { recursive: true });
    if (staleFiles.includes(rel)) {
      writeFileSync(destination, readFileSync(source, "utf8").replace("## Intake Interview Questions\n", ""));
    } else {
      writeFileSync(destination, readFileSync(source, "utf8"));
    }
  }
  return ws;
}

function listFilesRecursive(root) {
  const out = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of readdirSync(current)) {
      const full = join(current, entry);
      if (statSync(full).isDirectory()) {
        stack.push(full);
      } else {
        out.push(relative(root, full));
      }
    }
  }
  return out;
}

test("fresh materialization produces no freshness note", () => {
  const pluginRoot = makePluginFixture();
  try {
    const ws = materializeWorkspace(pluginRoot);
    assert.equal(templateFreshnessNote(ws, join(pluginRoot, "templates")), "");
  } finally {
    rmSync(pluginRoot, { recursive: true, force: true });
  }
});

test("stale or missing template files produce a refresh warning", () => {
  const pluginRoot = makePluginFixture();
  try {
    const ws = materializeWorkspace(pluginRoot, { staleFiles: ["application-inventory-template.md"] });
    const note = templateFreshnessNote(ws, join(pluginRoot, "templates"));
    assert.ok(note, "expected a freshness note");
    assert.ok(note.includes(REFRESH_HINT), `note should tell the user to run \`${REFRESH_HINT}\`: ${note}`);
    assert.ok(
      note.includes("application-inventory-template.md"),
      "note should name the drifted template",
    );
  } finally {
    rmSync(pluginRoot, { recursive: true, force: true });
  }
});

test("missing .arckit/templates materialization produces a refresh warning", () => {
  const pluginRoot = makePluginFixture();
  try {
    const ws = mkdtempSync(join(tmpdir(), "arckit-workspace-"));
    try {
      const note = templateFreshnessNote(ws, join(pluginRoot, "templates"));
      assert.ok(note, "expected a freshness note");
      assert.ok(note.includes(REFRESH_HINT), `note should tell the user to run \`${REFRESH_HINT}\`: ${note}`);
    } finally {
      rmSync(ws, { recursive: true, force: true });
    }
  } finally {
    rmSync(pluginRoot, { recursive: true, force: true });
  }
});

test("workspace materialization with extra local files still reports no drift", () => {
  const pluginRoot = makePluginFixture();
  try {
    const ws = materializeWorkspace(pluginRoot);
    writeFileSync(join(ws, ".arckit", "templates", "my-local-template.md"), "# Local\n");
    const note = templateFreshnessNote(ws, join(pluginRoot, "templates"));
    assert.equal(note, "", "extra local templates must not count as drift");
  } finally {
    rmSync(pluginRoot, { recursive: true, force: true });
  }
});

test("missing plugin template tree (dev-repo layout) produces no note", () => {
  const barePluginRoot = mkdtempSync(join(tmpdir(), "arckit-bare-plugin-"));
  const ws = mkdtempSync(join(tmpdir(), "arckit-workspace-"));
  try {
    assert.equal(templateFreshnessNote(ws, join(barePluginRoot, "templates")), "");
  } finally {
    rmSync(barePluginRoot, { recursive: true, force: true });
    rmSync(ws, { recursive: true, force: true });
  }
});
