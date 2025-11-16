#!/usr/bin/env python3
"""
Master analysis script for Claude conversation data.

This script orchestrates all individual analyzers to generate comprehensive
documentation for the entire .claude folder structure.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add tools directory to Python path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from logger import setup_logger, log_exception
from config import CONVERSATIONS_DIR, RESEARCH_DIR, validate_config
from markdown_generator import MarkdownBuilder, save_markdown

# Import all analyzers
from analyze_markdown_folders import MarkdownFolderAnalyzer
from analyze_json_files import JsonFileAnalyzer, PluginsAnalyzer
from analyze_jsonl_files import JsonlFileAnalyzer, JsonlFolderAnalyzer
from analyze_misc_folders import (
    DebugAnalyzer,
    SessionEnvAnalyzer,
    ShellSnapshotsAnalyzer,
    StatsigAnalyzer,
    FileHistoryAnalyzer,
    IdeAnalyzer
)


# Initialize logger
logger = setup_logger("analyze_all", "INFO")


def create_analyzer_instances():
    """
    Create all analyzer instances.

    Returns:
        list: List of (name, analyzer) tuples.
    """
    logger.info("Creating analyzer instances...")

    analyzers = []

    # Markdown folders
    analyzers.append(("agents", MarkdownFolderAnalyzer(
        "agents",
        "Custom agent definitions for specialized tasks. Each markdown file defines "
        "an agent's behavior, capabilities, and tools. Agents are loaded dynamically "
        "when invoked via the Task tool."
    )))

    analyzers.append(("commands", MarkdownFolderAnalyzer(
        "commands",
        "Custom slash commands that expand into prompts. Each markdown file contains "
        "instructions that are injected into the conversation when the command is used. "
        "Commands provide reusable workflows and standardized prompts."
    )))

    # JSON files
    settings_analyzer = JsonFileAnalyzer(
        folder_name="settings",
        purpose_description="Global Claude Code settings including status line configuration, "
                          "feature flags, and user preferences. This file persists settings across sessions.",
        relative_file_path=""
    )
    settings_analyzer.source_file = CONVERSATIONS_DIR / "settings.json"
    analyzers.append(("settings", settings_analyzer))

    analyzers.append(("plugins", PluginsAnalyzer()))

    # JSONL files
    history_file = CONVERSATIONS_DIR / "history.jsonl"
    if history_file.exists():
        analyzers.append(("history", JsonlFileAnalyzer(
            folder_name="history",
            purpose_description="Global conversation history containing all messages, tool calls, "
                              "and responses across all projects. Each line represents one conversation turn.",
            file_path=history_file
        )))

    analyzers.append(("projects", JsonlFolderAnalyzer(
        folder_name="projects",
        purpose_description="Project-specific conversation histories. Each project has its own "
                          "directory with JSONL files for individual conversations. Files are named "
                          "with conversation IDs or agent IDs."
    )))

    analyzers.append(("todos", JsonlFolderAnalyzer(
        folder_name="todos",
        purpose_description="Todo list persistence data. Contains JSONL files tracking todo items "
                          "across different sessions and projects. Each entry represents todo state changes."
    )))

    # Misc folders
    analyzers.append(("debug", DebugAnalyzer()))
    analyzers.append(("session-env", SessionEnvAnalyzer()))
    analyzers.append(("shell-snapshots", ShellSnapshotsAnalyzer()))
    analyzers.append(("statsig", StatsigAnalyzer()))
    analyzers.append(("file-history", FileHistoryAnalyzer()))
    analyzers.append(("ide", IdeAnalyzer()))

    logger.info(f"Created {len(analyzers)} analyzer instances")
    return analyzers


def run_all_analyzers(analyzers):
    """
    Run all analyzers and collect results.

    Args:
        analyzers: List of (name, analyzer) tuples.

    Returns:
        dict: Dictionary mapping analyzer names to their output paths.
    """
    logger.info(f"Running {len(analyzers)} analyzers...")

    results = {}
    failed = []

    for name, analyzer in analyzers:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Analyzing: {name}")
        logger.info(f"{'=' * 60}")

        try:
            output_path = analyzer.run()
            results[name] = output_path
            logger.info(f"✓ {name} analysis complete: {output_path}")

        except Exception as e:
            logger.error(f"✗ {name} analysis failed: {e}")
            log_exception(logger, e, f"{name} analysis")
            failed.append(name)

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Analysis Summary")
    logger.info(f"{'=' * 60}")
    logger.info(f"Successful: {len(results)}/{len(analyzers)}")
    logger.info(f"Failed: {len(failed)}/{len(analyzers)}")

    if failed:
        logger.warning(f"Failed analyzers: {', '.join(failed)}")

    return results, failed


def generate_master_readme(results, failed):
    """
    Generate master README.md with overview and links to all reports.

    Args:
        results: Dictionary mapping analyzer names to output paths.
        failed: List of failed analyzer names.
    """
    logger.info("Generating master README.md...")

    builder = MarkdownBuilder("Claude Conversation Data Analysis")

    # Introduction
    builder.add_header("Overview", level=2)
    builder.add_text(
        "This directory contains comprehensive documentation of the Claude Code conversation "
        "data structure. Each subfolder has been analyzed to document its purpose, data structure, "
        "temporal evolution, and provide sanitized examples."
    )

    builder.add_text(
        f"**Analysis completed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    builder.add_text(
        f"**Total components analyzed**: {len(results) + len(failed)}\n"
        f"**Successful**: {len(results)}\n"
        f"**Failed**: {len(failed)}"
    )

    # Table of Contents
    builder.add_header("Components", level=2)

    builder.add_text(
        "The `.claude` directory contains the following components. "
        "Click on each component to view detailed documentation."
    )

    # Group by category
    categories = {
        "Configuration": ["agents", "commands", "settings", "plugins"],
        "Conversation Data": ["history", "projects"],
        "State & Persistence": ["todos", "session-env", "shell-snapshots", "file-history"],
        "System & Diagnostics": ["debug", "statsig", "ide"]
    }

    for category, components in categories.items():
        builder.add_header(category, level=3)

        items = []
        for component in components:
            if component in results:
                # Relative path to the component README
                rel_path = f"./{component}/README.md"
                items.append(f"[**{component}**]({rel_path}) - View detailed analysis")
            elif component in failed:
                items.append(f"**{component}** - ⚠️  Analysis failed")
            else:
                items.append(f"**{component}** - Not analyzed")

        builder.add_list(items)

    # High-level structure
    builder.add_header("Directory Structure", level=2)

    builder.add_code_block("""conversations/.claude/
