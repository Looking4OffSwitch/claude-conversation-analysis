"""
Data sanitizer for removing sensitive paths from conversation data.

This module provides sanitization functionality that can be toggled on/off.
"""

import re
from typing import Any, Union
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SANITIZE_PATTERNS


class DataSanitizer:
    """Sanitizes sensitive information from conversation data."""

    def __init__(self, enabled: bool = False):
        """
        Initialize sanitizer.

        Args:
            enabled: Whether sanitization is enabled.
        """
        self.enabled = enabled
        self.patterns = SANITIZE_PATTERNS

        # Compile regex patterns
        self.project_pattern = re.compile(
            self.patterns['project_path'],
            re.IGNORECASE
        )
        self.user_pattern = re.compile(
            self.patterns['user_path'],
            re.IGNORECASE
        )

    def sanitize(self, data: Any) -> Any:
        """
        Sanitize data if enabled, otherwise return as-is.

        Args:
            data: Data to potentially sanitize.

        Returns:
            Any: Sanitized or original data.
        """
        if not self.enabled:
            return data

        return self._sanitize_recursive(data)

    def _sanitize_recursive(self, data: Any) -> Any:
        """
        Recursively sanitize data structure.

        Args:
            data: Data to sanitize.

        Returns:
            Any: Sanitized data.
        """
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return {key: self._sanitize_recursive(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_recursive(item) for item in data]
        else:
            return data

    def _sanitize_string(self, text: str) -> str:
        """
        Sanitize a string by replacing sensitive paths.

        Args:
            text: String to sanitize.

        Returns:
            str: Sanitized string.
        """
        # Replace project paths first (more specific)
        sanitized = self.project_pattern.sub(
            self.patterns['project_placeholder'],
            text
        )

        # Then replace user paths (less specific)
        sanitized = self.user_pattern.sub(
            self.patterns['user_placeholder'],
            sanitized
        )

        return sanitized


if __name__ == "__main__":
    # Test sanitizer
    print("Data Sanitizer Test")
    print("=" * 60)

    test_data = {
        "cwd": "/Users/Reed/dev/my-project/src",
        "message": "Error in /Users/Reed/dev/my-project/main.py",
        "nested": {
            "path": "/Users/Reed/Documents/file.txt"
        },
        "list": [
            "/Users/Reed/dev/another-project/test",
            "normal string"
        ]
    }

    print("\nOriginal data:")
    print(test_data)

    # Test with sanitization disabled
    sanitizer_off = DataSanitizer(enabled=False)
    result_off = sanitizer_off.sanitize(test_data)
    print("\nWith sanitization OFF:")
    print(result_off)

    # Test with sanitization enabled
    sanitizer_on = DataSanitizer(enabled=True)
    result_on = sanitizer_on.sanitize(test_data)
    print("\nWith sanitization ON:")
    print(result_on)
