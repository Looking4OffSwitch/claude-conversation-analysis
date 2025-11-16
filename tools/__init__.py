"""
Claude Conversation Analysis Tools

This package provides utilities for analyzing Claude Code conversation history
and generating comprehensive documentation.
"""

__version__ = "1.0.0"
__author__ = "Claude Conversation Analyzer"

# Import main utilities for easy access
from .config import (
    BASE_DIR,
    CONVERSATIONS_DIR,
    RESEARCH_DIR,
    validate_config
)
from .logger import setup_logger, log_exception
from .file_utils import get_file_stats, get_directory_stats, get_temporal_samples
from .json_parser import (
    parse_jsonl_file,
    parse_json_file,
    extract_schema_from_jsonl,
    sample_jsonl_entries
)
from .sanitizer import sanitize_data, sanitize_string, sanitize_dict
from .markdown_generator import (
    MarkdownBuilder,
    generate_statistics_section,
    generate_schema_section,
    save_markdown
)

__all__ = [
    # Config
    'BASE_DIR',
    'CONVERSATIONS_DIR',
    'RESEARCH_DIR',
    'validate_config',
    # Logger
    'setup_logger',
    'log_exception',
    # File utils
    'get_file_stats',
    'get_directory_stats',
    'get_temporal_samples',
    # JSON parser
    'parse_jsonl_file',
    'parse_json_file',
    'extract_schema_from_jsonl',
    'sample_jsonl_entries',
    # Sanitizer
    'sanitize_data',
    'sanitize_string',
    'sanitize_dict',
    # Markdown generator
    'MarkdownBuilder',
    'generate_statistics_section',
    'generate_schema_section',
    'save_markdown',
]
