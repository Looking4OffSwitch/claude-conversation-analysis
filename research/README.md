# Claude Conversation Data Analysis

## Overview

This directory contains comprehensive documentation of the Claude Code conversation data structure. Each subfolder has been analyzed to document its purpose, data structure, temporal evolution, and provide sanitized examples.

**Analysis completed**: 2025-11-16 07:52:14

**Total components analyzed**: 13
**Successful**: 13
**Failed**: 0

## Components

The `.claude` directory contains the following components. Click on each component to view detailed documentation.

### Configuration

- [**agents**](./agents/README.md) - View detailed analysis
- [**commands**](./commands/README.md) - View detailed analysis
- [**settings**](./settings/README.md) - View detailed analysis
- [**plugins**](./plugins/README.md) - View detailed analysis

### Conversation Data

- [**history**](./history/README.md) - View detailed analysis
- [**projects**](./projects/README.md) - View detailed analysis

### State & Persistence

- [**todos**](./todos/README.md) - View detailed analysis
- [**session-env**](./session-env/README.md) - View detailed analysis
- [**shell-snapshots**](./shell-snapshots/README.md) - View detailed analysis
- [**file-history**](./file-history/README.md) - View detailed analysis

### System & Diagnostics

- [**debug**](./debug/README.md) - View detailed analysis
- [**statsig**](./statsig/README.md) - View detailed analysis
- [**ide**](./ide/README.md) - View detailed analysis

## Directory Structure

```text
conversations/.claude/
├── agents/           # Custom agent definitions
├── commands/         # Custom slash commands
├── debug/            # Debug logs
├── file-history/     # File version history
├── ide/              # IDE integration data
├── plugins/          # Plugin configuration
├── projects/         # Project-specific conversations
├── session-env/      # Session environment data
├── shell-snapshots/  # Shell state snapshots
├── statsig/          # Statistics and feature flags
├── todos/            # Todo list persistence
├── history.jsonl     # Global conversation history
├── settings.json     # Global settings
└── CLAUDE.md         # Project-specific instructions

```

## Key Findings

- **Conversation data** is stored in JSONL format with one JSON object per line
- **Projects** are organized in separate directories with encoded path names
- **Settings** persist user preferences and configuration across sessions
- **Custom commands and agents** extend Claude Code functionality via markdown definitions
- **State data** (todos, shell snapshots, session env) enables session persistence
- **Debug logs** provide detailed execution traces for troubleshooting

## How to Use This Documentation

1. Start with the component you're interested in from the sections above
2. Each component's README contains:
   - Purpose and responsibility
   - Statistics (file counts, sizes, dates)
   - Data structure and schema documentation
   - Temporal evolution analysis
   - Sanitized examples from real data
