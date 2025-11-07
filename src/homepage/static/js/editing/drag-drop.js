/**
 * Drag and drop functionality for categories, subcategories, links, and widgets
 */

import { getConfig, setConfig } from './edit-mode.js';

// Drag state
let draggedCategory = null;
let draggedLink = null;
let draggedSubcategory = null;
let draggedWidget = null;
let widgetOrder = [];

/**
 * Enable category dragging
 */
export function enableCategoryDragging() {
    const container = document.getElementById('linksContainer');
    if (!container) return;

    const categories = container.querySelectorAll('.category');
    
    categories.forEach(category => {
        category.draggable = true;
        
        category.addEventListener('dragstart', handleCategoryDragStart);
        category.addEventListener('dragover', handleCategoryDragOver);
        category.addEventListener('drop', handleCategoryDrop);
        category.addEventListener('dragend', handleCategoryDragEnd);
        category.addEventListener('dragenter', handleCategoryDragEnter);
        category.addEventListener('dragleave', handleCategoryDragLeave);
    });
}

/**
 * Disable category dragging
 */
export function disableCategoryDragging() {
    const container = document.getElementById('linksContainer');
    if (!container) return;

    const categories = container.querySelectorAll('.category');
    categories.forEach(category => {
        category.draggable = false;
        category.removeEventListener('dragstart', handleCategoryDragStart);
        category.removeEventListener('dragover', handleCategoryDragOver);
        category.removeEventListener('drop', handleCategoryDrop);
        category.removeEventListener('dragend', handleCategoryDragEnd);
        category.removeEventListener('dragenter', handleCategoryDragEnter);
        category.removeEventListener('dragleave', handleCategoryDragLeave);
    });
}

function handleCategoryDragStart(e) {
    draggedCategory = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleCategoryDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleCategoryDragEnter(e) {
    if (this !== draggedCategory && this.classList.contains('category')) {
        this.classList.add('drag-over');
    }
}

function handleCategoryDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleCategoryDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedCategory !== this && this.classList.contains('category')) {
        const container = document.getElementById('linksContainer');
        const categories = Array.from(container.querySelectorAll('.category'));
        const draggedIndex = categories.indexOf(draggedCategory);
        const targetIndex = categories.indexOf(this);
        
        if (draggedIndex < targetIndex) {
            this.parentNode.insertBefore(draggedCategory, this.nextSibling);
        } else {
            this.parentNode.insertBefore(draggedCategory, this);
        }
        
        // Update config with new category order
        updateCategoryOrder();
    }
    
    return false;
}

function handleCategoryDragEnd(e) {
    this.classList.remove('dragging');
    
    const categories = document.querySelectorAll('.category');
    categories.forEach(category => {
        category.classList.remove('drag-over');
    });
}

function updateCategoryOrder() {
    const currentConfig = getConfig();
    if (!currentConfig) return;
    
    const container = document.getElementById('linksContainer');
    const categories = container.querySelectorAll('.category');
    
    // Reorder the config based on DOM order
    const newOrder = [];
    categories.forEach(categoryEl => {
        const index = parseInt(categoryEl.dataset.categoryIndex);
        if (!isNaN(index) && currentConfig.category[index]) {
            newOrder.push(currentConfig.category[index]);
        }
    });
    
    currentConfig.category = newOrder;
    setConfig(currentConfig);
    
    // Update the data-category-index attributes to match new order
    categories.forEach((categoryEl, newIndex) => {
        categoryEl.dataset.categoryIndex = newIndex;
    });
    
    console.log('Category order updated');
}

/**
 * Enable link dragging
 */
export function enableLinkDragging() {
    const container = document.getElementById('linksContainer');
    if (!container) return;

    const links = container.querySelectorAll('.link-item');
    
    links.forEach(link => {
        link.draggable = true;
        
        link.addEventListener('dragstart', handleLinkDragStart);
        link.addEventListener('dragover', handleLinkDragOver);
        link.addEventListener('drop', handleLinkDrop);
        link.addEventListener('dragend', handleLinkDragEnd);
        link.addEventListener('dragenter', handleLinkDragEnter);
        link.addEventListener('dragleave', handleLinkDragLeave);
    });
}

/**
 * Disable link dragging
 */
