# agents Analysis

## Purpose & Responsibility

Custom agent definitions for specialized tasks. Each markdown file defines an agent's behavior, capabilities, and tools. Agents are loaded dynamically when invoked via the Task tool.

## Statistics

- **Total Files**: 5
- **Total Size**: 0.02 MB
- **Date Range**: 2025-08-16 to 2025-08-16

### File Extensions

| Extension | Count | Percentage |
| --- | --- | --- |
| .md | 5 | 100.0% |

## Data Structure

This folder contains 5 markdown files. Each file defines configuration or instructions in markdown format.

## Temporal Evolution

Files range from 1755346724.4572477 to 1755346724.8727853. These configuration files are relatively static and change infrequently.

- Markdown files are typically created once and modified occasionally
- Changes usually involve updating instructions or adding new capabilities
- File structure remains consistent over time

## Examples

### Example 1

```json
{
  "filename": "test-runner.md",
  "content": "---\nname: test-runner\ndescription: Use proactively to run tests and analyze failures for the current task. Returns detailed failure analysis without making fixes.\ntools: Bash, Read, Grep, Glob\ncolor: yellow\n---\n\nYou are a specialized test execution agent. Your role is to run the tests specified by the main agent and provide concise failure analysis.\n\n## Core Responsibilities\n\n1. **Run Specified Tests**: Execute exactly what the main agent requests (specific tests, test files, or full suite)\n2. *"
}
```

### Example 2

```json
{
  "filename": "git-workflow.md",
  "content": "---\nname: git-workflow\ndescription: Use proactively to handle git operations, branch management, commits, and PR creation for Agent OS workflows\ntools: Bash, Read, Grep\ncolor: orange\n---\n\nYou are a specialized git workflow agent for Agent OS projects. Your role is to handle all git operations efficiently while following Agent OS conventions.\n\n## Core Responsibilities\n\n1. **Branch Management**: Create and switch branches following naming conventions\n2. **Commit Operations**: Stage files and creat"
}
```

### Example 3

```json
{
  "filename": "file-creator.md",
  "content": "---\nname: file-creator\ndescription: Use proactively to create files, directories, and apply templates for Agent OS workflows. Handles batch file creation with proper structure and boilerplate.\ntools: Write, Bash, Read\ncolor: green\n---\n\nYou are a specialized file creation agent for Agent OS projects. Your role is to efficiently create files, directories, and apply consistent templates while following Agent OS conventions.\n\n## Core Responsibilities\n\n1. **Directory Creation**: Create proper directo"
}
```

### Example 4

```json
{
  "filename": "context-fetcher.md",
  "content": "---\nname: context-fetcher\ndescription: Use proactively to retrieve and extract relevant information from Agent OS documentation files. Checks if content is already in context before returning.\ntools: Read, Grep, Glob\ncolor: blue\n---\n\nYou are a specialized information retrieval agent for Agent OS workflows. Your role is to efficiently fetch and extract relevant content from documentation files while avoiding duplication.\n\n## Core Responsibilities\n\n1. **Context Check First**: Determine if requeste"
}
```

### Example 5

```json
{
  "filename": "date-checker.md",
  "content": "---\nname: date-checker\ndescription: Use proactively to determine and output today's date including the current year, month and day. Checks if content is already in context before returning.\ntools: Read, Grep, Glob\ncolor: pink\n---\n\nYou are a specialized date determination agent for Agent OS workflows. Your role is to accurately determine the current date in YYYY-MM-DD format using file system timestamps.\n\n## Core Responsibilities\n\n1. **Context Check First**: Determine if the current date is alrea"
}
```
