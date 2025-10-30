#!/usr/bin/env python3
"""
Update task-orchestrator tasks for Sprint 1-3 completion
"""
import sqlite3
from datetime import datetime

DB_PATH = "tools/task-orchestrator-dashboard/data/tasks.db"

# Sprint 1 tasks
sprint1_tasks = [
    "Sprint 1: Update auth endpoint to return full name",
    "Sprint 1: Make tracking/invoice optional in frontend",
    "Sprint 1: Make tracking/invoice optional in backend",
    "Sprint 1: Add 'Documentación Pendiente' status to Envío model",
    "Sprint 1: Update shipping request creation logic for optional fields",
    "Sprint 1: Update success message with next steps",
    "Sprint 1: Test complete envío creation flow",
]

# Sprint 2 tasks
sprint2_tasks = [
    "Sprint 2: Create backend update endpoint for envíos",
    "Sprint 2: Add API client update method",
    "Sprint 2: Create frontend update page",
]

# Sprint 3 tasks
sprint3_tasks = [
    "Sprint 3: Create envío list API endpoint",
    "Sprint 3: Create dashboard layout and tab navigation",
    "Sprint 3: Implement 'Mis Envíos' tab with list",
    "Sprint 3: Update header with icon menu",
]

all_tasks = sprint1_tasks + sprint2_tasks + sprint3_tasks

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get current timestamp
    now = datetime.now().isoformat()

    updated_count = 0

    for task_title in all_tasks:
        # Check if task exists
        cursor.execute("SELECT id, status FROM tasks WHERE title = ?", (task_title,))
        result = cursor.fetchone()

        if result:
            task_id, current_status = result
            if current_status != 'completed':
                # Update task to completed
                cursor.execute(
                    "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                    ('completed', now, task_id)
                )
                updated_count += 1
                print(f"✅ Updated: {task_title}")
            else:
                print(f"⏭️  Already completed: {task_title}")
        else:
            print(f"❌ Not found: {task_title}")

    conn.commit()
    print(f"\n✨ Successfully updated {updated_count} tasks to 'completed' status")

except sqlite3.Error as e:
    print(f"❌ Database error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()
