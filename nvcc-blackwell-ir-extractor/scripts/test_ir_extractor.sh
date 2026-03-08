#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$PWD"
EXTRACTOR_SCRIPT="scripts/compile_and_dump_ir.py"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/nvcc-ir-extractor-test.XXXXXX")"
FAILS=0

cleanup() {
    if command -v trash-put >/dev/null 2>&1; then
        trash-put -- "$TEST_ROOT" >/dev/null 2>&1 || true
    else
        echo "Leaving test workspace at $TEST_ROOT" >&2
    fi
}

trap cleanup EXIT

echo "=== Running Integration Test for IR Extractor ==="

make_fake_toolchain() {
    local workspace="$1"
    mkdir -p "$workspace/fakebin"

    cat << 'EOF' > "$workspace/fakebin/nvcc"
#!/usr/bin/env bash
set -euo pipefail

ALL_ARGS=("$@")

# We need to extract the output_dir and input file from the args to create fake artifacts
OUT_DIR=""
INPUT=""
OUTPUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep-dir=*)
      OUT_DIR="${1#*=}"
      shift
      ;;
    -c)
      INPUT="$2"
      shift 2
      ;;
    -o)
      OUTPUT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$OUT_DIR" ] || [ -z "$INPUT" ]; then
    echo "Fake nvcc failed: Missing --keep-dir or -c input" >&2
    exit 1
fi

echo "FAKE NVCC CALLED WITH: ${ALL_ARGS[*]}" >&2

BASE_NAME=$(basename "$INPUT" .cu)

# Simulate real nvcc behavior: without -o the object lands in CWD.
if [ -n "$OUTPUT" ]; then
    touch "$OUTPUT"
else
    touch "$BASE_NAME.o"
fi

# Create fake new artifacts
touch "$OUT_DIR/$BASE_NAME.ptx"

if [ "${FAKE_NVCC_EMIT_CUBIN_IN_CWD:-0}" = "1" ]; then
    # Simulate a toolkit dropping cubin in CWD despite --keep-dir.
    touch "$BASE_NAME.sm_100.cubin"
else
    touch "$OUT_DIR/$BASE_NAME.sm_100.cubin"
fi

exit 0
EOF
    chmod +x "$workspace/fakebin/nvcc"

    cat << 'EOF' > "$workspace/fakebin/cuobjdump"
#!/usr/bin/env bash
set -euo pipefail

# Check if it was called with -sass and a file
if [ "${1:-}" != "-sass" ] || [ -z "${2:-}" ]; then
    echo "Fake cuobjdump failed: Expected -sass <file>" >&2
    exit 1
fi

if [[ ! "$2" == *.cubin ]]; then
    echo "Fake cuobjdump failed: Expected .cubin file, got $2" >&2
    exit 1
fi

echo "FAKE SASS OUTPUT FOR $(basename "$2")"
exit 0
EOF
    chmod +x "$workspace/fakebin/cuobjdump"
}

record_failure() {
    echo "❌ $1"
    FAILS=$((FAILS + 1))
}

run_extractor() {
    local workspace="$1"
    shift

    (
        cd "$workspace"
        PATH="$workspace/fakebin:$PATH" "$@"
    )
}

