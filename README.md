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
# Install dependencies (if not already installed)
uv sync

# Run the analysis using uv
uv run python tools/analyze_all.py

# Or activate the virtual environment and run directly
source .venv/bin/activate
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
├── .venv/                        # Python virtual environment (managed by uv)
├── pyproject.toml                # Project dependencies (uv configuration)
├── CLAUDE.md                     # Instructions for Claude Code
├── README.md                     # This file
├── TASKS.md                      # Development task tracking
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
├── flask_app/                    # Web viewer application
│   ├── app.py                    # Main Flask application
│   ├── config.py                 # Configuration settings
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── conversation_parser.py  # Parse JSONL files
│   │   ├── tree_builder.py         # Build message hierarchy
│   │   ├── cache_manager.py        # Performance caching
│   │   └── sanitizer.py            # Path sanitization
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html             # Base layout
│   │   ├── index.html            # Project selection
│   │   ├── conversation.html     # Main viewer
│   │   ├── export.html           # Standalone export
│   │   ├── 404.html              # Not found error
│   │   └── 500.html              # Server error
│   └── static/                   # Static assets
│       ├── css/
│       │   └── base.css          # Common styles
│       ├── themes/
│       │   ├── chatgpt.css       # ChatGPT theme
│       │   ├── github.css        # GitHub theme (TODO)
│       │   ├── slack.css         # Slack theme (TODO)
│       │   └── minimal.css       # Minimal theme (TODO)
│       └── js/
│           └── interactions.js   # Core JavaScript
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

## Flask Web Viewer

The Flask web application provides a beautiful, interactive interface for viewing and sharing Claude Code conversation histories.

### Features

- **Project Selection** - Browse all conversation projects from `~/.claude/projects`
- **Interactive Viewer** - Collapsible, nested message display with syntax highlighting
- **Multiple Themes** - ChatGPT (default), GitHub, Slack, and Minimal themes
- **Export to HTML** - Generate standalone, shareable HTML files
- **Path Sanitization** - Toggle-able privacy protection (default: OFF)
- **Statistics Dashboard** - Message counts, types, sessions, and agents
- **Keyboard Shortcuts** - Fast navigation and control
- **Performance Caching** - Fast loading for large conversations

### Installation

#### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

#### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

#### Install Dependencies

```bash
# Navigate to the project root
cd /path/to/claude_conversation

# Install all dependencies (Flask and optional dev tools)
uv sync

# Or install only core dependencies (Flask only)
uv pip install -e .
```

#### Required Packages

- **Flask** - Web framework
- **Jinja2** - Template engine (included with Flask)

#### Optional Dependencies

- **Gunicorn** - Production WSGI server (install with `uv sync` or `uv pip install gunicorn`)

### Configuration

The Flask app uses sensible defaults but can be customized via `flask_app/config.py`:

```python
# Default theme (chatgpt, github, slack, minimal)
DEFAULT_THEME = 'chatgpt'

# Default sanitization setting (True/False)
DEFAULT_SANITIZE = False  # OFF for local use

# Cache settings
CACHE_ENABLED = True
CACHE_DIR = '.cache'
CACHE_TTL_SECONDS = 3600  # 1 hour

# Server settings
DEBUG = True  # Set to False in production
HOST = '127.0.0.1'
PORT = 5000
```

#### Configuration Options

**CONVERSATIONS_DIR** - Path to Claude Code data directory
- Default: `~/.claude` (auto-detected)
- Override: Set environment variable `CLAUDE_CONVERSATIONS_DIR`

**DEFAULT_THEME** - Default visual theme
- Options: `chatgpt`, `github`, `slack`, `minimal`
- Users can change theme via dropdown in the web UI

**DEFAULT_SANITIZE** - Default path sanitization
- `False` - Show original paths (recommended for local use)
- `True` - Sanitize paths for privacy

**CACHE_ENABLED** - Enable/disable caching
- `True` - Cache parsed conversations for faster loading
- `False` - Always parse from source (slower, but always fresh)

**CACHE_TTL_SECONDS** - Cache time-to-live
- Default: 3600 (1 hour)
- Cached data expires after this duration

### Starting the Web Server

#### Basic Usage

```bash
# Navigate to the project root
cd /path/to/claude_conversation

# Start the Flask development server
python flask_app/app.py
```

The server will start on `http://127.0.0.1:5000` by default.

#### Alternative Methods

**Method 1: Using Flask CLI**
```bash
# Set the Flask app
export FLASK_APP=flask_app/app.py

# Run in development mode
flask run

# Run on a different port
flask run --port 8080

# Make accessible on network
flask run --host 0.0.0.0
```

**Method 2: Using Python Module**
```bash
python -m flask_app.app
```

**Method 3: Production Server (Gunicorn)**
```bash
# Install gunicorn (if not already installed via uv sync)
uv pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 127.0.0.1:5000 flask_app.app:app
```

### Using the Web Interface

#### 1. Project Selection Page

Navigate to `http://127.0.0.1:5000` to see:
- Grid of all available conversation projects
- File count for each project
- View and Export buttons
- Theme selector in navbar
- Sanitization toggle in navbar
- Cache statistics and controls

#### 2. Viewing Conversations

Click "View Conversation" to see:
- **Main Timeline** - All messages in chronological order
- **Statistics Sidebar** - Message counts, types, sessions, agents
- **Collapsible Sections** - Click to expand/collapse nested content
- **Message Types** - Color-coded icons (user, assistant, tool, system)
- **Code Blocks** - Syntax highlighted with copy buttons
- **Metadata** - Expandable details (UUID, timestamps, session info)

