# MY_SKILLS_CREATION

A collection of reusable skills for CUDA tooling, operator analysis, persistent memory, and structured knowledge reuse.

## Overview

This repository is a skills workspace: each directory captures a reusable capability distilled from real tasks, repeated workflows, and practical debugging work.

The goal is not just to store notes, but to package proven ways of working into skills that are easier to discover, reuse, and improve over time.

## Skills

### `agents-server-memory/`
Structured persistent memory for AI agents, with project-scoped knowledge, trace history, tagging, search, and maintenance commands.

**Value:** Helps turn short-lived session context into reusable long-term knowledge, reducing repeated explanation and making multi-session work more consistent.

### `godbolt-cuda-analyzer/`
Remote CUDA PTX/SASS analysis through Godbolt Compiler Explorer, focused on instruction inspection, optimization detection, and performance reasoning without requiring a local CUDA environment.

**Value:** Makes low-level CUDA performance analysis much more accessible, especially when you want fast feedback on generated assembly or optimization behavior.

### `llm-op-analyzer/`
A strict structured prompt for breaking deep learning operators into implementation-ready engineering documentation, including diagrams, shape tracing, math, memory access, and debugging probes.

**Value:** Turns complex operators into readable engineering blueprints, which is useful for implementation review, debugging, onboarding, and design communication.

### `nvcc-blackwell-ir-extractor/`
A specialized Blackwell-focused compilation utility for extracting PTX, cubin, SASS, and other intermediate artifacts when targeting `sm_100` / `sm_100a`.

**Value:** Shortens the path from CUDA source to Blackwell-specific IR inspection, making it easier to verify whether codegen is actually using the architecture features you care about.

### `nvcc-compiler/`
A routing-oriented CUDA compilation skill that helps choose the right `nvcc` workflow for PTX, SASS, cubin, fatbin, and architecture-aware output inspection.

**Value:** Reduces friction in CUDA compilation tasks by turning scattered compiler knowledge into a reusable, architecture-aware workflow.

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

## Notes

- Codex target path is auto-detected. If `~/.codex/skills` already
  exists, the script uses it for compatibility. Otherwise it defaults
  to `~/.agents/skills`, which matches the current Codex docs.
- OpenCode installs to `~/.config/opencode/skills`.
- Claude installs to `~/.claude/skills`.
- The script only installs top-level directories in this repo that contain `SKILL.md`.

## Next Steps

- add new skill directories and documentation
- continue refining skill descriptions and examples
- commit changes in small, focused commits
- keep `README.md` updated as the skill set evolves
