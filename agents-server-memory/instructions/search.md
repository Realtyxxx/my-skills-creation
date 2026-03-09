# MEMORY.SEARCH Implementation

## Command Syntax
```
MEMORY.SEARCH <keyword> [options]
```

## Options
- `--scope=global` - Search only _global
- `--scope=<slug>` - Search specific project
- `--type=knowledge` - Search only knowledge files
- `--type=trace` - Search only trace files
- `--since=YYYY-MM-DD` - Search entries after date
- `--regex` - Treat keyword as regex pattern
- `--all` - Show all matches (not just top 10)

## Implementation Steps

### 1. Parse Arguments
```bash
keyword="$1"
scope=""
type=""
since=""
use_regex=false
show_all=false

# Parse options
shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scope=*) scope="${1#*=}" ;;
        --type=*) type="${1#*=}" ;;
        --since=*) since="${1#*=}" ;;
        --regex) use_regex=true ;;
        --all) show_all=true ;;
    esac
    shift
done
```

### 2. Build Search Paths
```bash
memory_root="$HOME/AGENTS.MEMORY"
search_paths=()

if [[ -n "$scope" ]]; then
    # Specific scope
    if [[ "$scope" == "global" ]]; then
        search_paths+=("$memory_root/_global")
    else
        search_paths+=("$memory_root/$scope")
    fi
else
    # All projects
    for dir in "$memory_root"/*; do
        [[ -d "$dir" ]] && [[ "$(basename "$dir")" != "attic" ]] && [[ "$(basename "$dir")" != ".index" ]] && search_paths+=("$dir")
    done
fi

# Filter by type
if [[ "$type" == "knowledge" ]]; then
    file_pattern="knowledge*.md"
elif [[ "$type" == "trace" ]]; then
    file_pattern="trace*.md"
else
    file_pattern="*.md"
fi
```

### 3. Search with Grep
```bash
# Search function
search_memory() {
    local keyword="$1"
    local use_regex="$2"

    local grep_opts="-n -i -H"  # line number, case-insensitive, filename
    [[ "$use_regex" == "true" ]] && grep_opts+=" -E"

    # Search in all paths
    for path in "${search_paths[@]}"; do
        find "$path" -name "$file_pattern" -type f -exec grep $grep_opts "$keyword" {} \;
    done
}

# Execute search
results=$(search_memory "$keyword" "$use_regex")
```

### 4. Parse and Rank Results
```bash
# Parse results into structured format
parse_results() {
    local results="$1"

    # Format: filepath:line_number:content
    echo "$results" | while IFS=: read -r filepath line_num content; do
        # Extract metadata
        local project=$(basename "$(dirname "$filepath")")
        local file_type=$(basename "$filepath" | sed 's/_[0-9]*.md//')

        # Get date and tags from context
        local date=$(grep -B 20 -m 1 "^Date: " "$filepath" | tail -1 | sed 's/Date: //')
        local tags=$(grep -A 1 "^Date: $date" "$filepath" | grep "^Tags: " | sed 's/Tags: //')

        # Calculate relevance score
        local score=0
        # Exact match in conclusion/goal: +10
        echo "$content" | grep -qi "^Conclusion:\|^Goal:" && score=$((score + 10))
        # Tag match: +5
        echo "$tags" | grep -qi "$keyword" && score=$((score + 5))
        # Content match: +1
        score=$((score + 1))

        # Output structured result
        echo "$score|$project|$file_type|$date|$tags|$filepath:$line_num|$content"
    done | sort -t'|' -k1 -rn  # Sort by score descending
}

ranked_results=$(parse_results "$results")
```

### 5. Filter by Date
```bash
if [[ -n "$since" ]]; then
    ranked_results=$(echo "$ranked_results" | awk -F'|' -v since="$since" '$4 >= since')
fi
```

