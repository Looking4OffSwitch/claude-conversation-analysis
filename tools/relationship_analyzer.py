"""
Relationship analyzer for Claude conversation data.

This module analyzes relationships between different components in the .claude folder,
including ID cross-references, temporal correlations, and content references.
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional

from logger import setup_logger
from json_parser import parse_jsonl_file, parse_json_file
from config import CONVERSATIONS_DIR


# Initialize logger
logger = setup_logger(__name__)


@dataclass
class ComponentIdentifiers:
    """Identifiers found in a component."""

    component_name: str
    session_ids: Set[str] = field(default_factory=set)
    conversation_ids: Set[str] = field(default_factory=set)
    agent_ids: Set[str] = field(default_factory=set)
    message_uuids: Set[str] = field(default_factory=set)
    project_paths: Set[str] = field(default_factory=set)
    timestamps: List[float] = field(default_factory=list)
    file_count: int = 0

    def merge(self, other: 'ComponentIdentifiers') -> None:
        """
        Merge another ComponentIdentifiers into this one.

        Args:
            other: Another ComponentIdentifiers to merge.

        Raises:
            ValueError: If other is None.
            TypeError: If other is not ComponentIdentifiers.
        """
        if other is None:
            raise ValueError("other cannot be None")

        if not isinstance(other, ComponentIdentifiers):
            raise TypeError(f"Expected ComponentIdentifiers, got {type(other).__name__}")

        self.session_ids.update(other.session_ids)
        self.conversation_ids.update(other.conversation_ids)
        self.agent_ids.update(other.agent_ids)
        self.message_uuids.update(other.message_uuids)
        self.project_paths.update(other.project_paths)
        self.timestamps.extend(other.timestamps)
        self.file_count += other.file_count


@dataclass
class Relationship:
    """Represents a relationship between two components."""

    source_component: str
    target_component: str
    relationship_type: str  # 'id_sharing', 'temporal', 'content_reference', 'data_flow'
    strength: float  # 0.0 to 1.0
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (f"{self.source_component} -> {self.target_component} "
                f"({self.relationship_type}, strength: {self.strength:.2f})")


class IdentifierExtractor:
    """Extract identifiers from various file types."""

    # UUID pattern (8-4-4-4-12 hex digits)
    UUID_PATTERN = re.compile(
        r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
        re.IGNORECASE
    )

    # Agent ID pattern (agent-[hex])
    AGENT_ID_PATTERN = re.compile(r'\bagent-[0-9a-f]+\b', re.IGNORECASE)

    # Project path pattern
    PROJECT_PATH_PATTERN = re.compile(
        r'/Users/[^/]+/dev/[^/\s\"\'\)\]\}]+',
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize the identifier extractor."""
        self.logger = setup_logger(f"{__name__}.{self.__class__.__name__}")

    def extract_from_jsonl(self, file_path: Path) -> ComponentIdentifiers:
        """
        Extract identifiers from a JSONL file.

        Args:
            file_path: Path to the JSONL file.

        Returns:
            ComponentIdentifiers: Extracted identifiers.

        Raises:
            ValueError: If file_path is None.
            FileNotFoundError: If file doesn't exist.
        """
        if not file_path:
            raise ValueError("file_path cannot be None")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.debug(f"Extracting identifiers from JSONL: {file_path}")

        identifiers = ComponentIdentifiers(component_name=file_path.parent.name)
        identifiers.file_count = 1

        try:
            objects, _ = parse_jsonl_file(file_path, max_lines=1000)

            for obj in objects:
                self._extract_from_object(obj, identifiers)

        except Exception as e:
            self.logger.warning(f"Error extracting from {file_path}: {e}")

        return identifiers

    def extract_from_json(self, file_path: Path) -> ComponentIdentifiers:
        """
        Extract identifiers from a JSON file.

        Args:
            file_path: Path to the JSON file.

        Returns:
            ComponentIdentifiers: Extracted identifiers.

        Raises:
            ValueError: If file_path is None.
            FileNotFoundError: If file doesn't exist.
        """
        if not file_path:
            raise ValueError("file_path cannot be None")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.debug(f"Extracting identifiers from JSON: {file_path}")

        identifiers = ComponentIdentifiers(component_name=file_path.parent.name)
        identifiers.file_count = 1

        try:
            obj = parse_json_file(file_path)
            self._extract_from_object(obj, identifiers)

        except Exception as e:
            self.logger.warning(f"Error extracting from {file_path}: {e}")

        return identifiers

    def extract_from_text(self, file_path: Path) -> ComponentIdentifiers:
        """
        Extract identifiers from a text file.

        Args:
            file_path: Path to the text file.

        Returns:
            ComponentIdentifiers: Extracted identifiers.

        Raises:
            ValueError: If file_path is None.
            FileNotFoundError: If file doesn't exist.
        """
        if not file_path:
            raise ValueError("file_path cannot be None")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.debug(f"Extracting identifiers from text: {file_path}")

        identifiers = ComponentIdentifiers(component_name=file_path.parent.name)
        identifiers.file_count = 1

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)  # First 10KB

            # Extract UUIDs
            uuids = self.UUID_PATTERN.findall(content)
            identifiers.message_uuids.update(uuids)

            # Extract agent IDs
            agent_ids = self.AGENT_ID_PATTERN.findall(content)
            identifiers.agent_ids.update(agent_ids)

            # Extract project paths
            paths = self.PROJECT_PATH_PATTERN.findall(content)
            identifiers.project_paths.update(paths)

        except Exception as e:
            self.logger.warning(f"Error extracting from {file_path}: {e}")

        return identifiers

    def _extract_from_object(self, obj: Any, identifiers: ComponentIdentifiers) -> None:
        """
        Recursively extract identifiers from a JSON object.

        Args:
            obj: Object to extract from.
            identifiers: ComponentIdentifiers to populate.
        """
        if isinstance(obj, dict):
            # Extract known fields
            if 'sessionId' in obj:
                identifiers.session_ids.add(str(obj['sessionId']))

            if 'session_id' in obj:
                identifiers.session_ids.add(str(obj['session_id']))

            if 'agentId' in obj:
                identifiers.agent_ids.add(str(obj['agentId']))

            if 'agent_id' in obj:
                identifiers.agent_ids.add(str(obj['agent_id']))

            if 'uuid' in obj:
                identifiers.message_uuids.add(str(obj['uuid']))

            if 'messageId' in obj:
                identifiers.message_uuids.add(str(obj['messageId']))

            if 'project' in obj:
                identifiers.project_paths.add(str(obj['project']))

            if 'cwd' in obj:
                identifiers.project_paths.add(str(obj['cwd']))

            # Extract timestamps
            for timestamp_field in ['timestamp', 'modified', 'created']:
                if timestamp_field in obj:
                    try:
                        ts = obj[timestamp_field]
                        if isinstance(ts, (int, float)):
                            identifiers.timestamps.append(float(ts))
                        elif isinstance(ts, str):
                            # Try parsing ISO format
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            identifiers.timestamps.append(dt.timestamp())
                    except Exception:
                        pass

            # Recurse into nested objects
            for value in obj.values():
                self._extract_from_object(value, identifiers)

        elif isinstance(obj, list):
            for item in obj:
                self._extract_from_object(item, identifiers)


