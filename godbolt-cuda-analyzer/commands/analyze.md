---
description: "Analyze CUDA code performance using Godbolt Compiler Explorer"
argument-hint: "[FILE_PATH] [--mode ptx|sass] [--arch sm_XX]"
allowed-tools: ["Read", "Bash(python3:*)"]
---

# Godbolt CUDA Analyzer Command

Analyze CUDA code at the assembly level using Godbolt Compiler Explorer API.

## Execution

You are now executing the `godbolt-cuda-analyzer` skill to analyze CUDA code performance.

### Input Handling

**If user provides a file path:**
- Use `Read` tool to load the CUDA source code

**If user provides inline code:**
- Use the code directly from the message

**Parse arguments:**
- `--mode ptx|sass`: Output mode (default: ptx)
  - `ptx`: PTX virtual assembly (via nvcc) - supports sm_75 ~ sm_100+
  - `sass`: Real GPU machine code (via cuclang) - **only supports sm_75 ~ sm_90**
HQ|- `--arch sm_XX`: Target architecture (default: sm_90)
#JQ|
WP|### Analysis Workflow
- `--mode ptx|sass`: Output mode (default: ptx)
  - `ptx`: PTX virtual assembly (via nvcc)
  - `sass`: Real GPU machine code (via cuclang)
- `--arch sm_XX`: Target architecture (default: sm_90)

### Analysis Workflow

Follow the skill's workflow:

1. **Compile via Godbolt API**:
   ```python
   import sys, os
   SKILL_DIR = os.path.expanduser("~/.claude/skills/specialized-tools__godbolt-cuda-analyzer")
   sys.path.insert(0, SKILL_DIR)
   from godbolt_test import compile_and_analyze_asm

   result = compile_and_analyze_asm(
       source_code,
       output_mode="ptx",  # or "sass"
       flags="-O3 -arch=sm_90 --ptx"
   )
   ```

2. **Analyze Assembly**:
   - Count key instructions (memory access, compute, control flow)
   - Identify optimization patterns (loop unrolling, FMA usage)
   - Detect performance issues (register spills, divergent branches)

3. **Provide Insights**:
   - Report instruction statistics
   - Highlight optimization opportunities
   - Suggest code improvements

### Key Analysis Points

**PTX Mode:**
- Memory: `ld.global`, `st.global`, `ld.shared`, `st.shared`
- Compute: `fma.rn.f32` (optimal), `add.f32`, `mul.f32`
- Warnings: `ld.local`/`st.local` (register spills)

**SASS Mode:**
- Memory: `LDG`, `STG`, `LDS`, `STS`
- Compute: `FFMA` (optimal), `FADD`, `FMUL`
- Control: `BRA`, `ISETP`, `FSETP`

Refer to the main SKILL.md for complete instruction reference and analysis guidelines.