├── agents/           # Custom agent definitions
├── commands/         # Custom slash commands
├── debug/            # Debug logs
├── file-history/     # File version history
├── ide/              # IDE integration data
├── plugins/          # Plugin configuration
├── projects/         # Project-specific conversations
├── session-env/      # Session environment data
├── shell-snapshots/  # Shell state snapshots
├── statsig/          # Statistics and feature flags
├── todos/            # Todo list persistence
├── history.jsonl     # Global conversation history
├── settings.json     # Global settings
└── CLAUDE.md         # Project-specific instructions
""", language="text")

    # Key Findings
    builder.add_header("Key Findings", level=2)

    findings = [
        "**Conversation data** is stored in JSONL format with one JSON object per line",
        "**Projects** are organized in separate directories with encoded path names",
        "**Settings** persist user preferences and configuration across sessions",
        "**Custom commands and agents** extend Claude Code functionality via markdown definitions",
        "**State data** (todos, shell snapshots, session env) enables session persistence",
        "**Debug logs** provide detailed execution traces for troubleshooting"
    ]

    builder.add_list(findings)

    # Usage
    builder.add_header("How to Use This Documentation", level=2)

    builder.add_text(
        "1. Start with the component you're interested in from the sections above\n"
        "2. Each component's README contains:\n"
        "   - Purpose and responsibility\n"
        "   - Statistics (file counts, sizes, dates)\n"
        "   - Data structure and schema documentation\n"
        "   - Temporal evolution analysis\n"
        "   - Sanitized examples from real data"
    )

    # Failed analyses
    if failed:
        builder.add_header("Failed Analyses", level=2)
        builder.add_text(
            "The following components could not be analyzed. Check the logs for details:"
        )
        builder.add_list(failed)

    # Save
    markdown = builder.build()
    output_path = RESEARCH_DIR / "README.md"
    save_markdown(markdown, output_path)

    logger.info(f"Master README saved to: {output_path}")


def main():
    """Main entry point for the analysis script."""
    print("=" * 70)
    print("Claude Conversation Data Analysis")
    print("=" * 70)
    print()

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_config()
        logger.info(f"✓ Configuration valid")
        logger.info(f"  Source: {CONVERSATIONS_DIR}")
        logger.info(f"  Output: {RESEARCH_DIR}")
        print()

        # Create analyzers
        analyzers = create_analyzer_instances()
        print()

        # Run all analyzers
        results, failed = run_all_analyzers(analyzers)
        print()

        # Generate master README
        generate_master_readme(results, failed)
        print()

        # Final summary
        print("=" * 70)
        print("Analysis Complete!")
        print("=" * 70)
        print(f"✓ {len(results)} components analyzed successfully")
        if failed:
            print(f"✗ {len(failed)} components failed")
        print(f"\nResults saved to: {RESEARCH_DIR}")
        print(f"View master README at: {RESEARCH_DIR / 'README.md'}")
        print()

        return 0 if not failed else 1

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        log_exception(logger, e, "main")
        print(f"\n✗ Analysis failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