export function disableLinkDragging() {
    const container = document.getElementById('linksContainer');
    if (!container) return;

    const links = container.querySelectorAll('.link-item');
    links.forEach(link => {
        link.draggable = false;
        link.removeEventListener('dragstart', handleLinkDragStart);
        link.removeEventListener('dragover', handleLinkDragOver);
        link.removeEventListener('drop', handleLinkDrop);
        link.removeEventListener('dragend', handleLinkDragEnd);
        link.removeEventListener('dragenter', handleLinkDragEnter);
        link.removeEventListener('dragleave', handleLinkDragLeave);
    });
}

function handleLinkDragStart(e) {
    draggedLink = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.stopPropagation();
}

function handleLinkDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    e.stopPropagation();
    return false;
}

function handleLinkDragEnter(e) {
    if (this !== draggedLink && this.classList.contains('link-item')) {
        this.classList.add('drag-over');
    }
    e.stopPropagation();
}

function handleLinkDragLeave(e) {
    this.classList.remove('drag-over');
    e.stopPropagation();
}

function handleLinkDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedLink !== this && this.classList.contains('link-item')) {
        // Check if both links are in the same parent (same category or subcategory)
        const draggedParent = draggedLink.closest('.links-list');
        const targetParent = this.closest('.links-list');
        
        if (draggedParent === targetParent) {
            const links = Array.from(draggedParent.children);
            const draggedIndex = links.indexOf(draggedLink);
            const targetIndex = links.indexOf(this);
            
            if (draggedIndex < targetIndex) {
                this.parentNode.insertBefore(draggedLink, this.nextSibling);
            } else {
                this.parentNode.insertBefore(draggedLink, this);
            }
            
            // Update config with new link order
            updateLinkOrder(draggedParent);
        }
    }
    
    return false;
}

function handleLinkDragEnd(e) {
    this.classList.remove('dragging');
    
    const links = document.querySelectorAll('.link-item');
    links.forEach(link => {
        link.classList.remove('drag-over');
    });
    
    draggedLink = null;
    e.stopPropagation();
}

function updateLinkOrder(linksList) {
    const currentConfig = getConfig();
    if (!currentConfig) return;
    
    // Find which category/subcategory this links-list belongs to
    const subcategoryDiv = linksList.closest('.subcategory');
    const categoryDiv = linksList.closest('.category');
    const categoryIndex = parseInt(categoryDiv.dataset.categoryIndex);
    
    const newLinks = [];
    const linkItems = linksList.querySelectorAll('.link-item');
    
    linkItems.forEach((linkItem, newIndex) => {
        const oldIndex = parseInt(linkItem.dataset.linkIndex);
        
        if (subcategoryDiv) {
            const subcategoryIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
            const link = currentConfig.category[categoryIndex].subcategory[subcategoryIndex].links[oldIndex];
            if (link) {
                newLinks.push(link);
                linkItem.dataset.linkIndex = newIndex;
            }
        } else {
            const link = currentConfig.category[categoryIndex].links[oldIndex];
            if (link) {
                newLinks.push(link);
                linkItem.dataset.linkIndex = newIndex;
            }
        }
    });
    
    // Update config
    if (subcategoryDiv) {
        const subcategoryIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
        currentConfig.category[categoryIndex].subcategory[subcategoryIndex].links = newLinks;
    } else {
        currentConfig.category[categoryIndex].links = newLinks;
    }
    
    setConfig(currentConfig);
    console.log('Link order updated');
}

/**
 * Enable subcategory dragging
 */
export function enableSubcategoryDragging() {
    const container = document.getElementById('linksContainer');
    if (!container) return;

    const subcategories = container.querySelectorAll('.subcategory');
    
    subcategories.forEach(subcategory => {
        subcategory.draggable = true;
        
        subcategory.addEventListener('dragstart', handleSubcategoryDragStart);
        subcategory.addEventListener('dragover', handleSubcategoryDragOver);
        subcategory.addEventListener('drop', handleSubcategoryDrop);
        subcategory.addEventListener('dragend', handleSubcategoryDragEnd);
        subcategory.addEventListener('dragenter', handleSubcategoryDragEnter);
        subcategory.addEventListener('dragleave', handleSubcategoryDragLeave);
    });
}

/**
 * Disable subcategory dragging
 */
