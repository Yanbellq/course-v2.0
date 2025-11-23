/**
 * Universal Product List Manager
 * Automatically initializes all product tables on the page
 */

// Products data with prices
// These variables are declared in the Django template before this script loads
// We just reference them here - no need to redeclare
// If they're not defined in template, they will be undefined and we'll handle that in the code

/**
 * ProductListManager - Universal manager for product tables
 */
class ProductListManager {
    constructor(config) {
        this.config = {
            tableBodyId: config.tableBodyId,
            addButtonId: config.addButtonId,
            totalDisplayId: config.totalDisplayId,
            productSelectName: config.productSelectName || 'product_id[]',
            quantityInputName: config.quantityInputName || 'quantity[]',
            priceInputName: config.priceInputName || 'unit_price[]',
            productsSource: config.productsSource || 'productsList', // 'productsList' or 'componentsData'
            pricesSource: config.pricesSource || 'productsData', // 'productsData' or 'componentsData'
            emptyMessage: config.emptyMessage || 'No products added yet',
            emptyRowClass: config.emptyRowClass || 'empty-specifications',
            ...config
        };
        
        this.tableBody = document.getElementById(this.config.tableBodyId);
        this.addButton = document.getElementById(this.config.addButtonId);
        this.totalDisplay = document.getElementById(this.config.totalDisplayId);
        
        if (!this.tableBody) {
            console.warn(`ProductListManager: Table body with ID "${this.config.tableBodyId}" not found`);
            return;
        }
        
        if (!this.addButton) {
            console.warn(`ProductListManager: Add button with ID "${this.config.addButtonId}" not found`);
        }
        
        if (!this.totalDisplay) {
            console.warn(`ProductListManager: Total display with ID "${this.config.totalDisplayId}" not found`);
        }
        
        this.init();
    }
    
    init() {
        // Add event listeners first
        this.attachEventListeners();
        
        // Initialize existing rows
        this.updateEmptyState();
        
        // Calculate initial subtotals for existing rows with data attributes
        this.tableBody.querySelectorAll('.subtotal-display[data-quantity][data-price]').forEach(span => {
            const quantity = parseFloat(span.dataset.quantity) || 0;
            const price = parseFloat(span.dataset.price) || 0;
            const subtotal = quantity * price;
            span.textContent = '$' + subtotal.toFixed(2);
        });
        
        // Calculate total after initialization
        this.calculateTotal();
    }
    
