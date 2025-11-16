# debug Analysis

## Purpose & Responsibility

Debug logs and diagnostic information from Claude Code execution. Contains detailed logs of tool calls, errors, and system events for troubleshooting.

## Statistics

- **Total Files**: 89
- **Total Size**: 23.94 MB
- **Date Range**: 2025-10-08 to 2025-11-16

### File Extensions

| Extension | Count | Percentage |
| --- | --- | --- |
| .txt | 88 | 98.9% |

## Data Structure

Folder containing 89 files of various types.

## Temporal Evolution

Files range from 1759929292.976599 to 1763297533.761865. This folder contains dynamic data that changes with usage.

- Files are created and updated during active sessions
- Older files may represent historical state or debug information
- Newer files represent recent activity
- File count grows over time with usage

## Examples

### Example 1

```json
{
  "file": "771c1d5e-a9be-43b8-9b4c-d5f231a5edd9.txt",
  "type": ".txt",
  "content_preview": "[DEBUG] Watching for changes in setting files /Users/<USER>/.claude/settings.json...\n[DEBUG] Found 0 plugins (0 enabled, 0 disabled)\n[DEBUG] Creating shell snapshot for zsh (/bin/zsh)\n[DEBUG] Looking for shell config file: /Users/<USER>/.zshrc\n[DEBUG] Snapshots directory: /Users/<USER>/.claude/shell-snapshots\n[DEBUG] Creating snapshot at: /Users/<USER>/.claude/shell-snapshots/snapshot-zsh-1759929291798-59x90z.sh\n[DEBUG] Shell binary exists: true\n[DEBUG] Execution timeout: 10000ms\n[DEBUG] Writing to temp file: /Users/<USER>/.claude/todos/771c1d5e-a9be-43b8-9b4c-d5f231a5edd9-agent-771c1d5e-a9be-43b8-9b4c-d5f231a5edd9.json.tmp.20224.1759929291799\n[DEBUG] Temp file written successfully, size: 2 bytes\n[DEBUG] Renaming /Users/<USER>/.claude/todos/771c1d5e-a9be-43b8-9b4c-d5f231a5edd9-agent-771c1d5e-a9be-43b8-9b4c-d5f231a5edd9.json.tmp.20224.1759929291799 to /Users/<USER>/.claude/todos/771c1d5e-a9be-43b8-9b4c-d5f231a5edd9-agent-771c1d5e-a9be-43b8-9b4c-d5f231a5edd9.json\n[DEBUG] File /Users/<USER>/.claude/todos"
}
```

### Example 2

```json
{
  "file": "91a7b772-a062-4d3d-8a2c-3fa5a0e354f9.txt",
  "type": ".txt",
  "content_preview": "[DEBUG] Watching for changes in setting files /Users/Reed/.claude/settings.json...\n[DEBUG] Found 0 plugins (0 enabled, 0 disabled)\n[DEBUG] >>>>> getSkillsIfEnabled() CALLED <<<<<\n[DEBUG] ENABLE_SKILLS value: true, type: boolean\n[DEBUG] ENABLE_SKILLS check passed, loading skills...\n[DEBUG] Loading skills from directories: managed=/Library/Application Support/ClaudeCode/.claude/skills, user=/Users/Reed/.claude/skills, project=/Users/<USER>/dev/<PROJECT>/.claude/skills\n[DEBUG] >>>>> getPluginSkills CALLED <<<<<\n[DEBUG] Creating shell snapshot for zsh (/bin/zsh)\n[DEBUG] Looking for shell config file: /Users/Reed/.zshrc\n[DEBUG] Snapshots directory: /Users/Reed/.claude/shell-snapshots\n[DEBUG] Creating snapshot at: /Users/Reed/.claude/shell-snapshots/snapshot-zsh-1761316099839-n13emi.sh\n[DEBUG] Shell binary exists: true\n[DEBUG] Execution timeout: 10000ms\n[DEBUG] Writing to temp file: /Users/Reed/.claude/todos/91a7b772-a062-4d3d-8a2c-3fa5a0e354f9-agent-91a7b772-a062-4d3d-8a2c-3fa5a0e354f9.json.t"
}
```

