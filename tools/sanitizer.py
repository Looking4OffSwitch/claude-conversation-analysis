"""
Data sanitizer for removing sensitive information from examples.

This module provides functions to sanitize file paths, usernames, and other
potentially sensitive information while preserving the structure for documentation.
"""

import re
from typing import Any, Dict, Union

from logger import setup_logger
from config import SANITIZE_PATTERNS


# Initialize logger
logger = setup_logger(__name__)


def sanitize_string(text: str) -> str:
    """
    Sanitize a string by replacing sensitive information with placeholders.

    Args:
        text: The string to sanitize.

    Returns:
        str: Sanitized string with sensitive info replaced.

    Raises:
        ValueError: If text is None.
        TypeError: If text is not a string.
    """
    # Validate parameters
    if text is None:
        raise ValueError("text cannot be None")

    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text).__name__}")

    sanitized = text

    try:
        # Replace full project paths first (more specific)
        # Pattern: /Users/username/dev/project-name
        project_pattern = re.compile(
            r'/Users/[^/]+/dev/[^/\s\"\'\)\]\}]+',
            re.IGNORECASE
        )
        sanitized = project_pattern.sub(SANITIZE_PATTERNS["project_placeholder"], sanitized)

        # Then replace user home paths (less specific)
        # Pattern: /Users/username
        user_pattern = re.compile(
            r'/Users/[^/\s\"\'\)\]\}]+',
            re.IGNORECASE
        )
        # Only replace if not already part of the project placeholder
        if SANITIZE_PATTERNS["project_placeholder"] not in sanitized:
            sanitized = user_pattern.sub(SANITIZE_PATTERNS["user_placeholder"], sanitized)

        logger.debug(f"Sanitized string: '{text[:50]}...' -> '{sanitized[:50]}...'")

    except re.error as e:
        logger.error(f"Regex error during sanitization: {e}")
        raise

    return sanitized


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize all string values in a dictionary.

    Args:
        data: Dictionary to sanitize.

    Returns:
        Dict[str, Any]: New dictionary with sanitized values.

    Raises:
        ValueError: If data is None.
        TypeError: If data is not a dictionary.
    """
    # Validate parameters
    if data is None:
        raise ValueError("data cannot be None")

    if not isinstance(data, dict):
        raise TypeError(f"data must be a dict, got {type(data).__name__}")

    try:
        sanitized = {}

        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = sanitize_list(value)
            else:
                # Keep other types as-is (numbers, bools, None, etc.)
                sanitized[key] = value

        return sanitized

    except Exception as e:
        logger.error(f"Error sanitizing dictionary: {e}")
        raise


def sanitize_list(data: list) -> list:
    """
    Recursively sanitize all string values in a list.

    Args:
        data: List to sanitize.

    Returns:
        list: New list with sanitized values.

    Raises:
        ValueError: If data is None.
        TypeError: If data is not a list.
    """
    # Validate parameters
    if data is None:
        raise ValueError("data cannot be None")

    if not isinstance(data, list):
        raise TypeError(f"data must be a list, got {type(data).__name__}")

    try:
        sanitized = []

        for item in data:
            if isinstance(item, str):
                sanitized.append(sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(sanitize_list(item))
            else:
                # Keep other types as-is
                sanitized.append(item)

        return sanitized

    except Exception as e:
        logger.error(f"Error sanitizing list: {e}")
        raise


def sanitize_data(data: Union[str, dict, list, Any]) -> Union[str, dict, list, Any]:
    """
    Sanitize data of any type (string, dict, list, or other).

    This is the main entry point for sanitization. It dispatches to the
    appropriate specialized function based on the data type.

    Args:
        data: Data to sanitize (can be any type).

    Returns:
        Union[str, dict, list, Any]: Sanitized data of the same type.

    Raises:
        ValueError: If data is None.
    """
    # Validate parameters
    if data is None:
        raise ValueError("data cannot be None")

    try:
        if isinstance(data, str):
            return sanitize_string(data)
        elif isinstance(data, dict):
            return sanitize_dict(data)
        elif isinstance(data, list):
            return sanitize_list(data)
        else:
            # For other types (int, float, bool, None after the check above, etc.)
            # return as-is
            logger.debug(f"Data type {type(data).__name__} does not need sanitization")
            return data

    except Exception as e:
        logger.error(f"Error sanitizing data: {e}")
        raise


def add_custom_pattern(name: str, pattern: str, replacement: str) -> None:
    """
    Add a custom sanitization pattern.

    Args:
        name: Name identifier for the pattern.
        pattern: Regular expression pattern to match.
        replacement: Replacement string for matches.

    Raises:
        ValueError: If any parameter is None or empty.
        re.error: If pattern is not a valid regex.
    """
    # Validate parameters
    if not name:
        raise ValueError("name cannot be None or empty")

    if not pattern:
        raise ValueError("pattern cannot be None or empty")

    if replacement is None:
        raise ValueError("replacement cannot be None")

    # Test that pattern is valid regex
    try:
        re.compile(pattern)
    except re.error as e:
        logger.error(f"Invalid regex pattern '{pattern}': {e}")
        raise

    logger.info(f"Adding custom sanitization pattern: {name}")
    # Note: This modifies the global SANITIZE_PATTERNS, which is acceptable
    # for a utility module like this
    SANITIZE_PATTERNS[f"custom_{name}"] = replacement
    SANITIZE_PATTERNS[f"custom_{name}_pattern"] = pattern


if __name__ == "__main__":
    # Test the sanitizer
    print("Sanitizer Test")
    print("=" * 50)

    # Test string sanitization
    test_string = "/Users/Reed/dev/my-project/src/main.py"
    sanitized = sanitize_string(test_string)
    print(f"\nOriginal: {test_string}")
    print(f"Sanitized: {sanitized}")

    # Test dict sanitization
    test_dict = {
        "path": "/Users/Reed/dev/another-project/file.txt",
        "user": "Reed",
        "nested": {
            "location": "/Users/Reed/Documents/secret.txt"
        },
        "count": 42
    }
    sanitized_dict = sanitize_dict(test_dict)
    print(f"\nOriginal dict: {test_dict}")
    print(f"Sanitized dict: {sanitized_dict}")

    # Test list sanitization
    test_list = [
        "/Users/Reed/dev/project1",
        {"path": "/Users/Reed/dev/project2"},
        "normal string",
        123
    ]
    sanitized_list = sanitize_list(test_list)
    print(f"\nOriginal list: {test_list}")
    print(f"Sanitized list: {sanitized_list}")
