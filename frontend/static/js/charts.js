/**
 * Chart.js utility functions for Ambitious Hub
 */

// Chart configuration presets
const ChartConfigs = {
    default: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
            },
        },
    },
    
    bar: {
        ...this.default,
        scales: {
            y: {
                beginAtZero: true,
            },
        },
    },
    
    line: {
        ...this.default,
        scales: {
            y: {
                beginAtZero: true,
            },
        },
        elements: {
            line: {
                tension: 0.4,
            },
        },
    },
};

// Create a bar chart
function createBarChart(canvasId, labels, datasets, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            ...ChartConfigs.bar,
            ...options,
        },
    });
}

// Create a line chart
function createLineChart(canvasId, labels, datasets, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            ...ChartConfigs.line,
            ...options,
        },
    });
}

// Create a doughnut/pie chart
function createDoughnutChart(canvasId, labels, data, colors, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
            }],
        },
        options: {
            ...ChartConfigs.default,
            ...options,
        },
    });
}

// Update chart data
function updateChart(chart, newLabels, newDatasets) {
    if (!chart) return;
    
    chart.data.labels = newLabels;
    chart.data.datasets = newDatasets;
    chart.update();
}

// Destroy chart
function destroyChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.ChartUtils = {
        createBarChart,
        createLineChart,
        createDoughnutChart,
        updateChart,
        destroyChart,
    };
}

