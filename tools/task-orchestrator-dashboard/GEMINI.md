# Gemini Project Context: Task Orchestrator Dashboard

## Project Overview

This project is a lightweight, single-page dashboard for monitoring the [MCP Task Orchestrator](https://github.com/jpicklyk/task-orchestrator) in real-time. It provides a visual interface for developers to get a quick overview of their task hierarchy and progress.

The application is built with a Python backend using the FastAPI framework and a simple, dependency-free HTML frontend. It reads data directly from the Task Orchestrator's SQLite database (`tasks.db`).

### Core Functionality

*   **Real-time Statistics:** Displays the number of projects, features, and tasks, along with a task completion rate.
*   **Hierarchical View:** Shows tasks organized under their respective features and projects.
*   **Recent Activity:** Lists recently updated tasks.
*   **Auto-refresh:** The dashboard automatically refreshes every 10 seconds to provide the latest data.
*   **API:** A RESTful API provides access to the underlying data.

### Technology Stack

*   **Backend:** Python, FastAPI
*   **ASGI Server:** Uvicorn
*   **Database:** SQLite (read-only)
*   **Frontend:** HTML (no frameworks)
*   **Dependencies:** Pydantic for data validation, python-dotenv for environment variable management.

## Building and Running the Project

### Prerequisites

*   Python 3.8+
*   An existing `tasks.db` file from a running Task Orchestrator instance.

### Setup and Execution

1.  **Navigate to the dashboard directory:**
    ```bash
    cd tools/task-orchestrator-dashboard
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the database path (if necessary):**
    By default, the application looks for `data/tasks.db`. You can configure the path by creating a `.env` file (copy from `.env.example`) and setting the `TASK_ORCHESTRATOR_DB` variable.

5.  **Run the development server:**
    ```bash
    python server.py
    ```

6.  **Access the dashboard:**
    Open your web browser and navigate to `http://localhost:8888`.

### API Documentation

Interactive API documentation (Swagger UI) is available at `http://localhost:8888/docs` when the server is running.

## Development Conventions

*   **Self-Contained:** The project is designed to be self-contained and project-agnostic. It should not have any imports from parent projects.
*   **Configuration:** Configuration is managed through environment variables (`.env` file), with sensible defaults.
*   **Dependencies:** All Python dependencies are listed in `requirements.txt`.
*   **Frontend:** The frontend is a single `dashboard.html` file with no external framework dependencies.
*   **API:** The FastAPI backend provides a clear RESTful API for the frontend to consume.
