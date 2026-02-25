# Installation Guide

## Skill Installation

This skill has been installed to:
```
~/.claude/skills/specialized-tools__godbolt-cuda-analyzer/
```

## Directory Structure

```
specialized-tools__godbolt-cuda-analyzer/
├── README.md              # User documentation
├── SKILL.md               # Skill definition for Claude Code
├── godbolt_test.py        # Core API wrapper
├── run_test.sh            # UTF-8 safe test runner
└── examples/              # Example scripts
    ├── test1_basic_ptx.py
    └── quick_test.py
```

## Dependencies

Install required Python packages:

```bash
pip install requests
```

## Usage

### Activate the Skill

In Claude Code, use:
```
/godbolt-cuda-analyzer
```

Or mention it in your request:
```
"Use godbolt-cuda-analyzer to analyze this CUDA kernel"
```

### Run Examples

```bash
cd ~/.claude/skills/specialized-tools__godbolt-cuda-analyzer
./run_test.sh examples/test1_basic_ptx.py
./run_test.sh examples/quick_test.py
```

## Verification

Check that the skill is loaded:
```bash
ls -la ~/.claude/skills/specialized-tools__godbolt-cuda-analyzer/
```

You should see:
- ✓ SKILL.md (main skill definition)
- ✓ README.md (documentation)
- ✓ godbolt_test.py (core tool)
- ✓ run_test.sh (test runner)
- ✓ examples/ (example scripts)

## Quick Test

Test the core functionality:

```python
cd ~/.claude/skills/specialized-tools__godbolt-cuda-analyzer
python3 -c "
from godbolt_test import compile_and_analyze_asm

code = '''
extern \"C\" __global__ void test(float *x) {
    x[threadIdx.x] = x[threadIdx.x] * 2.0f;
}
'''

result = compile_and_analyze_asm(code, flags='-O3 -arch=sm_90 --ptx')
print('Success!' if result['success'] else 'Failed')
print(f\"Assembly lines: {len(result['asm'].split(chr(10)))}\")
"
```

Expected output:
```
Success!
Assembly lines: 50+
```

## Troubleshooting

### Issue: Module not found

```bash
pip install requests
```

### Issue: Encoding errors

Use the provided `run_test.sh` wrapper:
```bash
./run_test.sh examples/test1_basic_ptx.py
```

### Issue: API timeout

Godbolt API may be slow or rate-limited. Wait and retry.

### Issue: Skill not recognized

Restart Claude Code or check that SKILL.md exists in the skill directory.

## Uninstallation

To remove the skill:
```bash
rm -rf ~/.claude/skills/specialized-tools__godbolt-cuda-analyzer
```

## Support

For issues or questions:
- Check README.md for usage examples
- Review SKILL.md for detailed instructions
- Run example scripts to verify functionality

## License

MIT License