test_main_flow() {
    local workspace="$TEST_ROOT/main-flow"
    local input_dir="$workspace/test with space"
    local input_file="$input_dir/my kernel.cu"
    local out_dir="$workspace/test_output"
    local log_file="$workspace/test_run.log"

    mkdir -p "$input_dir" "$out_dir"
    touch "$input_file"
    touch "$out_dir/my kernel.old.cubin" "$out_dir/my kernel2.cubin"
    touch "$workspace/my kernel.old.cubin" "$workspace/my kernel_old.cubin"
    make_fake_toolchain "$workspace"

    echo
    echo "--- Running Main Flow Test ---"
    if ! run_extractor "$workspace" python3 "$REPO_ROOT/$EXTRACTOR_SCRIPT" \
        --input "$input_file" \
        --output-dir "$out_dir" \
        --arch sm_100a \
        --options="-DFAKE='hello world'" > "$log_file" 2>&1; then
        record_failure "Main flow failed."
        sed -n '1,220p' "$log_file"
        return
    fi

    if [ ! -f "$out_dir/my kernel.o" ]; then
        record_failure "Missing expected file: $out_dir/my kernel.o"
    fi
    if [ -f "$workspace/my kernel.o" ]; then
        record_failure "Object file incorrectly landed in CWD when -o should direct it to output_dir."
    fi
    if [ ! -f "$out_dir/my kernel.sm_100.sass" ]; then
        record_failure "Missing expected generated SASS: $out_dir/my kernel.sm_100.sass"
    fi
    if [ -f "$out_dir/my kernel.old.sass" ] || [ -f "$out_dir/my kernel2.sass" ]; then
        record_failure "Extracted SASS for stale or non-matching cubins."
    fi
    if ! grep -q "Executing NVCC Command:" "$log_file"; then
        record_failure "NVCC command echo missing."
    fi
    if ! grep -q "'-DFAKE=hello world'" "$log_file" && ! grep -q "\"-DFAKE=hello world\"" "$log_file"; then
        record_failure "shlex quoting missing for extra options with spaces."
    fi
    if grep -q "my kernel.old.cubin" "$log_file"; then
        record_failure "Stale file 'my kernel.old.cubin' listed in artifacts."
    fi
    if grep -q "my kernel2.cubin" "$log_file"; then
        record_failure "Non-matching file 'my kernel2.cubin' listed in artifacts."
    fi
}

test_cwd_fallback() {
    local workspace="$TEST_ROOT/cwd-fallback"
    local input_file="$workspace/src.cu"
    local out_dir="$workspace/test_output"
    local log_file="$workspace/test_run.log"

    mkdir -p "$workspace" "$out_dir"
    touch "$input_file"
    touch "$out_dir/src.sm_100.cubin"
    make_fake_toolchain "$workspace"

    echo
    echo "--- Running CWD Fallback Test ---"
    if ! FAKE_NVCC_EMIT_CUBIN_IN_CWD=1 run_extractor "$workspace" \
        python3 "$REPO_ROOT/$EXTRACTOR_SCRIPT" \
        --input "$input_file" \
        --output-dir "$out_dir" > "$log_file" 2>&1; then
        record_failure "CWD fallback flow failed."
        sed -n '1,220p' "$log_file"
        return
    fi

    if [ ! -f "$workspace/src.sm_100.sass" ]; then
        record_failure "Missing SASS extracted from CWD fallback cubin."
    fi
    if grep -q "Warning: No .cubin files found" "$log_file"; then
        record_failure "Unexpected warning about missing cubins during CWD fallback."
    fi
}

test_cubin_named_output_dir() {
    local workspace="$TEST_ROOT/cubin-output-dir"
    local input_file="$workspace/src.cu"
    local out_dir="$workspace/out.cubin.dir"
    local log_file="$workspace/test_run.log"

    mkdir -p "$workspace" "$out_dir"
    touch "$input_file"
    make_fake_toolchain "$workspace"

    echo
    echo "--- Running .cubin Output Path Test ---"
    if ! run_extractor "$workspace" python3 "$REPO_ROOT/$EXTRACTOR_SCRIPT" \
        --input "$input_file" \
        --output-dir "$out_dir" > "$log_file" 2>&1; then
        record_failure "Extractor crashed when output_dir contained '.cubin'."
        sed -n '1,220p' "$log_file"
        return
    fi

    if [ ! -f "$out_dir/src.sm_100.sass" ]; then
        record_failure "SASS was not written next to the cubin inside an output_dir containing '.cubin'."
    fi
}

test_main_flow
test_cwd_fallback
test_cubin_named_output_dir

if [ "$FAILS" -eq 0 ]; then
    echo "✅ All tests passed! Bugs successfully fixed."
    exit 0
else
    echo "❌ $FAILS tests failed."
    exit 1
fi
