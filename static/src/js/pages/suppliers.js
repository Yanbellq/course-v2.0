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
            <td>
                <a href="/suppliers/${supplier.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
                <button class="btn btn--sm btn--error" data-action="delete" data-url="/suppliers/${supplier.id}/" data-confirm="Ви впевнені, що хочете видалити постачальника ${supplier.name}?">Видалити</button>
            </td>
        </tr>
    `).join('');
}