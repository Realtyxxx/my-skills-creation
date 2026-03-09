# SASS Mode

## When to use

Use SASS mode when the user wants hardware-specific assembly, instruction-level
inspection, or low-level performance debugging for a concrete GPU target.

## Command

```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type sass \
  --arch sm_80
```

## Key options

- `--output-type sass`
- `--arch sm_XX` for the specific GPU target
- `--verbose` when register usage or assembler diagnostics are needed

## Output notes

- SASS mode first generates a cubin and then extracts `.sass` with `cuobjdump`.
- This path is single-architecture because the script selects the first target.
- See `references/nvcc_options.md` for shared flag semantics.
