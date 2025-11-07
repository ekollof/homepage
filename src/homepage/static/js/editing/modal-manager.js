/**
 * Modal dialog management
 */

import { getEditContext } from './edit-mode.js';
import { handleCategoryFormSubmit } from './category-editor.js';
import { handleLinkFormSubmit } from './link-editor.js';

/**
 * Close edit modal
 */
export function closeModal() {
    document.getElementById('editModal').classList.remove('show');
}

/**
 * Close confirm modal
 */
export function closeConfirmModal() {
    document.getElementById('confirmModal').classList.remove('show');
}

/**
 * Show confirmation dialog
 * @param {string} message - Message to display
 * @param {Function} onConfirm - Callback on confirmation
 */
export function showConfirmDialog(message, onConfirm) {
    document.getElementById('confirmMessage').textContent = message;
    document.getElementById('confirmButton').onclick = () => {
        onConfirm();
        closeConfirmModal();
    };
    document.getElementById('confirmModal').classList.add('show');
}

/**
 * Initialize modal event handlers
 */
export function initializeModals() {
    // Edit form submission
    const editForm = document.getElementById('editForm');
    if (editForm) {
        editForm.addEventListener('submit', (e) => {
            const editContext = getEditContext();
            
            if (!editContext) {
                e.preventDefault();
                return;
            }
            
            // Route to appropriate handler based on type
            if (editContext.type === 'link') {
                handleLinkFormSubmit(e);
            } else {
                handleCategoryFormSubmit(e);
            }
        });
    }
    
    // Close modals on click outside
    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.addEventListener('click', (e) => {
            if (e.target.id === 'editModal') closeModal();
        });
    }

    const confirmModal = document.getElementById('confirmModal');
    if (confirmModal) {
        confirmModal.addEventListener('click', (e) => {
            if (e.target.id === 'confirmModal') closeConfirmModal();
        });
    }
}

// Expose to window for onclick handlers
window.closeModal = closeModal;
window.closeConfirmModal = closeConfirmModal;
