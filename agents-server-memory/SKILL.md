---
name: agents-memory
description: Structured persistent memory system for AI agents. Provides project-scoped knowledge bases, process traces, smart auto-loading, and powerful search across sessions. Enhanced with tagging, time-based retention, and intelligent consolidation.
invocation: |
  This skill can be invoked in multiple ways:

  1. Via Skill tool: /agents-memory [command] [args]
     Examples:
     - /agents-memory status
     - /agents-memory read
     - /agents-memory search nginx
     - /agents-memory save
     - /agents-memory tag list

  2. Via natural language:
     - "MEMORY.READ" or "read memory"
     - "MEMORY.SEARCH nginx" or "search memory for nginx"
     - "MEMORY.STATUS" or "check memory status"
     - "MEMORY.SAVE" or "save to memory"

  When invoked, parse the command and execute the corresponding operation immediately.

  Command format: [command] [subcommand] [args]
  - status: Show memory status
  - read [trace|full]: Read memory
  - search <keyword> [--type=X] [--scope=X]: Search memory
  - save: Save current session
  - tag [list|show|stats]: Tag operations
---

# AGENTS.MEMORY - Persistent Memory for AI Agents

## Skill Invocation

This skill supports command-style invocation. When user says:
- `/agents-memory status` → Execute MEMORY.STATUS
- `/agents-memory read` → Execute MEMORY.READ
- `/agents-memory search nginx` → Execute MEMORY.SEARCH
- `/agents-memory save` → Execute MEMORY.SAVE
- `/agents-memory tag list` → Execute MEMORY.TAG list

Parse the arguments and execute the corresponding operation.

## Command Parser

When this skill is invoked with arguments:
1. Parse the command: `status`, `read`, `search`, `save`, `tag`
2. Parse subcommands and options
3. Execute the operation using available tools (Read, Grep, Write, Bash)
4. Format and present results to user

## Overview

A structured memory system that helps AI agents maintain context across sessions without polluting conversations. Provides project-scoped knowledge bases, process traces, and intelligent auto-loading based on context.

## Core Concepts

**Two Memory Types:**
- `knowledge.md` - Verified facts, runbooks, decisions (reusable truth)
- `trace.md` - Process history, session logs (what happened)

**Three Scopes:**
- `_global/` - Cross-project knowledge
- `_home/` - Home directory work
- `<slug>/` - Project-specific (auto-derived from working directory)

**Design Philosophy:**
- Append-only (never overwrites)
- Explicit control (no auto-save)
- Smart auto-loading (context-aware)
- Searchable and discoverable
- Time-aware retention

## Directory Structure

```
~/AGENTS.MEMORY/
  _global/
    knowledge.md          # Cross-project knowledge
    trace.md              # Global process history
    .backups/             # Timestamped backups
  _home/
    knowledge.md
    trace.md
    .backups/
  <slug>/                 # e.g., projects__myapp
    knowledge.md
    trace.md
    trace_archive.md      # 31-90 day old traces
    .backups/
  attic/                  # Cold archive (never auto-loaded)
  .index/
    tags.json             # Tag index for fast search
    projects.json         # Project metadata
```

## Slug Derivation

Projects are automatically identified by converting working directory to slug:
- `/home/user/projects/myapp` → `projects__myapp`
- `/home/user/` → `_home`
- Replace `/` with `__` after removing home prefix

## Auto-Loading Logic

Memory auto-loads (read-only) when:

1. **Project Scope Match** (strong)
   - Project has existing knowledge.md
   - Loads: _global/knowledge.md + <slug>/knowledge.md

2. **Recent Activity Match** (weak)
   - Trace has entries within last 14 days
   - User doing operational work (deploy, debug, fix, incident)
   - Loads: knowledge + recent trace portion

3. **Semantic Match** (medium)
   - User query matches knowledge tags
   - Example: "nginx ssl issue" → loads #nginx #ssl entries
   - Limit to top 3 most relevant

4. **Continuation Signal** (strong)
   - User says "continue", "as we discussed", "like last time"
   - Trace has entries within last 14 days
   - Loads: most recent trace session

**Never auto-saves** - all writes require explicit user confirmation.

## Commands

### MEMORY.READ
Read and summarize current project's memory.

**Usage:**
```
MEMORY.READ                    # Read knowledge only
MEMORY.READ trace              # Include trace
MEMORY.READ full               # Include everything
MEMORY.READ --raw              # Show raw content
MEMORY.READ --since=2026-01-01 # Filter by date
MEMORY.READ <slug>             # Read specific project
```

**Behavior:**
- Automatically follows continuation files (knowledge_2.md, etc.)
- Summarizes unless --raw specified
- Never loads attic unless explicitly requested

### MEMORY.SEARCH
Search across all memory files.

**Usage:**
```
MEMORY.SEARCH <keyword>                    # Search all
MEMORY.SEARCH <keyword> --scope=global     # Search _global only
MEMORY.SEARCH <keyword> --scope=<slug>     # Search specific project
MEMORY.SEARCH <keyword> --type=knowledge   # Knowledge only
MEMORY.SEARCH <keyword> --type=trace       # Trace only
MEMORY.SEARCH <keyword> --since=2026-01-01 # After date
MEMORY.SEARCH #deployment                  # Search by tag
MEMORY.SEARCH <regex> --regex              # Use regex
MEMORY.SEARCH <keyword> --all              # Show all matches (not just top 10)
```

