#!/usr/bin/env node
/**
 * Detects stale or missing .arckit/templates/ materializations.
 *
 * Codex skills resolve their "default" templates from the workspace's
 * .arckit/templates/ directory (see each SKILL.md template-resolution
 * step). That directory is materialized by `arckit init --here --ai codex`
 * and is never re-synced automatically, so a workspace initialized with an
 * older ArcKit version silently runs skills against pre-interview templates
 * and skips the "## Intake Interview Questions" block.
 *
 * This module reports that drift (content-based, not mtime-based, because
 * plugin-cache mtimes are unreliable) so the hook can surface a refresh
 * hint in the session context.
 */

import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const MAX_DRIFT_EXAMPLES = 5;
const REFRESH_HINT = "arckit init --here --ai codex";

function listFilesRecursive(root) {
  const files = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop();
    let entries = [];
    try {
      entries = readdirSync(current);
    } catch {
      continue;
    }
    for (const entry of entries) {
      const entryPath = join(current, entry);
      let stats;
      try {
        stats = statSync(entryPath);
      } catch {
        continue;
      }
      if (stats.isDirectory()) {
        stack.push(entryPath);
      } else {
        files.push(entryPath);
      }
    }
  }
  return files;
}

function readTextSafe(path) {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return null;
  }
}

/**
 * Returns a human-readable warning when the workspace's .arckit/templates/
 * is missing, or when any template file shipped by the plugin is missing or
 * byte-different there; returns "" when nothing is out of date.
 *
 * @param {string} workspaceRoot - resolved workspace root containing .arckit/
 * @param {string} pluginTemplatesDir - templates/ dir of the installed plugin
 * @returns {string} "" or a warning paragraph
 */
export function templateFreshnessNote(workspaceRoot, pluginTemplatesDir) {
  if (!existsSync(pluginTemplatesDir)) {
    return "";
  }
  const wsTemplatesDir = join(workspaceRoot, ".arckit", "templates");
  if (!existsSync(wsTemplatesDir)) {
    return (
      `Template freshness: \`.arckit/templates/\` is missing from this workspace, ` +
      `so skill default templates cannot resolve and intake interview questions ` +
      `will not be asked. Run \`${REFRESH_HINT}\` to materialize the template tree.`
    );
  }

  const drifted = [];
  for (const pluginFile of listFilesRecursive(pluginTemplatesDir)) {
    const rel = relative(pluginTemplatesDir, pluginFile).replaceAll("\\", "/");
    const wsFile = join(wsTemplatesDir, rel);
    const pluginContent = readTextSafe(pluginFile);
    const wsContent = readTextSafe(wsFile);
    if (pluginContent === null) {
      continue;
    }
    if (wsContent === null || wsContent !== pluginContent) {
      drifted.push(rel);
    }
  }
  if (!drifted.length) {
    return "";
  }
  const examples = drifted
    .sort()
    .slice(0, MAX_DRIFT_EXAMPLES)
    .map((name) => `\`${name}\``)
    .join(", ");
  const extra = drifted.length > MAX_DRIFT_EXAMPLES ? ` (+${drifted.length - MAX_DRIFT_EXAMPLES} more)` : "";
  return (
    `Template freshness: \`.arckit/templates/\` is out of date with the ArcKit plugin ` +
    `templates (${drifted.length} file(s) missing or changed: ${examples}${extra}). ` +
    `Skills may be missing interview blocks such as "## Intake Interview Questions". ` +
    `Run \`${REFRESH_HINT}\` to refresh; keep customizations in \`.arckit/templates-custom/\`.`
  );
}
