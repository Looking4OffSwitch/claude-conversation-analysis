"""
Configuration constants for the Claude conversation analysis tools.

This module contains all configuration constants used across the analysis scripts,
following the DRY principle by centralizing configuration in one location.
"""

import os
from pathlib import Path
from typing import Final

# Base paths
BASE_DIR: Final[Path] = Path(__file__).parent.parent
CONVERSATIONS_DIR: Final[Path] = BASE_DIR / "conversations" / ".claude"
RESEARCH_DIR: Final[Path] = BASE_DIR / "research"
TOOLS_DIR: Final[Path] = BASE_DIR / "tools"

# Logging configuration
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL: Final[str] = "INFO"

# Sanitization patterns
SANITIZE_PATTERNS: Final[dict[str, str]] = {
    "user_home": r"/Users/[^/]+",
    "user_placeholder": "/Users/<USER>",
    "project_path": r"/Users/[^/]+/dev/[^/\s\"']+",
    "project_placeholder": "/Users/<USER>/dev/<PROJECT>",
}

# Analysis configuration
MAX_FILE_SIZE_MB: Final[int] = 100  # Maximum file size to process in MB
SAMPLE_SIZE_LARGE_FILES: Final[int] = 100  # Number of entries to sample from large files
MIN_EXAMPLES_PER_STRUCTURE: Final[int] = 3  # Minimum examples to show for each data structure

# JSONL configuration
MAX_LINES_TO_ANALYZE: Final[int] = 1000  # Maximum lines to analyze for schema extraction
JSONL_ENCODING: Final[str] = "utf-8"

# Markdown generation
MARKDOWN_HEADER_LEVEL: Final[int] = 1  # Starting header level for generated markdown
CODE_BLOCK_LANGUAGE: Final[str] = "json"  # Language for code blocks

# File extensions to analyze
ANALYZED_EXTENSIONS: Final[set[str]] = {
    ".jsonl",
    ".json",
    ".md",
    ".log",
    ".txt",
    ".lock",
}


def validate_config() -> bool:
    """
    Validate that all required directories exist.

    Returns:
        bool: True if all required directories exist, False otherwise.

    Raises:
        ValueError: If critical directories are missing.
    """
    if not CONVERSATIONS_DIR.exists():
        raise ValueError(
            f"Conversations directory not found: {CONVERSATIONS_DIR}. "
            "Please ensure you're running this script from the correct location."
        )

    # Create research directory if it doesn't exist
    RESEARCH_DIR.mkdir(exist_ok=True, parents=True)

    return True


if __name__ == "__main__":
    # Test configuration
    print("Configuration Test")
    print("=" * 50)
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"CONVERSATIONS_DIR: {CONVERSATIONS_DIR}")
    print(f"RESEARCH_DIR: {RESEARCH_DIR}")
    print(f"TOOLS_DIR: {TOOLS_DIR}")
    print(f"\nValidating configuration...")

    try:
        validate_config()
        print("✓ Configuration valid")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
