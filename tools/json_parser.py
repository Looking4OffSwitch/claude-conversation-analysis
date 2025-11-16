"""
JSON and JSONL parser with schema extraction capabilities.

This module provides functions for parsing JSON and JSONL files, extracting
schemas, and analyzing the structure of conversation data.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from logger import setup_logger
from config import JSONL_ENCODING, MAX_LINES_TO_ANALYZE


# Initialize logger
logger = setup_logger(__name__)


class SchemaExtractor:
    """Extract and merge schemas from multiple JSON objects."""

    def __init__(self):
        """Initialize the schema extractor."""
        self.field_types: Dict[str, Set[str]] = defaultdict(set)
        self.nested_schemas: Dict[str, 'SchemaExtractor'] = {}
        self.array_item_schemas: Dict[str, 'SchemaExtractor'] = {}
        self.example_values: Dict[str, List[Any]] = defaultdict(list)
        self.field_counts: Dict[str, int] = defaultdict(int)
        self.total_objects = 0

    def add_object(self, obj: Dict[str, Any], path: str = "") -> None:
        """
        Add an object to the schema analysis.

        Args:
            obj: JSON object to analyze.
            path: Current path in nested structure (for logging).

        Raises:
            TypeError: If obj is not a dictionary.
        """
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {type(obj).__name__}")

        self.total_objects += 1

        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            # Count field occurrences
            self.field_counts[key] += 1

            # Record type
            value_type = type(value).__name__
            self.field_types[key].add(value_type)

            # Store example values (limit to 5 per field)
            if len(self.example_values[key]) < 5:
                self.example_values[key].append(value)

            # Handle nested objects
            if isinstance(value, dict):
                if key not in self.nested_schemas:
                    self.nested_schemas[key] = SchemaExtractor()
                self.nested_schemas[key].add_object(value, current_path)

            # Handle arrays
            elif isinstance(value, list) and value:
                if key not in self.array_item_schemas:
                    self.array_item_schemas[key] = SchemaExtractor()

                # Analyze first few items if they're objects
                for item in value[:10]:  # Limit to first 10 items
                    if isinstance(item, dict):
                        self.array_item_schemas[key].add_object(item, f"{current_path}[]")

    def get_schema(self) -> Dict[str, Any]:
        """
        Generate a schema dictionary from collected data.

        Returns:
            Dict[str, Any]: Schema representation with types and metadata.
        """
        schema = {}

        for field, types in self.field_types.items():
            field_schema = {
                "types": sorted(list(types)),
                "occurrence_rate": f"{(self.field_counts[field] / self.total_objects * 100):.1f}%",
                "occurrences": self.field_counts[field],
            }

            # Add example values
            if self.example_values[field]:
                field_schema["examples"] = self.example_values[field][:3]

            # Add nested schema if applicable
            if field in self.nested_schemas:
                field_schema["nested_schema"] = self.nested_schemas[field].get_schema()

            # Add array item schema if applicable
            if field in self.array_item_schemas:
                field_schema["array_item_schema"] = self.array_item_schemas[field].get_schema()

            schema[field] = field_schema

        return schema

    def get_json_schema(self) -> Dict[str, Any]:
        """
        Generate a JSON Schema compatible schema.

        Returns:
            Dict[str, Any]: JSON Schema representation.
        """
        properties = {}
        required = []

        for field, types in self.field_types.items():
            # Determine primary type
            type_list = sorted(list(types))

            # Map Python types to JSON Schema types
            json_types = []
            for t in type_list:
                if t in ("int", "float"):
                    json_types.append("number")
                elif t == "str":
                    json_types.append("string")
                elif t == "bool":
                    json_types.append("boolean")
                elif t == "dict":
                    json_types.append("object")
                elif t == "list":
                    json_types.append("array")
                elif t == "NoneType":
                    json_types.append("null")

            json_types = sorted(list(set(json_types)))

            field_schema = {}

            if len(json_types) == 1:
                field_schema["type"] = json_types[0]
            else:
                field_schema["type"] = json_types

            # Add nested schema for objects
            if field in self.nested_schemas:
                field_schema = self.nested_schemas[field].get_json_schema()

            # Add array item schema
            if field in self.array_item_schemas and "array" in json_types:
                field_schema["items"] = self.array_item_schemas[field].get_json_schema()

            properties[field] = field_schema

            # Mark as required if present in >80% of objects
            if self.field_counts[field] / self.total_objects > 0.8:
                required.append(field)

        schema = {
            "type": "object",
            "properties": properties
        }

        if required:
            schema["required"] = sorted(required)

        return schema


def parse_jsonl_file(
    file_path: Path,
    max_lines: Optional[int] = None
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Parse a JSONL file and return all valid JSON objects.

    Args:
        file_path: Path to the JSONL file.
        max_lines: Maximum number of lines to parse (None for all).

    Returns:
        Tuple[List[Dict], List[str]]: Tuple of (parsed objects, error messages).

    Raises:
        ValueError: If file_path is None or empty.
        FileNotFoundError: If the file doesn't exist.
    """
    # Validate parameters
    if not file_path:
        raise ValueError("file_path cannot be None or empty")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Parsing JSONL file: {file_path}")

    objects = []
    errors = []
    line_num = 0

    try:
        with open(file_path, 'r', encoding=JSONL_ENCODING) as f:
            for line in f:
                line_num += 1

                # Check max_lines limit
                if max_lines and line_num > max_lines:
                    logger.debug(f"Reached max_lines limit ({max_lines})")
                    break

                # Skip empty lines
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                    objects.append(obj)
                except json.JSONDecodeError as e:
                    error_msg = f"Line {line_num}: {e}"
                    errors.append(error_msg)
                    logger.warning(f"JSON decode error in {file_path}: {error_msg}")

        logger.info(f"Parsed {len(objects)} objects from {file_path} ({len(errors)} errors)")

    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

    return objects, errors


