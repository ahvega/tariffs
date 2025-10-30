# Task Orchestrator Setup & Usage Guide

## **Purpose:** Step-by-step guide to set up and use the task-orchestrator MCP server with SicargaBox project

### **Date:** 2025-10-27

---

## Prerequisites

✅ Docker Desktop for Windows installed and running
✅ WSL2 enabled with Ubuntu
✅ Docker MCP Plugin installed (v0.24.0)
✅ Task-orchestrator available in MCP catalog

---

## Quick Start

### Option 1: Run from Windows PowerShell (Recommended)

```powershell
# Navigate to your project directory
cd E:\mydevtools\tariffs

# Start the MCP gateway with task-orchestrator
docker mcp gateway run --servers task-orchestrator --port 3000
```

### Option 2: Run from WSL via PowerShell

```bash
# From WSL terminal
powershell.exe -Command "docker mcp gateway run --servers task-orchestrator --port 3000"
```

### Option 3: Run in Background

```powershell
# Windows PowerShell - Run in background
Start-Job -ScriptBlock {
    docker mcp gateway run --servers task-orchestrator --port 3000
}

# Check job status
Get-Job

# Get job output
Receive-Job -Id 1

# Stop the job
Stop-Job -Id 1
Remove-Job -Id 1
```

---

## Accessing Task Orchestrator Tools

Once the gateway is running, you'll have access to **42 tools** via MCP protocol. The tools are available through:

1. **Claude Desktop** with MCP support
2. **Cursor IDE** with MCP configuration
3. **Windsurf** with MCP integration
4. **Any MCP-compatible client**

### Configuration for Claude Desktop

Add to your Claude Desktop config file (`%APPDATA%\Claude\config.json` on Windows):

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "docker",
      "args": [
        "mcp",
        "gateway",
        "run",
        "--servers",
        "task-orchestrator"
      ]
    }
  }
}
```

After adding, restart Claude Desktop. You should see the task-orchestrator tools available.

---

## Initial Project Setup

### Step 1: Initialize Task Orchestrator

When you first connect to task-orchestrator, use the initialization prompt:

#### **Prompt:**

```bash
Use the initialize_task_orchestrator prompt to set up my project management system.
```

This will:

- Load AI guidelines for autonomous task management
- Set up pattern recognition
- Enable template discovery

### Step 2: Create the SicargaBox Project

#### **Prompt Step 2:**

```bash
Create a new project called "SicargaBox" with the following details:

Name: SicargaBox
Description: Comprehensive courier quotation and shipping request system for international shipments from US to Honduras
Status: IN_PROGRESS
Priority: HIGH
Tags: courier, quotation, shipping, django, nextjs, honduras, tariffs

Technology Stack:
- Backend: Django 5.0.2, DRF, PostgreSQL, Elasticsearch 8.17
- Frontend: Next.js 15.5.6, TailwindCSS 4, DaisyUI 5.3.7
- AI: Claude 3.5 Sonnet, DeepSeek
- Infrastructure: Docker, Redis
```

### Step 3: Create Main Features (Phases)

#### **Prompt Step 3:**

```bash
Create the following features for the SicargaBox project:

1. Phase 0: Foundation & Data
   - Status: COMPLETED
   - Priority: CRITICAL
   - Description: Complete Django project setup with PostgreSQL database, core models implementation, tariff data import (7,524 partidas), admin interface configuration, and authentication system

2. Phase 1: Backend Foundation
   - Status: IN_PROGRESS
   - Priority: CRITICAL
   - Progress: 35%
   - Description: Core backend functionality including public quote calculator, client onboarding workflow, quote acceptance, shipment tracking, liquidation system, and comprehensive API endpoints

3. Phase 2: Search & AI Enhancement
   - Status: COMPLETED
   - Priority: HIGH
   - Description: Elasticsearch integration with AI-powered bilingual keyword generation, 21% premium Claude quality coverage

4. Phase 4: Frontend Development
   - Status: IN_PROGRESS
   - Priority: CRITICAL
   - Progress: 40%
   - Description: Next.js 15.5.6 customer portal with public quote calculator, authentication, customer dashboard, and staff operations portal

5. Phase 5: Testing & Deployment
   - Status: NOT_STARTED
   - Priority: MEDIUM
   - Description: Comprehensive testing, performance optimization, security audit, production setup, and deployment

6. Phase 3: Elasticsearch Admin (OPTIONAL)
   - Status: NOT_STARTED
   - Priority: LOW
   - Description: Django admin interface for Elasticsearch operations with Celery background task processing

7. Phase 6: Mobile App (FUTURE)
   - Status: NOT_STARTED
   - Priority: LOW
   - Description: Mobile application for iOS and Android (future phase)
```

### Step 4: Import Tasks from Migration Document

#### **Option A: Manual Import (Recommended for Learning)**

Start with critical path tasks:

```bash
Create the following high-priority tasks for Phase 4 (Frontend Development):

1. Add Login/Register CTA buttons to quote results (Task 4.3.5)
   - Priority: CRITICAL
   - Status: NOT_STARTED
   - Effort: 1 hour
   - Feature: Phase 4 - Frontend Development
   - Description: Modify QuoteResults.tsx "Aceptar y Continuar" button to link to /login or /register
   - File: frontend/public_web/components/QuoteResults.tsx

