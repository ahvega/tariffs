/**
 * Detail Modal Component
 * Shows comprehensive entity details
 */

class DetailModal {
    constructor(modalId) {
        this.modalId = modalId;
        this.currentEntity = null;
        this.currentType = null;
        this.activeTab = 'overview';
    }

    /**
     * Initialize modal
     */
    init() {
        this.setupEventListeners();
    }

    /**
     * Show modal with entity details
     */
    async show(entityId, entityType = 'task') {
        this.currentEntity = entityId;
        this.currentType = entityType;

        const modal = document.getElementById(this.modalId);
        if (!modal) return;

        modal.classList.add('show');
        await this.loadData();
    }

    /**
     * Hide modal
     */
    hide() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.classList.remove('show');
        }
        this.currentEntity = null;
        this.currentType = null;
    }

    /**
     * Load entity data
     */
    async loadData() {
        try {
            let data;
            if (this.currentType === 'task') {
                try {
                    data = await api.getTask(this.currentEntity);
                    await this.renderTaskDetails(data);
                } catch (err) {
                    console.warn('Primary task fetch failed, attempting fallback from Kanban cache:', err);
                    const fallback = (window.kanbanBoard && Array.isArray(window.kanbanBoard.tasks))
                        ? window.kanbanBoard.tasks.find(t => t.id === this.currentEntity)
                        : null;

                    if (fallback) {
                        // Render minimal details from cached task while backend resolves
                        await this.renderTaskDetails({
                            id: fallback.id,
                            title: fallback.title || fallback.name || '(Untitled task)',
                            summary: fallback.summary || fallback.description || '',
                            status: fallback.status || 'pending',
                            priority: fallback.priority || 'medium',
                            complexity: fallback.complexity || 0,
                            created_at: fallback.created_at || null,
                            modified_at: fallback.modified_at || fallback.updated_at || null,
                            tags: fallback.tags || []
                        });

                        // Show a soft warning in the overview tab
                        const overviewTab = document.getElementById('tab-overview');
                        if (overviewTab) {
                            const note = document.createElement('div');
                            note.style.cssText = 'margin-top: 1rem; color: var(--warning); font-size: 0.875rem;';
                            note.textContent = 'Showing cached task details (live fetch failed).';
                            overviewTab.appendChild(note);
                        }
                    } else {
                        throw err; // Rethrow if no fallback available
                    }
                }
            } else if (this.currentType === 'feature') {
                data = await api.getFeature(this.currentEntity);
                await this.renderFeatureDetails(data);
            }
        } catch (error) {
            console.error('Failed to load entity details:', error);
            this.showError('Failed to load details');
        }
    }

    /**
     * Render task details
     */
    async renderTaskDetails(task) {
        document.getElementById('modal-title').textContent = task.title;

        // Overview tab
        const overviewTab = document.getElementById('tab-overview');
        overviewTab.innerHTML = `
            <div style="display: grid; gap: 1rem;">
                <div>
                    <strong>Status:</strong> ${Formatters.statusBadge(task.status)}
                </div>
                <div>
                    <strong>Priority:</strong> ${Formatters.priorityBadge(task.priority)}
                </div>
                <div>
                    <strong>Complexity:</strong> ${Formatters.complexityIndicator(task.complexity)}
                </div>
                <div>
                    <strong>Created:</strong> ${Formatters.datetime(task.created_at)}
                </div>
                <div>
                    <strong>Modified:</strong> ${Formatters.datetime(task.modified_at)}
                </div>
                <div>
                    <strong>ID:</strong>
                    <code style="background: var(--bg-tertiary); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">
                        ${task.id}
                    </code>
                    <button onclick="Helpers.copyToClipboard('${task.id}')" style="margin-left: 0.5rem; padding: 0.25rem 0.5rem; background: var(--primary); color: white; border: none; border-radius: 0.25rem; cursor: pointer; font-size: 0.75rem;">
                        Copy
                    </button>
                </div>
            </div>
        `;

        // Summary tab
        const summaryTab = document.getElementById('tab-summary');
        summaryTab.innerHTML = `
            <div style="line-height: 1.8;">
                ${task.summary ? Formatters.escapeHtml(task.summary) : '<em style="color: var(--text-secondary);">No summary available</em>'}
            </div>
        `;

        // Sections tab
        try {
            const sections = await api.getTaskSections(task.id);
            const sectionsTab = document.getElementById('tab-sections');
            if (sections && sections.length > 0) {
                sectionsTab.innerHTML = sections.map(section => `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 0.5rem;">
                        <h4 style="margin-bottom: 0.5rem;">${Formatters.escapeHtml(section.title)}</h4>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">
                            ${Formatters.escapeHtml(section.content || 'No content')}
                        </div>
                    </div>
                `).join('');
            } else {
                sectionsTab.innerHTML = '<p style="color: var(--text-secondary);">No sections available</p>';
            }
        } catch (error) {
            document.getElementById('tab-sections').innerHTML = '<p style="color: var(--danger);">Failed to load sections</p>';
        }

        // Dependencies tab
        try {
            const dependencies = await api.getTaskDependencies(task.id);
            const depsTab = document.getElementById('tab-dependencies');
            if (dependencies && dependencies.length > 0) {
                const incoming = dependencies.filter(d => d.to_task_id === task.id);
                const outgoing = dependencies.filter(d => d.from_task_id === task.id);

                depsTab.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <h4 style="color: var(--text-secondary); margin-bottom: 0.5rem;">Blocks (${outgoing.length})</h4>
                        ${outgoing.length > 0 ? outgoing.map(d => `<div style="padding: 0.5rem; background: var(--bg-tertiary); border-radius: 0.25rem; margin-bottom: 0.25rem;">${d.to_task_title || d.to_task_id}</div>`).join('') : '<p style="color: var(--text-secondary);">None</p>'}
                    </div>
                    <div>
                        <h4 style="color: var(--text-secondary); margin-bottom: 0.5rem;">Blocked By (${incoming.length})</h4>
                        ${incoming.length > 0 ? incoming.map(d => `<div style="padding: 0.5rem; background: var(--bg-tertiary); border-radius: 0.25rem; margin-bottom: 0.25rem;">${d.from_task_title || d.from_task_id}</div>`).join('') : '<p style="color: var(--text-secondary);">None</p>'}
                    </div>
                `;
            } else {
                depsTab.innerHTML = '<p style="color: var(--text-secondary);">No dependencies</p>';
            }
        } catch (error) {
            document.getElementById('tab-dependencies').innerHTML = '<p style="color: var(--danger);">Failed to load dependencies</p>';
        }

        // Tags tab
        const tagsTab = document.getElementById('tab-tags');
        if (task.tags && task.tags.length > 0) {
            tagsTab.innerHTML = task.tags.map(tag =>
                `<span class="badge-tag">${Formatters.escapeHtml(tag)}</span>`
            ).join(' ');
        } else {
            tagsTab.innerHTML = '<p style="color: var(--text-secondary);">No tags</p>';
        }
    }

    /**
     * Render feature details (simplified)
     */
    async renderFeatureDetails(feature) {
        document.getElementById('modal-title').textContent = feature.name;
        const overviewTab = document.getElementById('tab-overview');
        overviewTab.innerHTML = `
            <div>
                <strong>Status:</strong> ${Formatters.statusBadge(feature.status)}
            </div>
            <div>
                <strong>Summary:</strong> ${Formatters.escapeHtml(feature.summary || 'N/A')}
            </div>
        `;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Close button
        const closeBtn = document.getElementById('modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }

        // Close on overlay click
        const overlay = document.getElementById(this.modalId);
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.hide();
                }
            });
        }

        // Tab switching
        const tabs = document.querySelectorAll('.modal-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && overlay && overlay.classList.contains('show')) {
                this.hide();
            }
        });
    }

    /**
     * Switch active tab
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.modal-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('data-tab') === tabName) {
                tab.classList.add('active');
            }
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        const activeContent = document.getElementById(`tab-${tabName}`);
        if (activeContent) {
            activeContent.classList.add('active');
        }

        this.activeTab = tabName;
    }

    /**
     * Show error
     */
    showError(message) {
        const overviewTab = document.getElementById('tab-overview');
        if (overviewTab) {
            overviewTab.innerHTML = `<p style="color: var(--danger);">${message}</p>`;
        }
    }
}

// Create global instance
let detailModal = null;
