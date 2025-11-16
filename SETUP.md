# Flask Web Viewer - Setup Guide

The Flask web application provides a beautiful, interactive interface for viewing and sharing Claude Code conversation histories.

## Features

- **Project Selection** - Browse all conversation projects from `~/.claude/projects`
- **Interactive Viewer** - Collapsible, nested message display with syntax highlighting
- **Multiple Themes** - ChatGPT (default), GitHub, Slack, and Minimal themes
- **Export to HTML** - Generate standalone, shareable HTML files
- **Path Sanitization** - Toggle-able privacy protection (default: OFF)
- **Statistics Dashboard** - Message counts, types, sessions, and agents
- **Keyboard Shortcuts** - Fast navigation and control
- **Performance Caching** - Fast loading for large conversations

## Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- git

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Looking4OffSwitch/claude-conversation-analysis.git

# Navigate to the project directory
cd claude-conversation-analysis
```

### Step 2: Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 3: Install Dependencies

```bash
# Install all dependencies (Flask and dev tools like Gunicorn)
# This automatically creates a .venv virtual environment if it doesn't exist
uv sync

# Or install only core dependencies (Flask only, without dev tools)
uv sync --no-dev
```

### Required Packages

- **Flask** - Web framework
- **Jinja2** - Template engine (included with Flask)

### Optional Dependencies

- **Gunicorn** - Production WSGI server (installed automatically with `uv sync`)

## Configuration

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

### Configuration Options

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

## Starting the Web Server

### Basic Usage

```bash
# From the project root (claude-conversation-analysis)
python flask_app/app.py
```

The server will start on `http://127.0.0.1:5000` by default.

### Alternative Methods

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
# Gunicorn is installed automatically with 'uv sync'
# Run with 4 worker processes
gunicorn -w 4 -b 127.0.0.1:5000 flask_app.app:app
```

## Using the Web Interface

### 1. Project Selection Page

Navigate to `http://127.0.0.1:5000` to see:
- Grid of all available conversation projects
- File count for each project
- View and Export buttons
- Theme selector in navbar
- Sanitization toggle in navbar
- Cache statistics and controls

### 2. Viewing Conversations

Click "View Conversation" to see:
- **Main Timeline** - All messages in chronological order
- **Statistics Sidebar** - Message counts, types, sessions, agents
- **Collapsible Sections** - Click to expand/collapse nested content
- **Message Types** - Color-coded icons (user, assistant, tool, system)
- **Code Blocks** - Syntax highlighted with copy buttons
- **Metadata** - Expandable details (UUID, timestamps, session info)

### 3. Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `E` | Expand all messages |
| `C` | Collapse all messages |
| `T` | Scroll to top |
| `B` | Scroll to bottom |
| `Alt + ↓` | Navigate to next message |
| `Alt + ↑` | Navigate to previous message |
| `?` | Show keyboard shortcuts help |

### 4. Exporting Conversations

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

### 5. Theme Switching

Use the theme dropdown in the navbar:
- **ChatGPT** (Default) - Speech bubble interface, modern design
- **GitHub** - Linear discussion style (coming soon)
- **Slack** - Dense timeline style (coming soon)
- **Minimal** - Clean documentation style (coming soon)

Theme selection persists in URL query parameters and can be changed anytime.

### 6. Path Sanitization

Toggle the "Sanitize Paths" checkbox:
- **OFF** (Default) - Show original file paths (e.g., `/Users/Reed/dev/project/file.py`)
- **ON** - Sanitize for privacy (e.g., `/Users/<USER>/dev/<PROJECT>/file.py`)

Useful when sharing conversations publicly or taking screenshots.

### 7. Cache Management

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

## Troubleshooting

**Issue: "No projects found"**
- Check that `~/.claude/projects` directory exists
- Verify conversation files are in JSONL format
- Check server logs for permission errors

**Issue: "500 Internal Server Error"**
- Check Flask server logs for error details
- Verify all dependencies are installed
- Try clearing cache: `rm -rf flask_app/cache`

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

## Development Tips

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

## Security Considerations

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

## Performance

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

## Directory Structure

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

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/Looking4OffSwitch/claude-conversation-analysis).
