// static/src/js/pages/suppliers.js

import Button from '../components/button.js';

document.addEventListener('DOMContentLoaded', function() {
    const supplierTable = document.querySelector('#supplier-list-table');
    if (supplierTable) {
        console.log('Initializing supplier list page...');
        loadSuppliers().then(r => console.log(r));
    }
});

const pageHeaderActions = document.querySelector('#page-header-actions');
if (pageHeaderActions) {
    pageHeaderActions.insertAdjacentHTML('beforeend',
        Button('Додати постачальника', "add", 'shadow-glow', 'plus', '')
    );
    // if (window.lucide?.createIcons) window.lucide.createIcons();
}

async function loadSuppliers() {
    const tableBody = document.querySelector('#supplier-list-body');
    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center">
                <div class="loading-spinner" style="display: inline-block; vertical-align: middle;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></div>
                </div>
                <span style="vertical-align: middle; margin-left: 10px;">Завантаження постачальників...</span>
            </td>
        </tr>
    `;

    try {
        const response = await PCManagement.apiRequest('/suppliers/');
        renderSuppliers(response.suppliers, tableBody);
    } catch (error) {
        console.error('Failed to load suppliers:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-error">
                    Не вдалося завантажити список постачальників.
                </td>
            </tr>
        `;
    }
}

function renderSuppliers(suppliers, tableBody) {
    if (!suppliers || suppliers.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">Постачальників не знайдено. <a href="/suppliers/add/" class="text-primary underline">Додайте першого</a>.</td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = suppliers.map(supplier => `
        <tr data-supplier-id="${supplier.id}">
            <td><a href="/suppliers/${supplier.id}/" class="font-semibold underline">${supplier.name}</a></td>
            <td>${supplier.contact_person || '—'}</td>
            <td>${supplier.email}</td>
            <td>${supplier.phone}</td>
            <td class="dropdown-data">
                <button type="button" class="dropdown-toggle">...</button>
                <ul class="dropdown-menu">
                    <li>
                        <a href="/suppliers/${supplier.id}/edit/" class="btn btn--sm btn--secondary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="square-pen" class="lucide lucide-square-pen h-4 w-4">
                                <path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                <path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path>
                            </svg>
                            Редагувати
                        </a>
                    </li>
                    <li>
                        <button class="btn btn--sm btn--error w-full" data-action="delete" data-url="/suppliers/${supplier.id}/" data-confirm="Ви впевнені, що хочете видалити постачальника ${supplier.name}?">
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
    `).join('');
}