class RelationshipAnalyzer:
    """Analyze relationships between components."""

    def __init__(self):
        """Initialize the relationship analyzer."""
        self.logger = setup_logger(f"{__name__}.{self.__class__.__name__}")
        self.extractor = IdentifierExtractor()
        self.component_identifiers: Dict[str, ComponentIdentifiers] = {}

    def analyze_component(self, component_path: Path, component_name: str) -> ComponentIdentifiers:
        """
        Analyze a component directory and extract all identifiers.

        Args:
            component_path: Path to the component directory.
            component_name: Name of the component.

        Returns:
            ComponentIdentifiers: Aggregated identifiers for the component.

        Raises:
            ValueError: If parameters are invalid.
            FileNotFoundError: If component_path doesn't exist.
        """
        if not component_path:
            raise ValueError("component_path cannot be None")

        if not component_name:
            raise ValueError("component_name cannot be empty")

        if not component_path.exists():
            raise FileNotFoundError(f"Component path not found: {component_path}")

        self.logger.info(f"Analyzing component: {component_name}")

        aggregated = ComponentIdentifiers(component_name=component_name)

        # Get all files in the component
        files = [f for f in component_path.rglob("*") if f.is_file()]

        # Sample files if too many
        if len(files) > 100:
            self.logger.info(f"Sampling 100 of {len(files)} files in {component_name}")
            # Sample: first 30, middle 40, last 30
            files = files[:30] + files[len(files)//2 - 20:len(files)//2 + 20] + files[-30:]

        for file_path in files:
            try:
                if file_path.suffix == '.jsonl':
                    ids = self.extractor.extract_from_jsonl(file_path)
                    aggregated.merge(ids)
                elif file_path.suffix == '.json':
                    ids = self.extractor.extract_from_json(file_path)
                    aggregated.merge(ids)
                elif file_path.suffix in {'.md', '.txt', '.log'}:
                    ids = self.extractor.extract_from_text(file_path)
                    aggregated.merge(ids)
            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")

        self.logger.info(
            f"Component {component_name}: "
            f"{len(aggregated.session_ids)} sessions, "
            f"{len(aggregated.conversation_ids)} conversations, "
            f"{len(aggregated.agent_ids)} agents, "
            f"{len(aggregated.message_uuids)} messages, "
            f"{len(aggregated.project_paths)} projects"
        )

        return aggregated

    def analyze_file(self, file_path: Path, component_name: str) -> ComponentIdentifiers:
        """
        Analyze a single file.

        Args:
            file_path: Path to the file.
            component_name: Name of the component.

        Returns:
            ComponentIdentifiers: Identifiers from the file.
        """
        if not file_path or not file_path.exists():
            raise ValueError(f"Invalid file path: {file_path}")

        self.logger.info(f"Analyzing file: {file_path} ({component_name})")

        try:
            if file_path.suffix == '.jsonl':
                return self.extractor.extract_from_jsonl(file_path)
            elif file_path.suffix == '.json':
                return self.extractor.extract_from_json(file_path)
            elif file_path.suffix in {'.md', '.txt', '.log'}:
                return self.extractor.extract_from_text(file_path)
            else:
                return ComponentIdentifiers(component_name=component_name)
        except Exception as e:
            self.logger.error(f"Error analyzing file: {e}")
            return ComponentIdentifiers(component_name=component_name)

    def find_id_relationships(
        self,
        source: ComponentIdentifiers,
        target: ComponentIdentifiers
    ) -> Optional[Relationship]:
        """
        Find ID-based relationships between two components.

        Args:
            source: Source component identifiers.
            target: Target component identifiers.

        Returns:
            Optional[Relationship]: Relationship if found, None otherwise.
        """
        if not source or not target:
            return None

        shared_sessions = source.session_ids & target.session_ids
        shared_agents = source.agent_ids & target.agent_ids
        shared_messages = source.message_uuids & target.message_uuids
        shared_projects = source.project_paths & target.project_paths

        total_shared = (len(shared_sessions) + len(shared_agents) +
                       len(shared_messages) + len(shared_projects))

        if total_shared == 0:
            return None

        # Calculate strength (0-1) based on overlap percentage
        source_total = (len(source.session_ids) + len(source.agent_ids) +
                       len(source.message_uuids) + len(source.project_paths))
        target_total = (len(target.session_ids) + len(target.agent_ids) +
                       len(target.message_uuids) + len(target.project_paths))

        avg_total = (source_total + target_total) / 2 if (source_total + target_total) > 0 else 1
        strength = min(1.0, total_shared / avg_total)

        return Relationship(
            source_component=source.component_name,
            target_component=target.component_name,
            relationship_type='id_sharing',
            strength=strength,
            details={
                'shared_sessions': len(shared_sessions),
                'shared_agents': len(shared_agents),
                'shared_messages': len(shared_messages),
                'shared_projects': len(shared_projects),
                'sample_sessions': list(shared_sessions)[:5],
                'sample_projects': list(shared_projects)[:5]
            }
        )

    def find_temporal_relationships(
        self,
        source: ComponentIdentifiers,
        target: ComponentIdentifiers
    ) -> Optional[Relationship]:
        """
        Find temporal relationships between two components.

        Args:
            source: Source component identifiers.
            target: Target component identifiers.

        Returns:
            Optional[Relationship]: Relationship if found, None otherwise.
        """
        if not source.timestamps or not target.timestamps:
            return None

        source_min = min(source.timestamps)
        source_max = max(source.timestamps)
        target_min = min(target.timestamps)
        target_max = max(target.timestamps)

        # Check for temporal overlap
        overlap_start = max(source_min, target_min)
        overlap_end = min(source_max, target_max)

        if overlap_start >= overlap_end:
            # No overlap
            return None

        overlap_duration = overlap_end - overlap_start
        source_duration = source_max - source_min
        target_duration = target_max - target_min

        avg_duration = (source_duration + target_duration) / 2
        strength = min(1.0, overlap_duration / avg_duration if avg_duration > 0 else 0)

        # Determine causality direction
        if source_min < target_min:
            direction = f"{source.component_name} precedes {target.component_name}"
        else:
            direction = f"{target.component_name} precedes {source.component_name}"

        return Relationship(
            source_component=source.component_name,
            target_component=target.component_name,
            relationship_type='temporal',
            strength=strength,
            details={
                'overlap_percentage': strength * 100,
                'direction': direction,
                'source_range': (datetime.fromtimestamp(source_min).isoformat(),
                               datetime.fromtimestamp(source_max).isoformat()),
                'target_range': (datetime.fromtimestamp(target_min).isoformat(),
                               datetime.fromtimestamp(target_max).isoformat())
            }
        )

    def analyze_all_relationships(
        self,
        components: Dict[str, ComponentIdentifiers]
    ) -> List[Relationship]:
        """
        Analyze all pairwise relationships between components.

        Args:
            components: Dictionary mapping component names to their identifiers.

        Returns:
            List[Relationship]: List of all discovered relationships.
        """
        self.logger.info(f"Analyzing relationships between {len(components)} components")

        relationships = []
        component_list = list(components.values())

        for i, source in enumerate(component_list):
            for target in component_list[i+1:]:
                # Find ID-based relationships
                id_rel = self.find_id_relationships(source, target)
                if id_rel and id_rel.strength > 0.01:  # Threshold
                    relationships.append(id_rel)

                # Find temporal relationships
                temporal_rel = self.find_temporal_relationships(source, target)
                if temporal_rel and temporal_rel.strength > 0.1:  # Threshold
                    relationships.append(temporal_rel)

        self.logger.info(f"Found {len(relationships)} relationships")

        return relationships


if __name__ == "__main__":
    # Test the relationship analyzer
    print("Relationship Analyzer Test")
    print("=" * 50)

    analyzer = RelationshipAnalyzer()

    # Test analyzing a component
    projects_path = CONVERSATIONS_DIR / "projects"
    if projects_path.exists():
        print(f"\nAnalyzing projects component...")
        projects_ids = analyzer.analyze_component(projects_path, "projects")
        print(f"Found {len(projects_ids.session_ids)} sessions")
        print(f"Found {len(projects_ids.project_paths)} projects")
