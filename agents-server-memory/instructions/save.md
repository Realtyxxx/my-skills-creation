# MEMORY.SUMMARIZE_AND_ASK_SAVE Implementation

## Command Syntax
```
MEMORY.SUMMARIZE_AND_ASK_SAVE
```

## Implementation Steps

### 1. Analyze Current Session Context

Agent should review:
- Recent tool calls and their results
- User's stated goals
- Actions taken
- Outcomes achieved
- Any errors encountered and resolutions

### 2. Generate Knowledge Candidate

Only if there's a verified, reusable conclusion:

```markdown
**Knowledge Candidate:**

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
```

**Criteria for Knowledge:**
- Verified solution (not just attempted)
- Reusable pattern or runbook
- Clear cause and effect
- Reproducible steps
- Confirmed outcome

### 3. Generate Trace Candidate

Always generate for non-trivial sessions:

```markdown
**Trace Candidate:**

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

**Criteria for Trace:**
- Any significant work session
- Debugging process (even if unresolved)
- Exploratory work with findings
- Incident response
- Configuration changes

### 4. Assess Confidence Level

```python
def assess_confidence(session_context):
    score = 0

    # HIGH confidence indicators (+10 each)
    if user_confirmed_success: score += 10
    if reusable_runbook_created: score += 10
    if recurring_issue_resolved: score += 10
    if key_decision_documented: score += 10

    # MEDIUM confidence indicators (+5 each)
    if partial_success: score += 5
    if workaround_found: score += 5
    if valuable_lessons: score += 5

    # LOW confidence indicators (+2 each)
    if exploratory_work: score += 2
    if temporary_solution: score += 2

    # Determine level
    if score >= 10: return "HIGH"
    elif score >= 5: return "MEDIUM"
    else: return "LOW"
```

### 5. Suggest Tags

```python
def suggest_tags(content):
    tags = []

    # Type tags
    if "deploy" in content.lower(): tags.append("#deployment")
    if "bug" in content.lower() or "fix" in content.lower(): tags.append("#bug-fix")
    if "config" in content.lower(): tags.append("#config")
    if "performance" in content.lower() or "slow" in content.lower(): tags.append("#performance")
    if "security" in content.lower() or "ssl" in content.lower(): tags.append("#security")
    if "incident" in content.lower() or "outage" in content.lower(): tags.append("#incident")

    # Tech tags (extract from content)
    tech_keywords = ["nginx", "docker", "kubernetes", "postgres", "redis", "python", "nodejs"]
    for tech in tech_keywords:
        if tech in content.lower(): tags.append(f"#{tech}")

    # Severity tags
    if "critical" in content.lower() or "production down" in content.lower(): tags.append("#critical")
    elif "urgent" in content.lower(): tags.append("#high")

    return tags[:5]  # Limit to 5 tags
```

### 6. Derive Slug and Determine Location

```bash
# Get current slug
cwd=$(pwd)
if [[ "$cwd" == "$HOME" || "$cwd" == "~" ]]; then
    slug="_home"
else
    slug=$(echo "$cwd" | sed "s|^$HOME/||" | tr '/' '_')
fi

# Suggest location
if [[ knowledge_is_cross_project ]]; then
    suggested_location="global (_global)"
else
    suggested_location="project ($slug)"
fi
```

### 7. Ask User for Confirmation

Present in this format:

```
=== MEMORY.SUMMARIZE_AND_ASK_SAVE ===

[HIGH CONFIDENCE]

Knowledge Candidate:
---
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
---

Trace Candidate:
---
Date: 2026-03-03
Tags: #deployment #incident
Goal: Fix SSL certificate expiration on production
Actions:
  - Generated new cert with Let's Encrypt
  - Copied to /etc/nginx/ssl/
  - Restarted nginx service
Outcome: SSL working, monitoring for 24h
---

Save to memory?
  Location: project (projects__web) or global (_global)?
  Type: knowledge, trace, or both?
  Tags: (suggested above, edit if needed)
  Or skip?
