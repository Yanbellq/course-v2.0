function loadDashboardData(){updateStats({productsCount:156,customersCount:89,monthlyRevenue:45e4,activeRepairs:12}),renderRecentSales([{id:1,title:"Intel Core i9-14900K",customer:"Олена Вовк",date:"2024-05-20",amount:25e3},{id:2,title:"NVIDIA RTX 4080 Super",customer:"Андрій Коваль",date:"2024-05-19",amount:52e3},{id:3,title:"32GB DDR5 Kingston FURY",customer:"Ірина Мельник",date:"2024-05-18",amount:4500}]),renderActiveRepairs([{id:1,title:"Заміна термопасти MacBook Pro",customer:"Сергій Пономар",date:"2024-05-18",status:"Ремонтується",statusClass:"warning"},{id:2,title:"Діагностика ПК",customer:"Марія Сидоренко",date:"2024-05-15",status:"Діагностика",statusClass:"info"},{id:3,title:"Чистка ноутбука від пилу",customer:"Віктор Бондаренко",date:"2024-05-14",status:"Готово",statusClass:"success"}]);renderLowStockProducts([{id:"674f1a2b8d4c5e1234567898",title:"ASUS ROG Strix B760-F",current:2,min:5},{id:"674f1a2b8d4c5e1234567899",title:"Corsair RM850x",current:1,min:3},{id:"674f1a2b8d4c5e123456789a",title:"Kingston FURY 64GB DDR5",current:4,min:8}])}function updateStats(t){document.querySelector('[data-stat="products-count"]').textContent=t.productsCount,document.querySelector('[data-stat="customers-count"]').textContent=t.customersCount,document.querySelector('[data-stat="monthly-revenue"]').textContent=PCManagement.formatCurrency(t.monthlyRevenue,"UAH"),document.querySelector('[data-stat="active-repairs"]').textContent=t.activeRepairs}function renderRecentSales(t){var e=document.querySelector("#recent-sales");e&&(t=t.map(t=>`
        <div class="operation-item">
            <div class="operation-item__info">
                <h4 class="operation-item__title">${t.title}</h4>
                <p class="operation-item__details">${t.customer} • ${PCManagement.formatShortDate(t.date)}</p>
            </div>
            <div class="operation-item__amount">${PCManagement.formatCurrency(t.amount,"UAH")}</div>
        </div>
    `).join(""),e.innerHTML=t)}function renderActiveRepairs(t){var e=document.querySelector("#active-repairs");e&&(t=t.map(t=>`
        <div class="operation-item">
            <div class="operation-item__info">
                <h4 class="operation-item__title">${t.title}</h4>
                <p class="operation-item__details">${t.customer} • ${PCManagement.formatShortDate(t.date)}</p>
                <span class="status-badge status-badge--${t.statusClass}">${t.status}</span>
            </div>
        </div>
    `).join(""),e.innerHTML=t)}function renderLowStockProducts(t){var e=document.querySelector("#low-stock-products"),a=document.querySelector("#low-stock-count");e&&a&&(a.textContent=t.length+" позиції",a=t.map(t=>`
        <div class="alert-item">
            <div class="alert-item__info">
                <h4 class="alert-item__title">${t.title}</h4>
                <p class="alert-item__details">Залишок: ${t.current} шт. (мін: ${t.min} шт.)</p>
            </div>
            <button class="btn btn--sm btn--primary" onclick="orderProduct('${t.id}')">Замовити</button>
        </div>
    `).join(""),e.innerHTML=a)}function orderProduct(t){console.log("Ordering product:",t),PCManagement.showNotification(`Замовлення товару ${t}...`,"info")}function initCharts(){var t;"undefined"==typeof Chart?console.warn("Chart.js is not loaded. Skipping chart initialization."):(console.log("Initializing charts..."),(t=document.getElementById("sales-chart"))&&new Chart(t,{type:"line",data:{labels:["Пн","Вт","Ср","Чт","Пт","Сб","Нд"],datasets:[{label:"Продажі",data:[12e3,19e3,8e3,15e3,21e3,3e4,25e3],borderColor:"var(--color-primary)",backgroundColor:"rgba(37, 99, 235, 0.1)",fill:!0,tension:.4}]},options:{responsive:!0,maintainAspectRatio:!1}}),(t=document.getElementById("categories-chart"))&&new Chart(t,{type:"doughnut",data:{labels:["Процесори","Відеокарти","Пам'ять","Периферія"],datasets:[{label:"Топ категорії",data:[30,45,15,10],backgroundColor:["#2563eb","#10b981","#f59e0b","#64748b"]}]},options:{responsive:!0,maintainAspectRatio:!1}}))}document.addEventListener("DOMContentLoaded",function(){document.querySelector(".dashboard-stats")&&(console.log("Initializing dashboard page..."),loadDashboardData(),initCharts())}),window.orderProduct=orderProduct;