# FATBIN Mode

## When to use

Use fatbin mode when the user needs one packaged binary that carries code for
multiple SM targets.

## Command

```bash
python ~/.claude/skills/nvcc-compiler/scripts/compile_ir.py \
  --input kernel.cu \
  --output-type fatbin \
  --arch sm_80,sm_86,sm_90
```

## Key options

- `--output-type fatbin`
- `--arch` with one or more comma-separated SM targets
- `--options` for extra nvcc flags that apply across all generated targets

## Output notes

- FATBIN mode produces a `.fatbin` artifact.
- The script emits one `-gencode` pair per requested SM target.
- See `references/nvcc_options.md` for shared flag semantics.
