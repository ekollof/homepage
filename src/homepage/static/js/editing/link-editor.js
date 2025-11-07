/**
 * Link CRUD operations
 */

import { getConfig, setConfig, getEditContext, setEditContext } from './edit-mode.js';
import { updateCategoryDisplay } from './category-editor.js';
import { closeModal, showConfirmDialog } from './modal-manager.js';
import { fetchAndCacheFavicon } from './favicon-service.js';

/**
 * Get category from DOM element
 * @param {HTMLElement} element - Element within category
 * @returns {object} Category div and index
 */
function getCategoryFromElement(element) {
    const categoryDiv = element.closest('.category');
    const categoryIndex = parseInt(categoryDiv.dataset.categoryIndex);
    return { categoryDiv, categoryIndex };
}

/**
 * Add new link
 * @param {HTMLElement} button - Add button element
 * @param {boolean} isSubcategory - Whether link is in subcategory
 */
export function addLink(button, isSubcategory) {
    if (isSubcategory) {
        const subcategoryDiv = button.closest('.subcategory');
        const { categoryIndex } = getCategoryFromElement(button);
        const subcategoryIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
        setEditContext({ type: 'link', action: 'add', categoryIndex, subcategoryIndex });
    } else {
        const { categoryIndex } = getCategoryFromElement(button);
        setEditContext({ type: 'link', action: 'add', categoryIndex });
    }

    document.getElementById('modalTitle').textContent = 'Add Link';
    document.getElementById('itemName').value = '';
    document.getElementById('itemUrl').value = '';
    document.getElementById('itemIcon').value = '';
    document.getElementById('urlGroup').style.display = 'block';
    document.getElementById('editModal').classList.add('show');
}

/**
 * Edit existing link
 * @param {HTMLElement} button - Edit button element
 * @param {boolean} isSubcategory - Whether link is in subcategory
 * @param {Event} event - Click event
 */
export function editLink(button, isSubcategory, event) {
    event.preventDefault();
    event.stopPropagation();

    const currentConfig = getConfig();
    const linkItem = button.closest('.link-item');
    const linkIndex = parseInt(linkItem.dataset.linkIndex);
    
    if (isSubcategory) {
        const subcategoryDiv = button.closest('.subcategory');
        const { categoryIndex } = getCategoryFromElement(button);
        const subcategoryIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
        const link = currentConfig.category[categoryIndex].subcategory[subcategoryIndex].links[linkIndex];
        
        setEditContext({ type: 'link', action: 'edit', categoryIndex, subcategoryIndex, linkIndex });
        
        document.getElementById('modalTitle').textContent = 'Edit Link';
        document.getElementById('itemName').value = link.name;
        document.getElementById('itemUrl').value = link.url;
        document.getElementById('itemIcon').value = link.icon || '🔗';
    } else {
        const { categoryIndex } = getCategoryFromElement(button);
        const link = currentConfig.category[categoryIndex].links[linkIndex];
        
        setEditContext({ type: 'link', action: 'edit', categoryIndex, linkIndex });
        
        document.getElementById('modalTitle').textContent = 'Edit Link';
        document.getElementById('itemName').value = link.name;
        document.getElementById('itemUrl').value = link.url;
        document.getElementById('itemIcon').value = link.icon || '🔗';
    }

    document.getElementById('urlGroup').style.display = 'block';
    document.getElementById('editModal').classList.add('show');
}

/**
 * Delete link
 * @param {HTMLElement} button - Delete button element
 * @param {boolean} isSubcategory - Whether link is in subcategory
 * @param {Event} event - Click event
 */
export function deleteLink(button, isSubcategory, event) {
    event.preventDefault();
    event.stopPropagation();

    const currentConfig = getConfig();
    const linkItem = button.closest('.link-item');
    const linkIndex = parseInt(linkItem.dataset.linkIndex);

    if (isSubcategory) {
        const subcategoryDiv = button.closest('.subcategory');
        const { categoryIndex } = getCategoryFromElement(button);
        const subcategoryIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
        const link = currentConfig.category[categoryIndex].subcategory[subcategoryIndex].links[linkIndex];

        showConfirmDialog(
            `Delete link "${link.name}"?`,
            () => {
                currentConfig.category[categoryIndex].subcategory[subcategoryIndex].links.splice(linkIndex, 1);
                setConfig(currentConfig);
                updateCategoryDisplay();
            }
        );
    } else {
        const { categoryIndex } = getCategoryFromElement(button);
        const link = currentConfig.category[categoryIndex].links[linkIndex];

        showConfirmDialog(
            `Delete link "${link.name}"?`,
            () => {
                currentConfig.category[categoryIndex].links.splice(linkIndex, 1);
                setConfig(currentConfig);
                updateCategoryDisplay();
            }
        );
    }
}

/**
 * Save link to configuration
 * @param {object} link - Link object
 */
function saveLinkToConfig(link) {
    const currentConfig = getConfig();
    const editContext = getEditContext();
    
    if (editContext.action === 'edit') {
        // Edit existing link
        if (editContext.subcategoryIndex !== undefined) {
            currentConfig.category[editContext.categoryIndex].subcategory[editContext.subcategoryIndex].links[editContext.linkIndex] = link;
        } else {
            currentConfig.category[editContext.categoryIndex].links[editContext.linkIndex] = link;
        }
    } else {
        // Add new link
        if (editContext.subcategoryIndex !== undefined) {
            if (!currentConfig.category[editContext.categoryIndex].subcategory[editContext.subcategoryIndex].links) {
                currentConfig.category[editContext.categoryIndex].subcategory[editContext.subcategoryIndex].links = [];
            }
            currentConfig.category[editContext.categoryIndex].subcategory[editContext.subcategoryIndex].links.push(link);
        } else {
            if (!currentConfig.category[editContext.categoryIndex].links) {
                currentConfig.category[editContext.categoryIndex].links = [];
            }
            currentConfig.category[editContext.categoryIndex].links.push(link);
        }
    }
    
    setConfig(currentConfig);
    closeModal();
    updateCategoryDisplay();
}

/**
 * Handle link form submission
 * @param {Event} e - Form submit event
 */
export function handleLinkFormSubmit(e) {
    e.preventDefault();
    const editContext = getEditContext();

    const name = document.getElementById('itemName').value.trim();
    const url = document.getElementById('itemUrl').value.trim();
    const icon = document.getElementById('itemIcon').value.trim();

    if (!name) {
        alert('Name is required');
        return;
    }

    if (!url) {
        alert('URL is required for links');
        return;
    }

    if (!editContext) return;

    // If icon is empty, fetch favicon and convert to base64
    if (!icon || icon.trim() === '') {
        fetchAndCacheFavicon(url).then(faviconData => {
            const link = { name, url, icon: faviconData };
            saveLinkToConfig(link);
        }).catch(error => {
            console.error('Failed to fetch favicon:', error);
            // Save with empty icon if fetch fails
            const link = { name, url, icon: '' };
            saveLinkToConfig(link);
        });
        return; // Exit early, will continue in promise
    }
    
    const link = { name, url, icon };
    saveLinkToConfig(link);
}

// Expose functions to window for onclick handlers
window.addLink = addLink;
window.editLink = editLink;
window.deleteLink = deleteLink;