def parse_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Dict[str, Any]: Parsed JSON object.

    Raises:
        ValueError: If file_path is None or empty.
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    # Validate parameters
    if not file_path:
        raise ValueError("file_path cannot be None or empty")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Parsing JSON file: {file_path}")

    try:
        with open(file_path, 'r', encoding=JSONL_ENCODING) as f:
            obj = json.load(f)
        return obj
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def extract_schema_from_jsonl(
    file_path: Path,
    max_lines: Optional[int] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extract schema from a JSONL file.

    Args:
        file_path: Path to the JSONL file.
        max_lines: Maximum number of lines to analyze (None for all).

    Returns:
        Tuple[Dict, Dict]: Tuple of (custom schema, JSON Schema).

    Raises:
        ValueError: If file_path is None or empty.
        FileNotFoundError: If the file doesn't exist.
    """
    logger.info(f"Extracting schema from: {file_path}")

    # Parse the file
    objects, errors = parse_jsonl_file(file_path, max_lines or MAX_LINES_TO_ANALYZE)

    if not objects:
        logger.warning(f"No valid objects found in {file_path}")
        return {}, {}

    # Extract schema
    extractor = SchemaExtractor()
    for obj in objects:
        if isinstance(obj, dict):
            extractor.add_object(obj)

    custom_schema = extractor.get_schema()
    json_schema = extractor.get_json_schema()

    logger.info(f"Extracted schema from {len(objects)} objects")

    return custom_schema, json_schema


def sample_jsonl_entries(
    file_path: Path,
    sample_size: int = 10
) -> List[Dict[str, Any]]:
    """
    Sample entries from a JSONL file with even distribution.

    Args:
        file_path: Path to the JSONL file.
        sample_size: Number of entries to sample.

    Returns:
        List[Dict[str, Any]]: Sampled entries.

    Raises:
        ValueError: If file_path is None or sample_size < 1.
        FileNotFoundError: If the file doesn't exist.
    """
    # Validate parameters
    if not file_path:
        raise ValueError("file_path cannot be None or empty")

    if sample_size < 1:
        raise ValueError("sample_size must be at least 1")

    logger.info(f"Sampling {sample_size} entries from: {file_path}")

    # First, count total lines
    with open(file_path, 'r', encoding=JSONL_ENCODING) as f:
        total_lines = sum(1 for line in f if line.strip())

    if total_lines <= sample_size:
        # Return all entries
        objects, _ = parse_jsonl_file(file_path)
        return objects

    # Calculate sample indices
    step = total_lines / sample_size
    sample_indices = set(int(i * step) for i in range(sample_size))
    # Always include first and last
    sample_indices.add(0)
    sample_indices.add(total_lines - 1)

    # Parse only sampled lines
    samples = []
    with open(file_path, 'r', encoding=JSONL_ENCODING) as f:
        for i, line in enumerate(f):
            if i in sample_indices:
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        samples.append(obj)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing line {i}: {e}")

    logger.info(f"Sampled {len(samples)} entries")
    return samples


if __name__ == "__main__":
    # Test the parser
    from config import CONVERSATIONS_DIR

    print("JSON Parser Test")
    print("=" * 50)

    # Find a test JSONL file
    test_files = list(CONVERSATIONS_DIR.glob("**/*.jsonl"))

    if test_files:
        test_file = test_files[0]
        print(f"\nTesting with: {test_file}")

        # Extract schema
        custom, json_schema = extract_schema_from_jsonl(test_file, max_lines=100)

        print("\nCustom Schema (first 3 fields):")
        for i, (field, schema) in enumerate(custom.items()):
            if i >= 3:
                break
            print(f"\n{field}:")
            print(f"  Types: {schema.get('types')}")
            print(f"  Occurrence: {schema.get('occurrence_rate')}")

        print("\n\nJSON Schema:")
        print(json.dumps(json_schema, indent=2)[:500] + "...")
    else:
        print("No JSONL files found for testing")
