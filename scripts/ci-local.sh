#!/usr/bin/env bash
# Run the `lint-markdown` GitHub Actions workflow's checks locally, so you can
# commit freely and push to main only once everything is green.
#
#   ./scripts/ci-local.sh                 all checks (markdownlint + npm steps need network)
#   SKIP_NETWORK=1 ./scripts/ci-local.sh  offline: skip npx/npm steps
#
# Mirrors .github/workflows/lint-markdown.yml step-for-step (locally-runnable
# steps). If a checker is added to the workflow, add it here too.
set -u
cd "$(dirname "$0")/.."

SKIP_NETWORK="${SKIP_NETWORK:-0}"
FAILED=()

run() { # <label> <cmd...>
  local label="$1"
  shift
  if "$@"; then
    printf 'PASS  %s\n' "$label"
  else
    printf 'FAIL  %s\n' "$label"
    FAILED+=("$label")
  fi
}

# --- markdown style (npx fetches the package when absent: needs network) ---
if [ "$SKIP_NETWORK" = "1" ]; then
  echo "SKIP  markdownlint-cli2 (SKIP_NETWORK=1)"
else
  run "markdownlint-cli2" npx markdownlint-cli2 "**/*.md"
fi

# --- python checkers (check_references.py needs pyyaml: pip install pyyaml) ---
run "cross-reference linter"     python3 scripts/check_references.py
run "recipe sanity linter"       python3 scripts/check_recipes.py
run "doc-type collision check"   python3 scripts/check_doctype_collisions.py
run "shared-asset drift check"   python3 scripts/sync-shared-assets.py --check
run "guide-tree parity check"    python3 scripts/check-guide-parity.py --check
run "multi-instance parity"      python3 scripts/check-multi-instance-parity.py
run "doc-type registry refs"     python3 scripts/check-doc-type-registry.py
run "guide site-link check"      python3 scripts/check-guide-site-links.py
run "colon notation check"       python3 scripts/standardise-colon.py --check

# --- node registration / template tests (no network) ---
run "doc-types dual registration" node scripts/tests/test-doc-types-dual-registration.mjs
run "regime registration"         node scripts/tests/test-regime-registration.mjs
run "fde template consistency"    node scripts/tests/test-fde-templates.mjs

# --- npm validator + hook suites (npm ci needs network) ---
if [ "$SKIP_NETWORK" = "1" ]; then
  echo "SKIP  npm validator + hook suites (SKIP_NETWORK=1)"
else
  run "npm ci"            npm ci
  run "handoff validators" bash -c 'node tests/plugin/test_validate_handoff.mjs \
    && node tests/plugin/test_validate_grants_handoff.mjs \
    && node tests/plugin/test_validate_gov_reuse_handoff.mjs \
    && node tests/plugin/test_validate_tenders_handoff.mjs'
  run "plugin hook suites" node --test tests/plugin/*.test.mjs tests/plugin/test_hook_utils.mjs
fi

echo
if [ "${#FAILED[@]}" -eq 0 ]; then
  echo "All local CI checks passed — safe to push."
  exit 0
fi
echo "${#FAILED[@]} check(s) failed: ${FAILED[*]-}"
echo "Fix the above and re-run ./scripts/ci-local.sh before pushing."
exit 1
