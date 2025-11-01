# Task Orchestrator Dashboard v2.0

**Real-time monitoring dashboard for MCP Task Orchestrator with Docker integration**

## 🎬 The Inception Moment: Dashboard Tracking Itself

**Project ID:** `7c39484d-6cea-4d8c-b1bd-dc2466a97303`

The Task Orchestrator Dashboard now tracks its own development! This meta-project demonstrates the system's capabilities by using it to manage the dashboard's development lifecycle.

**🎯 Live in Dashboard:** Select "Task Orchestrator Dashboard" project to see:
- 6 Features (Phases 1-6) with 2 completed
- 8 Tasks across visualization, analytics, and deployment
- Complete project roadmap with priorities and complexity ratings

_"We have to go deeper..."_ - See `META_PROJECT.md` for details.

---

## 🎯 What's New in v2.0

### Phase 1: Infrastructure (COMPLETE)

- ✅ **Real-Time Updates** - WebSocket-based live data synchronization (1-2 second latency)
- ✅ **Docker Integration** - Automatic Docker volume detection and access
- ✅ **Connection Pooling** - Efficient concurrent request handling
- ✅ **Enhanced API** - 10+ new endpoints exposing all database tables
- ✅ **Comprehensive Data** - Access to dependencies, sections, tags, templates, work sessions, locks

### Phase 2: Visual Enhancements (COMPLETE)

- ✅ **Multi-View Dashboard** - Overview, Kanban, Graph, and Analytics views
- ✅ **Dependency Graph** - Interactive task visualization with Cytoscape.js
- ✅ **Kanban Board** - 4-column task board with blocked task detection
- ✅ **Timeline Feed** - Chronological activity updates
- ✅ **Detail Modals** - Comprehensive task/feature information
- ✅ **Global Search** - Autocomplete search with Ctrl+K shortcut
- ✅ **Analytics Dashboard** - Charts and metrics with Chart.js

### Architecture

- Component-based frontend architecture
- Event-driven real-time updates
- Modular service layer (`services/` directory)
- Thread-safe database connection pooling
- WebSocket manager with database file watching
- Docker volume auto-detection with platform-specific strategies
- Graceful degradation (WebSocket fallback to polling)

## 🚀 Quick Start

### Installation

```bash
cd tools/task-orchestrator-dashboard

# Activate virtual environment
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Running v2.0

**Option 1: Use PowerShell startup script (Windows)**

```powershell
.\start-server-v2.ps1
```

**Option 2: Direct Python**

```bash
python server_v2.py
```

**Option 3: With custom configuration**

```bash
# Set environment variables
set TASK_ORCHESTRATOR_DB=path\to\tasks.db
set ENABLE_WEBSOCKET=true
set ENABLE_DOCKER_DETECTION=true

python server_v2.py
```

### Accessing the Dashboard

- **Web UI**: <http://localhost:8888>
- **API Docs**: <http://localhost:8888/docs>
- **Health Check**: <http://localhost:8888/api/health>

## 📚 Documentation

- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Complete 7-phase implementation plan
- **[PHASE1_SUMMARY.md](PHASE1_SUMMARY.md)** - Detailed Phase 1 summary with metrics
- **[PHASE1_TESTING_GUIDE.md](PHASE1_TESTING_GUIDE.md)** - Comprehensive testing guide

## 🔧 New API Endpoints

### Enhanced Endpoints

- `GET /api/stats` - Now includes dependencies, sections, templates counts
- `GET /api/health` - Includes WebSocket connection count and version

### New Endpoints

- `GET /api/dependencies` - All task dependencies with task names
- `GET /api/tasks/{task_id}/dependencies` - Task-specific dependencies
- `GET /api/sections` - Documentation sections (filterable)
- `GET /api/tags` - Tag usage statistics across all entities
- `GET /api/templates` - Available templates
- `GET /api/work-sessions` - Active AI agent sessions
- `GET /api/task-locks` - Current task locks
- `GET /api/analytics/overview` - Comprehensive analytics data
- `GET /api/search` - Global search across projects/features/tasks
- `WebSocket /ws` - Real-time update stream

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TASK_ORCHESTRATOR_DB` | `data/tasks.db` | Path to task-orchestrator database |
| `ENABLE_WEBSOCKET` | `true` | Enable WebSocket real-time updates |
| `ENABLE_DOCKER_DETECTION` | `true` | Auto-detect Docker volumes |

