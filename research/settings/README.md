# settings Analysis

## Purpose & Responsibility

Global Claude Code settings including status line configuration, feature flags, and user preferences. This file persists settings across sessions.

*Error generating statistics: Source directory not found: /Users/Reed/dev/claude_conversation/conversations/.claude/settings*

## Data Structure

JSON configuration file with 4 top-level keys.

```json
{
  "type": "object",
  "properties": {
    "$schema": {
      "type": "str",
      "example": "https://json.schemastore.org/claude-code-settings.json"
    },
    "statusLine": {
      "type": "object",
      "properties": {
        "type": {
          "type": "str",
          "example": "command"
        },
        "command": {
          "type": "str",
          "example": "input=$(cat); cwd=$(echo \"$input\" | jq -r '.workspace.current_dir'); dir_name=$(basename \"$cwd\"); gi..."
        }
      }
    },
    "alwaysThinkingEnabled": {
      "type": "bool",
      "example": true
    },
    "feedbackSurveyState": {
      "type": "object",
      "properties": {
        "lastShownTime": {
          "type": "int",
          "example": 1754137571853
        }
      }
    }
  }
}
```

## Temporal Evolution

Configuration files are modified when settings change. The structure typically remains stable with values being updated.

- Configuration files are updated when user changes settings
- New keys may be added as new features are introduced
- Values are modified to reflect current configuration
- File structure remains relatively stable over time

## Examples

### Example 1

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "statusLine": {
    "type": "command",
    "command": "input=$(cat); cwd=$(echo \"$input\" | jq -r '.workspace.current_dir'); dir_name=$(basename \"$cwd\"); git_info=\"\"; if git -C \"$cwd\" rev-parse --git-dir > /dev/null 2>&1; then branch=$(git -C \"$cwd\" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null); if [ -n \"$branch\" ]; then if git -C \"$cwd\" --no-optional-locks diff --quiet 2>/dev/null && git -C \"$cwd\" --no-optional-locks diff --cached --quiet 2>/dev/null; then git_info=$(printf \" \\033[1;34mgit:(\\033[0;31m%s\\033[1;34m)\\033[0m\" \"$branch\"); else git_info=$(printf \" \\033[1;34mgit:(\\033[0;31m%s\\033[1;34m) \\033[0;33m\u2717\\033[0m\" \"$branch\"); fi; fi; fi; printf \"\\033[1;32m\u279c\\033[0m  \\033[0;36m%s\\033[0m%s\" \"$dir_name\" \"$git_info\""
  },
  "alwaysThinkingEnabled": true,
  "feedbackSurveyState": {
    "lastShownTime": 1754137571853
  }
}
```
