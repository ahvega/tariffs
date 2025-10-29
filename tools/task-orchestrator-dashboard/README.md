# Task Orchestrator Dashboard

A lightweight, single-page dashboard for monitoring [MCP Task Orchestrator](https://github.com/jpicklyk/task-orchestrator) progress in real-time.

## 🎯 Overview

This dashboard provides a visual interface for monitoring task-orchestrator projects, features, and tasks. While task-orchestrator is designed to be AI-native, this tool gives developers a quick visual overview of their task hierarchy and progress.

**Features:**
- 📊 Real-time stats (projects, features, tasks, completion rate)
- 🔄 Auto-refresh every 10 seconds
- 📦 Self-contained: 2 files (Python backend + HTML frontend)
- 🚀 Fast: FastAPI backend reads directly from SQLite
- 💡 Clean UI: No framework dependencies in frontend
- 🔌 Standalone: Can run alongside any project using task-orchestrator

## 📁 Project Structure

```
task-orchestrator-dashboard/
├── server.py            # FastAPI backend (reads SQLite)
├── dashboard.html       # Single-page dashboard UI
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env.example        # Example configuration (with Docker paths)
├── .gitignore          # Git ignore rules
├── find_docker_db.sh   # Helper script (Linux/macOS)
└── find_docker_db.ps1  # Helper script (Windows PowerShell)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Task Orchestrator MCP running and creating `tasks.db`

### Setup

1. **Navigate to dashboard directory:**
   ```bash
   cd tools/task-orchestrator-dashboard
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database path (optional):**
   ```bash
   # Copy example config
   cp .env.example .env

   # Edit .env to point to your task-orchestrator database
   # Default: data/tasks.db
   ```

5. **Run the dashboard:**
   ```bash
   python server.py
   ```

6. **Open in browser:**
   ```
   http://localhost:8000
   ```

## ⚙️ Configuration

The dashboard looks for the task-orchestrator SQLite database at these locations (in order):

1. `TASK_ORCHESTRATOR_DB` environment variable
2. Default: `data/tasks.db` (relative to dashboard directory)

**Set custom database path:**

```bash
# Option 1: Environment variable
export TASK_ORCHESTRATOR_DB=/path/to/your/tasks.db
python server.py

# Option 2: .env file
echo "TASK_ORCHESTRATOR_DB=/path/to/your/tasks.db" > .env
python server.py
```

**For Docker-based task-orchestrator:**

If you're running task-orchestrator via MCP Docker toolkit, use the helper scripts to find your database:

```bash
# Linux/macOS
./find_docker_db.sh

# Windows PowerShell
.\find_docker_db.ps1
```

The scripts will:
- Detect your Docker volume location
- Show the full path to `tasks.db`
- Provide the exact line to add to your `.env` file

**Manual method:**

```bash
# Find Docker volume
docker volume inspect mcp-task-data

# Common paths:
# Linux/macOS: /var/lib/docker/volumes/mcp-task-data/_data/tasks.db
# Windows WSL2: \\wsl$\docker-desktop-data\data\docker\volumes\mcp-task-data\_data\tasks.db
```

**Alternative: Copy database from container (Recommended for Windows):**

```bash
mkdir data
docker compose cp mcp-task-orchestrator:/app/data/tasks.db ./data/tasks.db
# Then use: TASK_ORCHESTRATOR_DB=data/tasks.db
```

## 📖 Usage

### Development Workflow

1. Start the dashboard server:
   ```bash
   python server.py
   ```

2. Keep the dashboard open in a browser tab while you work

3. As your AI assistant (Claude Code, Cursor, etc.) updates tasks via task-orchestrator MCP, the dashboard auto-refreshes every 10 seconds

### API Endpoints

The FastAPI backend also provides a REST API:

- `GET /api/health` - Health check
- `GET /api/stats` - Overall statistics
- `GET /api/projects` - All projects with features and tasks
- `GET /api/projects/{id}` - Specific project details
- `GET /api/tasks/recent?limit=20` - Recently updated tasks

**Interactive API docs:** http://localhost:8000/docs

## 🔌 Integration with Other Projects

This dashboard is **project-agnostic** and can monitor any project using task-orchestrator.

### Option 1: Monorepo (Current Setup)

Keep the dashboard in `tools/task-orchestrator-dashboard/` and use it across multiple projects in the monorepo.

### Option 2: Standalone Installation

Copy this directory to any project:

```bash
# In your new project
mkdir -p tools
cp -r /path/to/task-orchestrator-dashboard tools/

cd tools/task-orchestrator-dashboard
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python server.py
```

### Option 3: System-wide Installation

Install once, use everywhere:

```bash
# Clone to a global location
git clone <future-repo-url> ~/task-orchestrator-dashboard
cd ~/task-orchestrator-dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create a shell alias
echo 'alias task-dash="cd ~/task-orchestrator-dashboard && source venv/bin/activate && python server.py"' >> ~/.bashrc

# Usage from any project
task-dash
```

## 📦 Making it an Independent Project

This dashboard is designed to be easily extracted into its own repository:

### Current State (Monorepo)
- Lives in `tools/task-orchestrator-dashboard/`
- Git tracks it as part of the tariffs project
- Self-contained with its own venv and dependencies

### Future: Independent Repository

**Option A: Git Subtree Split**
```bash
# Split into separate repo (preserves history)
git subtree split --prefix=tools/task-orchestrator-dashboard -b dashboard-branch
cd ../
git clone <new-repo-url> task-orchestrator-dashboard
cd task-orchestrator-dashboard
git pull ../tariffs dashboard-branch
```

**Option B: Clean Start**
```bash
# Copy to new repo (fresh history)
cp -r tools/task-orchestrator-dashboard ../task-orchestrator-dashboard
cd ../task-orchestrator-dashboard
git init
git add .
git commit -m "Initial commit: Task Orchestrator Dashboard"
```

### Publishing as a Package

**PyPI Package (future):**
```bash
pip install task-orchestrator-dashboard
task-orchestrator-dashboard --db-path=/path/to/tasks.db
```

**NPM Package (alternative):**
```bash
npm install -g task-orchestrator-dashboard
task-orchestrator-dashboard
```

## 🛠️ Development

### File Organization

Keep these principles to maintain independence:

1. ✅ **No external imports** from parent project
2. ✅ **Self-contained dependencies** in requirements.txt
3. ✅ **Relative paths** or environment variables for config
4. ✅ **Standalone documentation** in README.md

### Source Control Strategy

**While in Monorepo:**
- Commit dashboard changes to the main tariffs repo
- Keep commits focused on dashboard when possible
- Use clear commit messages: `[dashboard] Add feature X`

**Preparing for Independence:**
- Avoid dependencies on parent project code
- Keep all assets (HTML, CSS, JS) self-contained
- Document all assumptions and requirements

### Testing

```bash
# Run with test database
TASK_ORCHESTRATOR_DB=test_data/tasks.db python server.py

# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/projects
```

## 🐛 Troubleshooting

### Database not found

**Error:** `Database not found at data/tasks.db`

**Solution:**
```bash
# Find your task-orchestrator database
# For Docker-based MCP:
docker volume ls
docker volume inspect <task-orchestrator-volume>

# Set the correct path
export TASK_ORCHESTRATOR_DB=/path/to/actual/tasks.db
```

### Port already in use

**Error:** `Address already in use: port 8000`

**Solution:**
```bash
# Option 1: Kill process on port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Option 2: Use different port
# Edit server.py and change the port in uvicorn.run()
```

### CORS errors in browser

**Error:** `Access to fetch at 'http://localhost:8000' from origin 'file://' has been blocked`

**Solution:** Always access the dashboard through http://localhost:8000 (served by the Python server), not by opening dashboard.html directly in the browser.

## 📝 License

[Choose license when extracting to independent repo]

## 🤝 Contributing

This dashboard is currently part of the SicargaBox tariffs project but designed for independence.

**Current contributors:** Submit PRs to the main tariffs repository
**Future:** Will accept PRs at independent repository URL

## 🔗 Related Projects

- [MCP Task Orchestrator](https://github.com/jpicklyk/task-orchestrator) - The task orchestration system this dashboard monitors
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol powering MCP tools

## 📧 Support

- **Issues:** [Create issue in tariffs repo](https://github.com/yourusername/tariffs/issues) (for now)
- **Discussions:** [Start a discussion](https://github.com/yourusername/tariffs/discussions)

---

**Built with ❤️ for developers who want visibility into their AI-managed tasks**
