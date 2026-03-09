# GPU Architecture Reference

This page is the shared fact sheet for NVIDIA architecture families used by the
`nvcc-compiler` skill. Use the thin pages in `arch/` for family-specific compile
notes, and keep the detailed facts here.

## Architecture Cards

### Volta

| SM Targets   | Representative GPUs                              | Notable features                                                             |
| ------------ | ------------------------------------------------ | ---------------------------------------------------------------------------- |
| SM 70, SM 72 | Tesla V100, Titan V, Jetson Xavier, Drive Xavier | 1st gen Tensor Cores, independent thread scheduling, improved unified memory |

### Turing

| SM Targets | Representative GPUs                               | Notable features                                                            |
| ---------- | ------------------------------------------------- | --------------------------------------------------------------------------- |
| SM 75      | RTX 2060/2070/2080/2080 Ti, Titan RTX, Quadro RTX | 2nd gen Tensor Cores, 1st gen RT Cores, concurrent FP32 and INT32 execution |

### Ampere

| SM Targets          | Representative GPUs                                                                | Notable features                                                 |
| ------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| SM 80, SM 86, SM 87 | A100, A30, RTX 3060/3070/3080/3090, RTX A4000/A5000/A6000, Jetson Orin, Drive Orin | 3rd gen Tensor Cores, TF32/BF16 support, `cp.async`, MIG on A100 |

### Ada

| SM Targets | Representative GPUs                   | Notable features                                                             |
| ---------- | ------------------------------------- | ---------------------------------------------------------------------------- |
| SM 89      | RTX 4060/4070/4080/4090, RTX 6000 Ada | 4th gen Tensor Cores with FP8, 3rd gen RT Cores, Shader Execution Reordering |

### Hopper

| SM Targets    | Representative GPUs  | Notable features                                                                                                      |
| ------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| SM 90, SM 90a | H100, H100 NVL, H200 | 4th gen Tensor Cores, Thread Block Clusters, Tensor Memory Accelerator, Distributed Shared Memory, Transformer Engine |

### Blackwell

| SM Targets      | Representative GPUs | Notable features                                                                                                    |
| --------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| SM 100, SM 100a | B100, B200          | 5th gen Tensor Core instructions such as `tcgen05`, TMA and cluster workflows, architecture-specific `sm_100a` path |

## Feature Comparison

| Feature                   | Volta   | Turing  | Ampere  | Ada     | Hopper  | Blackwell           |
| ------------------------- | ------- | ------- | ------- | ------- | ------- | ------------------- |
| Tensor Cores              | 1st gen | 2nd gen | 3rd gen | 4th gen | 4th gen | 5th gen (`tcgen05`) |
| RT Cores                  | No      | 1st gen | 2nd gen | 3rd gen | No      | No                  |
| Async copy (`cp.async`)   | No      | No      | Yes     | Yes     | Yes     | Yes                 |
| TF32                      | No      | No      | Yes     | Yes     | Yes     | Yes                 |
| BF16                      | No      | No      | Yes     | Yes     | Yes     | Yes                 |
| FP8                       | No      | No      | No      | Yes     | Yes     | Yes                 |
| Thread Block Clusters     | No      | No      | No      | No      | Yes     | Yes                 |
| Tensor Memory Accelerator | No      | No      | No      | No      | Yes     | Yes                 |

## Detection

### `nvidia-smi`

```bash
nvidia-smi --query-gpu=compute_cap --format=csv,noheader
# Example output: 8.0
```

Map the reported compute capability to an SM target such as `8.0 -> sm_80` or
`10.0 -> sm_100`.

### CUDA Runtime

```cuda
int device;
cudaGetDevice(&device);

cudaDeviceProp prop;
cudaGetDeviceProperties(&prop, device);

printf("Compute Capability: %d.%d\n", prop.major, prop.minor);
```

### CUDA Samples

```bash
/usr/local/cuda/samples/bin/x86_64/linux/release/deviceQuery
```

## Selection Patterns

### Development and testing

- Prefer PTX generation with a single `compute_XX` target when the goal is to
  inspect virtual ISA or keep forward-compatible output.
- Keep the architecture family thin pages focused on family-specific caveats,
  then return here for cross-family comparisons.

### Multi-GPU support

- Use cubin or fatbin generation with multiple `sm_XX` targets when deployment
  spans more than one GPU family.
- For multi-target cubin or fatbin requests, follow the script pattern of one
  `-gencode=arch=compute_XX,code=sm_XX` pair per requested architecture.

### Broad compatibility

- Choose a broad compatibility bundle when the user needs coverage across
  multiple deployed generations rather than peak tuning for one device.
- A common example is combining Volta, Turing, Ampere, Ada, Hopper, or
  Blackwell targets in separate `-gencode` pairs so each deployed GPU gets a
  matching `sm_XX` artifact.

## Notes

- PTX generation usually targets `compute_XX`, while cubin, fatbin, and SASS
  workflows typically target one or more `sm_XX` values.
- Prefer the thin architecture docs in `arch/` when the user names a family or
  when system detection already tells you which family to target.
- Keep family facts centralized here so `SKILL.md`, `README.md`, and the thin
  `arch/*.md` pages do not drift.
- Use `sm_100a` only when the target environment or source path needs
  architecture-specific Blackwell features.
