# Component Relationships Analysis

## Overview

This document provides a comprehensive analysis of relationships between different components in the Claude Code conversation data structure. Relationships are identified through shared identifiers (session IDs, conversation IDs, agent IDs, message UUIDs, project paths) and temporal correlations.

## Summary Statistics

- **Total Relationships Found**: 1
- **ID Sharing Relationships**: 1
- **Temporal Correlation Relationships**: 0
- **Components Analyzed**: 13

## Relationship Matrix

The following matrix shows which components have relationships with each other. Strength is indicated by the number of relationship types found.

| Component | agents | commands | debug | file-history | history | ide | plugins | projects | session-env | settings | shell-snapshots | statsig | todos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agents | - |  |  |  |  |  |  |  |  |  |  |  |  |
| commands |  | - |  |  |  |  |  |  |  |  |  |  |  |
| debug |  |  | - |  |  |  |  |  |  |  |  |  |  |
| file-history |  |  |  | - |  |  |  |  |  |  |  |  |  |
| history |  |  |  |  | - |  |  |  |  |  |  |  |  |
| ide |  |  |  |  |  | - |  |  |  |  |  |  |  |
| plugins |  |  |  |  |  |  | - |  |  |  |  |  |  |
| projects |  |  |  |  |  |  |  | - |  |  |  |  |  |
| session-env |  |  |  |  |  |  |  |  | - |  |  |  |  |
| settings |  |  |  |  |  |  |  |  |  | - |  |  |  |
| shell-snapshots |  |  |  |  |  |  |  |  |  |  | - |  |  |
| statsig |  |  |  |  |  |  |  |  |  |  |  | - |  |
| todos |  |  |  |  |  |  |  |  |  |  |  |  | - |

## Strongest Relationships

The following are the strongest relationships found, sorted by relationship strength:

### 1. debug ↔ .claude

**Type**: Id Sharing
**Strength**: 7.6%

**Details**: Shared Projects: 11

## Isolated Components

The following components have **no significant relationships** with other components:

- agents
- commands
- file-history
- history
- ide
- plugins
- projects
- session-env
- settings
- shell-snapshots
- statsig
- todos

*These components operate independently and do not share identifiers or have temporal correlations with other components.*

## Component Details

### agents

*No identifiers found*

### commands

*No identifiers found*

### debug

Agent IDs: 80, Message UUIDs: 135, Project Paths: 20

### file-history

*No identifiers found*

### history

Session IDs: 28, Project Paths: 27, Timestamps: 978

### ide

*No identifiers found*

### plugins

*No identifiers found*

### projects

Session IDs: 55, Agent IDs: 57, Message UUIDs: 11735, Project Paths: 18, Timestamps: 12416

### session-env

*No identifiers found*

### settings

*No identifiers found*

### shell-snapshots

*No identifiers found*

### statsig

*No identifiers found*

### todos

*No identifiers found*