### Example 3

```json
{
  "file": "60fed7e5-1323-4025-8006-6b608129b2c6.txt",
  "type": ".txt",
  "content_preview": "[DEBUG] Getting matching hook commands for SessionStart with query: clear\n[DEBUG] Found 0 hook matchers in settings\n[DEBUG] Matched 0 unique hooks for query \"clear\" (0 before deduplication)\n[DEBUG] FileHistory: Added snapshot for 7e7c24bb-21b7-4855-8a39-3188323019a3, tracking 0 files\n[DEBUG] Rendering user message with 1 content blocks\n[DEBUG] Block 0: <command-name>/clear</command-name>\n            <command-message>clear</command-message>\n           ...\n[DEBUG] UserCommandMessage rendering: \"clear\" (args: \"none\")\n[DEBUG] isSkillFormat: false, prefix: \"/\"\n[DEBUG] Writing to temp file: /Users/<USER>/.claude.json.tmp.10313.1761748338696\n[DEBUG] Preserving file permissions: 100644\n[DEBUG] Temp file written successfully, size: 17087453 bytes\n[DEBUG] Applied original permissions to temp file\n[DEBUG] Renaming /Users/<USER>/.claude.json.tmp.10313.1761748338696 to /Users/<USER>/.claude.json\n[DEBUG] File /Users/<USER>/.claude.json written atomically\n[DEBUG] MCP server \"context7\": HTTP connection droppe"
}
```

### Example 4

```json
{
  "file": "effae53c-6551-4e72-9e73-f8b39a2eb0d5.txt",
  "type": ".txt",
  "content_preview": "[DEBUG] Watching for changes in setting files /Users/Reed/.claude/settings.json, /Users/<USER>/dev/<PROJECT>/.claude/settings.local.json...\n[DEBUG] Applying permission update: Adding 1 allow rule(s) to destination 'localSettings': [\"WebSearch\"]\n[DEBUG] Found 0 plugins (0 enabled, 0 disabled)\n[DEBUG] Total LSP servers loaded: 0\n[DEBUG] LSP manager initialized with 0 servers\n[DEBUG] LSP server manager initialized successfully\n[DEBUG] Loading skills from directories: managed=/Library/Application Support/ClaudeCode/.claude/skills, user=/Users/Reed/.claude/skills, project=/Users/<USER>/dev/<PROJECT>/.claude/skills\n[DEBUG] >>>>> getPluginSkills CALLED <<<<<\n[DEBUG] Creating shell snapshot for zsh (/bin/zsh)\n[DEBUG] Looking for shell config file: /Users/Reed/.zshrc\n[DEBUG] Snapshots directory: /Users/Reed/.claude/shell-snapshots\n[DEBUG] Creating snapshot at: /Users/Reed/.claude/shell-snapshots/snapshot-zsh-1762173643458-x65uv8.sh\n[DEBUG] Shell binary exists: true\n[DEBUG] Exe"
}
```

### Example 5

```json
{
  "file": "latest",
  "type": "",
  "note": "Binary file or non-text format",
  "size_bytes": 102710
}
```

## Relationships to Other Components

This component has **1 relationships** with other components:

### .claude

**Relationship Type**: ID Sharing (strength: 7.6%)

- **Shared Project Paths**: 11


**Sample Shared Projects**:

- /Users/Reed/dev/firefox-tab-group-sync-extension
- /Users/Reed/dev/nanochat-curriculum
- /Users/Reed/dev/neural-compression-poc

### Relationship Summary

- **Agent IDs tracked**: 80
- **Message UUIDs tracked**: 135
- **Project paths tracked**: 20

