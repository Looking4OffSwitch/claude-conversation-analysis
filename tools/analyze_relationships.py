#!/usr/bin/env python3
"""
Relationship analysis script for Claude conversation data.

This script analyzes relationships between all components in the .claude folder
and updates documentation with relationship information.
"""

import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

# Add tools directory to Python path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from logger import setup_logger, log_exception
from config import CONVERSATIONS_DIR, RESEARCH_DIR, validate_config
from relationship_analyzer import RelationshipAnalyzer, ComponentIdentifiers, Relationship
from markdown_generator import MarkdownBuilder, save_markdown


# Initialize logger
logger = setup_logger("analyze_relationships", "INFO")


# Component definitions
COMPONENTS = {
    'agents': {'type': 'folder', 'path': 'agents'},
    'commands': {'type': 'folder', 'path': 'commands'},
    'debug': {'type': 'folder', 'path': 'debug'},
    'file-history': {'type': 'folder', 'path': 'file-history'},
    'ide': {'type': 'folder', 'path': 'ide'},
    'plugins': {'type': 'folder', 'path': 'plugins'},
    'projects': {'type': 'folder', 'path': 'projects'},
    'session-env': {'type': 'folder', 'path': 'session-env'},
    'shell-snapshots': {'type': 'folder', 'path': 'shell-snapshots'},
    'statsig': {'type': 'folder', 'path': 'statsig'},
    'todos': {'type': 'folder', 'path': 'todos'},
    'history': {'type': 'file', 'path': 'history.jsonl'},
    'settings': {'type': 'file', 'path': 'settings.json'},
}


def analyze_all_components() -> Dict[str, ComponentIdentifiers]:
    """
    Analyze all components and extract their identifiers.

    Returns:
        Dict[str, ComponentIdentifiers]: Component name to identifiers mapping.
    """
    logger.info("Analyzing all components for identifiers...")

    analyzer = RelationshipAnalyzer()
    component_identifiers = {}

    for name, config in COMPONENTS.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing component: {name}")
        logger.info(f"{'='*60}")

        try:
            if config['type'] == 'folder':
                path = CONVERSATIONS_DIR / config['path']
                if path.exists():
                    identifiers = analyzer.analyze_component(path, name)
                    component_identifiers[name] = identifiers
                else:
                    logger.warning(f"Component path not found: {path}")
                    # Create empty identifiers
                    component_identifiers[name] = ComponentIdentifiers(component_name=name)

            elif config['type'] == 'file':
                path = CONVERSATIONS_DIR / config['path']
                if path.exists():
                    identifiers = analyzer.analyze_file(path, name)
                    component_identifiers[name] = identifiers
                else:
                    logger.warning(f"Component file not found: {path}")
                    component_identifiers[name] = ComponentIdentifiers(component_name=name)

        except Exception as e:
            logger.error(f"Error analyzing {name}: {e}")
            log_exception(logger, e, f"analyze {name}")
            component_identifiers[name] = ComponentIdentifiers(component_name=name)

    return component_identifiers


def find_all_relationships(
    component_identifiers: Dict[str, ComponentIdentifiers]
) -> List[Relationship]:
    """
    Find all relationships between components.

    Args:
        component_identifiers: Component identifiers dictionary.

    Returns:
        List[Relationship]: All discovered relationships.
    """
    logger.info("\nFinding relationships between components...")

    analyzer = RelationshipAnalyzer()
    relationships = analyzer.analyze_all_relationships(component_identifiers)

    # Sort by strength (strongest first)
    relationships.sort(key=lambda r: r.strength, reverse=True)

    logger.info(f"Found {len(relationships)} total relationships")

    return relationships


