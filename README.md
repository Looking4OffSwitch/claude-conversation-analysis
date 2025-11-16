# Claude Conversation Analysis Project

This project provides comprehensive documentation and analysis tools for Claude Code conversation data stored in the `conversations/.claude` directory.

## Project Overview

This repository contains:
- **Conversation Data**: Claude Code conversation histories and configuration
- **Analysis Tools**: Python-based tools for analyzing conversation structure
- **Research Documentation**: Comprehensive markdown documentation of all components

## Quick Start

### Running the Analysis

To analyze the conversation data and generate documentation:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the analysis
python tools/analyze_all.py
```

This will:
1. Analyze all subfolders in `conversations/.claude`
2. Extract schemas from JSONL files
3. Generate statistics and temporal analysis
4. Create sanitized examples
5. Output comprehensive markdown documentation to `./research/`

### Viewing Results

After running the analysis, view the documentation:

```bash
# Open the master README
open research/README.md

# Or browse individual component documentation
open research/projects/README.md
open research/history/README.md
```

## Project Structure

```
claude_conversation/
├── .gitignore                    # Git ignore rules
├── .venv/                        # Python virtual environment
├── CLAUDE.md                     # Instructions for Claude Code
├── README.md                     # This file
│
├── conversations/                # Conversation data (ignored by git)
│   └── .claude/                  # Claude Code data directory
│       ├── agents/               # Custom agent definitions
│       ├── commands/             # Custom slash commands
│       ├── debug/                # Debug logs
│       ├── file-history/         # File version history
│       ├── ide/                  # IDE integration
│       ├── plugins/              # Plugin config
│       ├── projects/             # Project conversations
│       ├── session-env/          # Session state
│       ├── shell-snapshots/      # Shell snapshots
│       ├── statsig/              # Statistics
│       ├── todos/                # Todo persistence
│       ├── history.jsonl         # Global history
│       └── settings.json         # Global settings
│
├── research/                     # Generated documentation
│   ├── README.md                 # Master documentation index
│   ├── agents/                   # Agent analysis
│   ├── commands/                 # Commands analysis
│   ├── debug/                    # Debug analysis
│   ├── file-history/             # File history analysis
│   ├── history/                  # Global history analysis
│   ├── ide/                      # IDE integration analysis
│   ├── plugins/                  # Plugins analysis
│   ├── projects/                 # Projects analysis
│   ├── session-env/              # Session env analysis
│   ├── settings/                 # Settings analysis
│   ├── shell-snapshots/          # Shell snapshots analysis
│   ├── statsig/                  # Statsig analysis
│   └── todos/                    # Todos analysis
│
└── tools/                        # Analysis tools
    ├── __init__.py               # Package initialization
    ├── analyze_all.py            # Master analysis script
    ├── analyze_json_files.py     # JSON file analyzer
    ├── analyze_jsonl_files.py    # JSONL file analyzer
    ├── analyze_markdown_folders.py # Markdown analyzer
    ├── analyze_misc_folders.py   # Misc folders analyzer
    ├── base_analyzer.py          # Base analyzer class
    ├── config.py                 # Configuration constants
    ├── file_utils.py             # File utilities
    ├── json_parser.py            # JSON/JSONL parser
    ├── logger.py                 # Logging utilities
    ├── markdown_generator.py     # Markdown generation
    └── sanitizer.py              # Data sanitization
```

## Analysis Tools

### Core Modules

1. **config.py** - Centralized configuration constants
2. **logger.py** - Logging setup and utilities
3. **file_utils.py** - File statistics and temporal analysis
4. **json_parser.py** - JSON/JSONL parsing with schema extraction
5. **sanitizer.py** - Data sanitization (removes sensitive paths)
6. **markdown_generator.py** - Markdown report generation
7. **base_analyzer.py** - Abstract base class for all analyzers

### Analyzer Scripts

1. **analyze_markdown_folders.py** - Analyzes `agents/` and `commands/`
2. **analyze_json_files.py** - Analyzes `settings.json` and `plugins/`
3. **analyze_jsonl_files.py** - Analyzes `history.jsonl`, `projects/`, `todos/`
4. **analyze_misc_folders.py** - Analyzes `debug/`, `session-env/`, `shell-snapshots/`, etc.
5. **analyze_all.py** - Master script that orchestrates all analyzers

## Code Quality Standards

All code follows modern software engineering best practices:

- **DRY (Don't Repeat Yourself)**: Shared functionality in reusable modules
- **Encapsulation**: Clear module boundaries and responsibilities
- **Abstraction**: Base classes for common patterns
- **Error Handling**: Comprehensive try/except with logging
- **Parameter Validation**: All function inputs validated
- **Type Hints**: Python type annotations throughout
- **Documentation**: Docstrings for all classes and functions
- **Logging**: Verbose logging for debugging
- **Code Readability**: Clear naming and structure

## Generated Documentation

Each component's documentation includes:

1. **Purpose & Responsibility** - What the component does
2. **Statistics** - File counts, sizes, date ranges
3. **Data Structure**:
   - Abstract description
   - JSON Schema (for structured data)
   - Field-by-field documentation
4. **Temporal Evolution** - How data changes over time
5. **Examples** - Sanitized real-world examples

### Data Sanitization

All examples have sensitive information sanitized:
- User paths: `/Users/Reed/` → `/Users/<USER>/`
- Project paths: `/Users/Reed/dev/my-project/` → `/Users/<USER>/dev/<PROJECT>/`

## Statistics

- **Total Code**: ~3,300 lines of Python
- **Components Analyzed**: 13
- **Documentation Files**: 14 markdown files
- **Conversation Files Analyzed**: 180+ JSONL files
- **Schemas Extracted**: Multiple comprehensive JSON schemas

## Usage Examples

### Analyze a Specific Component

```python
from tools.analyze_jsonl_files import JsonlFileAnalyzer
from pathlib import Path

analyzer = JsonlFileAnalyzer(
    folder_name="my_analysis",
    purpose_description="Custom analysis",
    file_path=Path("path/to/file.jsonl")
)

report_path = analyzer.run()
print(f"Report generated: {report_path}")
```

### Extract Schema from JSONL

```python
from tools.json_parser import extract_schema_from_jsonl
from pathlib import Path

custom_schema, json_schema = extract_schema_from_jsonl(
    Path("conversations/.claude/history.jsonl")
)

print(json_schema)
```

### Sanitize Data

```python
from tools.sanitizer import sanitize_data

data = {
    "path": "/Users/Reed/dev/my-project/file.txt",
    "content": "Some content"
}

sanitized = sanitize_data(data)
# Result: {"path": "/Users/<USER>/dev/<PROJECT>/file.txt", "content": "Some content"}
```

## Contributing

When modifying the analysis tools:

1. Follow the existing code style and patterns
2. Add comprehensive docstrings
3. Include error handling with logging
4. Validate all function parameters
5. Update this README if adding new features

## Future Enhancements

Potential improvements:
- Add support for analyzing additional file formats
- Create visualization tools for conversation flow
- Add timeline analysis of conversation patterns
- Generate summary statistics across all projects
- Create interactive HTML documentation

## License

This is a personal analysis tool for Claude Code conversation data.
