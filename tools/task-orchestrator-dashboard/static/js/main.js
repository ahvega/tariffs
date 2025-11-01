/**
 * Main Application Controller
 * Initializes all components and handles view switching
 */

class DashboardApp {
    constructor() {
        this.currentView = 'overview';
        this.components = {};
        this.isInitialized = false;
    }

    /**
     * Initialize application
     */
    async init() {
        console.log('Initializing Task Orchestrator Dashboard v2.0...');

        try {
            // Setup navigation
            this.setupNavigation();

            // Initialize global components
            this.initializeGlobalComponents();

            // Load initial view
            await this.loadView(this.currentView);

            this.isInitialized = true;
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showInitError();
        }
    }

    /**
     * Initialize global components (search, modal, etc.)
     */
    initializeGlobalComponents() {
        try {
            // Initialize search
            if (typeof Search !== 'undefined') {
                window.search = new Search('search-input', 'search-results');
                window.search.init();
            } else {
                console.warn('Search component not loaded');
            }

            // Initialize detail modal
            if (typeof DetailModal !== 'undefined') {
                window.detailModal = new DetailModal('detail-modal');
                window.detailModal.init();
            } else {
                console.warn('DetailModal component not loaded');
            }

            // Initialize refresh button
            this.setupRefreshButton();
        } catch (error) {
            console.error('Error initializing global components:', error);
        }
    }

    /**
     * Setup refresh button handler
     */
    setupRefreshButton() {
        const refreshBtn = document.getElementById('btn-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                await this.refreshDatabase();
            });
        }
    }

    /**
     * Refresh database connections and reload current view
     */
    async refreshDatabase() {
        const refreshBtn = document.getElementById('btn-refresh');
        const refreshIcon = refreshBtn.querySelector('.refresh-icon');
        
        try {
            // Add loading state
            refreshBtn.classList.add('loading');
            refreshBtn.disabled = true;
            
            console.log('Refreshing database...');
            
            // Call refresh endpoint
            const response = await fetch('/api/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('Database refreshed:', result.message);
                Helpers.showToast('Data refreshed successfully!', 'success');
                
                // Reload current view to show updated data
                await this.loadView(this.currentView);
                
                // Reload project selector if it's open
                if (window.projectSelector) {
                    window.projectSelector.loadProjects();
                }
            } else {
                console.error('Refresh failed:', result.message);
                Helpers.showToast('Failed to refresh data: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error refreshing database:', error);
            Helpers.showToast('Error refreshing data', 'error');
        } finally {
            // Remove loading state
            refreshBtn.classList.remove('loading');
            refreshBtn.disabled = false;
        }
    }

    /**
     * Setup navigation event listeners
     */
    setupNavigation() {
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const view = tab.getAttribute('data-view');
                this.switchView(view);
            });
        });
    }

    /**
     * Switch to different view
     */
    async switchView(viewName) {
        if (viewName === this.currentView) return;

        console.log(`Switching to view: ${viewName}`);

        // Update navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('data-view') === viewName) {
                tab.classList.add('active');
            }
        });

        // Update view containers
        document.querySelectorAll('.view-container').forEach(container => {
            container.classList.remove('active');
        });

        const viewContainer = document.getElementById(`${viewName}-view`);
        if (viewContainer) {
            viewContainer.classList.add('active');
        }

        this.currentView = viewName;

        // Load view content
        await this.loadView(viewName);
    }

    /**
     * Load view content
     */
    async loadView(viewName) {
        console.log(`Loading view: ${viewName}`);

        switch (viewName) {
            case 'overview':
                await this.loadOverviewView();
                break;
            case 'kanban':
                await this.loadKanbanView();
                break;
            case 'graph':
                await this.loadGraphView();
                break;
            case 'analytics':
                await this.loadAnalyticsView();
                break;
            default:
                console.warn(`Unknown view: ${viewName}`);
        }
    }

    /**
     * Load overview view
     * Overview is now managed by the CurrentProject component
     */
    async loadOverviewView() {
        // CurrentProject component handles all overview content
        // No additional loading needed here
    }

    /**
     * Load Kanban view
     */
    async loadKanbanView() {
        try {
            if (!this.components.kanban && typeof KanbanBoard !== 'undefined') {
                window.kanbanBoard = new KanbanBoard('kanban-board');
                this.components.kanban = window.kanbanBoard;
                await window.kanbanBoard.init();
            } else if (this.components.kanban) {
                await this.components.kanban.init();
            } else {
                console.warn('KanbanBoard component not loaded');
            }
        } catch (error) {
            console.error('Failed to load Kanban view:', error);
        }
    }

    /**
     * Load graph view
     */
    async loadGraphView() {
        try {
            if (!this.components.graph && typeof DependencyGraph !== 'undefined') {
                window.dependencyGraph = new DependencyGraph('dependency-graph');
                this.components.graph = window.dependencyGraph;
                await window.dependencyGraph.init();
            } else if (this.components.graph) {
                await this.components.graph.init();
            } else {
                console.warn('DependencyGraph component not loaded');
            }
        } catch (error) {
            console.error('Failed to load graph view:', error);
        }
    }

    /**
     * Load analytics view
     */
    async loadAnalyticsView() {
        try {
            if (!this.components.analytics && typeof Analytics !== 'undefined') {
                window.analytics = new Analytics();
                this.components.analytics = window.analytics;
                await window.analytics.init();
            } else if (this.components.analytics) {
                await this.components.analytics.init();
            } else {
                console.warn('Analytics component not loaded');
            }
        } catch (error) {
            console.error('Failed to load analytics view:', error);
        }
    }

    /**
     * Show initialization error
     */
    showInitError() {
        document.body.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; flex-direction: column; gap: 1rem;">
                <h1 style="color: #ef4444; font-size: 2rem;">Failed to Initialize Dashboard</h1>
                <p style="color: #cbd5e1;">Please check the console for details.</p>
                <button onclick="location.reload()" style="padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 0.5rem; cursor: pointer; font-size: 1rem;">
                    Reload
                </button>
            </div>
        `;
    }

    /**
     * Reload current view
     */
    async reload() {
        await this.loadView(this.currentView);
        Helpers.showToast('Dashboard reloaded', 'info');
    }
}

// Initialize application when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
    window.app = new DashboardApp();
    app.init();
});

// Setup auto-refresh with WebSocket
wsClient.on('database_update', () => {
    console.log('Database updated from WebSocket');
    if (window.app && window.app.isInitialized) {
        // Reload stats for all views
        if (app.currentView === 'overview') {
            app.loadStats();
        }
        // Components handle their own updates via WebSocket listeners
    }
});

// Prevent default behavior on keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Prevent Cmd+K from browser search on Mac
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
    }
});