**Output:**
- Top 10 matches by relevance (exact > tag > content)
- Shows: file path, date, tags, matched line with context
- Suggests related tags

### MEMORY.TAG
Manage and search by tags.

**Usage:**
```
MEMORY.TAG list                    # List all tags with counts
MEMORY.TAG list --project=<slug>   # Project-specific tags
MEMORY.TAG show #deployment        # Show all entries with tag
MEMORY.TAG stats                   # Tag statistics and trends
```

**Tag Format:**
- Use #hashtag format in entry content
- Common tags: #deployment #bug-fix #config #performance #security #incident
- Tech tags: #nginx #docker #kubernetes #postgres #redis
- Severity: #critical #high #medium #low

### MEMORY.SUMMARIZE_AND_ASK_SAVE
Propose saving current session to memory.

**Behavior:**
1. Summarizes session into knowledge and/or trace candidates
2. Suggests relevant tags based on content
3. Assesses confidence: HIGH / MEDIUM / LOW
4. Asks: "[CONFIDENCE] Save to memory? Location: project/global? Type: knowledge/trace? Tags: #tag1 #tag2. Or skip?"
5. Only saves after explicit confirmation

**Confidence Levels:**
- HIGH: User confirmed success + reusable pattern
- MEDIUM: Partial success + lessons learned
- LOW: Exploratory work + uncertain outcome

**Adaptive:**
- If user declines HIGH confidence save, asks if should stop suggesting for this task type
- Reduces frequency after 3 consecutive declines
- Increases sensitivity if user accepts LOW confidence saves

### MEMORY.STATUS
Show current project's memory status.

**Output:**
```
Current: projects__myapp
Global knowledge: 45 lines
Project knowledge: 123 lines (+ knowledge_2.md: 67 lines)
Trace: 8 recent (0-14d), 3 medium (15-30d), 0 old
Archive: 15 entries (31-90d)
Top tags: #deployment(5) #nginx(3) #ssl(2) #bug-fix(2)
Suggestions: Consider consolidating knowledge files (190 total lines)
```

**Checks:**
- File existence and line counts
- Trace age distribution
- Archive status
- Top tags
- Suggests: consolidate, archive, cleanup

### MEMORY.CONSOLIDATE
Merge fragmented files and remove duplicates.

**Usage:**
```
MEMORY.CONSOLIDATE                  # Current project
MEMORY.CONSOLIDATE --project=<slug> # Specific project
MEMORY.CONSOLIDATE --global         # Global memory
MEMORY.CONSOLIDATE --dry-run        # Preview only
```

**Behavior:**
- Merges knowledge_2.md, knowledge_3.md → knowledge.md
- Removes duplicate entries (same date + conclusion)
- Sorts by date (newest first)
- Creates backup before consolidation
- Requires confirmation

### MEMORY.ARCHIVE
Move old trace entries to archive.

**Usage:**
```
MEMORY.ARCHIVE                   # Current project
MEMORY.ARCHIVE --all             # All projects
MEMORY.ARCHIVE --threshold=60    # Custom day threshold
MEMORY.ARCHIVE --to-attic        # Move ancient entries to attic
```

**Retention Policy:**
- Recent (0-14d): Keep in trace.md, auto-load for ops tasks
- Medium (15-30d): Keep in trace.md, load on keyword match
- Old (31-90d): Move to trace_archive.md, searchable but not auto-loaded
- Ancient (>90d): Suggest moving to attic

### MEMORY.STATS
Show memory usage across all projects.

**Output:**
```
Total projects: 12
Total knowledge entries: 234
Total trace entries: 567
Most active: projects__api (45), projects__web (32)
Stale projects: projects__old-tool (last: 2025-10-15)
Top global tags: #deployment(23) #bug-fix(18) #config(15)
Storage: 2.3 MB (knowledge: 0.8 MB, trace: 1.5 MB)
Suggestions:
  - Archive traces in 3 projects
  - Move 2 stale projects to attic
```

### MEMORY.CLEANUP
Interactive cleanup wizard.

**Usage:**
```
MEMORY.CLEANUP                  # Interactive mode
MEMORY.CLEANUP --auto           # Auto with safe defaults
MEMORY.CLEANUP --project=<slug> # Specific project
```

**Actions:**
- Remove duplicate entries
- Archive old traces
- Consolidate fragmented files
- Verify cross-references
- Move stale projects to attic

### MEMORY.GRAPH
Show relationships between entries.

**Usage:**
```
MEMORY.GRAPH                # Current project
MEMORY.GRAPH --all          # All projects
MEMORY.GRAPH --tag=#deploy  # Entries related to tag
```

**Output:**
- ASCII tree or list format
- Shows: entry → references → related entries
- Highlights: strong connections (3+ refs), weak (1 ref)

