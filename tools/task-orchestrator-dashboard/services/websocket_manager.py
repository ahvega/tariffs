"""
WebSocket Manager Service

Manages WebSocket connections and broadcasts real-time updates to clients.
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Set, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts updates"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.last_db_mtime = None
        self.watcher_task = None
        self.db_path: str = None

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

        # Send initial connection confirmation
        await self.send_to_client(websocket, {
            "type": "connection_established",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Task Orchestrator Dashboard"
        })

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_to_client(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
            await self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        self.active_connections -= disconnected

        if disconnected:
            logger.info(f"Cleaned up {len(disconnected)} disconnected clients")

    async def broadcast_update(self, update_type: str, data: Dict[str, Any] = None):
        """Broadcast a typed update to all clients"""
        message = {
            "type": update_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        await self.broadcast(message)

    def set_db_path(self, db_path: str):
        """Set the database path to watch"""
        self.db_path = db_path
        logger.info(f"Watching database at: {db_path}")

    async def watch_database(self):
        """Watch database for changes and broadcast updates"""
        if not self.db_path:
            logger.warning("No database path set for watching")
            return

        logger.info(f"Starting database watcher for: {self.db_path}")

        while True:
            try:
                # Check if database file exists
                if not os.path.exists(self.db_path):
                    logger.warning(f"Database not found at {self.db_path}")
                    await asyncio.sleep(5)
                    continue

                # Get current modification time
                current_mtime = os.path.getmtime(self.db_path)

                # Check if database changed
                if self.last_db_mtime is not None and current_mtime != self.last_db_mtime:
                    logger.info(f"Database changed detected at {datetime.now()}")

                    # Broadcast update to all clients
                    await self.broadcast_update("database_update", {
                        "modified_at": datetime.fromtimestamp(current_mtime).isoformat(),
                        "message": "Task orchestrator database has been updated"
                    })

                self.last_db_mtime = current_mtime

                # Check every second for changes
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Database watch error: {e}")
                await asyncio.sleep(5)

    async def start_watching(self, db_path: str):
        """Start the database watcher task"""
        self.set_db_path(db_path)

        # Cancel existing watcher if any
        if self.watcher_task and not self.watcher_task.done():
            self.watcher_task.cancel()

        # Start new watcher task
        self.watcher_task = asyncio.create_task(self.watch_database())
        logger.info("Database watcher task started")

    async def stop_watching(self):
        """Stop the database watcher task"""
        if self.watcher_task and not self.watcher_task.done():
            self.watcher_task.cancel()
            try:
                await self.watcher_task
            except asyncio.CancelledError:
                pass
            logger.info("Database watcher task stopped")

    async def broadcast_stats_update(self, stats: Dict[str, Any]):
        """Broadcast statistics update"""
        await self.broadcast_update("stats_update", stats)

    async def broadcast_task_update(self, task_data: Dict[str, Any]):
        """Broadcast task update"""
        await self.broadcast_update("task_update", task_data)

    async def broadcast_feature_update(self, feature_data: Dict[str, Any]):
        """Broadcast feature update"""
        await self.broadcast_update("feature_update", feature_data)

    async def broadcast_project_update(self, project_data: Dict[str, Any]):
        """Broadcast project update"""
        await self.broadcast_update("project_update", project_data)

    async def broadcast_error(self, error_message: str):
        """Broadcast error message"""
        await self.broadcast_update("error", {
            "message": error_message
        })

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)

    async def ping_all(self):
        """Send ping to all clients to keep connections alive"""
        await self.broadcast_update("ping", {
            "message": "keepalive",
            "connections": self.get_connection_count()
        })
