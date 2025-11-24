// Зберігаємо посилання на графіки
let revenueChart = null;
let categoryChart = null;
let repairChart = null;
let customerChart = null;

async function loadData() {
    try {
        // Отримуємо токен з cookies
        const getCookie = (name) => {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return null;
        };
        
        const token = getCookie('access_token');
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const res = await fetch("/api/analytics/", {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });
        
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            console.error("API Error:", res.status, errorData);
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();

        console.log("Analytics data received:", data);
        
        // Завжди будуємо графіки, навіть якщо дані порожні
        buildRevenueChart(data.revenue_months || [], data.revenue_values || []);
        buildCategoryChart(data.category_labels || [], data.category_sales || []);
        buildRepairChart(data.repair_labels || [], data.repair_counts || []);
        buildCustomerChart(data.customer_labels || [], data.customer_counts || []);
    } catch (error) {
        console.error("Error loading analytics data:", error);
        // Показуємо порожні графіки
        buildRevenueChart([], []);
        buildCategoryChart([], []);
        buildRepairChart([], []);
        buildCustomerChart([], []);
    }
}

function buildRevenueChart(labels, values) {
    const ctx = document.getElementById("revenueChart");
    if (!ctx) {
        console.warn("Revenue chart canvas not found");
        return;
    }
    
    // Видаляємо старий графік, якщо він існує
    if (revenueChart) {
        revenueChart.destroy();
    }
    
    revenueChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels || [],
            datasets: [{
                label: "Revenue ($)",
                data: values || [],
                borderColor: "#000",
                borderWidth: 2,
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function buildCategoryChart(labels, values) {
    const ctx = document.getElementById("categoryChart");
    if (!ctx) {
        console.warn("Category chart canvas not found");
        return;
    }
    
    // Видаляємо старий графік, якщо він існує
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels || [],
            datasets: [{
                label: "Sales",
                data: values || [],
                backgroundColor: "#000"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function buildRepairChart(labels, values) {
    const ctx = document.getElementById("repairChart");
    if (!ctx) {
        console.warn("Repair chart canvas not found");
        return;
    }
    
    // Видаляємо старий графік, якщо він існує
    if (repairChart) {
        repairChart.destroy();
    }
    
    repairChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels || [],
            datasets: [{
                label: "Repairs",
                data: values || [],
                backgroundColor: "#000",
                borderColor: "#000",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function buildCustomerChart(labels, values) {
    const ctx = document.getElementById("customerChart");
    if (!ctx) {
        console.warn("Customer chart canvas not found");
        return;
    }
    
    // Видаляємо старий графік, якщо він існує
    if (customerChart) {
        customerChart.destroy();
    }
    
    customerChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels || [],
            datasets: [{
                label: "New Customers",
                data: values || [],
                backgroundColor: "#000"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Wait for Chart.js to load and DOM to be ready
let waitAttempts = 0;
const MAX_WAIT_ATTEMPTS = 50; // Максимум 5 секунд (50 * 100ms)

function waitForChart() {
    waitAttempts++;
    
    if (waitAttempts > MAX_WAIT_ATTEMPTS) {
        console.error("Chart.js failed to load after", MAX_WAIT_ATTEMPTS * 100, "ms");
        console.error("Chart.js available:", typeof Chart !== 'undefined');
        return;
    }
    
    if (typeof Chart !== 'undefined') {
        console.log("Chart.js loaded successfully");
        
        // Перевіряємо, чи всі canvas елементи готові
        const canvases = [
            document.getElementById("revenueChart"),
            document.getElementById("categoryChart"),
            document.getElementById("repairChart"),
            document.getElementById("customerChart")
        ];
        
        const missingCanvases = canvases.filter(canvas => canvas === null);
        
        if (missingCanvases.length === 0) {
            console.log("All canvas elements found, loading data...");
            loadData();
        } else {
            console.log("Waiting for canvas elements...", missingCanvases.length, "missing");
            // Якщо canvas ще не готові, чекаємо трохи
            setTimeout(waitForChart, 100);
        }
    } else {
        // Retry after a short delay
        if (waitAttempts % 10 === 0) {
            console.log("Waiting for Chart.js to load... attempt", waitAttempts);
        }
        setTimeout(waitForChart, 100);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log("DOM loaded, waiting for Chart.js...");
        waitForChart();
    });
} else {
    console.log("DOM already ready, waiting for Chart.js...");
    waitForChart();
}

//# sourceMappingURL=analytics.js.map
