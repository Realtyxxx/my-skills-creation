# Hopper

## SM Targets

- SM 90
- SM 90a

## Notable features

- 4th gen Tensor Cores
- Thread Block Clusters
- Tensor Memory Accelerator
- Distributed Shared Memory
- Transformer Engine

## Compile notes

- Use Hopper targets for H100, H100 NVL, or H200 generation requests.
- Keep SM 90 and SM 90a distinctions explicit when the target environment cares
  about architecture-specific instructions.

## See also

- `references/architectures.md` for the full comparison table and detection
  guidance.
