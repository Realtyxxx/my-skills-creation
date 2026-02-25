---
description: "Analyze CUDA code PTX assembly (virtual ISA)"
argument-hint: "[FILE_PATH] [--arch sm_XX]"
allowed-tools: ["Read", "Bash(python3:*)"]
---

# PTX Analysis Command

Analyze CUDA code at the PTX (virtual assembly) level using nvcc compiler.

## Execution

```python
import sys, os
SKILL_DIR = os.path.expanduser("~/.claude/skills/specialized-tools__godbolt-cuda-analyzer")
sys.path.insert(0, SKILL_DIR)
from godbolt_test import compile_and_analyze_asm

# Read source code if file path provided
# Otherwise use inline code from user message

result = compile_and_analyze_asm(
    source_code,
    output_mode="ptx",
    flags="-O3 -arch=sm_90 --ptx"  # Adjust arch if user specifies
)

if result["success"]:
    # Analyze PTX assembly
    # Count: ld.global, st.global, ld.shared, st.shared, fma.rn.f32
    # Warn: ld.local/st.local (register spills)
    # Report optimization patterns
else:
    # Report compilation errors
    print(result["stderr"])
```

Focus on PTX-specific patterns: memory coalescing, shared memory usage, FMA instructions, and register pressure.
