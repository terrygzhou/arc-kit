#!/usr/bin/env bash
# Render and check ArcKit diagram sidecars (D2 corpus + archify showcase HTML).
#
#   ./scripts/diagrams.sh check    # validate every diagram sidecar (CI)
#   ./scripts/diagrams.sh render   # .d2 -> svg/ and archify .json -> .html
#
# Diagrams live under projects/<id>/diagrams/ — see docs/DIAGRAMS.md.
# Missing toolchains SKIP (with a notice), never fail the build.
#
# Env overrides: D2_BIN, ARCHIFY_BIN, ARCHIFY_QUALITY (default: standard)
set -u
cd "$(dirname "$0")/.."

CMD="${1:-check}"
D2_BIN="${D2_BIN:-$(command -v d2 || true)}"
ARCHIFY_BIN="${ARCHIFY_BIN:-$HOME/.codex/skills/archify/bin/archify.mjs}"
QUALITY="${ARCHIFY_QUALITY:-standard}"

d2_files=()
archify_specs=()
archify_htmls=()
while IFS= read -r f; do d2_files+=("$f"); done < <(find projects -type f -name '*.d2' 2>/dev/null | sort)
while IFS= read -r f; do archify_specs+=("$f"); done < <(find projects -type f \( -name '*.workflow.json' -o -name '*.architecture.json' -o -name '*.dataflow.json' -o -name '*.lifecycle.json' -o -name '*.sequence.json' \) 2>/dev/null | sort)
while IFS= read -r f; do archify_htmls+=("$f"); done < <(find projects -type f \( -name '*.workflow.html' -o -name '*.architecture.html' \) 2>/dev/null | sort)

FAILED=0

# --- D2 corpus ---------------------------------------------------------------
if [ ${#d2_files[@]} -gt 0 ]; then
  if [ -z "$D2_BIN" ]; then
    echo "SKIP  d2 not installed — ${#d2_files[@]} .d2 sidecar(s) not checked (install: https://d2lang.org/install)"
  elif [ "$CMD" = "render" ]; then
    for f in "${d2_files[@]}"; do
      out="$(dirname "$f")/svg/$(basename "${f%.d2}").svg"
      mkdir -p "$(dirname "$out")"
      if d2 "$f" "$out" >/dev/null 2>&1; then
        printf 'PASS  render %s\n' "$f"
      else
        printf 'FAIL  render %s\n' "$f"
        FAILED=1
      fi
    done
  else
    # Detect old pre-0.1-versioned builds: `d2 check <probe>` misreads
    # "check" as the input file and reports "failed to compile check".
    probe="$(mktemp -d)"
    old_build=0
    if d2 check "$probe/probe.d2" 2>&1 | grep -q 'failed to compile check'; then
      old_build=1
    fi
    rm -rf "$probe"
    if [ "$old_build" -eq 0 ]; then
      # modern d2 (0.1+ versioning): dedicated lint
      if d2 check "${d2_files[@]}" >/dev/null 2>&1; then
        printf 'PASS  d2 check (%s sidecar(s))\n' "${#d2_files[@]}"
      else
        printf 'FAIL  d2 check\n'
        FAILED=1
      fi
    else
      # older build: compile-only lint via throwaway render
      fail=0
      for f in "${d2_files[@]}"; do
        tmp="$(mktemp -d)"
        if ! d2 "$f" "$tmp/x.svg" >/dev/null 2>&1; then
          printf 'FAIL  %s (compile)\n' "$f"
          fail=1
        fi
        rm -rf "$tmp"
      done
      if [ "$fail" -eq 0 ]; then
        printf 'PASS  d2 compile (%s sidecar(s); pre-0.1 build, no `d2 check`)\n' "${#d2_files[@]}"
      else
        FAILED=1
      fi
    fi
  fi
fi

# --- archify showcase specs ---------------------------------------------------
if [ ${#archify_specs[@]} -gt 0 ]; then
  if [ ! -f "$ARCHIFY_BIN" ]; then
    echo "SKIP  archify skill not found at $ARCHIFY_BIN — ${#archify_specs[@]} spec(s) not checked"
  else
    for spec in "${archify_specs[@]}"; do
      type="$(node -p "require('$PWD/$spec').diagram_type || 'architecture'" 2>/dev/null || echo architecture)"
      if [ "$CMD" = "render" ]; then
        out="$(dirname "$spec")/${spec%.json}.html"
        if node "$ARCHIFY_BIN" deliver "$type" "$spec" "$out" --quality "$QUALITY" --json >/dev/null 2>&1; then
          printf 'PASS  deliver %s\n' "$spec"
        else
          printf 'FAIL  deliver %s (quality: %s)\n' "$spec" "$QUALITY"
          FAILED=1
        fi
      else
        if node "$ARCHIFY_BIN" validate "$type" "$spec" --quality "$QUALITY" --json >/dev/null 2>&1; then
          printf 'PASS  archify validate %s\n' "$spec"
        else
          printf 'FAIL  archify validate %s (quality: %s)\n' "$spec" "$QUALITY"
          FAILED=1
        fi
      fi
    done
  fi
fi

# --- archify delivered HTML artifacts ------------------------------------------
if [ ${#archify_htmls[@]} -gt 0 ] && [ "$CMD" = "check" ] && [ -f "$ARCHIFY_BIN" ]; then
  ok=1
  for html in "${archify_htmls[@]}"; do
    if ! node "$ARCHIFY_BIN" check "$html" --json >/dev/null 2>&1; then
      printf 'FAIL  archify check %s\n' "$html"
      ok=0
      FAILED=1
    fi
  done
  if [ "$ok" -eq 1 ]; then
    printf 'PASS  archify check (%s HTML artifact(s))\n' "${#archify_htmls[@]}"
  fi
fi

if [ "$FAILED" -eq 0 ]; then
  echo "All diagram checks passed."
fi
exit "$FAILED"