def build_relationship_matrix(
    component_identifiers: Dict[str, ComponentIdentifiers],
    relationships: List[Relationship]
) -> Dict[str, Dict[str, List[Relationship]]]:
    """
    Build a matrix of relationships for easy lookup.

    Args:
        component_identifiers: Component identifiers.
        relationships: List of all relationships.

    Returns:
        Dict mapping source -> target -> list of relationships.
    """
    matrix = defaultdict(lambda: defaultdict(list))

    for rel in relationships:
        matrix[rel.source_component][rel.target_component].append(rel)
        # Add reverse relationship
        matrix[rel.target_component][rel.source_component].append(rel)

    return dict(matrix)


def generate_relationship_section(
    component_name: str,
    matrix: Dict[str, Dict[str, List[Relationship]]],
    component_identifiers: Dict[str, ComponentIdentifiers]
) -> str:
    """
    Generate markdown section documenting relationships for a component.

    Args:
        component_name: Name of the component.
        matrix: Relationship matrix.
        component_identifiers: All component identifiers.

    Returns:
        str: Markdown content for relationships section.
    """
    builder = MarkdownBuilder()
    builder.add_header("Relationships to Other Components", level=2)

    if component_name not in matrix or not matrix[component_name]:
        builder.add_text(
            "**No significant relationships found** with other components. "
            "This component operates independently."
        )
        builder.add_text(
            "*Analysis checked for: shared session IDs, conversation IDs, agent IDs, "
            "message UUIDs, project paths, and temporal correlations.*"
        )
        return builder.build()

    # Get relationships for this component
    related_components = matrix[component_name]

    # Sort by total strength
    sorted_components = sorted(
        related_components.items(),
        key=lambda x: sum(r.strength for r in x[1]),
        reverse=True
    )

    builder.add_text(
        f"This component has **{len(sorted_components)} relationships** with other components:"
    )

    for target_name, rels in sorted_components:
        builder.add_header(target_name, level=3)

        # Group relationships by type
        by_type = defaultdict(list)
        for rel in rels:
            by_type[rel.relationship_type].append(rel)

        # ID sharing relationships
        if 'id_sharing' in by_type:
            for rel in by_type['id_sharing']:
                strength_pct = rel.strength * 100
                builder.add_text(f"**Relationship Type**: ID Sharing (strength: {strength_pct:.1f}%)")

                details = rel.details
                shared_info = []

                if details.get('shared_sessions', 0) > 0:
                    shared_info.append(f"- **Shared Sessions**: {details['shared_sessions']}")

                if details.get('shared_agents', 0) > 0:
                    shared_info.append(f"- **Shared Agent IDs**: {details['shared_agents']}")

                if details.get('shared_messages', 0) > 0:
                    shared_info.append(f"- **Shared Message UUIDs**: {details['shared_messages']}")

                if details.get('shared_projects', 0) > 0:
                    shared_info.append(f"- **Shared Project Paths**: {details['shared_projects']}")
                    if details.get('sample_projects'):
                        builder.add_text("\n".join(shared_info))
                        builder.add_text("\n**Sample Shared Projects**:")
                        builder.add_list(details['sample_projects'][:3])
                        shared_info = []

                if shared_info:
                    builder.add_text("\n".join(shared_info))

        # Temporal relationships
        if 'temporal' in by_type:
            for rel in by_type['temporal']:
                strength_pct = rel.strength * 100
                builder.add_text(f"**Relationship Type**: Temporal Correlation (overlap: {strength_pct:.1f}%)")

                details = rel.details
                builder.add_text(f"- **Direction**: {details.get('direction', 'Unknown')}")

                source_range = details.get('source_range', ('Unknown', 'Unknown'))
                target_range = details.get('target_range', ('Unknown', 'Unknown'))

                builder.add_text(
                    f"- **{component_name} Active**: {source_range[0][:10]} to {source_range[1][:10]}"
                )
                builder.add_text(
                    f"- **{target_name} Active**: {target_range[0][:10]} to {target_range[1][:10]}"
                )

    # Summary statistics
    builder.add_header("Relationship Summary", level=3)

    ids = component_identifiers[component_name]
    summary_items = []

    if ids.session_ids:
        summary_items.append(f"**Session IDs tracked**: {len(ids.session_ids)}")

    if ids.agent_ids:
        summary_items.append(f"**Agent IDs tracked**: {len(ids.agent_ids)}")

    if ids.message_uuids:
        summary_items.append(f"**Message UUIDs tracked**: {len(ids.message_uuids)}")

    if ids.project_paths:
        summary_items.append(f"**Project paths tracked**: {len(ids.project_paths)}")

    if ids.timestamps:
        summary_items.append(f"**Time span**: {len(ids.timestamps)} timestamps")

    if summary_items:
        builder.add_list(summary_items)

    return builder.build()


