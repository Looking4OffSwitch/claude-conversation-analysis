"""
Message tree builder for nested conversation display.

This module builds a tree structure from flat message lists based on parent-child relationships.
"""

from typing import List, Dict, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from conversation_parser import Message
from logger import setup_logger


logger = setup_logger(__name__)


class MessageTreeBuilder:
    """Builds a tree structure from flat message lists."""

    def __init__(self, messages: List[Message]):
        """
        Initialize tree builder.

        Args:
            messages: List of messages to build tree from.

        Raises:
            ValueError: If messages is None.
        """
        if messages is None:
            raise ValueError("messages cannot be None")

        self.messages = messages
        self.message_map: Dict[str, Message] = {}
        self.root_messages: List[Message] = []

    def build(self) -> List[Message]:
        """
        Build the message tree.

        Returns:
            List[Message]: Root-level messages with children populated.
        """
        logger.info(f"Building tree from {len(self.messages)} messages")

        # Create UUID -> Message lookup map
        for message in self.messages:
            self.message_map[message.uuid] = message

        # Build parent-child relationships
        for message in self.messages:
            if message.parent_uuid and message.parent_uuid in self.message_map:
                # This message has a parent, add it as a child
                parent = self.message_map[message.parent_uuid]
                parent.children.append(message)
            else:
                # This is a root message (no parent or parent not found)
                self.root_messages.append(message)

        # Sort root messages by timestamp
        self.root_messages.sort(key=lambda m: m.timestamp_ms)

        # Sort children recursively
        self._sort_children_recursive(self.root_messages)

        logger.info(f"Built tree with {len(self.root_messages)} root messages")

        return self.root_messages

    def _sort_children_recursive(self, messages: List[Message]) -> None:
        """
        Recursively sort children by timestamp.

        Args:
            messages: List of messages to sort children for.
        """
        for message in messages:
            if message.children:
                message.children.sort(key=lambda m: m.timestamp_ms)
                self._sort_children_recursive(message.children)

    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the message tree.

        Returns:
            Dict: Statistics including counts, depths, etc.
        """
        stats = {
            'total_messages': len(self.messages),
            'root_messages': len(self.root_messages),
            'max_depth': self._calculate_max_depth(),
            'message_types': self._count_message_types(),
            'sidechains': sum(1 for m in self.messages if m.is_sidechain),
            'sessions': len(set(m.session_id for m in self.messages if m.session_id)),
            'agents': len(set(m.agent_id for m in self.messages if m.agent_id)),
        }

        return stats

    def _calculate_max_depth(self) -> int:
        """Calculate maximum depth of the tree."""
        def get_depth(message: Message, current_depth: int = 0) -> int:
            if not message.children:
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in message.children)

        if not self.root_messages:
            return 0

        return max(get_depth(msg) for msg in self.root_messages)

    def _count_message_types(self) -> Dict[str, int]:
        """Count messages by type."""
        type_counts = {}
        for message in self.messages:
            type_counts[message.type] = type_counts.get(message.type, 0) + 1
        return type_counts

    def flatten_with_depth(self) -> List[tuple[Message, int]]:
        """
        Flatten the tree with depth information for linear display.

        Returns:
            List[tuple[Message, int]]: Messages with their depth level.
        """
        flattened = []

        def traverse(message: Message, depth: int = 0):
            flattened.append((message, depth))
            for child in message.children:
                traverse(child, depth + 1)

        for root in self.root_messages:
            traverse(root)

        return flattened


class SessionGrouper:
    """Groups messages by session for multi-session navigation."""

    def __init__(self, messages: List[Message]):
        """
        Initialize session grouper.

        Args:
            messages: List of messages to group.
        """
        self.messages = messages

    def group_by_session(self) -> Dict[str, List[Message]]:
        """
        Group messages by session ID.

        Returns:
            Dict[str, List[Message]]: Messages grouped by session ID.
        """
        sessions = {}

        for message in self.messages:
            session_id = message.session_id or 'unknown'
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append(message)

        # Sort messages within each session
        for session_id in sessions:
            sessions[session_id].sort(key=lambda m: m.timestamp_ms)

        return sessions

    def get_session_info(self) -> List[Dict[str, any]]:
        """
        Get information about each session.

        Returns:
            List[Dict]: Session information including counts, time ranges, etc.
        """
        sessions = self.group_by_session()
        session_info = []

        for session_id, messages in sessions.items():
            if not messages:
                continue

            first_msg = messages[0]
            last_msg = messages[-1]

            info = {
                'session_id': session_id,
                'message_count': len(messages),
                'first_timestamp': first_msg.timestamp,
                'last_timestamp': last_msg.timestamp,
                'duration_ms': last_msg.timestamp_ms - first_msg.timestamp_ms,
                'agents_used': list(set(m.agent_id for m in messages if m.agent_id)),
                'message_types': {},
            }

            # Count message types in this session
            for message in messages:
                msg_type = message.type
                info['message_types'][msg_type] = info['message_types'].get(msg_type, 0) + 1

            session_info.append(info)

        # Sort by first timestamp
        session_info.sort(key=lambda s: s['first_timestamp'])

        return session_info


if __name__ == "__main__":
    # Test the tree builder
    from conversation_parser import ConversationParser
    from pathlib import Path
    import sys

    config_path = Path(__file__).parent.parent / "config.py"
    sys.path.insert(0, str(config_path.parent))

    from config import CONVERSATIONS_DIR

    # Find a test project
    projects = list(CONVERSATIONS_DIR.iterdir())
    if projects:
        test_project = projects[0]
        print(f"Testing tree builder with: {test_project.name}")
        print("=" * 60)

        parser = ConversationParser(test_project)
        messages = parser.parse_all()

        builder = MessageTreeBuilder(messages)
        tree = builder.build()

        print(f"\nTree Statistics:")
        stats = builder.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print(f"\nFirst few root messages:")
        for i, msg in enumerate(tree[:3]):
            print(f"  {i+1}. {msg.type} - {msg.timestamp} - {len(msg.children)} children")

        # Test session grouper
        print(f"\nSession Information:")
        grouper = SessionGrouper(messages)
        session_info = grouper.get_session_info()
        for info in session_info[:3]:
            print(f"  Session {info['session_id'][:8]}...")
            print(f"    Messages: {info['message_count']}")
            print(f"    Duration: {info['duration_ms'] / 1000:.1f}s")

    else:
        print("No projects found for testing")
