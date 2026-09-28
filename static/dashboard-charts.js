const currencyFormatter = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
});

function readChartData(elementId) {
    const dataElement = document.getElementById(elementId);
    return JSON.parse(dataElement.textContent);
}

function formatCurrency(value) {
    return currencyFormatter.format(value);
}

function initializeDashboardCharts() {
    if (typeof Chart === "undefined") {
        return;
    }

    const incomeExpenseData = readChartData("income-expense-data");
    const incomeExpenseCanvas = document.getElementById("income-expense-chart");

    new Chart(incomeExpenseCanvas, {
        type: "bar",
        data: {
            labels: incomeExpenseData.labels,
            datasets: [{
                data: incomeExpenseData.values,
                backgroundColor: ["#176a4b", "#a34234"],
                borderRadius: 5,
                maxBarThickness: 72,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => formatCurrency(context.raw),
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: "#687572" },
                    border: { display: false },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: "#edf0ed" },
                    ticks: {
                        color: "#87918d",
                        callback: (value) => formatCurrency(value),
                    },
                    border: { display: false },
                },
            },
        },
    });

    const expenseCategoryData = readChartData("expense-category-data");
    const nonZeroCategories = expenseCategoryData.labels
        .map((label, index) => ({ label, value: expenseCategoryData.values[index] }))
        .filter((category) => category.value > 0);
    const categoryCanvas = document.getElementById("expense-category-chart");

    if (nonZeroCategories.length === 0) {
        categoryCanvas.hidden = true;
        document.getElementById("expense-chart-empty").hidden = false;
        return;
    }

    new Chart(categoryCanvas, {
        type: "doughnut",
        data: {
            labels: nonZeroCategories.map((category) => category.label),
            datasets: [{
                data: nonZeroCategories.map((category) => category.value),
                backgroundColor: [
                    "#176a4b",
                    "#d39835",
                    "#527a96",
                    "#bb6250",
                    "#7b8e50",
                    "#826b99",
                    "#89938e",
                ],
                borderColor: "#ffffff",
                borderWidth: 3,
                hoverOffset: 5,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "62%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#687572",
                        boxWidth: 9,
                        boxHeight: 9,
                        padding: 14,
                        usePointStyle: true,
                        pointStyle: "circle",
                        font: { size: 10 },
                    },
                },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.label}: ${formatCurrency(context.raw)}`,
                    },
                },
            },
        },
    });
}

initializeDashboardCharts();