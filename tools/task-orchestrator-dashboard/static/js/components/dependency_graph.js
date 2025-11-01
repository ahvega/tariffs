/**
 * Dependency Graph Component
 * Interactive task dependency visualization using Cytoscape.js
 */

class DependencyGraph {
    constructor(containerId) {
        this.containerId = containerId;
        this.cy = null;
        this.data = { nodes: [], edges: [] };
        this.layout = 'dagre';
        this.filters = {
            project: null,
            feature: null,
            status: null
        };
    }

    /**
     * Initialize the graph
     */
    async init() {
        try {
            await this.loadData();
            this.render();
            this.setupEventListeners();
            this.setupWebSocketListener();
        } catch (error) {
            console.error('Failed to initialize dependency graph:', error);
            this.showError('Failed to load dependency graph');
        }
    }

    /**
     * Load graph data from API
     */
    async loadData() {
        try {
            // Get selected project from global state
            const projectId = window.appState ? window.appState.getProjectId() : null;
            
            const dependencies = await api.getDependencies();
            const tasks = await api.getTasks();

            // Filter tasks by project if one is selected
            const filteredTasks = projectId
                ? tasks.filter(task => task.project_id === projectId)
                : tasks;

            // Build nodes from filtered tasks
            this.data.nodes = filteredTasks.map(task => ({
                data: {
                    id: task.id,
                    label: task.title,
                    status: task.status,
                    priority: task.priority,
                    complexity: task.complexity || 5,
                    feature_id: task.feature_id,
                    tags: task.tags || []
                }
            }));

            // Build edges from dependencies - only include edges between filtered tasks
            const taskIds = new Set(filteredTasks.map(t => t.id));
            this.data.edges = dependencies
                .filter(dep => taskIds.has(dep.from_task_id) && taskIds.has(dep.to_task_id))
                .map(dep => ({
                    data: {
                        id: `${dep.from_task_id}-${dep.to_task_id}`,
                        source: dep.from_task_id,
                        target: dep.to_task_id,
                        type: dep.type
                    }
                }));

            console.log(`Loaded ${this.data.nodes.length} nodes and ${this.data.edges.length} edges (project: ${projectId || 'all'})`);
        } catch (error) {
            console.error('Failed to load graph data:', error);
            throw error;
        }
    }

