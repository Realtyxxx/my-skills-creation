# GPU Architecture Reference

## NVIDIA GPU Compute Capabilities

### Volta Architecture (2017)

| Compute Capability | Architecture | GPUs |
|-------------------|--------------|------|
| SM 70 | Volta | Tesla V100, Titan V |
| SM 72 | Volta | Jetson Xavier, Drive Xavier |

**Key Features:**
- Tensor Cores (1st gen)
- Independent thread scheduling
- Unified memory improvements
- 32 FP32 cores per SM

### Turing Architecture (2018)

| Compute Capability | Architecture | GPUs |
|-------------------|--------------|------|
| SM 75 | Turing | RTX 2060/2070/2080/2080 Ti, Titan RTX, Quadro RTX |

**Key Features:**
- RT Cores (ray tracing)
- Tensor Cores (2nd gen)
- Concurrent execution of FP32 and INT32
- 64 FP32 cores per SM

### Ampere Architecture (2020)

| Compute Capability | Architecture | GPUs |
|-------------------|--------------|------|
| SM 80 | Ampere | A100, A30 |
| SM 86 | Ampere | RTX 3060/3070/3080/3090, RTX A4000/A5000/A6000 |
| SM 87 | Ampere | Jetson Orin, Drive Orin |

**Key Features:**
- Tensor Cores (3rd gen) with TF32, BF16, FP64
- Async copy (cp.async)
- Multi-instance GPU (MIG) on A100
- 64 FP32 cores per SM (SM 80)
- 128 FP32 cores per SM (SM 86)

### Ada Lovelace Architecture (2022)

| Compute Capability | Architecture | GPUs |
|-------------------|--------------|------|
| SM 89 | Ada | RTX 4060/4070/4080/4090, RTX 6000 Ada |

**Key Features:**
- Tensor Cores (4th gen) with FP8
- RT Cores (3rd gen)
- Shader Execution Reordering (SER)
- Opacity Micromaps
- 128 FP32 cores per SM

### Hopper Architecture (2022)

| Compute Capability | Architecture | GPUs |
|-------------------|--------------|------|
| SM 90 | Hopper | H100, H200 |
| SM 90a | Hopper | H100 NVL |

**Key Features:**
- Tensor Cores (4th gen) with FP8, FP16, BF16, TF32
- Thread Block Clusters
- Tensor Memory Accelerator (TMA)
- Distributed Shared Memory
- Transformer Engine
- 128 FP32 cores per SM

## Architecture Selection Guide

### For Development and Testing
```bash
# Use compute_ for PTX (forward compatible)
nvcc --ptx -arch=compute_80 kernel.cu
```

### For Production Deployment
```bash
# Use sm_ for specific GPU (optimized)
nvcc -arch=sm_80 kernel.cu
```

### For Multi-GPU Support
```bash
# Generate code for multiple architectures
nvcc -gencode=arch=compute_80,code=sm_80 \
     -gencode=arch=compute_86,code=sm_86 \
     -gencode=arch=compute_90,code=sm_90 \
     kernel.cu
```

### For Maximum Compatibility
```bash
# Include PTX for future GPUs
nvcc -gencode=arch=compute_80,code=compute_80 \
     -gencode=arch=compute_80,code=sm_80 \
     -gencode=arch=compute_86,code=sm_86 \
     -gencode=arch=compute_90,code=sm_90 \
     kernel.cu
```

## Common Architecture Combinations

### Data Center (AI/HPC)
```bash
# A100 + H100
-gencode=arch=compute_80,code=sm_80 \
-gencode=arch=compute_90,code=sm_90
```

### Gaming/Workstation
```bash
# RTX 30/40 series
-gencode=arch=compute_86,code=sm_86 \
-gencode=arch=compute_89,code=sm_89
```

### Broad Compatibility
```bash
# Volta through Hopper
-gencode=arch=compute_70,code=sm_70 \
-gencode=arch=compute_75,code=sm_75 \
-gencode=arch=compute_80,code=sm_80 \
-gencode=arch=compute_86,code=sm_86 \
-gencode=arch=compute_89,code=sm_89 \
-gencode=arch=compute_90,code=sm_90
```

## Feature Support by Architecture

| Feature | Volta (70) | Turing (75) | Ampere (80/86) | Ada (89) | Hopper (90) |
|---------|-----------|-------------|----------------|----------|-------------|
| Tensor Cores | ✓ (1st) | ✓ (2nd) | ✓ (3rd) | ✓ (4th) | ✓ (4th) |
| RT Cores | ✗ | ✓ (1st) | ✓ (2nd) | ✓ (3rd) | ✗ |
| Async Copy | ✗ | ✗ | ✓ | ✓ | ✓ |
| TF32 | ✗ | ✗ | ✓ | ✓ | ✓ |
| BF16 | ✗ | ✗ | ✓ | ✓ | ✓ |
| FP8 | ✗ | ✗ | ✗ | ✓ | ✓ |
| Thread Block Clusters | ✗ | ✗ | ✗ | ✗ | ✓ |
| TMA | ✗ | ✗ | ✗ | ✗ | ✓ |

## Detecting GPU Architecture

### Using nvidia-smi
```bash
nvidia-smi --query-gpu=compute_cap --format=csv,noheader
# Output: 8.0 (for SM 80)
```

### Using CUDA Runtime
```cuda
int device;
cudaGetDevice(&device);

cudaDeviceProp prop;
cudaGetDeviceProperties(&prop, device);

printf("Compute Capability: %d.%d\n", prop.major, prop.minor);
// Output: Compute Capability: 8.0 (for SM 80)
```

### Using deviceQuery
```bash
# CUDA samples
/usr/local/cuda/samples/bin/x86_64/linux/release/deviceQuery
```

## Recommended Architectures by Use Case

### Deep Learning Training
- **Primary**: SM 90 (H100) - Best performance with FP8
- **Alternative**: SM 80 (A100) - Excellent for FP16/BF16

### Deep Learning Inference
- **Primary**: SM 89 (RTX 4090) - Good price/performance
- **Alternative**: SM 90 (H100) - Maximum throughput

### Scientific Computing
- **Primary**: SM 90 (H100) - FP64 Tensor Cores
- **Alternative**: SM 80 (A100) - Strong FP64 performance

### Graphics/Rendering
- **Primary**: SM 89 (RTX 4090) - RT Cores + DLSS 3
- **Alternative**: SM 86 (RTX 3090) - Good value

### Edge/Embedded
- **Primary**: SM 87 (Jetson Orin) - Power efficient
- **Alternative**: SM 72 (Jetson Xavier) - Lower cost
