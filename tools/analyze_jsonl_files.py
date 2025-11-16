"""
Analyzer for JSONL files (history.jsonl, projects/*, todos/*).

This module analyzes JSONL conversation and state files and generates documentation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from base_analyzer import BaseAnalyzer
from logger import setup_logger
from json_parser import (
    parse_jsonl_file,
    extract_schema_from_jsonl,
    sample_jsonl_entries
)
from file_utils import get_temporal_samples
from sanitizer import sanitize_data
from config import SAMPLE_SIZE_LARGE_FILES


logger = setup_logger(__name__)


class JsonlFileAnalyzer(BaseAnalyzer):
    """Analyzer for single JSONL files."""

    def __init__(self, folder_name: str, purpose_description: str, file_path: Path):
        """
        Initialize the JSONL file analyzer.

        Args:
            folder_name: Name for output folder.
            purpose_description: Description of the file's purpose.
            file_path: Path to the JSONL file to analyze.
        """
        super().__init__(folder_name)
        self.purpose_description = purpose_description
        self.file_path = file_path

    def get_purpose(self) -> str:
        """Get the purpose and responsibility of this file."""
        return self.purpose_description

    def analyze_data_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the JSONL file."""
        self.logger.info(f"Analyzing JSONL structure: {self.file_path}")

        if not self.file_path.exists():
            return {
                "description": f"File {self.file_path} does not exist.",
                "schema": {}
            }

        try:
            # Extract schema
            custom_schema, json_schema = extract_schema_from_jsonl(self.file_path)

            # Get line count
            with open(self.file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for line in f if line.strip())

            structure = {
                "description": f"JSONL file with {line_count} entries. Each line is a separate JSON object.",
                "line_count": line_count,
                "custom_schema": custom_schema,
                "json_schema": json_schema
            }

            return structure

        except Exception as e:
            self.logger.error(f"Error analyzing {self.file_path}: {e}")
            return {
                "description": f"Error analyzing file: {e}",
                "schema": {}
            }

    def analyze_temporal_evolution(self) -> Dict[str, Any]:
        """Analyze how the JSONL file changes over time."""
        self.logger.info(f"Analyzing temporal evolution: {self.file_path}")

        if not self.file_path.exists():
            return {
                "description": "File does not exist.",
                "changes": []
            }

        try:
            # Sample entries from different time periods
            samples = sample_jsonl_entries(self.file_path, SAMPLE_SIZE_LARGE_FILES)

            # Compare first and last entries
            evolution = {
                "description": "JSONL files grow over time as new entries are appended. "
                             "Each entry represents a conversation turn or state change.",
                "total_entries": len(samples),
                "changes": [
                    "New entries are appended to the end of the file",
                    "Earlier entries represent older conversations/states",
                    "Later entries represent recent conversations/states",
                    "File grows linearly with usage over time"
                ]
            }

            if samples:
                evolution["first_entry_keys"] = list(samples[0].keys()) if isinstance(samples[0], dict) else []
                evolution["last_entry_keys"] = list(samples[-1].keys()) if isinstance(samples[-1], dict) else []

                # Check if schema has evolved
                if evolution["first_entry_keys"] != evolution["last_entry_keys"]:
                    evolution["changes"].append("Schema has evolved: keys have changed between first and last entries")

            return evolution

        except Exception as e:
            self.logger.error(f"Error analyzing temporal evolution: {e}")
            return {
                "description": f"Error: {e}",
                "changes": []
            }

    def get_examples(self) -> List[Any]:
        """Get sanitized examples from the JSONL file."""
        self.logger.info(f"Collecting examples from: {self.file_path}")

        if not self.file_path.exists():
            return []

        try:
            # Get samples
            samples = sample_jsonl_entries(self.file_path, min(10, SAMPLE_SIZE_LARGE_FILES))

            # Sanitize
            sanitized_samples = []
            for sample in samples[:5]:  # Limit to 5 examples
                sanitized = sanitize_data(sample)
                sanitized_samples.append(sanitized)

            return sanitized_samples

        except Exception as e:
            self.logger.error(f"Error getting examples: {e}")
            return []


