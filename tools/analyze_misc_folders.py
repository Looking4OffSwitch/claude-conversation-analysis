"""
Analyzer for miscellaneous folders (debug, session-env, shell-snapshots, statsig, file-history, ide).

This module analyzes folders with mixed content types and generates documentation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from base_analyzer import BaseAnalyzer
from logger import setup_logger
from sanitizer import sanitize_data
from file_utils import get_temporal_samples, get_file_stats


logger = setup_logger(__name__)


class MiscFolderAnalyzer(BaseAnalyzer):
    """Analyzer for folders with miscellaneous content types."""

    def __init__(self, folder_name: str, purpose_description: str):
        """
        Initialize the misc folder analyzer.

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
        """Analyze the structure of files in the folder."""
        self.logger.info(f"Analyzing folder structure: {self.source_dir}")

        if not self.source_dir.exists():
            return {
                "description": f"Directory {self.source_dir} does not exist.",
                "files": []
            }

        # Get all files recursively
        all_files = [f for f in self.source_dir.rglob("*") if f.is_file()]

        # Group by extension
        by_extension = {}
        for file_path in all_files:
            ext = file_path.suffix or "(no extension)"
            if ext not in by_extension:
                by_extension[ext] = []
            by_extension[ext].append(file_path)

        structure = {
            "description": f"Folder containing {len(all_files)} files of various types.",
            "total_files": len(all_files),
            "extensions": {}
        }

        for ext, files in by_extension.items():
            structure["extensions"][ext] = {
                "count": len(files),
                "total_size_bytes": sum(f.stat().st_size for f in files),
                "example_files": [f.name for f in files[:5]]
            }

        return structure

    def analyze_temporal_evolution(self) -> Dict[str, Any]:
        """Analyze how files in the folder change over time."""
        self.logger.info(f"Analyzing temporal evolution: {self.source_dir}")

        if not self.source_dir.exists():
            return {
                "description": "Directory does not exist.",
                "changes": []
            }

        all_files = [f for f in self.source_dir.rglob("*") if f.is_file()]

        if not all_files:
            return {
                "description": "No files found.",
                "changes": []
            }

        # Sort by modification time
        all_files_sorted = sorted(all_files, key=lambda f: f.stat().st_mtime)

        oldest = all_files_sorted[0]
        newest = all_files_sorted[-1]

        evolution = {
            "description": f"Files range from {oldest.stat().st_mtime} to {newest.stat().st_mtime}. "
                         f"This folder contains dynamic data that changes with usage.",
            "oldest_file": {
                "name": oldest.name,
                "modified": oldest.stat().st_mtime
            },
            "newest_file": {
                "name": newest.name,
                "modified": newest.stat().st_mtime
            },
            "changes": [
                "Files are created and updated during active sessions",
                "Older files may represent historical state or debug information",
                "Newer files represent recent activity",
                "File count grows over time with usage"
            ]
        }

        return evolution

    def get_examples(self) -> List[Any]:
        """Get sanitized examples from files in the folder."""
        self.logger.info(f"Collecting examples from: {self.source_dir}")

        if not self.source_dir.exists():
            return []

        examples = []

        # Get sample files
        all_files = [f for f in self.source_dir.rglob("*") if f.is_file()]

        if not all_files:
            return []

        # Get temporal samples
        file_stats = [get_file_stats(f) for f in all_files]
        samples = get_temporal_samples(file_stats, min(5, len(file_stats)))

        for file_stat in samples:
            file_path = file_stat.path

            try:
                # Try to read as text
                if file_path.suffix in {'.json', '.jsonl', '.txt', '.log', '.md'}:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000)  # First 1000 chars

                    sanitized = sanitize_data(content)

                    examples.append({
                        "file": file_path.name,
                        "type": file_path.suffix,
                        "content_preview": sanitized
                    })
                else:
                    # Binary or unknown file
                    examples.append({
                        "file": file_path.name,
                        "type": file_path.suffix,
                        "note": "Binary file or non-text format",
                        "size_bytes": file_path.stat().st_size
                    })

            except Exception as e:
                self.logger.warning(f"Error reading {file_path}: {e}")

        return examples


class ShellSnapshotsAnalyzer(MiscFolderAnalyzer):
    """Specialized analyzer for shell-snapshots folder."""

    def __init__(self):
        super().__init__(
            folder_name="shell-snapshots",
            purpose_description="Shell state snapshots capturing command history, environment variables, "
                              "and working directory state at various points during execution. Used for "
                              "shell session persistence and recovery."
        )

    def analyze_data_structure(self) -> Dict[str, Any]:
        """Analyze shell snapshot structure."""
        structure = super().analyze_data_structure()

        # Add shell-specific analysis
        if self.source_dir.exists():
            snapshot_files = list(self.source_dir.glob("*"))

            # Try to analyze a sample snapshot
            if snapshot_files:
                sample_file = snapshot_files[0]
                try:
                    with open(sample_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(500)

                    structure["snapshot_format"] = {
                        "description": "Snapshot files contain shell state data",
                        "sample_content_preview": content[:200]
                    }
                except Exception as e:
                    self.logger.warning(f"Could not read snapshot sample: {e}")

        return structure


class DebugAnalyzer(MiscFolderAnalyzer):
    """Specialized analyzer for debug folder."""

    def __init__(self):
        super().__init__(
            folder_name="debug",
            purpose_description="Debug logs and diagnostic information from Claude Code execution. "
                              "Contains detailed logs of tool calls, errors, and system events for troubleshooting."
        )


class SessionEnvAnalyzer(MiscFolderAnalyzer):
    """Specialized analyzer for session-env folder."""

    def __init__(self):
        super().__init__(
            folder_name="session-env",
            purpose_description="Session environment data containing context and state information "
                              "for active and past sessions. Preserves session state across restarts."
        )


class StatsigAnalyzer(MiscFolderAnalyzer):
    """Specialized analyzer for statsig folder."""

    def __init__(self):
        super().__init__(
            folder_name="statsig",
            purpose_description="Statistics and feature flag data from Statsig integration. "
                              "Contains telemetry and experiment configuration used for A/B testing "
                              "and feature rollouts."
        )


class FileHistoryAnalyzer(MiscFolderAnalyzer):
    """Specialized analyzer for file-history folder."""

    def __init__(self):
        super().__init__(
            folder_name="file-history",
            purpose_description="File version history tracking changes made to files during sessions. "
                              "Provides a backup and audit trail of file modifications."
        )


class IdeAnalyzer(MiscFolderAnalyzer):
    """Specialized analyzer for ide folder."""

    def __init__(self):
        super().__init__(
            folder_name="ide",
            purpose_description="IDE integration data including lock files and state information "
                              "for coordinating with VS Code or other editors."
        )


if __name__ == "__main__":
    # Analyze all misc folders
    analyzers = [
        ("debug", DebugAnalyzer()),
        ("session-env", SessionEnvAnalyzer()),
        ("shell-snapshots", ShellSnapshotsAnalyzer()),
        ("statsig", StatsigAnalyzer()),
        ("file-history", FileHistoryAnalyzer()),
        ("ide", IdeAnalyzer()),
    ]

    for name, analyzer in analyzers:
        print(f"\nAnalyzing {name} folder...")
        try:
            analyzer.run()
        except Exception as e:
            print(f"Error analyzing {name}: {e}")

    print("\nMiscellaneous folder analysis complete!")
