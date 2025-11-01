/**
 * API Client for Task Orchestrator Dashboard
 * Provides a clean interface for all API endpoints
 */

const API_BASE = '';  // Same origin

class APIClient {
    constructor(baseURL = API_BASE) {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // Health & Status
    async getHealth() {
        return this.fetch('/api/health');
    }

    async getStats() {
        return this.fetch('/api/stats');
    }

    // Projects
    async getProjects() {
        return this.fetch('/api/projects');
    }

    async getProject(projectId) {
        return this.fetch(`/api/projects/${projectId}`);
    }

    // Features
    async getFeatures(projectId = null) {
        const query = projectId ? `?project_id=${projectId}` : '';
        return this.fetch(`/api/features${query}`);
    }

    async getFeature(featureId) {
        return this.fetch(`/api/features/${featureId}`);
    }

    // Tasks
    async getTasks(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/api/tasks${query ? '?' + query : ''}`);
    }

    async getTask(taskId) {
        return this.fetch(`/api/tasks/${taskId}`);
    }

    // Dependencies
    async getDependencies() {
        return this.fetch('/api/dependencies');
    }

    async getTaskDependencies(taskId) {
        return this.fetch(`/api/tasks/${taskId}/dependencies`);
    }

    async getDependencyGraph(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/api/dependency-graph${query ? '?' + query : ''}`);
    }

    // Sections
    async getSections(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/api/sections${query ? '?' + query : ''}`);
    }

    async getTaskSections(taskId) {
        return this.fetch(`/api/sections?entity_type=task&entity_id=${taskId}`);
    }

    async getFeatureSections(featureId) {
        return this.fetch(`/api/sections?entity_type=feature&entity_id=${featureId}`);
    }

    // Tags
    async getTags() {
        return this.fetch('/api/tags');
    }

    // Templates
    async getTemplates() {
        return this.fetch('/api/templates');
    }

    // Work Sessions
    async getWorkSessions() {
        return this.fetch('/api/work-sessions');
    }

    // Task Locks
    async getTaskLocks() {
        return this.fetch('/api/task-locks');
    }

    // Analytics
    async getAnalyticsOverview() {
        return this.fetch('/api/analytics/overview');
    }

    async getActivityTimeline(days = 7, entityType = null) {
        const params = { days };
        if (entityType) params.entity_type = entityType;
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/api/analytics/timeline?${query}`);
    }

    // Search
    async search(query, entityType = null) {
        const params = { q: query };
        if (entityType) params.entity_type = entityType;
        const queryString = new URLSearchParams(params).toString();
        return this.fetch(`/api/search?${queryString}`);
    }
}

// Create global instance
const api = new APIClient();
