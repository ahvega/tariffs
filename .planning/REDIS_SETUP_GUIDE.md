# Redis Setup Guide for SicargaBox

## **Complete step-by-step guide to set up Redis using Docker**

---

## What You'll Get

After following this guide:

- ✅ Redis running in Docker container
- ✅ Accessible at `localhost:6379`
- ✅ Data persisted across restarts
- ✅ Web UI to manage Redis (optional)
- ✅ Ready for Celery integration

---

## Prerequisites

### 1. Install Docker Desktop

**Windows:**

1. Download: [Docker Desktop]<https://www.docker.com/products/docker-desktop/>
2. Run installer
3. Restart computer
4. Verify installation:

   ```bash
   docker --version
   docker-compose --version
   ```

**Already have Docker?** Skip to Step 2.

---

## Step-by-Step Setup

### Step 1: Navigate to Redis Directory

```bash
cd E:/MyDevTools/tariffs/docker/redis
```

**Verify files exist:**

```bash
dir
# Should see:
# - Dockerfile
# - docker-compose.yml
# - redis.conf
# - README.md
# - .env.example
```

---

### Step 2: Create Environment File

```bash
# Copy example environment file
copy .env.example .env
```

**Default values work for development** - no need to edit unless you want custom settings.

---

### Step 3: Start Redis Container

```bash
# Start Redis in detached mode (runs in background)
docker-compose up -d
```

**Expected output:**

```bash
Creating network "redis_sicargabox-network" ... done
Creating volume "redis_redis-data" ... done
Creating sicargabox-redis ... done
Creating sicargabox-redis-ui ... done
```

**Note:** First time will take 1-2 minutes to download Redis image.

---

### Step 4: Verify Redis is Running

```bash
# Check container status
docker-compose ps
```

**Expected output:**

```bash
Name                   State    Ports
sicargabox-redis       Up       0.0.0.0:6379->6379/tcp
sicargabox-redis-ui    Up       0.0.0.0:8081->8081/tcp
```

---

### Step 5: Test Redis Connection

```bash
# Test Redis ping (should return PONG)
docker exec -it sicargabox-redis redis-cli ping
```

**Expected output:** `PONG`

```bash
# Test set/get operation
docker exec -it sicargabox-redis redis-cli SET test "Hello Redis"
docker exec -it sicargabox-redis redis-cli GET test
```

**Expected output:** `"Hello Redis"`

---

### Step 6: Access Redis Commander (Web UI)

Open browser: <http://localhost:8081>

**What you'll see:**

- Redis server connection (local)
- Database selection (db0, db1, etc.)
- Key browser
- Command console

**Try it:**

1. Click on "db0"
2. You should see the "test" key from Step 5
3. Click "test" to view its value

---

### Step 7: View Logs (Optional)

```bash
# View Redis logs in real-time
docker-compose logs -f redis
```

## **Press Ctrl+C to exit logs view**

---

## Django Integration

### Step 1: Install Python Dependencies

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

# Activate virtual environment
venv\Scripts\activate

# Install packages
pip install redis celery django-celery-results django-celery-beat

# Update requirements
pip freeze > requirements.txt
```

---

### Step 2: Update Django Settings

**File:** `backend/sicargabox/SicargaBox/settings.py`

**Add to end of file:**

```python
# ============================================================
# REDIS & CELERY CONFIGURATION
# ============================================================

import os

# Redis Configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_DB = os.environ.get('REDIS_DB', '0')
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Tegucigalpa'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max
CELERY_TASK_SOFT_TIME_LIMIT = 28 * 60  # Soft limit at 28 minutes

# Task routing
CELERY_TASK_ROUTES = {
    'admintools.tasks.rebuild_elasticsearch_index': {'queue': 'elasticsearch'},
    'admintools.tasks.generate_ai_keywords': {'queue': 'ai_generation'},
    'admintools.tasks.enrich_search_keywords': {'queue': 'learning'},
}

# Celery Beat (Scheduled Tasks)
CELERY_BEAT_SCHEDULE = {}  # Will be populated later
```

**Update INSTALLED_APPS:**

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_celery_results',
    'django_celery_beat',
]
```

---

### Step 3: Create Celery Configuration

**File:** `backend/sicargabox/SicargaBox/celery.py` (create new file)

```python
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SicargaBox.settings')

# Create Celery app
app = Celery('SicargaBox')

# Load config from Django settings (namespace='CELERY' means all celery settings must have CELERY_ prefix)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
```

---

### Step 4: Update `__init__.py`

**File:** `backend/sicargabox/SicargaBox/__init__.py`

**Add:**

```python
# Import Celery app to ensure it's loaded when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

### Step 5: Run Migrations

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

python manage.py migrate django_celery_results
python manage.py migrate django_celery_beat
```

**Expected output:**

```bash
Running migrations:
  Applying django_celery_results.0001_initial... OK
  Applying django_celery_results.0002_add_task_name_args_kwargs... OK
  ...
```

---

### Step 6: Test Celery Connection

**Open Django shell:**

```bash
python manage.py shell
```

**Test code:**

```python
# Test Redis connection
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # Should print: True

# Test Celery
from SicargaBox.celery import app
print(app.conf.broker_url)  # Should print: redis://localhost:6379/0

# Send test task
from SicargaBox.celery import debug_task
result = debug_task.delay()
print(f"Task ID: {result.id}")
print(f"Task State: {result.state}")

# Exit shell
exit()
```

---

### Step 7: Start Celery Worker

