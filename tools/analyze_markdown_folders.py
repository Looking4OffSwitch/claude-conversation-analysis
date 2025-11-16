"""
Analyzer for markdown-based folders (agents, commands).

This module analyzes folders containing markdown files and generates documentation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from base_analyzer import BaseAnalyzer
from logger import setup_logger
from sanitizer import sanitize_data


logger = setup_logger(__name__)


class MarkdownFolderAnalyzer(BaseAnalyzer):
    """Analyzer for folders containing markdown files."""

    def __init__(self, folder_name: str, purpose_description: str):
        """
        Initialize the markdown folder analyzer.

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
        """Analyze the data structure of markdown files."""
        self.logger.info(f"Analyzing markdown structure in: {self.source_dir}")

        if not self.source_dir.exists():
            return {
                "description": f"Directory {self.source_dir} does not exist.",
                "files": []
            }

        # Get all markdown files
        md_files = list(self.source_dir.glob("*.md"))

        structure = {
            "description": f"This folder contains {len(md_files)} markdown files. "
                         "Each file defines configuration or instructions in markdown format.",
            "file_count": len(md_files),
            "files": []
        }

        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Analyze markdown structure
                lines = content.split('\n')
                headers = [line for line in lines if line.startswith('#')]

                file_info = {
                    "name": md_file.name,
                    "size_bytes": md_file.stat().st_size,
                    "line_count": len(lines),
                    "header_count": len(headers),
                    "headers": headers[:10]  # First 10 headers
                }

                structure["files"].append(file_info)

            except Exception as e:
                self.logger.warning(f"Error analyzing {md_file}: {e}")

        return structure

    def analyze_temporal_evolution(self) -> Dict[str, Any]:
        """Analyze how markdown files change over time."""
        self.logger.info(f"Analyzing temporal evolution in: {self.source_dir}")

        if not self.source_dir.exists():
            return {
                "description": "Directory does not exist.",
                "changes": []
            }

        md_files = list(self.source_dir.glob("*.md"))

        if not md_files:
            return {
                "description": "No markdown files found.",
                "changes": []
            }

        # Sort by modification time
        md_files_sorted = sorted(md_files, key=lambda f: f.stat().st_mtime)

        oldest = md_files_sorted[0]
        newest = md_files_sorted[-1]

        evolution = {
            "description": f"Files range from {oldest.stat().st_mtime} to {newest.stat().st_mtime}. "
                         f"These configuration files are relatively static and change infrequently.",
            "oldest_file": {
                "name": oldest.name,
                "modified": oldest.stat().st_mtime
            },
            "newest_file": {
                "name": newest.name,
                "modified": newest.stat().st_mtime
            },
            "changes": [
                "Markdown files are typically created once and modified occasionally",
                "Changes usually involve updating instructions or adding new capabilities",
                "File structure remains consistent over time"
            ]
        }

        return evolution

    def get_examples(self) -> List[Any]:
        """Get sanitized examples from markdown files."""
        self.logger.info(f"Collecting examples from: {self.source_dir}")

        if not self.source_dir.exists():
            return []

        md_files = list(self.source_dir.glob("*.md"))
        examples = []

        for md_file in md_files[:5]:  # First 5 files
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Sanitize content
                sanitized_content = sanitize_data(content)

                example = {
                    "filename": md_file.name,
                    "content": sanitized_content[:500]  # First 500 chars
                }

                examples.append(example)

            except Exception as e:
                self.logger.warning(f"Error reading {md_file}: {e}")

        return examples


if __name__ == "__main__":
    # Analyze agents folder
    print("Analyzing agents folder...")
    agents_analyzer = MarkdownFolderAnalyzer(
        "agents",
        "Custom agent definitions for specialized tasks. Each markdown file defines "
        "an agent's behavior, capabilities, and tools. Agents are loaded dynamically "
        "when invoked via the Task tool."
    )
    agents_analyzer.run()

    # Analyze commands folder
    print("\nAnalyzing commands folder...")
    commands_analyzer = MarkdownFolderAnalyzer(
        "commands",
        "Custom slash commands that expand into prompts. Each markdown file contains "
        "instructions that are injected into the conversation when the command is used. "
        "Commands provide reusable workflows and standardized prompts."
    )
    commands_analyzer.run()

    print("\nMarkdown folder analysis complete!")
