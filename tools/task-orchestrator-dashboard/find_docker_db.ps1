# Helper script to find task-orchestrator Docker database path (Windows PowerShell)

Write-Host "🔍 Finding task-orchestrator database in Docker..." -ForegroundColor Cyan
Write-Host ""

# Check if docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not running or not installed" -ForegroundColor Red
    exit 1
}

# Find the volume
$VOLUME_NAME = "mcp-task-data"
Write-Host "Looking for Docker volume: $VOLUME_NAME"
Write-Host ""

# Check if volume exists
try {
    docker volume inspect $VOLUME_NAME | Out-Null
} catch {
    Write-Host "❌ Error: Volume '$VOLUME_NAME' not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available volumes:"
    docker volume ls | Select-String "task"
    Write-Host ""
    Write-Host "💡 Tip: Make sure task-orchestrator Docker container is running:" -ForegroundColor Yellow
    Write-Host "   docker compose ps"
    exit 1
}

# Get volume mountpoint
$volumeInfo = docker volume inspect $VOLUME_NAME | ConvertFrom-Json
$mountpoint = $volumeInfo[0].Mountpoint

Write-Host "✅ Found Docker volume!" -ForegroundColor Green
Write-Host ""
Write-Host "Volume name:  $VOLUME_NAME"
Write-Host "Mountpoint:   $mountpoint"
Write-Host ""

# Determine the actual path based on Docker backend
if ($mountpoint -like "/var/lib/docker/*") {
    # WSL2 backend
    Write-Host "🐧 Detected WSL2 Docker backend" -ForegroundColor Cyan
    Write-Host ""

    # Try different WSL paths
    $wslPaths = @(
        "\\wsl.localhost\docker-desktop-data\data\docker\volumes\$VOLUME_NAME\_data\tasks.db",
        "\\wsl$\docker-desktop-data\data\docker\volumes\$VOLUME_NAME\_data\tasks.db"
    )

    $foundPath = $null
    foreach ($path in $wslPaths) {
        if (Test-Path $path) {
            $foundPath = $path
            break
        }
    }

    if ($foundPath) {
        $dbSize = (Get-Item $foundPath).Length / 1KB
        Write-Host "📊 Database file found (size: $([math]::Round($dbSize, 2)) KB)" -ForegroundColor Green
        Write-Host "Database:     $foundPath"
        Write-Host ""
        Write-Host "✏️  Update your .env file with:" -ForegroundColor Yellow
        Write-Host "   TASK_ORCHESTRATOR_DB=$foundPath"
    } else {
        Write-Host "⚠️  Could not access database directly from Windows" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 Option 1: Access via WSL" -ForegroundColor Cyan
        Write-Host "   wsl"
        Write-Host "   ls -lh $mountpoint/tasks.db"
        Write-Host ""
        Write-Host "💡 Option 2: Copy database from container (Recommended)" -ForegroundColor Green
        Write-Host "   mkdir data"
        Write-Host "   docker compose cp mcp-task-orchestrator:/app/data/tasks.db ./data/tasks.db"
        Write-Host "   Then use: TASK_ORCHESTRATOR_DB=data/tasks.db"
    }
} else {
    # Direct path (Windows containers or different setup)
    $dbPath = Join-Path $mountpoint "tasks.db"
    Write-Host "Database:     $dbPath"

    if (Test-Path $dbPath) {
        $dbSize = (Get-Item $dbPath).Length / 1KB
        Write-Host ""
        Write-Host "📊 Database file exists (size: $([math]::Round($dbSize, 2)) KB)" -ForegroundColor Green
        Write-Host ""
        Write-Host "✏️  Update your .env file with:" -ForegroundColor Yellow
        Write-Host "   TASK_ORCHESTRATOR_DB=$dbPath"
    } else {
        Write-Host ""
        Write-Host "⚠️  Database file not found at expected location" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🚀 To start the dashboard:" -ForegroundColor Cyan
Write-Host "   1. Copy .env.example to .env"
Write-Host "   2. Update TASK_ORCHESTRATOR_DB in .env"
Write-Host "   3. Run: python server.py"
Write-Host ""
Write-Host "💡 Alternative: Use the copy method (works on all platforms)" -ForegroundColor Yellow
Write-Host "   mkdir data"
Write-Host "   docker compose cp mcp-task-orchestrator:/app/data/tasks.db ./data/tasks.db"
Write-Host "   # Then .env: TASK_ORCHESTRATOR_DB=data/tasks.db"
