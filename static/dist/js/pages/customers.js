// static/src/js/pages/customers.js

import Button from '../components/button.js';


const customerTable = document.querySelector('#customer-list-table');
if (customerTable) {
    console.log('Initializing customer list page...');
    loadCustomers();
}

const pageHeaderActions = document.querySelector('#page-header-actions');
if (pageHeaderActions) {
    pageHeaderActions.insertAdjacentHTML('beforeend', 
        Button('Додати клієнта', "add", 'shadow-glow', 'plus', '')
    );
    // if (window.lucide?.createIcons) window.lucide.createIcons();
}



async function loadCustomers() {
    const tableBody = document.querySelector('#customer-list-body');
    if (!tableBody) return;

    // Показуємо стан завантаження
    tableBody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center">
                <div class="loading-spinner" style="display: inline-block; vertical-align: middle;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></div>
                </div>
                <span style="vertical-align: middle; margin-left: 10px;">Завантаження клієнтів...</span>
            </td>
        </tr>
    `;

    try {
        // Робимо запит до нашого API
        const response = await PCManagement.apiRequest('/customers/');
        renderCustomers(response.customers, tableBody);
    } catch (error) {
        console.error('Failed to load customers:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-error">
                    Не вдалося завантажити список клієнтів. Спробуйте оновити сторінку.
                </td>
            </tr>
        `;
    }
}

function renderCustomers(customers, tableBody) {
    if (!customers || customers.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">Клієнтів не знайдено. <a href="/customers/add/">Додайте першого</a>.</td>
            </tr>
        `;
        return;
    }

    const rowsHtml = customers.map(customer => {
        // Форматуємо дату за допомогою глобальної функції з main.js
        const registrationDate = PCManagement.formatDate(customer.created_at);

        return `
            <tr data-customer-id="${customer.id}">
                <td><a href="/customers/${customer.id}/" class="font-semibold underline">${customer.name} ${customer.surname}</a></td>
                <td>${customer.email}</td>
                <td>${customer.phone}</td>
                <td>${registrationDate}</td>
                <td>
                    <a href="/customers/${customer.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
                    <button class="btn btn--sm btn--error" data-action="delete" data-url="/customers/${customer.id}/" data-confirm="Ви впевнені, що хочете видалити клієнта ${customer.name} ${customer.surname}?">Видалити</button>
                </td>
            </tr>
        `;
    }).join('');

    tableBody.innerHTML = rowsHtml;
}
//# sourceMappingURL=customers.js.map