#### 3. Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `E` | Expand all messages |
| `C` | Collapse all messages |
| `T` | Scroll to top |
| `B` | Scroll to bottom |
| `Alt + ↓` | Navigate to next message |
| `Alt + ↑` | Navigate to previous message |
| `?` | Show keyboard shortcuts help |

#### 4. Exporting Conversations

**Web Export:**
1. Click "Export HTML" button on project card
2. Browser downloads a standalone HTML file
3. File is fully self-contained (all CSS/JS inlined)
4. Can be shared via email, cloud storage, or web hosting

**Export Features:**
- Single HTML file with no external dependencies
- Includes export metadata (date, sanitization status)
- Full interactivity (collapse/expand, copy buttons)
- Same visual appearance as web viewer
- Print-friendly styles

#### 5. Theme Switching

Use the theme dropdown in the navbar:
- **ChatGPT** (Default) - Speech bubble interface, modern design
- **GitHub** - Linear discussion style (coming soon)
- **Slack** - Dense timeline style (coming soon)
- **Minimal** - Clean documentation style (coming soon)

Theme selection persists in URL query parameters and can be changed anytime.

#### 6. Path Sanitization

Toggle the "Sanitize Paths" checkbox:
- **OFF** (Default) - Show original file paths (e.g., `/Users/Reed/dev/project/file.py`)
- **ON** - Sanitize for privacy (e.g., `/Users/<USER>/dev/<PROJECT>/file.py`)

Useful when sharing conversations publicly or taking screenshots.

#### 7. Cache Management

**View Cache Stats:**
- Project selection page shows cached project count
- Displays cache size and last cleared date

**Clear Cache:**
- Click "Clear Cache" button on project selection page
- Refreshes all conversation data
- Useful after making changes to source files

**API Endpoints:**
```bash
# Get cache statistics
curl http://127.0.0.1:5000/api/cache/stats

# Clear cache
curl -X POST http://127.0.0.1:5000/api/cache/clear
```

### Troubleshooting

**Issue: "No projects found"**
- Check that `~/.claude/projects` directory exists
- Verify conversation files are in JSONL format
- Check server logs for permission errors

**Issue: "500 Internal Server Error"**
- Check Flask server logs for error details
- Verify all dependencies are installed
- Try clearing cache: `rm -rf flask_app/.cache`

**Issue: "Slow loading for large conversations"**
- Ensure caching is enabled (`CACHE_ENABLED = True`)
- Increase cache TTL for frequently accessed projects
- Consider using a production server (Gunicorn)

**Issue: "Syntax highlighting not working"**
- Check browser console for JavaScript errors
- Verify Prism.js is loading (check Network tab)
- Try a hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

**Issue: "Theme not loading"**
- Verify theme CSS file exists in `flask_app/static/themes/`
- Check browser console for 404 errors
- Clear browser cache

### Development Tips

**Hot Reload:**
Flask development server auto-reloads on code changes:
```bash
python flask_app/app.py
# Edit files and refresh browser to see changes
```

**Debug Mode:**
Enable detailed error pages by setting in `config.py`:
```python
DEBUG = True
```

**Logging:**
View detailed logs by checking the console output or configuring logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Custom Themes:**
Create new themes by adding CSS files to `flask_app/static/themes/`:
1. Create `flask_app/static/themes/mytheme.css`
2. Add theme name to `AVAILABLE_THEMES` in `config.py`
3. Restart server and select theme from dropdown

### Security Considerations

**Local Use:**
- Default configuration is safe for local use
- Binds to `127.0.0.1` (localhost only)
- Not accessible from network

**Public Deployment:**
- Enable path sanitization by default (`DEFAULT_SANITIZE = True`)
- Use production WSGI server (Gunicorn, uWSGI)
- Set `DEBUG = False` in production
- Consider adding authentication (Flask-Login, etc.)
- Use HTTPS (reverse proxy with nginx/Apache)
- Review conversation content before sharing exports

**Privacy:**
- Conversations may contain sensitive information
- Use sanitization when sharing
- Review exported HTML before publishing
- Consider what metadata to include in exports

### Performance

**Optimization Tips:**
- Enable caching for faster subsequent loads
- Increase cache TTL for stable projects
- Use production WSGI server for better concurrency
- Consider pagination for extremely large conversations (1000+ messages)
- Use CDN for Prism.js in production

**Benchmarks:**
- Small conversation (50 messages): ~100ms load time
- Medium conversation (200 messages): ~300ms load time
- Large conversation (1000 messages): ~1s load time (with caching)

### Directory Structure

```
flask_app/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── conversation_parser.py  # Parse JSONL files
│   ├── tree_builder.py         # Build message hierarchy
│   ├── cache_manager.py        # Performance caching
│   └── sanitizer.py            # Path sanitization
├── templates/                  # Jinja2 templates
│   ├── base.html               # Base layout
│   ├── index.html              # Project selection
│   ├── conversation.html       # Main viewer
│   ├── export.html             # Standalone export
│   ├── 404.html                # Not found error
│   └── 500.html                # Server error
└── static/                     # Static assets
    ├── css/
    │   └── base.css            # Common styles
    ├── themes/
    │   ├── chatgpt.css         # ChatGPT theme
    │   ├── github.css          # GitHub theme (TODO)
    │   ├── slack.css           # Slack theme (TODO)
    │   └── minimal.css         # Minimal theme (TODO)
    └── js/
        └── interactions.js     # Core JavaScript

Note: Dependencies are managed via pyproject.toml in the project root.
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
