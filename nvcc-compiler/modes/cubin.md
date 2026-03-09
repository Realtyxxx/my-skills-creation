# CUBIN Mode

## When to use

Use cubin mode when the user needs device-specific binary output for one or more
explicit SM targets, often for deployment checks or resource-usage inspection.

## Command

```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type cubin \
  --arch sm_80
```

## Key options

- `--output-type cubin`
- `--arch sm_XX` or comma-separated targets such as `sm_80,sm_86`
- `--verbose` to surface PTX assembler resource diagnostics

## Output notes

- CUBIN mode produces a `.cubin` artifact.
- With multiple targets, the script emits `-gencode=arch=compute_XX,code=sm_XX`
  pairs for each requested architecture.
- See `references/nvcc_options.md` for shared flag semantics.