## Entry Formats

### Knowledge Entry
```markdown
Date: 2026-03-03
Tags: #nginx #ssl #deployment
Conclusion: Nginx SSL requires both cert and key in /etc/nginx/ssl/
Details:
  - Command: sudo cp cert.pem key.pem /etc/nginx/ssl/
  - Config: ssl_certificate /etc/nginx/ssl/cert.pem;
  - Restart: sudo systemctl restart nginx
Verification:
  - Tested on production server
  - SSL Labs grade A+
Related: _global/knowledge.md:2026-02-15
```

### Trace Entry
```markdown
Date: 2026-03-03
Tags: #deployment #incident
Goal: Fix SSL certificate expiration on production
Actions:
  - Generated new cert with Let's Encrypt
  - Copied to /etc/nginx/ssl/
  - Restarted nginx service
Outcome: SSL working, monitoring for 24h
Notes: Set calendar reminder for renewal in 80 days
```

### Continuation Marker
```markdown
---
→ Continued in knowledge_2.md
---
```

### Cross-Reference
```markdown
Related: _global/knowledge.md:2026-02-15
Related: projects__api/knowledge.md#deployment
See: https://docs.example.com/api
```

## File Size Management

- Each file limited to 200 lines
- When exceeded: create knowledge_2.md with continuation marker
- MEMORY.READ automatically follows continuations
- When total > 500 lines: suggest MEMORY.CONSOLIDATE
- When trace.md > 300 lines: suggest MEMORY.ARCHIVE

## Backup System

- Every write creates timestamped backup in .backups/
- Format: knowledge.md.2026-03-03T14-30-00.bak
- Keep last 10 backups per file
- Auto-cleanup backups older than 90 days
- MEMORY.ROLLBACK to restore (requires confirmation)

## Save Criteria

Propose saving when:

**HIGH confidence (propose immediately):**
- User confirms success or satisfaction
- Reusable runbook or verified config produced
- Recurring pitfall with clear resolution identified
- Key decision with reasoning finalized

**MEDIUM confidence (propose if user seems satisfied):**
- Partial success with valuable lessons
- Workaround found but root cause unclear
- Useful debugging process documented

**LOW confidence (only if user asks):**
- Exploratory work with uncertain outcome
- Temporary solution that might change
- Information that might be outdated soon

## Hard Constraints

- Never auto-save
- Never auto-load attic
- Never overwrite files (append-only except consolidation)
- Only store confirmed facts in knowledge
- Unconfirmed/exploratory info goes to trace
- All destructive operations require confirmation
- Keep files under 200 lines (create continuations)
- Never infer save intent without user confirmation

## Migration from Original

If upgrading from original AGENTS.MEMORY:
1. Existing files work as-is (backward compatible)
2. Tags are optional (add gradually)
3. New commands are additive (old commands still work)
4. Auto-trigger logic enhanced but not breaking
5. Run MEMORY.STATUS to see new features

## Usage Examples

**Starting a new project:**
```
# Memory auto-loads if project has existing knowledge
# Otherwise, work normally and save when done
MEMORY.SUMMARIZE_AND_ASK_SAVE
```

**Searching for past solutions:**
```
MEMORY.SEARCH "nginx ssl error"
MEMORY.SEARCH #deployment --type=knowledge
```

**Maintaining memory:**
```
MEMORY.STATUS                    # Check current state
MEMORY.CONSOLIDATE --dry-run     # Preview consolidation
MEMORY.ARCHIVE                   # Archive old traces
MEMORY.CLEANUP                   # Interactive cleanup
```

**Exploring relationships:**
```
MEMORY.GRAPH                     # See connections
MEMORY.TAG list                  # Browse tags
MEMORY.STATS                     # Overall statistics
```

## Best Practices

1. **Use tags consistently** - Makes search powerful
2. **Save knowledge, not just traces** - Extract reusable patterns
3. **Archive regularly** - Keep trace.md focused on recent work
4. **Consolidate when fragmented** - Easier to read unified files
5. **Cross-reference related entries** - Build knowledge graph
6. **Verify before saving to knowledge** - Only confirmed facts
7. **Use global for cross-project patterns** - Share learnings
8. **Review MEMORY.STATUS periodically** - Maintain hygiene

## When to Use This Skill

**Auto-triggers (read-only):**
- When working in a project with existing memory
- When doing operational work with recent trace history
- When user query matches knowledge tags
- When user says "continue" or "as we discussed"

**Manual invocation:**
- End of session: MEMORY.SUMMARIZE_AND_ASK_SAVE
- Looking for past solutions: MEMORY.SEARCH
- Checking project status: MEMORY.STATUS
- Maintenance: MEMORY.CONSOLIDATE, MEMORY.ARCHIVE, MEMORY.CLEANUP
- Exploration: MEMORY.GRAPH, MEMORY.TAG, MEMORY.STATS

## Integration with Other Skills

- Works alongside Claude Code's auto memory (different scopes)
- Complements project documentation (more structured)
- Useful for long-running projects with multiple sessions
- Ideal for team environments (shared knowledge base)
- Supports incident response (trace history)
