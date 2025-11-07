/**
 * Category and subcategory CRUD operations
 */

import { getConfig, setConfig, getEditContext, setEditContext } from './edit-mode.js';
import { closeModal, showConfirmDialog } from './modal-manager.js';

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
 * Update category display from current config
 */
export function updateCategoryDisplay(config) {
    const currentConfig = config || getConfig();
    
    // Changes are stored in currentConfig and will be saved when exiting edit mode
    // Rebuild the links container from currentConfig
    const container = document.getElementById('linksContainer');
    if (!container || !currentConfig) return;
    
    // Simple approach: regenerate the entire container HTML
    // This ensures the DOM matches currentConfig
    let html = '';
    
    currentConfig.category.forEach((category, catIndex) => {
        html += `<div class="category" data-category-index="${catIndex}" draggable="false">`;
        html += `<span class="category-drag-handle">⋮⋮</span>`;
        html += `<div class="category-title">`;
        html += `<span class="category-icon">${category.icon || '📁'}</span>`;
        html += `<span>${category.name}</span>`;
        html += `</div>`;
        
        // Category links
        if (category.links && category.links.length > 0) {
            html += `<ul class="links-list">`;
            category.links.forEach((link, linkIndex) => {
                let iconHtml;
                if (link.icon) {
                    // Check if it's a base64 data URI
                    if (link.icon.startsWith('data:image/')) {
                        iconHtml = `<img src="${link.icon}" alt="" style="width: 1em; height: 1em; vertical-align: middle;">`;
                    } else {
                        // It's an emoji or text
                        iconHtml = link.icon;
                    }
                } else {
                    // Fallback to Google favicon service
                    iconHtml = `<img src="https://www.google.com/s2/favicons?domain=${encodeURIComponent(link.url)}&sz=32" alt="" style="width: 1em; height: 1em; vertical-align: middle;">`;
                }
                html += `<li class="link-item" data-link-index="${linkIndex}" draggable="false">`;
                html += `<span class="link-drag-handle">⋮⋮</span>`;
                html += `<a href="${link.url}" target="_blank" rel="noopener noreferrer" data-link="${link.name}">`;
                html += `<span class="link-icon">${iconHtml}</span>`;
                html += `<span>${link.name}</span>`;
                html += `</a>`;
                html += `<div class="edit-controls link-controls">`;
                html += `<button class="edit-btn edit-btn-small" onclick="window.editLink(this, false, event)">Edit</button>`;
                html += `<button class="edit-btn edit-btn-small danger" onclick="window.deleteLink(this, false, event)">×</button>`;
                html += `</div>`;
                html += `</li>`;
            });
            html += `</ul>`;
        }
        
        // Subcategories
        if (category.subcategory && category.subcategory.length > 0) {
            category.subcategory.forEach((subcategory, subIndex) => {
                html += `<div class="subcategory" data-subcategory-index="${subIndex}" draggable="false">`;
                html += `<div class="subcategory-title">`;
                html += `<span class="subcategory-drag-handle">⋮⋮</span>`;
                html += `<span class="subcategory-icon">${subcategory.icon || '📂'}</span>`;
                html += `<span>${subcategory.name}</span>`;
                html += `</div>`;
                
                if (subcategory.links && subcategory.links.length > 0) {
                    html += `<ul class="links-list">`;
                    subcategory.links.forEach((link, linkIndex) => {
                        let iconHtml;
                        if (link.icon) {
                            // Check if it's a base64 data URI
                            if (link.icon.startsWith('data:image/')) {
                                iconHtml = `<img src="${link.icon}" alt="" style="width: 1em; height: 1em; vertical-align: middle;">`;
                            } else {
                                // It's an emoji or text
                                iconHtml = link.icon;
                            }
                        } else {
                            // Fallback to Google favicon service
                            iconHtml = `<img src="https://www.google.com/s2/favicons?domain=${encodeURIComponent(link.url)}&sz=32" alt="" style="width: 1em; height: 1em; vertical-align: middle;">`;
                        }
                        html += `<li class="link-item" data-link-index="${linkIndex}" draggable="false">`;
                        html += `<span class="link-drag-handle">⋮⋮</span>`;
                        html += `<a href="${link.url}" target="_blank" rel="noopener noreferrer" data-link="${link.name}">`;
                        html += `<span class="link-icon">${iconHtml}</span>`;
                        html += `<span>${link.name}</span>`;
                        html += `</a>`;
                        html += `<div class="edit-controls link-controls">`;
                        html += `<button class="edit-btn edit-btn-small" onclick="window.editLink(this, true, event)">Edit</button>`;
                        html += `<button class="edit-btn edit-btn-small danger" onclick="window.deleteLink(this, true, event)">×</button>`;
                        html += `</div>`;
                        html += `</li>`;
                    });
                    html += `</ul>`;
                }
                
                html += `<div class="edit-controls">`;
                html += `<button class="edit-btn" onclick="window.editSubcategory(this)">Edit Subcategory</button>`;
                html += `<button class="edit-btn add" onclick="window.addLink(this, true)">+ Link</button>`;
                html += `<button class="edit-btn danger" onclick="window.deleteSubcategory(this)">Delete</button>`;
                html += `</div>`;
                html += `</div>`;
            });
        }
        
        // Category edit controls
        html += `<div class="edit-controls">`;
        html += `<button class="edit-btn" onclick="window.editCategory(this)">Edit Category</button>`;
        html += `<button class="edit-btn add" onclick="window.addLink(this, false)">+ Link</button>`;
        html += `<button class="edit-btn add" onclick="window.addSubcategory(this)">+ Subcategory</button>`;
        html += `<button class="edit-btn danger" onclick="window.deleteCategory(this)">Delete</button>`;
        html += `</div>`;
        html += `</div>`;
    });
    
    // Add category button
    html += `<div class="edit-controls add-category-container">`;
    html += `<button class="edit-btn add" onclick="window.addCategory()" style="font-size: 1rem; padding: 10px 20px;">+ Add Category</button>`;
    html += `</div>`;
    
    container.innerHTML = html;
    
    // Re-apply edit mode class if still in edit mode
    if (window.editMode) {
        container.classList.add('edit-mode');
        // Re-enable dragging for newly created elements
        if (typeof window.enableCategoryDragging === 'function') window.enableCategoryDragging();
        if (typeof window.enableLinkDragging === 'function') window.enableLinkDragging();
        if (typeof window.enableSubcategoryDragging === 'function') window.enableSubcategoryDragging();
    }
    
    console.log('DOM updated from currentConfig');
}

