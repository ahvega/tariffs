/**
 * Global Application State Manager
 * Handles project selection and context persistence
 */
class AppState {
    constructor() {
        this.selectedProjectId = null;
        this.selectedProjectName = 'All Projects';
        this.listeners = [];
        this.projects = [];
        this.loadFromStorage();
    }

    /**
     * Set the currently selected project
     */
    setProject(projectId, projectName) {
        this.selectedProjectId = projectId;
        this.selectedProjectName = projectName;
        this.saveToStorage();
        this.notify();
    }

    /**
     * Clear project selection (show all projects)
     */
    clearProject() {
        this.selectedProjectId = null;
        this.selectedProjectName = 'All Projects';
        this.saveToStorage();
        this.notify();
    }

    /**
     * Get current project ID
     */
    getProjectId() {
        return this.selectedProjectId;
    }

    /**
     * Get current project name
     */
    getProjectName() {
        return this.selectedProjectName;
    }

    /**
     * Subscribe to state changes
     */
    subscribe(callback) {
        this.listeners.push(callback);
    }

    /**
     * Notify all listeners of state change
     */
    notify() {
        this.listeners.forEach(cb => cb({
            projectId: this.selectedProjectId,
            projectName: this.selectedProjectName
        }));
    }

    /**
     * Save state to localStorage
     */
    saveToStorage() {
        try {
            localStorage.setItem('selectedProject', JSON.stringify({
                id: this.selectedProjectId,
                name: this.selectedProjectName
            }));
        } catch (error) {
            console.error('Failed to save state to localStorage:', error);
        }
    }

    /**
     * Load state from localStorage
     */
    loadFromStorage() {
        try {
            const stored = localStorage.getItem('selectedProject');
            if (stored) {
                const { id, name } = JSON.parse(stored);
                this.selectedProjectId = id;
                this.selectedProjectName = name;
            }
        } catch (error) {
            console.error('Failed to load state from localStorage:', error);
        }
    }

    /**
     * Load most recently updated project automatically
     */
    async loadMostRecentProject() {
        try {
            const projects = await api.getProjects();
            if (projects && projects.length > 0) {
                // Backend should sort by last_activity descending
                const mostRecent = projects[0];
                this.setProject(mostRecent.id, mostRecent.name);
            }
        } catch (error) {
            console.error('Failed to load recent project:', error);
        }
    }
}

// Create global instance
const appState = new AppState();