### 6. Format Output
```bash
# Format results for display
format_results() {
    local results="$1"
    local show_all="$2"

    local count=0
    local max_results=10
    [[ "$show_all" == "true" ]] && max_results=999999

    echo "$results" | while IFS='|' read -r score project file_type date tags location content; do
        ((count++))
        [[ $count -gt $max_results ]] && break

        echo "[$count] $project/$file_type ($date)"
        [[ -n "$tags" ]] && echo "    Tags: $tags"
        echo "    $location"
        echo "    $content"
        echo ""
    done

    # Show total count
    local total=$(echo "$results" | wc -l)
    if [[ $total -gt $max_results ]]; then
        echo "Showing top $max_results of $total results. Use --all to see more."
    else
        echo "Total: $total results"
    fi
}

format_results "$ranked_results" "$show_all"
```

### 7. Suggest Related Tags
```bash
# Extract and suggest related tags
suggest_tags() {
    local results="$1"

    # Extract all tags from results
    local all_tags=$(echo "$results" | cut -d'|' -f5 | tr ' ' '\n' | grep '^#' | sort | uniq -c | sort -rn | head -5)

    if [[ -n "$all_tags" ]]; then
        echo ""
        echo "Related tags found:"
        echo "$all_tags" | while read count tag; do
            echo "  $tag ($count)"
        done
    fi
}

suggest_tags "$ranked_results"
```

## Output Format

```
=== MEMORY.SEARCH: "nginx ssl" ===

[1] projects__web/knowledge (2026-03-03)
    Tags: #nginx #ssl #deployment
    /Users/user/AGENTS.MEMORY/projects__web/knowledge.md:15
    Conclusion: Nginx SSL requires both cert and key in /etc/nginx/ssl/

[2] projects__api/trace (2026-03-01)
    Tags: #nginx #incident
    /Users/user/AGENTS.MEMORY/projects__api/trace.md:42
    Goal: Fix SSL certificate expiration on production

[3] _global/knowledge (2026-02-15)
    Tags: #ssl #security
    /Users/user/AGENTS.MEMORY/_global/knowledge.md:8
    Details: SSL Labs grade A+ requires TLS 1.2+

Total: 3 results

Related tags found:
  #nginx (2)
  #ssl (3)
  #deployment (1)
  #incident (1)
```

## Special Cases

### Tag Search
```bash
# If keyword starts with #, search in Tags: lines
if [[ "$keyword" == \#* ]]; then
    grep_pattern="^Tags:.*$keyword"
    # Then show full entries containing that tag
fi
```

### Regex Search
```bash
# Example regex patterns
MEMORY.SEARCH "nginx.*ssl" --regex
MEMORY.SEARCH "error|failure|bug" --regex
MEMORY.SEARCH "^Conclusion:.*performance" --regex
```

### Context Lines
```bash
# Show context around matches
grep_opts+=" -A 3 -B 1"  # 3 lines after, 1 before
```

## Error Handling

```bash
# No results
if [[ -z "$results" ]]; then
    echo "No results found for: $keyword"
    echo ""
    echo "Suggestions:"
    echo "  - Try broader keywords"
    echo "  - Use --regex for pattern matching"
    echo "  - Check available tags with: MEMORY.TAG list"
    exit 0
fi

# Invalid scope
if [[ -n "$scope" && ! -d "$memory_root/$scope" ]]; then
    echo "Project not found: $scope"
    echo "Available projects:"
    ls -1 "$memory_root" | grep -v "^attic" | grep -v "^\.index"
    exit 1
fi
```

## Agent Behavior

When executing MEMORY.SEARCH:

1. **Parse arguments** to extract keyword and options
2. **Build search paths** based on scope and type filters
3. **Execute grep search** across all relevant files
4. **Parse and rank results** by relevance (exact > tag > content)
5. **Filter by date** if --since specified
6. **Format output** showing top 10 (or all with --all)
7. **Suggest related tags** found in results

**Key Points:**
- Case-insensitive by default
- Rank by relevance (not just chronological)
- Show context (file, date, tags, location)
- Suggest related tags for further exploration
- Support both simple keywords and regex patterns
- Limit to top 10 by default to avoid overwhelming output
