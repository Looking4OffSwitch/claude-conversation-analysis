/**
 * Interactions.js - Core interactivity for Claude Conversation Viewer
 * Handles collapse/expand, copy-to-clipboard, keyboard shortcuts, and preferences
 */

(function() {
    'use strict';

    // ===== CONFIGURATION =====
    const CONFIG = {
        STORAGE_KEY: 'claude_viewer_prefs',
        SCROLL_BEHAVIOR: 'smooth',
        COPY_SUCCESS_DURATION: 2000,
        ANIMATION_DURATION: 300,
    };

    // ===== STATE MANAGEMENT =====
    let preferences = {
        theme: 'chatgpt',
        collapsedMessages: new Set(),
        autoCollapseToolResults: true,
    };

    // ===== INITIALIZATION =====
    function init() {
        loadPreferences();
        setupCollapsibleSections();
        setupCopyButtons();
        setupKeyboardShortcuts();
        setupExpandCollapseAll();
        setupScrollToTop();
        applyInitialState();
        console.log('Claude Conversation Viewer initialized');
    }

    // ===== PREFERENCES (localStorage) =====
    function loadPreferences() {
        try {
            const stored = localStorage.getItem(CONFIG.STORAGE_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                preferences = {
                    ...preferences,
                    ...parsed,
                    collapsedMessages: new Set(parsed.collapsedMessages || []),
                };
            }
        } catch (error) {
            console.warn('Failed to load preferences:', error);
        }
    }

    function savePreferences() {
        try {
            const toSave = {
                ...preferences,
                collapsedMessages: Array.from(preferences.collapsedMessages),
            };
            localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(toSave));
        } catch (error) {
            console.warn('Failed to save preferences:', error);
        }
    }

    // ===== COLLAPSE/EXPAND FUNCTIONALITY =====
    function setupCollapsibleSections() {
        document.addEventListener('click', function(e) {
            const toggleBtn = e.target.closest('.collapse-toggle');
            if (toggleBtn) {
                e.preventDefault();
                toggleCollapse(toggleBtn);
            }
        });
    }

    function toggleCollapse(button) {
        const message = button.closest('.message');
        if (!message) return;

        const uuid = message.dataset.uuid;
        const isCollapsed = message.classList.contains('collapsed');

        if (isCollapsed) {
            expandMessage(message, uuid);
        } else {
            collapseMessage(message, uuid);
        }

        savePreferences();
    }

    function collapseMessage(message, uuid) {
        message.classList.add('collapsed');
        if (uuid) {
            preferences.collapsedMessages.add(uuid);
        }

        // Smooth height animation
        const children = message.querySelector('.message-children');
        if (children) {
            children.style.transition = `opacity ${CONFIG.ANIMATION_DURATION}ms ease`;
            children.style.opacity = '0';
        }
    }

    function expandMessage(message, uuid) {
        message.classList.remove('collapsed');
        if (uuid) {
            preferences.collapsedMessages.delete(uuid);
        }

        // Smooth height animation
        const children = message.querySelector('.message-children');
        if (children) {
            children.style.transition = `opacity ${CONFIG.ANIMATION_DURATION}ms ease`;
            children.style.opacity = '1';
        }
    }

    function applyInitialState() {
        // Auto-collapse tool results by default
        if (preferences.autoCollapseToolResults) {
            document.querySelectorAll('.message-tool_result').forEach(msg => {
                const uuid = msg.dataset.uuid;
                if (!preferences.collapsedMessages.has(uuid)) {
                    msg.classList.add('collapsed');
                }
            });
        }

        // Restore collapsed state from preferences
        preferences.collapsedMessages.forEach(uuid => {
            const message = document.querySelector(`.message[data-uuid="${uuid}"]`);
            if (message && !message.classList.contains('collapsed')) {
                message.classList.add('collapsed');
            }
        });
    }

    // ===== EXPAND/COLLAPSE ALL =====
    function setupExpandCollapseAll() {
        // Create controls if they don't exist
        const timeline = document.querySelector('.conversation-timeline');
        if (!timeline) return;

        // Find existing controls or create new ones
        let controls = document.querySelector('.conversation-controls');
        if (!controls) {
            controls = document.createElement('div');
            controls.className = 'conversation-controls';
            timeline.parentElement.insertBefore(controls, timeline);
        }

        // Add expand/collapse all buttons if they don't exist
        if (!controls.querySelector('.expand-all-btn')) {
            const expandBtn = document.createElement('button');
            expandBtn.className = 'control-btn expand-all-btn';
            expandBtn.innerHTML = '⬇ Expand All';
            expandBtn.onclick = expandAll;
            controls.appendChild(expandBtn);
        }

        if (!controls.querySelector('.collapse-all-btn')) {
            const collapseBtn = document.createElement('button');
            collapseBtn.className = 'control-btn secondary collapse-all-btn';
            collapseBtn.innerHTML = '⬆ Collapse All';
            collapseBtn.onclick = collapseAll;
            controls.appendChild(collapseBtn);
        }
    }

    function expandAll() {
        document.querySelectorAll('.message.collapsed').forEach(msg => {
            const uuid = msg.dataset.uuid;
            expandMessage(msg, uuid);
        });

        // Also expand all <details> elements
        document.querySelectorAll('details').forEach(details => {
            details.open = true;
        });

        preferences.collapsedMessages.clear();
        savePreferences();
    }

    function collapseAll() {
        document.querySelectorAll('.message').forEach(msg => {
            const hasChildren = msg.querySelector('.message-children');
            const isCollapsible = msg.classList.contains('message-tool_use') ||
                                  msg.classList.contains('message-tool_result') ||
                                  hasChildren;

            if (isCollapsible) {
                const uuid = msg.dataset.uuid;
                collapseMessage(msg, uuid);
            }
        });

        // Also collapse all <details> elements
        document.querySelectorAll('details').forEach(details => {
            details.open = false;
        });

        savePreferences();
    }

    // ===== COPY TO CLIPBOARD =====
    function setupCopyButtons() {
        // Add copy buttons to all code blocks
        document.querySelectorAll('pre[class*="language-"]').forEach(pre => {
            if (!pre.querySelector('.copy-code-btn')) {
                const button = document.createElement('button');
                button.className = 'copy-code-btn';
                button.textContent = 'Copy';
                button.onclick = function() {
                    copyCode(this);
                };
                pre.style.position = 'relative';
                pre.appendChild(button);
            }
        });
    }

    function copyCode(button) {
        const pre = button.closest('pre');
        const code = pre.querySelector('code');
        const text = code.textContent;

        navigator.clipboard.writeText(text).then(() => {
            showCopySuccess(button);
        }).catch(err => {
            console.error('Failed to copy:', err);
            showCopyFailure(button);
        });
    }

    function showCopySuccess(button) {
        const originalText = button.textContent;
        button.textContent = '✓ Copied!';
        button.style.background = 'rgba(16, 163, 127, 0.3)';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, CONFIG.COPY_SUCCESS_DURATION);
    }

    function showCopyFailure(button) {
        const originalText = button.textContent;
        button.textContent = '✗ Failed';
        button.style.background = 'rgba(239, 68, 68, 0.3)';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, CONFIG.COPY_SUCCESS_DURATION);
    }

    // ===== KEYBOARD SHORTCUTS =====
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', handleKeyPress);
    }

    function handleKeyPress(e) {
        // Ignore if user is typing in an input field
        if (e.target.matches('input, textarea, select')) {
            return;
        }

        // 'e' or 'E' - Expand all
        if (e.key === 'e' || e.key === 'E') {
            if (!e.ctrlKey && !e.metaKey && !e.altKey) {
                e.preventDefault();
                expandAll();
            }
        }

        // 'c' or 'C' - Collapse all
        if (e.key === 'c' || e.key === 'C') {
            if (!e.ctrlKey && !e.metaKey && !e.altKey) {
                e.preventDefault();
                collapseAll();
            }
        }

        // 't' or 'T' - Back to top
        if (e.key === 't' || e.key === 'T') {
            if (!e.ctrlKey && !e.metaKey && !e.altKey) {
                e.preventDefault();
                scrollToTop();
            }
        }

        // 'b' or 'B' - Back to bottom
        if (e.key === 'b' || e.key === 'B') {
            if (!e.ctrlKey && !e.metaKey && !e.altKey) {
                e.preventDefault();
                scrollToBottom();
            }
        }

        // '?' - Show keyboard shortcuts help
        if (e.key === '?') {
            e.preventDefault();
            showKeyboardHelp();
        }

        // Arrow keys for navigation
        if (e.key === 'ArrowDown' && e.altKey) {
            e.preventDefault();
            navigateToNextMessage();
        }

        if (e.key === 'ArrowUp' && e.altKey) {
            e.preventDefault();
            navigateToPreviousMessage();
        }
    }

    // ===== NAVIGATION =====
    function navigateToNextMessage() {
        const messages = Array.from(document.querySelectorAll('.message.depth-0'));
        const current = findCurrentMessage(messages);
        if (current !== null && current < messages.length - 1) {
            scrollToMessage(messages[current + 1]);
        } else if (messages.length > 0) {
            scrollToMessage(messages[0]);
        }
    }

    function navigateToPreviousMessage() {
        const messages = Array.from(document.querySelectorAll('.message.depth-0'));
        const current = findCurrentMessage(messages);
        if (current !== null && current > 0) {
            scrollToMessage(messages[current - 1]);
        } else if (messages.length > 0) {
            scrollToMessage(messages[messages.length - 1]);
        }
    }

    function findCurrentMessage(messages) {
        const scrollPos = window.scrollY + window.innerHeight / 3;
        for (let i = 0; i < messages.length; i++) {
            const rect = messages[i].getBoundingClientRect();
            const absoluteTop = rect.top + window.scrollY;
            if (absoluteTop > scrollPos) {
                return Math.max(0, i - 1);
            }
        }
        return messages.length - 1;
    }

    function scrollToMessage(message) {
        if (!message) return;
        message.scrollIntoView({
            behavior: CONFIG.SCROLL_BEHAVIOR,
            block: 'center',
        });
        // Highlight briefly
        message.style.transition = 'background-color 0.3s ease';
        const originalBg = message.style.backgroundColor;
        message.style.backgroundColor = 'rgba(16, 163, 127, 0.1)';
        setTimeout(() => {
            message.style.backgroundColor = originalBg;
        }, 1000);
    }

    // ===== SCROLL TO TOP/BOTTOM =====
    function setupScrollToTop() {
        // Create back-to-top button
        const backToTop = document.createElement('button');
        backToTop.className = 'back-to-top-btn';
        backToTop.innerHTML = '↑';
        backToTop.title = 'Back to top (T)';
        backToTop.onclick = scrollToTop;
        document.body.appendChild(backToTop);

        // Show/hide based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
    }

    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: CONFIG.SCROLL_BEHAVIOR,
        });
    }

    function scrollToBottom() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: CONFIG.SCROLL_BEHAVIOR,
        });
    }

    // ===== KEYBOARD SHORTCUTS HELP MODAL =====
    function showKeyboardHelp() {
        // Check if modal already exists
        let modal = document.getElementById('keyboard-help-modal');
        if (modal) {
            modal.style.display = 'flex';
            return;
        }

        // Create modal
        modal = document.createElement('div');
        modal.id = 'keyboard-help-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Keyboard Shortcuts</h2>
                    <button class="modal-close" onclick="this.closest('.modal').style.display='none'">&times;</button>
                </div>
                <div class="modal-body">
                    <table class="shortcuts-table">
                        <tr>
                            <td><kbd>E</kbd></td>
                            <td>Expand all messages</td>
                        </tr>
                        <tr>
                            <td><kbd>C</kbd></td>
                            <td>Collapse all messages</td>
                        </tr>
                        <tr>
                            <td><kbd>T</kbd></td>
                            <td>Scroll to top</td>
                        </tr>
                        <tr>
                            <td><kbd>B</kbd></td>
                            <td>Scroll to bottom</td>
                        </tr>
                        <tr>
                            <td><kbd>Alt</kbd> + <kbd>↓</kbd></td>
                            <td>Navigate to next message</td>
                        </tr>
                        <tr>
                            <td><kbd>Alt</kbd> + <kbd>↑</kbd></td>
                            <td>Navigate to previous message</td>
                        </tr>
                        <tr>
                            <td><kbd>?</kbd></td>
                            <td>Show this help</td>
                        </tr>
                    </table>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'flex';

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                modal.style.display = 'none';
            }
        });

        // Add modal styles if not already present
        if (!document.getElementById('modal-styles')) {
            const style = document.createElement('style');
            style.id = 'modal-styles';
            style.textContent = `
                .modal {
                    display: none;
                    position: fixed;
                    z-index: 10000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    align-items: center;
                    justify-content: center;
                }
                .modal-content {
                    background: white;
                    border-radius: 12px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                }
                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1.5rem;
                    border-bottom: 1px solid #e5e7eb;
                }
                .modal-header h2 {
                    margin: 0;
                    font-size: 1.5rem;
                    color: #1f2937;
                }
                .modal-close {
                    background: none;
                    border: none;
                    font-size: 2rem;
                    color: #6b7280;
                    cursor: pointer;
                    line-height: 1;
                    padding: 0;
                    width: 32px;
                    height: 32px;
                }
                .modal-close:hover {
                    color: #1f2937;
                }
                .modal-body {
                    padding: 1.5rem;
                }
                .shortcuts-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .shortcuts-table tr {
                    border-bottom: 1px solid #f0f0f0;
                }
                .shortcuts-table tr:last-child {
                    border-bottom: none;
                }
                .shortcuts-table td {
                    padding: 0.75rem 0;
                }
                .shortcuts-table td:first-child {
                    font-weight: 500;
                    color: #10a37f;
                }
                kbd {
                    background: #f3f4f6;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 0.2rem 0.5rem;
                    font-family: monospace;
                    font-size: 0.9rem;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                }
                .back-to-top-btn {
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    background: #10a37f;
                    color: white;
                    border: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    opacity: 0;
                    visibility: hidden;
                    transition: all 0.3s ease;
                    z-index: 1000;
                }
                .back-to-top-btn.visible {
                    opacity: 1;
                    visibility: visible;
                }
                .back-to-top-btn:hover {
                    background: #0d8f6f;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
                }
            `;
            document.head.appendChild(style);
        }
    }

    // ===== SHOW MORE/LESS FOR LONG CONTENT =====
    function toggleShowMore(button) {
        const content = button.previousElementSibling;
        if (!content) return;

        content.classList.toggle('expanded');
        button.textContent = content.classList.contains('expanded') ? 'Show Less' : 'Show All';
    }

    // ===== EXPORT UTILITY =====
    window.toggleShowMore = toggleShowMore;
    window.expandAll = expandAll;
    window.collapseAll = collapseAll;

    // ===== AUTO-INITIALIZE ON DOM READY =====
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
