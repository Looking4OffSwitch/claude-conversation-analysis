"""
Markdown report generator for documentation.

This module provides functions to generate well-formatted markdown documentation
from analysis results, schemas, and statistics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from logger import setup_logger
from file_utils import DirectoryStats, FileStats
from config import CODE_BLOCK_LANGUAGE


# Initialize logger
logger = setup_logger(__name__)


class MarkdownBuilder:
    """Builder class for constructing markdown documents."""

    def __init__(self, title: Optional[str] = None):
        """
        Initialize the markdown builder.

        Args:
            title: Optional document title.
        """
        self.lines: List[str] = []
        if title:
            self.add_header(title, level=1)

    def add_header(self, text: str, level: int = 1) -> 'MarkdownBuilder':
        """
        Add a header to the document.

        Args:
            text: Header text.
            level: Header level (1-6).

        Returns:
            MarkdownBuilder: Self for chaining.

        Raises:
            ValueError: If level is not between 1 and 6.
        """
        if not 1 <= level <= 6:
            raise ValueError(f"Header level must be between 1 and 6, got {level}")

        self.lines.append(f"{'#' * level} {text}")
        self.lines.append("")
        return self

    def add_text(self, text: str) -> 'MarkdownBuilder':
        """
        Add paragraph text.

        Args:
            text: Text to add.

        Returns:
            MarkdownBuilder: Self for chaining.
        """
        self.lines.append(text)
        self.lines.append("")
        return self

    def add_code_block(
        self,
        code: str,
        language: str = CODE_BLOCK_LANGUAGE
    ) -> 'MarkdownBuilder':
        """
        Add a code block.

        Args:
            code: Code content.
            language: Language for syntax highlighting.

        Returns:
            MarkdownBuilder: Self for chaining.
        """
        self.lines.append(f"```{language}")
        self.lines.append(code)
        self.lines.append("```")
        self.lines.append("")
        return self

    def add_list(self, items: List[str], ordered: bool = False) -> 'MarkdownBuilder':
        """
        Add a list to the document.

        Args:
            items: List items.
            ordered: Whether to use ordered (numbered) list.

        Returns:
            MarkdownBuilder: Self for chaining.

        Raises:
            ValueError: If items is empty.
        """
        if not items:
            raise ValueError("items cannot be empty")

        for i, item in enumerate(items, 1):
            prefix = f"{i}." if ordered else "-"
            self.lines.append(f"{prefix} {item}")

        self.lines.append("")
        return self

    def add_table(
        self,
        headers: List[str],
        rows: List[List[str]]
    ) -> 'MarkdownBuilder':
        """
        Add a table to the document.

        Args:
            headers: Table header row.
            rows: Table data rows.

        Returns:
            MarkdownBuilder: Self for chaining.

        Raises:
            ValueError: If headers is empty or rows have inconsistent columns.
        """
        if not headers:
            raise ValueError("headers cannot be empty")

        # Validate all rows have same number of columns
        expected_cols = len(headers)
        for i, row in enumerate(rows):
            if len(row) != expected_cols:
                raise ValueError(
                    f"Row {i} has {len(row)} columns, expected {expected_cols}"
                )

        # Add header
        self.lines.append("| " + " | ".join(headers) + " |")

        # Add separator
        self.lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Add rows
        for row in rows:
            self.lines.append("| " + " | ".join(row) + " |")

        self.lines.append("")
        return self

    def add_horizontal_rule(self) -> 'MarkdownBuilder':
        """Add a horizontal rule."""
        self.lines.append("---")
        self.lines.append("")
        return self

    def add_blockquote(self, text: str) -> 'MarkdownBuilder':
        """
        Add a blockquote.

        Args:
            text: Quote text.

        Returns:
            MarkdownBuilder: Self for chaining.
        """
        lines = text.split('\n')
        for line in lines:
            self.lines.append(f"> {line}")
        self.lines.append("")
        return self

    def build(self) -> str:
        """
        Build and return the final markdown document.

        Returns:
            str: Complete markdown document.
        """
        return '\n'.join(self.lines)


def generate_statistics_section(stats: DirectoryStats) -> str:
    """
    Generate a markdown section for directory statistics.

    Args:
        stats: DirectoryStats object.

    Returns:
        str: Markdown formatted statistics section.

    Raises:
        ValueError: If stats is None.
    """
    if stats is None:
        raise ValueError("stats cannot be None")

    builder = MarkdownBuilder()
    builder.add_header("Statistics", level=2)

    # Basic stats
    stats_list = [
        f"**Total Files**: {stats.total_files}",
        f"**Total Size**: {stats.total_size_mb:.2f} MB",
    ]

    # Date range
    if stats.date_range:
        oldest, newest = stats.date_range
        stats_list.append(f"**Date Range**: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}")

    builder.add_list(stats_list)

    # File extensions table
    if stats.extensions:
        builder.add_header("File Extensions", level=3)
        headers = ["Extension", "Count", "Percentage"]
        rows = []

        for ext, count in sorted(stats.extensions.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats.total_files * 100)
            rows.append([ext, str(count), f"{percentage:.1f}%"])

        builder.add_table(headers, rows)

    return builder.build()


def generate_schema_section(
    custom_schema: Dict[str, Any],
    json_schema: Dict[str, Any]
) -> str:
    """
    Generate a markdown section for schema documentation.

    Args:
        custom_schema: Custom schema dictionary.
        json_schema: JSON Schema dictionary.

    Returns:
        str: Markdown formatted schema section.

    Raises:
        ValueError: If both schemas are None.
    """
    if custom_schema is None and json_schema is None:
        raise ValueError("At least one schema must be provided")

    builder = MarkdownBuilder()
    builder.add_header("Data Structure", level=2)

    # Custom schema (field-by-field)
    if custom_schema:
        builder.add_header("Field Descriptions", level=3)

        for field, field_info in sorted(custom_schema.items()):
            builder.add_header(field, level=4)

            # Type information
            types = field_info.get('types', [])
            builder.add_text(f"**Type(s)**: `{', '.join(types)}`")

            # Occurrence rate
            occurrence = field_info.get('occurrence_rate', 'N/A')
            occurrences = field_info.get('occurrences', 0)
            builder.add_text(f"**Occurrence**: {occurrence} ({occurrences} times)")

            # Examples
            examples = field_info.get('examples', [])
            if examples:
                builder.add_text("**Examples**:")
                for example in examples[:3]:
                    example_str = json.dumps(example, indent=2) if isinstance(example, (dict, list)) else str(example)
                    if len(example_str) > 100:
                        example_str = example_str[:100] + "..."
                    builder.add_code_block(example_str)

            # Nested schema
            if 'nested_schema' in field_info:
                builder.add_text("**Nested Structure**: See nested schema below")

            # Array item schema
            if 'array_item_schema' in field_info:
                builder.add_text("**Array Items**: See array item schema below")

    # JSON Schema
    if json_schema:
        builder.add_header("JSON Schema", level=3)
        schema_json = json.dumps(json_schema, indent=2)
        builder.add_code_block(schema_json)

    return builder.build()


def generate_file_inventory_section(file_stats: List[FileStats]) -> str:
    """
    Generate a markdown section for file inventory.

    Args:
        file_stats: List of FileStats objects.

    Returns:
        str: Markdown formatted file inventory section.

    Raises:
        ValueError: If file_stats is None or empty.
    """
    if not file_stats:
        raise ValueError("file_stats cannot be None or empty")

    builder = MarkdownBuilder()
    builder.add_header("File Inventory", level=2)

    # Create table
    headers = ["File", "Size", "Modified", "Lines"]
    rows = []

    for stats in sorted(file_stats, key=lambda s: s.modified_time, reverse=True)[:50]:
        size_str = f"{stats.size_mb:.2f}MB" if stats.size_mb > 1 else f"{stats.size_kb:.1f}KB"
        modified_str = stats.modified_time.strftime("%Y-%m-%d %H:%M")
        lines_str = str(stats.line_count) if stats.line_count else "N/A"

        rows.append([
            stats.path.name,
            size_str,
            modified_str,
            lines_str
        ])

    builder.add_table(headers, rows)

    if len(file_stats) > 50:
        builder.add_text(f"*Showing 50 of {len(file_stats)} files*")

    return builder.build()


def generate_examples_section(
    title: str,
    examples: List[Dict[str, Any]],
    max_examples: int = 5
) -> str:
    """
    Generate a markdown section with data examples.

    Args:
        title: Section title.
        examples: List of example data objects.
        max_examples: Maximum number of examples to include.

    Returns:
        str: Markdown formatted examples section.

    Raises:
        ValueError: If title is empty or examples is None.
    """
    if not title:
        raise ValueError("title cannot be empty")

    if examples is None:
        raise ValueError("examples cannot be None")

    builder = MarkdownBuilder()
    builder.add_header(title, level=2)

    if not examples:
        builder.add_text("*No examples available*")
        return builder.build()

    for i, example in enumerate(examples[:max_examples], 1):
        builder.add_header(f"Example {i}", level=3)
        example_json = json.dumps(example, indent=2)
        builder.add_code_block(example_json)

    if len(examples) > max_examples:
        builder.add_text(f"*Showing {max_examples} of {len(examples)} examples*")

    return builder.build()


def save_markdown(content: str, output_path: Path) -> None:
    """
    Save markdown content to a file.

    Args:
        content: Markdown content to save.
        output_path: Path where to save the file.

    Raises:
        ValueError: If content or output_path is None/empty.
        IOError: If the file cannot be written.
    """
    if not content:
        raise ValueError("content cannot be None or empty")

    if not output_path:
        raise ValueError("output_path cannot be None or empty")

    try:
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Saved markdown to: {output_path}")

    except IOError as e:
        logger.error(f"Failed to save markdown to {output_path}: {e}")
        raise


if __name__ == "__main__":
    # Test the markdown generator
    print("Markdown Generator Test")
    print("=" * 50)

    # Build a test document
    builder = MarkdownBuilder("Test Document")
    builder.add_header("Introduction", level=2)
    builder.add_text("This is a test document to demonstrate the markdown builder.")

    builder.add_header("Features", level=2)
    builder.add_list([
        "Headers of multiple levels",
        "Text paragraphs",
        "Code blocks",
        "Tables",
        "Lists"
    ])

    builder.add_header("Example Code", level=2)
    builder.add_code_block('{"test": "value", "number": 42}', "json")

    builder.add_header("Example Table", level=2)
    builder.add_table(
        ["Column 1", "Column 2", "Column 3"],
        [
            ["A", "B", "C"],
            ["1", "2", "3"],
            ["X", "Y", "Z"]
        ]
    )

    markdown = builder.build()
    print("\nGenerated Markdown:")
    print(markdown)
