# PTX Mode

## When to use

Use PTX mode when the goal is to inspect virtual ISA, share a forward-compatible
intermediate representation, or debug compiler output before hardware-specific
assembly.

## Command

```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type ptx \
  --arch sm_80
```

## Key options

- `--output-type ptx`
- `--arch sm_XX` (the script converts the first target to `compute_XX` for PTX)
- `--options "-lineinfo"` or other extra nvcc flags when needed

## Output notes

- PTX mode produces a `.ptx` file.
- PTX requests typically use one target because the script keeps the first
  architecture for `compute_XX` emission.
- See `references/nvcc_options.md` for shared flag semantics.
