#!/usr/bin/env python3
"""
Task Orchestrator Dashboard Server - Version 2.0
Phase 1: Real-Time Infrastructure with Docker Integration

Features:
- Docker volume auto-detection
- WebSocket real-time updates
- Database connection pooling
- Enhanced API endpoints (dependencies, sections, tags, analytics)
"""

import os
import base64
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Import custom services
from services import DockerVolumeDetector, WebSocketManager, DatabasePool
from services.database_pool import dict_from_row, rows_to_dicts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_DB_PATH = os.getenv("TASK_ORCHESTRATOR_DB", "data/tasks.db")
ENABLE_DOCKER_DETECTION = os.getenv("ENABLE_DOCKER_DETECTION", "true").lower() == "true"
ENABLE_WEBSOCKET = os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true"

# Initialize FastAPI app
app = FastAPI(
    title="Task Orchestrator Dashboard",
    version="2.0.0",
    description="Real-time monitoring dashboard for MCP Task Orchestrator"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for JavaScript, CSS, etc.
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Global state
ws_manager = WebSocketManager()
db_pool: Optional[DatabasePool] = None


# Pydantic Models
class TaskStatus(BaseModel):
    """Task model returned to the frontend"""
    id: str
    title: str
    status: str
    summary: Optional[str] = None
    # Backward/compat fields (kept if used elsewhere)
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    complexity: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    feature_id: Optional[str] = None
    project_id: Optional[str] = None  # Computed from task.project_id or feature.project_id


class Feature(BaseModel):
    """Feature model"""
    id: str
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    project_id: Optional[str] = None
    tasks: List[TaskStatus] = []


class Project(BaseModel):
    """Project model"""
    id: str
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    features: List[Feature] = []


class DependencyResponse(BaseModel):
    """Dependency model"""
    id: str
    from_task_id: str
    to_task_id: str
    type: str
    created_at: str
    from_task_title: Optional[str] = None
    to_task_title: Optional[str] = None


class SectionResponse(BaseModel):
    """Section model"""
    id: str
    entity_type: str
    entity_id: str
    title: str
    usage_description: str
    content: str
    content_format: str
    ordinal: int
    tags: str
    created_at: str
    modified_at: str


class TagResponse(BaseModel):
    """Tag model with usage count"""
    tag: str
    count: int
    entity_types: List[str]


# Helper functions
def get_db_pool() -> DatabasePool:
    """Get database connection pool"""
    if db_pool is None:
        raise HTTPException(
            status_code=503,
            detail="Database not initialized"
        )
    return db_pool


def _normalize_status(raw_status: Optional[str]) -> Optional[str]:
    """Map DB status values to UI-friendly values used by the frontend."""
    if not raw_status:
        return raw_status
    s = raw_status.strip().upper()
    mapping = {
        'IN_PROGRESS': 'in-progress',
        'INPROGRESS': 'in-progress',
        'DOING': 'in-progress',
        'COMPLETED': 'completed',
        'DONE': 'completed',
        'PENDING': 'pending',
        'TODO': 'pending',
        'BLOCKED': 'blocked',
        'CANCELLED': 'cancelled',
        'DEFERRED': 'deferred',
    }
    return mapping.get(s, raw_status.lower())


def _task_from_row(row) -> dict:
    """Convert sqlite3.Row to a task dict with expected frontend fields."""
    d = dict_from_row(row)
    # Preserve title/summary as expected by frontend
    title = d.get('title') or d.get('name') or ''
    summary = d.get('summary') or d.get('description')
    status = _normalize_status(d.get('status'))
    result = {
        **d,
        'title': title,
        'summary': summary,
        'status': status,
        # Optional compatibility duplicates
        'name': title,
        'description': summary,
    }
    # UI expects modified_at; mirror from updated_at if present
    if 'updated_at' in d and d.get('updated_at') and not d.get('modified_at'):
        result['modified_at'] = d.get('updated_at')
    return result


def _uuid_params(uuid_str: str):
    """Return tuple (uuid_bytes_or_None, original_str) for dual-typed UUID columns."""
    try:
        return (bytes.fromhex(uuid_str.replace('-', '')), uuid_str)
    except Exception:
        return (None, uuid_str)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global db_pool

    logger.info("=" * 60)
    logger.info("Task Orchestrator Dashboard - Starting")
    logger.info("=" * 60)

    # Detect Docker volume if enabled
    db_path = DEFAULT_DB_PATH
    is_docker_volume = False
    
    if ENABLE_DOCKER_DETECTION:
        logger.info("Docker detection enabled, checking for volumes...")
        detector = DockerVolumeDetector()
        detected_path = detector.get_recommended_path(DEFAULT_DB_PATH)
        if detected_path != DEFAULT_DB_PATH:
            db_path = detected_path
            is_docker_volume = True
    
    # Check if path contains Docker volume indicators
    if 'docker' in db_path.lower() or 'wsl' in db_path.lower():
        is_docker_volume = True

    logger.info(f"Using database: {db_path}")
    if is_docker_volume:
        logger.info("⚠️  Docker volume detected - enabling READ-ONLY mode to prevent locking")

    # Initialize database pool
    try:
        db_pool = DatabasePool(db_path, read_only=is_docker_volume)
        logger.info(f"Database pool initialized successfully (read_only={is_docker_volume})")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise

    # Start WebSocket database watcher if enabled
    if ENABLE_WEBSOCKET:
        logger.info("Starting WebSocket database watcher...")
        await ws_manager.start_watching(db_path)
        logger.info("WebSocket watcher started")

    logger.info("=" * 60)
    logger.info("Dashboard server ready!")
    logger.info(f"WebSocket support: {'Enabled' if ENABLE_WEBSOCKET else 'Disabled'}")
    logger.info(f"Docker detection: {'Enabled' if ENABLE_DOCKER_DETECTION else 'Disabled'}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")

    if ws_manager:
        await ws_manager.stop_watching()

    if db_pool:
        db_pool.close_all()

    logger.info("Shutdown complete")


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()

            # Handle ping/pong
            if data == "ping":
                await ws_manager.send_to_client(websocket, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket)


# Basic endpoints
@app.get("/")
async def root():
    """Serve the dashboard HTML"""
    return FileResponse(Path(__file__).parent / "dashboard.html")


@app.get("/dashboard.html")
async def dashboard_file():
    """Serve the dashboard HTML"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="Dashboard not found")


# Favicon endpoint to avoid 404s
@app.get("/favicon.ico")
async def favicon():
    """Serve a tiny in-memory PNG favicon to prevent 404."""
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )
    return Response(content=png_data, media_type="image/png")


@app.get("/dashboard.html")
async def dashboard_v1():
    """Serve the original dashboard v1.0"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="Dashboard not found")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        pool = get_db_pool()
        # Test database connection
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1").fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "websocket_connections": ws_manager.get_connection_count(),
            "version": "2.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "websocket_connections": ws_manager.get_connection_count()
        }


