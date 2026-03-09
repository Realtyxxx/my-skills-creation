# MEMORY.TAG Implementation

## Command Syntax
```
MEMORY.TAG <subcommand> [options]
```

## Subcommands

### 1. MEMORY.TAG list
List all tags with usage counts.

```bash
list_all_tags() {
    local memory_root="$HOME/AGENTS.MEMORY"
    local project_filter="$1"  # optional

    # Find all knowledge and trace files
    local files=()
    if [[ -n "$project_filter" ]]; then
        files=("$memory_root/$project_filter"/*.md)
    else
        files=("$memory_root"/*/*.md)
    fi

    # Extract and count tags
    for file in "${files[@]}"; do
        [[ ! -f "$file" ]] && continue
        grep "^Tags: " "$file" | sed 's/Tags: //' | tr ' ' '\n'
    done | grep '^#' | sort | uniq -c | sort -rn
}

# Usage
MEMORY.TAG list                    # All tags
MEMORY.TAG list --project=<slug>   # Project-specific tags
```

**Output:**
```
=== MEMORY.TAG list ===

  23 #deployment
  18 #bug-fix
  15 #config
  12 #nginx
  10 #performance
   8 #ssl
   7 #docker
   5 #incident
   ...

Total: 45 unique tags
```

### 2. MEMORY.TAG show #tag
Show all entries with specific tag.

```bash
show_tag_entries() {
    local tag="$1"
    local memory_root="$HOME/AGENTS.MEMORY"

    # Search for tag in all files
    for file in "$memory_root"/*/*.md; do
        [[ ! -f "$file" ]] && continue

        # Check if file contains the tag
        if grep -q "^Tags:.*$tag" "$file"; then
            local project=$(basename "$(dirname "$file")")
            local file_type=$(basename "$file" .md)

            echo "=== $project/$file_type ==="
            echo ""

            # Extract entries with this tag
            awk -v tag="$tag" '
                /^Date: / { in_entry=1; entry="" }
                in_entry { entry = entry $0 "\n" }
                /^Tags:/ && $0 ~ tag { print_entry=1 }
                /^$/ && in_entry {
                    if (print_entry) print entry
                    in_entry=0; print_entry=0; entry=""
                }
            ' "$file"
            echo ""
        fi
    done
}

# Usage
MEMORY.TAG show #deployment
```

**Output:**
```
=== MEMORY.TAG show #deployment ===

=== projects__web/knowledge ===

Date: 2026-03-03
Tags: #deployment #nginx #ssl
Conclusion: Nginx SSL requires both cert and key in /etc/nginx/ssl/
Details:
  - Command: sudo cp cert.pem key.pem /etc/nginx/ssl/
...

=== projects__api/trace ===

Date: 2026-03-01
Tags: #deployment #incident
Goal: Deploy API v2.0 to production
...
```

### 3. MEMORY.TAG stats
Show tag statistics and trends.

```bash
tag_statistics() {
    local memory_root="$HOME/AGENTS.MEMORY"
    local index_file="$memory_root/.index/tags.json"

    # If index exists, use it
    if [[ -f "$index_file" ]]; then
        jq -r 'to_entries | sort_by(-.value.count) | .[] |
            "\(.key): \(.value.count) uses, \(.value.projects | length) projects, last: \(.value.last_used)"' \
            "$index_file"
    else
        # Fallback: generate stats on the fly
        echo "Tag index not found. Generating statistics..."
        echo ""

        # Count tags by project
        for project_dir in "$memory_root"/*/; do
            [[ ! -d "$project_dir" ]] && continue
            local project=$(basename "$project_dir")
            [[ "$project" == "attic" || "$project" == ".index" ]] && continue

            local tags=$(grep "^Tags: " "$project_dir"/*.md 2>/dev/null | \
                sed 's/Tags: //' | tr ' ' '\n' | grep '^#' | sort -u)

            if [[ -n "$tags" ]]; then
                echo "$project: $tags"
            fi
        done
    fi
}

# Usage
MEMORY.TAG stats
```

**Output:**
```
=== MEMORY.TAG stats ===

#deployment: 23 uses, 5 projects, last: 2026-03-03
#bug-fix: 18 uses, 4 projects, last: 2026-03-02
#config: 15 uses, 3 projects, last: 2026-03-01
#nginx: 12 uses, 2 projects, last: 2026-03-03
#performance: 10 uses, 3 projects, last: 2026-02-28

Tag trends (last 30 days):
  #deployment: ████████████ (12 new)
  #bug-fix: ████████ (8 new)
  #incident: ████ (4 new)
```

## Tag Index Management

### Update Tag Index
```bash
update_tag_index() {
    local tags="$1"
    local project="$2"
    local date="$3"

    local index_file="$HOME/AGENTS.MEMORY/.index/tags.json"
    mkdir -p "$(dirname "$index_file")"

    # Initialize if doesn't exist
    [[ ! -f "$index_file" ]] && echo "{}" > "$index_file"

    # Update each tag
    for tag in $tags; do
        # Use jq to update JSON
        jq --arg tag "$tag" \
           --arg proj "$project" \
           --arg date "$date" '
            .[$tag] = {
                count: ((.[$tag].count // 0) + 1),
                projects: ((.[$tag].projects // []) + [$proj] | unique),
                last_used: $date
            }
        ' "$index_file" > "$index_file.tmp" && mv "$index_file.tmp" "$index_file"
    done
}
```

### Rebuild Tag Index
```bash
rebuild_tag_index() {
    local memory_root="$HOME/AGENTS.MEMORY"
    local index_file="$memory_root/.index/tags.json"

    echo "Rebuilding tag index..."
    echo "{}" > "$index_file"

    # Scan all files
    for file in "$memory_root"/*/*.md; do
        [[ ! -f "$file" ]] && continue

        local project=$(basename "$(dirname "$file")")
        [[ "$project" == "attic" || "$project" == ".index" ]] && continue

        # Extract tags and dates
        awk '/^Date: / {date=$2} /^Tags: / {print date, $0}' "$file" | \
        while read date tags_line; do
            local tags=$(echo "$tags_line" | sed 's/Tags: //')
            update_tag_index "$tags" "$project" "$date"
        done
    done

    echo "✓ Tag index rebuilt"
}
```

## Agent Behavior

When executing MEMORY.TAG:

1. **Parse subcommand** (list/show/stats)
2. **Access tag index** if available (fast path)
3. **Fallback to file scan** if index missing
4. **Format output** based on subcommand
5. **Suggest related tags** when showing specific tag

**Key Points:**
- Use tag index for fast lookups
- Fallback to file scan if index missing
- Show context with each tag (project, date, entry)
- Support filtering by project
- Provide statistics and trends
- Help discover related tags