export function disableSubcategoryDragging() {
    const container = document.getElementById('linksContainer');
    if (!container) return;

    const subcategories = container.querySelectorAll('.subcategory');
    subcategories.forEach(subcategory => {
        subcategory.draggable = false;
        subcategory.removeEventListener('dragstart', handleSubcategoryDragStart);
        subcategory.removeEventListener('dragover', handleSubcategoryDragOver);
        subcategory.removeEventListener('drop', handleSubcategoryDrop);
        subcategory.removeEventListener('dragend', handleSubcategoryDragEnd);
        subcategory.removeEventListener('dragenter', handleSubcategoryDragEnter);
        subcategory.removeEventListener('dragleave', handleSubcategoryDragLeave);
    });
}

function handleSubcategoryDragStart(e) {
    draggedSubcategory = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.stopPropagation();
}

function handleSubcategoryDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    e.stopPropagation();
    return false;
}

function handleSubcategoryDragEnter(e) {
    if (this !== draggedSubcategory && this.classList.contains('subcategory')) {
        this.classList.add('drag-over');
    }
    e.stopPropagation();
}

function handleSubcategoryDragLeave(e) {
    this.classList.remove('drag-over');
    e.stopPropagation();
}

function handleSubcategoryDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedSubcategory !== this && this.classList.contains('subcategory')) {
        // Check if both subcategories are in the same category
        const draggedParent = draggedSubcategory.closest('.category');
        const targetParent = this.closest('.category');
        
        if (draggedParent === targetParent) {
            const subcategories = Array.from(draggedParent.querySelectorAll('.subcategory'));
            const draggedIndex = subcategories.indexOf(draggedSubcategory);
            const targetIndex = subcategories.indexOf(this);
            
            if (draggedIndex < targetIndex) {
                this.parentNode.insertBefore(draggedSubcategory, this.nextSibling);
            } else {
                this.parentNode.insertBefore(draggedSubcategory, this);
            }
            
            // Update config with new subcategory order
            updateSubcategoryOrder(draggedParent);
        }
    }
    
    return false;
}

function handleSubcategoryDragEnd(e) {
    this.classList.remove('dragging');
    
    const subcategories = document.querySelectorAll('.subcategory');
    subcategories.forEach(subcategory => {
        subcategory.classList.remove('drag-over');
    });
    
    draggedSubcategory = null;
    e.stopPropagation();
}

function updateSubcategoryOrder(categoryDiv) {
    const currentConfig = getConfig();
    if (!currentConfig) return;
    
    const categoryIndex = parseInt(categoryDiv.dataset.categoryIndex);
    const subcategoryDivs = categoryDiv.querySelectorAll('.subcategory');
    
    const newOrder = [];
    subcategoryDivs.forEach((subcategoryDiv, newIndex) => {
        const oldIndex = parseInt(subcategoryDiv.dataset.subcategoryIndex);
        const subcategory = currentConfig.category[categoryIndex].subcategory[oldIndex];
        if (subcategory) {
            newOrder.push(subcategory);
            subcategoryDiv.dataset.subcategoryIndex = newIndex;
        }
    });
    
    currentConfig.category[categoryIndex].subcategory = newOrder;
    setConfig(currentConfig);
    console.log('Subcategory order updated');
}

/**
 * Enable widget dragging
 */
export function enableWidgetDragging() {
    const widgetsContainer = document.getElementById('widgetsContainer');
    if (!widgetsContainer) return;

    const widgets = widgetsContainer.querySelectorAll('.widget-wrapper');
    
    // Store initial order
    widgetOrder = Array.from(widgets).map(w => w.dataset.widget);
    
    widgets.forEach(widget => {
        widget.draggable = true;
        
        widget.addEventListener('dragstart', handleWidgetDragStart);
        widget.addEventListener('dragover', handleWidgetDragOver);
        widget.addEventListener('drop', handleWidgetDrop);
        widget.addEventListener('dragend', handleWidgetDragEnd);
        widget.addEventListener('dragenter', handleWidgetDragEnter);
        widget.addEventListener('dragleave', handleWidgetDragLeave);
    });
}

/**
 * Disable widget dragging
 */
