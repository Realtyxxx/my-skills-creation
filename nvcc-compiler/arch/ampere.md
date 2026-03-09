# Ampere

## SM Targets

- SM 80
- SM 86
- SM 87

## Notable features

- 3rd gen Tensor Cores with TF32 and BF16 support
- `cp.async` asynchronous copy support
- MIG support on A100

## Compile notes

- Ampere is a common default family for current server and workstation CUDA
  targets.
- If the user needs one binary for multiple Ampere subfamilies, use fatbin or
  multi-target cubin generation rather than duplicating commands here.

## See also

- `references/architectures.md` for the full comparison table and detection
  guidance.
