# Task Orchestrator - Quick Reference Card

**SicargaBox Project Management**
**Date:** 2025-10-27

---

## 🚀 Quick Start

```powershell
# Start task-orchestrator gateway
docker mcp gateway run --servers task-orchestrator --port 3000

# Or from WSL
powershell.exe -Command "docker mcp gateway run --servers task-orchestrator --port 3000"
```

---

## 📋 42 Available Tools

### Task Management (12 tools)

| Tool | Description | Example |
|------|-------------|---------|
| `create_task` | Create new task | Create task "Add login page" |
| `update_task` | Modify task | Update task priority to CRITICAL |
| `get_task` | Get task details | Show task "Add login page" |
| `search_tasks` | Find tasks | Search tasks with status IN_PROGRESS |
| `delete_task` | Remove task | Delete task "Old feature" |
| `set_status` | Update status | Set task status to COMPLETED |
| `bulk_update_tasks` | Update multiple | Mark 10 tasks as completed |
| `get_next_task` | Get recommendation | What should I work on next? |
| `get_blocked_tasks` | Find blockers | Show blocked tasks |
| `get_overview` | Project overview | Show project overview |
| `list_tags` | Show all tags | List all tags with counts |
| `task_to_markdown` | Export task | Export task to markdown |

### Feature Management (6 tools)

| Tool | Description | Example |
|------|-------------|---------|
| `create_feature` | Create feature | Create feature "Authentication" |
| `update_feature` | Modify feature | Update feature status |
| `get_feature` | Get details | Show feature with tasks |
| `search_features` | Find features | Search features by status |
| `delete_feature` | Remove feature | Delete feature "Old module" |
| `feature_to_markdown` | Export | Export feature to markdown |

### Project Management (6 tools)

| Tool | Description | Example |
|------|-------------|---------|
| `create_project` | Create project | Create project "SicargaBox" |
| `update_project` | Modify project | Update project status |
| `get_project` | Get details | Show project overview |
| `search_projects` | Find projects | List all projects |
| `delete_project` | Remove project | Delete project "Archive" |
| `project_to_markdown` | Export | Export project to markdown |

### Dependency Management (3 tools)

| Tool | Description | Example |
|------|-------------|---------|
| `create_dependency` | Link tasks | Task A blocks Task B |
| `get_task_dependencies` | View chain | Show dependencies for task |
| `delete_dependency` | Remove link | Delete dependency |

### Section Management (9 tools)

| Tool | Description | Example |
|------|-------------|---------|
| `add_section` | Add content | Add implementation notes |
| `get_sections` | View sections | Show all task sections |
| `update_section` | Modify section | Update section content |
| `update_section_text` | Replace text | Replace section text |
| `update_section_metadata` | Change metadata | Update section title |
| `delete_section` | Remove section | Delete old notes |
| `reorder_sections` | Change order | Move section up |
| `bulk_create_sections` | Add multiple | Add 3 sections at once |
| `bulk_update_sections` | Update multiple | Update all sections |

### Template Management (9 tools)

| Tool | Description | Example |
|------|-------------|---------|
| `list_templates` | Show templates | List available templates |
| `get_template` | View template | Show template details |
| `apply_template` | Use template | Apply to task |
| `create_template` | New template | Create custom template |
| `add_template_section` | Add section | Add section to template |
| `update_template_metadata` | Modify template | Update template name |
| `enable_template` | Activate | Make template available |
| `disable_template` | Deactivate | Restrict template |
| `delete_template` | Remove | Delete custom template |

### Built-in Prompts (6 prompts)

| Prompt | Purpose |
|--------|---------|
| `initialize_task_orchestrator` | AI initialization and setup |
| `create_feature_workflow` | Comprehensive feature creation |
| `task_breakdown_workflow` | Complex task decomposition |
| `project_setup_workflow` | Complete project initialization |
| `implementation_workflow` | Git-aware implementation with validation |

---

## 💡 Common Commands

### Daily Workflow

```bash
# Morning - Get context
"Show me the SicargaBox project overview"
"What's the next high-priority task?"
"Show me all tasks I'm currently working on"

# Start work
"I'm starting work on [task name]. Update status to IN_PROGRESS"

# During work
"Add implementation notes to [task]: [details]"
"This task is blocked by [reason]"

# Complete work
"Mark [task] as COMPLETED and show next task"
```

### Task Status Updates

```bash
# Status options: NOT_STARTED, IN_PROGRESS, COMPLETED
"Set task [name] status to IN_PROGRESS"
"Mark task [name] as COMPLETED"
"Update all authentication tasks to COMPLETED"
```

### Priority Management

```bash
# Priority options: LOW, MEDIUM, HIGH, CRITICAL
"Set task [name] priority to CRITICAL"
"Show all CRITICAL priority tasks"
"Find HIGH priority tasks that are NOT_STARTED"
```bash

### Search & Filter

```bash
"Search for tasks containing 'authentication'"
"Find all tasks tagged with 'frontend'"
"Show tasks with status IN_PROGRESS and priority HIGH"
"List all blocked tasks"
"Show tasks assigned to Phase 4"
```

### Dependencies

```bash
"Task A blocks Task B"
"Task X depends on Task Y"
"Show dependency chain for [task]"
"Find all tasks blocking [task]"
```

### Documentation