@app.post("/api/refresh")
async def refresh_database():
    """
    Refresh database connections to pick up latest data.
    
    Useful when database is in read-only immutable mode and needs to reload
    changes made by other processes (e.g., MCP Task Orchestrator container).
    """
    try:
        pool = get_db_pool()
        
        # Close all existing connections
        pool.close_all()
        logger.info("Closed all database connections for refresh")
        
        # Connections will be automatically recreated on next request
        # Force a test connection to verify it works
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            projects_count = cursor.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        
        logger.info(f"Database refreshed successfully ({projects_count} projects)")
        
        return {
            "success": True,
            "message": "Database connections refreshed successfully",
            "projects_count": projects_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to refresh database: {e}")
        return {
            "success": False,
            "message": f"Failed to refresh database: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Count projects
        projects_count = cursor.execute("SELECT COUNT(*) FROM projects").fetchone()[0]

        # Count features
        features_count = cursor.execute("SELECT COUNT(*) FROM features").fetchone()[0]

        # Count tasks by status
        tasks_total = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        tasks_completed = cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'COMPLETED'"
        ).fetchone()[0]
        tasks_in_progress = cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'IN_PROGRESS'"
        ).fetchone()[0]
        tasks_pending = cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status IN ('PENDING', 'TODO')"
        ).fetchone()[0]

        # Count dependencies
        dependencies_count = cursor.execute("SELECT COUNT(*) FROM dependencies").fetchone()[0]

        # Count sections
        sections_count = cursor.execute("SELECT COUNT(*) FROM sections").fetchone()[0]

        # Count templates
        templates_count = cursor.execute("SELECT COUNT(*) FROM templates WHERE is_enabled = 1").fetchone()[0]

        return {
            "projects": projects_count,
            "features": features_count,
            "tasks": {
                "total": tasks_total,
                "completed": tasks_completed,
                "in_progress": tasks_in_progress,
                "pending": tasks_pending,
                "completion_rate": round((tasks_completed / tasks_total * 100) if tasks_total > 0 else 0, 1)
            },
            "dependencies": dependencies_count,
            "sections": sections_count,
            "templates": templates_count,
            "last_updated": datetime.now().isoformat()
        }


# ============================================================================
# Phase 1 Enhancement: Specific project routes MUST come before parametrized route
# ============================================================================

