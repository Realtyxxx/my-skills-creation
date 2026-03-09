# NVCC Compiler Skill

## What it does

`nvcc-compiler` helps route CUDA compilation requests to the right `nvcc`
workflow, whether the user needs PTX, SASS, cubin, fatbin, or follow-up output
analysis.

## Directory layout

```text
nvcc-compiler/
├── SKILL.md
├── README.md
├── modes/
│   ├── ptx.md
│   ├── sass.md
│   ├── cubin.md
│   └── fatbin.md
├── arch/
│   ├── volta.md
│   ├── turing.md
│   ├── ampere.md
│   ├── ada.md
│   ├── hopper.md
│   └── blackwell.md
├── references/
│   ├── nvcc_options.md
│   └── architectures.md
├── scripts/
│   ├── compile_ir.py
│   └── analyze_output.py
└── templates/
    └── compile_config.yaml
```

## Where to look for mode guidance

- Start with `modes/ptx.md`, `modes/sass.md`, `modes/cubin.md`, or
  `modes/fatbin.md` depending on the requested output artifact.
- Each mode page gives the exact `compile_ir.py` invocation and points back to
  `references/nvcc_options.md` for shared flag details.

## Where to look for architecture guidance

- Use `arch/` only when the user names a GPU family or the environment already
  identifies one.
- Use `references/architectures.md` for the shared comparison table, SM mapping,
  and detection commands.
- Route `sm_100` and `sm_100a` questions through `arch/blackwell.md`.

## Requirements

- NVIDIA CUDA Toolkit with `nvcc`
- `cuobjdump` when SASS extraction is required
- Python 3

## Testing

Run the documentation and script tests from the repository root:

```bash
python nvcc-compiler/tests/test_skill_docs.py -v
python nvcc-compiler/tests/test_compile_ir.py -v
python nvcc-compiler/tests/test_analyze_output.py -v
```
