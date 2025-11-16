# Flask Conversation Viewer - Remaining Tasks

## Phase 1: Core HTML Templates

### Base Template & Layout
- [x] Create `templates/base.html` - Base layout with navigation, theme selector, sanitization toggle
- [x] Add responsive meta tags and basic structure
- [x] Include theme CSS loader (dynamic based on selected theme)
- [x] Add navigation bar with project info and controls

### Project Selection Page
- [x] Create `templates/index.html` - Project selection interface
- [x] Add dropdown/list of available projects with file counts
- [x] Include theme selection dropdown
- [x] Add sanitization toggle checkbox
- [x] Display cache statistics
- [x] Add cache clear button

### Main Conversation Viewer
- [x] Create `templates/conversation.html` - Main conversation display
- [x] Implement message rendering with Jinja2 macros for recursion
- [x] Add collapsible sections for:
  - Agent conversations (nested under parent)
  - Tool invocations
  - Tool results (collapsed by default)
  - System messages
  - File history snapshots
- [x] Display message metadata (timestamp, type, session ID, agent ID)
- [x] Add "copy" buttons for code blocks
- [x] Implement syntax highlighting for code (using Prism.js or highlight.js)
- [x] Add "expand/collapse all" buttons
- [x] Display conversation statistics sidebar/header

### Export Template
- [x] Create `templates/export.html` - Standalone HTML export
- [x] Inline all CSS and JavaScript (no external dependencies)
- [x] Include export metadata (date, sanitization status)
- [x] Make fully self-contained for easy sharing

### Error Templates
- [x] Create `templates/404.html` - Not found error page
- [x] Create `templates/500.html` - Server error page

## Phase 2: Theme System CSS

### ChatGPT Theme (Default)
- [x] Create `static/themes/chatgpt.css`
- [x] Speech bubble style messages
- [x] User messages aligned right with distinct color
- [x] Assistant messages aligned left
- [x] Smooth rounded corners
- [x] Clean, modern typography
- [x] Collapsible sections with smooth animations

### GitHub Theme
- [ ] Create `static/themes/github.css`
- [ ] Linear discussion style
- [ ] Compact message display
- [ ] Code-style monospace for technical content
- [ ] GitHub-like color scheme
- [ ] Subtle borders and spacing

### Slack Theme
- [ ] Create `static/themes/slack.css`
- [ ] Dense timeline style
- [ ] Minimal spacing for maximum content density
- [ ] Message type badges/icons
- [ ] Slack-inspired colors
- [ ] Compact nested threads

### Minimal Theme
- [ ] Create `static/themes/minimal.css`
- [ ] Clean documentation style
- [ ] Maximum readability
- [ ] Minimal decoration
- [ ] Print-friendly styles
- [ ] High contrast for accessibility

### Base Styles
- [x] Create `static/css/base.css` - Common styles across all themes
- [x] Reset/normalize CSS
- [x] Layout grid system
- [x] Utility classes (spacing, colors, typography)
- [x] Print styles
- [x] Responsive breakpoints

## Phase 3: JavaScript Interactivity

### Core Interactions
- [x] Create `static/js/interactions.js`
- [x] Implement collapse/expand functionality for nested messages
- [x] Add "expand all" / "collapse all" buttons
- [x] Add copy-to-clipboard for code blocks
- [x] Implement smooth scroll animations
- [x] Add keyboard shortcuts (e/c for expand/collapse, arrow keys to navigate)
- [x] Save user preferences (theme, collapsed states) to localStorage

### Message Navigation
- [ ] Add jump-to-timestamp functionality
- [ ] Implement search/filter within conversation
- [ ] Add session navigation (if multiple sessions)
- [ ] Highlight search results
- [ ] Add "back to top" button for long conversations

### Export Utilities
- [ ] Create `static/js/export-utils.js`
- [ ] Preview before export
- [ ] Progress indicator for large exports
- [ ] Export options modal (theme, sanitization)

## Phase 4: Message Type Renderers

### Message Components (Jinja2 Macros)
- [ ] Create macro for user messages
- [ ] Create macro for assistant messages
- [ ] Create macro for tool invocations:
  - Read file displays
  - Write file displays
  - Edit file displays (with diff highlighting)
  - Bash command displays with output
  - Glob/Grep search results
  - Task/Agent launches
  - Web operations
