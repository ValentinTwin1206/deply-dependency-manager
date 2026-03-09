#!/usr/bin/env bash
# -------------------------------------------------------------------
#  Build a standalone deply binary with Nuitka.
#
#  Works identically in CI (GitHub Actions) and locally:
#    .github/scripts/build_binary.sh
#
#  Environment variables (all optional):
#    OUTPUT_DIR   – where to write the binary   (default: dist/)
#    OUTPUT_NAME  – binary filename              (default: deply)
#    NUITKA_JOBS  – parallel compile jobs        (default: nproc)
# -------------------------------------------------------------------
set -e

# ── Defaults ────────────────────────────────────────────────────────
OUTPUT_DIR="${OUTPUT_DIR:-dist/}"
OUTPUT_NAME="${OUTPUT_NAME:-deply}"
NUITKA_JOBS="${NUITKA_JOBS:-$(nproc)}"
ENTRY_POINT="src/deply/cli.py"

# ── Helper ──────────────────────────────────────────────────────────
info()  { echo "▸ $*"; }
error() { echo "✖ $*" >&2; }

# In CI, emit GitHub Actions annotations
if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
  error() { echo "::error::$*" >&2; }
fi

# ── Pre-flight checks ──────────────────────────────────────────────
info "Checking build prerequisites..."

for cmd in gcc ccache python; do
  if ! command -v "$cmd" &>/dev/null; then
    error "$cmd not found on PATH"
    exit 1
  fi
done

info "================================================================="
info "Parsed following system utilities"
info "gcc    : $(gcc --version | head -1)"
info "ccache : $(ccache --version | head -1)"
info "python : $(python --version 2>&1)"
info "nuitka : $(python -m nuitka --version 2>&1 | head -1)"
printenv | grep -E '^CC|^CXX' || true

# ── Build ───────────────────────────────────────────────────────────
info "Building ${OUTPUT_NAME} → ${OUTPUT_DIR}"

python -m nuitka \
  --onefile \
  --jobs="$NUITKA_JOBS" \
  --assume-yes-for-downloads \
  --output-filename="$OUTPUT_NAME" \
  --output-dir="$OUTPUT_DIR" \
  --include-package=rich \
  --include-package=rich_click \
  --include-package=click \
  --include-package=deply \
  --include-package-data=deply \
  --include-distribution-metadata=deply \
  --include-distribution-metadata=rich \
  --include-distribution-metadata=rich-click \
  --include-distribution-metadata=click \
  "$ENTRY_POINT"

# ── Verify ──────────────────────────────────────────────────────────
BINARY="${OUTPUT_DIR%/}/${OUTPUT_NAME}"

if [[ ! -x "$BINARY" ]]; then
  error "Binary not found or not executable: $BINARY"
  exit 1
fi

info "Binary size: $(du -h "$BINARY" | cut -f1)"
info "Health check:"
"$BINARY" --help

info "Build complete ✔"
