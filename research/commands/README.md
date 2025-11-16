# commands Analysis

## Purpose & Responsibility

Custom slash commands that expand into prompts. Each markdown file contains instructions that are injected into the conversation when the command is used. Commands provide reusable workflows and standardized prompts.

## Statistics

- **Total Files**: 5
- **Total Size**: 0.00 MB
- **Date Range**: 2025-08-16 to 2025-08-18

### File Extensions

| Extension | Count | Percentage |
| --- | --- | --- |
| .md | 5 | 100.0% |

## Data Structure

This folder contains 5 markdown files. Each file defines configuration or instructions in markdown format.

## Temporal Evolution

Files range from 1755346724.0504696 to 1755523356.8996656. These configuration files are relatively static and change infrequently.

- Markdown files are typically created once and modified occasionally
- Changes usually involve updating instructions or adding new capabilities
- File structure remains consistent over time

## Examples

### Example 1

```json
{
  "filename": "analyze-product.md",
  "content": "# Analyze Product\n\nAnalyze your product's codebase and install Agent OS\n\nRefer to the instructions located in @~/.agent-os/instructions/core/analyze-product.md\n"
}
```

### Example 2

```json
{
  "filename": "execute-tasks.md",
  "content": "# Execute Task\n\nExecute the next task.\n\nRefer to the instructions located in @~/.agent-os/instructions/core/execute-tasks.md\n"
}
```

### Example 3

```json
{
  "filename": "plan-product.md",
  "content": "# Plan Product\n\nPlan a new product and install Agent OS in its codebase.\n\nRefer to the instructions located in @~/.agent-os/instructions/core/plan-product.md\n"
}
```

### Example 4

```json
{
  "filename": "reed-review.md",
  "content": "Please ensure all of the code adheres to modern software engineering practices. \n\nThe includes \"don't repeat yourself (DRY)\", encapsulation, abstraction, rigorous error checking& handling, loose coupling, parameter validation, verbose logging to make debugging easier, and code readability and code comments.\n\nAny dead code or old files that we no longer need should be removed.\n\nDO NOT BREAK ANY FUNCTIONALITY!!\n"
}
```

### Example 5

```json
{
  "filename": "create-spec.md",
  "content": "# Create Spec\n\nCreate a detailed spec for a new feature with technical specifications and task breakdown\n\nRefer to the instructions located in @~/.agent-os/instructions/core/create-spec.md\n"
}
```
