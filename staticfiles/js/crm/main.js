'use strict';

// static/src/js/main.js

// === GLOBAL VARIABLES ===
let isLoading = false;
const API_BASE_URL = '/api';

// === UTILITY FUNCTIONS ===
function showLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.classList.add('is-visible');
        isLoading = true;
    }
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.classList.remove('is-visible');
        isLoading = false;
    }
}

function formatCurrency(amount, currency = 'UAH') {
    const formatter = new Intl.NumberFormat('uk-UA', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    });
    return formatter.format(amount).replace('UAH', '₴');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatShortDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// === API FUNCTIONS ===
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
    };

    const config = { ...defaultOptions, ...options };

    try {
        showLoading();
        const response = await fetch(url, config);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Request failed:', error);
        showNotification('Помилка завантаження даних', 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

function getCsrfToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }

    const csrfCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));

    return csrfCookie ? csrfCookie.split('=')[1] : '';
}

// === NOTIFICATION SYSTEM ===
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.innerHTML = `
        <div class="notification__content">
            <span class="notification__message">${message}</span>
            <button class="notification__close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // Додати стилі для notifications, якщо їх немає
    if (!document.querySelector('.notifications-container')) {
        const container = document.createElement('div');
        container.className = 'notifications-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1080;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    const container = document.querySelector('.notifications-container');
    notification.style.cssText = `
        background: var(--color-white);
        border: 1px solid var(--color-gray-200);
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-lg);
        padding: var(--spacing-4);
        margin-bottom: var(--spacing-2);
        min-width: 300px;
        pointer-events: all;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;

    if (type === 'error') {
        notification.style.borderColor = 'var(--color-error)';
        notification.style.backgroundColor = 'rgb(239 68 68 / 0.05)';
    } else if (type === 'success') {
        notification.style.borderColor = 'var(--color-success)';
        notification.style.backgroundColor = 'rgb(16 185 129 / 0.05)';
    } else if (type === 'warning') {
        notification.style.borderColor = 'var(--color-warning)';
        notification.style.backgroundColor = 'rgb(245 158 11 / 0.05)';
    }

    container.appendChild(notification);

    // Анімація появи
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Автоматичне видалення
    if (duration > 0) {
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, duration);
    }
}

// === HEADER & NAVIGATION ===
function initHeader() {
    const searchToggle = document.querySelector('.search-toggle');
    const searchPanel = document.querySelector('.header__search');
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');

    // Пошук
    if (searchToggle && searchPanel) {
        searchToggle.addEventListener('click', () => {
            searchPanel.classList.toggle('is-visible');
            if (searchPanel.classList.contains('is-visible')) {
                const searchInput = searchPanel.querySelector('.search-form__input');
                if (searchInput) {
                    setTimeout(() => searchInput.focus(), 300);
                }
            }
        });

        // Закрити пошук по ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchPanel.classList.contains('is-visible')) {
                searchPanel.classList.remove('is-visible');
            }
        });
    }

    // Мобільне меню (заглушка для майбутньої реалізації)
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            console.log('Mobile menu toggle');
        });
    }

    // Пошук
    initSearch();
}

function initSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-form__input');
    const searchBtn = document.querySelector('.search-form__btn');

    if (!searchForm || !searchInput) return;

    const debouncedSearch = debounce(performSearch, 300);

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            debouncedSearch(query);
        }
    });

    if (searchBtn) {
        searchBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                performSearch(query);
            }
        });
    }

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });
}

