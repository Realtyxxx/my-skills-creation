# NVCC Compiler Options Reference

## Output Generation Options

### Intermediate Representation

| Option | Description |
|--------|-------------|
| `--ptx` | Generate PTX (Parallel Thread Execution) intermediate code |
| `--cubin` | Generate cubin (CUDA binary) for specific architecture |
| `--fatbin` | Generate fatbin containing code for multiple architectures |
| `--optix-ir` | Generate OptiX IR (for OptiX ray tracing) |

### Compilation Stages

| Option | Description |
|--------|-------------|
| `-c` | Compile and assemble, but do not link |
| `-dc` | Compile for separate compilation (device code) |
| `-dlink` | Link device code (used with `-dc`) |
| `-E` | Preprocess only |
| `-M` | Generate dependency file |

## Architecture Specification

### Virtual and Real Architectures

| Option | Description |
|--------|-------------|
| `-arch=compute_XX` | Specify virtual architecture (PTX version) |
| `-code=sm_XX` | Specify real architecture (GPU compute capability) |
| `-gencode=arch=...,code=...` | Full architecture specification for multi-targeting |

### Examples

```bash
# Single architecture
nvcc -arch=sm_80 kernel.cu

# Multiple architectures
nvcc -gencode=arch=compute_80,code=sm_80 \
     -gencode=arch=compute_86,code=sm_86 \
     kernel.cu

# PTX + multiple architectures
nvcc -gencode=arch=compute_80,code=compute_80 \
     -gencode=arch=compute_80,code=sm_80 \
     -gencode=arch=compute_86,code=sm_86 \
     kernel.cu
```

## Optimization Options

| Option | Description |
|--------|-------------|
| `-O0` | No optimization |
| `-O1` | Basic optimization |
| `-O2` | Moderate optimization |
| `-O3` | Aggressive optimization (default) |
| `-use_fast_math` | Use fast math library |
| `-ftz=true` | Flush denormal values to zero |
| `-prec-div=false` | Use fast division |
| `-prec-sqrt=false` | Use fast square root |

## Debug and Profiling

| Option | Description |
|--------|-------------|
| `-g` | Generate debug information for host code |
| `-G` | Generate debug information for device code |
| `-lineinfo` | Generate line number information |
| `--ptxas-options=-v` | Verbose PTX assembler output (shows register usage) |
| `-Xptxas=-v` | Short form of above |

## Intermediate File Management

| Option | Description |
|--------|-------------|
| `-keep` | Keep all intermediate files |
| `--keep-dir <dir>` | Directory for intermediate files |
| `--save-temps` | Save temporary files |
| `-clean-targets` | Clean up intermediate files |

## PTX Assembler Options

Pass options to PTX assembler using `-Xptxas`:

| Option | Description |
|--------|-------------|
| `-Xptxas=-v` | Verbose output (register/memory usage) |
| `-Xptxas=-O3` | PTX optimization level |
| `-Xptxas=--warn-on-spills` | Warn about register spills |
| `-Xptxas=--warn-on-local-memory-usage` | Warn about local memory usage |

## Compiler Options

Pass options to host compiler using `-Xcompiler`:

```bash
# Pass -Wall to host compiler
nvcc -Xcompiler=-Wall kernel.cu

# Multiple options
nvcc -Xcompiler=-Wall,-Wextra,-O3 kernel.cu
```

## Linking Options

| Option | Description |
|--------|-------------|
| `-l<library>` | Link with library |
| `-L<path>` | Add library search path |
| `--cudart=<type>` | CUDA runtime library (shared/static/none) |
| `-rdc=true` | Enable relocatable device code |

## Preprocessor Options

| Option | Description |
|--------|-------------|
| `-D<macro>` | Define preprocessor macro |
| `-U<macro>` | Undefine preprocessor macro |
| `-I<path>` | Add include search path |
| `--pre-include <file>` | Include file before processing |

## Miscellaneous

| Option | Description |
|--------|-------------|
| `--dryrun` | Show commands without executing |
| `--verbose` | Verbose output |
| `-time <file>` | Time individual compilation phases |
| `--resource-usage` | Show resource usage |

## Common Combinations

### Generate PTX with verbose output
```bash
nvcc --ptx -arch=compute_80 -Xptxas=-v kernel.cu
```

### Generate cubin for multiple architectures
```bash
nvcc --cubin \
  -gencode=arch=compute_80,code=sm_80 \
  -gencode=arch=compute_86,code=sm_86 \
  -gencode=arch=compute_90,code=sm_90 \
  kernel.cu
```

### Keep all intermediate files
```bash
nvcc -keep -arch=sm_80 kernel.cu
# Generates: kernel.cudafe1.cpp, kernel.ptx, kernel.cubin, etc.
```

### Debug build with line info
```bash
nvcc -G -lineinfo -arch=sm_80 kernel.cu
```

### Optimized build with fast math
```bash
nvcc -O3 -use_fast_math -arch=sm_80 kernel.cu
```

### Separate compilation
```bash
# Compile device code
nvcc -dc -arch=sm_80 kernel1.cu kernel2.cu

# Link device code
nvcc -dlink -arch=sm_80 kernel1.o kernel2.o -o device_link.o

# Final link
nvcc -arch=sm_80 kernel1.o kernel2.o device_link.o -o program
```
