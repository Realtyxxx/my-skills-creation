# Godbolt CUDA Analyzer - Quick Reference

## Activation

```
/godbolt-cuda-analyzer
```

## Core Function

```python
from godbolt_test import compile_and_analyze_asm

# PTX 模式（默认）
result = compile_and_analyze_asm(
    source_code="...",
    language="cuda",
    compiler_id="nvcc131",
    flags="-O3 -arch=sm_90 --ptx",
    output_mode="ptx"
)

# SASS 模式（自动切换到 cuclang）
result = compile_and_analyze_asm(
    source_code="...",
    output_mode="sass"
)
```

## Common Flags

| Flag | Description |
|------|-------------|
| `-O0` | No optimization |
| `-O3` | Aggressive optimization |
| `-arch=sm_80` | Ampere (A100) |
| `-arch=sm_86` | Ampere (RTX 30) |
| `-arch=sm_90` | Hopper (H100) |
| `-arch=sm_100` | Blackwell (B100/B200) - PTX only |
| `--ptx` | Generate PTX assembly |
| `--cubin` | Generate ELF binary (not readable; needs local `nvdisasm`) |
ZW|| `-use_fast_math` | Fast math library |
#YJ|

| Flag | Description |
|------|-------------|
| `-O0` | No optimization |
| `-O3` | Aggressive optimization |
| `-arch=sm_80` | Ampere (A100) |
| `-arch=sm_86` | Ampere (RTX 30) |
| `-arch=sm_90` | Hopper (H100) |
| `--ptx` | Generate PTX assembly |
| `--cubin` | Generate ELF binary (not readable; needs local `nvdisasm`) |
| `-use_fast_math` | Fast math library |

## Key PTX Instructions

### Memory
- `ld.global` - Load from global memory
- `st.global` - Store to global memory
- `ld.shared` - Load from shared memory
- `ld.local` ⚠️ - Register spill (slow!)

### Compute
- `add.f32` - Float addition
- `mul.f32` - Float multiplication
- `fma.rn.f32` - Fused multiply-add ✓
- `mad.lo.s32` - Integer multiply-add

### Control
- `setp` - Set predicate
- `@p bra` - Conditional branch
- `bar.sync` - Thread synchronization

## Key SASS Instructions

### Memory
- `LDG` / `LDG.E` - Global load
- `STG` / `STG.E` - Global store
- `LDS` / `STS` - Shared memory

### Compute
- `FADD` - FP32 add
- `FFMA` - FP32 fused multiply-add ✓
- `IMAD` - Integer multiply-add

### Control
- `ISETP` - Integer set predicate
- `BRA` - Branch
- `S2R` - Read special register
- `EXIT` - Thread exit

## Analysis Checklist

- [ ] Global memory access count
- [ ] Register spills (`ld.local`/`st.local`)
- [ ] Loop unrolling
- [ ] FMA instruction usage
- [ ] Branch count
- [ ] Shared memory usage

## Quick Commands

```bash
# Run examples
./run_test.sh examples/test1_basic_ptx.py
./run_test.sh examples/quick_test.py

# Check installation
ls -la ~/.claude/skills/specialized-tools__godbolt-cuda-analyzer/
```

## Example Usage

```
User: "Analyze this CUDA kernel for performance"

Agent will:
1. Compile via Godbolt API
2. Count key instructions
3. Detect optimizations
4. Identify bottlenecks
5. Provide recommendations
```

## Performance Patterns

✓ **Good**:
- Loop unrolling
- FMA instructions
- No register spills
- Coalesced memory access

⚠️ **Bad**:
- `ld.local`/`st.local` (spills)
- Excessive global loads
- Unfused mul+add
- Branch divergence
