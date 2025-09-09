'use strict'

// static/src/js/pages/products.js

// import Button from '../components/button.js';
import Button from '../../../dist_ts/components/btn.js';

document.addEventListener('DOMContentLoaded', function() {
    const productTable = document.querySelector('#product-list-table');
    if (productTable) {
        console.log('Initializing product list page...');
        loadProducts();
    }
});

const btn_props = {
    text: 'Додати товар',
    link: "add",
    styles: 'shadow-glow',
    icon: 'plus',
    icon_styles: '',
}

const pageHeaderActions = document.querySelector('#page-header-actions');
if (pageHeaderActions) {
    pageHeaderActions.insertAdjacentHTML('beforeend',
        Button(btn_props)
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

window.activate = (e) => {
    const dropdown = e.target.closest('.dropdown');
    dropdown.querySelector('.dropdown-menu').classList.toggle('active');
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
        const stockClass = product.quantity_in_stock <= product.min_stock_level ? 'text-error font-bold' : '';

        return `
            <tr data-product-id="${product.id}">
                <td><a href="/products/${product.id}/" class="font-semibold underline">${product.name}</a></td>
                <td>${product.category}</td>
                <td>${product.manufacturer || '—'}</td>
                <td>${price}</td>
                <td class="${stockClass}">${product.quantity_in_stock}</td>
                <td class="dropdown">
                    <button type="button" class="dropdown-toggle">...</button>
                    <ul class="dropdown-menu">
                        <li><a href="/products/${product.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a></li>
                        <li><button class="btn btn--sm btn--error" data-action="delete" data-url="/products/${product.id}/" data-confirm="Ви впевнені, що хочете видалити товар ${product.name}?">Видалити</button></li>
                    </ul>
                </td>
            </tr>
        `;
    }).join('');

    tableBody.innerHTML = rowsHtml;


    function initDropdowns() {
        document.querySelectorAll('.dropdown').forEach(dropdown => {
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
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.active').forEach(menu => {
                    menu.classList.remove('active');
                });
            }
        });
    }

    initDropdowns();
}


// <a href="/products/${product.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
// <button class="btn btn--sm btn--error" data-action="delete" data-url="/products/${product.id}/" data-confirm="Ви впевнені, що хочете видалити товар ${product.name}?">Видалити</button>
//# sourceMappingURL=products.js.map
