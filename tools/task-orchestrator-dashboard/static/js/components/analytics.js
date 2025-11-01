/**
 * Analytics Component
 * Charts and metrics visualization
 */

class Analytics {
    constructor() {
        this.charts = {};
        this.data = null;
    }

    /**
     * Initialize analytics
     */
    async init() {
        try {
            await this.loadData();
            this.renderCharts();
            this.setupWebSocketListener();
        } catch (error) {
            console.error('Failed to initialize analytics:', error);
        }
    }

    /**
     * Load analytics data
     */
    async loadData() {
        try {
            this.data = await api.getAnalyticsOverview();
            console.log('Analytics data loaded:', this.data);
        } catch (error) {
            console.error('Failed to load analytics data:', error);
            throw error;
        }
    }

    /**
     * Render all charts
     */
    renderCharts() {
        this.renderStatusChart();
        this.renderPriorityChart();
        this.renderTrendChart();
        this.renderComplexityChart();
    }

    /**
     * Render status distribution pie chart
     */
    renderStatusChart() {
        const canvas = document.getElementById('status-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.charts.status) {
            this.charts.status.destroy();
        }

        const statusData = this.data?.task_status_distribution || {};
        const labels = Object.keys(statusData);
        const values = Object.values(statusData);

        this.charts.status = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#64748b',  // pending
                        '#3b82f6',  // in-progress
                        '#10b981',  // completed
                        '#94a3b8',  // cancelled
                        '#f59e0b'   // deferred
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#f1f5f9' }
                    }
                }
            }
        });
    }

    /**
     * Render priority distribution bar chart
     */
    renderPriorityChart() {
        const canvas = document.getElementById('priority-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.charts.priority) {
            this.charts.priority.destroy();
        }

        const priorityData = this.data?.task_priority_distribution || {};
        const labels = ['High', 'Medium', 'Low'];
        const values = [
            priorityData.high || 0,
            priorityData.medium || 0,
            priorityData.low || 0
        ];

        this.charts.priority = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tasks',
                    data: values,
                    backgroundColor: ['#ef4444', '#f59e0b', '#64748b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#475569' }
                    },
                    x: {
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#475569' }
                    }
                }
            }
        });
    }

    /**
     * Render completion trend line chart
     */
    renderTrendChart() {
        const canvas = document.getElementById('trend-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.charts.trend) {
            this.charts.trend.destroy();
        }

        // Mock trend data (7 days)
        const labels = ['7d ago', '6d ago', '5d ago', '4d ago', '3d ago', '2d ago', 'Yesterday'];
        const values = [2, 3, 1, 4, 2, 3, 5];  // Mock data

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Completed Tasks',
                    data: values,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f1f5f9' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#475569' }
                    },
                    x: {
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#475569' }
                    }
                }
            }
        });
    }

    /**
     * Render complexity distribution histogram
     */
    renderComplexityChart() {
        const canvas = document.getElementById('complexity-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.charts.complexity) {
            this.charts.complexity.destroy();
        }

        // Mock complexity distribution
        const labels = ['1-3', '4-6', '7-10'];
        const values = [5, 12, 8];  // Mock data

        this.charts.complexity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tasks',
                    data: values,
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#475569' }
                    },
                    x: {
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#475569' }
                    }
                }
            }
        });
    }

    /**
     * Setup WebSocket listener
     */
    setupWebSocketListener() {
        wsClient.on('database_update', () => {
            console.log('Database updated, reloading analytics...');
            this.reload();
        });
    }

    /**
     * Reload analytics
     */
    async reload() {
        try {
            await this.loadData();
            this.renderCharts();
        } catch (error) {
            console.error('Failed to reload analytics:', error);
        }
    }

    /**
     * Destroy all charts
     */
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Create global instance
let analytics = null;
