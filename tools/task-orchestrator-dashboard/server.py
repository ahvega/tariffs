#!/usr/bin/env python3
"""
Task Orchestrator Dashboard Server

Lightweight FastAPI server that reads from task-orchestrator SQLite database
and serves data to the dashboard frontend.
"""

import os
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Configuration
DEFAULT_DB_PATH = os.getenv("TASK_ORCHESTRATOR_DB", "data/tasks.db")

app = FastAPI(title="Task Orchestrator Dashboard", version="1.0.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskStatus(BaseModel):
    """Task status model"""
    id: str
    name: str
    status: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    feature_id: Optional[str] = None
    dependencies: Optional[List[str]] = []


class Feature(BaseModel):
    """Feature model"""
    id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    project_id: Optional[str] = None
    tasks: List[TaskStatus] = []


class Project(BaseModel):
    """Project model"""
    id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    features: List[Feature] = []


def get_db_connection():
    """Get database connection"""
    db_path = Path(DEFAULT_DB_PATH)
    if not db_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Database not found at {db_path.absolute()}. "
            f"Set TASK_ORCHESTRATOR_DB environment variable to the correct path."
        )

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row) -> Dict:
    """Convert sqlite3.Row to dict"""
    return {key: row[key] for key in row.keys()}


@app.get("/")
async def root():
    """Serve the dashboard HTML"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return {"message": "Task Orchestrator Dashboard API", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Count projects
        projects_count = cursor.execute("SELECT COUNT(*) FROM projects").fetchone()[0]

        # Count features
        features_count = cursor.execute("SELECT COUNT(*) FROM features").fetchone()[0]

        # Count tasks by status
        tasks_total = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        tasks_completed = cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'completed'"
        ).fetchone()[0]
        tasks_in_progress = cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'"
        ).fetchone()[0]
        tasks_pending = cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'pending' OR status = 'todo'"
        ).fetchone()[0]

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
            "last_updated": datetime.now().isoformat()
        }
    finally:
        conn.close()


@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    """Get all projects with features and tasks"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all projects
        projects_rows = cursor.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        ).fetchall()

        projects = []
        for project_row in projects_rows:
            project_dict = dict_from_row(project_row)
            # Projects use 'name' directly, no 'title' to pop
            # if 'title' in project_dict:
            #     project_dict['name'] = project_dict.pop('title')
            project_id = project_dict["id"]

            # Get features for this project
            features_rows = cursor.execute(
                "SELECT * FROM features WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            ).fetchall()

            features = []
            for feature_row in features_rows:
                feature_dict = dict_from_row(feature_row)
                # Features use 'name' directly, no 'title' to pop
                # if 'title' in feature_dict:
                #     feature_dict['name'] = feature_dict.pop('title')
                feature_id = feature_dict["id"]

                # Get tasks for this feature
                tasks_rows = cursor.execute(
                    "SELECT * FROM tasks WHERE feature_id = ? ORDER BY created_at DESC",
                    (feature_id,)
                ).fetchall()

                tasks = []
                for task_row in tasks_rows:
                    task_dict = dict_from_row(task_row)
                    task_dict['name'] = task_dict.pop('title') # Map title to name for TaskStatus model
                    tasks.append(TaskStatus(**task_dict))

                feature_dict["tasks"] = tasks
                features.append(Feature(**feature_dict))

            project_dict["features"] = features
            projects.append(Project(**project_dict))

        return projects
    finally:
        conn.close()


@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project with its features and tasks"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get project
        project_row = cursor.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()

        if not project_row:
            raise HTTPException(status_code=404, detail="Project not found")

        project_dict = dict_from_row(project_row)
        # Projects use 'name' directly, no 'title' to pop
        # if 'title' in project_dict:
        #     project_dict['name'] = project_dict.pop('title')

        # Get features
        features_rows = cursor.execute(
            "SELECT * FROM features WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,)
        ).fetchall()

        features = []
        for feature_row in features_rows:
            feature_dict = dict_from_row(feature_row)
            # Features use 'name' directly, no 'title' to pop
            # if 'title' in feature_dict:
            #     feature_dict['name'] = feature_dict.pop('title')
            feature_id = feature_dict["id"]

            # Get tasks
            tasks_rows = cursor.execute(
                "SELECT * FROM tasks WHERE feature_id = ? ORDER BY created_at DESC",
                (feature_id,)
            ).fetchall()

            tasks = []
            for task_row in tasks_rows:
                task_dict = dict_from_row(task_row)
                task_dict['name'] = task_dict.pop('title') # Map title to name for TaskStatus model
                tasks.append(TaskStatus(**task_dict))
            feature_dict["tasks"] = tasks
            features.append(Feature(**feature_dict))

        project_dict["features"] = features
        return Project(**project_dict)
    finally:
        conn.close()


@app.get("/api/tasks/recent")
async def get_recent_tasks(limit: int = 20):
    """Get recently updated tasks"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        tasks_rows = cursor.execute(
            "SELECT * FROM tasks ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        ).fetchall()

        return [dict_from_row(row) for row in tasks_rows]
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Task Orchestrator Dashboard Server")
    print(f"📁 Database: {Path(DEFAULT_DB_PATH).absolute()}")
    print(f"🌐 Dashboard: http://localhost:8888")
    print(f"📖 API Docs: http://localhost:8888/docs")

    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
