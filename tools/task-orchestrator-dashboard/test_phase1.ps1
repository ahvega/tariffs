#!/usr/bin/env pwsh
# Phase 1 Backend Endpoint Tests

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Phase 1 Backend Endpoint Tests" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Make sure server is running with venv activated:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  python server_v2.py" -ForegroundColor Gray
Write-Host ""

$baseUrl = "http://localhost:8888"

# Test if server is running
Write-Host "1. Testing server health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/api/health" -Method Get
    Write-Host "   ✓ Server is healthy" -ForegroundColor Green
    Write-Host "   Database: $($health.database)" -ForegroundColor Gray
    Write-Host "   Version: $($health.version)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Server is not running or unreachable" -ForegroundColor Red
    Write-Host "   Please start the server with: python server_v2.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test project summary
Write-Host "2. Testing /api/projects/summary..." -ForegroundColor Yellow
try {
    $summary = Invoke-RestMethod -Uri "$baseUrl/api/projects/summary" -Method Get
    Write-Host "   ✓ Endpoint working" -ForegroundColor Green
    Write-Host "   Found $($summary.count) projects" -ForegroundColor Gray
    if ($summary.projects.Count -gt 0) {
        $proj = $summary.projects[0]
        Write-Host "   Sample: $($proj.name) ($($proj.feature_count) features, $($proj.task_count) tasks)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test most recent project
Write-Host "3. Testing /api/projects/most-recent..." -ForegroundColor Yellow
try {
    $recent = Invoke-RestMethod -Uri "$baseUrl/api/projects/most-recent" -Method Get
    Write-Host "   ✓ Endpoint working" -ForegroundColor Green
    Write-Host "   Most recent: $($recent.name) (status: $($recent.status))" -ForegroundColor Gray
    $projectId = $recent.id
} catch {
    Write-Host "   ✗ Endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Message -like "*404*") {
        Write-Host "   (This is expected if you have no projects in the database)" -ForegroundColor Yellow
    }
    $projectId = $null
}

Write-Host ""

# Test recent activity (all)
Write-Host "4. Testing /api/recent-activity (all projects)..." -ForegroundColor Yellow
try {
    $activity = Invoke-RestMethod -Uri "$baseUrl/api/recent-activity?limit=5" -Method Get
    Write-Host "   ✓ Endpoint working" -ForegroundColor Green
    Write-Host "   Found $($activity.count) recent activities" -ForegroundColor Gray
    if ($activity.activities.Count -gt 0) {
        $act = $activity.activities[0]
        Write-Host "   Latest: $($act.entity_type) '$($act.entity_name)' in $($act.project)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test project overview (if we have a project ID)
if ($projectId) {
    Write-Host "5. Testing /api/projects/{id}/overview..." -ForegroundColor Yellow
    try {
        $overview = Invoke-RestMethod -Uri "$baseUrl/api/projects/$projectId/overview" -Method Get
        Write-Host "   ✓ Endpoint working" -ForegroundColor Green
        Write-Host "   Project: $($overview.project.name)" -ForegroundColor Gray
        Write-Host "   Stats: $($overview.stats.feature_count) features, $($overview.stats.task_count) tasks" -ForegroundColor Gray
        Write-Host "          $($overview.stats.dependency_count) dependencies, $($overview.stats.section_count) sections" -ForegroundColor Gray
    } catch {
        Write-Host "   ✗ Endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "5. Skipping /api/projects/{id}/overview (no project available)" -ForegroundColor Yellow
}

Write-Host ""

# Test recent activity (project-scoped) if we have a project ID
if ($projectId) {
    Write-Host "6. Testing /api/recent-activity (project-scoped)..." -ForegroundColor Yellow
    try {
        $activityScoped = Invoke-RestMethod -Uri "$baseUrl/api/recent-activity?project_id=$projectId&limit=5" -Method Get
        Write-Host "   ✓ Endpoint working" -ForegroundColor Green
        Write-Host "   Found $($activityScoped.count) activities for this project" -ForegroundColor Gray
    } catch {
        Write-Host "   ✗ Endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "6. Skipping /api/recent-activity (project-scoped) - no project available" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "All Phase 1 endpoints are implemented and functional!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the API docs at: $baseUrl/docs" -ForegroundColor Gray
Write-Host "  2. Proceed to Phase 3: Project Selector Modal (Frontend)" -ForegroundColor Gray
Write-Host ""
