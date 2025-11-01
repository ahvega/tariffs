/**
 * Current Project Component
 * 
 * Displays the currently selected project with features and tasks.
 * Replaces the Overview tab content when a project is selected.
 */

class CurrentProject {
    constructor() {
        this.container = document.getElementById('current-project-section');
        this.currentProjectId = null;
        
        this.init();
    }
    
    init() {
        // Listen for project selection changes
        window.addEventListener('project-selected', (e) => {
            this.loadProject(e.detail.projectId);
        });
        
        // Check if a project is already selected
        if (window.appState) {
            const projectId = window.appState.getProjectId();
            if (projectId) {
                this.loadProject(projectId);
            } else {
                this.showEmptyState();
            }
        } else {
            this.showEmptyState();
        }
    }
    
    async loadProject(projectId) {
        if (!projectId) {
            this.showEmptyState();
            return;
        }
        
        this.currentProjectId = projectId;
        
        try {
            this.showLoading();
            
            const response = await fetch(`/api/projects/${projectId}/overview`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.render(data);
        } catch (error) {
            console.error('Failed to load project:', error);
            this.showError(error.message);
        }
    }
    
    showLoading() {
        this.container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading project details...</p>
            </div>
        `;
    }
    
    showError(message) {
        this.container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3 class="empty-state-title">Error Loading Project</h3>
                <p class="empty-state-text">${this.escapeHtml(message)}</p>
                <button class="btn-primary" onclick="window.projectSelector.open()">
                    Select Different Project
                </button>
            </div>
        `;
    }
    
    showEmptyState() {
        this.container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📁</div>
                <h3 class="empty-state-title">No Project Selected</h3>
                <p class="empty-state-text">Select a project to view its details, features, and tasks</p>
                <button class="btn-primary" onclick="window.projectSelector.open()">
                    Select Project
                </button>
            </div>
        `;
    }
    
    render(data) {
        const { project, features, tasks, stats } = data;
        
        this.container.innerHTML = `
            <!-- Project Header -->
            <div class="current-project-header">
                <h1 class="current-project-title">${this.escapeHtml(project.name)}</h1>
                ${project.summary ? `<p class="current-project-summary">${this.escapeHtml(project.summary)}</p>` : ''}
                <div class="current-project-meta">
                    ${project.status ? `
                        <div class="meta-item">
                            <span>📊</span>
                            <span class="meta-value">${project.status}</span>
                        </div>
                    ` : ''}
                    <div class="meta-item">
                        <span>📦</span>
                        <span class="meta-value">${stats.feature_count}</span>
                        <span>features</span>
                    </div>
                    <div class="meta-item">
                        <span>✓</span>
                        <span class="meta-value">${stats.task_count}</span>
                        <span>tasks</span>
                    </div>
                    <div class="meta-item">
                        <span>🔗</span>
                        <span class="meta-value">${stats.dependency_count}</span>
                        <span>dependencies</span>
                    </div>
                    <div class="meta-item">
                        <span>📄</span>
                        <span class="meta-value">${stats.section_count}</span>
                        <span>sections</span>
                    </div>
                </div>
            </div>

            <!-- Features Section -->
            ${features.length > 0 ? `
                <div class="section-header">
                    <h2 class="section-title">Features</h2>
                </div>
                <div class="features-grid">
                    ${features.map(feature => this.renderFeatureCard(feature)).join('')}
                </div>
            ` : ''}

            <!-- Recent Tasks Section -->
            <div class="section-header">
                <h2 class="section-title">Recent Tasks</h2>
            </div>
            ${tasks.length > 0 ? `
                <div class="tasks-list">
                    ${tasks.map(task => this.renderTaskItem(task)).join('')}
                </div>
            ` : `
                <div class="empty-state">
                    <p>No tasks found in this project</p>
                </div>
            `}
        `;
    }
    
    renderFeatureCard(feature) {
        const completionRate = feature.task_count > 0
            ? Math.round((feature.completed_count / feature.task_count) * 100)
            : 0;
        
        return `
            <div class="feature-card">
                <div class="feature-card-header">
                    <h3 class="feature-card-name">${this.escapeHtml(feature.name)}</h3>
                    ${feature.status ? `<span class="feature-card-status ${feature.status}">${feature.status}</span>` : ''}
                </div>
                <div class="feature-card-progress">
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${completionRate}%"></div>
                    </div>
                    <div class="progress-text">
                        ${feature.completed_count} of ${feature.task_count} tasks completed (${completionRate}%)
                    </div>
                </div>
                <div class="feature-card-tasks">
                    <div class="task-stat">
                        <span class="text-success">✓</span>
                        <span>${feature.completed_count} completed</span>
                    </div>
                    <div class="task-stat">
                        <span class="text-primary">→</span>
                        <span>${feature.in_progress_count} in progress</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderTaskItem(task) {
        return `
            <div class="task-item" data-task-id="${task.id}">
                <div class="task-status-badge ${task.status || 'pending'}">${task.status || 'pending'}</div>
                <div class="task-title-col">${this.escapeHtml(task.title)}</div>
                ${task.feature_name ? `<div class="task-feature-col">${this.escapeHtml(task.feature_name)}</div>` : '<div></div>'}
                ${task.priority ? `<div class="task-priority-badge ${task.priority}">${task.priority}</div>` : '<div></div>'}
                ${task.complexity ? `<div class="task-complexity-badge">C:${task.complexity}</div>` : '<div></div>'}
            </div>
        `;
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.currentProject = new CurrentProject();
    });
} else {
    window.currentProject = new CurrentProject();
}