class JsonlFolderAnalyzer(BaseAnalyzer):
    """Analyzer for folders containing multiple JSONL files."""

    def __init__(self, folder_name: str, purpose_description: str):
        """
        Initialize the JSONL folder analyzer.

        Args:
            folder_name: Name of the folder to analyze.
            purpose_description: Description of the folder's purpose.
        """
        super().__init__(folder_name)
        self.purpose_description = purpose_description

    def get_purpose(self) -> str:
        """Get the purpose and responsibility of this folder."""
        return self.purpose_description

    def analyze_data_structure(self) -> Dict[str, Any]:
        """Analyze the structure of all JSONL files in the folder."""
        self.logger.info(f"Analyzing JSONL folder: {self.source_dir}")

        if not self.source_dir.exists():
            return {
                "description": f"Directory {self.source_dir} does not exist.",
                "files": []
            }

        # Get all JSONL files
        jsonl_files = list(self.source_dir.rglob("*.jsonl"))

        self.logger.info(f"Found {len(jsonl_files)} JSONL files")

        structure = {
            "description": f"Folder containing {len(jsonl_files)} JSONL files. "
                         "Each file contains conversation data or state information.",
            "file_count": len(jsonl_files),
            "files": []
        }

        # Analyze a sample of files
        sample_size = min(10, len(jsonl_files))
        samples = get_temporal_samples(
            [self._file_to_stats(f) for f in jsonl_files],
            sample_size
        ) if len(jsonl_files) > 0 else []

        for file_stat in samples:
            try:
                file_path = file_stat.path
                custom_schema, json_schema = extract_schema_from_jsonl(file_path, max_lines=100)

                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f if line.strip())

                file_info = {
                    "name": file_path.name,
                    "line_count": line_count,
                    "size_bytes": file_path.stat().st_size,
                    "schema_summary": self._summarize_schema(custom_schema)
                }

                structure["files"].append(file_info)

            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")

        return structure

    def _file_to_stats(self, file_path: Path):
        """Convert a file path to FileStats object."""
        from file_utils import get_file_stats
        return get_file_stats(file_path)

    def _summarize_schema(self, schema: Dict[str, Any]) -> Dict[str, List[str]]:
        """Create a summary of the schema showing top-level keys and their types."""
        summary = {}
        for key, info in schema.items():
            types = info.get('types', [])
            summary[key] = types
        return summary

    def analyze_temporal_evolution(self) -> Dict[str, Any]:
        """Analyze how JSONL files change over time."""
        self.logger.info(f"Analyzing temporal evolution in: {self.source_dir}")

        if not self.source_dir.exists():
            return {
                "description": "Directory does not exist.",
                "changes": []
            }

        jsonl_files = list(self.source_dir.rglob("*.jsonl"))

        if not jsonl_files:
            return {
                "description": "No JSONL files found.",
                "changes": []
            }

        # Sort by modification time
        jsonl_files_sorted = sorted(jsonl_files, key=lambda f: f.stat().st_mtime)

        oldest = jsonl_files_sorted[0]
        newest = jsonl_files_sorted[-1]

        evolution = {
            "description": f"Files range from {oldest.stat().st_mtime} to {newest.stat().st_mtime}. "
                         f"New files are created for each conversation or state change.",
            "oldest_file": {
                "name": oldest.name,
                "modified": oldest.stat().st_mtime
            },
            "newest_file": {
                "name": newest.name,
                "modified": newest.stat().st_mtime
            },
            "changes": [
                "New JSONL files are created when new conversations start",
                "Existing files grow as new entries are appended",
                "Files are organized by project or session",
                "Older files represent historical conversations",
                "Newer files represent recent activity"
            ]
        }

        return evolution

    def get_examples(self) -> List[Any]:
        """Get sanitized examples from JSONL files."""
        self.logger.info(f"Collecting examples from: {self.source_dir}")

        if not self.source_dir.exists():
            return []

        jsonl_files = list(self.source_dir.rglob("*.jsonl"))

        if not jsonl_files:
            return []

        examples = []

        # Get examples from a few files
        for jsonl_file in jsonl_files[:3]:  # First 3 files
            try:
                samples = sample_jsonl_entries(jsonl_file, 2)  # 2 samples per file

                for sample in samples:
                    sanitized = sanitize_data(sample)
                    examples.append({
                        "file": jsonl_file.name,
                        "data": sanitized
                    })

            except Exception as e:
                self.logger.warning(f"Error reading {jsonl_file}: {e}")

        return examples[:5]  # Limit to 5 total examples


if __name__ == "__main__":
    from config import CONVERSATIONS_DIR

    # Analyze history.jsonl
    print("Analyzing history.jsonl...")
    history_file = CONVERSATIONS_DIR / "history.jsonl"
    if history_file.exists():
        history_analyzer = JsonlFileAnalyzer(
            folder_name="history",
            purpose_description="Global conversation history containing all messages, tool calls, "
                              "and responses across all projects. Each line represents one conversation turn.",
            file_path=history_file
        )
        history_analyzer.run()

    # Analyze projects folder
    print("\nAnalyzing projects folder...")
    projects_analyzer = JsonlFolderAnalyzer(
        folder_name="projects",
        purpose_description="Project-specific conversation histories. Each project has its own "
                          "directory with JSONL files for individual conversations. Files are named "
                          "with conversation IDs or agent IDs."
    )
    projects_analyzer.run()

    # Analyze todos folder
    print("\nAnalyzing todos folder...")
    todos_analyzer = JsonlFolderAnalyzer(
        folder_name="todos",
        purpose_description="Todo list persistence data. Contains JSONL files tracking todo items "
                          "across different sessions and projects. Each entry represents todo state changes."
    )
    todos_analyzer.run()

    print("\nJSONL file analysis complete!")