- [ ] Create macro for tool results (collapsible, line-limited)
- [ ] Create macro for system messages (subtle, optional visibility)
- [ ] Create macro for file history snapshots
- [ ] Create macro for conversation metadata badges

### Syntax Highlighting
- [ ] Integrate Prism.js or highlight.js
- [ ] Support for Python, JavaScript, JSON, Bash, etc.
- [ ] Language detection from file extensions
- [ ] Line numbers for code blocks
- [ ] Copy button for each code block

## Phase 5: Advanced Features

### Performance Optimizations
- [ ] Implement lazy loading for very long conversations (1000+ messages)
- [ ] Virtual scrolling for large message lists
- [ ] Progressive rendering (render visible messages first)
- [ ] Optimize cache serialization

### Enhanced Export
- [ ] Add PDF export option (using headless browser or library)
- [ ] Add Markdown export
- [ ] Add JSON export (raw data)
- [ ] Batch export (multiple projects at once)

### Analytics & Insights
- [ ] Add conversation statistics dashboard:
  - Total messages
  - Message type breakdown
  - Tool usage statistics
  - Time spent per session
  - Lines of code written
  - Files modified count
- [ ] Visualize conversation timeline
- [ ] Show project evolution over time

### Search & Filter
- [ ] Full-text search within conversation
- [ ] Filter by message type
- [ ] Filter by session
- [ ] Filter by agent
- [ ] Filter by date range
- [ ] Regex search support

## Phase 6: Testing & Documentation

### Testing
- [ ] Test with empty project (no messages)
- [ ] Test with single-file conversation
- [ ] Test with multi-session project
- [ ] Test with large conversation (1000+ messages)
- [ ] Test with deeply nested agent conversations
- [ ] Test all themes render correctly
- [ ] Test export functionality
- [ ] Test sanitization toggle
- [ ] Test cache performance
- [ ] Test error handling (missing files, corrupt data)

### Documentation
- [ ] Create README.md for Flask app
- [ ] Document installation steps
- [ ] Document usage instructions
- [ ] Document theme customization
- [ ] Add screenshots of each theme
- [ ] Document export process
- [ ] Add troubleshooting section

### User Experience
- [ ] Add loading indicators for slow operations
- [ ] Add tooltips for controls
- [ ] Add help/tutorial modal
- [ ] Ensure mobile responsiveness
- [ ] Test accessibility (screen readers, keyboard navigation)
- [ ] Add print stylesheet

## Phase 7: Deployment & Sharing

### Production Readiness
- [ ] Add requirements.txt for Flask dependencies
- [ ] Create setup.py or pyproject.toml
- [ ] Add environment variable configuration
- [ ] Document security considerations
- [ ] Add CSRF protection for forms
- [ ] Rate limiting for API endpoints

### Docker Support (Optional)
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Document Docker deployment

### Static Site Generation (Optional)
- [ ] Add command to generate static site (all conversations as HTML)
- [ ] Create index page for static site
- [ ] Add GitHub Pages deployment option

## Priority Order

**Immediate (Phase 1-3)**: Get basic viewer working
1. Base template with navigation
2. Index page with project selection
3. Conversation viewer with ChatGPT theme
4. Basic JavaScript for collapsible sections
5. Export functionality

**Short-term (Phase 4)**: Polish core features
6. All message type renderers
7. Additional themes
8. Enhanced interactions

**Medium-term (Phase 5-6)**: Advanced features
9. Search and filter
10. Analytics dashboard
11. Testing and documentation

**Long-term (Phase 7)**: Production deployment
12. Docker support
13. Static site generation
14. Public sharing features

---

## Current Status

**Completed**: ✅
- All backend infrastructure (config, parser, cache, routes)
- All Phase 1 HTML templates (base, index, conversation, export, error pages)
- Base CSS with comprehensive utilities and responsive design
- ChatGPT theme CSS (default, speech bubble style)
- Core JavaScript interactions (collapse/expand, copy, keyboard shortcuts, localStorage)

**In Progress**: 🔄 Additional theme development

**Next**: Additional themes (GitHub, Slack, Minimal), enhanced features (search, analytics)
