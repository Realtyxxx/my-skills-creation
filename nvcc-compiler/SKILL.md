---
name: nvcc-compiler
description: "Use when the user asks to compile CUDA code, generate PTX/SASS/cubin, export IR, view assembly, analyze compilation output, or work with nvcc compiler options. Supports multi-architecture compilation and intermediate representation generation."
version: "1.0.0"
user-invocable: true
---

# NVCC Compiler Skill

This skill provides a unified interface for CUDA compilation and intermediate representation (IR) generation using the NVIDIA CUDA Compiler (nvcc).

## Core Capabilities

1. **Generate Intermediate Representations**
   - PTX (Parallel Thread Execution) - virtual intermediate code
   - SASS (Streaming ASSembler) - actual GPU assembly
   - cubin - binary code for specific GPU architectures
   - fatbin - multi-architecture binary

2. **Multi-Architecture Support**
   - Compile for multiple GPU architectures simultaneously
   - Support for Volta, Turing, Ampere, Ada, and Hopper architectures

3. **Compilation Analysis**
   - View register usage, shared memory usage
   - Analyze instruction counts and complexity
   - Extract compilation statistics

4. **Debugging and Optimization**
   - Keep intermediate files for inspection
   - Generate debug information
   - View detailed compilation logs

## Usage

When the user requests CUDA compilation or IR generation, follow these steps:

1. **Identify the compilation target**
   - What output format? (PTX, SASS, cubin, etc.)
   - Which GPU architecture(s)?
   - Any specific optimization flags?

2. **Use the compilation script**
   ```bash
   python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
     --input <source.cu> \
     --output-type <ptx|cubin|sass|all> \
     --arch <sm_XX> \
     [--options "additional nvcc flags"]
   ```

3. **Analyze the output**
   ```bash
   python ~/.claude/skills/nvcc-compiler/scripts/analyze_output.py \
     --file <output_file> \
     --type <ptx|cubin|sass>
   ```

## Common Scenarios

### Generate PTX for a kernel
```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type ptx \
  --arch sm_80
```

### Generate SASS assembly
```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type sass \
  --arch sm_80
```

### Multi-architecture compilation
```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type cubin \
  --arch sm_80,sm_86,sm_90
```

### View compilation statistics
```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type cubin \
  --arch sm_80 \
  --verbose
```

## Key NVCC Options

Refer to `references/nvcc_options.md` for detailed option descriptions.

**IR Generation:**
- `--ptx` - Generate PTX intermediate code
- `--cubin` - Generate cubin binary
- `--fatbin` - Generate multi-architecture fatbin

**Architecture Specification:**
- `-arch=compute_XX` - Virtual architecture
- `-code=sm_XX` - Real architecture
- `-gencode=arch=...,code=...` - Full architecture specification

**Compilation Control:**
- `-c` - Compile only, don't link
- `-dc` - Device code compilation
- `-keep` - Keep all intermediate files
- `-Xptxas=-v` - Verbose PTX assembler output

## Supported Architectures

See `references/architectures.md` for the complete list.

- SM 70, 72 (Volta)
- SM 75 (Turing)
- SM 80, 86, 87 (Ampere)
- SM 89 (Ada)
- SM 90, 92 (Hopper)

## Files and Scripts

- `scripts/compile_ir.py` - Main compilation script
- `scripts/analyze_output.py` - Output analysis script
- `references/nvcc_options.md` - NVCC option reference
- `references/architectures.md` - GPU architecture list
- `templates/compile_config.yaml` - Configuration template

## Agent Instructions

When this skill is invoked:

1. **Parse user request** - Identify what they want to compile and what output they need
2. **Check prerequisites** - Ensure nvcc is available, source file exists
3. **Determine architecture** - Use user-specified arch or detect from system
4. **Execute compilation** - Run the appropriate script with correct parameters
5. **Present results** - Show compilation output, any errors, and generated files
6. **Offer analysis** - If requested, analyze the generated IR/assembly

Always provide clear feedback about:
- What files were generated
- Where they are located
- Any compilation warnings or errors
- Key statistics (register usage, memory usage, etc.)