async function performSearch(query) {
    try {
        console.log('Searching for:', query);
        // Тут буде логіка пошуку через API
        // const results = await apiRequest(`/search/?q=${encodeURIComponent(query)}`);
        // displaySearchResults(results);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

// === DATA TABLES ===
function initDataTable(tableSelector, options = {}) {
    const table = document.querySelector(tableSelector);
    if (!table) return;

    const defaultOptions = {
        sortable: true,
        filterable: true,
        pagination: true,
        pageSize: 10,
    };

    const config = { ...defaultOptions, ...options };

    if (config.sortable) {
        addTableSorting(table);
    }

    if (config.filterable) {
        addTableFiltering(table);
    }

    if (config.pagination) {
        addTablePagination(table, config.pageSize);
    }
}

function addTableSorting(table) {
    // const headers = table.querySelectorAll('th[data-sortable="true"]');

    // headers.forEach((header, index) => {
    //     header.style.cursor = 'pointer';
    //     header.innerHTML += ' <span class="sort-indicator">↕️</span>';

    //     header.addEventListener('click', () => {
    //         sortTable(table, index, header);
    //     });
    // });
    return table;
}

function sortTable(table, columnIndex, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = header.classList.contains('sort-asc');

    // Очистити попередні індикатори сортування
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        const indicator = th.querySelector('.sort-indicator');
        if (indicator) {
            indicator.textContent = '↕️';
        }
    });

    // Сортування
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();

        // Спробувати як числа
        const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAsc ? bNum - aNum : aNum - bNum;
        }

        // Як текст
        return isAsc ? bText.localeCompare(aText) : aText.localeCompare(bText);
    });

    // Оновити DOM
    rows.forEach(row => tbody.appendChild(row));

    // Оновити індикатор
    header.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
    const indicator = header.querySelector('.sort-indicator');
    if (indicator) {
        indicator.textContent = isAsc ? '↓' : '↑';
    }
}

function addTableFiltering(table) {
    const tableContainer = table.closest('.table-container');
    if (!tableContainer) return;

    // Перевіряємо, чи фільтр вже існує
    if (tableContainer.querySelector('.table-filter')) return;

    const filterInput = document.createElement('input');
    filterInput.type = 'text';
    filterInput.placeholder = 'Фільтрувати...';
    filterInput.className = 'table-filter form-input';
    filterInput.style.marginBottom = 'var(--spacing-4)';
    // filterInput.style.maxWidth = '300px';
    filterInput.id = 'table-filter';

    tableContainer.insertBefore(filterInput, table);

    const handleFilter = debounce(() => {
        const filterValue = filterInput.value.toLowerCase();
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');

        rows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            if (rowText.includes(filterValue)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }, 250);

    filterInput.addEventListener('keyup', handleFilter);
}

function addTablePagination(table, pageSize) {
    const tableContainer = table.closest('.table-container');
    if (!tableContainer) return;

    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const totalPages = Math.ceil(rows.length / pageSize);
    let currentPage = 1;

    if (totalPages <= 1) return;

    function showPage(page) {
        currentPage = page;
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;

        rows.forEach((row, index) => {
            row.style.display = (index >= startIndex && index < endIndex) ? '' : 'none';
        });

        updatePaginationControls();
    }

    function updatePaginationControls() {
        let paginationContainer = tableContainer.querySelector('.pagination-container');
        if (!paginationContainer) {
            paginationContainer = document.createElement('div');
            paginationContainer.className = 'pagination-container';
            paginationContainer.style.marginTop = 'var(--spacing-4)';
            tableContainer.appendChild(paginationContainer);
        }

        let paginationHtml = '<div class="pagination">';
        paginationHtml += `<button class="btn btn--sm btn--secondary" ${currentPage === 1 ? 'disabled' : ''} onclick="this.closest('.table-container').__pagination.showPage(${currentPage - 1})">Попередня</button>`;

        paginationHtml += `<span class="pagination__info">Сторінка ${currentPage} з ${totalPages}</span>`;

        paginationHtml += `<button class="btn btn--sm btn--secondary" ${currentPage === totalPages ? 'disabled' : ''} onclick="this.closest('.table-container').__pagination.showPage(${currentPage + 1})">Наступна</button>`;
        paginationHtml += '</div>';

        paginationContainer.innerHTML = paginationHtml;
    }

    // Зберігаємо функції в об'єкті, прив'язаному до контейнера, щоб уникнути глобальних конфліктів
    tableContainer.__pagination = { showPage };

    showPage(1);
}

// === FORM HANDLING ===
function initForms() {
    // Загальна ініціалізація форм
    const forms = document.querySelectorAll('form[data-ajax="true"]');

    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Валідація полів в реальному часі
    const inputs = document.querySelectorAll('.form-input, .form-select, .form-textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

async function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : '';

    try {

        // Показати стан завантаження
        if (submitBtn) {
            submitBtn.disabled = true;

            submitBtn.textContent = 'Збереження...';
        }

        // Отримати дані форми
        const formData = new FormData(form);

        
        const data = Object.fromEntries(formData.entries());
        
        // console.log(data.email.toString())
        if(data.email) {
            data.email += '@gmail.com'
        }
        // console.log(data.email.toString() + '   3')


        // Відправити запит
        const endpoint = form.getAttribute('action') || window.location.pathname;
        const response = await apiRequest(endpoint, {
            method: form.method || 'POST',
            body: JSON.stringify(data)
        });

        showNotification('Дані успішно збережено', 'success');

        // Перенаправлення або оновлення
        if (response.redirect_url) {
            window.location.href = response.redirect_url;
        } else if (form.dataset.reload === 'true') {
            window.location.reload();
        }

    } catch (error) {
        showNotification('Помилка збереження даних', 'error');

        // Показати помилки полів
        if (error.field_errors) {
            displayFieldErrors(form, error.field_errors);
        }
    } finally {
        // Відновити кнопку
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    const fieldName = field.name;

    // Очистити попередні помилки
    clearFieldError({ target: field });

    // Валідація за типом поля
    let error = null;

    if (field.hasAttribute('required') && !value) {
        error = 'Це поле обов\'язкове';
    }
    // else if (field.type === 'email' && value && !isValidEmail(value)) {
    //     error = 'Невірний формат email';
    // } 
    else if (field.type === 'tel' && value && !isValidPhone(value)) {
        error = 'Невірний формат телефону';
    } else if (field.dataset.minLength && value.length < parseInt(field.dataset.minLength)) {
        error = `Мінімальна довжина ${field.dataset.minLength} символів`;
    }

    if (error) {
        showError(field, error);
        displayFieldError(field, error);
    }
}

function clearFieldError(event) {
    const field = event.target;
    const errorElement = field.parentElement.querySelector('.form-error');
    if (errorElement) {
        errorElement.remove();
    }
    field.classList.remove('form-input--error');
}

function displayFieldError(field, message) {
    // Видалити попередню помилку
    clearFieldError({ target: field });

    // Додати клас помилки
    field.classList.add('form-input--error');

    // Створити елемент помилки
    const errorElement = document.createElement('div');
    errorElement.className = 'form-error';
    errorElement.textContent = message;

    // Вставити після поля
    field.parentElement.appendChild(errorElement);
}

function displayFieldErrors(form, errors) {
    Object.keys(errors).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            displayFieldError(field, errors[fieldName][0]);
        }
    });
}