2. Implement quote session storage (Task 4.4.7)
   - Priority: HIGH
   - Status: NOT_STARTED
   - Effort: 2-3 hours
   - Feature: Phase 4 - Frontend Development
   - Description: Use sessionStorage or localStorage to persist quote data, restore on page reload
   - Dependencies: None

3. Integrate NextAuth.js with Django backend (Task 4.2.1)
   - Priority: CRITICAL
   - Status: NOT_STARTED
   - Effort: 4-6 hours
   - Feature: Phase 4 - Frontend Development
   - Description: Setup NextAuth.js, configure Django backend endpoints, implement session management
   - Blocking: All authenticated features
```

#### **Option B: Bulk Import from File**

```bash
I have a detailed migration document at TASK_ORCHESTRATOR_MIGRATION.md. Please read it and import all tasks into the task orchestrator system using bulk operations for efficiency.
```

---

## Using Task Orchestrator - Common Workflows

### Daily Workflow

#### **1. Get Overview of Project**

```bash
Show me the overview of the SicargaBox project with all features and their progress.
```

#### **2. Get Next Recommended Task**

```bash
What's the next task I should work on for SicargaBox? Consider priorities and dependencies.
```

#### **3. Start Working on a Task**

```bash
I'm starting work on task "Add Login/Register CTA buttons". Update its status to IN_PROGRESS.
```

#### **4. Complete a Task**

```bash
I've completed task "Add Login/Register CTA buttons". Mark it as completed and show me the next task.
```

#### **5. Add Implementation Notes**

```bash
Add a section to task "Add Login/Register CTA buttons" with implementation details:
- Modified QuoteResults.tsx line 234
- Added useRouter hook from next/navigation
- Created onClick handler to navigate to /register
- Tested on mobile and desktop
```

### Task Management

#### **Create a New Task**

```bash
Create a new task for Phase 4:
- Title: Create /rastreo tracking page
- Priority: HIGH
- Status: NOT_STARTED
- Description: Public shipment tracking page accessible without login, displays status timeline
- Dependencies: Backend shipment tracking API (Task 1.10)
```

#### **Update Task Status**

```bash
Update task "Implement quote session storage" to IN_PROGRESS
```

#### **Bulk Update Multiple Tasks**

```bash
Mark the following tasks as COMPLETED:
- Task 4.1.1: Initialize Next.js
- Task 4.1.2: Configure TailwindCSS
- Task 4.1.3: Setup theme switching
```

#### **Search for Tasks**

```bash
Find all tasks related to "authentication" that are NOT_STARTED
```

#### **Get Blocked Tasks**

```bash
Show me all tasks that are blocked by dependencies
```

### Feature Management

#### **Get Feature Details**

```bash
Show me the details of "Phase 4: Frontend Development" feature with all its tasks
```

#### **Update Feature Progress**

```bash
Update "Phase 4: Frontend Development" progress to 45%
```

#### **Export Feature to Markdown**

```bash
Export "Phase 1: Backend Foundation" feature to markdown format
```

### Dependency Management

#### **Create Dependencies**

```bash
Create a BLOCKS dependency:
- Task "Integrate NextAuth.js" blocks task "Create customer dashboard"
```

#### **View Dependency Chain**

```bash
Show me the dependency chain for task "Create customer dashboard"
```

### Template Usage

#### **List Available Templates**

```bash
Show me all available templates
```

#### **Apply Template**

```bash
Apply the "implementation_workflow" template to task "Add Login/Register CTA buttons"
```

#### **Create Custom Template**

```bash
Create a new template called "Frontend Feature" with sections:
1. Component Files
2. API Integration
3. Styling Notes
4. Testing Checklist
5. Mobile Responsiveness
```

---

## Advanced Usage

### Working with Sections

#### **Add Documentation Section to Task**

```bash
Add a "Implementation Details" section to task "Quote Calculator UI" with markdown content describing the component structure
```

#### **Add Code Section**

```bash
Add a "Code Changes" section with code format to task "Add CTA buttons" containing the updated QuoteResults.tsx code
```

#### **Bulk Create Sections**

```bash
Add multiple sections to task "Authentication":
1. Setup (markdown): NextAuth configuration steps
2. Environment Variables (code): Required .env.local variables
3. Testing (markdown): Testing checklist
```

### Tracking Progress

#### **Get Statistics**

```bash
Show me statistics for SicargaBox:
- Total tasks
- Completed tasks
- In progress tasks
- Blocked tasks
- By priority breakdown
```

#### **Generate Weekly Report**

```bash
Generate a report of all tasks completed this week in SicargaBox
```

### Working with Tags

#### **List All Tags**

```bash
Show me all tags used in SicargaBox with usage counts
```

#### **Find Tasks by Tag**

```bash
Find all tasks tagged with "authentication" and "critical"
```

---

## Integration with Claude Code

If using Claude Code (claude.ai/code) in VSCode, the task-orchestrator can provide:

1. **Persistent Context**: Tasks and progress survive across sessions
2. **Automatic Updates**: Claude can update task status as it works
3. **Dependency Awareness**: Claude knows what's blocking what
4. **Documentation**: All implementation details stored with tasks

### **Example Claude Code Workflow:**

```bash
Claude: I'm going to work on adding the Login/Register CTA buttons now.

