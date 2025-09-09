// static/src/js/pages/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // Цей скрипт виконується тільки на сторінці, де є елемент .dashboard-stats
    if (document.querySelector('.dashboard-stats')) {
        console.log('Initializing dashboard page...');
        loadDashboardData();
        initCharts();
    }
});

function loadDashboardData() {
    // У майбутньому тут будуть AJAX-запити до вашого Django API.
    // Зараз використовуються "заглушки" (mock data).

    // Mock-дані для статистики
    const stats = {
        productsCount: 156,
        customersCount: 89,
        monthlyRevenue: 450000,
        activeRepairs: 12
    };
    updateStats(stats);

    // Mock-дані для останніх продажів
    const recentSales = [
        { id: 1, title: 'Intel Core i9-14900K', customer: 'Олена Вовк', date: '2024-05-20', amount: 25000 },
        { id: 2, title: 'NVIDIA RTX 4080 Super', customer: 'Андрій Коваль', date: '2024-05-19', amount: 52000 },
        { id: 3, title: '32GB DDR5 Kingston FURY', customer: 'Ірина Мельник', date: '2024-05-18', amount: 4500 }
    ];
    renderRecentSales(recentSales);

    // Mock-дані для активних ремонтів
    const activeRepairs = [
        { id: 1, title: 'Заміна термопасти MacBook Pro', customer: 'Сергій Пономар', date: '2024-05-18', status: 'Ремонтується', statusClass: 'warning' },
        { id: 2, title: 'Діагностика ПК', customer: 'Марія Сидоренко', date: '2024-05-15', status: 'Діагностика', statusClass: 'info' },
        { id: 3, title: 'Чистка ноутбука від пилу', customer: 'Віктор Бондаренко', date: '2024-05-14', status: 'Готово', statusClass: 'success' }
    ];
    renderActiveRepairs(activeRepairs);

    // Mock-дані для товарів, що закінчуються
    const lowStockProducts = [
        { id: '674f1a2b8d4c5e1234567898', title: 'ASUS ROG Strix B760-F', current: 2, min: 5 },
        { id: '674f1a2b8d4c5e1234567899', title: 'Corsair RM850x', current: 1, min: 3 },
        { id: '674f1a2b8d4c5e123456789a', title: 'Kingston FURY 64GB DDR5', current: 4, min: 8 }
    ];
    renderLowStockProducts(lowStockProducts);
}

function updateStats(stats) {
    document.querySelector('[data-stat="products-count"]').textContent = stats.productsCount;
    document.querySelector('[data-stat="customers-count"]').textContent = stats.customersCount;
    document.querySelector('[data-stat="monthly-revenue"]').textContent = PCManagement.formatCurrency(stats.monthlyRevenue, 'UAH');
    document.querySelector('[data-stat="active-repairs"]').textContent = stats.activeRepairs;
}

function renderRecentSales(sales) {
    const container = document.querySelector('#recent-sales');
    if (!container) return;

    const html = sales.map(sale => `
        <div class="operation-item">
            <div class="operation-item__info">
                <h4 class="operation-item__title">${sale.title}</h4>
                <p class="operation-item__details">${sale.customer} • ${PCManagement.formatShortDate(sale.date)}</p>
            </div>
            <div class="operation-item__amount">${PCManagement.formatCurrency(sale.amount, 'UAH')}</div>
        </div>
    `).join('');

    container.innerHTML = html;
}

function renderActiveRepairs(repairs) {
    const container = document.querySelector('#active-repairs');
    if (!container) return;

    const html = repairs.map(repair => `
        <div class="operation-item">
            <div class="operation-item__info">
                <h4 class="operation-item__title">${repair.title}</h4>
                <p class="operation-item__details">${repair.customer} • ${PCManagement.formatShortDate(repair.date)}</p>
                <span class="status-badge status-badge--${repair.statusClass}">${repair.status}</span>
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

function renderLowStockProducts(products) {
    const container = document.querySelector('#low-stock-products');
    const countEl = document.querySelector('#low-stock-count');
    if (!container || !countEl) return;

    countEl.textContent = `${products.length} позиції`;

    const html = products.map(product => `
        <div class="alert-item">
            <div class="alert-item__info">
                <h4 class="alert-item__title">${product.title}</h4>
                <p class="alert-item__details">Залишок: ${product.current} шт. (мін: ${product.min} шт.)</p>
            </div>
            <button class="btn btn--sm btn--primary" onclick="orderProduct('${product.id}')">Замовити</button>
        </div>
    `).join('');

    container.innerHTML = html;
}


function orderProduct(productId) {
    console.log('Ordering product:', productId);
    PCManagement.showNotification(`Замовлення товару ${productId}...`, 'info');
    // Тут буде логіка замовлення товару через API
    // PCManagement.apiRequest(`/api/products/${productId}/order`, { method: 'POST' });
}
// Робимо функцію глобальною, щоб її можна було викликати з HTML (onclick)
window.orderProduct = orderProduct;

function initCharts() {
    // Ініціалізація графіків (потрібна бібліотека, наприклад, Chart.js)
    // Перевіряємо, чи є Chart.js на сторінці
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded. Skipping chart initialization.');
        return;
    }

    console.log('Initializing charts...');

    // Графік продажів за тиждень
    const salesChartCtx = document.getElementById('sales-chart');
    if (salesChartCtx) {
        new Chart(salesChartCtx, {
            type: 'line',
            data: {
                labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'],
                datasets: [{
                    label: 'Продажі',
                    data: [12000, 19000, 8000, 15000, 21000, 30000, 25000],
                    borderColor: 'var(--color-primary)',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Графік категорій
    const categoriesChartCtx = document.getElementById('categories-chart');
    if (categoriesChartCtx) {
        new Chart(categoriesChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['Процесори', 'Відеокарти', 'Пам\'ять', 'Периферія'],
                datasets: [{
                    label: 'Топ категорії',
                    data: [30, 45, 15, 10],
                    backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#64748b']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}//# sourceMappingURL=dashboard.js.map
