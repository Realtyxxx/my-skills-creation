# Godbolt CUDA Analyzer

A professional CUDA performance analysis skill that integrates Godbolt Compiler Explorer API to compile and analyze CUDA code at the assembly level - without requiring a local CUDA environment.

## Features

- **Remote Compilation**: Compile CUDA code via Godbolt API
- **PTX Analysis**: Parse and interpret PTX virtual assembly (via nvcc)
- **SASS Analysis**: Inspect real GPU machine code (via cuclang + binary mode)
- **Agent-Driven Pattern Recognition**: The agent inspects returned assembly to identify loop unrolling, register spills, memory patterns
- **Performance Insights**: Provide actionable optimization recommendations
- **Comparative Analysis**: Compare different optimization levels, GPU architectures, and PTX vs SASS

## Quick Start

### Basic Usage

```bash
# Activate the skill
/godbolt-cuda-analyzer
```

Then provide your CUDA code for analysis.

### Example

```cuda
__global__ void vectorAdd(float *a, float *b, float *c, int n) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    if (i < n) c[i] = a[i] + b[i];
}
```

The skill will:
1. Compile the code using NVCC 12.0
2. Generate PTX assembly
3. Analyze instruction patterns
4. Identify performance characteristics
5. Provide optimization recommendations

## Core Tool

The skill uses `godbolt_test.py` which provides:

```python
from godbolt_test import compile_and_analyze_asm

# PTX 模式（默认）
result = compile_and_analyze_asm(
    source_code: str,
    language: str = "cuda",
    compiler_id: str = "nvcc120",
    flags: str = "-O3 -arch=sm_90 --ptx",
    output_mode: str = "ptx"   # "ptx" 或 "sass"
)

# SASS 模式
result = compile_and_analyze_asm(source_code, output_mode="sass")
```

## Supported Architectures

- `sm_75` - Turing (RTX 20 series)
- `sm_80` - Ampere (A100)
- `sm_86` - Ampere (RTX 30 series)
- `sm_89` - Ada Lovelace (RTX 40 series)
- `sm_90` - Hopper (H100)

## Common Use Cases

### 1. Performance Analysis

Analyze memory access patterns, compute intensity, and identify bottlenecks.

### 2. Optimization Verification

Verify that compiler optimizations (loop unrolling, instruction fusion) are applied as expected.

### 3. Cross-Architecture Comparison

Compare code generation across different GPU architectures.

### 4. Teaching and Learning

Understand how CUDA code translates to assembly and learn optimization techniques.

## Examples

See the `examples/` directory for:
- `test1_basic_ptx.py` - Basic connectivity test
- `quick_test.py` - Quick test templates for various scenarios

## Running Tests

```bash
cd ~/.claude/skills/specialized-tools__godbolt-cuda-analyzer
./run_test.sh examples/test1_basic_ptx.py
./run_test.sh examples/quick_test.py
```

## Key Instructions Analyzed

### Memory Access
- `ld.global.*` - Global memory loads
- `st.global.*` - Global memory stores
- `ld.shared.*` - Shared memory loads
- `st.shared.*` - Shared memory stores
- `ld.local.*` / `st.local.*` - Register spills (performance warning!)

### Compute
- `add.f32` - Float addition
- `mul.f32` - Float multiplication
- `fma.rn.f32` - Fused multiply-add (optimal)
- `mad.lo.s32` - Integer multiply-add

### Control Flow
- `setp.*` - Predicate setting
- `@p bra` - Conditional branches
- `bra` - Unconditional jumps

### Synchronization
- `bar.sync` - Thread block synchronization

## Performance Patterns

The agent analyzes the returned PTX to identify:

✓ Loop unrolling
✓ Register allocation efficiency
✓ Instruction fusion (FMA)
✓ Memory coalescing
✓ Loop-invariant code motion

⚠️ Performance issues:
- Register spills
- Excessive global memory accesses
- Unfused operations
- Branch divergence

## Requirements

- Python 3.x
- `requests` library (for Godbolt API calls)

Install dependencies:
```bash
pip install requests
```

## Notes

- Godbolt API may have rate limits
- PTX is virtual assembly (via nvcc); SASS is real GPU machine code (via cuclang + binary mode)
- SASS mode automatically switches compiler to `cuclang2010-1291` and converts flags
- Different NVCC versions may optimize differently
- Always use UTF-8 encoding for Chinese output

## License

MIT License

## Author

Created for CUDA performance optimization and education.
