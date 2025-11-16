# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository stores Claude Code conversation history and configuration data. It contains:
- Conversation histories organized by project in `.jsonl` format
- Custom slash commands and agent definitions
- Settings and session state
- Shell snapshots and debug logs

## Repository Structure

```
conversations/.claude/
├── agents/          # Custom agent definitions (context-fetcher, git-workflow, etc.)
├── commands/        # Custom slash commands (analyze-product, create-spec, etc.)
├── projects/        # Project-specific conversation histories (.jsonl files)
├── debug/           # Debug logs
├── file-history/    # File version history
├── session-env/     # Session environment data
├── shell-snapshots/ # Shell state snapshots
├── todos/           # Todo list persistence
├── history.jsonl    # Global conversation history
├── settings.json    # Claude Code settings
└── CLAUDE.md        # This file (exists at this location)
```

## Important Conventions

### Conversation Data
- Conversations are stored in `conversations/.claude/projects/` as `.jsonl` files
- Each line in a `.jsonl` file is a separate JSON object representing a conversation turn
- Project paths are encoded in directory names (e.g., `-Users-Reed-dev-job-coach/`)
- Do NOT modify conversation history files unless explicitly instructed

### Custom Commands
Located in `conversations/.claude/commands/`:
- `/analyze-product` - Analyze product codebase and install Agent OS
- `/create-spec` - Create detailed feature specs with technical specifications
- `/execute-tasks` - Execute the next task from a plan
- `/plan-product` - Plan a new product and install Agent OS
- `/reed-review` - Code review focusing on modern software engineering practices (DRY, encapsulation, error handling, etc.)

### Custom Agents
Located in `conversations/.claude/agents/`:
- `context-fetcher` - Retrieve Agent OS documentation
- `date-checker` - Check current date
- `file-creator` - Create files and apply templates
- `git-workflow` - Handle git operations and PR creation
- `test-runner` - Run tests and analyze failures

## Settings Configuration

The `conversations/.claude/settings.json` file contains:
- Custom status line configuration (shows git branch and directory)
- "Always thinking" mode enabled
- Feedback survey state

## Working with This Repository

### Reading Conversation History
To examine past conversations:
```bash
# List all project directories
ls conversations/.claude/projects/

# Read a specific conversation
cat conversations/.claude/projects/<project-path>/<conversation-id>.jsonl | jq
```

### Analyzing Conversations
Each `.jsonl` file contains conversation turns with structure like:
- User messages
- Assistant responses
- Tool invocations and results
- System messages

Use `jq` for parsing and analyzing JSON data.

## Code Quality Standards

When reviewing or modifying code (per `/reed-review` command):
- Follow DRY (Don't Repeat Yourself) principles
- Ensure proper encapsulation and abstraction
- Implement rigorous error checking and handling
- Maintain loose coupling between components
- Validate all parameters
- Include verbose logging for debugging
- Write readable code with clear comments
- Remove dead code and unused files
- DO NOT BREAK EXISTING FUNCTIONALITY
