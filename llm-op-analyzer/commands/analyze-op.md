---
description: "Analyze a Deep Learning operator and generate comprehensive documentation"
argument-hint: "[FILE_PATH]"
allowed-tools: ["Read", "Write", "Edit", "Bash(mkdir:*)", "AskUserQuestion", "Skill"]
---

# Analyze Deep Learning Operator Command

This command invokes the `llm-op-analyzer` skill to analyze Deep Learning operators.

## Execution

Load and follow the main skill:

```!
# The skill content is loaded - follow its EXECUTION WORKFLOW
```

**Your task:** Execute the `llm-op-analyzer` skill's workflow to analyze the provided operator code and generate comprehensive documentation in `docs/op_description/{operator_name}.md`.

**Key points:**
1. Gather input (file path or inline code, tensor constraints, focus area)
2. Analyze code structure and trace shape transformations
3. Generate all 13 sections following the strict format
4. Save documentation in Chinese to the specified directory

Refer to the main SKILL.md for complete format specifications.
