"""
Conversation parser for Claude Code project conversations.

This module parses JSONL conversation files and extracts structured message data.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from logger import setup_logger


logger = setup_logger(__name__)


@dataclass
class Message:
    """Represents a single message in a conversation."""

    uuid: str
    timestamp: str
    timestamp_ms: int
    type: str  # 'user', 'assistant', 'tool_use', 'tool_result', 'system', etc.
    content: Any
    parent_uuid: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    is_sidechain: bool = False
    tool_name: Optional[str] = None
    tool_use_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List['Message'] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary, excluding circular references."""
        data = asdict(self)
        # Remove children from dict to avoid circular references
        # They'll be added separately when needed
        data.pop('children', None)
        return data


class ConversationParser:
    """Parser for Claude Code conversation files."""

    def __init__(self, project_path: Path):
        """
        Initialize conversation parser.

        Args:
            project_path: Path to the project directory.

        Raises:
            ValueError: If project_path is invalid.
            FileNotFoundError: If project doesn't exist.
        """
        if not project_path:
            raise ValueError("project_path cannot be None")

        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")

        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        self.project_path = project_path
        self.project_id = self._generate_project_id()
        self.logger = setup_logger(f"{__name__}.{self.project_id}")

    def _generate_project_id(self) -> str:
        """Generate a unique ID for this project based on path."""
        path_str = str(self.project_path)
        return hashlib.md5(path_str.encode()).hexdigest()[:12]

    def parse_all(self) -> List[Message]:
        """
        Parse all conversation files in the project directory.

        Returns:
            List[Message]: All messages from all conversation files.

        Raises:
            Exception: If parsing fails.
        """
        self.logger.info(f"Parsing conversations in: {self.project_path}")

        all_messages = []
        jsonl_files = list(self.project_path.glob("*.jsonl"))

        self.logger.info(f"Found {len(jsonl_files)} conversation files")

        for jsonl_file in jsonl_files:
            try:
                messages = self._parse_file(jsonl_file)
                all_messages.extend(messages)
                self.logger.debug(f"Parsed {len(messages)} messages from {jsonl_file.name}")
            except Exception as e:
                self.logger.error(f"Error parsing {jsonl_file.name}: {e}")
                # Continue with other files

        # Sort all messages by timestamp
        all_messages.sort(key=lambda m: m.timestamp_ms)

        self.logger.info(f"Parsed {len(all_messages)} total messages")

        return all_messages

    def _parse_file(self, file_path: Path) -> List[Message]:
        """
        Parse a single JSONL conversation file.

        Args:
            file_path: Path to the JSONL file.

        Returns:
            List[Message]: Messages from the file.
        """
        messages = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    message = self._parse_message(data)
                    if message:
                        messages.append(message)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON decode error in {file_path.name}:{line_num}: {e}")
                except Exception as e:
                    self.logger.warning(f"Error parsing message in {file_path.name}:{line_num}: {e}")

        return messages

    def _parse_message(self, data: Dict[str, Any]) -> Optional[Message]:
        """
        Parse a single message from JSON data.

        Args:
            data: Message data dictionary.

        Returns:
            Optional[Message]: Parsed message or None if invalid.
        """
        # Determine message type
        msg_type = data.get('type', 'unknown')

        # Extract UUID
        uuid = data.get('uuid')
        if not uuid:
            # Some messages might not have UUID, skip them
            return None

        # Extract timestamp
        timestamp_str = data.get('timestamp', '')
        try:
            if isinstance(timestamp_str, str):
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                timestamp_ms = int(dt.timestamp() * 1000)
            elif isinstance(timestamp_str, (int, float)):
                timestamp_ms = int(timestamp_str)
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                timestamp_str = dt.isoformat()
            else:
                timestamp_ms = 0
                timestamp_str = ''
        except Exception:
            timestamp_ms = 0

        # Extract content based on type
        content = self._extract_content(data, msg_type)

        # Extract parent UUID
        parent_uuid = data.get('parentUuid')

        # Extract session and agent info
        session_id = data.get('sessionId')
        agent_id = data.get('agentId')
        is_sidechain = data.get('isSidechain', False)

        # Extract tool information for tool-related messages
        tool_name = None
        tool_use_id = None

        if msg_type in ('tool_use', 'tool_result'):
            # Tool use might be in message.content
            if 'message' in data and isinstance(data['message'], dict):
                msg_content = data['message'].get('content', [])
                if isinstance(msg_content, list):
                    for item in msg_content:
                        if isinstance(item, dict) and item.get('type') == 'tool_use':
                            tool_name = item.get('name')
                            tool_use_id = item.get('id')
                            break
                        elif isinstance(item, dict) and item.get('type') == 'tool_result':
                            tool_use_id = item.get('tool_use_id')

        # Build metadata
        metadata = {
            'cwd': data.get('cwd'),
            'version': data.get('version'),
            'git_branch': data.get('gitBranch'),
            'user_type': data.get('userType'),
            'model': data.get('message', {}).get('model') if isinstance(data.get('message'), dict) else None,
        }

        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return Message(
            uuid=uuid,
            timestamp=timestamp_str,
            timestamp_ms=timestamp_ms,
            type=msg_type,
            content=content,
            parent_uuid=parent_uuid,
            session_id=session_id,
            agent_id=agent_id,
            is_sidechain=is_sidechain,
            tool_name=tool_name,
            tool_use_id=tool_use_id,
            metadata=metadata,
            raw_data=data
        )

    def _extract_content(self, data: Dict[str, Any], msg_type: str) -> Any:
        """
        Extract content from message data based on type.

        Args:
            data: Message data dictionary.
            msg_type: Message type.

        Returns:
            Any: Extracted content.
        """
        # If there's a 'message' field, extract from there
        if 'message' in data and isinstance(data['message'], dict):
            message = data['message']

            # For assistant messages
            if message.get('role') == 'assistant':
                content = message.get('content', [])
                if isinstance(content, list):
                    # Extract text blocks
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                    return '\n'.join(text_parts) if text_parts else content
                return content

            # For user messages
            elif message.get('role') == 'user':
                content = message.get('content')
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Extract text or tool results
                    parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if item.get('type') == 'text':
                                parts.append(item.get('text', ''))
                            elif item.get('type') == 'tool_result':
                                # Return full tool result structure
                                return item
                    return '\n'.join(parts) if parts else content
                return content

        # For system messages
        if 'content' in data:
            return data['content']

        # For file history snapshots
        if msg_type == 'file-history-snapshot':
            return data.get('snapshot', {})

        # Default: return the whole data structure
        return data


if __name__ == "__main__":
    # Test the parser
    import sys
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "config.py"
    sys.path.insert(0, str(config_path.parent))

    from config import CONVERSATIONS_DIR

    # Find a test project
    projects = list(CONVERSATIONS_DIR.iterdir())
    if projects:
        test_project = projects[0]
        print(f"Testing parser with: {test_project.name}")
        print("=" * 60)

        parser = ConversationParser(test_project)
        messages = parser.parse_all()

        print(f"\nParsed {len(messages)} messages")
        print(f"\nFirst message:")
        if messages:
            msg = messages[0]
            print(f"  UUID: {msg.uuid}")
            print(f"  Type: {msg.type}")
            print(f"  Timestamp: {msg.timestamp}")
            print(f"  Content: {str(msg.content)[:100]}...")
    else:
        print("No projects found for testing")