```bash
"Add section 'Implementation Details' to [task] with: [content]"
"Add code section to [task] with file changes"
"Export [task] to markdown"
"Export entire project to markdown"
```

---

## 🎯 SicargaBox Specific Commands

### Get Current Status

```bash
"Show SicargaBox project status"
"What's the progress on Phase 4 Frontend?"
"Show all frontend tasks"
"Get overview of authentication feature"
```

### Work on Critical Path

```bash
"Show next critical path task for frontend"
"What's blocking the quote acceptance flow?"
"Show all tasks needed before MVP launch"
```

### Update Progress

```bash
"Update Phase 4 progress to 45%"
"Mark Quote Calculator UI as 95% complete"
"All foundation tasks are done"
```

### Generate Reports

```bash
"Show weekly progress report"
"List all completed tasks this week"
"Show statistics by phase"
"Export Phase 1 to markdown"
```

---

## 📊 Status & Priority Reference

### Task Status

- `NOT_STARTED` - Not yet begun
- `IN_PROGRESS` - Currently working
- `COMPLETED` - Finished

### Priority Levels

- `CRITICAL` - Must complete ASAP, blocking
- `HIGH` - Important, should do soon
- `MEDIUM` - Normal priority
- `LOW` - Nice to have, can defer

### Dependency Types

- `BLOCKS` - This task blocks another
- `IS_BLOCKED_BY` - This task is blocked
- `RELATES_TO` - Related but not blocking

---

## 🔧 Troubleshooting Quick Fixes

```powershell
# Gateway won't start
docker ps  # Check Docker is running
docker context use default  # Switch to default context

# Reset task data (CAUTION: Deletes all data)
docker volume rm mcp-task-data

# View gateway logs
docker logs <container-id>

# Check running containers
docker ps | grep task-orchestrator
```

---

## 💾 Keyboard Shortcuts (Claude Desktop)

When MCP is configured in Claude Desktop:

```bash
Ctrl+K → Open command palette
Type "task" → See task-orchestrator tools
Select tool → Fill parameters
Enter → Execute
```

---

## 📁 File Locations

```bash
Migration Document: /mnt/e/mydevtools/tariffs/TASK_ORCHESTRATOR_MIGRATION.md
Setup Guide: /mnt/e/mydevtools/tariffs/TASK_ORCHESTRATOR_SETUP_GUIDE.md
Master Task List: /mnt/e/mydevtools/tariffs/MASTER_TASK_LIST.md
Quick Reference: /mnt/e/mydevtools/tariffs/TASK_ORCHESTRATOR_QUICK_REFERENCE.md
```

---

## 🎨 Section Format Types

When adding sections to tasks:

- `MARKDOWN` - Formatted text with markdown
- `JSON` - Structured JSON data
- `CODE` - Source code snippets
- `PLAIN_TEXT` - Plain text content

**Example:**

```bash
Add a CODE section to task "Add CTA buttons" containing the updated QuoteResults.tsx component
```

---

## 🏆 Best Practices Checklist

✅ Update task status as you work (NOT_STARTED → IN_PROGRESS → COMPLETED)
✅ Add implementation notes before marking complete
✅ Set dependencies for blocked tasks
✅ Use consistent tag names
✅ Keep task descriptions clear and actionable
✅ Review get_next_task recommendations daily
✅ Export important features to markdown for backup
✅ Use bulk operations for efficiency (70-95% token savings)

---

## 📞 Quick Help

```bash
# Get help on any tool
"How do I use bulk_update_tasks?"
"What parameters does create_task accept?"
"Show example of add_section"

# List capabilities
"What can task-orchestrator do?"
"Show all available templates"
"List all tags in use"
```

---

## 🔗 Integration Example

**Git Workflow Integration:**

```bash
# Before starting work
git checkout -b feature/add-login-ctas

# Update task in orchestrator
"Set task 'Add Login/Register CTAs' to IN_PROGRESS"

# Do work...
# Make changes to code

# Add notes to task
"Add implementation notes to 'Add Login/Register CTAs':
- Modified QuoteResults.tsx line 234
- Added useRouter hook
- Created onClick handler
- Tested on mobile and desktop"

# Commit with task reference
git commit -m "feat: Add login/register CTAs to quote results

Refs: Task 4.3.5 - Add Login/Register CTA buttons
Completed: QuoteResults component now has working CTA buttons
that navigate to /register page after quote calculation"

# Mark complete
"Mark task 'Add Login/Register CTAs' as COMPLETED"

# Get next task
"What should I work on next?"
```

---

## 🌟 Power User Tips

1. **Use Bulk Operations**: Update multiple tasks at once to save tokens
2. **Apply Templates**: Consistent documentation across similar tasks
3. **Track Dependencies**: Prevents working on blocked tasks
4. **Tag Everything**: Makes searching much easier
5. **Add Sections**: Rich documentation with code, notes, and links
6. **Export Regularly**: Backup to markdown for safety
7. **Review Weekly**: Check blocked tasks and update priorities
8. **Use get_next_task**: Let AI recommend what to work on

---

**Need more help?** See [TASK_ORCHESTRATOR_SETUP_GUIDE.md](TASK_ORCHESTRATOR_SETUP_GUIDE.md) for detailed instructions.

**Ready to migrate?** See [TASK_ORCHESTRATOR_MIGRATION.md](TASK_ORCHESTRATOR_MIGRATION.md) for complete task list.
