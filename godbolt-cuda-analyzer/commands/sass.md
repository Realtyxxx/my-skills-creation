---
description: "Analyze CUDA code SASS assembly (real GPU machine code)"
argument-hint: "[FILE_PATH] [--arch sm_XX]"
allowed-tools: ["Read", "Bash(python3:*)"]
---

# SASS Analysis Command

Analyze CUDA code at the SASS (real GPU machine code) level using cuclang compiler.

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
    output_mode="sass",  # Automatically uses cuclang + binary mode
    flags="-O3 -arch=sm_90"  # Adjust arch if user specifies
)

if result["success"]:
    # Analyze SASS assembly
    # Count: LDG, STG, LDS, STS, FFMA, FADD, FMUL
    # Check: Control flow (BRA, ISETP), memory patterns
    # Report real hardware instruction usage
else:
    # Report compilation errors
    print(result["stderr"])
```

Focus on SASS-specific insights: actual instruction scheduling, register allocation, memory transaction patterns, and hardware-level optimizations.