def update_component_readme(
    component_name: str,
    relationship_section: str
) -> None:
    """
    Update a component's README with relationship information.

    Args:
        component_name: Name of the component.
        relationship_section: Markdown content for relationships.
    """
    readme_path = RESEARCH_DIR / component_name / "README.md"

    if not readme_path.exists():
        logger.warning(f"README not found for {component_name}: {readme_path}")
        return

    try:
        # Read existing content
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if relationships section already exists
        if "## Relationships to Other Components" in content:
            # Remove old section
            parts = content.split("## Relationships to Other Components")
            # Find the next ## header
            after_section = parts[1]
            next_header_pos = after_section.find("\n## ")

            if next_header_pos != -1:
                content = parts[0] + after_section[next_header_pos:]
            else:
                # Relationships was the last section
                content = parts[0]

        # Add new relationships section (before the last line)
        content = content.rstrip() + "\n\n" + relationship_section + "\n"

        # Write back
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Updated README for {component_name}")

    except Exception as e:
        logger.error(f"Error updating README for {component_name}: {e}")
        log_exception(logger, e, f"update README {component_name}")


def generate_master_relationships_doc(
    component_identifiers: Dict[str, ComponentIdentifiers],
    relationships: List[Relationship],
    matrix: Dict[str, Dict[str, List[Relationship]]]
) -> None:
    """
    Generate master RELATIONSHIPS.md document.

    Args:
        component_identifiers: All component identifiers.
        relationships: All relationships.
        matrix: Relationship matrix.
    """
    logger.info("Generating master RELATIONSHIPS.md...")

    builder = MarkdownBuilder("Component Relationships Analysis")

    # Overview
    builder.add_header("Overview", level=2)
    builder.add_text(
        "This document provides a comprehensive analysis of relationships between "
        "different components in the Claude Code conversation data structure. "
        "Relationships are identified through shared identifiers (session IDs, conversation IDs, "
        "agent IDs, message UUIDs, project paths) and temporal correlations."
    )

    # Statistics
    builder.add_header("Summary Statistics", level=2)

    total_rels = len(relationships)
    id_rels = len([r for r in relationships if r.relationship_type == 'id_sharing'])
    temporal_rels = len([r for r in relationships if r.relationship_type == 'temporal'])

    stats = [
        f"**Total Relationships Found**: {total_rels}",
        f"**ID Sharing Relationships**: {id_rels}",
        f"**Temporal Correlation Relationships**: {temporal_rels}",
        f"**Components Analyzed**: {len(component_identifiers)}",
    ]

    builder.add_list(stats)

    # Relationship Matrix
    builder.add_header("Relationship Matrix", level=2)
    builder.add_text(
        "The following matrix shows which components have relationships with each other. "
        "Strength is indicated by the number of relationship types found."
    )

    # Build matrix table
    component_names = sorted(component_identifiers.keys())
    headers = ["Component"] + component_names

    rows = []
    for source in component_names:
        row = [source]
        for target in component_names:
            if source == target:
                cell = "-"
            elif target in matrix.get(source, {}):
                rel_count = len(matrix[source][target])
                cell = f"✓ ({rel_count})"
            else:
                cell = ""
            row.append(cell)
        rows.append(row)

    builder.add_table(headers, rows)

    # Strongest Relationships
    builder.add_header("Strongest Relationships", level=2)
    builder.add_text(
        "The following are the strongest relationships found, sorted by relationship strength:"
    )

    top_relationships = relationships[:20]  # Top 20

    for i, rel in enumerate(top_relationships, 1):
        strength_pct = rel.strength * 100
        builder.add_header(
            f"{i}. {rel.source_component} ↔ {rel.target_component}",
            level=3
        )
        builder.add_text(
            f"**Type**: {rel.relationship_type.replace('_', ' ').title()}\n"
            f"**Strength**: {strength_pct:.1f}%"
        )

        if rel.relationship_type == 'id_sharing':
            details = rel.details
            info = []
            if details.get('shared_sessions'):
                info.append(f"Shared Sessions: {details['shared_sessions']}")
            if details.get('shared_agents'):
                info.append(f"Shared Agents: {details['shared_agents']}")
            if details.get('shared_messages'):
                info.append(f"Shared Messages: {details['shared_messages']}")
            if details.get('shared_projects'):
                info.append(f"Shared Projects: {details['shared_projects']}")

            if info:
                builder.add_text("**Details**: " + ", ".join(info))

    # Isolated Components
    builder.add_header("Isolated Components", level=2)
    isolated = [name for name in component_names if name not in matrix or not matrix[name]]

    if isolated:
        builder.add_text(
            "The following components have **no significant relationships** with other components:"
        )
        builder.add_list(isolated)
        builder.add_text(
            "*These components operate independently and do not share identifiers or "
            "have temporal correlations with other components.*"
        )
    else:
        builder.add_text("All components have at least one relationship with another component.")

    # Component Details
    builder.add_header("Component Details", level=2)

    for name, ids in sorted(component_identifiers.items()):
        builder.add_header(name, level=3)

        details = []
        if ids.session_ids:
            details.append(f"Session IDs: {len(ids.session_ids)}")
        if ids.agent_ids:
            details.append(f"Agent IDs: {len(ids.agent_ids)}")
        if ids.message_uuids:
            details.append(f"Message UUIDs: {len(ids.message_uuids)}")
        if ids.project_paths:
            details.append(f"Project Paths: {len(ids.project_paths)}")
        if ids.timestamps:
            details.append(f"Timestamps: {len(ids.timestamps)}")

        if details:
            builder.add_text(", ".join(details))
        else:
            builder.add_text("*No identifiers found*")

    # Save
    markdown = builder.build()
    output_path = RESEARCH_DIR / "RELATIONSHIPS.md"
    save_markdown(markdown, output_path)

    logger.info(f"Master relationships document saved to: {output_path}")