**Open NEW terminal window:**

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
venv\Scripts\activate

# Start Celery worker
celery -A SicargaBox worker -l info -P solo
```

**Note:** `-P solo` is for Windows. Linux/Mac can omit this flag.

**Expected output:**

```bash
 -------------- celery@HOSTNAME v5.3.x
---- **** -----
--- * ***  * -- Windows-10
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         SicargaBox:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/1
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ----
--- ***** -----

[tasks]
  . SicargaBox.celery.debug_task

[2025-10-20 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-10-20 10:00:00,000: INFO/MainProcess] celery@HOSTNAME ready.
```

**Keep this terminal open** - Celery worker needs to run continuously.

---

### Step 8: Test Background Task

**In Django shell (new terminal):**

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
venv\Scripts\activate
python manage.py shell
```

```python
from SicargaBox.celery import debug_task

# Send task to queue
result = debug_task.delay()
print(f"Task sent! ID: {result.id}")

# Check status
print(f"Status: {result.status}")

# Get result (waits for completion)
print(f"Result: {result.get(timeout=10)}")
```

**In Celery worker terminal, you should see:**

```bash
[2025-10-20 10:05:00,000: INFO/MainProcess] Task SicargaBox.celery.debug_task[abc-123] received
[2025-10-20 10:05:00,000: INFO/MainProcess] Task SicargaBox.celery.debug_task[abc-123] succeeded
```

**Success!** ✅ Celery is working with Redis.

---

## Common Operations

### Start/Stop Redis

```bash
cd E:/MyDevTools/tariffs/docker/redis

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f redis
```

---

### Start Celery Worker

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
venv\Scripts\activate

# Development (single worker)
celery -A SicargaBox worker -l info -P solo

# With specific queues
celery -A SicargaBox worker -l info -P solo -Q elasticsearch,ai_generation,learning
```

---

### Start Celery Beat (Scheduled Tasks)

**Open another terminal:**

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
venv\Scripts\activate

# Start beat scheduler
celery -A SicargaBox beat -l info
```

**Note:** Beat scheduler manages periodic tasks (like nightly keyword enrichment).

---

### Monitor Tasks

**Web UI:** <http://localhost:8081>

**Redis CLI:**

```bash
# Connect to Redis
docker exec -it sicargabox-redis redis-cli

# List all keys
KEYS *

# List Celery task keys
KEYS celery-task-meta-*

# Get specific task result
GET celery-task-meta-<task-id>

# Monitor commands in real-time
MONITOR

# Exit
exit
```

---

## Troubleshooting

### Redis Container Won't Start

**Check if port 6379 is in use:**

```bash
netstat -ano | findstr :6379
```

**Solution:** Stop the process using port 6379 or change Redis port in `docker-compose.yml`.

---

### Celery Can't Connect to Redis

**Check Redis is running:**

```bash
docker-compose ps
```

**Test connection:**

```bash
docker exec -it sicargabox-redis redis-cli ping
```

**Check firewall:** Ensure port 6379 is not blocked.

---

### Task Queue Not Processing

**Ensure Celery worker is running:**

- Check terminal where you ran `celery -A SicargaBox worker`
- Look for "ready" message

**Check Redis:**

```bash
# List pending tasks
docker exec -it sicargabox-redis redis-cli LLEN celery
```

---

### Out of Memory

**Check Redis memory:**

```bash
docker exec -it sicargabox-redis redis-cli INFO memory
```

**Clear database (⚠️ DESTRUCTIVE):**

```bash
docker exec -it sicargabox-redis redis-cli FLUSHDB
```

---

## Production Considerations

### 1. Set Redis Password

**Edit:** `docker/redis/redis.conf`

```conf
# Uncomment and set password
requirepass your_secure_password_here
```

**Update Django settings:**

```python
CELERY_BROKER_URL = 'redis://:your_secure_password_here@localhost:6379/0'
```

---

### 2. Use Supervisor/Systemd

**Don't run Celery manually in production.** Use process manager:

- **Windows:** NSSM (Non-Sucking Service Manager)
- **Linux:** Systemd or Supervisor

---

### 3. Monitor Performance

- Use Redis Commander
- Set up alerts for high memory usage
- Monitor Celery worker health

---

## Next Steps

Now that Redis is running:

1. ✅ **Phase 1, Task 1.1** is complete (Celery & Redis Setup)
2. ➡️ Continue with **Task 1.2**: Create Admin Tools App
3. ➡️ Follow the implementation plan in `SEARCH_KEYWORD_IMPROVEMENT_PLAN.md`

---

## Quick Reference

```bash
# Start Redis
cd E:/MyDevTools/tariffs/docker/redis
docker-compose up -d

# Start Celery Worker
cd E:/MyDevTools/tariffs/backend/sicargabox
venv\Scripts\activate
celery -A SicargaBox worker -l info -P solo

# Start Celery Beat
celery -A SicargaBox beat -l info

# Access Redis UI
http://localhost:8081

# Test Redis
docker exec -it sicargabox-redis redis-cli ping

# View logs
docker-compose logs -f redis

# Stop Redis
docker-compose down
```

---

## Resources

- Redis Documentation: <https://redis.io/docs/>
- Celery Documentation: <https://docs.celeryq.dev/>
- Docker Documentation: <https://docs.docker.com/>
- Django-Celery-Results: <https://pypi.org/project/django-celery-results/>

---

**Questions?** Check the detailed README in `docker/redis/README.md`
