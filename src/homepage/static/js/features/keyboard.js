/**
 * Keyboard shortcuts handler
 */

import { ENABLE_EDITING } from '../core/constants.js.j2';

/**
 * Initialize keyboard shortcuts
 */
export function initializeKeyboardShortcuts() {
    const searchInput = document.getElementById('searchInput');
    const helpOverlay = document.getElementById('helpOverlay');
    
    document.addEventListener('keydown', (e) => {
        // Ignore if typing in input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
            if (e.key === 'Escape') {
                searchInput.value = '';
                searchInput.blur();
            }
            return;
        }

        switch(e.key) {
            case '/':
                e.preventDefault();
                searchInput.focus();
                break;
            case '?':
                e.preventDefault();
                helpOverlay.classList.toggle('show');
                break;
            case 'Escape':
                helpOverlay.classList.remove('show');
                break;
        }

        // Ctrl+Number for search provider selection
        if (e.ctrlKey && e.key >= '1' && e.key <= '4') {
            e.preventDefault();
            const provider = document.getElementById('searchProvider');
            provider.selectedIndex = parseInt(e.key) - 1;
        }

        // Ctrl+Arrow keys for widget reordering in edit mode (if editing enabled)
        if (ENABLE_EDITING && window.editMode && e.ctrlKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
            e.preventDefault();
            if (e.key === 'ArrowUp' && typeof window.moveWidgetUp === 'function') {
                window.moveWidgetUp();
            } else if (e.key === 'ArrowDown' && typeof window.moveWidgetDown === 'function') {
                window.moveWidgetDown();
            }
        }
    });

    // Click outside help to close
    if (helpOverlay) {
        helpOverlay.addEventListener('click', (e) => {
            if (e.target.id === 'helpOverlay') {
                e.target.classList.remove('show');
            }
        });
    }
}
