# MEMORY.STATUS Implementation

## Command Syntax
```
MEMORY.STATUS
```

## Implementation Steps

### 1. Derive Current Slug
```bash
cwd=$(pwd)
if [[ "$cwd" == "$HOME" || "$cwd" == "~" ]]; then
    slug="_home"
else
    slug=$(echo "$cwd" | sed "s|^$HOME/||" | tr '/' '_')
fi
```

### 2. Check File Existence and Sizes
```bash
memory_root="$HOME/AGENTS.MEMORY"

# Global files
global_knowledge="$memory_root/_global/knowledge.md"
global_trace="$memory_root/_global/trace.md"

# Project files
project_knowledge="$memory_root/$slug/knowledge.md"
project_trace="$memory_root/$slug/trace.md"
project_archive="$memory_root/$slug/trace_archive.md"

# Count lines
count_lines() {
    [[ -f "$1" ]] && wc -l < "$1" || echo 0
}

global_k_lines=$(count_lines "$global_knowledge")
project_k_lines=$(count_lines "$project_knowledge")
project_t_lines=$(count_lines "$project_trace")
archive_lines=$(count_lines "$project_archive")
```

### 3. Count Continuation Files
```bash
count_continuations() {
    local base_file="$1"
    local dir=$(dirname "$base_file")
    local base=$(basename "$base_file" .md)
    local count=0

    local i=2
    while [[ -f "$dir/${base}_${i}.md" ]]; do
        ((count++))
        ((i++))
    done

    echo "$count"
}

k_continuations=$(count_continuations "$project_knowledge")
```

### 4. Analyze Trace Age Distribution
```bash
analyze_trace_age() {
    local trace_file="$1"
    [[ ! -f "$trace_file" ]] && return

    local today=$(date +%Y-%m-%d)
    local recent=0 medium=0 old=0

    # Extract dates and calculate age
    grep "^Date: " "$trace_file" | sed 's/Date: //' | while read date; do
        local age_days=$(( ($(date -j -f "%Y-%m-%d" "$today" +%s) - $(date -j -f "%Y-%m-%d" "$date" +%s)) / 86400 ))

        if [[ $age_days -le 14 ]]; then
            ((recent++))
        elif [[ $age_days -le 30 ]]; then
            ((medium++))
        else
            ((old++))
        fi
    done

    echo "$recent $medium $old"
}

read recent medium old <<< $(analyze_trace_age "$project_trace")
```

### 5. Extract Top Tags
```bash
extract_top_tags() {
    local knowledge_file="$1"
    [[ ! -f "$knowledge_file" ]] && return

    # Extract all tags, count, sort
    grep "^Tags: " "$knowledge_file" | \
        sed 's/Tags: //' | \
        tr ' ' '\n' | \
        grep '^#' | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -5 | \
        awk '{print $2"("$1")"}'
}

top_tags=$(extract_top_tags "$project_knowledge")
```

### 6. Generate Suggestions
```bash
generate_suggestions() {
    local suggestions=()

    # Consolidation suggestion
    local total_k_lines=$((project_k_lines + $(count_continuation_lines)))
    if [[ $total_k_lines -gt 500 ]]; then
        suggestions+=("Consider consolidating knowledge files ($total_k_lines total lines)")
    fi

    # Archive suggestion
    if [[ $project_t_lines -gt 300 ]]; then
        suggestions+=("Trace file is large ($project_t_lines lines). Run MEMORY.ARCHIVE")
    fi

    # Old traces suggestion
    if [[ $old -gt 0 ]]; then
        suggestions+=("$old old trace entries (31-90d). Run MEMORY.ARCHIVE")
    fi

    # Stale project suggestion
    if [[ $recent -eq 0 && $medium -eq 0 ]]; then
        suggestions+=("No recent activity. Consider moving to attic if project is inactive")
    fi

    # Print suggestions
    for suggestion in "${suggestions[@]}"; do
        echo "  - $suggestion"
    done
}
```

### 7. Format Output
```bash
echo "=== MEMORY.STATUS ==="
echo ""
echo "Current: $slug"
echo ""

# Global memory
if [[ -f "$global_knowledge" ]]; then
    echo "Global knowledge: $global_k_lines lines"
else
    echo "Global knowledge: not found"
fi

# Project memory
if [[ -f "$project_knowledge" ]]; then
    echo "Project knowledge: $project_k_lines lines"
    if [[ $k_continuations -gt 0 ]]; then
        echo "  + $k_continuations continuation file(s)"
    fi
else
    echo "Project knowledge: not found"
fi

# Trace status
if [[ -f "$project_trace" ]]; then
    echo "Trace: $recent recent (0-14d), $medium medium (15-30d), $old old (31+d)"
else
    echo "Trace: not found"
fi

# Archive status
if [[ -f "$project_archive" ]]; then
    local archive_entries=$(grep -c "^Date: " "$project_archive")
    echo "Archive: $archive_entries entries"
fi

# Top tags
if [[ -n "$top_tags" ]]; then
    echo ""
    echo "Top tags: $top_tags"
fi

# Suggestions
echo ""
echo "Suggestions:"
generate_suggestions
```

## Output Format

```
=== MEMORY.STATUS ===

Current: projects__myapp

Global knowledge: 45 lines
Project knowledge: 123 lines
  + 2 continuation file(s)
Trace: 8 recent (0-14d), 3 medium (15-30d), 0 old (31+d)
Archive: 15 entries

Top tags: #deployment(5) #nginx(3) #ssl(2) #bug-fix(2) #performance(1)

Suggestions:
  - Consider consolidating knowledge files (257 total lines)
```

## Agent Behavior

When executing MEMORY.STATUS:

1. **Derive slug** from current directory
2. **Check file existence** for global and project memory
3. **Count lines** in all files
4. **Detect continuations** (knowledge_2.md, etc.)
5. **Analyze trace age** distribution (recent/medium/old)
6. **Extract top tags** from knowledge
7. **Generate suggestions** based on state
8. **Present structured output** with clear sections

**Key Points:**
- Fast operation (no full file reads)
- Show what exists and what doesn't
- Provide actionable suggestions
- Highlight potential issues (large files, old traces)
- Help user understand current memory state