### Docker Volume Access

The dashboard automatically detects Docker volumes using platform-specific strategies:

**Linux/macOS:**

- Direct access to volume mount at `/var/lib/docker/volumes/mcp-task-data/_data`

**Windows with Docker Desktop:**

- WSL network path: `\\wsl.localhost\docker-desktop-data\data\docker\volumes\mcp-task-data\_data\tasks.db`
- Or: `\\wsl$\docker-desktop-data\data\docker\volumes\mcp-task-data\_data\tasks.db`

**Fallback (all platforms):**

```bash
# Manual copy from container
docker cp mcp-task-orchestrator:/app/data/tasks.db ./data/tasks.db
```

## 🧪 Testing

### Component Tests

```bash
python test_phase1.py
```

Expected output:

```
[PASS] Services imported successfully
[PASS] Docker detection test passed
[PASS] Database pool test passed
[PASS] WebSocket manager test passed
[PASS] ALL TESTS PASSED
```

### API Tests

```bash
# Health check
curl http://localhost:8888/api/health

# Get enhanced stats
curl http://localhost:8888/api/stats

# Search
curl "http://localhost:8888/api/search?q=authentication"
```

### WebSocket Test (Browser Console)

```javascript
const ws = new WebSocket('ws://localhost:8888/ws');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

## 📊 Performance Metrics

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| Update Latency | 10s | 1-2s | 83% faster |
| API Endpoints | 5 | 15+ | 3x more |
| Database Tables | 3 | 13 | 4.3x coverage |
| Concurrent Requests | Limited | Excellent | Unlimited |
| Real-Time Updates | ❌ | ✅ | New feature |

## 🔄 Backward Compatibility

v2.0 is fully backward compatible with v1.0:

- Original `server.py` still works
- No changes to database schema required
- Existing `dashboard.html` compatible with both servers
- Can run v1.0 and v2.0 side-by-side (different ports)

## 🗂️ Project Structure

```
tools/task-orchestrator-dashboard/
├── services/                      # NEW: Service layer
│   ├── __init__.py
│   ├── docker_volume_detector.py  # Docker integration
│   ├── websocket_manager.py       # WebSocket real-time updates
│   └── database_pool.py           # Connection pooling
├── server.py                      # v1.0 (original)
├── server_v2.py                   # NEW: v2.0 with Phase 1 features
├── dashboard.html                 # Original dashboard UI
├── dashboard_v1_backup.html       # Backup of original
├── requirements.txt               # Updated with new dependencies
├── test_phase1.py                 # NEW: Component tests
├── start-server-v2.ps1           # NEW: Windows startup script
├── README.md                      # Original README
├── README_V2.md                   # This file
├── IMPLEMENTATION_PLAN.md         # NEW: Complete implementation plan
├── PHASE1_SUMMARY.md              # NEW: Phase 1 detailed summary
└── PHASE1_TESTING_GUIDE.md        # NEW: Comprehensive testing guide
```

## 🔍 Troubleshooting

### Database not found

```bash
# Check if database exists
ls data/tasks.db

# Copy from Docker
docker cp mcp-task-orchestrator:/app/data/tasks.db ./data/tasks.db

# Or set custom path
set TASK_ORCHESTRATOR_DB=C:\path\to\tasks.db
```

### Docker connection failed

```bash
# Disable Docker detection
set ENABLE_DOCKER_DETECTION=false
python server_v2.py
```

### WebSocket issues

```bash
# Disable WebSocket (fallback to polling)
set ENABLE_WEBSOCKET=false
python server_v2.py
```

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python test_phase1.py
```