    attachEventListeners() {
        // Listen for changes in quantity and price inputs
        this.tableBody.addEventListener('input', (e) => {
            if (e.target.name === this.config.quantityInputName || e.target.name === this.config.priceInputName) {
                this.calculateTotal();
            }
        });
        
        // Listen for product select changes (works for both select and any element with matching name)
        this.tableBody.addEventListener('change', (e) => {
            if (e.target.tagName === 'SELECT' && e.target.name === this.config.productSelectName) {
                this.updateUnitPrice(e.target);
            }
        });
        
        // Listen for remove button clicks (delegated event)
        this.tableBody.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-product') || e.target.closest('.remove-product')) {
                const button = e.target.classList.contains('remove-product') ? e.target : e.target.closest('.remove-product');
                const row = button.closest('tr');
                if (row) {
                    row.remove();
                    this.updateEmptyState();
                    this.calculateTotal();
                }
            }
        });
        
        // Add button click handler
        if (this.addButton) {
            this.addButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.addRow();
            });
        } else {
            console.warn(`ProductListManager: Add button "${this.config.addButtonId}" not found, cannot add rows`);
        }
    }
    
    updateEmptyState() {
        const productRows = this.tableBody.querySelectorAll('.product-row');
        const emptyRow = this.tableBody.querySelector(`.${this.config.emptyRowClass}`);
        
        if (productRows.length === 0) {
            // Show empty message if it doesn't exist
            if (!emptyRow) {
                const emptyTr = document.createElement('tr');
                emptyTr.className = `specification-row ${this.config.emptyRowClass}`;
                emptyTr.innerHTML = `<td colspan="5">${this.config.emptyMessage}</td>`;
                this.tableBody.appendChild(emptyTr);
            }
        } else {
            // Hide empty message if products exist
            if (emptyRow) {
                emptyRow.remove();
            }
        }
    }
    
    calculateSubtotal(row) {
        const quantityInput = row.querySelector(`input[name="${this.config.quantityInputName}"]`);
        const priceInput = row.querySelector(`input[name="${this.config.priceInputName}"]`);
        const subtotalSpan = row.querySelector('.subtotal-display');
        
        if (quantityInput && priceInput && subtotalSpan) {
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const subtotal = quantity * price;
            subtotalSpan.textContent = '$' + subtotal.toFixed(2);
        }
    }
    
    calculateTotal() {
        const productRows = this.tableBody.querySelectorAll('.product-row');
        let total = 0;
        
        productRows.forEach(row => {
            const quantityInput = row.querySelector(`input[name="${this.config.quantityInputName}"]`);
            const priceInput = row.querySelector(`input[name="${this.config.priceInputName}"]`);
            
            if (quantityInput && priceInput) {
                const quantity = parseFloat(quantityInput.value) || 0;
                const price = parseFloat(priceInput.value) || 0;
                total += quantity * price;
                this.calculateSubtotal(row);
            }
        });
        
        if (this.totalDisplay) {
            this.totalDisplay.textContent = '$' + total.toFixed(2);
        }
        
        // Auto-update additional field if configured (e.g., cost field, total_amount)
        if (this.config.autoUpdateFieldId) {
            const field = document.getElementById(this.config.autoUpdateFieldId);
            if (field) {
                field.value = total.toFixed(2);
            }
        }
        
        // Auto-update total_amount hidden field if it exists (for contracts, supplies, etc.)
        const totalAmountField = document.getElementById('total_amount');
        if (totalAmountField && !this.config.autoUpdateFieldId) {
            totalAmountField.value = total.toFixed(2);
        }
    }
    
    updateUnitPrice(selectElement) {
        const row = selectElement.closest('.product-row');
        if (!row) return;
        
        const priceInput = row.querySelector(`input[name="${this.config.priceInputName}"]`);
        if (!priceInput) return;
        
        const productId = selectElement.value;
        
        let price = null;
        
        if (productId) {
            // Try to get price from configured source
            if (this.config.pricesSource === 'componentsData') {
                if (typeof componentsData !== 'undefined' && Array.isArray(componentsData)) {
                    const component = componentsData.find(c => String(c.id) === String(productId));
                    if (component && component.price) {
                        price = component.price;
                    }
                }
            } else if (this.config.pricesSource === 'productsData') {
                if (typeof productsData !== 'undefined') {
                    price = productsData[productId];
                }
            }
        }
        
        if (price !== null && price > 0) {
            priceInput.value = price;
        } else {
            priceInput.value = '';
        }
        
        this.calculateTotal();
    }
    
    addRow() {
        const row = document.createElement('tr');
        row.className = 'product-row';
        
        // Get products source (variables are declared in template)
        let productsSource;
        if (this.config.productsSource === 'componentsData') {
            productsSource = typeof componentsData !== 'undefined' ? componentsData : [];
        } else {
            productsSource = typeof productsList !== 'undefined' ? productsList : [];
        }
        
        // Build options HTML
        let optionsHTML = '<option value="">Select product</option>';
        if (productsSource && Array.isArray(productsSource)) {
            productsSource.forEach(product => {
                if (product && product.id && product.name) {
                    optionsHTML += `<option value="${product.id}">${product.name}</option>`;
                }
            });
        }
        
        // Determine placeholder text
        const placeholder = this.config.productsSource === 'componentsData' ? 'Select component' : 'Select product';
        optionsHTML = optionsHTML.replace('Select product', placeholder);
        
        row.innerHTML = `
            <td>
                <select name="${this.config.productSelectName}" class="product-select" required style="width: 100%; padding: 4px 8px;">
                    ${optionsHTML}
                </select>
            </td>
            <td>
                <input type="number" name="${this.config.quantityInputName}" min="1" class="quantity-input" value="1" required style="width: 100%; padding: 4px 8px;">
            </td>
            <td>
                <input type="number" name="${this.config.priceInputName}" step="0.01" min="0" class="unit-price-input" value="0" required style="width: 100%; padding: 4px 8px;">
            </td>
            <td>
                <span class="subtotal-display">$0.00</span>
            </td>
            <td style="text-align: center;">
                <button type="button" class="btn btn--danger remove-product" style="padding: 4px 8px;">×</button>
            </td>
        `;
        
        this.tableBody.appendChild(row);
        this.updateEmptyState();
        this.calculateTotal();
    }
}

