# MEMORY.READ Implementation

## Command Syntax
```
MEMORY.READ [options] [slug]
```

## Options
- (no args) - Read knowledge only for current project
- `trace` - Include trace
- `full` or `all` - Include everything
- `--raw` - Show raw content without summarization
- `--since=YYYY-MM-DD` - Only entries after date
- `<slug>` - Read specific project's memory

## Implementation Steps

### 1. Derive Slug
```bash
# Get current working directory
cwd=$(pwd)

# Derive slug
if [[ "$cwd" == "$HOME" || "$cwd" == "~" ]]; then
    slug="_home"
else
    # Remove home prefix and replace / with __
    slug=$(echo "$cwd" | sed "s|^$HOME/||" | tr '/' '_')
fi

echo "Current slug: $slug"
```

### 2. Check File Existence
```bash
memory_root="$HOME/AGENTS.MEMORY"
global_knowledge="$memory_root/_global/knowledge.md"
project_knowledge="$memory_root/$slug/knowledge.md"
project_trace="$memory_root/$slug/trace.md"

# Check what exists
[[ -f "$global_knowledge" ]] && echo "✓ Global knowledge exists"
[[ -f "$project_knowledge" ]] && echo "✓ Project knowledge exists"
[[ -f "$project_trace" ]] && echo "✓ Project trace exists"
```

### 3. Read and Follow Continuations
```bash
# Function to read file and follow continuations
read_with_continuations() {
    local file="$1"
    local dir=$(dirname "$file")
    local base=$(basename "$file" .md)

    if [[ -f "$file" ]]; then
        cat "$file"

        # Check for continuations
        local i=2
        while [[ -f "$dir/${base}_${i}.md" ]]; do
            echo ""
            echo "--- From ${base}_${i}.md ---"
            cat "$dir/${base}_${i}.md"
            ((i++))
        done
    fi
}
```

### 4. Filter by Date (if --since specified)
```bash
# Filter entries by date
filter_by_date() {
    local content="$1"
    local since_date="$2"

    # Extract entries with Date: field >= since_date
    # This is a simplified version - actual implementation needs proper parsing
    echo "$content" | awk -v since="$since_date" '
        /^Date: / {
            date = substr($0, 7)
            if (date >= since) print_entry = 1
            else print_entry = 0
        }
        print_entry { print }
    '
}
```

### 5. Summarize (unless --raw)
```bash
# Summarize content
summarize_memory() {
    local content="$1"

    # Count entries
    local entry_count=$(echo "$content" | grep -c "^Date: ")

    # Extract unique tags
    local tags=$(echo "$content" | grep "^Tags: " | sed 's/Tags: //' | tr ' ' '\n' | sort -u | head -10)

    # Show recent entries (last 5)
    echo "Total entries: $entry_count"
    echo ""
    echo "Recent tags: $tags"
    echo ""
    echo "Recent entries:"
    echo "$content" | grep -A 10 "^Date: " | head -50
}
```

### 6. Output Format

**Summarized Output:**
```
=== AGENTS.MEMORY: projects__myapp ===

Global Knowledge (45 lines):
  - 3 entries
  - Tags: #deployment #nginx #ssl
  - Last updated: 2026-03-01

Project Knowledge (123 lines + 67 in continuation):
  - 8 entries
  - Tags: #deployment #bug-fix #config #performance
  - Last updated: 2026-03-03

Recent Entries:
---
Date: 2026-03-03
Tags: #nginx #ssl
Conclusion: Nginx SSL requires both cert and key in /etc/nginx/ssl/
...
```

**Raw Output:**
```
=== _global/knowledge.md ===
[full file content]

=== projects__myapp/knowledge.md ===
[full file content]

=== projects__myapp/knowledge_2.md ===
[full file content]
```

## Error Handling

```bash
# No memory found
if [[ ! -f "$global_knowledge" && ! -f "$project_knowledge" ]]; then
    echo "No memory found for project: $slug"
    echo "Use MEMORY.SUMMARIZE_AND_ASK_SAVE to create first entry"
    exit 0
fi

# Invalid slug
if [[ -n "$specified_slug" && ! -d "$memory_root/$specified_slug" ]]; then
    echo "Project not found: $specified_slug"
    echo "Available projects:"
    ls -1 "$memory_root" | grep -v "^_" | grep -v "^attic" | grep -v "^\.index"
    exit 1
fi
```

## Agent Behavior

When executing MEMORY.READ:

1. **Parse arguments** to determine what to read
2. **Derive slug** from current directory (or use specified)
3. **Check file existence** and report what's available
4. **Read files** following continuation markers
5. **Filter by date** if --since specified
6. **Summarize or show raw** based on --raw flag
7. **Present results** in clear, structured format

**Key Points:**
- Always show what files were found/not found
- Follow continuation files automatically
- Summarize by default (easier to digest)
- Show raw only when explicitly requested
- Include line counts and entry counts
- Highlight recent entries and common tags
