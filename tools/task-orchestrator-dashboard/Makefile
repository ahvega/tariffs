# Task Orchestrator Dashboard - Make helpers

PORT ?= 8888

.PHONY: build up down logs restart ps run

build:
	@echo "Building dashboard image..."
	docker compose build

up:
	@echo "Starting dashboard on port $(PORT)..."
	DASHBOARD_PORT=$(PORT) docker compose up --build -d

down:
	@echo "Stopping dashboard..."
	docker compose down

logs:
	@echo "Tailing logs... (Ctrl+C to exit)"
	docker compose logs -f dashboard

restart: down up

ps:
	docker compose ps

run:
	@echo "Running without compose (volume must exist: mcp-task-data)"
	docker run --rm -p $(PORT):8888 \
	  -e TASK_ORCHESTRATOR_DB=/data/tasks.db \
	  -e ENABLE_WEBSOCKET=true \
	  -e ENABLE_DOCKER_DETECTION=false \
	  -v mcp-task-data:/data:ro \
	  task-orchestrator-dashboard:latest