// Auto-initialize all product tables on page load
function initProductListManagers() {
    // Initialize products table (if exists)
    if (document.getElementById('productsTableBody')) {
        new ProductListManager({
            tableBodyId: 'productsTableBody',
            addButtonId: 'addProductBtn',
            totalDisplayId: 'totalAmountDisplayFooter',
            productSelectName: 'product_id[]',
            quantityInputName: 'quantity[]',
            priceInputName: 'unit_price[]',
            productsSource: 'productsList',
            pricesSource: 'productsData',
            emptyMessage: 'No products added yet'
        });
    }
    
    // Initialize custom build products table (if exists)
    if (document.getElementById('customBuildProductsTableBody')) {
        new ProductListManager({
            tableBodyId: 'customBuildProductsTableBody',
            addButtonId: 'addCustomBuildProductBtn',
            totalDisplayId: 'customBuildTotalDisplayFooter',
            productSelectName: 'cb_product_id[]',
            quantityInputName: 'cb_quantity[]',
            priceInputName: 'cb_unit_price[]',
            productsSource: 'componentsData',
            pricesSource: 'componentsData',
            emptyMessage: 'No components added yet'
        });
    }
    
    // Initialize products used table (if exists)
    if (document.getElementById('productsUsedTableBody')) {
        new ProductListManager({
            tableBodyId: 'productsUsedTableBody',
            addButtonId: 'addProductUsedBtn',
            totalDisplayId: 'productsUsedTotalDisplay',
            productSelectName: 'used_product_id[]',
            quantityInputName: 'used_quantity[]',
            priceInputName: 'used_unit_price[]',
            productsSource: 'productsList',
            pricesSource: 'productsData',
            emptyMessage: 'No products added yet',
            autoUpdateFieldId: 'cost' // Auto-update cost field
        });
    }
    
    // Initialize delivery products table (if exists) - for order total display only
    // Check specifically for delivery form by looking for orderTotalDisplayFooter
    const orderTotalDisplay = document.getElementById('orderTotalDisplayFooter');
    if (orderTotalDisplay) {
        const deliveryTableBody = document.getElementById('productsTableBody');
        if (deliveryTableBody) {
            // Listen for changes in quantity and price inputs to update order total
            deliveryTableBody.addEventListener('input', (e) => {
                if (e.target.name === 'quantity[]' || e.target.name === 'unit_price[]') {
                    const productRows = deliveryTableBody.querySelectorAll('.product-row');
                    let total = 0;
                    
                    productRows.forEach(row => {
                        const quantityInput = row.querySelector('input[name="quantity[]"]');
                        const priceInput = row.querySelector('input[name="unit_price[]"]');
                        
                        if (quantityInput && priceInput) {
                            const quantity = parseFloat(quantityInput.value) || 0;
                            const price = parseFloat(priceInput.value) || 0;
                            total += quantity * price;
                            
                            // Update subtotal
                            const subtotalSpan = row.querySelector('.subtotal-display');
                            if (subtotalSpan) {
                                subtotalSpan.textContent = '$' + (quantity * price).toFixed(2);
                            }
                        }
                    });
                    
                    orderTotalDisplay.textContent = '$' + total.toFixed(2);
                }
            });
        }
    }
    
    // Calculate initial subtotals for all existing rows with data attributes
    document.querySelectorAll('.subtotal-display[data-quantity][data-price]').forEach(span => {
        const quantity = parseFloat(span.dataset.quantity) || 0;
        const price = parseFloat(span.dataset.price) || 0;
        const subtotal = quantity * price;
        span.textContent = '$' + subtotal.toFixed(2);
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProductListManagers);
} else {
    // DOM is already ready
    initProductListManagers();
}

// Legacy functions for backward compatibility (if needed)
function toggleCustomBuild() {
    const checkbox = document.getElementById('has_custom_build');
    const section = document.getElementById('custom_build_section');
    if (checkbox && section) {
        section.style.display = checkbox.checked ? 'block' : 'none';
        if (checkbox.checked) {
            setTimeout(() => {
                const manager = window.productListManagers?.find(m => m.config.tableBodyId === 'customBuildProductsTableBody');
                if (manager) manager.calculateTotal();
            }, 100);
        }
    }
}

function toggleSoftwareService() {
    const checkbox = document.getElementById('has_software_service');
    const section = document.getElementById('software_service_section');
    if (checkbox && section) {
        section.style.display = checkbox.checked ? 'block' : 'none';
    }
}