@app.get("/api/projects/summary")
async def get_projects_summary():
    """
    Get project summary for project selector modal.
    Returns lightweight project data with counts.
    """
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Get all projects with counts
        # Note: Count tasks both directly attached to project AND through features
        projects_rows = cursor.execute("""
            SELECT 
                p.*,
                COUNT(DISTINCT f.id) as feature_count,
                (
                    SELECT COUNT(DISTINCT t.id)
                    FROM tasks t
                    LEFT JOIN features f2 ON t.feature_id = f2.id
                    WHERE t.project_id = p.id OR f2.project_id = p.id
                ) as task_count
            FROM projects p
            LEFT JOIN features f ON f.project_id = p.id
            GROUP BY p.id
            ORDER BY p.modified_at DESC, p.created_at DESC
        """).fetchall()

        projects = []
        for row in projects_rows:
            project = dict_from_row(row)
            projects.append({
                "id": project["id"],
                "name": project["name"],
                "status": project.get("status"),
                "feature_count": row["feature_count"] or 0,
                "task_count": row["task_count"] or 0,
                "modified_at": project.get("modified_at") or project.get("created_at"),
                "created_at": project.get("created_at")
            })

        return {
            "projects": projects,
            "count": len(projects)
        }


@app.get("/api/projects/most-recent")
async def get_most_recent_project():
    """
    Get the most recently updated project.
    Used for auto-loading on dashboard startup.
    """
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        project_row = cursor.execute("""
            SELECT * FROM projects
            ORDER BY modified_at DESC, created_at DESC
            LIMIT 1
        """).fetchone()

        if not project_row:
            raise HTTPException(status_code=404, detail="No projects found")

        project = dict_from_row(project_row)

        return {
            "id": project["id"],
            "name": project["name"],
            "status": project.get("status"),
            "modified_at": project.get("modified_at"),
            "created_at": project.get("created_at")
        }


@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    """Get all projects with features and tasks"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Get all projects
        projects_rows = cursor.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        ).fetchall()

        projects = []
        for project_row in projects_rows:
            project_dict = dict_from_row(project_row)
            project_id = project_dict["id"]

            # Get features for this project
            features_rows = cursor.execute(
                "SELECT * FROM features WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            ).fetchall()

            features = []
            for feature_row in features_rows:
                feature_dict = dict_from_row(feature_row)
                feature_id = feature_dict["id"]

                # Get tasks for this feature
                tasks_rows = cursor.execute(
                    "SELECT * FROM tasks WHERE feature_id = ? ORDER BY created_at DESC",
                    (feature_id,)
                ).fetchall()

                tasks = []
                for task_row in tasks_rows:
                    task_dict = _task_from_row(task_row)
                    tasks.append(TaskStatus(**task_dict))

                feature_dict["tasks"] = tasks
                features.append(Feature(**feature_dict))

            project_dict["features"] = features
            projects.append(Project(**project_dict))

        return projects


@app.get("/api/features", response_model=List[Feature])
async def get_features(project_id: Optional[str] = Query(None)):
    """Get all features, optionally filtered by project"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Get features
        if project_id:
            p_bytes, p_str = _uuid_params(project_id)
            p_nodash = p_str.replace('-', '') if p_str else None
            features_rows = cursor.execute(
                """
                SELECT * FROM features
                WHERE (
                    project_id = ?
                    OR LOWER(CAST(project_id AS TEXT)) = LOWER(?)
                    OR LOWER(REPLACE(CAST(project_id AS TEXT), '-', '')) = LOWER(?)
                )
                ORDER BY created_at DESC
                """,
                (p_bytes, p_str, p_nodash)
            ).fetchall()
        else:
            features_rows = cursor.execute(
                "SELECT * FROM features ORDER BY created_at DESC"
            ).fetchall()

        features = []
        for feature_row in features_rows:
            feature_dict = dict_from_row(feature_row)
            feature_id = feature_dict["id"]

            # Get tasks for this feature
            tasks_rows = cursor.execute(
                "SELECT * FROM tasks WHERE feature_id = ? ORDER BY created_at DESC",
                (feature_id,)
            ).fetchall()

            tasks = []
            for task_row in tasks_rows:
                task_dict = _task_from_row(task_row)
                tasks.append(TaskStatus(**task_dict))

            feature_dict["tasks"] = tasks
            features.append(Feature(**feature_dict))

        return features


