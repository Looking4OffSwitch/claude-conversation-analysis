#!/usr/bin/env python3
"""
Flask application for viewing Claude Code conversation histories.

This application allows users to view and export conversation histories
from their Claude Code projects.
"""

import sys
import importlib.util
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort

# Get the absolute path to flask_app directory
FLASK_APP_DIR = Path(__file__).parent
PROJECT_ROOT = FLASK_APP_DIR.parent

# Import flask_app config directly to avoid conflict with tools/config.py
config_path = FLASK_APP_DIR / "config.py"
spec = importlib.util.spec_from_file_location("flask_config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# Add tools directory to path for other imports
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from utils import (
    ConversationParser,
    MessageTreeBuilder,
    SessionGrouper,
    CacheManager,
)
from utils.sanitizer import DataSanitizer
from logger import setup_logger


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize logger
logger = setup_logger(__name__)

# Initialize cache manager
cache_manager = CacheManager(
    cache_dir=config.CACHE_DIR,
    ttl_seconds=config.CACHE_TTL_SECONDS
)


def get_available_projects():
    """
    Get list of available projects from conversations directory.

    Returns:
        list: List of project dictionaries with id, name, and path.
    """
    try:
        projects = []

        for project_dir in config.CONVERSATIONS_DIR.iterdir():
            if not project_dir.is_dir():
                continue

            # Skip hidden directories
            if project_dir.name.startswith('.'):
                continue

            # Check if directory contains .jsonl files
            jsonl_files = list(project_dir.glob("*.jsonl"))
            if not jsonl_files:
                continue

            # Extract project name from path encoding
            # Example: -Users-Reed-dev-my-project -> my-project
            path_encoded = project_dir.name
            parts = path_encoded.split('-')

            # Try to find the project name (usually after 'dev')
            try:
                dev_index = parts.index('dev')
                project_name = '-'.join(parts[dev_index + 1:])
            except (ValueError, IndexError):
                project_name = path_encoded

            projects.append({
                'id': path_encoded,
                'name': project_name or path_encoded,
                'path': str(project_dir),
                'file_count': len(jsonl_files)
            })

        # Sort by name
        projects.sort(key=lambda p: p['name'].lower())

        logger.info(f"Found {len(projects)} projects")
        return projects

    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return []


def get_project_path(project_id: str) -> Path:
    """
    Get project directory path from project ID.

    Args:
        project_id: Project identifier (directory name).

    Returns:
        Path: Project directory path.

    Raises:
        FileNotFoundError: If project doesn't exist.
    """
    project_path = config.CONVERSATIONS_DIR / project_id

    if not project_path.exists() or not project_path.is_dir():
        raise FileNotFoundError(f"Project not found: {project_id}")

    return project_path


def parse_conversation(project_id: str, use_cache: bool = True):
    """
    Parse conversation for a project.

    Args:
        project_id: Project identifier.
        use_cache: Whether to use cache.

    Returns:
        tuple: (messages, tree, stats) where messages is the flat list,
               tree is the root messages with children, and stats is metadata.
    """
    logger.info(f"Parsing conversation for project: {project_id}")

    project_path = get_project_path(project_id)

    # Try to load from cache first
    messages = None
    if use_cache and config.CACHE_ENABLED:
        messages = cache_manager.get(project_path)

    # Parse if not in cache
    if messages is None:
        parser = ConversationParser(project_path)
        messages = parser.parse_all()

        # Cache the results
        if config.CACHE_ENABLED:
            cache_manager.set(project_path, messages)

    # Build tree structure
    tree_builder = MessageTreeBuilder(messages)
    tree = tree_builder.build()
    stats = tree_builder.get_statistics()

    # Get session information
    session_grouper = SessionGrouper(messages)
    session_info = session_grouper.get_session_info()

    stats['sessions_info'] = session_info

    logger.info(f"Parsed {len(messages)} messages, {len(tree)} root messages")

    return messages, tree, stats


@app.route('/')
def index():
    """Home page with project selection."""
    try:
        projects = get_available_projects()
        return render_template(
            'index.html',
            projects=projects,
            themes=config.AVAILABLE_THEMES,
            default_theme=config.DEFAULT_THEME
        )
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return f"Error: {e}", 500


@app.route('/conversation/<project_id>')
def view_conversation(project_id: str):
    """View conversation for a specific project."""
    try:
        # Get settings from query params
        theme = request.args.get('theme', config.DEFAULT_THEME)
        sanitize = request.args.get('sanitize', 'false').lower() == 'true'
        refresh_cache = request.args.get('refresh', 'false').lower() == 'true'

        # Validate theme
        if theme not in config.AVAILABLE_THEMES:
            theme = config.DEFAULT_THEME

        # Parse conversation
        use_cache = not refresh_cache
        messages, tree, stats = parse_conversation(project_id, use_cache=use_cache)

        # Get project info
        projects = get_available_projects()
        project = next((p for p in projects if p['id'] == project_id), None)

        if not project:
            abort(404, description="Project not found")

        # Apply sanitization if enabled
        sanitizer = DataSanitizer(enabled=sanitize)

        # Prepare data for template
        template_data = {
            'project': project,
            'messages': messages,
            'tree': tree,
            'stats': stats,
            'theme': theme,
            'sanitize_enabled': sanitize,
            'themes': config.AVAILABLE_THEMES,
            'sanitizer': sanitizer,
            'config': config,
        }

        return render_template('conversation.html', **template_data)

    except FileNotFoundError as e:
        logger.error(f"Project not found: {e}")
        abort(404, description=str(e))
    except Exception as e:
        logger.error(f"Error viewing conversation: {e}")
        return f"Error: {e}", 500


@app.route('/api/projects')
def api_projects():
    """API endpoint to get available projects."""
    try:
        projects = get_available_projects()
        return jsonify({
            'success': True,
            'projects': projects,
            'count': len(projects)
        })
    except Exception as e:
        logger.error(f"Error in API projects: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conversation/<project_id>')
def api_conversation(project_id: str):
    """API endpoint to get conversation data."""
    try:
        refresh_cache = request.args.get('refresh', 'false').lower() == 'true'
        use_cache = not refresh_cache

        messages, tree, stats = parse_conversation(project_id, use_cache=use_cache)

        # Convert messages to dicts for JSON serialization
        messages_data = [msg.to_dict() for msg in messages]

        return jsonify({
            'success': True,
            'project_id': project_id,
            'message_count': len(messages),
            'messages': messages_data,
            'stats': stats
        })

    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error in API conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/export/<project_id>')
def export_conversation(project_id: str):
    """Export conversation as standalone HTML file."""
    try:
        # Get settings from query params
        theme = request.args.get('theme', config.DEFAULT_THEME)
        sanitize = request.args.get('sanitize', str(config.EXPORT_SANITIZE_DEFAULT)).lower() == 'true'

        # Parse conversation
        messages, tree, stats = parse_conversation(project_id)

        # Get project info
        projects = get_available_projects()
        project = next((p for p in projects if p['id'] == project_id), None)

        if not project:
            abort(404, description="Project not found")

        # Apply sanitization
        sanitizer = DataSanitizer(enabled=sanitize)

        # Render export template
        html_content = render_template(
            'export.html',
            project=project,
            messages=messages,
            tree=tree,
            stats=stats,
            theme=theme,
            sanitize_enabled=sanitize,
            sanitizer=sanitizer,
            config=config,
            export_date=datetime.now().isoformat()
        )

        # Save to file
        export_filename = f"{project['name']}_conversation.html"
        export_path = config.EXPORT_DIR / export_filename

        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Exported conversation to: {export_path}")

        # Return the file
        return send_file(
            export_path,
            as_attachment=True,
            download_name=export_filename,
            mimetype='text/html'
        )

    except FileNotFoundError as e:
        logger.error(f"Project not found: {e}")
        abort(404, description=str(e))
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        return f"Error: {e}", 500


@app.route('/cache/clear')
def clear_cache():
    """Clear all cache."""
    try:
        count = cache_manager.clear()
        return jsonify({
            'success': True,
            'message': f'Cleared {count} cache files',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/cache/stats')
def cache_stats():
    """Get cache statistics."""
    try:
        stats = cache_manager.get_cache_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html', error=error), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}")
    return render_template('500.html', error=error), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        config.validate_config()
        logger.info("Configuration valid")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Run the app
    logger.info(f"Starting Flask app on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