/**
 * Add new category
 */
export function addCategory() {
    const currentConfig = getConfig();
    if (!currentConfig) return;

    setEditContext({ type: 'category', action: 'add' });
    document.getElementById('modalTitle').textContent = 'Add Category';
    document.getElementById('itemName').value = '';
    document.getElementById('itemIcon').value = '📁';
    document.getElementById('urlGroup').style.display = 'none';
    document.getElementById('editModal').classList.add('show');
}

/**
 * Edit existing category
 * @param {HTMLElement} button - Edit button element
 */
export function editCategory(button) {
    const currentConfig = getConfig();
    const { categoryDiv, categoryIndex } = getCategoryFromElement(button);
    const category = currentConfig.category[categoryIndex];

    setEditContext({ type: 'category', action: 'edit', index: categoryIndex });
    document.getElementById('modalTitle').textContent = 'Edit Category';
    document.getElementById('itemName').value = category.name;
    document.getElementById('itemIcon').value = category.icon || '📁';
    document.getElementById('urlGroup').style.display = 'none';
    document.getElementById('editModal').classList.add('show');
}

/**
 * Delete category
 * @param {HTMLElement} button - Delete button element
 */
export function deleteCategory(button) {
    const currentConfig = getConfig();
    const { categoryIndex } = getCategoryFromElement(button);
    const category = currentConfig.category[categoryIndex];

    showConfirmDialog(
        `Delete category "${category.name}" and all its contents?`,
        () => {
            currentConfig.category.splice(categoryIndex, 1);
            setConfig(currentConfig);
            updateCategoryDisplay();
        }
    );
}