@app.get("/api/tasks", response_model=List[TaskStatus])
async def get_tasks(
    feature_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: Optional[int] = Query(1000)  # Increased from 100 to handle larger projects
):
    """Get all tasks with computed project_id, with optional filtering"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Build query with LEFT JOIN to get project_id from features
        # Use COALESCE to get project_id from task directly or from feature
        query = """
            SELECT 
                t.*,
                COALESCE(t.project_id, f.project_id) as computed_project_id
            FROM tasks t
            LEFT JOIN features f ON t.feature_id = f.id
            WHERE 1=1
        """
        params = []

        if feature_id:
            f_bytes, f_str = _uuid_params(feature_id)
            f_nodash = f_str.replace('-', '') if f_str else None
            query += " AND (t.feature_id = ? OR LOWER(CAST(t.feature_id AS TEXT)) = LOWER(?) OR LOWER(REPLACE(CAST(t.feature_id AS TEXT), '-', '')) = LOWER(?))"
            params.extend([f_bytes, f_str, f_nodash])

        if status:
            query += " AND t.status = ?"
            params.append(status)

        if priority:
            query += " AND t.priority = ?"
            params.append(priority)

        query += " ORDER BY t.created_at DESC LIMIT ?"
        params.append(limit)

        # Execute query
        tasks_rows = cursor.execute(query, tuple(params)).fetchall()

        tasks = []
        for task_row in tasks_rows:
            task_dict = _task_from_row(task_row)
            
            # Use computed_project_id as the effective project_id
            if 'computed_project_id' in task_dict:
                task_dict['project_id'] = task_dict['computed_project_id']
            
            tasks.append(TaskStatus(**task_dict))

        return tasks


@app.get("/api/tasks/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """Get a single task by ID"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Convert hex string ID with dashes to bytes (stored as BLOB)
        uuid_bytes, uuid_str = _uuid_params(task_id)
        uuid_nodash = uuid_str.replace('-', '') if uuid_str else None

        # Try multiple match strategies: BLOB(16), TEXT(dashed), TEXT(nodash)
        task_row = cursor.execute(
            """
            SELECT * FROM tasks
            WHERE id = ?
               OR LOWER(CAST(id AS TEXT)) = LOWER(?)
               OR LOWER(REPLACE(CAST(id AS TEXT), '-', '')) = LOWER(?)
               OR UPPER(HEX(id)) = UPPER(?)
            """,
            (uuid_bytes, uuid_str, uuid_nodash, uuid_nodash)
        ).fetchone()

        if not task_row:
            raise HTTPException(status_code=404, detail="Task not found")

        task_dict = _task_from_row(task_row)
        return TaskStatus(**task_dict)


