/**
 * Project Selector Component
 * 
 * Displays a modal with a grid of all projects.
 * Clicking a project updates the global app state and closes the modal.
 */

class ProjectSelector {
    constructor() {
        this.modal = document.getElementById('project-selector-modal');
        this.closeBtn = document.getElementById('project-selector-close');
        this.projectGrid = document.getElementById('project-grid');
        this.openBtn = document.getElementById('btn-project-selector');
        this.currentProjectName = document.getElementById('current-project-name');
        
        this.projects = [];
        
        this.init();
    }
    
    init() {
        // Bind events
        this.openBtn.addEventListener('click', () => this.open());
        this.closeBtn.addEventListener('click', () => this.close());
        
        // Close on overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                this.close();
            }
        });
        
        // Listen for project changes from AppState
        if (window.appState) {
            window.appState.subscribe((state) => {
                this.updateCurrentProjectDisplay(state.projectName);
            });
            
            // Set initial display if project already selected
            const currentName = window.appState.getProjectName();
            if (currentName) {
                this.updateCurrentProjectDisplay(currentName);
            }
        }
    }
    
    async open() {
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        await this.loadProjects();
    }
    
    close() {
        this.modal.classList.remove('show');
        document.body.style.overflow = '';
    }
    
    updateCurrentProjectDisplay(projectName) {
        if (projectName) {
            this.currentProjectName.textContent = projectName;
            this.openBtn.style.borderColor = 'var(--primary)';
        } else {
            this.currentProjectName.textContent = 'Select Project';
            this.openBtn.style.borderColor = 'var(--border)';
        }
    }
    
    async loadProjects() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/projects/summary');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.projects = data.projects || [];
            
            this.render();
        } catch (error) {
            console.error('Failed to load projects:', error);
            this.showError(error.message);
        }
    }
    
    showLoading() {
        this.projectGrid.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading projects...</p>
            </div>
        `;
    }
    
    showError(message) {
        this.projectGrid.innerHTML = `
            <div class="loading">
                <p style="color: var(--danger);">❌ Error loading projects</p>
                <p style="font-size: 0.875rem; color: var(--text-secondary);">${message}</p>
            </div>
        `;
    }
    
    render() {
        if (this.projects.length === 0) {
            this.projectGrid.innerHTML = `
                <div class="loading">
                    <p>No projects found</p>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">
                        Create a project using the Task Orchestrator MCP tools
                    </p>
                </div>
            `;
            return;
        }
        
        const currentProjectId = window.appState?.getProjectId();
        
        this.projectGrid.innerHTML = this.projects.map(project => `
            <div class="project-card" 
                 data-project-id="${project.id}"
                 data-project-name="${this.escapeHtml(project.name)}"
                 ${project.id === currentProjectId ? 'style="border-color: var(--primary);"' : ''}>
                <div class="project-card-header">
                    <h3 class="project-card-name">${this.escapeHtml(project.name)}</h3>
                    ${project.status ? `<span class="project-card-status ${project.status}">${project.status}</span>` : ''}
                </div>
                <div class="project-card-stats">
                    <div class="project-card-stat">
                        <span>📦</span>
                        <span class="project-card-stat-value">${project.feature_count || 0}</span>
                        <span>features</span>
                    </div>
                    <div class="project-card-stat">
                        <span>✓</span>
                        <span class="project-card-stat-value">${project.task_count || 0}</span>
                        <span>tasks</span>
                    </div>
                </div>
                <div class="project-card-date">
                    Updated ${this.formatDate(project.modified_at || project.created_at)}
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        this.projectGrid.querySelectorAll('.project-card').forEach(card => {
            card.addEventListener('click', () => {
                const projectId = card.dataset.projectId;
                const projectName = card.dataset.projectName;
                this.selectProject(projectId, projectName);
            });
        });
    }
    
    selectProject(projectId, projectName) {
        // Update global state
        if (window.appState) {
            window.appState.setProject(projectId, projectName);
        }
        
        // Close modal
        this.close();
        
        // Dispatch custom event for other components to react
        window.dispatchEvent(new CustomEvent('project-selected', {
            detail: { projectId, projectName }
        }));
        
        console.log(`Project selected: ${projectName} (${projectId})`);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        
        try {
            const date = new Date(dateStr);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
            });
        } catch (e) {
            return dateStr;
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.projectSelector = new ProjectSelector();
    });
} else {
    window.projectSelector = new ProjectSelector();
}