## 🎯 Roadmap

### ✅ Phase 1: Infrastructure (COMPLETE)

- Real-time WebSocket updates
- Docker integration
- Connection pooling
- Enhanced API endpoints

### ✅ Phase 2: Visual Enhancements (COMPLETE)

- Dependency graph visualization (Cytoscape.js)
- Kanban board view (4 columns)

## 🐳 Docker

Run the dashboard as an independent container alongside the MCP server while reading the same live database volume.

### Requirements

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- The MCP server’s named volume: `mcp-task-data` (contains `tasks.db`)

### Using Docker Compose (recommended)

```bash
docker compose up --build -d
# Open http://localhost:8888
```

Compose mounts the external volume `mcp-task-data` to `/data:ro` and sets:

- `TASK_ORCHESTRATOR_DB=/data/tasks.db`
- `ENABLE_WEBSOCKET=true`
- `ENABLE_DOCKER_DETECTION=false` (not needed inside the container)

### Using Docker directly

```bash
docker build -t task-orchestrator-dashboard .
docker run --rm -p 8888:8888 \
  -e TASK_ORCHESTRATOR_DB=/data/tasks.db \
  -e ENABLE_WEBSOCKET=true \
  -e ENABLE_DOCKER_DETECTION=false \
  -v mcp-task-data:/data:ro \
  task-orchestrator-dashboard
```

### Helper Commands

- PowerShell (Windows):
  - Start: `./docker-up.ps1 -Port 8888`
  - Stop: `./docker-down.ps1`
  - Logs: `./docker-logs.ps1`
- Make (macOS/Linux):
  - Start: `make up PORT=8888`
  - Stop: `make down`
  - Logs: `make logs`

### Environment File (optional)

Copy `.env.example` to `.env` to override defaults used by `docker-compose.yml`:

```
cp .env.example .env
# or on Windows PowerShell
Copy-Item .env.example .env
```

Editable keys:

- `DASHBOARD_PORT` (host port)
- `TASK_ORCHESTRATOR_DB` (container DB path)
- `ENABLE_WEBSOCKET`, `ENABLE_DOCKER_DETECTION`

### Troubleshooting (Docker)

- Volume not found: ensure the MCP container created `mcp-task-data` or create/copy `tasks.db` into a new named volume.
- Custom volume name/path: adjust `docker-compose.yml` (volume name) or `TASK_ORCHESTRATOR_DB`.
- Port conflict: change host port (e.g., `-p 8890:8888`) and open `http://localhost:8890`.
- Health check: `curl http://localhost:8888/api/health` should show `status: healthy` and `version: 2.0.0`.
- Timeline/activity feed
- Enhanced detail modals
- Global search with autocomplete
- Analytics dashboard (Chart.js)

### 🔄 Phase 3: Advanced Features (PLANNED)

- Search UI with filters
- Multi-view switcher
- Analytics dashboard
- Notification system

### 🔄 Phase 4: Polish & Testing (PLANNED)

- Comprehensive test suite
- Performance optimization
- Documentation completion

### 🔄 Phase 5: Deployment (PLANNED)

- Docker containerization
- Standalone executable
- Release v2.0 final

## 📝 Contributing

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for architecture details and contribution guidelines.

## 📄 License

Same as parent project (MIT License)

## 🙏 Acknowledgments

Built on top of [task-orchestrator](https://github.com/jpicklyk/task-orchestrator) by jpicklyk

---

**Version:** 2.0.0 (Phase 2)
**Status:** ✅ Complete and Ready for Use
**Last Updated:** 2025-10-29

## 📚 Documentation

- **[PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)** - Phase 1 completion summary
- **[PHASE2_COMPLETE.md](PHASE2_COMPLETE.md)** - Phase 2 completion summary
- **[PHASE2_PLAN.md](PHASE2_PLAN.md)** - Phase 2 implementation plan
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Complete 7-phase roadmap