@app.get("/api/features/{feature_id}", response_model=Feature)
async def get_feature(feature_id: str):
    """Get a single feature by ID"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        f_bytes, f_str = _uuid_params(feature_id)
        f_nodash = f_str.replace('-', '') if f_str else None
        feature_row = cursor.execute(
            """
            SELECT * FROM features
            WHERE id = ?
               OR LOWER(CAST(id AS TEXT)) = LOWER(?)
               OR LOWER(REPLACE(CAST(id AS TEXT), '-', '')) = LOWER(?)
            """,
            (f_bytes, f_str, f_nodash)
        ).fetchone()

        if not feature_row:
            raise HTTPException(status_code=404, detail="Feature not found")

        feature_dict = dict_from_row(feature_row)

        # Get tasks for this feature
        tasks_rows = cursor.execute(
            """
            SELECT * FROM tasks
            WHERE (
                feature_id = ?
                OR LOWER(CAST(feature_id AS TEXT)) = LOWER(?)
                OR LOWER(REPLACE(CAST(feature_id AS TEXT), '-', '')) = LOWER(?)
            )
            ORDER BY created_at DESC
            """,
            (f_bytes, f_str, f_nodash)
        ).fetchall()

        tasks = []
        for task_row in tasks_rows:
            task_dict = _task_from_row(task_row)
            tasks.append(TaskStatus(**task_dict))

        feature_dict["tasks"] = tasks

        return Feature(**feature_dict)


@app.get("/api/projects/{project_id}/overview")
async def get_project_overview(project_id: str):
    """
    Get detailed overview of a specific project.
    Returns project with features, tasks, dependencies, and sections.
    """
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Get project
        p_bytes, p_str = _uuid_params(project_id)
        p_nodash = p_str.replace('-', '') if p_str else None

        project_row = cursor.execute("""
            SELECT * FROM projects
            WHERE id = ?
               OR LOWER(CAST(id AS TEXT)) = LOWER(?)
               OR LOWER(REPLACE(CAST(id AS TEXT), '-', '')) = LOWER(?)
        """, (p_bytes, p_str, p_nodash)).fetchone()

        if not project_row:
            raise HTTPException(status_code=404, detail="Project not found")

        project = dict_from_row(project_row)
        
        # Convert project ID back to bytes for subsequent queries
        # project["id"] is now a string UUID, but we need bytes for comparisons
        project_id_bytes = p_bytes

        # Get features with task counts
        features_rows = cursor.execute("""
            SELECT 
                f.*,
                COUNT(DISTINCT t.id) as task_count,
                SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN t.status = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_count
            FROM features f
            LEFT JOIN tasks t ON t.feature_id = f.id
            WHERE f.project_id = ?
            GROUP BY f.id
            ORDER BY f.modified_at DESC, f.created_at DESC
        """, (project_id_bytes,)).fetchall()

        features = []
        for frow in features_rows:
            feature = dict_from_row(frow)
            features.append({
                "id": feature["id"],
                "name": feature["name"],
                "status": feature.get("status"),
                "task_count": frow["task_count"] or 0,
                "completed_count": frow["completed_count"] or 0,
                "in_progress_count": frow["in_progress_count"] or 0
            })

        # Get recent tasks (all tasks in project)
        tasks_rows = cursor.execute("""
            SELECT t.*, f.name as feature_name
            FROM tasks t
            LEFT JOIN features f ON t.feature_id = f.id
            WHERE t.project_id = ?
               OR t.feature_id IN (
                   SELECT id FROM features WHERE project_id = ?
               )
            ORDER BY t.modified_at DESC, t.created_at DESC
            LIMIT 50
        """, (project_id_bytes, project_id_bytes)).fetchall()

        tasks = []
        for trow in tasks_rows:
            task = _task_from_row(trow)
            tasks.append({
                "id": task["id"],
                "title": task["title"],
                "status": task["status"],
                "priority": task.get("priority"),
                "complexity": task.get("complexity"),
                "feature_name": dict_from_row(trow).get("feature_name"),
                "modified_at": task.get("modified_at") or task.get("updated_at")
            })

        # Get dependency count
        dep_count = cursor.execute("""
            SELECT COUNT(*) FROM dependencies d
            WHERE d.from_task_id IN (
                SELECT t.id FROM tasks t
                LEFT JOIN features f ON t.feature_id = f.id
                WHERE t.project_id = ? OR f.project_id = ?
            )
        """, (project_id_bytes, project_id_bytes)).fetchone()[0]

        # Get section count
        section_count = cursor.execute("""
            SELECT COUNT(*) FROM sections
            WHERE (entity_type = 'PROJECT' AND entity_id = ?)
               OR (entity_type = 'FEATURE' AND entity_id IN (
                   SELECT id FROM features WHERE project_id = ?
               ))
               OR (entity_type = 'TASK' AND entity_id IN (
                   SELECT t.id FROM tasks t
                   LEFT JOIN features f ON t.feature_id = f.id
                   WHERE t.project_id = ? OR f.project_id = ?
               ))
        """, (project_id_bytes, project_id_bytes, project_id_bytes, project_id_bytes)).fetchone()[0]

        return {
            "project": {
                "id": project["id"],
                "name": project["name"],
                "summary": project.get("summary"),
                "status": project.get("status"),
                "created_at": project.get("created_at"),
                "modified_at": project.get("modified_at")
            },
            "features": features,
            "tasks": tasks,
            "stats": {
                "feature_count": len(features),
                "task_count": len(tasks),
                "dependency_count": dep_count,
                "section_count": section_count
            }
        }


@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a single project by ID"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        p_bytes, p_str = _uuid_params(project_id)
        p_nodash = p_str.replace('-', '') if p_str else None
        project_row = cursor.execute(
            """
            SELECT * FROM projects
            WHERE id = ?
               OR LOWER(CAST(id AS TEXT)) = LOWER(?)
               OR LOWER(REPLACE(CAST(id AS TEXT), '-', '')) = LOWER(?)
            """,
            (p_bytes, p_str, p_nodash)
        ).fetchone()

        if not project_row:
            raise HTTPException(status_code=404, detail="Project not found")

        project_dict = dict_from_row(project_row)

        # Get features for this project
        features_rows = cursor.execute(
            """
            SELECT * FROM features
            WHERE (
                project_id = ?
                OR LOWER(CAST(project_id AS TEXT)) = LOWER(?)
                OR LOWER(REPLACE(CAST(project_id AS TEXT), '-', '')) = LOWER(?)
            )
            ORDER BY created_at DESC
            """,
            (p_bytes, p_str, p_nodash)
        ).fetchall()

        features = []
        for feature_row in features_rows:
            feature_dict = dict_from_row(feature_row)
            feature_id = feature_dict["id"]

            # Get tasks for this feature
            tasks_rows = cursor.execute(
                "SELECT * FROM tasks WHERE feature_id = ? ORDER BY created_at DESC",
                (feature_id,)
            ).fetchall()

            tasks = []
            for task_row in tasks_rows:
                task_dict = _task_from_row(task_row)
                tasks.append(TaskStatus(**task_dict))

            feature_dict["tasks"] = tasks
            features.append(Feature(**feature_dict))

        project_dict["features"] = features

        return Project(**project_dict)


# NEW Phase 1 Endpoints

@app.get("/api/dependencies", response_model=List[DependencyResponse])
async def get_dependencies():
    """Get all dependencies with task information"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        query = """
            SELECT
                d.*,
                t1.title as from_task_title,
                t2.title as to_task_title
            FROM dependencies d
            LEFT JOIN tasks t1 ON d.from_task_id = t1.id
            LEFT JOIN tasks t2 ON d.to_task_id = t2.id
            ORDER BY d.created_at DESC
        """

        rows = cursor.execute(query).fetchall()
        return [dict_from_row(row) for row in rows]


@app.get("/api/tasks/{task_id}/dependencies", response_model=List[DependencyResponse])
async def get_task_dependencies(task_id: str):
    """Get dependencies for a specific task"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        query = """
            SELECT
                d.*,
                t1.title as from_task_title,
                t2.title as to_task_title
            FROM dependencies d
            LEFT JOIN tasks t1 ON d.from_task_id = t1.id
            LEFT JOIN tasks t2 ON d.to_task_id = t2.id
            WHERE d.from_task_id = ? OR d.to_task_id = ?
            ORDER BY d.created_at DESC
        """

        # Support UUID stored as BLOB(16) or TEXT
        tid_bytes, tid_str = _uuid_params(task_id)
        rows = cursor.execute(query, (tid_bytes, tid_bytes)).fetchall()
        if not rows:
            query_text = """
                SELECT
                    d.*,
                    t1.title as from_task_title,
                    t2.title as to_task_title
                FROM dependencies d
                LEFT JOIN tasks t1 ON d.from_task_id = t1.id
                LEFT JOIN tasks t2 ON d.to_task_id = t2.id
                WHERE CAST(d.from_task_id AS TEXT) = ? OR CAST(d.to_task_id AS TEXT) = ?
                ORDER BY d.created_at DESC
            """
            rows = cursor.execute(query_text, (tid_str, tid_str)).fetchall()
        return [dict_from_row(row) for row in rows]


@app.get("/api/dependency-graph")
async def get_dependency_graph(
    project_id: Optional[str] = Query(None),
    feature_id: Optional[str] = Query(None)
):
    """Get dependency graph data optimized for visualization"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Build query with optional filters
        task_query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if project_id:
            p_bytes, p_str = _uuid_params(project_id)
            p_nodash = p_str.replace('-', '') if p_str else None
            task_query += " AND (project_id = ? OR CAST(project_id AS TEXT) = ? OR CAST(project_id AS TEXT) = ?)"
            params.extend([p_bytes, p_str, p_nodash])

        if feature_id:
            f_bytes, f_str = _uuid_params(feature_id)
            f_nodash = f_str.replace('-', '') if f_str else None
            task_query += " AND (feature_id = ? OR CAST(feature_id AS TEXT) = ? OR CAST(feature_id AS TEXT) = ?)"
            params.extend([f_bytes, f_str, f_nodash])

        # Get tasks
        tasks = cursor.execute(task_query, params).fetchall()
        task_dicts = [dict_from_row(row) for row in tasks]

        # Build nodes
        nodes = []
        for task in task_dicts:
            nodes.append({
                "id": task["id"],
                "label": task["title"],
                "status": task.get("status", "pending"),
                "priority": task.get("priority", "medium"),
                "complexity": task.get("complexity", 5)
            })

        # Get dependencies (filtered by tasks in result set)
        if tasks:
            task_ids = [t["id"] for t in task_dicts]
            placeholders = ','.join('?' * len(task_ids))

            dep_query = f"""
                SELECT * FROM dependencies
                WHERE from_task_id IN ({placeholders})
                   OR to_task_id IN ({placeholders})
            """

            # Double the task IDs for both IN clauses
            dep_params = task_ids + task_ids
            deps = cursor.execute(dep_query, dep_params).fetchall()
            dep_dicts = [dict_from_row(row) for row in deps]
        else:
            dep_dicts = []

        # Build edges
        edges = []
        for dep in dep_dicts:
            edges.append({
                "source": dep["from_task_id"],
                "target": dep["to_task_id"],
                "type": dep.get("type", "BLOCKS")
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "circular_dependencies": []  # TODO: Implement cycle detection
        }


@app.get("/api/sections", response_model=List[SectionResponse])
async def get_sections(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None)
):
    """Get sections, optionally filtered by entity"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        if entity_type and entity_id:
            # Convert hex ID to bytes
            try:
                entity_id_bytes = bytes.fromhex(entity_id.replace('-', ''))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid entity ID format")

            rows = cursor.execute(
                "SELECT * FROM sections WHERE entity_type = ? AND entity_id = ? ORDER BY ordinal",
                (entity_type.upper(), entity_id_bytes)
            ).fetchall()
        else:
            rows = cursor.execute(
                "SELECT * FROM sections ORDER BY created_at DESC LIMIT 100"
            ).fetchall()

        return [dict_from_row(row) for row in rows]


@app.get("/api/tags", response_model=List[TagResponse])
async def get_tags():
    """Get all tags with usage counts"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        query = """
            SELECT
                tag,
                COUNT(*) as count,
                GROUP_CONCAT(DISTINCT entity_type) as entity_types
            FROM entity_tags
            GROUP BY tag
            ORDER BY count DESC
        """

        rows = cursor.execute(query).fetchall()
        results = []

        for row in rows:
            row_dict = dict_from_row(row)
            row_dict["entity_types"] = row_dict["entity_types"].split(",") if row_dict.get("entity_types") else []
            results.append(row_dict)

        return results


@app.get("/api/templates")
async def get_templates():
    """Get all available templates"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        rows = cursor.execute(
            "SELECT * FROM templates WHERE is_enabled = 1 ORDER BY name"
        ).fetchall()

        return [dict_from_row(row) for row in rows]


