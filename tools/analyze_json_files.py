"""
Analyzer for JSON configuration files (settings.json, plugins/config.json).

This module analyzes JSON configuration files and generates documentation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from base_analyzer import BaseAnalyzer
from logger import setup_logger
from json_parser import parse_json_file
from sanitizer import sanitize_data


logger = setup_logger(__name__)


class JsonFileAnalyzer(BaseAnalyzer):
    """Analyzer for single JSON configuration files."""

    def __init__(self, folder_name: str, purpose_description: str, relative_file_path: str = ""):
        """
        Initialize the JSON file analyzer.

        Args:
            folder_name: Name for output folder.
            purpose_description: Description of the file's purpose.
            relative_file_path: Path relative to CONVERSATIONS_DIR (empty for root files).
        """
        super().__init__(folder_name)
        self.purpose_description = purpose_description
        self.relative_file_path = relative_file_path

        # Override source_dir for root-level files
        if not relative_file_path:
            # This is a root-level file like settings.json
            self.source_file = self.source_dir
        else:
            self.source_file = self.source_dir / relative_file_path

    def get_purpose(self) -> str:
        """Get the purpose and responsibility of this file."""
        return self.purpose_description

    def analyze_data_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the JSON file."""
        self.logger.info(f"Analyzing JSON structure: {self.source_file}")

        if not self.source_file.exists():
            return {
                "description": f"File {self.source_file} does not exist.",
                "schema": {}
            }

        try:
            data = parse_json_file(self.source_file)

            # Extract schema by analyzing the structure
            schema = self._extract_schema(data)

            structure = {
                "description": f"JSON configuration file with {len(data)} top-level keys." if isinstance(data, dict) else "JSON file (not a dict)",
                "schema": schema,
                "top_level_keys": list(data.keys()) if isinstance(data, dict) else [],
                "structure_type": type(data).__name__
            }

            return structure

        except Exception as e:
            self.logger.error(f"Error analyzing {self.source_file}: {e}")
            return {
                "description": f"Error analyzing file: {e}",
                "schema": {}
            }

    def _extract_schema(self, obj: Any, depth: int = 0, max_depth: int = 5) -> Dict[str, Any]:
        """
        Recursively extract schema from a JSON object.

        Args:
            obj: Object to analyze.
            depth: Current recursion depth.
            max_depth: Maximum recursion depth.

        Returns:
            Dict[str, Any]: Schema description.
        """
        if depth > max_depth:
            return {"type": type(obj).__name__, "note": "Max depth reached"}

        if isinstance(obj, dict):
            schema = {}
            for key, value in obj.items():
                schema[key] = self._extract_schema(value, depth + 1, max_depth)
            return {
                "type": "object",
                "properties": schema
            }
        elif isinstance(obj, list):
            if obj:
                # Analyze first item
                item_schema = self._extract_schema(obj[0], depth + 1, max_depth)
                return {
                    "type": "array",
                    "items": item_schema,
                    "example_length": len(obj)
                }
            else:
                return {"type": "array", "items": "unknown", "length": 0}
        else:
            return {
                "type": type(obj).__name__,
                "example": obj if not isinstance(obj, str) or len(str(obj)) < 100 else str(obj)[:100] + "..."
            }

    def analyze_temporal_evolution(self) -> Dict[str, Any]:
        """Analyze how the JSON file changes over time."""
        self.logger.info(f"Analyzing temporal evolution: {self.source_file}")

        if not self.source_file.exists():
            return {
                "description": "File does not exist.",
                "changes": []
            }

        try:
            stat = self.source_file.stat()

            evolution = {
                "description": "Configuration files are modified when settings change. "
                             "The structure typically remains stable with values being updated.",
                "file_age_days": (Path(__file__).stat().st_mtime - stat.st_ctime) / 86400,
                "last_modified": stat.st_mtime,
                "changes": [
                    "Configuration files are updated when user changes settings",
                    "New keys may be added as new features are introduced",
                    "Values are modified to reflect current configuration",
                    "File structure remains relatively stable over time"
                ]
            }

            return evolution

        except Exception as e:
            self.logger.error(f"Error analyzing temporal evolution: {e}")
            return {
                "description": f"Error: {e}",
                "changes": []
            }

    def get_examples(self) -> List[Any]:
        """Get sanitized examples from the JSON file."""
        self.logger.info(f"Collecting example from: {self.source_file}")

        if not self.source_file.exists():
            return []

        try:
            data = parse_json_file(self.source_file)
            sanitized = sanitize_data(data)

            return [sanitized]

        except Exception as e:
            self.logger.error(f"Error getting example: {e}")
            return []


class PluginsAnalyzer(JsonFileAnalyzer):
    """Specialized analyzer for plugins folder."""

    def __init__(self):
        super().__init__(
            folder_name="plugins",
            purpose_description="Plugin configuration for Claude Code extensions. "
                              "Contains config.json which defines enabled plugins and their settings.",
            relative_file_path="config.json"
        )

    def analyze_data_structure(self) -> Dict[str, Any]:
        """Analyze plugins structure including all files in the folder."""
        # First get the base JSON analysis
        structure = super().analyze_data_structure()

        # Also check for other files in the plugins directory
        parent_dir = self.source_file.parent if self.source_file.is_file() else self.source_file

        if parent_dir.exists():
            all_files = list(parent_dir.glob("*"))
            structure["all_files"] = [f.name for f in all_files if f.is_file()]

        return structure


if __name__ == "__main__":
    import sys
    from config import CONVERSATIONS_DIR

    # Analyze settings.json
    print("Analyzing settings.json...")
    settings_analyzer = JsonFileAnalyzer(
        folder_name="settings",
        purpose_description="Global Claude Code settings including status line configuration, "
                          "feature flags, and user preferences. This file persists settings across sessions.",
        relative_file_path=""
    )
    # Override source_file to point to settings.json
    settings_analyzer.source_file = CONVERSATIONS_DIR / "settings.json"
    settings_analyzer.run()

    # Analyze plugins
    print("\nAnalyzing plugins...")
    plugins_analyzer = PluginsAnalyzer()
    plugins_analyzer.run()

    print("\nJSON file analysis complete!")
