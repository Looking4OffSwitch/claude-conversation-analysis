"""
Base analyzer class for Claude conversation data analysis.

This module provides an abstract base class that all specific folder analyzers
will inherit from, ensuring consistent structure and behavior.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from logger import setup_logger
from config import RESEARCH_DIR, CONVERSATIONS_DIR
from file_utils import get_directory_stats, DirectoryStats
from markdown_generator import (
    MarkdownBuilder,
    generate_statistics_section,
    save_markdown
)


class BaseAnalyzer(ABC):
    """Abstract base class for folder analyzers."""

    def __init__(self, folder_name: str):
        """
        Initialize the analyzer.

        Args:
            folder_name: Name of the folder to analyze (relative to CONVERSATIONS_DIR).

        Raises:
            ValueError: If folder_name is None or empty.
        """
        if not folder_name:
            raise ValueError("folder_name cannot be None or empty")

        self.folder_name = folder_name
        self.source_dir = CONVERSATIONS_DIR / folder_name
        self.output_dir = RESEARCH_DIR / folder_name
        self.logger = setup_logger(f"{self.__class__.__name__}_{folder_name}")

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized analyzer for: {folder_name}")

    @abstractmethod
    def get_purpose(self) -> str:
        """
        Get the purpose and responsibility of this folder.

        Returns:
            str: Description of the folder's purpose.
        """
        pass

    @abstractmethod
    def analyze_data_structure(self) -> Dict[str, Any]:
        """
        Analyze the data structure of files in this folder.

        Returns:
            Dict[str, Any]: Dictionary containing structure analysis results.
        """
        pass

    @abstractmethod
    def analyze_temporal_evolution(self) -> Dict[str, Any]:
        """
        Analyze how data in this folder changes over time.

        Returns:
            Dict[str, Any]: Dictionary containing temporal analysis results.
        """
        pass

    @abstractmethod
    def get_examples(self) -> List[Any]:
        """
        Get sanitized examples from this folder's data.

        Returns:
            List[Any]: List of example data (sanitized).
        """
        pass

    def get_statistics(self) -> DirectoryStats:
        """
        Get statistics for the folder.

        Returns:
            DirectoryStats: Statistics object for the folder.

        Raises:
            FileNotFoundError: If source directory doesn't exist.
        """
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")

        self.logger.info(f"Collecting statistics for: {self.source_dir}")
        return get_directory_stats(self.source_dir, recursive=True)

    def generate_report(self) -> str:
        """
        Generate a comprehensive markdown report for this folder.

        Returns:
            str: Path to the generated report.

        Raises:
            Exception: If report generation fails.
        """
        self.logger.info(f"Generating report for: {self.folder_name}")

        try:
            # Build markdown document
            builder = MarkdownBuilder(f"{self.folder_name} Analysis")

            # Purpose section
            builder.add_header("Purpose & Responsibility", level=2)
            builder.add_text(self.get_purpose())

            # Statistics section
            try:
                stats = self.get_statistics()
                stats_md = generate_statistics_section(stats)
                builder.lines.extend(stats_md.split('\n'))
            except Exception as e:
                self.logger.error(f"Failed to generate statistics: {e}")
                builder.add_text(f"*Error generating statistics: {e}*")

            # Data structure section
            try:
                structure = self.analyze_data_structure()
                builder.add_header("Data Structure", level=2)
                self._add_structure_to_builder(builder, structure)
            except Exception as e:
                self.logger.error(f"Failed to analyze data structure: {e}")
                builder.add_text(f"*Error analyzing data structure: {e}*")

            # Temporal evolution section
            try:
                temporal = self.analyze_temporal_evolution()
                builder.add_header("Temporal Evolution", level=2)
                self._add_temporal_to_builder(builder, temporal)
            except Exception as e:
                self.logger.error(f"Failed to analyze temporal evolution: {e}")
                builder.add_text(f"*Error analyzing temporal evolution: {e}*")

            # Examples section
            try:
                examples = self.get_examples()
                if examples:
                    builder.add_header("Examples", level=2)
                    self._add_examples_to_builder(builder, examples)
            except Exception as e:
                self.logger.error(f"Failed to get examples: {e}")
                builder.add_text(f"*Error getting examples: {e}*")

            # Generate and save
            markdown = builder.build()
            output_path = self.output_dir / "README.md"
            save_markdown(markdown, output_path)

            self.logger.info(f"Report saved to: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            raise

    def _add_structure_to_builder(
        self,
        builder: MarkdownBuilder,
        structure: Dict[str, Any]
    ) -> None:
        """
        Add structure analysis to markdown builder.

        Args:
            builder: MarkdownBuilder instance.
            structure: Structure analysis dictionary.
        """
        # Default implementation - can be overridden
        if 'description' in structure:
            builder.add_text(structure['description'])

        if 'schema' in structure:
            import json
            builder.add_code_block(json.dumps(structure['schema'], indent=2))

    def _add_temporal_to_builder(
        self,
        builder: MarkdownBuilder,
        temporal: Dict[str, Any]
    ) -> None:
        """
        Add temporal analysis to markdown builder.

        Args:
            builder: MarkdownBuilder instance.
            temporal: Temporal analysis dictionary.
        """
        # Default implementation - can be overridden
        if 'description' in temporal:
            builder.add_text(temporal['description'])

        if 'changes' in temporal:
            builder.add_list(temporal['changes'])

    def _add_examples_to_builder(
        self,
        builder: MarkdownBuilder,
        examples: List[Any]
    ) -> None:
        """
        Add examples to markdown builder.

        Args:
            builder: MarkdownBuilder instance.
            examples: List of examples.
        """
        # Default implementation - can be overridden
        import json

        for i, example in enumerate(examples[:5], 1):
            builder.add_header(f"Example {i}", level=3)
            if isinstance(example, (dict, list)):
                builder.add_code_block(json.dumps(example, indent=2))
            else:
                builder.add_code_block(str(example), "text")

    def run(self) -> str:
        """
        Run the complete analysis and generate report.

        Returns:
            str: Path to the generated report.

        Raises:
            Exception: If analysis fails.
        """
        self.logger.info(f"Starting analysis of: {self.folder_name}")

        try:
            report_path = self.generate_report()
            self.logger.info(f"Analysis complete: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise


if __name__ == "__main__":
    # This is an abstract class, so we can't instantiate it directly
    print("BaseAnalyzer is an abstract class.")
    print("Create concrete implementations that inherit from it.")