    /**
     * Render the graph using Cytoscape
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }

        // Destroy existing instance
        if (this.cy) {
            this.cy.destroy();
        }

        // Create Cytoscape instance
        this.cy = cytoscape({
            container: container,
            elements: [...this.data.nodes, ...this.data.edges],
            style: this.getGraphStyle(),
            layout: this.getLayoutConfig(this.layout)
        });

        // Setup interactions
        this.setupGraphInteractions();

        console.log('Graph rendered successfully');
    }

    /**
     * Get graph visual style
     */
    getGraphStyle() {
        return [
            // Node styles
            {
                selector: 'node',
                style: {
                    'background-color': (ele) => this.getStatusColor(ele.data('status')),
                    'label': 'data(label)',
                    'color': '#f1f5f9',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': '10px',
                    'width': (ele) => Math.max(30, ele.data('complexity') * 5),
                    'height': (ele) => Math.max(30, ele.data('complexity') * 5),
                    'border-width': 2,
                    'border-color': '#475569',
                    'text-wrap': 'wrap',
                    'text-max-width': '80px'
                }
            },
            // Edge styles
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#64748b',
                    'target-arrow-color': '#64748b',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'arrow-scale': 1
                }
            },
            // Edge type styles
            {
                selector: 'edge[type="BLOCKS"]',
                style: {
                    'line-color': '#ef4444',
                    'target-arrow-color': '#ef4444'
                }
            },
            {
                selector: 'edge[type="IS_BLOCKED_BY"]',
                style: {
                    'line-color': '#f59e0b',
                    'target-arrow-color': '#f59e0b'
                }
            },
            // Highlighted state
            {
                selector: 'node:selected',
                style: {
                    'border-color': '#3b82f6',
                    'border-width': 4
                }
            },
            {
                selector: 'node.highlighted',
                style: {
                    'border-color': '#10b981',
                    'border-width': 4
                }
            },
            // High priority nodes
            {
                selector: 'node[priority="high"]',
                style: {
                    'border-color': '#ef4444',
                    'border-width': 3
                }
            }
        ];
    }

    /**
     * Get layout configuration
     */
    getLayoutConfig(layoutName) {
        const layouts = {
            dagre: {
                name: 'dagre',
                rankDir: 'TB',
                animate: true,
                animationDuration: 500,
                nodeSep: 50,
                rankSep: 100
            },
            cose: {
                name: 'cose',
                animate: true,
                animationDuration: 500,
                nodeRepulsion: 400000,
                idealEdgeLength: 100
            },
            circle: {
                name: 'circle',
                animate: true,
                animationDuration: 500
            },
            grid: {
                name: 'grid',
                animate: true,
                animationDuration: 500,
                rows: Math.ceil(Math.sqrt(this.data.nodes.length))
            }
        };

        return layouts[layoutName] || layouts.dagre;
    }

    /**
     * Setup graph interactions
     */
    setupGraphInteractions() {
        // Click to show details
        this.cy.on('tap', 'node', (event) => {
            const node = event.target;
            const taskId = node.data('id');
            this.showTaskDetails(taskId);
        });

        // Hover to highlight dependencies
        this.cy.on('mouseover', 'node', (event) => {
            const node = event.target;
            const connected = node.neighborhood();

            this.cy.elements().removeClass('highlighted');
            connected.addClass('highlighted');
            node.addClass('highlighted');
        });

        this.cy.on('mouseout', 'node', () => {
            this.cy.elements().removeClass('highlighted');
        });

        // Double-click to focus
        this.cy.on('dbltap', 'node', (event) => {
            const node = event.target;
            this.cy.animate({
                fit: {
                    eles: node.closedNeighborhood(),
                    padding: 50
                },
                duration: 500
            });
        });
    }

    /**
     * Setup WebSocket listener for real-time updates
     */
    setupWebSocketListener() {
        wsClient.on('database_update', () => {
            console.log('Database updated, reloading graph...');
            this.reload();
        });

        wsClient.on('task_update', (data) => {
            console.log('Task updated:', data);
            this.updateNode(data.task_id);
        });

        // Listen for project selection changes
        window.addEventListener('project-selected', () => {
            console.log('Project changed, reloading graph...');
            this.reload();
        });
    }

    /**
     * Setup event listeners for controls
     */
    setupEventListeners() {
        // Layout selector
        const layoutSelect = document.getElementById('graph-layout');
        if (layoutSelect) {
            layoutSelect.addEventListener('change', (e) => {
                this.layout = e.target.value;
                this.applyLayout(this.layout);
            });
        }

        // Fit button
        const fitBtn = document.getElementById('graph-fit');
        if (fitBtn) {
            fitBtn.addEventListener('click', () => {
                this.fit();
            });
        }

        // Reset button
        const resetBtn = document.getElementById('graph-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.reset();
            });
        }

        // Export button
        const exportBtn = document.getElementById('graph-export');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportPNG();
            });
        }
    }

    /**
     * Apply new layout
     */
    applyLayout(layoutName) {
        if (!this.cy) return;

        const layout = this.cy.layout(this.getLayoutConfig(layoutName));
        layout.run();
    }

    /**
     * Fit graph to container
     */
    fit() {
        if (!this.cy) return;
        this.cy.fit(null, 50);
    }

    /**
     * Reset zoom and pan
     */
    reset() {
        if (!this.cy) return;
        this.cy.zoom(1);
        this.cy.center();
    }

    /**
     * Export graph as PNG
     */
    exportPNG() {
        if (!this.cy) return;

        const png = this.cy.png({
            output: 'blob',
            bg: '#0f172a',
            full: true,
            scale: 2
        });

        const url = URL.createObjectURL(png);
        const link = document.createElement('a');
        link.href = url;
        link.download = `dependency-graph-${Date.now()}.png`;
        link.click();
        URL.revokeObjectURL(url);

        Helpers.showToast('Graph exported successfully', 'success');
    }

    /**
     * Update single node
     */
    async updateNode(taskId) {
        if (!this.cy) return;

        try {
            const task = await api.getTask(taskId);
            const node = this.cy.getElementById(taskId);

            if (node.length > 0) {
                node.data({
                    label: task.title,
                    status: task.status,
                    priority: task.priority,
                    complexity: task.complexity || 5
                });

                node.style('background-color', this.getStatusColor(task.status));
            }
        } catch (error) {
            console.error('Failed to update node:', error);
        }
    }

    /**
     * Reload entire graph
     */
    async reload() {
        try {
            await this.loadData();
            this.render();
            Helpers.showToast('Graph updated', 'info');
        } catch (error) {
            console.error('Failed to reload graph:', error);
            Helpers.showToast('Failed to reload graph', 'error');
        }
    }

    /**
     * Show task details modal
     */
    showTaskDetails(taskId) {
        if (window.detailModal) {
            window.detailModal.show(taskId, 'task');
        }
    }

    /**
     * Get status color
     */
    getStatusColor(status) {
        return Formatters.statusColor(status);
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: #ef4444;">
                    <p>${message}</p>
                    <button onclick="dependencyGraph.init()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #3b82f6; color: white; border: none; border-radius: 0.375rem; cursor: pointer;">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    /**
     * Get layout configuration with safe fallbacks
     */
    getLayoutConfig(name) {
        // Prefer Dagre when available
        if (name === 'dagre') {
            if (typeof dagre !== 'undefined') {
                return {
                    name: 'dagre',
                    rankDir: 'LR',
                    nodeSep: 50,
                    edgeSep: 25,
                    rankSep: 75,
                    fit: true,
                    padding: 30
                };
            } else {
                console.warn('Dagre library not detected; using breadthfirst layout.');
                return { name: 'breadthfirst', directed: true, fit: true, padding: 30 };
            }
        }

        // Other supported layouts
        if (name === 'cose') return { name: 'cose', fit: true, padding: 30 };
        if (name === 'circle') return { name: 'circle', fit: true, padding: 30 };
        if (name === 'grid') return { name: 'grid', fit: true, padding: 30 };

        // Default
        return { name: 'breadthfirst', directed: true, fit: true, padding: 30 };
    }

    /**
     * Destroy graph instance
     */
    destroy() {
        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }
    }
}

// Create global instance (initialized in main.js)
let dependencyGraph = null;
