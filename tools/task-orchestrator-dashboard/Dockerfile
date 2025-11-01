FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional: add build tools if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default env for container usage: read DB from mounted volume
ENV TASK_ORCHESTRATOR_DB=/data/tasks.db \
    ENABLE_WEBSOCKET=true \
    ENABLE_DOCKER_DETECTION=false

EXPOSE 8888

CMD ["python", "server.py"]


