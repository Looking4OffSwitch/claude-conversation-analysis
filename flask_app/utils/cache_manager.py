"""
Cache manager for parsed conversations.

This module handles caching of parsed conversation data for improved performance.
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import hashlib

import sys
sys.path.insert(0, str(Path(__file__).parent))

from conversation_parser import Message
from logger import setup_logger


logger = setup_logger(__name__)


class CacheManager:
    """Manages caching of parsed conversation data."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 3600):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage.
            ttl_seconds: Time-to-live for cache entries in seconds.

        Raises:
            ValueError: If cache_dir is None.
        """
        if not cache_dir:
            raise ValueError("cache_dir cannot be None")

        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Cache manager initialized: {cache_dir} (TTL: {ttl_seconds}s)")

    def get_cache_key(self, project_path: Path) -> str:
        """
        Generate cache key for a project.

        Args:
            project_path: Path to the project.

        Returns:
            str: Cache key.
        """
        # Use project path + modification time of directory
        path_str = str(project_path.resolve())

        # Get the latest modification time of any file in the project
        try:
            files = list(project_path.glob("*.jsonl"))
            if files:
                latest_mtime = max(f.stat().st_mtime for f in files)
                key_str = f"{path_str}_{latest_mtime}"
            else:
                key_str = path_str
        except Exception:
            key_str = path_str

        return hashlib.md5(key_str.encode()).hexdigest()

    def get_cache_path(self, cache_key: str) -> Path:
        """
        Get cache file path for a cache key.

        Args:
            cache_key: Cache key.

        Returns:
            Path: Path to cache file.
        """
        return self.cache_dir / f"{cache_key}.cache"

    def is_cache_valid(self, cache_path: Path) -> bool:
        """
        Check if cache file is still valid (within TTL).

        Args:
            cache_path: Path to cache file.

        Returns:
            bool: True if cache is valid, False otherwise.
        """
        if not cache_path.exists():
            return False

        # Check if cache has expired
        try:
            stat = cache_path.stat()
            age_seconds = (datetime.now().timestamp() - stat.st_mtime)

            if age_seconds > self.ttl_seconds:
                logger.debug(f"Cache expired: {cache_path.name} (age: {age_seconds:.0f}s)")
                return False

            return True

        except Exception as e:
            logger.warning(f"Error checking cache validity: {e}")
            return False

    def get(self, project_path: Path) -> Optional[List[Message]]:
        """
        Get cached messages for a project.

        Args:
            project_path: Path to the project.

        Returns:
            Optional[List[Message]]: Cached messages or None if not cached/expired.
        """
        cache_key = self.get_cache_key(project_path)
        cache_path = self.get_cache_path(cache_key)

        if not self.is_cache_valid(cache_path):
            return None

        try:
            logger.info(f"Loading from cache: {project_path.name}")

            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)

            # Validate cached data
            if not isinstance(cached_data, dict):
                logger.warning("Invalid cache format")
                return None

            messages_data = cached_data.get('messages', [])

            # Reconstruct Message objects from dicts
            messages = []
            for msg_data in messages_data:
                # Reconstruct Message object
                msg = Message(**msg_data)
                messages.append(msg)

            logger.info(f"Loaded {len(messages)} messages from cache")
            return messages

        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
            return None

    def set(self, project_path: Path, messages: List[Message]) -> bool:
        """
        Cache messages for a project.

        Args:
            project_path: Path to the project.
            messages: Messages to cache.

        Returns:
            bool: True if successfully cached, False otherwise.
        """
        cache_key = self.get_cache_key(project_path)
        cache_path = self.get_cache_path(cache_key)

        try:
            logger.info(f"Caching {len(messages)} messages for: {project_path.name}")

            # Convert messages to serializable format
            messages_data = []
            for msg in messages:
                # Convert to dict, excluding children to avoid recursion
                msg_dict = msg.to_dict()
                messages_data.append(msg_dict)

            cache_data = {
                'project_path': str(project_path),
                'cached_at': datetime.now().isoformat(),
                'message_count': len(messages),
                'messages': messages_data
            }

            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.info(f"Successfully cached to: {cache_path.name}")
            return True

        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False

    def clear(self, project_path: Optional[Path] = None) -> int:
        """
        Clear cache for a specific project or all projects.

        Args:
            project_path: Path to project to clear cache for, or None to clear all.

        Returns:
            int: Number of cache files cleared.
        """
        if project_path:
            # Clear specific project cache
            cache_key = self.get_cache_key(project_path)
            cache_path = self.get_cache_path(cache_key)

            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"Cleared cache for: {project_path.name}")
                return 1
            return 0

        else:
            # Clear all caches
            count = 0
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                    count += 1
                except Exception as e:
                    logger.warning(f"Error deleting cache file {cache_file}: {e}")

            logger.info(f"Cleared {count} cache files")
            return count

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dict: Cache statistics.
        """
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)

        stats = {
            'cache_dir': str(self.cache_dir),
            'file_count': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'ttl_seconds': self.ttl_seconds,
        }

        return stats


if __name__ == "__main__":
    # Test cache manager
    from pathlib import Path
    import sys

    config_path = Path(__file__).parent.parent / "config.py"
    sys.path.insert(0, str(config_path.parent))

    from config import CACHE_DIR, CONVERSATIONS_DIR
    from conversation_parser import ConversationParser

    print("Cache Manager Test")
    print("=" * 60)

    manager = CacheManager(CACHE_DIR)

    # Get stats
    stats = manager.get_cache_stats()
    print("\nCache Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test with a project
    projects = list(CONVERSATIONS_DIR.iterdir())
    if projects:
        test_project = projects[0]
        print(f"\nTesting with project: {test_project.name}")

        # Try to get from cache (should be None first time)
        cached = manager.get(test_project)
        if cached:
            print(f"  Found in cache: {len(cached)} messages")
        else:
            print("  Not in cache, parsing...")
            parser = ConversationParser(test_project)
            messages = parser.parse_all()

            # Cache the messages
            success = manager.set(test_project, messages)
            print(f"  Cached: {success} ({len(messages)} messages)")

            # Try to get again
            cached = manager.get(test_project)
            if cached:
                print(f"  Retrieved from cache: {len(cached)} messages")

    print()
