/**
 * Search Component
 * Global search with autocomplete
 */

class Search {
    constructor(inputId, resultsId) {
        this.inputId = inputId;
        this.resultsId = resultsId;
        this.debounceTimer = null;
        this.results = [];
    }

    /**
     * Initialize search
     */
    init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const input = document.getElementById(this.inputId);
        if (!input) return;

        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length >= 2) {
                this.debouncedSearch(query);
            } else {
                this.hideResults();
            }
        });

        input.addEventListener('focus', (e) => {
            if (e.target.value.trim().length >= 2) {
                this.showResults();
            }
        });

        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideResults();
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+K or Cmd+K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const input = document.getElementById(this.inputId);
                if (input) {
                    input.focus();
                    input.select();
                }
            }

            // Escape to clear search
            if (e.key === 'Escape') {
                const input = document.getElementById(this.inputId);
                if (input === document.activeElement) {
                    input.value = '';
                    this.hideResults();
                }
            }
        });
    }

    /**
     * Debounced search
     */
    debouncedSearch(query) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }

    /**
     * Perform search
     */
    async performSearch(query) {
        try {
            this.results = await api.search(query);
            this.renderResults();
            this.showResults();
        } catch (error) {
            console.error('Search failed:', error);
            this.showError();
        }
    }

    /**
     * Render results
     */
    renderResults() {
        const container = document.getElementById(this.resultsId);
        if (!container) return;

        if (this.results.length === 0) {
            container.innerHTML = '<div style="padding: 1rem; color: var(--text-secondary);">No results found</div>';
            return;
        }

        const html = this.results.slice(0, 10).map(result => {
            const icon = Formatters.entityIcon(result.entity_type);
            return `
                <div class="search-result-item" data-id="${result.id}" data-type="${result.entity_type}" style="padding: 0.75rem; cursor: pointer; border-bottom: 1px solid var(--border);">
                    <div style="font-weight: 600;">${icon} ${Formatters.escapeHtml(result.title || result.name)}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                        ${result.entity_type} ${result.status ? '• ' + result.status : ''}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;

        // Add click listeners
        container.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = item.getAttribute('data-id');
                const type = item.getAttribute('data-type');
                this.selectResult(id, type);
            });
        });
    }

    /**
     * Show results dropdown
     */
    showResults() {
        const container = document.getElementById(this.resultsId);
        if (container) {
            container.classList.add('show');
        }
    }

    /**
     * Hide results dropdown
     */
    hideResults() {
        const container = document.getElementById(this.resultsId);
        if (container) {
            container.classList.remove('show');
        }
    }

    /**
     * Select result
     */
    selectResult(id, type) {
        this.hideResults();
        if (window.detailModal) {
            window.detailModal.show(id, type);
        }
    }

    /**
     * Show error
     */
    showError() {
        const container = document.getElementById(this.resultsId);
        if (container) {
            container.innerHTML = '<div style="padding: 1rem; color: var(--danger);">Search failed</div>';
            this.showResults();
        }
    }
}
