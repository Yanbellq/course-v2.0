async function loadData() {
    const res = await fetch("/api/analytics/");
    const data = await res.json();

    buildRevenueChart(data.revenue_months, data.revenue_values);
    buildCategoryChart(data.category_labels, data.category_sales);
    buildRepairChart(data.repair_labels, data.repair_counts);
    buildCustomerChart(data.customer_labels, data.customer_counts);
}

function buildRevenueChart(labels, values) {
    new Chart(document.getElementById("revenueChart"), {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "₴ Прибуток",
                data: values,
                borderColor: "#000",
                borderWidth: 2,
                fill: false
            }]
        }
    });
}

function buildCategoryChart(labels, values) {
    new Chart(document.getElementById("categoryChart"), {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Продажі",
                data: values,
                backgroundColor: "#000"
            }]
        }
    });
}

function buildRepairChart(labels, values) {
    new Chart(document.getElementById("repairChart"), {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Ремонти",
                data: values,
                borderColor: "#000",
                borderWidth: 2
            }]
        }
    });
}

function buildCustomerChart(labels, values) {
    new Chart(document.getElementById("customerChart"), {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Нові клієнти",
                data: values,
                backgroundColor: "#000"
            }]
        }
    });
}

loadData();
//# sourceMappingURL=analytics.js.map
