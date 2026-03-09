# MY_SKILLS_CREATION

Personal workspace for creating and organizing skills.

## Overview

This repository is used to:

- draft and iterate skill definitions
- keep skill-related experiments in one place
- version control skill updates

## Current Structure

- `godbolt-cuda-analyzer/` - CUDA performance analysis skill
  (PTX/SASS via Godbolt)
- `llm-op-analyzer/` - LLM operator analysis skill (13-section documentation)
- `nvcc-blackwell-ir-extractor/` - Blackwell (sm_100/sm_100a) IR
  extraction and SASS dump utility
- `nvcc-compiler/` - Comprehensive CUDA compilation and IR generation
  skill (PTX/SASS/cubin/fatbin)

## Install Skills

Use the installer to link or copy all repository skills into Codex,
OpenCode, and Claude in one command.

```bash
python3 scripts/install_skills.py
```

Recommended during active skill development:

```bash
python3 scripts/install_skills.py --method symlink
```

Install only selected agents or skills:

```bash
python3 scripts/install_skills.py --agents codex claude --skills nvcc-compiler godbolt-cuda-analyzer
```

Preview changes without writing:

```bash
python3 scripts/install_skills.py --dry-run
```

Replace existing destinations by moving them into a timestamped backup
directory first:

```bash
python3 scripts/install_skills.py --force
```

Notes:

- Codex target path is auto-detected. If `~/.codex/skills` already
  exists, the script uses it for compatibility. Otherwise it defaults
  to `~/.agents/skills`, which matches the current Codex docs.
- OpenCode installs to `~/.config/opencode/skills`.
- Claude installs to `~/.claude/skills`.
- The script only installs top-level directories in this repo that contain `SKILL.md`.

## Next Steps

- add new skill directories and documentation
- commit changes in small, focused commits
- keep `README.md` updated as structure evolves