[Claude uses task-orchestrator to:]
1. Update task status to IN_PROGRESS
2. Read task details and dependencies
3. Make code changes
4. Add implementation notes to task
5. Mark task as COMPLETED
6. Get next recommended task
```

---

## Troubleshooting

### Gateway Not Starting

#### **Problem:** `Docker Desktop is not running`

#### **Solution:**

1. Open Docker Desktop application
2. Wait for Docker to fully start (green icon in system tray)
3. Verify: `docker ps` should work
4. Try again

### MCP Commands Not Working from WSL

#### **Problem:** `docker mcp` commands fail in WSL bash

#### **Solution 1:**

- Run through PowerShell: `powershell.exe -Command "docker mcp ..."`
- Or switch to Windows PowerShell terminal

### Gateway Starts but No Tools Available

#### **Problem:** Gateway runs but tools aren't visible

#### **Solution 2:**

1. Check gateway is actually running: `docker ps | grep task-orchestrator`
2. Restart Claude Desktop or MCP client
3. Verify config.json is correct
4. Check gateway logs for errors

### Database/Data Persistence

#### **Problem:** Tasks disappear after restarting

#### **Solution 3:**

- Task-orchestrator uses SQLite with Docker volume `mcp-task-data`
- Data persists across restarts
- To reset: `docker volume rm mcp-task-data`

---

## Data Backup & Export

### Export All Data

```bash
Export the entire SicargaBox project to markdown format including all features, tasks, and sections.
```

### Backup Task Data

The task-orchestrator stores data in Docker volume `mcp-task-data`.

#### **Backup volume:**

```powershell
# Create backup directory
mkdir E:\backups\task-orchestrator

# Copy volume data
docker run --rm -v mcp-task-data:/data -v E:\backups\task-orchestrator:/backup alpine tar czf /backup/task-data-backup.tar.gz -C /data .
```

#### **Restore volume:**

```powershell
# Restore from backup
docker run --rm -v mcp-task-data:/data -v E:\backups\task-orchestrator:/backup alpine sh -c "cd /data && tar xzf /backup/task-data-backup.tar.gz"
```

---

## Best Practices

### Task Creation

✅ Use descriptive task titles
✅ Add clear descriptions
✅ Set realistic priorities
✅ Estimate effort when possible
✅ Link dependencies
✅ Add relevant tags

### Task Updates

✅ Update status as you work (NOT_STARTED → IN_PROGRESS → COMPLETED)
✅ Add implementation notes
✅ Document blockers
✅ Update progress regularly

### Organization

✅ Group related tasks into features
✅ Use consistent naming conventions
✅ Apply templates for consistency
✅ Review blocked tasks weekly
✅ Archive completed features

### Integration with Development

✅ Update tasks BEFORE committing code
✅ Reference task IDs in commit messages
✅ Add code snippets to task sections
✅ Document decisions in task notes

---

## Example Session

```bash
User: Start the task orchestrator and set up my SicargaBox project

Claude: [Starts gateway]
I've started the task-orchestrator MCP gateway on port 3000. Now let me initialize the project...

[Uses initialize_task_orchestrator prompt]
[Creates SicargaBox project]
[Creates 7 main features]
[Imports critical path tasks]

Your SicargaBox project is now set up in task-orchestrator with:
- 7 features (Phases 0-6)
- 45 high-priority tasks imported
- Dependencies mapped
- Ready for development tracking

Next recommended task: "Add Login/Register CTA buttons to quote results" (1 hour, CRITICAL priority)

Would you like me to start working on this task?

User: Yes, let's do it

Claude: [Updates task to IN_PROGRESS]
I'm now working on adding Login/Register CTA buttons...

[Makes code changes]
[Tests changes]
[Adds implementation notes to task]
[Marks task COMPLETED]

Task completed! I've added the CTAs to QuoteResults.tsx.

Next recommended task: "Implement quote session storage" (2-3 hours, HIGH priority)

Ready to continue?
```

---

## Resources

### **Task Orchestrator:**

- GitHub: <https://github.com/jpicklyk/task-orchestrator>
- Docker Hub: ghcr.io/jpicklyk/task-orchestrator
- Documentation: Check GitHub repo for latest docs

#### **MCP Protocol:**

- Spec: <https://modelcontextprotocol.io>
- Docker MCP: <https://docs.docker.com/mcp/>

#### **SicargaBox Project:**

- Master Task List: `MASTER_TASK_LIST.md`
- Migration Doc: `TASK_ORCHESTRATOR_MIGRATION.md`
- Project Docs: `CLAUDE.md` and other `*_PLAN.md` files

---

#### **End of Setup Guide**

You're now ready to use task-orchestrator with your SicargaBox project! Start the gateway and begin tracking your development tasks with persistent AI memory across sessions.