@app.get("/api/work-sessions")
async def get_work_sessions():
    """Get active work sessions"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        rows = cursor.execute(
            "SELECT * FROM work_sessions ORDER BY last_activity DESC"
        ).fetchall()

        return [dict_from_row(row) for row in rows]


@app.get("/api/task-locks")
async def get_task_locks():
    """Get current task locks"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        rows = cursor.execute(
            """
            SELECT
                l.*,
                w.client_id,
                w.user_context
            FROM task_locks l
            LEFT JOIN work_sessions w ON l.session_id = w.session_id
            WHERE l.expires_at > datetime('now')
            ORDER BY l.locked_at DESC
            """
        ).fetchall()

        return [dict_from_row(row) for row in rows]


@app.get("/api/analytics/overview")
async def get_analytics_overview(
    project_id: Optional[str] = Query(None, description="Filter by project ID")
):
    """Get comprehensive analytics data, optionally filtered by project"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Build WHERE clause for project filtering
        where_clause = "WHERE project_id = ?" if project_id else ""
        params = (project_id,) if project_id else ()

        # Tasks by status
        status_stats = cursor.execute(f"""
            SELECT status, COUNT(*) as count
            FROM tasks
            {where_clause}
            GROUP BY status
        """, params).fetchall()

        # Tasks by priority
        priority_stats = cursor.execute(f"""
            SELECT priority, COUNT(*) as count
            FROM tasks
            {where_clause}
            GROUP BY priority
        """, params).fetchall()

        # Average complexity
        avg_complexity = cursor.execute(f"""
            SELECT AVG(complexity) as avg_complexity
            FROM tasks
            {where_clause}
        """, params).fetchone()[0] or 0

        # Blocked tasks count - only count tasks in the filtered project
        if project_id:
            blocked_count = cursor.execute("""
                SELECT COUNT(DISTINCT d.to_task_id)
                FROM dependencies d
                JOIN tasks t ON d.to_task_id = t.id
                WHERE d.type = 'BLOCKS' AND t.project_id = ?
            """, (project_id,)).fetchone()[0]
        else:
            blocked_count = cursor.execute("""
                SELECT COUNT(DISTINCT to_task_id)
                FROM dependencies
                WHERE type = 'BLOCKS'
            """).fetchone()[0]

        # Build response with proper key names matching frontend expectations
        return {
            "task_status_distribution": {row[0]: row[1] for row in status_stats},
            "task_priority_distribution": {row[0]: row[1] for row in priority_stats},
            "average_complexity": round(avg_complexity, 2),
            "blocked_tasks": blocked_count,
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id
        }


@app.get("/api/search")
async def search_all(
    q: str = Query(..., min_length=1),
    entity_type: Optional[str] = Query(None)
):
    """Global search across projects, features, tasks"""
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        results = []
        search_term = f"%{q}%"

        # Search projects
        if not entity_type or entity_type == "projects":
            projects = cursor.execute(
                "SELECT * FROM projects WHERE name LIKE ? OR summary LIKE ? LIMIT 20",
                (search_term, search_term)
            ).fetchall()
            for p in projects:
                result = dict_from_row(p)
                result["type"] = "project"
                results.append(result)

        # Search features
        if not entity_type or entity_type == "features":
            features = cursor.execute(
                "SELECT * FROM features WHERE name LIKE ? OR summary LIKE ? LIMIT 20",
                (search_term, search_term)
            ).fetchall()
            for f in features:
                result = dict_from_row(f)
                result["type"] = "feature"
                results.append(result)

        # Search tasks
        if not entity_type or entity_type == "tasks":
            tasks = cursor.execute(
                "SELECT * FROM tasks WHERE title LIKE ? OR summary LIKE ? LIMIT 20",
                (search_term, search_term)
            ).fetchall()
            for t in tasks:
                result = dict_from_row(t)
                result["type"] = "task"
                results.append(result)

        return {
            "query": q,
            "results": results,
            "count": len(results)
        }


@app.get("/api/recent-activity")
async def get_recent_activity(
    project_id: Optional[str] = Query(None),
    limit: int = Query(20, le=100)
):
    """
    Get recent activity across all entities or filtered by project.
    Returns datetime, project, entity type, entity name, and action.
    """
    pool = get_db_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        activities = []

        # Helper to add activities
        def add_activity(entity_type: str, rows, action: str = "updated"):
            for row in rows:
                entity = dict_from_row(row)
                activities.append({
                    "datetime": entity.get("modified_at") or entity.get("updated_at") or entity.get("created_at"),
                    "project": entity.get("project_name", "Unknown"),
                    "entity_type": entity_type,
                    "entity_name": entity.get("name") or entity.get("title", "Unnamed"),
                    "entity_id": entity.get("id"),
                    "action": action
                })

        # Get recent projects
        if not project_id:
            project_rows = cursor.execute("""
                SELECT *, name as project_name FROM projects
                ORDER BY modified_at DESC, created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            add_activity("project", project_rows)

        # Get recent features
        if project_id:
            p_bytes, p_str = _uuid_params(project_id)
            p_nodash = p_str.replace('-', '') if p_str else None
            feature_rows = cursor.execute("""
                SELECT f.*, p.name as project_name
                FROM features f
                LEFT JOIN projects p ON f.project_id = p.id
                WHERE f.project_id = ?
                   OR LOWER(CAST(f.project_id AS TEXT)) = LOWER(?)
                   OR LOWER(REPLACE(CAST(f.project_id AS TEXT), '-', '')) = LOWER(?)
                ORDER BY f.modified_at DESC, f.created_at DESC
                LIMIT ?
            """, (p_bytes, p_str, p_nodash, limit)).fetchall()
        else:
            feature_rows = cursor.execute("""
                SELECT f.*, p.name as project_name
                FROM features f
                LEFT JOIN projects p ON f.project_id = p.id
                ORDER BY f.modified_at DESC, f.created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
        add_activity("feature", feature_rows)

        # Get recent tasks
        if project_id:
            p_bytes, p_str = _uuid_params(project_id)
            p_nodash = p_str.replace('-', '') if p_str else None
            task_rows = cursor.execute("""
                SELECT t.*, 
                       COALESCE(p.name, p2.name, 'Unknown') as project_name,
                       t.title as name
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                LEFT JOIN features f ON t.feature_id = f.id
                LEFT JOIN projects p2 ON f.project_id = p2.id
                WHERE t.project_id = ?
                   OR LOWER(CAST(t.project_id AS TEXT)) = LOWER(?)
                   OR LOWER(REPLACE(CAST(t.project_id AS TEXT), '-', '')) = LOWER(?)
                   OR f.project_id = ?
                   OR LOWER(CAST(f.project_id AS TEXT)) = LOWER(?)
                   OR LOWER(REPLACE(CAST(f.project_id AS TEXT), '-', '')) = LOWER(?)
                ORDER BY t.modified_at DESC, t.created_at DESC
                LIMIT ?
            """, (p_bytes, p_str, p_nodash, p_bytes, p_str, p_nodash, limit)).fetchall()
        else:
            task_rows = cursor.execute("""
                SELECT t.*,
                       COALESCE(p.name, p2.name, 'Unknown') as project_name,
                       t.title as name
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                LEFT JOIN features f ON t.feature_id = f.id
                LEFT JOIN projects p2 ON f.project_id = p2.id
                ORDER BY t.modified_at DESC, t.created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
        add_activity("task", task_rows)

        # Sort all activities by datetime
        activities.sort(key=lambda x: x["datetime"] or "", reverse=True)

        # Return top N
        return {
            "activities": activities[:limit],
            "count": len(activities[:limit])
        }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 Task Orchestrator Dashboard Server v2.0")
    print("=" * 60)
    print(f"📁 Database: {Path(DEFAULT_DB_PATH).absolute()}")
    print(f"🌐 Dashboard: http://localhost:8888")
    print(f"📖 API Docs: http://localhost:8888/docs")
    print(f"🔌 WebSocket: {'Enabled' if ENABLE_WEBSOCKET else 'Disabled'}")
    print(f"🐳 Docker Detection: {'Enabled' if ENABLE_DOCKER_DETECTION else 'Disabled'}")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")

