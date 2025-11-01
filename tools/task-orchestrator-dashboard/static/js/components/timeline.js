/**
 * Timeline Component
 * Activity feed showing recent updates
 */

class Timeline {
    constructor(containerId) {
        this.containerId = containerId;
        this.events = [];
        this.days = 7;
    }

    /**
     * Initialize timeline
     */
    async init() {
        try {
            await this.loadEvents();
            this.render();
            this.setupWebSocketListener();
        } catch (error) {
            console.error('Failed to initialize timeline:', error);
            this.showError('Failed to load activity feed');
        }
    }

    /**
     * Load events from API
     */
    async loadEvents() {
        try {
            // For now, we'll create synthetic events from tasks
            // In Phase 3, we'll implement proper event tracking
            const tasks = await api.getTasks();

            // Create events from task modifications
            this.events = tasks
                .sort((a, b) => new Date(b.modified_at) - new Date(a.modified_at))
                .slice(0, 50)
                .map(task => ({
                    timestamp: task.modified_at,
                    entity_type: 'task',
                    entity_id: task.id,
                    entity_title: task.title,
                    event_type: 'modified',
                    status: task.status,
                    priority: task.priority
                }));

            console.log(`Loaded ${this.events.length} timeline events`);
        } catch (error) {
            console.error('Failed to load timeline events:', error);
            throw error;
        }
    }

    /**
     * Render timeline
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }

        if (this.events.length === 0) {
            container.innerHTML = `
                <p style="color: var(--text-secondary); text-align: center; padding: 2rem;">
                    No recent activity
                </p>
            `;
            return;
        }

        // Group events by date
        const groupedEvents = this.groupEventsByDate();

        const html = Object.entries(groupedEvents).map(([date, events]) => {
            const eventItems = events.map(event => this.renderEvent(event)).join('');
            return `
                <div class="timeline-group">
                    <h4 style="color: var(--text-secondary); font-size: 0.875rem; font-weight: 600; margin: 1rem 0 0.5rem 1rem;">
                        ${date}
                    </h4>
                    ${eventItems}
                </div>
            `;
        }).join('');

        container.innerHTML = html;

        // Add click listeners
        this.setupEventListeners();
    }

    /**
     * Group events by relative date
     */
    groupEventsByDate() {
        const grouped = {};
        const now = new Date();

        this.events.forEach(event => {
            const eventDate = new Date(event.timestamp);
            const daysDiff = Math.floor((now - eventDate) / (1000 * 60 * 60 * 24));

            let dateLabel;
            if (daysDiff === 0) {
                dateLabel = 'Today';
            } else if (daysDiff === 1) {
                dateLabel = 'Yesterday';
            } else if (daysDiff < 7) {
                dateLabel = 'This Week';
            } else {
                dateLabel = 'Earlier';
            }

            if (!grouped[dateLabel]) {
                grouped[dateLabel] = [];
            }
            grouped[dateLabel].push(event);
        });

        return grouped;
    }

    /**
     * Render single event
     */
    renderEvent(event) {
        const icon = Formatters.entityIcon(event.entity_type);
        const time = Formatters.relativeTime(event.timestamp);
        const statusBadge = Formatters.statusBadge(event.status);

        return `
            <div class="timeline-event" data-entity-id="${event.entity_id}" data-entity-type="${event.entity_type}">
                <div class="event-time">${time}</div>
                <div class="event-content">
                    <div class="event-title">
                        ${icon} ${Formatters.escapeHtml(event.entity_title)}
                    </div>
                    <div class="event-description">
                        ${this.getEventDescription(event)} ${statusBadge}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get event description
     */
    getEventDescription(event) {
        switch (event.event_type) {
            case 'created':
                return 'Task created';
            case 'modified':
                return 'Task updated';
            case 'status_changed':
                return `Status changed to ${event.status}`;
            case 'priority_changed':
                return `Priority changed to ${event.priority}`;
            default:
                return 'Updated';
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const eventElements = document.querySelectorAll('.timeline-event');
        eventElements.forEach(element => {
            element.addEventListener('click', () => {
                const entityId = element.getAttribute('data-entity-id');
                const entityType = element.getAttribute('data-entity-type');
                this.showDetails(entityId, entityType);
            });
        });
    }

    /**
     * Setup WebSocket listener
     */
    setupWebSocketListener() {
        wsClient.on('database_update', () => {
            console.log('Database updated, reloading timeline...');
            this.reload();
        });

        wsClient.on('task_update', (data) => {
            console.log('Task updated, reloading timeline...');
            this.reload();
        });
    }

    /**
     * Reload timeline
     */
    async reload() {
        try {
            await this.loadEvents();
            this.render();
        } catch (error) {
            console.error('Failed to reload timeline:', error);
        }
    }

    /**
     * Show entity details
     */
    showDetails(entityId, entityType) {
        if (window.detailModal) {
            window.detailModal.show(entityId, entityType);
        }
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
                </div>
            `;
        }
    }
}

// Create global instance (initialized in main.js)
let timeline = null;
