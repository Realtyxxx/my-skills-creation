---
name: nvcc-blackwell-ir-extractor
description: Use when compiling CUDA code for NVIDIA Blackwell (sm_100 or sm_100a), extracting PTX/cubin/SASS intermediate artifacts, dumping Blackwell IR, or checking generated assembly for architecture-specific instructions such as tcgen05, TMA, cp.async.bulk, cluster operations, WGMMA, setmaxnreg, cuobjdump, or ptxas verbose output.
---

# NVCC Blackwell IR Extractor Skill

You are an expert AI GPU Architecture Specialist focusing on the NVIDIA Blackwell architecture (`sm_100` and `sm_100a`).
This skill compiles CUDA code, retains every intermediate file, extracts SASS, and guides analysis of Blackwell-specific assembly features.

## When to Use

- User asks to compile CUDA code **specifically for Blackwell / sm_100 / sm_100a**.
- User wants to **extract or inspect** PTX, cubin, SASS, or fatbin artifacts.
- User wants to **check whether generated code uses** `tcgen05`, TMA, cluster ops, or other Blackwell-native instructions.
- User wants to **analyze register usage, spills, or shared memory** from `ptxas` verbose output.

## When NOT to Use

- User wants **generic CUDA compilation** without IR inspection — use standard `nvcc` instead.
- User targets a **non-Blackwell architecture** (e.g. sm_80, sm_89, sm_90) — this skill will reject it.
- User wants **runtime profiling** (Nsight Compute / `ncu`) — this skill only does static artifact analysis.
- **CUDA Toolkit is not installed** — the script will detect this and exit with install instructions.

## Quick Reference

| Item         | Value                                                               |
| ------------ | ------------------------------------------------------------------- |
| Input        | `.cu` source file                                                   |
| Output       | `.ptx`, `.cubin`, `.sass`, `.fatbin`, `.o`, and other intermediates |
| Default arch | `sm_100`                                                            |
| Allowed arch | `sm_100`, `sm_100a`                                                 |
| Output dir   | `./blackwell_ir_output` (configurable via `--output-dir`)           |
| Core flags   | `--save-temps`, `--keep-dir`, `-Xptxas=-v`, `-lineinfo`             |
| Dependencies | `nvcc`, `cuobjdump` (from CUDA Toolkit)                             |

## Agent Workflow

### 1. Locate the Script

The script is at `scripts/compile_and_dump_ir.py` relative to this skill's root directory.
Resolve the absolute path based on your framework's skill installation location before invoking.

### 2. Invoke the Script

```bash
python <resolved-skill-dir>/scripts/compile_and_dump_ir.py --input kernel.cu
```

Options:

- `--output-dir <dir>` — where to store intermediates (default: `./blackwell_ir_output`)
- `--arch sm_100a` — use architecture-specific features
- `--options '<extra nvcc flags>'` — additional flags (supports quoted args)

### 3. Read the Output

The script prints:

- The exact `nvcc` command executed (shell-safe — can be copy-pasted even with spaces in paths)
- `ptxas` verbose output (registers, spills, smem) from stderr
- A list of all generated artifacts with sizes

### 4. Analyze the Artifacts

Use file reading tools to inspect `.ptx` and `.sass` files in the output directory.

### 5. Identify Blackwell-Specific Features

Look for these in the assembly, **ordered by importance**:

#### Primary Targets (Blackwell-native)

- **`tcgen05.mma*`** (5th-gen Tensor Core): The **most important** Blackwell signature.
  7 new instructions, 2x–4x faster than Hopper's WGMMA:
  - `tcgen05.mma.cta_group::[1|2].kind::tf32` — TF32 tensor ops
  - `tcgen05.mma.cta_group::[1|2].kind::f16` — FP16/BF16 tensor ops
  - `tcgen05.mma.cta_group::[1|2].kind::i8` — INT8 tensor ops
  - `tcgen05.mma.cta_group::[1|2].kind::f8f6f4` — Mixed precision FP8/FP6/FP4
  - `tcgen05.mma.sp.*` — Structured sparsity variants

- **TMA** (Tensor Memory Accelerator): `cp.async.bulk` (PTX) or TMA-related memory instructions in SASS.

- **Cluster / DSMEM** (Distributed Shared Memory):
  - `cp.async.bulk.shared::cluster` — Cluster-level async copy
  - `barrier.cluster` — Cluster barrier synchronization

- **`setmaxnreg`** — Dynamic maximum register count control.

#### Secondary Targets (Hopper-compatible, may also appear)

- **WGMMA**: `wgmma.mma_async` — Hopper-era but still valid on Blackwell.
- **FP8 Types**: `e4m3`, `e5m2` low-precision tensor core operations.

#### Always Check

- **Register Usage & Spills**: From `ptxas` stderr output — register pressure, spill stores/loads, shared memory usage.

## Common Mistakes

- **Mistaking `wgmma` for Blackwell-exclusive**: `wgmma` is Hopper-era (sm_90). On Blackwell, the native instructions are `tcgen05.mma*`. If you only see `wgmma` and no `tcgen05`, the code is on a Hopper-compatible path, not Blackwell-native.
- **Assuming no `.cubin` means failure**: With `--save-temps`, nvcc may name cubin files as `{stem}.sm_100.cubin` or similar depending on version. The script uses precise stem matching (`{stem}[.<tag>...].cubin`) to find all variants without false positives.
- **Ignoring stderr**: `ptxas` resource usage info is printed to stderr, not stdout. The script captures and displays both.
- **Passing complex `--options` without quoting**: Use `--options '-I/path/to/include -DFOO=1'` with proper quoting. The script uses `shlex.split()` to handle this correctly.

## Failure Interpretation

| Symptom                                                   | Meaning                                            | Action                                                                                  |
| --------------------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `nvcc fatal : Unsupported gpu architecture 'compute_100'` | CUDA Toolkit too old for Blackwell                 | Upgrade to CUDA 12.8+                                                                   |
| `.ptx` generated but no `.cubin`                          | Compilation stopped at PTX stage                   | Check for `--ptx` in extra options; ensure `-c` is being used                           |
| No `tcgen05` instructions in SASS                         | Source code doesn't trigger Blackwell tensor cores | Not a failure; code may use scalar ops or Hopper-compatible path                        |
| Only `wgmma`, no `tcgen05`                                | Code compiled for Hopper-compatible path           | Try `sm_100a` instead of `sm_100`; check if source uses CUTLASS 4.x or newer intrinsics |
| `cuobjdump` not found                                     | CUDA Toolkit bin/ not in PATH                      | `export PATH=/usr/local/cuda/bin:$PATH`                                                 |
| High spill stores/loads in `ptxas` output                 | Register pressure too high                         | Reduce per-thread state, use `__launch_bounds__`, or consider `setmaxnreg`              |

## References

- [NVIDIA PTX ISA](https://docs.nvidia.com/cuda/parallel-thread-execution/) — Canonical instruction reference
- [CUTLASS Blackwell Functionality](https://docs.nvidia.com/cutlass/latest/media/docs/cpp/blackwell_functionality.html) — `tcgen05.mma` details
- [NVCC Compiler Driver](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/) — Compiler flags reference

## File Locations

- Script: `scripts/compile_and_dump_ir.py`
