// static/src/js/pages/products.js

import Button from '../components/button.js';

document.addEventListener('DOMContentLoaded', function() {
    const productTable = document.querySelector('#product-list-table');
    if (productTable) {
        console.log('Initializing product list page...');
        loadProducts();
    }
});

const pageHeaderActions = document.querySelector('#page-header-actions');
if (pageHeaderActions) {
    pageHeaderActions.insertAdjacentHTML('beforeend',
        Button('Додати товар', "add", 'shadow-glow', 'plus', '')
    );
    // if (window.lucide?.createIcons) window.lucide.createIcons();
}


async function loadProducts() {
    const tableBody = document.querySelector('#product-list-body');
    const table = document.querySelector('#product-list-table');
    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center">
                <div class="loading-spinner" style="display: inline-block; vertical-align: middle;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></div>
                </div>
                <span style="vertical-align: middle; margin-left: 10px;">Завантаження товарів...</span>
            </td>
        </tr>
    `;

    try {
        const response = await PCManagement.apiRequest('/products/');
        renderProducts(response.products, tableBody);
        // Після рендерингу даних, ініціалізуємо функціонал таблиці
        PCManagement.initDataTable('#product-list-table', { pageSize: 15 });
    } catch (error) {
        console.error('Failed to load products:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-error">
                    Не вдалося завантажити список товарів.
                </td>
            </tr>
        `;
    }
}

function renderProducts(products, tableBody) {
    if (!products || products.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">Товарів не знайдено. <a href="/products/add/" class="text-primary underline">Додайте перший</a>.</td>
            </tr>
        `;
        return;
    }

    const rowsHtml = products.map(product => {
        const price = PCManagement.formatCurrency(product.price);
        const stockClass = product.quantity_in_stock <= product.min_stock_level ? 'text-error font-bold' : '';

        return `
            <tr data-product-id="${product.id}">
                <td><a href="/products/${product.id}/" class="font-semibold underline">${product.name}</a></td>
                <td>${product.category}</td>
                <td>${product.manufacturer || '—'}</td>
                <td>${price}</td>
                <td class="${stockClass}">${product.quantity_in_stock}</td>
                <td>
                    <a href="/products/${product.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
                    <button class="btn btn--sm btn--error" data-action="delete" data-url="/products/${product.id}/" data-confirm="Ви впевнені, що хочете видалити товар ${product.name}?">Видалити</button>
                </td>
            </tr>
        `;
    }).join('');

    tableBody.innerHTML = rowsHtml;
}