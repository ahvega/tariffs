/**
 * Data Formatting Utilities
 * Functions for formatting dates, numbers, and data for display
 */

const Formatters = {
    /**
     * Format ISO date string to relative time (e.g., "5 minutes ago")
     */
    relativeTime(dateString) {
        if (!dateString) return 'N/A';

        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60,
            second: 1
        };

        for (const [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            if (interval >= 1) {
                return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
            }
        }

        return 'Just now';
    },

    /**
     * Format ISO date string to readable date/time
     */
    datetime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Format date only (no time)
     */
    date(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    /**
     * Get status badge HTML
     */
    statusBadge(status) {
        const statusMap = {
            'pending': { label: 'Pending', class: 'badge-secondary' },
            'in-progress': { label: 'In Progress', class: 'badge-primary' },
            'completed': { label: 'Completed', class: 'badge-success' },
            'cancelled': { label: 'Cancelled', class: 'badge-danger' },
            'deferred': { label: 'Deferred', class: 'badge-warning' },
            'blocked': { label: 'Blocked', class: 'badge-danger' }
        };

        const config = statusMap[status] || { label: status, class: 'badge-secondary' };
        return `<span class="badge ${config.class}">${config.label}</span>`;
    },

    /**
     * Get priority badge HTML
     */
    priorityBadge(priority) {
        const priorityMap = {
            'high': { label: 'High', class: 'badge priority-high' },
            'medium': { label: 'Medium', class: 'badge priority-medium' },
            'low': { label: 'Low', class: 'badge priority-low' }
        };

        const config = priorityMap[priority] || { label: priority, class: 'badge-secondary' };
        return `<span class="${config.class}">${config.label}</span>`;
    },

    /**
     * Get complexity indicator HTML
     */
    complexityIndicator(complexity) {
        if (!complexity) return '';

        const level = complexity <= 3 ? 'low' : complexity <= 6 ? 'medium' : 'high';
        const colors = {
            low: '#10b981',
            medium: '#f59e0b',
            high: '#ef4444'
        };

        return `
            <div class="complexity-indicator" title="Complexity: ${complexity}/10">
                <span style="color: ${colors[level]}">⬤</span>
                <span style="font-size: 0.75rem">${complexity}/10</span>
            </div>
        `;
    },

    /**
     * Format tag list
     */
    tagList(tags) {
        if (!tags || tags.length === 0) return 'No tags';

        return tags.map(tag => {
            const escaped = this.escapeHtml(tag);
            return `<span class="badge badge-tag">${escaped}</span>`;
        }).join(' ');
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Truncate text to max length
     */
    truncate(text, maxLength = 100) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    /**
     * Format number with commas
     */
    number(num) {
        return num.toLocaleString('en-US');
    },

    /**
     * Format percentage
     */
    percentage(value, total) {
        if (!total) return '0%';
        const pct = (value / total * 100).toFixed(1);
        return `${pct}%`;
    },

    /**
     * Get entity type icon
     */
    entityIcon(entityType) {
        const icons = {
            'project': '📁',
            'feature': '⭐',
            'task': '📝',
            'section': '📄'
        };
        return icons[entityType] || '📋';
    },

    /**
     * Format UUID for display (shortened)
     */
    shortId(uuid) {
        if (!uuid) return '';
        return uuid.substring(0, 8);
    },

    /**
     * Get status color for styling
     */
    statusColor(status) {
        const colors = {
            'pending': '#64748b',
            'in-progress': '#3b82f6',
            'completed': '#10b981',
            'cancelled': '#94a3b8',
            'deferred': '#f59e0b',
            'blocked': '#ef4444'
        };
        return colors[status] || '#64748b';
    },

    /**
     * Get priority color for styling
     */
    priorityColor(priority) {
        const colors = {
            'high': '#ef4444',
            'medium': '#f59e0b',
            'low': '#64748b'
        };
        return colors[priority] || '#64748b';
    }
};
