"""
Flask application configuration.

This module contains all configuration settings for the conversation viewer application.
"""

import os
from pathlib import Path


# Base paths
BASE_DIR = Path(__file__).parent.parent
CONVERSATIONS_DIR = BASE_DIR / "conversations" / ".claude" / "projects"
CACHE_DIR = BASE_DIR / "flask_app" / "cache"
EXPORT_DIR = BASE_DIR / "flask_app" / "exports"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
PORT = int(os.environ.get('FLASK_PORT', 5000))

# Application settings
DEFAULT_THEME = 'chatgpt'
AVAILABLE_THEMES = ['chatgpt', 'github', 'slack', 'minimal']

# Sanitization settings
DEFAULT_SANITIZE = False  # Default to not sanitizing
SANITIZE_PATTERNS = {
    'user_path': r'/Users/[^/]+',
    'user_placeholder': '/Users/<USER>',
    'project_path': r'/Users/[^/]+/dev/[^/\s\"\'\)\]\}]+',
    'project_placeholder': '/Users/<USER>/dev/<PROJECT>',
}

# Cache settings
CACHE_ENABLED = True
CACHE_TTL_SECONDS = 3600  # 1 hour

# Display settings
MAX_TOOL_RESULT_LINES = 50  # Lines to show before "expand" button
SYNTAX_HIGHLIGHTING = True
SHOW_TIMESTAMPS = True
SHOW_METADATA = True

# Export settings
EXPORT_INLINE_ASSETS = True  # Embed CSS/JS in exported HTML
EXPORT_SANITIZE_DEFAULT = True  # Default to sanitized for exports

# Message type display configuration
MESSAGE_TYPE_CONFIG = {
    'user': {
        'icon': '👤',
        'label': 'User',
        'color': '#10a37f',
        'align': 'right'
    },
    'assistant': {
        'icon': '🤖',
        'label': 'Assistant',
        'color': '#6e6e80',
        'align': 'left'
    },
    'tool_use': {
        'icon': '🔧',
        'label': 'Tool',
        'color': '#ff6b6b',
        'collapsible': True
    },
    'tool_result': {
        'icon': '📤',
        'label': 'Result',
        'color': '#4dabf7',
        'collapsible': True
    },
    'system': {
        'icon': 'ℹ️',
        'label': 'System',
        'color': '#adb5bd',
        'subtle': True
    },
    'file-history-snapshot': {
        'icon': '📸',
        'label': 'Snapshot',
        'color': '#868e96',
        'collapsible': True
    }
}

# Tool name mapping for better display
TOOL_DISPLAY_NAMES = {
    'Read': '📖 Read File',
    'Write': '✏️ Write File',
    'Edit': '✂️ Edit File',
    'Bash': '💻 Run Command',
    'Glob': '🔍 Find Files',
    'Grep': '🔎 Search Code',
    'Task': '🎯 Launch Agent',
    'WebFetch': '🌐 Fetch URL',
    'WebSearch': '🔍 Web Search',
}


def validate_config():
    """
    Validate configuration settings.

    Raises:
        ValueError: If configuration is invalid.
    """
    if not CONVERSATIONS_DIR.exists():
        raise ValueError(
            f"Conversations directory not found: {CONVERSATIONS_DIR}. "
            "Please ensure the .claude directory exists."
        )

    if DEFAULT_THEME not in AVAILABLE_THEMES:
        raise ValueError(
            f"Invalid default theme: {DEFAULT_THEME}. "
            f"Must be one of {AVAILABLE_THEMES}"
        )

    return True


if __name__ == "__main__":
    print("Configuration Validation")
    print("=" * 50)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Conversations: {CONVERSATIONS_DIR}")
    print(f"Cache Directory: {CACHE_DIR}")
    print(f"Export Directory: {EXPORT_DIR}")
    print(f"Default Theme: {DEFAULT_THEME}")
    print(f"Available Themes: {', '.join(AVAILABLE_THEMES)}")
    print()

    try:
        validate_config()
        print("✓ Configuration valid")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
