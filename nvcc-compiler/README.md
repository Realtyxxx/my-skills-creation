# NVCC Compiler Skill

A comprehensive skill for CUDA compilation and intermediate representation (IR) generation using the NVIDIA CUDA Compiler (nvcc).

## Features

- **Generate PTX** - Parallel Thread Execution virtual intermediate code
- **Generate SASS** - Streaming ASSembler (actual GPU assembly)
- **Generate cubin** - Binary code for specific GPU architectures
- **Generate fatbin** - Multi-architecture binary
- **Multi-architecture support** - Compile for multiple GPU architectures simultaneously
- **Compilation analysis** - View register usage, shared memory, instruction counts
- **Auto-detection** - Automatically detect GPU architecture if not specified

## Quick Start

### Using the Skill

Simply ask Claude to compile CUDA code or generate IR:

```
"Generate PTX for this kernel"
"Compile this CUDA code for sm_80"
"Show me the SASS assembly for this kernel"
"Generate cubin for multiple architectures"
```

### Direct Script Usage

#### Generate PTX
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type ptx \
  --arch sm_80 \
  --verbose
```

#### Generate SASS Assembly
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type sass \
  --arch sm_80
```

#### Multi-Architecture Compilation
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type cubin \
  --arch sm_80,sm_86,sm_90
```

#### Analyze Output
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/analyze_output.py \
  --file kernel.ptx \
  --type ptx
```

## Directory Structure

```
nvcc-compiler/
├── SKILL.md                    # Skill configuration and documentation
├── README.md                   # This file
├── scripts/
│   ├── compile_ir.py          # Main compilation script
│   └── analyze_output.py      # Output analysis script
├── references/
│   ├── nvcc_options.md        # NVCC option reference
│   └── architectures.md       # GPU architecture list
└── templates/
    └── compile_config.yaml    # Configuration template
```

## Supported GPU Architectures

- **Volta** (SM 70, 72) - Tesla V100, Jetson Xavier
- **Turing** (SM 75) - RTX 2080 Ti, Titan RTX
- **Ampere** (SM 80, 86, 87) - A100, RTX 3090, Jetson Orin
- **Ada** (SM 89) - RTX 4090
- **Hopper** (SM 90, 92) - H100, H200

See `references/architectures.md` for complete details.

## Common Use Cases

### 1. Quick PTX Generation
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  -i kernel.cu -t ptx -v
```

### 2. View Register Usage
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  -i kernel.cu -t cubin -a sm_80 -v
```

### 3. Generate All Outputs
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  -i kernel.cu -t all -a sm_80 -k
```

### 4. Analyze PTX
```bash
python3 ~/.claude/skills/nvcc-compiler/scripts/analyze_output.py \
  -f kernel.ptx
```

## Configuration

Use the template in `templates/compile_config.yaml` to create custom compilation configurations.

## Requirements

- NVIDIA CUDA Toolkit (nvcc, cuobjdump)
- Python 3.6+
- NVIDIA GPU (for auto-detection, optional)

## Testing

A test kernel is provided at `/tmp/test_kernel.cu`:

```bash
# Generate PTX
python3 ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  -i /tmp/test_kernel.cu -t ptx -a sm_80 -v

# Analyze PTX
python3 ~/.claude/skills/nvcc-compiler/scripts/analyze_output.py \
  -f /tmp/test_kernel.ptx
```

## References

- `references/nvcc_options.md` - Complete NVCC option reference
- `references/architectures.md` - GPU architecture details and feature comparison

## Version

1.0.0

## Author

Created for Claude Code skill system
