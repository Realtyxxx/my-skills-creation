# Volta

## SM Targets

- SM 70
- SM 72

## Notable features

- 1st gen Tensor Cores
- Independent thread scheduling
- Improved unified memory behavior versus pre-Volta parts

## Compile notes

- Use Volta targets when the deployment environment is Tesla V100 or Jetson
  Xavier class hardware.
- PTX requests still route through `compute_70` or `compute_72` style targets in
  the script.

## See also

- `references/architectures.md` for the full comparison table and detection
  guidance.
