---
name: nvcc-compiler
description: Use when the user asks to compile CUDA code, generate PTX, SASS, cubin, or fatbin output, inspect compiler-generated artifacts, or choose nvcc targets and options for a CUDA build.
version: "1.0.0"
user-invocable: true
---

# NVCC Compiler Skill

This skill helps with CUDA compilation requests that need `nvcc`, generated IR,
or architecture-aware output inspection.

## Routing Workflow

Load exactly one mode reference from `modes/`.
Load one architecture reference only when the user names a target architecture
or the system detects one.
Use `references/nvcc_options.md` and `references/architectures.md` only for
shared facts.

## What to Load

- `modes/ptx.md` for PTX output requests.
- `modes/sass.md` for disassembly or assembly inspection requests.
- `modes/cubin.md` for single-architecture binary output requests.
- `modes/fatbin.md` for multi-architecture packaging requests.
- `arch/volta.md`, `arch/turing.md`, `arch/ampere.md`, `arch/ada.md`,
  `arch/hopper.md`, or `arch/blackwell.md` only when the request or detection
  identifies that family.
- `references/nvcc_options.md` for shared flag meanings.
- `references/architectures.md` for shared SM and feature facts.

## Script Entry Points

- `scripts/compile_ir.py` compiles CUDA input into PTX, cubin, SASS, or fatbin
  outputs.
- `scripts/analyze_output.py` inspects generated PTX, cubin, or SASS output.

## Operating Notes

- Confirm the requested output type before running the compiler.
- Prefer explicit `--arch` values when the user supplies them; otherwise rely on
  detection or the script default.
- Keep top-level responses concise and pull detailed options or architecture
  facts from the routed documents instead of repeating them here.
