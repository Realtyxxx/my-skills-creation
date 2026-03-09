# Blackwell

## SM Targets

- SM 100
- SM 100a

## Notable features

- 5th gen Tensor Core instructions such as `tcgen05`
- Thread Block Clusters
- Tensor Memory Accelerator
- Distributed Shared Memory
- Architecture-specific `sm_100a` path for Blackwell-native features

## Compile notes

- Use Blackwell targets for B100 or B200 generation requests.
- Default to `sm_100` for general Blackwell compilation and reserve `sm_100a`
  for code paths that require architecture-specific features.
- If the user needs deep Blackwell IR inspection rather than general routed
  compilation guidance, hand off to the dedicated `nvcc-blackwell-ir-extractor`
  skill.

## See also

- `references/architectures.md` for the full comparison table and detection
  guidance.