export function disableWidgetDragging() {
    const widgetsContainer = document.getElementById('widgetsContainer');
    if (!widgetsContainer) return;

    const widgets = widgetsContainer.querySelectorAll('.widget-wrapper');
    widgets.forEach(widget => {
        widget.draggable = false;
        widget.removeEventListener('dragstart', handleWidgetDragStart);
        widget.removeEventListener('dragover', handleWidgetDragOver);
        widget.removeEventListener('drop', handleWidgetDrop);
        widget.removeEventListener('dragend', handleWidgetDragEnd);
        widget.removeEventListener('dragenter', handleWidgetDragEnter);
        widget.removeEventListener('dragleave', handleWidgetDragLeave);
    });
}

function handleWidgetDragStart(e) {
    draggedWidget = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleWidgetDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleWidgetDragEnter(e) {
    if (this !== draggedWidget) {
        this.classList.add('drag-over');
    }
}

function handleWidgetDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleWidgetDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedWidget !== this) {
        const container = document.getElementById('widgetsContainer');
        const widgets = Array.from(container.children);
        const draggedIndex = widgets.indexOf(draggedWidget);
        const targetIndex = widgets.indexOf(this);
        
        if (draggedIndex < targetIndex) {
            this.parentNode.insertBefore(draggedWidget, this.nextSibling);
        } else {
            this.parentNode.insertBefore(draggedWidget, this);
        }
        
        // Update widget order
        updateWidgetOrder();
    }
    
    return false;
}

function handleWidgetDragEnd(e) {
    this.classList.remove('dragging');
    
    const widgets = document.querySelectorAll('.widget-wrapper');
    widgets.forEach(widget => {
        widget.classList.remove('drag-over');
    });
}

function updateWidgetOrder() {
    const widgetsContainer = document.getElementById('widgetsContainer');
    if (!widgetsContainer) return;
    
    const widgets = widgetsContainer.querySelectorAll('.widget-wrapper');
    widgetOrder = Array.from(widgets).map(w => w.dataset.widget);
    
    // Save to currentConfig for later saving to TOML
    const currentConfig = getConfig();
    if (currentConfig) {
        currentConfig.widget_order = widgetOrder;
        setConfig(currentConfig);
    }
}

/**
 * Move widget up in order
 */
export function moveWidgetUp() {
    if (!window.editMode) return;
    
    const widgetsContainer = document.getElementById('widgetsContainer');
    if (!widgetsContainer) return;
    
    const widgets = Array.from(widgetsContainer.children);
    const focused = document.querySelector('.widget-wrapper:hover');
    
    if (!focused) {
        // Move first widget
        if (widgets.length > 1) {
            widgetsContainer.insertBefore(widgets[0], null);
            updateWidgetOrder();
        }
        return;
    }
    
    const index = widgets.indexOf(focused);
    if (index > 0) {
        widgetsContainer.insertBefore(focused, widgets[index - 1]);
        updateWidgetOrder();
    }
}

/**
 * Move widget down in order
 */
export function moveWidgetDown() {
    if (!window.editMode) return;
    
    const widgetsContainer = document.getElementById('widgetsContainer');
    if (!widgetsContainer) return;
    
    const widgets = Array.from(widgetsContainer.children);
    const focused = document.querySelector('.widget-wrapper:hover');
    
    if (!focused) {
        // Move last widget
        if (widgets.length > 1) {
            widgetsContainer.insertBefore(widgets[widgets.length - 1], widgets[0]);
            updateWidgetOrder();
        }
        return;
    }
    
    const index = widgets.indexOf(focused);
    if (index < widgets.length - 1) {
        widgetsContainer.insertBefore(widgets[index + 1], focused);
        updateWidgetOrder();
    }
}

// Expose functions to window
window.enableCategoryDragging = enableCategoryDragging;
window.disableCategoryDragging = disableCategoryDragging;
window.enableLinkDragging = enableLinkDragging;
window.disableLinkDragging = disableLinkDragging;
window.enableSubcategoryDragging = enableSubcategoryDragging;
window.disableSubcategoryDragging = disableSubcategoryDragging;
window.enableWidgetDragging = enableWidgetDragging;
window.disableWidgetDragging = disableWidgetDragging;
window.moveWidgetUp = moveWidgetUp;
window.moveWidgetDown = moveWidgetDown;