def main():
    """Main entry point."""
    print("=" * 70)
    print("Claude Conversation Relationship Analysis")
    print("=" * 70)
    print()

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_config()
        logger.info("✓ Configuration valid")
        print()

        # Analyze all components
        component_identifiers = analyze_all_components()
        print()

        # Find relationships
        relationships = find_all_relationships(component_identifiers)
        print()

        # Build relationship matrix
        logger.info("Building relationship matrix...")
        matrix = build_relationship_matrix(component_identifiers, relationships)

        # Update component READMEs
        logger.info("\nUpdating component READMEs...")
        for component_name in COMPONENTS.keys():
            logger.info(f"Updating {component_name}...")
            relationship_section = generate_relationship_section(
                component_name,
                matrix,
                component_identifiers
            )
            update_component_readme(component_name, relationship_section)

        # Generate master document
        generate_master_relationships_doc(
            component_identifiers,
            relationships,
            matrix
        )

        # Final summary
        print()
        print("=" * 70)
        print("Relationship Analysis Complete!")
        print("=" * 70)
        print(f"✓ Found {len(relationships)} relationships")
        print(f"✓ Updated {len(COMPONENTS)} component READMEs")
        print(f"✓ Generated master RELATIONSHIPS.md")
        print(f"\nView results at: {RESEARCH_DIR / 'RELATIONSHIPS.md'}")
        print()

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        log_exception(logger, e, "main")
        print(f"\n✗ Analysis failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