function showError(input, message) {
    let inputGroup = input.closest('.input-group');
    let error = inputGroup.nextElementSibling;

    if (!error || !error.classList.contains('error-message')) {
        error = document.createElement('div');
        error.className = 'error-message text-error mt-1 text-sm';
        inputGroup.insertAdjacentElement('afterend', error);
    }

    error.textContent = message;
}

// === VALIDATION HELPERS ===
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^\+380\d{9}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// === MODAL HANDLING ===
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('is-visible');
        document.body.style.overflow = 'hidden';

        // Фокус на першому елементі
        const firstFocusable = modal.querySelector('input, button, textarea, select');
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 100);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('is-visible');
        document.body.style.overflow = '';
    }
}

function initModals() {
    // Закриття модалок по кліку на backdrop
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
    });

    // Закриття модалок по ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const visibleModal = document.querySelector('.modal.is-visible');
            if (visibleModal) {
                closeModal(visibleModal.id);
            }
        }
    });

    // Кнопки закриття модалок
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-close')) {
            const modal = e.target.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        }
    });
}

// === DATA LOADING FUNCTIONS ===
async function loadData(endpoint, containerId, renderFunction) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
        showLoading();
        const data = await apiRequest(endpoint);
        renderFunction(data, container);
    } catch (error) {
        container.innerHTML = '<p class="text-error">Помилка завантаження даних</p>';
    } finally {
        hideLoading();
    }
}

