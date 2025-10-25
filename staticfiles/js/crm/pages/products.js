// 'use strict'

// static/src/js/pages/products.js

import Button from '../components/button.js';
// import Button from '../../../../dist_ts/components/btn.js';

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
                <td colspan="6" class="text-center">
                    <div>
                        <div class="flex items-center justify-center pt-4">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="package" class="lucide lucide-package h-10 w-10 text-gray-600">
                                <path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"></path>
                                <path d="M12 22V12"></path>
                                <polyline points="3.29 7 12 12 20.71 7"></polyline>
                                <path d="m7.5 4.27 9 5.15"></path>
                            </svg>
                        </div>
                        <h3 class="mt-2 text-base font-medium text-gray-900 text-center mt-4">Товари не знайдено</h3>
                        <p class="mt-1 text-sm text-gray-500 text-center pb-4 mt-2">
                            Спробуйте змінити параметри пошуку або створіть новий товар.
                        </p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    const rowsHtml = products.map(product => {
        const price = PCManagement.formatCurrency(product.price);
        const stockClass = product.quantity_in_stock <= product.min_stock_level ? 'text-error' : '';

        return `
            <tr data-product-id="${product.id}">
                <td><a href="/products/${product.id}/" class="font-semibold underline">${product.name}</a></td>
                <td>${product.category}</td>
                <td>${product.manufacturer || '—'}</td>
                <td>${price}</td>
                <td class="${stockClass}">${product.quantity_in_stock}</td>
                <td class="dropdown-data">
                    <button type="button" class="dropdown-toggle">...</button>
                    <ul class="dropdown-menu">
                        <li>
                            <a href="/products/${product.id}/edit/" class="btn btn--sm btn--secondary">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="square-pen" class="lucide lucide-square-pen h-4 w-4">
                                    <path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path>
                                </svg>
                                Редагувати
                            </a>
                        </li>
                        <li>
                            <button class="btn btn--sm btn--error w-full" data-action="delete" data-url="/products/${product.id}/" data-confirm="Ви впевнені, що хочете видалити товар ${product.name}?">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trash-2" class="lucide lucide-trash-2 h-4 w-4">
                                    <path d="M10 11v6"></path><path d="M14 11v6"></path>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path>
                                    <path d="M3 6h18"></path><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                                Видалити
                            </button>
                        </li>
                    </ul>
                </td>
            </tr>
        `;
    }).join('');

    tableBody.innerHTML = rowsHtml;


    function initDropdowns() {
        document.querySelectorAll('.dropdown-data').forEach(dropdown => {
            const dropdownToggle = dropdown.querySelector('.dropdown-toggle');
            const dropdownMenu = dropdown.querySelector('.dropdown-menu');

            dropdownToggle.addEventListener('click', (e) => {
                // Close all dropdowns first
                document.querySelectorAll('.dropdown-menu.active').forEach(menu => {
                    if (menu !== dropdownMenu) {
                        menu.classList.remove('active');
                    }
                });
                // Toggle only the clicked dropdown
                dropdownMenu.classList.toggle('active');
            });
        });

        // Optional: close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown-data')) {
                document.querySelectorAll('.dropdown-menu.active').forEach(menu => {
                    menu.classList.remove('active');
                });
            }
        });
    }

    initDropdowns();
}


// <a href="/products/${product.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
// <button class="btn btn--sm btn--error" data-action="delete" data-url="/products/${product.id}/" data-confirm="Ви впевнені, що хочете видалити товар ${product.name}?">Видалити</button>//# sourceMappingURL=products.js.map
