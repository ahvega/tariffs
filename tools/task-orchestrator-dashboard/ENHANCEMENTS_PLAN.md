# Task Orchestrator Dashboard - Project Context Enhancement Plan

**Version:** 1.0  
**Date:** November 1, 2025  
**Status:** Planning Phase  
**Estimated Effort:** 16-24 hours  

---

## 🎬 Meta-Project: Self-Tracking Inception

**Date Created:** 2025-11-01  
**Status:** Active Development  
**Project ID:** `7c39484d-6cea-4d8c-b1bd-dc2466a97303`

### The Inception Moment

The Task Orchestrator Dashboard now tracks its own development using the MCP Task Orchestrator system it visualizes! This meta-project demonstrates the power and flexibility of the system by creating a complete project structure for the dashboard's development.

**What Was Created:**
- ✅ **Project:** "Task Orchestrator Dashboard"
- ✅ **6 Features** representing development phases (Phases 1-6)
- ✅ **8 Tasks** across Phases 3, 4, and 6
- ✅ Complete project structure with priorities and complexity ratings

**Development Phases Tracked:**

1. **Phase 1: Real-Time Infrastructure** (COMPLETED)
   - Docker volume detection & read-only immutable mode
   - WebSocket real-time updates
   - Database connection pooling

2. **Phase 2: Project Selector & Context** (COMPLETED)
   - Project selector modal
   - Context switching & state management
   - Route ordering fixes & UUID BLOB comparisons

3. **Phase 3: Enhanced Visualization** (PLANNING) - 4 Tasks
   - Drag-and-drop Kanban board
   - D3.js interactive dependency graph
   - Timeline zoom/pan controls
   - Task detail modal with inline editing

4. **Phase 4: Analytics & Reporting** (PLANNING) - 2 Tasks
   - Velocity tracking & burndown charts
   - Complexity analysis dashboard

5. **Phase 5: Search & Filtering** (PLANNING)
   - Fuzzy matching & multi-criteria filters
   - Global cross-project search

6. **Phase 6: Production Deployment** (PLANNING) - 1 Task
   - Comprehensive test suite (pytest, 80%+ coverage)

**The Inception Loop:**

_"We have to go deeper..."_ - The dashboard can now:
- See its own development in the project selector
- Track its features in Kanban view
- Visualize its task dependencies in the graph view
- Monitor its progress in analytics

This perfect meta-loop demonstrates the system's capability to manage complex software projects with multiple phases, features, and interdependent tasks.

**Documentation:** See `META_PROJECT.md` for complete technical details and project structure.

---

## Executive Summary

This plan outlines enhancements to enable project-scoped viewing and navigation in the Task Orchestrator Dashboard. Currently, the dashboard shows all data globally without project context. These enhancements will allow users to:

1. Select a specific project to focus on
2. View project-specific statistics and progress
3. Filter all views (Overview, Kanban, Graph, Analytics) by selected project
4. Track recent activity with project context
5. Navigate seamlessly between projects

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Enhancement Requirements](#enhancement-requirements)
3. [Architecture Overview](#architecture-overview)
4. [Implementation Phases](#implementation-phases)
5. [Detailed Implementation](#detailed-implementation)
6. [Testing Strategy](#testing-strategy)
7. [Rollback Plan](#rollback-plan)

---

## Current State Analysis

### Existing Architecture

**Backend (server_v2.py):**
- FastAPI server with WebSocket support
- SQLite database via connection pool
- Project, Feature, Task models defined
- `/api/projects` endpoint exists but underutilized
- Stats endpoint returns global aggregates

**Frontend (Static JS):**
- Single-page application with tab navigation
- No global state management for project context
- All views load data globally
- Modular component architecture (Search, DetailModal, Timeline, Kanban, Graph, Analytics)

### Current Data Flow

```
Dashboard Init → API.getStats() → Display Global Stats
Tab Switch → Load Tab Data (all projects) → Render View
```

### Limitations

1. **No Project Filtering:** All data displayed globally
2. **No Project Context:** Users can't focus on specific projects
3. **No Project Selection UI:** No way to choose a project
4. **No Activity Context:** Timeline doesn't show which project activities belong to
5. **Graph Overflow:** Dependency graph doesn't fit screen properly

---

## Enhancement Requirements

### 1. Project Selector Modal

**Location:** Overview tab, Projects stat card  
**Trigger:** Click on Projects card or "Select Project" button  

**UI Specifications:**
- Modal popup (similar to task detail modal)
- Grid/table display with columns:
  - Project Name (clickable)
  - Features Count
  - Tasks Count
  - Progress % (calculated from completed tasks)
  - Last Updated (datetime)
- Sorting: Default by last updated (descending)
- Responsive design for mobile/tablet
- Close on selection or cancel button

**Behavior:**
- Clicking project name selects that project
- Selected project stored in localStorage
- Modal closes automatically on selection
- Dashboard refreshes with project context
- Visual indication of currently selected project

---

### 2. Current Project Section (Overview Tab)

**Location:** Overview tab, below stats cards, above Recent Activity

**Layout Structure:**
```
┌─────────────────────────────────────────┐
│  Current Project: [Project Name]        │  ← Subheader
├─────────────────────────────────────────┤
│  Features (5 of 8 completed - 62.5%)    │
│  ┌─────────────────────┬──────┬──────┐  │
│  │ Feature Name        │ Tasks│ Done │  │
│  ├─────────────────────┼──────┼──────┤  │
│  │ User Authentication │  12  │  75% │  │
│  │ Payment Processing  │   8  │  50% │  │
│  └─────────────────────┴──────┴──────┘  │
│                                          │
│  Tasks: 45 total (20 pending, 15 in-    │
│         progress, 10 completed)          │
│  Dependencies: 12 active                 │
│  Sections: 28 documentation blocks       │
└─────────────────────────────────────────┘
```

**Data Display:**
- Project name as prominent subheader
- Features list with:
  - Feature name
  - Task count
  - Completion percentage
  - Status indicator (planning/in-development/completed)
- Task summary by status
- Dependencies count
- Sections count
- Visual progress indicators

**Default Behavior:**
- Auto-select most recently updated project on first load
- If no projects exist, show "No projects available" message
- If project is deleted, revert to default (most recent)

---

### 3. Recent Activity Grid

**Location:** Overview tab, below Current Project section

**Current State:**
- Timeline component shows cards with limited information
- No project context in activity items

**Enhanced Layout:**
```
┌────────────┬─────────────────┬──────────────┬───────────────┐
│ Date/Time  │ Project         │ Task         │ Action        │
├────────────┼─────────────────┼──────────────┼───────────────┤
│ 11/01 14:30│ MyApp Frontend  │ Implement... │ Created       │
│ 11/01 13:45│ MyApp Backend   │ Setup API    │ Completed     │
│ 11/01 12:20│ MyApp Frontend  │ Design UI    │ Status Changed│
│ 11/01 11:10│ MyApp Backend   │ Database...  │ Updated       │
└────────────┴─────────────────┴──────────────┴───────────────┘
```

**Specifications:**
- **Date/Time Column:** Short format (MM/DD HH:mm)
- **Project Column:** Project name (truncate if long)
- **Task Column:** Task title (truncate with ellipsis)
- **Action Column:** Type of change
  - `Created` - New task created
  - `Updated` - Task modified
  - `Completed` - Status changed to completed
  - `Status Changed` - Status transition
  - `Assigned` - Feature/project assignment
- **Row Limit:** Show last 20 activities by default
- **Clickable Rows:** Click to open task detail modal
- **Color Coding:** Action types have different colors
  - Created: Blue
  - Completed: Green
  - Updated: Gray
  - Status Changed: Orange

**Data Requirements:**
- Enhanced timeline endpoint with project information
- Activity tracking for task lifecycle events
- Proper datetime formatting utilities

---

### 4. Graph Fit-to-Screen

**Location:** Graph tab

**Current Issue:**
- Graph may overflow container
- Not properly fitted to viewport
- Users must scroll to see full graph

**Enhancements:**
```javascript
// Cytoscape layout configuration
cy.layout({
  name: 'dagre',
  rankDir: 'TB',
  fit: true,              // ✓ Fit to container
  padding: 30,            // ✓ Padding from edges
  animate: false,         // Performance
  boundingBox: undefined, // Use full container
  nodeDimensionsIncludeLabels: true
}).run();

// Add window resize handler
window.addEventListener('resize', () => {
  cy.fit(cy.elements(), 30); // Refit on resize
});
```

**Specifications:**
- Default layout: Grid or Dagre with `fit: true`
- Proper viewport configuration
- Zoom controls remain functional
- Resize handler for responsive behavior
- Optional zoom-to-fit button

---

### 5. Project Name Subtitle on All Tabs

**Location:** Below navigation tabs, above content on all views

**Layout:**
```
┌────────────────────────────────────────────────┐
│  [Overview] [Kanban] [Graph] [Analytics]       │  ← Nav Tabs
├────────────────────────────────────────────────┤
│  📁 Current Project: MyApp Frontend            │  ← Subtitle
├────────────────────────────────────────────────┤
│  [Tab Content Here]                            │
```

**Specifications:**
- Fixed position below nav tabs
- Consistent styling across all tabs
- Icon prefix (📁 or project icon)
- Project name with link to change project
- "All Projects" text if no project selected
- Subtle background to distinguish from content

**Styling:**
```css
.project-subtitle {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  padding: 0.75rem 2rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.project-subtitle .project-name {
  color: var(--primary);
  font-weight: 600;
  cursor: pointer;
}

.project-subtitle .project-name:hover {
  text-decoration: underline;
}
```

---

## Architecture Overview

### Component Structure

```
Dashboard App
├── Global State (AppState)
│   ├── selectedProjectId
│   ├── selectedProjectName
│   └── projectCache
├── Components
│   ├── ProjectSelector (NEW)
│   │   ├── ProjectList
│   │   └── ProjectCard
│   ├── ProjectSubtitle (NEW)
│   ├── CurrentProjectSection (NEW)
│   ├── EnhancedTimeline (MODIFIED)
│   ├── Overview (MODIFIED)
│   ├── Kanban (MODIFIED)
│   ├── Graph (MODIFIED)
│   └── Analytics (MODIFIED)
└── Services
    ├── API Client (MODIFIED)
    └── StorageManager (NEW)
```

### Data Flow

```
User Action → Project Selection
     ↓
Update AppState (localStorage + memory)
     ↓
Emit project-change event
     ↓
All views listen and reload with project filter
     ↓
API requests include ?project_id=xxx parameter
     ↓
Backend filters data by project
     ↓
Render filtered data
```

### State Management

**AppState (New Global State Manager):**
```javascript
class AppState {
  constructor() {
    this.selectedProjectId = null;
    this.selectedProjectName = 'All Projects';
    this.listeners = [];
    this.loadFromStorage();
  }

  setProject(projectId, projectName) {
    this.selectedProjectId = projectId;
    this.selectedProjectName = projectName;
    this.saveToStorage();
    this.notify();
  }

  clearProject() {
    this.selectedProjectId = null;
    this.selectedProjectName = 'All Projects';
    this.saveToStorage();
    this.notify();
  }

  getProjectId() {
    return this.selectedProjectId;
  }

  getProjectName() {
    return this.selectedProjectName;
  }

  subscribe(callback) {
    this.listeners.push(callback);
  }

  notify() {
    this.listeners.forEach(cb => cb({
      projectId: this.selectedProjectId,
      projectName: this.selectedProjectName
    }));
  }

  saveToStorage() {
    localStorage.setItem('selectedProject', JSON.stringify({
      id: this.selectedProjectId,
      name: this.selectedProjectName
    }));
  }

  loadFromStorage() {
    const stored = localStorage.getItem('selectedProject');
    if (stored) {
      const { id, name } = JSON.parse(stored);
      this.selectedProjectId = id;
      this.selectedProjectName = name;
    }
  }
}
```

---

## Implementation Phases

### Phase 1: Backend API Enhancements (4-6 hours)

**Objective:** Add project-scoped endpoints and enhanced activity data

**Tasks:**

1. **Add Project Stats Endpoint**
   - File: `server_v2.py`
   - Endpoint: `/api/projects/{project_id}/stats`
   - Returns: Features count, tasks by status, completion %, dependencies, sections
   ```python
   @app.get("/api/projects/{project_id}/stats")
   async def get_project_stats(project_id: str):
       pool = get_db_pool()
       with pool.get_connection() as conn:
           # Query features for project
           # Query tasks for project
           # Calculate completion rate
           # Count dependencies
           # Count sections
           return {
               "features": {...},
               "tasks": {...},
               "completion_rate": float,
               "dependencies": int,
               "sections": int
           }
   ```

2. **Enhance Projects List Endpoint**
   - File: `server_v2.py`
   - Endpoint: `/api/projects` (enhance existing)
   - Add computed fields:
     - `features_count`
     - `tasks_count`
     - `completion_rate`
     - `last_activity` (most recent task update)
   ```python
   @app.get("/api/projects")
   async def get_projects_with_stats():
       pool = get_db_pool()
       with pool.get_connection() as conn:
           projects = []
           for project in get_all_projects(conn):
               project['features_count'] = count_features(conn, project['id'])
               project['tasks_count'] = count_tasks(conn, project['id'])
               project['completion_rate'] = calc_completion(conn, project['id'])
               project['last_activity'] = get_last_activity(conn, project['id'])
               projects.append(project)
           return sorted(projects, key=lambda x: x['last_activity'], reverse=True)
   ```

3. **Enhance Activity Timeline Endpoint**
   - File: `server_v2.py`
   - Endpoint: `/api/analytics/timeline` (enhance existing)
   - Add project information to each activity
   - Add action type classification
   ```python
   @app.get("/api/analytics/timeline")
   async def get_activity_timeline(
       days: int = 7,
       project_id: Optional[str] = None
   ):
       pool = get_db_pool()
       with pool.get_connection() as conn:
           activities = []
           query = """
               SELECT 
                   t.id, t.title, t.modified_at,
                   t.status, t.created_at,
                   p.name as project_name, p.id as project_id,
                   f.name as feature_name
               FROM tasks t
               LEFT JOIN features f ON t.feature_id = f.id
               LEFT JOIN projects p ON f.project_id = p.id OR t.project_id = p.id
               WHERE t.modified_at >= datetime('now', ?)
           """
           params = [f'-{days} days']
           
           if project_id:
               query += " AND (p.id = ? OR t.project_id = ?)"
               params.extend([project_id, project_id])
               
           query += " ORDER BY t.modified_at DESC LIMIT 50"
           
           rows = conn.execute(query, params).fetchall()
           
           for row in rows:
               action_type = determine_action_type(row)
               activities.append({
                   'task_id': row['id'],
                   'task_title': row['title'],
                   'project_name': row['project_name'] or 'No Project',
                   'project_id': row['project_id'],
                   'feature_name': row['feature_name'],
                   'timestamp': row['modified_at'],
                   'action': action_type
               })
           
           return activities
   ```

4. **Update Stats Endpoint for Project Filtering**
   - File: `server_v2.py`
   - Endpoint: `/api/stats?project_id=xxx`
   - Make stats project-aware
   ```python
   @app.get("/api/stats")
   async def get_stats(project_id: Optional[str] = None):
       pool = get_db_pool()
       with pool.get_connection() as conn:
           if project_id:
               # Return project-specific stats
               return get_project_specific_stats(conn, project_id)
           else:
               # Return global stats (existing behavior)
               return get_global_stats(conn)
   ```

5. **Add Project Features Endpoint**
   - File: `server_v2.py`
   - Endpoint: `/api/projects/{project_id}/features`
   - Returns features with task summaries
   ```python
   @app.get("/api/projects/{project_id}/features")
   async def get_project_features(project_id: str):
       pool = get_db_pool()
       with pool.get_connection() as conn:
           features = get_features_for_project(conn, project_id)
           for feature in features:
               feature['tasks'] = get_tasks_summary(conn, feature['id'])
               feature['completion_rate'] = calc_feature_completion(conn, feature['id'])
           return features
   ```

**Testing:**
- Test all new endpoints with Postman/curl
- Verify project_id filtering works correctly
- Check performance with multiple projects
- Validate response schemas

---

### Phase 2: Global State Management (2-3 hours)

**Objective:** Create centralized state management for project context

**Tasks:**

1. **Create AppState Class**
   - File: `static/js/utils/app-state.js` (NEW)
   - Implement state management with localStorage persistence
   - Event system for state changes
   ```javascript
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

       // ... (implementation as shown in Architecture Overview)

       async loadMostRecentProject() {
           try {
               const projects = await api.getProjects();
               if (projects && projects.length > 0) {
                   const mostRecent = projects[0]; // Already sorted by backend
                   this.setProject(mostRecent.id, mostRecent.name);
               }
           } catch (error) {
               console.error('Failed to load recent project:', error);
           }
       }
   }

   // Create global instance
   const appState = new AppState();
   ```

2. **Update API Client**
   - File: `static/js/utils/api.js`
   - Add project context to requests
   ```javascript
   class APIClient {
       // ... existing code ...

       // Add helper to include project context
       getProjectContext() {
           if (window.appState && window.appState.getProjectId()) {
               return { project_id: window.appState.getProjectId() };
           }
           return {};
       }

       // Enhanced methods with project filtering
       async getStats(projectId = null) {
           const pid = projectId || (window.appState ? window.appState.getProjectId() : null);
           return this.fetch(`/api/stats${pid ? `?project_id=${pid}` : ''}`);
       }

       async getProjectStats(projectId) {
           return this.fetch(`/api/projects/${projectId}/stats`);
       }

       async getProjectFeatures(projectId) {
           return this.fetch(`/api/projects/${projectId}/features`);
       }

       async getProjectsWithStats() {
           return this.fetch('/api/projects');
       }

       async getActivityTimeline(days = 7, projectId = null) {
           const pid = projectId || (window.appState ? window.appState.getProjectId() : null);
           const params = new URLSearchParams({ days: days.toString() });
           if (pid) params.append('project_id', pid);
           return this.fetch(`/api/analytics/timeline?${params.toString()}`);
       }

       // Update existing methods to respect project context
       async getTasks(params = {}) {
           const projectParams = { ...params, ...this.getProjectContext() };
           const query = new URLSearchParams(projectParams).toString();
           return this.fetch(`/api/tasks${query ? '?' + query : ''}`);
       }

       async getFeatures(projectId = null) {
           const pid = projectId || (window.appState ? window.appState.getProjectId() : null);
           const query = pid ? `?project_id=${pid}` : '';
           return this.fetch(`/api/features${query}`);
       }

       async getDependencyGraph(params = {}) {
           const projectParams = { ...params, ...this.getProjectContext() };
           const query = new URLSearchParams(projectParams).toString();
           return this.fetch(`/api/dependency-graph${query ? '?' + query : ''}`);
       }
   }
   ```

3. **Initialize State on App Load**
   - File: `static/js/main.js`
   - Update DashboardApp initialization
   ```javascript
   class DashboardApp {
       constructor() {
           this.currentView = 'overview';
           this.components = {};
           this.isInitialized = false;
           this.appState = null; // Add reference
       }

       async init() {
           console.log('Initializing Task Orchestrator Dashboard v2.0...');

           try {
               // Initialize app state first
               if (typeof AppState !== 'undefined') {
                   this.appState = window.appState || new AppState();
                   window.appState = this.appState;
                   
                   // Auto-load most recent project if none selected
                   if (!this.appState.getProjectId()) {
                       await this.appState.loadMostRecentProject();
                   }
                   
                   // Subscribe to project changes
                   this.appState.subscribe((state) => {
                       console.log('Project changed:', state);
                       this.onProjectChange(state);
                   });
               }

               // ... rest of initialization ...
           } catch (error) {
               console.error('Failed to initialize dashboard:', error);
               this.showInitError();
           }
       }

       /**
        * Handle project context change
        */
       async onProjectChange(state) {
           console.log(`Project context changed to: ${state.projectName}`);
           
           // Update project subtitle
           this.updateProjectSubtitle(state.projectName);
           
           // Reload current view with new context
           await this.loadView(this.currentView);
           
           // Notify all subscribed components
           if (this.components.kanban && this.components.kanban.onProjectChange) {
               await this.components.kanban.onProjectChange(state.projectId);
           }
           if (this.components.graph && this.components.graph.onProjectChange) {
               await this.components.graph.onProjectChange(state.projectId);
           }
           if (this.components.analytics && this.components.analytics.onProjectChange) {
               await this.components.analytics.onProjectChange(state.projectId);
           }
       }

       /**
        * Update project subtitle across all tabs
        */
       updateProjectSubtitle(projectName) {
           const subtitle = document.getElementById('project-subtitle');
           if (subtitle) {
               const nameSpan = subtitle.querySelector('.project-name');
               if (nameSpan) {
                   nameSpan.textContent = projectName || 'All Projects';
               }
           }
       }
   }
   ```

**Testing:**
- Verify state persists across page reloads
- Test project selection triggers updates
- Validate localStorage data format
- Check event propagation to listeners

---

### Phase 3: Project Selector Modal (3-4 hours)

**Objective:** Create UI for project selection

**Tasks:**

1. **Create ProjectSelector Component**
   - File: `static/js/components/project-selector.js` (NEW)
   ```javascript
   /**
    * Project Selector Modal Component
    * Displays list of projects for selection
    */
   class ProjectSelector {
       constructor(modalId = 'project-selector-modal') {
           this.modalId = modalId;
           this.modal = null;
           this.projects = [];
           this.onSelect = null;
       }

       /**
        * Initialize the modal
        */
       init() {
           // Check if modal already exists
           this.modal = document.getElementById(this.modalId);
           
           if (!this.modal) {
               // Create modal HTML
               this.modal = this.createModal();
               document.body.appendChild(this.modal);
           }

           // Setup event listeners
           this.setupEventListeners();
           
           console.log('ProjectSelector initialized');
       }

       /**
        * Create modal HTML structure
        */
       createModal() {
           const modal = document.createElement('div');
           modal.id = this.modalId;
           modal.className = 'modal';
           modal.innerHTML = `
               <div class="modal-backdrop"></div>
               <div class="modal-container project-selector-container">
                   <div class="modal-header">
                       <h2>Select Project</h2>
                       <button class="modal-close" aria-label="Close">×</button>
                   </div>
                   <div class="modal-body">
                       <div class="project-selector-search">
                           <input type="text" 
                                  class="search-input" 
                                  id="project-search" 
                                  placeholder="Search projects..." />
                       </div>
                       <div class="project-selector-list" id="project-list">
                           <div class="loading">Loading projects...</div>
                       </div>
                   </div>
                   <div class="modal-footer">
                       <button class="btn-secondary modal-close">Cancel</button>
                       <button class="btn-primary" id="clear-project-btn">Show All Projects</button>
                   </div>
               </div>
           `;
           return modal;
       }

       /**
        * Setup event listeners
        */
       setupEventListeners() {
           // Close button
           const closeButtons = this.modal.querySelectorAll('.modal-close');
           closeButtons.forEach(btn => {
               btn.addEventListener('click', () => this.close());
           });

           // Backdrop click
           const backdrop = this.modal.querySelector('.modal-backdrop');
           backdrop.addEventListener('click', () => this.close());

           // Clear project button
           const clearBtn = this.modal.querySelector('#clear-project-btn');
           clearBtn.addEventListener('click', () => {
               this.selectProject(null, 'All Projects');
           });

           // Search input
           const searchInput = this.modal.querySelector('#project-search');
           searchInput.addEventListener('input', (e) => {
               this.filterProjects(e.target.value);
           });

           // ESC key to close
           document.addEventListener('keydown', (e) => {
               if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                   this.close();
               }
           });
       }

       /**
        * Open modal and load projects
        */
       async open(onSelectCallback) {
           this.onSelect = onSelectCallback;
           
           // Load projects
           await this.loadProjects();
           
           // Show modal
           this.modal.classList.add('show');
           document.body.style.overflow = 'hidden';
           
           // Focus search input
           setTimeout(() => {
               const searchInput = this.modal.querySelector('#project-search');
               if (searchInput) searchInput.focus();
           }, 100);
       }

       /**
        * Close modal
        */
       close() {
           this.modal.classList.remove('show');
           document.body.style.overflow = '';
           
           // Clear search
           const searchInput = this.modal.querySelector('#project-search');
           if (searchInput) searchInput.value = '';
       }

       /**
        * Load projects from API
        */
       async loadProjects() {
           try {
               this.projects = await api.getProjectsWithStats();
               this.renderProjects(this.projects);
           } catch (error) {
               console.error('Failed to load projects:', error);
               this.renderError();
           }
       }

       /**
        * Render projects list
        */
       renderProjects(projects) {
           const listContainer = this.modal.querySelector('#project-list');
           
           if (!projects || projects.length === 0) {
               listContainer.innerHTML = '<div class="no-results">No projects found</div>';
               return;
           }

           const currentProjectId = window.appState ? window.appState.getProjectId() : null;

           const html = `
               <div class="projects-grid">
                   ${projects.map(project => this.renderProjectCard(project, currentProjectId)).join('')}
               </div>
           `;

           listContainer.innerHTML = html;

           // Add click handlers
           listContainer.querySelectorAll('.project-card').forEach(card => {
               card.addEventListener('click', () => {
                   const projectId = card.dataset.projectId;
                   const projectName = card.dataset.projectName;
                   this.selectProject(projectId, projectName);
               });
           });
       }

       /**
        * Render individual project card
        */
       renderProjectCard(project, currentProjectId) {
           const isSelected = project.id === currentProjectId;
           const completionRate = project.completion_rate || 0;
           const lastActivity = project.last_activity 
               ? new Date(project.last_activity).toLocaleDateString()
               : 'No activity';

           return `
               <div class="project-card ${isSelected ? 'selected' : ''}" 
                    data-project-id="${project.id}"
                    data-project-name="${project.name}">
                   <div class="project-card-header">
                       <h3 class="project-card-title">${project.name}</h3>
                       ${isSelected ? '<span class="badge-selected">Current</span>' : ''}
                   </div>
                   <div class="project-card-stats">
                       <div class="stat-item">
                           <span class="stat-label">Features</span>
                           <span class="stat-value">${project.features_count || 0}</span>
                       </div>
                       <div class="stat-item">
                           <span class="stat-label">Tasks</span>
                           <span class="stat-value">${project.tasks_count || 0}</span>
                       </div>
                       <div class="stat-item">
                           <span class="stat-label">Progress</span>
                           <span class="stat-value">${completionRate}%</span>
                       </div>
                   </div>
                   <div class="project-card-progress">
                       <div class="progress-bar">
                           <div class="progress-fill" style="width: ${completionRate}%"></div>
                       </div>
                   </div>
                   <div class="project-card-footer">
                       <span class="last-activity">Last activity: ${lastActivity}</span>
                   </div>
               </div>
           `;
       }

       /**
        * Filter projects by search term
        */
       filterProjects(searchTerm) {
           const filtered = this.projects.filter(project => 
               project.name.toLowerCase().includes(searchTerm.toLowerCase())
           );
           this.renderProjects(filtered);
       }

       /**
        * Select a project
        */
       selectProject(projectId, projectName) {
           if (this.onSelect) {
               this.onSelect(projectId, projectName);
           }
           this.close();
       }

       /**
        * Render error state
        */
       renderError() {
           const listContainer = this.modal.querySelector('#project-list');
           listContainer.innerHTML = `
               <div class="error-state">
                   <p>Failed to load projects</p>
                   <button class="btn-primary" onclick="projectSelector.loadProjects()">
                       Retry
                   </button>
               </div>
           `;
       }
   }

   // Create global instance
   const projectSelector = new ProjectSelector();
   ```

2. **Add Modal CSS**
   - File: `dashboard.html` (add to <style> section)
   ```css
   /* Project Selector Modal */
   .project-selector-container {
       width: 90%;
       max-width: 900px;
       max-height: 80vh;
   }

   .project-selector-search {
       margin-bottom: 1rem;
   }

   .project-selector-list {
       max-height: 500px;
       overflow-y: auto;
   }

   .projects-grid {
       display: grid;
       grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
       gap: 1rem;
   }

   .project-card {
       background: var(--bg-tertiary);
       border: 2px solid var(--border);
       border-radius: 0.5rem;
       padding: 1rem;
       cursor: pointer;
       transition: all 0.2s;
   }

   .project-card:hover {
       border-color: var(--primary);
       transform: translateY(-2px);
       box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
   }

   .project-card.selected {
       border-color: var(--primary);
       background: var(--bg-secondary);
   }

   .project-card-header {
       display: flex;
       justify-content: space-between;
       align-items: flex-start;
       margin-bottom: 1rem;
   }

   .project-card-title {
       font-size: 1.125rem;
       font-weight: 600;
       color: var(--text-primary);
       margin: 0;
   }

   .badge-selected {
       background: var(--primary);
       color: white;
       padding: 0.25rem 0.5rem;
       border-radius: 0.25rem;
       font-size: 0.75rem;
       font-weight: 600;
   }

   .project-card-stats {
       display: grid;
       grid-template-columns: repeat(3, 1fr);
       gap: 0.75rem;
       margin-bottom: 1rem;
   }

   .project-card-stats .stat-item {
       text-align: center;
   }

   .project-card-stats .stat-label {
       display: block;
       font-size: 0.75rem;
       color: var(--text-secondary);
       margin-bottom: 0.25rem;
   }

   .project-card-stats .stat-value {
       display: block;
       font-size: 1.25rem;
       font-weight: 600;
       font-family: var(--font-mono);
       color: var(--text-primary);
   }

   .project-card-progress {
       margin-bottom: 0.75rem;
   }

   .progress-bar {
       height: 6px;
       background: var(--bg-primary);
       border-radius: 3px;
       overflow: hidden;
   }

   .progress-fill {
       height: 100%;
       background: linear-gradient(90deg, var(--primary), var(--success));
       transition: width 0.3s;
   }

   .project-card-footer {
       text-align: center;
   }

   .last-activity {
       font-size: 0.75rem;
       color: var(--text-secondary);
   }

   .no-results, .error-state {
       text-align: center;
       padding: 3rem;
       color: var(--text-secondary);
   }

   .loading {
       text-align: center;
       padding: 3rem;
       color: var(--text-secondary);
   }
   ```

3. **Update Overview Stats Card**
   - File: `static/js/main.js`
   - Make Projects card clickable
   ```javascript
   async loadStats() {
       try {
           const projectId = window.appState ? window.appState.getProjectId() : null;
           const stats = await api.getStats(projectId);
           const statsGrid = document.getElementById('stats-grid');

           if (!statsGrid) return;

           const html = `
               <div class="stat-card clickable" id="projects-card">
                   <div class="stat-label">Projects</div>
                   <div class="stat-value">${stats.projects || 0}</div>
                   <div class="stat-description">Click to select</div>
               </div>
               <!-- ... other stat cards ... -->
           `;

           statsGrid.innerHTML = html;

           // Add click handler for projects card
           const projectsCard = document.getElementById('projects-card');
           if (projectsCard && window.projectSelector) {
               projectsCard.addEventListener('click', () => {
                   window.projectSelector.open((projectId, projectName) => {
                       if (window.appState) {
                           if (projectId) {
                               window.appState.setProject(projectId, projectName);
                           } else {
                               window.appState.clearProject();
                           }
                       }
                   });
               });
           }
       } catch (error) {
           console.error('Failed to load stats:', error);
       }
   }
   ```

4. **Add CSS for Clickable Card**
   - File: `dashboard.html`
   ```css
   .stat-card.clickable {
       cursor: pointer;
       transition: all 0.2s;
   }

   .stat-card.clickable:hover {
       transform: translateY(-4px);
       box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
       border-color: var(--primary);
   }

   .stat-card.clickable .stat-description {
       color: var(--primary);
       font-weight: 500;
   }
   ```

**Testing:**
- Test modal open/close
- Verify project selection works
- Test search functionality
- Check responsive layout
- Validate state updates

---

### Phase 4: Current Project Section (3-4 hours)

**Objective:** Add detailed project context to Overview tab

**Tasks:**

1. **Create CurrentProjectSection Component**
   - File: `static/js/components/current-project-section.js` (NEW)
   ```javascript
   /**
    * Current Project Section Component
    * Displays detailed information about the selected project
    */
   class CurrentProjectSection {
       constructor(containerId = 'current-project-section') {
           this.containerId = containerId;
           this.container = null;
           this.projectId = null;
           this.projectData = null;
       }

       /**
        * Initialize component
        */
       init() {
           this.container = document.getElementById(this.containerId);
           
           if (!this.container) {
               console.warn(`Container #${this.containerId} not found`);
               return;
           }

           // Subscribe to project changes
           if (window.appState) {
               window.appState.subscribe((state) => {
                   this.onProjectChange(state.projectId);
               });
           }

           console.log('CurrentProjectSection initialized');
       }

       /**
        * Handle project context change
        */
       async onProjectChange(projectId) {
           this.projectId = projectId;
           
           if (!projectId) {
               this.renderEmptyState();
               return;
           }

           await this.loadProjectData();
       }

       /**
        * Load project data
        */
       async loadProjectData() {
           if (!this.projectId) return;

           try {
               this.renderLoading();
               
               const [stats, features] = await Promise.all([
                   api.getProjectStats(this.projectId),
                   api.getProjectFeatures(this.projectId)
               ]);

               this.projectData = { stats, features };
               this.render();
           } catch (error) {
               console.error('Failed to load project data:', error);
               this.renderError();
           }
       }

       /**
        * Render project section
        */
       render() {
           if (!this.projectData) return;

           const { stats, features } = this.projectData;
           const projectName = window.appState ? window.appState.getProjectName() : 'Current Project';

           const html = `
               <div class="current-project">
                   <div class="section-header">
                       <h2 class="section-title">Current Project: ${projectName}</h2>
                       <button class="btn-secondary btn-sm" id="change-project-btn">
                           Change Project
                       </button>
                   </div>

                   <div class="project-overview-grid">
                       <!-- Features List -->
                       <div class="project-features">
                           <h3 class="subsection-title">
                               Features (${this.getCompletedCount(features)} of ${features.length} completed)
                           </h3>
                           <div class="features-table">
                               ${this.renderFeaturesTable(features)}
                           </div>
                       </div>

                       <!-- Project Stats -->
                       <div class="project-stats-summary">
                           <h3 class="subsection-title">Summary</h3>
                           <div class="stats-list">
                               ${this.renderStatsList(stats)}
                           </div>
                       </div>
                   </div>
               </div>
           `;

           this.container.innerHTML = html;

           // Add event handler for change project button
           const changeBtn = this.container.querySelector('#change-project-btn');
           if (changeBtn && window.projectSelector) {
               changeBtn.addEventListener('click', () => {
                   window.projectSelector.open((projectId, projectName) => {
                       if (window.appState) {
                           if (projectId) {
                               window.appState.setProject(projectId, projectName);
                           } else {
                               window.appState.clearProject();
                           }
                       }
                   });
               });
           }
       }

       /**
        * Render features table
        */
       renderFeaturesTable(features) {
           if (!features || features.length === 0) {
               return '<div class="no-data">No features yet</div>';
           }

           return `
               <table class="features-data-table">
                   <thead>
                       <tr>
                           <th>Feature Name</th>
                           <th class="text-center">Tasks</th>
                           <th class="text-center">Status</th>
                           <th class="text-right">Progress</th>
                       </tr>
                   </thead>
                   <tbody>
                       ${features.map(feature => this.renderFeatureRow(feature)).join('')}
                   </tbody>
               </table>
           `;
       }

       /**
        * Render feature row
        */
       renderFeatureRow(feature) {
           const completionRate = feature.completion_rate || 0;
           const taskCount = feature.tasks ? feature.tasks.length : 0;
           const statusClass = this.getStatusClass(feature.status);

           return `
               <tr>
                   <td>
                       <div class="feature-name" title="${feature.name}">
                           ${feature.name}
                       </div>
                   </td>
                   <td class="text-center">
                       <span class="badge-count">${taskCount}</span>
                   </td>
                   <td class="text-center">
                       <span class="status-badge ${statusClass}">
                           ${feature.status || 'planning'}
                       </span>
                   </td>
                   <td class="text-right">
                       <div class="progress-with-label">
                           <span class="progress-label">${completionRate}%</span>
                           <div class="progress-bar-mini">
                               <div class="progress-fill" style="width: ${completionRate}%"></div>
                           </div>
                       </div>
                   </td>
               </tr>
           `;
       }

       /**
        * Render stats list
        */
       renderStatsList(stats) {
           return `
               <div class="stat-row">
                   <span class="stat-label">Total Tasks</span>
                   <span class="stat-value">${stats.tasks?.total || 0}</span>
               </div>
               <div class="stat-row">
                   <span class="stat-label">Pending</span>
                   <span class="stat-value pending">${stats.tasks?.pending || 0}</span>
               </div>
               <div class="stat-row">
                   <span class="stat-label">In Progress</span>
                   <span class="stat-value in-progress">${stats.tasks?.in_progress || 0}</span>
               </div>
               <div class="stat-row">
                   <span class="stat-label">Completed</span>
                   <span class="stat-value completed">${stats.tasks?.completed || 0}</span>
               </div>
               <div class="stat-row">
                   <span class="stat-label">Dependencies</span>
                   <span class="stat-value">${stats.dependencies || 0}</span>
               </div>
               <div class="stat-row">
                   <span class="stat-label">Sections</span>
                   <span class="stat-value">${stats.sections || 0}</span>
               </div>
               <div class="stat-row highlight">
                   <span class="stat-label">Completion Rate</span>
                   <span class="stat-value">${stats.completion_rate || 0}%</span>
               </div>
           `;
       }

       /**
        * Helper methods
        */
       getCompletedCount(features) {
           return features.filter(f => f.status === 'completed').length;
       }

       getStatusClass(status) {
           const statusMap = {
               'planning': 'status-planning',
               'in-development': 'status-in-progress',
               'completed': 'status-completed',
               'archived': 'status-archived'
           };
           return statusMap[status] || 'status-default';
       }

       /**
        * Render states
        */
       renderLoading() {
           this.container.innerHTML = `
               <div class="current-project loading-state">
                   <div class="spinner"></div>
                   <p>Loading project data...</p>
               </div>
           `;
       }

       renderEmptyState() {
           this.container.innerHTML = `
               <div class="current-project empty-state">
                   <p>No project selected. Select a project to view details.</p>
                   <button class="btn-primary" id="select-project-empty-btn">
                       Select Project
                   </button>
               </div>
           `;

           const selectBtn = this.container.querySelector('#select-project-empty-btn');
           if (selectBtn && window.projectSelector) {
               selectBtn.addEventListener('click', () => {
                   window.projectSelector.open((projectId, projectName) => {
                       if (window.appState && projectId) {
                           window.appState.setProject(projectId, projectName);
                       }
                   });
               });
           }
       }

       renderError() {
           this.container.innerHTML = `
               <div class="current-project error-state">
                   <p>Failed to load project data</p>
                   <button class="btn-primary" onclick="window.currentProjectSection.loadProjectData()">
                       Retry
                   </button>
               </div>
           `;
       }
   }

   // Create global instance
   const currentProjectSection = new CurrentProjectSection();
   ```

2. **Add HTML Container to Overview**
   - File: `dashboard.html`
   - Add after stats-grid, before timeline
   ```html
   <!-- Current Project Section -->
   <div id="current-project-section"></div>
   ```

3. **Add CSS Styles**
   - File: `dashboard.html`
   ```css
   /* Current Project Section */
   .current-project {
       background: var(--bg-secondary);
       border-radius: 0.75rem;
       padding: 1.5rem;
       margin-bottom: 2rem;
   }

   .section-header {
       display: flex;
       justify-content: space-between;
       align-items: center;
       margin-bottom: 1.5rem;
   }

   .section-title {
       font-size: 1.5rem;
       font-weight: 700;
       color: var(--text-primary);
       margin: 0;
   }

   .subsection-title {
       font-size: 1.125rem;
       font-weight: 600;
       color: var(--text-primary);
       margin-bottom: 1rem;
   }

   .project-overview-grid {
       display: grid;
       grid-template-columns: 2fr 1fr;
       gap: 2rem;
   }

   @media (max-width: 768px) {
       .project-overview-grid {
           grid-template-columns: 1fr;
       }
   }

   /* Features Table */
   .features-table {
       overflow-x: auto;
   }

   .features-data-table {
       width: 100%;
       border-collapse: collapse;
   }

   .features-data-table th {
       background: var(--bg-tertiary);
       padding: 0.75rem;
       text-align: left;
       font-size: 0.875rem;
       font-weight: 600;
       color: var(--text-secondary);
       border-bottom: 2px solid var(--border);
   }

   .features-data-table td {
       padding: 0.75rem;
       border-bottom: 1px solid var(--border);
   }

   .features-data-table tbody tr:hover {
       background: var(--bg-tertiary);
   }

   .feature-name {
       font-weight: 500;
       color: var(--text-primary);
       overflow: hidden;
       text-overflow: ellipsis;
       white-space: nowrap;
       max-width: 300px;
   }

   .badge-count {
       background: var(--bg-tertiary);
       padding: 0.25rem 0.5rem;
       border-radius: 0.25rem;
       font-family: var(--font-mono);
       font-size: 0.875rem;
       font-weight: 600;
   }

   .status-badge {
       padding: 0.25rem 0.75rem;
       border-radius: 9999px;
       font-size: 0.75rem;
       font-weight: 600;
       text-transform: uppercase;
   }

   .status-planning {
       background: rgba(148, 163, 184, 0.2);
       color: #94a3b8;
   }

   .status-in-progress {
       background: rgba(59, 130, 246, 0.2);
       color: #3b82f6;
   }

   .status-completed {
       background: rgba(16, 185, 129, 0.2);
       color: #10b981;
   }

   .status-archived {
       background: rgba(100, 116, 139, 0.2);
       color: #64748b;
   }

   .progress-with-label {
       display: flex;
       align-items: center;
       gap: 0.5rem;
   }

   .progress-label {
       font-family: var(--font-mono);
       font-size: 0.875rem;
       font-weight: 600;
       min-width: 40px;
       text-align: right;
   }

   .progress-bar-mini {
       flex: 1;
       height: 6px;
       background: var(--bg-primary);
       border-radius: 3px;
       overflow: hidden;
   }

   /* Project Stats Summary */
   .project-stats-summary {
       background: var(--bg-tertiary);
       border-radius: 0.5rem;
       padding: 1.5rem;
   }

   .stats-list {
       display: flex;
       flex-direction: column;
       gap: 0.75rem;
   }

   .stat-row {
       display: flex;
       justify-content: space-between;
       align-items: center;
       padding: 0.5rem 0;
       border-bottom: 1px solid var(--border);
   }

   .stat-row:last-child {
       border-bottom: none;
   }

   .stat-row.highlight {
       background: rgba(59, 130, 246, 0.1);
       padding: 0.75rem;
       margin-top: 0.5rem;
       border-radius: 0.25rem;
       border-bottom: none;
   }

   .stat-row .stat-label {
       font-size: 0.875rem;
       color: var(--text-secondary);
   }

   .stat-row .stat-value {
       font-family: var(--font-mono);
       font-size: 1.125rem;
       font-weight: 600;
       color: var(--text-primary);
   }

   .stat-row .stat-value.pending {
       color: var(--warning);
   }

   .stat-row .stat-value.in-progress {
       color: var(--primary);
   }

   .stat-row .stat-value.completed {
       color: var(--success);
   }

   /* Empty/Loading/Error States */
   .loading-state, .empty-state, .error-state {
       text-align: center;
       padding: 3rem;
       color: var(--text-secondary);
   }

   .loading-state .spinner {
       width: 40px;
       height: 40px;
       border: 4px solid var(--border);
       border-top-color: var(--primary);
       border-radius: 50%;
       animation: spin 0.8s linear infinite;
       margin: 0 auto 1rem;
   }

   @keyframes spin {
       to { transform: rotate(360deg); }
   }

   .text-center {
       text-align: center;
   }

   .text-right {
       text-align: right;
   }

   .btn-sm {
       padding: 0.375rem 0.75rem;
       font-size: 0.875rem;
   }
   ```

4. **Update Main.js to Initialize Component**
   - File: `static/js/main.js`
   ```javascript
   async loadOverviewView() {
       try {
           // Load stats
           await this.loadStats();

           // Initialize current project section
           if (!this.components.currentProjectSection && typeof CurrentProjectSection !== 'undefined') {
               window.currentProjectSection = new CurrentProjectSection();
               this.components.currentProjectSection = window.currentProjectSection;
               window.currentProjectSection.init();
               
               // Load project data if project is selected
               if (window.appState && window.appState.getProjectId()) {
                   await window.currentProjectSection.onProjectChange(
                       window.appState.getProjectId()
                   );
               }
           }

           // Initialize timeline
           if (!this.components.timeline && typeof Timeline !== 'undefined') {
               window.timeline = new Timeline('timeline-feed');
               this.components.timeline = window.timeline;
               await window.timeline.init();
           } else if (this.components.timeline) {
               await this.components.timeline.init();
           }
       } catch (error) {
           console.error('Failed to load overview:', error);
       }
   }
   ```

**Testing:**
- Verify section shows/hides based on project selection
- Test features table rendering
- Check stats calculation accuracy
- Validate responsive layout
- Test change project button

---

### Phase 5: Enhanced Activity Timeline (2-3 hours)

**Objective:** Replace timeline cards with activity grid

**Tasks:**

1. **Update Timeline Component**
   - File: `static/js/components/timeline.js`
   - Modify to render as grid/table
   ```javascript
   /**
    * Enhanced Timeline Component
    * Displays recent activity as a grid
    */
   class Timeline {
       constructor(containerId = 'timeline-feed') {
           this.containerId = containerId;
           this.container = null;
           this.activities = [];
           this.days = 7;
       }

       async init() {
           this.container = document.getElementById(this.containerId);
           
           if (!this.container) {
               console.warn(`Container #${this.containerId} not found`);
               return;
           }

           // Subscribe to project changes
           if (window.appState) {
               window.appState.subscribe((state) => {
                   this.onProjectChange(state.projectId);
               });
           }

           await this.load();
           console.log('Timeline initialized');
       }

       /**
        * Handle project change
        */
       async onProjectChange(projectId) {
           await this.load();
       }

       /**
        * Load activities from API
        */
       async load() {
           try {
               this.renderLoading();
               
               const projectId = window.appState ? window.appState.getProjectId() : null;
               this.activities = await api.getActivityTimeline(this.days, projectId);
               
               this.render();
           } catch (error) {
               console.error('Failed to load timeline:', error);
               this.renderError();
           }
       }

       /**
        * Render activity grid
        */
       render() {
           if (!this.activities || this.activities.length === 0) {
               this.renderEmpty();
               return;
           }

           const html = `
               <div class="activity-grid-container">
                   <div class="activity-header">
                       <h3>Recent Activity</h3>
                       <div class="activity-controls">
                           <select id="activity-days-filter" class="days-filter">
                               <option value="1">Last 24 hours</option>
                               <option value="7" selected>Last 7 days</option>
                               <option value="14">Last 14 days</option>
                               <option value="30">Last 30 days</option>
                           </select>
                       </div>
                   </div>
                   <div class="activity-grid">
                       <table class="activity-table">
                           <thead>
                               <tr>
                                   <th class="col-datetime">Date/Time</th>
                                   <th class="col-project">Project</th>
                                   <th class="col-task">Task</th>
                                   <th class="col-action">Action</th>
                               </tr>
                           </thead>
                           <tbody>
                               ${this.activities.map(activity => this.renderActivityRow(activity)).join('')}
                           </tbody>
                       </table>
                   </div>
               </div>
           `;

           this.container.innerHTML = html;

           // Add event handler for days filter
           const daysFilter = this.container.querySelector('#activity-days-filter');
           if (daysFilter) {
               daysFilter.addEventListener('change', async (e) => {
                   this.days = parseInt(e.target.value);
                   await this.load();
               });
           }

           // Add click handlers for rows
           this.container.querySelectorAll('.activity-row').forEach(row => {
               row.addEventListener('click', () => {
                   const taskId = row.dataset.taskId;
                   if (taskId && window.detailModal) {
                       window.detailModal.show(taskId, 'task');
                   }
               });
           });
       }

       /**
        * Render single activity row
        */
       renderActivityRow(activity) {
           const datetime = this.formatDateTime(activity.timestamp);
           const projectName = activity.project_name || 'No Project';
           const taskTitle = this.truncate(activity.task_title, 50);
           const actionClass = this.getActionClass(activity.action);
           const actionLabel = this.getActionLabel(activity.action);

           return `
               <tr class="activity-row" data-task-id="${activity.task_id}">
                   <td class="col-datetime">
                       <span class="datetime-text">${datetime}</span>
                   </td>
                   <td class="col-project">
                       <span class="project-name" title="${projectName}">
                           ${projectName}
                       </span>
                   </td>
                   <td class="col-task">
                       <span class="task-title" title="${activity.task_title}">
                           ${taskTitle}
                       </span>
                   </td>
                   <td class="col-action">
                       <span class="action-badge ${actionClass}">
                           ${actionLabel}
                       </span>
                   </td>
               </tr>
           `;
       }

       /**
        * Format datetime to short format (MM/DD HH:mm)
        */
       formatDateTime(timestamp) {
           const date = new Date(timestamp);
           const month = String(date.getMonth() + 1).padStart(2, '0');
           const day = String(date.getDate()).padStart(2, '0');
           const hours = String(date.getHours()).padStart(2, '0');
           const minutes = String(date.getMinutes()).padStart(2, '0');
           return `${month}/${day} ${hours}:${minutes}`;
       }

       /**
        * Get action class for styling
        */
       getActionClass(action) {
           const actionMap = {
               'created': 'action-created',
               'updated': 'action-updated',
               'completed': 'action-completed',
               'status_changed': 'action-status-changed',
               'assigned': 'action-assigned'
           };
           return actionMap[action] || 'action-default';
       }

       /**
        * Get human-readable action label
        */
       getActionLabel(action) {
           const labelMap = {
               'created': 'Created',
               'updated': 'Updated',
               'completed': 'Completed',
               'status_changed': 'Status Changed',
               'assigned': 'Assigned'
           };
           return labelMap[action] || action;
       }

       /**
        * Truncate text with ellipsis
        */
       truncate(text, maxLength) {
           if (!text) return '';
           if (text.length <= maxLength) return text;
           return text.substring(0, maxLength) + '...';
       }

       /**
        * Render states
        */
       renderLoading() {
           this.container.innerHTML = `
               <div class="activity-loading">
                   <div class="spinner"></div>
                   <p>Loading activity...</p>
               </div>
           `;
       }

       renderEmpty() {
           this.container.innerHTML = `
               <div class="activity-empty">
                   <p>No recent activity</p>
               </div>
           `;
       }

       renderError() {
           this.container.innerHTML = `
               <div class="activity-error">
                   <p>Failed to load activity</p>
                   <button class="btn-primary" onclick="window.timeline.load()">
                       Retry
                   </button>
               </div>
           `;
       }
   }
   ```

2. **Add Activity Grid CSS**
   - File: `dashboard.html`
   ```css
   /* Activity Grid */
   .activity-grid-container {
       background: var(--bg-secondary);
       border-radius: 0.75rem;
       padding: 1.5rem;
       margin-top: 2rem;
   }

   .activity-header {
       display: flex;
       justify-content: space-between;
       align-items: center;
       margin-bottom: 1rem;
   }

   .activity-header h3 {
       font-size: 1.25rem;
       font-weight: 600;
       color: var(--text-primary);
       margin: 0;
   }

   .days-filter {
       padding: 0.5rem 1rem;
       border: 1px solid var(--border);
       border-radius: 0.375rem;
       background: var(--bg-tertiary);
       color: var(--text-primary);
       font-size: 0.875rem;
       cursor: pointer;
   }

   .days-filter:focus {
       outline: none;
       border-color: var(--primary);
   }

   .activity-grid {
       overflow-x: auto;
   }

   .activity-table {
       width: 100%;
       border-collapse: collapse;
   }

   .activity-table th {
       background: var(--bg-tertiary);
       padding: 0.75rem;
       text-align: left;
       font-size: 0.875rem;
       font-weight: 600;
       color: var(--text-secondary);
       border-bottom: 2px solid var(--border);
       white-space: nowrap;
   }

   .activity-table .col-datetime {
       width: 120px;
   }

   .activity-table .col-project {
       width: 200px;
   }

   .activity-table .col-task {
       width: auto;
   }

   .activity-table .col-action {
       width: 150px;
   }

   .activity-table td {
       padding: 0.75rem;
       border-bottom: 1px solid var(--border);
   }

   .activity-row {
       cursor: pointer;
       transition: background 0.2s;
   }

   .activity-row:hover {
       background: var(--bg-tertiary);
   }

   .datetime-text {
       font-family: var(--font-mono);
       font-size: 0.875rem;
       color: var(--text-secondary);
   }

   .project-name, .task-title {
       display: block;
       overflow: hidden;
       text-overflow: ellipsis;
       white-space: nowrap;
   }

   .project-name {
       font-weight: 500;
       color: var(--text-primary);
   }

   .task-title {
       color: var(--text-secondary);
   }

   .action-badge {
       display: inline-block;
       padding: 0.25rem 0.75rem;
       border-radius: 0.25rem;
       font-size: 0.75rem;
       font-weight: 600;
       text-transform: capitalize;
   }

   .action-created {
       background: rgba(59, 130, 246, 0.2);
       color: #3b82f6;
   }

   .action-updated {
       background: rgba(148, 163, 184, 0.2);
       color: #94a3b8;
   }

   .action-completed {
       background: rgba(16, 185, 129, 0.2);
       color: #10b981;
   }

   .action-status-changed {
       background: rgba(245, 158, 11, 0.2);
       color: #f59e0b;
   }

   .action-assigned {
       background: rgba(168, 85, 247, 0.2);
       color: #a855f7;
   }

   .action-default {
       background: rgba(100, 116, 139, 0.2);
       color: #64748b;
   }

   /* Activity States */
   .activity-loading, .activity-empty, .activity-error {
       text-align: center;
       padding: 3rem;
       color: var(--text-secondary);
   }

   /* Responsive */
   @media (max-width: 768px) {
       .activity-table .col-project {
           display: none;
       }
       
       .activity-table .col-task {
           max-width: 200px;
       }
   }
   ```

**Testing:**
- Test activity loading with project filter
- Verify datetime formatting
- Check row click opens task detail
- Test days filter dropdown
- Validate responsive behavior

---

### Phase 6: Graph Enhancements & Project Subtitle (2-3 hours)

**Objective:** Fix graph viewport and add project context to all tabs

**Tasks:**

1. **Update Graph Component**
   - File: `static/js/components/graph.js`
   - Add fit-to-screen and project filtering
   ```javascript
   class Graph {
       // ... existing code ...

       /**
        * Handle project change
        */
       async onProjectChange(projectId) {
           this.projectId = projectId;
           await this.load();
       }

       /**
        * Load graph data with project filter
        */
       async load() {
           try {
               this.renderLoading();
               
               const projectId = window.appState ? window.appState.getProjectId() : null;
               const params = projectId ? { project_id: projectId } : {};
               
               const data = await api.getDependencyGraph(params);
               this.renderGraph(data);
           } catch (error) {
               console.error('Failed to load graph:', error);
               this.renderError();
           }
       }

       /**
        * Render graph with fit-to-screen
        */
       renderGraph(data) {
           if (!this.cy) {
               this.initCytoscape();
           }

           // Clear existing elements
           this.cy.elements().remove();

           // Add nodes and edges
           this.cy.add(data.elements);

           // Apply layout with fit
           const layout = this.cy.layout({
               name: 'dagre',
               rankDir: 'TB',
               fit: true,              // ✓ Fit to container
               padding: 30,            // ✓ Padding from edges
               animate: false,
               nodeDimensionsIncludeLabels: true,
               spacingFactor: 1.2
           });

           layout.run();

           // Add resize handler
           this.addResizeHandler();
       }

       /**
        * Add window resize handler
        */
       addResizeHandler() {
           if (this.resizeHandler) {
               window.removeEventListener('resize', this.resizeHandler);
           }

           this.resizeHandler = () => {
               if (this.cy) {
                   this.cy.resize();
                   this.cy.fit(this.cy.elements(), 30);
               }
           };

           window.addEventListener('resize', this.resizeHandler);
       }

       /**
        * Add zoom-to-fit button
        */
       addZoomControls() {
           const controls = document.createElement('div');
           controls.className = 'graph-controls';
           controls.innerHTML = `
               <button class="graph-control-btn" id="zoom-to-fit" title="Fit to screen">
                   <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                       <path d="M3 3h14v14H3z" stroke="currentColor" fill="none" stroke-width="2"/>
                       <path d="M7 10h6M10 7v6" stroke="currentColor" stroke-width="2"/>
                   </svg>
               </button>
               <button class="graph-control-btn" id="zoom-in" title="Zoom in">+</button>
               <button class="graph-control-btn" id="zoom-out" title="Zoom out">-</button>
           `;

           this.container.appendChild(controls);

           // Add event handlers
           document.getElementById('zoom-to-fit').addEventListener('click', () => {
               this.cy.fit(this.cy.elements(), 30);
           });

           document.getElementById('zoom-in').addEventListener('click', () => {
               this.cy.zoom(this.cy.zoom() * 1.2);
               this.cy.center();
           });

           document.getElementById('zoom-out').addEventListener('click', () => {
               this.cy.zoom(this.cy.zoom() * 0.8);
               this.cy.center();
           });
       }
   }
   ```

2. **Add Graph Controls CSS**
   - File: `dashboard.html`
   ```css
   /* Graph Controls */
   .graph-controls {
       position: absolute;
       top: 1rem;
       right: 1rem;
       display: flex;
       gap: 0.5rem;
       z-index: 10;
   }

   .graph-control-btn {
       background: var(--bg-secondary);
       border: 1px solid var(--border);
       color: var(--text-primary);
       width: 36px;
       height: 36px;
       border-radius: 0.375rem;
       display: flex;
       align-items: center;
       justify-content: center;
       cursor: pointer;
       transition: all 0.2s;
       font-size: 1.25rem;
       font-weight: 600;
   }

   .graph-control-btn:hover {
       background: var(--bg-tertiary);
       border-color: var(--primary);
   }

   .graph-control-btn:active {
       transform: scale(0.95);
   }
   ```

3. **Add Project Subtitle Component**
   - File: `static/js/components/project-subtitle.js` (NEW)
   ```javascript
   /**
    * Project Subtitle Component
    * Shows current project name below navigation tabs
    */
   class ProjectSubtitle {
       constructor(containerId = 'project-subtitle') {
           this.containerId = containerId;
           this.container = null;
       }

       init() {
           this.container = document.getElementById(this.containerId);
           
           if (!this.container) {
               // Create container if it doesn't exist
               this.container = this.createContainer();
               
               const navTabs = document.querySelector('.nav-tabs');
               if (navTabs && navTabs.parentNode) {
                   navTabs.parentNode.insertBefore(this.container, navTabs.nextSibling);
               }
           }

           // Subscribe to project changes
           if (window.appState) {
               window.appState.subscribe((state) => {
                   this.update(state.projectName);
               });

               // Initial update
               this.update(window.appState.getProjectName());
           }

           // Add click handler
           this.setupClickHandler();

           console.log('ProjectSubtitle initialized');
       }

       createContainer() {
           const container = document.createElement('div');
           container.id = this.containerId;
           container.className = 'project-subtitle';
           container.innerHTML = `
               <span class="project-icon">📁</span>
               <span class="project-label">Current Project:</span>
               <span class="project-name">All Projects</span>
           `;
           return container;
       }

       update(projectName) {
           if (!this.container) return;

           const nameSpan = this.container.querySelector('.project-name');
           if (nameSpan) {
               nameSpan.textContent = projectName || 'All Projects';
           }
       }

       setupClickHandler() {
           const nameSpan = this.container.querySelector('.project-name');
           if (nameSpan && window.projectSelector) {
               nameSpan.addEventListener('click', () => {
                   window.projectSelector.open((projectId, projectName) => {
                       if (window.appState) {
                           if (projectId) {
                               window.appState.setProject(projectId, projectName);
                           } else {
                               window.appState.clearProject();
                           }
                       }
                   });
               });
           }
       }
   }

   // Create global instance
   const projectSubtitle = new ProjectSubtitle();
   ```

4. **Add Project Subtitle to HTML**
   - File: `dashboard.html`
   - Add after nav-tabs
   ```html
   <!-- Navigation Tabs -->
   <nav class="nav-tabs">
       <!-- ... existing tabs ... -->
   </nav>

   <!-- Project Subtitle -->
   <div id="project-subtitle" class="project-subtitle">
       <span class="project-icon">📁</span>
       <span class="project-label">Current Project:</span>
       <span class="project-name">All Projects</span>
   </div>
   ```

5. **Initialize Components in Main.js**
   - File: `static/js/main.js`
   ```javascript
   initializeGlobalComponents() {
       try {
           // ... existing code ...

           // Initialize project subtitle
           if (typeof ProjectSubtitle !== 'undefined') {
               window.projectSubtitle = new ProjectSubtitle();
               window.projectSubtitle.init();
           }

           // Initialize project selector
           if (typeof ProjectSelector !== 'undefined') {
               window.projectSelector = new ProjectSelector();
               window.projectSelector.init();
           }
       } catch (error) {
           console.error('Error initializing global components:', error);
       }
   }
   ```

6. **Update Other Views to Respect Project Context**
   - File: `static/js/components/kanban.js`
   ```javascript
   class Kanban {
       // Add project change handler
       async onProjectChange(projectId) {
           this.projectId = projectId;
           await this.load();
       }

       async load() {
           // ... existing code with project filtering ...
           const projectId = window.appState ? window.appState.getProjectId() : null;
           const params = projectId ? { project_id: projectId } : {};
           const tasks = await api.getTasks(params);
           // ... rest of rendering ...
       }
   }
   ```

   - File: `static/js/components/analytics.js`
   ```javascript
   class Analytics {
       // Add project change handler
       async onProjectChange(projectId) {
           this.projectId = projectId;
           await this.load();
       }

       async load() {
           // Load analytics with project filter
           const projectId = window.appState ? window.appState.getProjectId() : null;
           const data = await api.getAnalyticsOverview(projectId);
           this.render(data);
       }
   }
   ```

**Testing:**
- Test graph fit-to-screen on different viewport sizes
- Verify zoom controls work
- Test project subtitle updates on all tabs
- Check subtitle is clickable
- Validate all views filter by project

---

## Testing Strategy

### Unit Testing

**Backend Tests:**
```python
# test_project_api.py
def test_get_projects_with_stats():
    response = client.get("/api/projects")
    assert response.status_code == 200
    projects = response.json()
    assert all('features_count' in p for p in projects)
    assert all('completion_rate' in p for p in projects)

def test_get_project_stats():
    response = client.get("/api/projects/test-project-id/stats")
    assert response.status_code == 200
    stats = response.json()
    assert 'features' in stats
    assert 'tasks' in stats
    assert 'dependencies' in stats

def test_activity_timeline_with_project_filter():
    response = client.get("/api/analytics/timeline?project_id=test-id")
    assert response.status_code == 200
    activities = response.json()
    assert all(a['project_id'] == 'test-id' for a in activities)
```

**Frontend Tests:**
```javascript
// test-app-state.js
describe('AppState', () => {
    test('sets project correctly', () => {
        const state = new AppState();
        state.setProject('test-id', 'Test Project');
        expect(state.getProjectId()).toBe('test-id');
        expect(state.getProjectName()).toBe('Test Project');
    });

    test('persists to localStorage', () => {
        const state = new AppState();
        state.setProject('test-id', 'Test Project');
        const stored = JSON.parse(localStorage.getItem('selectedProject'));
        expect(stored.id).toBe('test-id');
    });

    test('notifies listeners on change', () => {
        const state = new AppState();
        const listener = jest.fn();
        state.subscribe(listener);
        state.setProject('test-id', 'Test Project');
        expect(listener).toHaveBeenCalledWith({
            projectId: 'test-id',
            projectName: 'Test Project'
        });
    });
});
```

### Integration Testing

1. **Project Selection Flow:**
   - Click Projects card → Modal opens
   - Select project → Modal closes & state updates
   - Verify all views reload with project filter
   - Check localStorage persistence

2. **Project Context Flow:**
   - Select project A → Verify filtered data
   - Switch to project B → Verify data changes
   - Clear project → Verify shows all data

3. **Activity Timeline:**
   - Load timeline → Verify activities shown
   - Filter by project → Verify only project activities
   - Click activity row → Verify detail modal opens

### Manual Testing Checklist

- [ ] Backend endpoints return correct data
- [ ] Project selector modal opens/closes properly
- [ ] Project selection updates all views
- [ ] Current project section displays correctly
- [ ] Activity grid shows proper data
- [ ] Graph fits to screen properly
- [ ] Project subtitle shows on all tabs
- [ ] State persists across page reloads
- [ ] Responsive design works on mobile
- [ ] No console errors
- [ ] Performance is acceptable

---

## Rollback Plan

### If Issues Arise During Implementation

1. **Backend Issues:**
   - Revert server_v2.py changes
   - Restore database if migrations applied
   - Restart server with previous version

2. **Frontend Issues:**
   - Remove new JS files
   - Restore previous main.js
   - Clear localStorage: `localStorage.removeItem('selectedProject')`
   - Hard refresh browser

3. **Database Issues:**
   - No schema changes planned, low risk
   - If needed, restore from backup

### Rollback Commands

```bash
# Git rollback
git stash  # Stash current changes
git checkout <last-working-commit>

# Docker restart
docker-compose down
docker-compose up -d

# Clear browser state
# In browser console:
localStorage.clear();
location.reload(true);
```

---

## Implementation Order & Dependencies

### Week 1: Backend & State Management

**Day 1-2:** Phase 1 - Backend API Enhancements
- Add project stats endpoints
- Enhance activity timeline
- Test all endpoints

**Day 3:** Phase 2 - Global State Management
- Create AppState class
- Update API client
- Integrate with main.js

### Week 2: UI Components

**Day 4-5:** Phase 3 - Project Selector Modal
- Create ProjectSelector component
- Add modal CSS
- Make Projects card clickable

**Day 6-7:** Phase 4 - Current Project Section
- Create CurrentProjectSection component
- Add features table
- Add stats summary

### Week 3: Enhancements & Polish

**Day 8:** Phase 5 - Enhanced Activity Timeline
- Update Timeline component
- Replace cards with grid
- Add date filtering

**Day 9:** Phase 6 - Graph & Subtitle
- Fix graph fit-to-screen
- Add ProjectSubtitle component
- Update all views for project context

**Day 10:** Testing & Bug Fixes
- Run all tests
- Fix issues
- Polish UI

---

## Success Criteria

✅ **Must Have:**
1. Project selector modal functional
2. Current project section displays data
3. Activity grid shows recent activities
4. Graph fits to screen
5. Project subtitle on all tabs
6. All views filter by selected project
7. State persists across reloads

✅ **Should Have:**
8. Responsive design works well
9. No performance degradation
10. Clean error handling
11. Loading states for all async operations

✅ **Nice to Have:**
12. Smooth animations and transitions
13. Keyboard shortcuts for project selection
14. Export current project data
15. Project comparison view

---

## Notes & Considerations

### Performance Considerations

- **Caching:** Cache project list to reduce API calls
- **Debouncing:** Debounce search input in project selector
- **Lazy Loading:** Load activity timeline in chunks if needed
- **Memoization:** Cache computed stats in backend

### Accessibility Considerations

- **Keyboard Navigation:** Tab through modal, ESC to close
- **ARIA Labels:** Add proper ARIA labels to interactive elements
- **Focus Management:** Return focus after modal closes
- **Color Contrast:** Ensure all text meets WCAG AA standards

### Browser Compatibility

- **localStorage:** Supported in all modern browsers
- **Fetch API:** Polyfill not needed for modern browsers
- **CSS Grid:** Supported in all modern browsers
- **Flexbox:** Fallback for older browsers

### Future Enhancements

1. **Multi-Project Comparison:**
   - Side-by-side project statistics
   - Progress comparison charts

2. **Project Templates:**
   - Save project configurations as templates
   - Quick project setup from templates

3. **Project Archiving:**
   - Archive completed projects
   - Filter to show/hide archived projects

4. **Advanced Filtering:**
   - Filter by multiple projects
   - Filter by date range
   - Filter by team member

5. **Export Functionality:**
   - Export project report as PDF
   - Export activity log as CSV
   - Export dependency graph as image

---

## File Checklist

### New Files to Create

- [ ] `static/js/utils/app-state.js`
- [ ] `static/js/components/project-selector.js`
- [ ] `static/js/components/current-project-section.js`
- [ ] `static/js/components/project-subtitle.js`

### Files to Modify

- [ ] `server_v2.py` (add endpoints)
- [ ] `static/js/utils/api.js` (add methods)
- [ ] `static/js/main.js` (initialization)
- [ ] `static/js/components/timeline.js` (grid view)
- [ ] `static/js/components/graph.js` (fit-to-screen)
- [ ] `static/js/components/kanban.js` (project filter)
- [ ] `static/js/components/analytics.js` (project filter)
- [ ] `dashboard.html` (CSS, HTML structure, script tags)

### Load Order in HTML

```html
<!-- Utils (loaded first) -->
<script src="/static/js/utils/api.js"></script>
<script src="/static/js/utils/app-state.js"></script>
<script src="/static/js/utils/formatters.js"></script>
<script src="/static/js/utils/helpers.js"></script>

<!-- Components -->
<script src="/static/js/components/project-selector.js"></script>
<script src="/static/js/components/project-subtitle.js"></script>
<script src="/static/js/components/current-project-section.js"></script>
<script src="/static/js/components/timeline.js"></script>
<script src="/static/js/components/kanban.js"></script>
<script src="/static/js/components/graph.js"></script>
<script src="/static/js/components/analytics.js"></script>
<script src="/static/js/components/detail-modal.js"></script>
<script src="/static/js/components/search.js"></script>

<!-- Main app (loaded last) -->
<script src="/static/js/main.js"></script>
<script src="/static/js/websocket_client.js"></script>
```

---

## Conclusion

This enhancement plan provides a comprehensive roadmap for adding project-scoped viewing to the Task Orchestrator Dashboard. The phased approach ensures:

- **Minimal Disruption:** Backward compatibility maintained
- **Progressive Enhancement:** Each phase builds on previous work
- **Testing at Each Stage:** Quality assurance throughout
- **Clear Rollback Path:** Easy to revert if issues arise

The estimated total effort is **16-24 hours** spread across 10 days, with clear milestones and success criteria at each phase.

---

**End of Enhancement Plan**
