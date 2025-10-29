#!/bin/bash
# Helper script to find task-orchestrator Docker database path

echo "🔍 Finding task-orchestrator database in Docker..."
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running or not installed"
    exit 1
fi

# Find the volume
VOLUME_NAME="mcp-task-data"
echo "Looking for Docker volume: $VOLUME_NAME"
echo ""

# Check if volume exists
if ! docker volume inspect $VOLUME_NAME > /dev/null 2>&1; then
    echo "❌ Error: Volume '$VOLUME_NAME' not found"
    echo ""
    echo "Available volumes:"
    docker volume ls | grep task
    echo ""
    echo "💡 Tip: Make sure task-orchestrator Docker container is running:"
    echo "   docker compose ps"
    exit 1
fi

# Get volume mountpoint
MOUNTPOINT=$(docker volume inspect $VOLUME_NAME --format '{{ .Mountpoint }}')
DB_PATH="$MOUNTPOINT/tasks.db"

echo "✅ Found Docker volume!"
echo ""
echo "Volume name:  $VOLUME_NAME"
echo "Mountpoint:   $MOUNTPOINT"
echo "Database:     $DB_PATH"
echo ""

# Check if database file exists
if [ -f "$DB_PATH" ]; then
    DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo "📊 Database file exists (size: $DB_SIZE)"
    echo ""
    echo "✏️  Update your .env file with:"
    echo "   TASK_ORCHESTRATOR_DB=$DB_PATH"
else
    echo "⚠️  Database file not found at expected location"
    echo ""
    echo "💡 Alternative: Copy database from container:"
    echo "   docker compose cp mcp-task-orchestrator:/app/data/tasks.db ./data/tasks.db"
    echo "   Then use: TASK_ORCHESTRATOR_DB=data/tasks.db"
fi

echo ""
echo "🚀 To start the dashboard:"
echo "   1. Copy .env.example to .env"
echo "   2. Update TASK_ORCHESTRATOR_DB in .env"
echo "   3. Run: python server.py"