/**
 * Add new subcategory
 * @param {HTMLElement} button - Add button element
 */
export function addSubcategory(button) {
    const { categoryIndex } = getCategoryFromElement(button);

    setEditContext({ type: 'subcategory', action: 'add', categoryIndex });
    document.getElementById('modalTitle').textContent = 'Add Subcategory';
    document.getElementById('itemName').value = '';
    document.getElementById('itemIcon').value = '📂';
    document.getElementById('urlGroup').style.display = 'none';
    document.getElementById('editModal').classList.add('show');
}

/**
 * Edit existing subcategory
 * @param {HTMLElement} button - Edit button element
 */
export function editSubcategory(button) {
    const currentConfig = getConfig();
    const subcategoryDiv = button.closest('.subcategory');
    const { categoryIndex } = getCategoryFromElement(button);
    const subcategoryIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
    const subcategory = currentConfig.category[categoryIndex].subcategory[subcategoryIndex];

    setEditContext({ type: 'subcategory', action: 'edit', categoryIndex, subcategoryIndex });
    document.getElementById('modalTitle').textContent = 'Edit Subcategory';
    document.getElementById('itemName').value = subcategory.name;
    document.getElementById('itemIcon').value = subcategory.icon || '📂';
    document.getElementById('urlGroup').style.display = 'none';
    document.getElementById('editModal').classList.add('show');
}

/**
 * Delete subcategory
 * @param {HTMLElement} button - Delete button element
 */
export function deleteSubcategory(button) {
    const currentConfig = getConfig();
    const subcategoryDiv = button.closest('.subcategory');
    const { categoryIndex } = getCategoryFromElement(button);
    const subcategoryIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
    const subcategory = currentConfig.category[categoryIndex].subcategory[subcategoryIndex];

    showConfirmDialog(
        `Delete subcategory "${subcategory.name}" and all its links?`,
        () => {
            currentConfig.category[categoryIndex].subcategory.splice(subcategoryIndex, 1);
            setConfig(currentConfig);
            updateCategoryDisplay();
        }
    );
}

/**
 * Handle edit form submission
 * @param {Event} e - Form submit event
 */
export function handleCategoryFormSubmit(e) {
    e.preventDefault();
    const currentConfig = getConfig();
    const editContext = getEditContext();

    const name = document.getElementById('itemName').value.trim();
    const icon = document.getElementById('itemIcon').value.trim();

    if (!name) {
        alert('Name is required');
        return;
    }

    if (!editContext || !currentConfig) return;

    switch (editContext.type) {
        case 'category':
            if (editContext.action === 'add') {
                currentConfig.category.push({
                    name,
                    icon: icon || '📁',
                    links: [],
                    subcategory: []
                });
            } else {
                currentConfig.category[editContext.index].name = name;
                currentConfig.category[editContext.index].icon = icon || '📁';
            }
            break;

        case 'subcategory':
            if (editContext.action === 'add') {
                if (!currentConfig.category[editContext.categoryIndex].subcategory) {
                    currentConfig.category[editContext.categoryIndex].subcategory = [];
                }
                currentConfig.category[editContext.categoryIndex].subcategory.push({
                    name,
                    icon: icon || '📂',
                    links: []
                });
            } else {
                const subcat = currentConfig.category[editContext.categoryIndex].subcategory[editContext.subcategoryIndex];
                subcat.name = name;
                subcat.icon = icon || '📂';
            }
            break;
    }

    setConfig(currentConfig);
    closeModal();
    updateCategoryDisplay();
}

// Expose functions to window for onclick handlers
window.addCategory = addCategory;
window.editCategory = editCategory;
window.deleteCategory = deleteCategory;
window.addSubcategory = addSubcategory;
window.editSubcategory = editSubcategory;
window.deleteSubcategory = deleteSubcategory;
