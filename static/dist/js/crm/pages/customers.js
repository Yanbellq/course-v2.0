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
                <td class="dropdown-data">
                    <button type="button" class="dropdown-toggle">...</button>
                    <ul class="dropdown-menu">
                        <li>
                            <a href="/customers/${customer.id}/edit/" class="btn btn--sm btn--secondary">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="square-pen" class="lucide lucide-square-pen h-4 w-4">
                                    <path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path>
                                </svg>
                                Редагувати
                            </a>
                        </li>
                        <li>
                            <button class="btn btn--sm btn--error w-full" data-action="delete" data-url="/customers/${customer.id}/" data-confirm="Ви впевнені, що хочете видалити клієнта ${customer.name} ${customer.surname}?">
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
}//# sourceMappingURL=customers.js.map
