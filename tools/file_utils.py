"""
File utilities for analyzing Claude conversation data.

This module provides functions for file operations, statistics collection,
and temporal analysis of files in the conversation directory.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from logger import setup_logger


# Initialize logger
logger = setup_logger(__name__)


@dataclass
class FileStats:
    """Statistics about a file or directory."""

    path: Path
    size_bytes: int
    created_time: datetime
    modified_time: datetime
    is_directory: bool
    line_count: Optional[int] = None
    extension: Optional[str] = None

    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    @property
    def size_kb(self) -> float:
        """Get file size in kilobytes."""
        return self.size_bytes / 1024

    def __str__(self) -> str:
        """Human-readable string representation."""
        size_str = f"{self.size_mb:.2f}MB" if self.size_mb > 1 else f"{self.size_kb:.2f}KB"
        type_str = "Directory" if self.is_directory else "File"
        lines_str = f", {self.line_count} lines" if self.line_count else ""
        return f"{type_str}: {self.path.name} ({size_str}{lines_str})"


@dataclass
class DirectoryStats:
    """Aggregated statistics for a directory."""

    path: Path
    total_files: int
    total_size_bytes: int
    file_stats: List[FileStats]
    oldest_file: Optional[FileStats] = None
    newest_file: Optional[FileStats] = None
    extensions: Optional[dict[str, int]] = None

    @property
    def total_size_mb(self) -> float:
        """Get total size in megabytes."""
        return self.total_size_bytes / (1024 * 1024)

    @property
    def date_range(self) -> Optional[Tuple[datetime, datetime]]:
        """Get the date range of files in the directory."""
        if not self.oldest_file or not self.newest_file:
            return None
        return (self.oldest_file.modified_time, self.newest_file.modified_time)


def get_file_stats(file_path: Path) -> FileStats:
    """
    Get statistics for a single file.

    Args:
        file_path: Path to the file to analyze.

    Returns:
        FileStats: Statistics object for the file.

    Raises:
        ValueError: If file_path is None or empty.
        FileNotFoundError: If the file doesn't exist.
        OSError: If there's an error accessing the file.
    """
    # Validate parameters
    if not file_path:
        raise ValueError("file_path cannot be None or empty")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        stat = file_path.stat()
        is_dir = file_path.is_dir()

        # Get line count for text files
        line_count = None
        if not is_dir and file_path.suffix in {'.jsonl', '.json', '.md', '.txt', '.log'}:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
            except Exception as e:
                logger.warning(f"Could not count lines in {file_path}: {e}")

        return FileStats(
            path=file_path,
            size_bytes=stat.st_size,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            is_directory=is_dir,
            line_count=line_count,
            extension=file_path.suffix if not is_dir else None
        )
    except OSError as e:
        logger.error(f"Error accessing file {file_path}: {e}")
        raise


def get_directory_stats(
    directory: Path,
    recursive: bool = True,
    file_pattern: Optional[str] = None
) -> DirectoryStats:
    """
    Get aggregated statistics for all files in a directory.

    Args:
        directory: Path to the directory to analyze.
        recursive: Whether to recursively analyze subdirectories.
        file_pattern: Optional glob pattern to filter files (e.g., "*.jsonl").

    Returns:
        DirectoryStats: Aggregated statistics for the directory.

    Raises:
        ValueError: If directory is None or not a directory.
        FileNotFoundError: If directory doesn't exist.
    """
    # Validate parameters
    if not directory:
        raise ValueError("directory cannot be None")

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    logger.info(f"Analyzing directory: {directory}")

    try:
        # Get all files
        if recursive:
            if file_pattern:
                files = list(directory.rglob(file_pattern))
            else:
                files = [f for f in directory.rglob("*") if f.is_file()]
        else:
            if file_pattern:
                files = list(directory.glob(file_pattern))
            else:
                files = [f for f in directory.glob("*") if f.is_file()]

        logger.debug(f"Found {len(files)} files in {directory}")

        # Collect stats for each file
        file_stats_list = []
        for file_path in files:
            try:
                stats = get_file_stats(file_path)
                file_stats_list.append(stats)
            except Exception as e:
                logger.warning(f"Skipping file {file_path}: {e}")

        # Calculate aggregated stats
        total_size = sum(f.size_bytes for f in file_stats_list)

        # Find oldest and newest files
        oldest = min(file_stats_list, key=lambda f: f.modified_time) if file_stats_list else None
        newest = max(file_stats_list, key=lambda f: f.modified_time) if file_stats_list else None

        # Count file extensions
        extensions = {}
        for f in file_stats_list:
            if f.extension:
                extensions[f.extension] = extensions.get(f.extension, 0) + 1

        return DirectoryStats(
            path=directory,
            total_files=len(file_stats_list),
            total_size_bytes=total_size,
            file_stats=file_stats_list,
            oldest_file=oldest,
            newest_file=newest,
            extensions=extensions
        )
    except Exception as e:
        logger.error(f"Error analyzing directory {directory}: {e}")
        raise


def get_temporal_samples(
    file_stats_list: List[FileStats],
    sample_count: int = 5
) -> List[FileStats]:
    """
    Get temporally distributed samples from a list of files.

    Selects files evenly distributed across the time range, including
    the oldest and newest files.

    Args:
        file_stats_list: List of FileStats to sample from.
        sample_count: Number of samples to return (minimum 2).

    Returns:
        List[FileStats]: Temporally distributed sample of files.

    Raises:
        ValueError: If sample_count < 2 or file_stats_list is empty.
    """
    # Validate parameters
    if not file_stats_list:
        raise ValueError("file_stats_list cannot be empty")

    if sample_count < 2:
        raise ValueError("sample_count must be at least 2")

    # Sort by modification time
    sorted_files = sorted(file_stats_list, key=lambda f: f.modified_time)

    # If we have fewer files than requested samples, return all
    if len(sorted_files) <= sample_count:
        return sorted_files

    # Calculate indices for evenly distributed samples
    indices = []
    step = (len(sorted_files) - 1) / (sample_count - 1)

    for i in range(sample_count):
        index = int(round(i * step))
        indices.append(index)

    # Ensure we get the oldest and newest
    indices[0] = 0
    indices[-1] = len(sorted_files) - 1

    # Remove duplicates while preserving order
    indices = sorted(set(indices))

    samples = [sorted_files[i] for i in indices]

    logger.debug(f"Selected {len(samples)} temporal samples from {len(sorted_files)} files")

    return samples


if __name__ == "__main__":
    # Test the utilities
    import sys
    from config import CONVERSATIONS_DIR

    print("File Utilities Test")
    print("=" * 50)

    try:
        # Test directory stats
        stats = get_directory_stats(CONVERSATIONS_DIR, recursive=False)
        print(f"\nDirectory: {stats.path}")
        print(f"Total files: {stats.total_files}")
        print(f"Total size: {stats.total_size_mb:.2f} MB")

        if stats.oldest_file:
            print(f"Oldest file: {stats.oldest_file.path.name} ({stats.oldest_file.modified_time})")
        if stats.newest_file:
            print(f"Newest file: {stats.newest_file.path.name} ({stats.newest_file.modified_time})")

        if stats.extensions:
            print("\nFile extensions:")
            for ext, count in stats.extensions.items():
                print(f"  {ext}: {count}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