```

### 8. Execute Save Based on User Response

```bash
save_to_memory() {
    local location="$1"  # "project" or "global"
    local type="$2"      # "knowledge" or "trace" or "both"
    local content="$3"
    local tags="$4"

    # Determine file path
    if [[ "$location" == "global" ]]; then
        base_path="$HOME/AGENTS.MEMORY/_global"
    else
        base_path="$HOME/AGENTS.MEMORY/$slug"
    fi

    # Create directory if needed
    mkdir -p "$base_path/.backups"

    # Determine target file
    if [[ "$type" == "knowledge" ]]; then
        target_file="$base_path/knowledge.md"
    elif [[ "$type" == "trace" ]]; then
        target_file="$base_path/trace.md"
    fi

    # Create backup
    if [[ -f "$target_file" ]]; then
        backup_file="$base_path/.backups/$(basename "$target_file").$(date +%Y-%m-%dT%H-%M-%S).bak"
        cp "$target_file" "$backup_file"
        echo "✓ Backup created: $backup_file"
    fi

    # Append content
    echo "" >> "$target_file"
    echo "$content" >> "$target_file"
    echo "✓ Saved to: $target_file"

    # Update tag index
    update_tag_index "$tags" "$location" "$slug"
}
```

### 9. Update Tag Index

```bash
update_tag_index() {
    local tags="$1"
    local location="$2"
    local slug="$3"

    local index_file="$HOME/AGENTS.MEMORY/.index/tags.json"
    mkdir -p "$(dirname "$index_file")"

    # Initialize if doesn't exist
    [[ ! -f "$index_file" ]] && echo "{}" > "$index_file"

    # Update each tag (simplified - actual implementation needs proper JSON handling)
    for tag in $tags; do
        # Increment count, add project, update last_used
        # This requires jq or similar JSON tool
        jq --arg tag "$tag" --arg proj "$slug" --arg date "$(date +%Y-%m-%d)" \
           '.[$tag].count += 1 | .[$tag].projects += [$proj] | .[$tag].last_used = $date' \
           "$index_file" > "$index_file.tmp" && mv "$index_file.tmp" "$index_file"
    done
}
```

### 10. Handle User Decline

```bash
# Track decline count
decline_count_file="$HOME/AGENTS.MEMORY/.index/decline_count"

if user_declined; then
    # Increment decline count
    count=$(cat "$decline_count_file" 2>/dev/null || echo 0)
    count=$((count + 1))
    echo "$count" > "$decline_count_file"

    # After 3 declines, ask if should reduce frequency
    if [[ $count -ge 3 ]]; then
        echo ""
        echo "You've declined saving 3 times in a row."
        echo "Should I reduce the frequency of save suggestions?"
        echo "  (yes/no)"
        # Store preference
    fi
fi
```

## Agent Behavior

When executing MEMORY.SUMMARIZE_AND_ASK_SAVE:

1. **Review session context** - What was done, what was achieved
2. **Generate candidates** - Knowledge (if verified) and/or Trace
3. **Assess confidence** - HIGH/MEDIUM/LOW based on criteria
4. **Suggest tags** - Auto-detect from content
5. **Determine location** - Project vs global based on scope
6. **Present to user** - Clear, structured format
7. **Wait for confirmation** - Never save without explicit approval
8. **Execute save** - Create backup, append content, update index
9. **Confirm completion** - Show where saved

**Key Points:**
- Only propose when there's something worth saving
- Be honest about confidence level
- Suggest good defaults but let user override
- Create backups before every write
- Update tag index for searchability
- Respect user preferences (reduce frequency if declined repeatedly)
- Never save without explicit confirmation

## Confidence Level Examples

**HIGH:**
- "Fixed production SSL issue, verified with SSL Labs A+"
- "Created deployment runbook, tested on 3 servers"
- "Identified root cause of memory leak, confirmed fix"

**MEDIUM:**
- "Found workaround for API timeout, but root cause unclear"
- "Partially resolved performance issue, needs more testing"
- "Documented debugging process, issue still intermittent"

**LOW:**
- "Explored different approaches, no clear winner yet"
- "Temporary fix applied, proper solution needs design"
- "Gathered information, next steps unclear"