// === PAGINATION ===
function initPagination(containerId, loadFunction) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let currentPage = 1;
    const pageSize = 10;

    function createPaginationControls(totalPages) {
        const paginationHtml = `
            <div class="pagination">
                <button class="pagination__btn" onclick="loadPage(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''}>
                    Попередня
                </button>
                <span class="pagination__info">
                    Сторінка ${currentPage} з ${totalPages}
                </span>
                <button class="pagination__btn" onclick="loadPage(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''}>
                    Наступна
                </button>
            </div>
        `;

        let paginationContainer = container.querySelector('.pagination-container');
        if (!paginationContainer) {
            paginationContainer = document.createElement('div');
            paginationContainer.className = 'pagination-container';
            container.appendChild(paginationContainer);
        }

        paginationContainer.innerHTML = paginationHtml;
    }

    window.loadPage = function(page) {
        if (page < 1) return;
        currentPage = page;
        loadFunction(page, pageSize);
    };
}

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', function() {
    // Основна ініціалізація
    initHeader();
    initForms();
    initModals();

    // Ініціалізація таблиць
    const tables = document.querySelectorAll('.table-container .table-wrapper');
    if (tables.length > 0) {
        initDataTable('.table-container .table-wrapper');
    }

    // Глобальні обробники подій
    document.addEventListener('click', handleGlobalClicks);

    console.log('PC Management System initialized');
});

// === GLOBAL CLICK HANDLER ===
function handleGlobalClicks(event) {
    const target = event.target;

    console.log('object hui');

    // Обробка кнопок з data-атрибутами
    if (target.dataset.action) {
        event.preventDefault();
        handleDataAction(target.dataset.action, target);
    }

    // Обробка посилань з підтвердженням
    if (target.classList.contains('confirm-link')) {
        event.preventDefault();
        const message = target.dataset.confirm || 'Ви впевнені?';
        if (confirm(message)) {
            window.location.href = target.href;
        }
    }
}

function handleDataAction(action, element) {
    switch (action) {
        case 'delete':
            handleDelete(element);
            break;
        case 'toggle-status':
            handleToggleStatus(element);
            break;
        case 'export':
            handleExport(element);
            break;
        default:
            console.warn('Unknown action:', action);
    }
}

async function handleDelete(element) {
    const confirmMessage = element.dataset.confirm || 'Ви впевнені, що хочете видалити?';
    if (!confirm(confirmMessage)) {
        return;
    }

    const deleteUrl = element.dataset.url || element.href;

    try {
        await apiRequest(deleteUrl, { method: 'DELETE' });
        showNotification('Запис видалено', 'success');

        // Видалити рядок з таблиці або перезавантажити сторінку
        const row = element.closest('tr');
        if (row) {
            row.remove();
        } else {
            window.location.reload();
        }
    } catch (error) {
        showNotification('Помилка видалення', 'error');
    }
}

async function handleToggleStatus(element) {
    const toggleUrl = element.dataset.url;
    const currentStatus = element.dataset.status;

    try {
        const response = await apiRequest(toggleUrl, {
            method: 'POST',
            body: JSON.stringify({ status: currentStatus === 'active' ? 'inactive' : 'active' })
        });

        // Оновити UI
        element.dataset.status = response.status;
        element.textContent = response.status === 'active' ? 'Деактивувати' : 'Активувати';

        showNotification('Статус оновлено', 'success');
    } catch (error) {
        showNotification('Помилка оновлення статусу', 'error');
    }
}

function handleExport(element) {
    const exportUrl = element.dataset.url;
    const format = element.dataset.format || 'excel';

    // Відкрити в новому вікні для завантаження
    window.open(`${exportUrl}?format=${format}`, '_blank');
}

// === EXPORT FUNCTIONS ===
window.PCManagement = {
    // API функції
    apiRequest,
    showNotification,
    showLoading,
    hideLoading,

    // Utility функції
    formatCurrency,
    formatDate,
    formatShortDate,
    debounce,

    // Modal функції
    openModal,
    closeModal,

    // Form функції
    validateField,
    clearFieldError,
    displayFieldError,

    // Data функції
    loadData,
    initDataTable,
    initPagination
};//# sourceMappingURL=main.js.map
