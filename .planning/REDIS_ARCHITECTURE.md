# Redis Architecture in SicargaBox

Visual guide to understand how Redis integrates with the SicargaBox system.

---

## System Architecture

```bash
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Elasticsearch Admin UI (Django Admin)            │   │
│  │                                                          │   │
│  │  [Rebuild Index] [Generate Keywords] [View Tasks]        │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Request
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                     DJANGO APPLICATION                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AdminTools Views (admintools/views.py)                  │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ rebuild_index_action(request):                      │ │   │
│  │  │   task = rebuild_elasticsearch_index.delay()        │ │   │
│  │  │   return JsonResponse({'task_id': task.id})         │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         │ .delay() - Send task to queue         │
│                         ↓                                       │
└─────────────────────────────────────────────────────────────────┘
                          │
                          │ Redis Protocol (TCP/6379)
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    REDIS (Docker Container)                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DATABASE 0 - Celery Broker (Task Queue)                 │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ Queue: celery                                      │  │   │
│  │  │ ┌─────────────────────────────────────────────┐    │  │   │
│  │  │ │ Task: rebuild_elasticsearch_index           │    │  │   │
│  │  │ │ ID: abc-123-def-456                         │    │  │   │
│  │  │ │ Args: []                                    │    │  │   │
│  │  │ │ Status: PENDING                             │    │  │   │
│  │  │ └─────────────────────────────────────────────┘    │  │   │
│  │  │                                                    │  │   │
│  │  │ Queue: elasticsearch                               │  │   │
│  │  │ Queue: ai_generation                               │  │   │
│  │  │ Queue: learning                                    │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DATABASE 1 - Celery Result Backend (Task Results)       │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ celery-task-meta-abc-123-def-456                   │  │   │
│  │  │ {                                                  │  │   │
│  │  │   "status": "SUCCESS",                             │  │   │
│  │  │   "result": {"documents": 4682, "time": "45s"},    │  │   │
│  │  │   "traceback": null,                               │  │   │
│  │  │   "children": [],                                  │  │   │
│  │  │   "date_done": "2025-10-20T10:15:00"               │  │   │
│  │  │ }                                                  │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Port: 6379                                                     │
│  Memory: 256MB (configurable)                                   │
│  Persistence: RDB + AOF                                         │
└─────────────────────────────────────────────────────────────────┘
                          ↑
                          │ Picks up tasks from queue
                          │
┌─────────────────────────────────────────────────────────────────┐
│              CELERY WORKER (Background Process)                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Worker Process                                          │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ 1. Poll Redis for new tasks                         │ │   │
│  │  │ 2. Pick up task: rebuild_elasticsearch_index        │ │   │
│  │  │ 3. Execute task                                     │ │   │
│  │  │    - Call Django management command                 │ │   │
│  │  │    - Update progress in Redis                       │ │   │
│  │  │ 4. Store result in Redis (DB 1)                     │ │   │
│  │  │ 5. Mark task as SUCCESS/FAILURE                     │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Command: celery -A SicargaBox worker -l info -P solo           │
└─────────────────────────────────────────────────────────────────┘
                          │
                          │ Updates
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   ELASTICSEARCH (Docker)                        │
│                                                                 │
│  Index: partidas_arancelarias                                   │
│  Documents: 4,682                                               │
│  Status: green                                                  │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                           │
│                                                                 │
│  Tables:                                                        │
│  - MiCasillero_partidaarancelaria (source data)                 │
│  - django_celery_results_taskresult (task history)              │
│  - admintools_taskhistory (custom task tracking)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow: Rebuild Elasticsearch Index

### 1. User Triggers Action

```bash
User clicks [Rebuild Index] button in Admin UI
    ↓
JavaScript sends POST to /admin/elasticsearch/rebuild/
```

### 2. Django Creates Task

```python
# admintools/views.py
def rebuild_index_action(request):
    # Create Celery task (returns immediately)
    task = rebuild_elasticsearch_index.delay()

    # Store in TaskHistory table
    TaskHistory.objects.create(
        task_id=task.id,
        task_name='rebuild_elasticsearch_index',
        status='PENDING',
        initiated_by=request.user
    )

    # Return task ID to frontend
    return JsonResponse({
        'status': 'started',
        'task_id': task.id
    })
```

### 3. Task Queued in Redis

```bash
Redis DB 0 (Broker):
    Key: celery-task-meta-abc-123
    Value: {
        "task": "admintools.tasks.rebuild_elasticsearch_index",
        "id": "abc-123",
        "args": [],
        "kwargs": {},
        "eta": null
    }
```

### 4. Celery Worker Picks Up Task

```bash
[Worker Terminal Output]
[2025-10-20 10:00:00,000: INFO/MainProcess]
    Task admintools.tasks.rebuild_elasticsearch_index[abc-123] received

[2025-10-20 10:00:05,000: INFO/MainProcess]
    Rebuilding Elasticsearch index...

[2025-10-20 10:00:10,000: INFO/MainProcess]
    Progress: 500/4682 documents indexed

[2025-10-20 10:00:45,000: INFO/MainProcess]
    Task admintools.tasks.rebuild_elasticsearch_index[abc-123] succeeded
    Result: {'documents': 4682, 'time': '45s'}
```

### 5. Result Stored in Redis

```bash
Redis DB 1 (Result Backend):
    Key: celery-task-meta-abc-123
    Value: {
        "status": "SUCCESS",
        "result": {"documents": 4682, "time": "45s"},
        "date_done": "2025-10-20T10:00:45"
    }
```

### 6. Frontend Polls for Status

```javascript
// JavaScript polls every 2 seconds
setInterval(() => {
    fetch(`/admin/elasticsearch/task-status/${taskId}/`)
        .then(res => res.json())
        .then(data => {
            updateProgressBar(data.progress);
            if (data.status === 'SUCCESS') {
                showSuccessMessage();
                clearInterval(pollInterval);
            }
        });
}, 2000);
```

---

## Redis Data Structures Used by Celery

### List (Task Queues)

```bash
Key: celery
Type: LIST
Values: [task_1, task_2, task_3]

# Celery uses LPUSH to add tasks to queue
# Workers use BRPOP to get tasks (blocking operation)
```

### Hash (Task Metadata)

```bash
Key: celery-task-meta-abc-123
Type: HASH
Fields:
    status: SUCCESS
    result: {"documents": 4682}
    traceback: null
    children: []
    date_done: 2025-10-20T10:00:45
```

### Set (Task Results)

```bash
Key: unacked_set
Type: SET
Members: [task_abc, task_def, task_xyz]

# Tasks that have been picked up but not yet acknowledged
```

---

## Redis Memory Layout

```bash
Total Memory: 256 MB (configurable)

┌─────────────────────────────────────────┐
│  DB 0: Celery Broker (50 MB)            │
│  ├─ celery queue                        │
│  ├─ elasticsearch queue                 │
│  ├─ ai_generation queue                 │
│  └─ learning queue                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  DB 1: Celery Results (100 MB)          │
│  ├─ celery-task-meta-*                  │
│  ├─ task results (7 day TTL)            │
│  └─ task progress data                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  DB 2-15: Available (Reserved)           │
│  - Future use (caching, sessions, etc)  │
└─────────────────────────────────────────┘

Memory Policy: allkeys-lru
(Evicts least recently used keys when memory limit reached)
```

---

## Task Lifecycle in Redis

```bash
┌──────────────┐
│   PENDING    │  Task created, waiting in queue
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   STARTED    │  Worker picked up task, began execution
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   PROGRESS   │  Task updating progress (optional)
└──────┬───────┘
       │
       ↓
┌──────────────┐     ┌──────────────┐
│   SUCCESS    │ or  │   FAILURE    │  Task completed
└──────────────┘     └──────────────┘
       │                     │
       ↓                     ↓
┌──────────────────────────────┐
│   RESULT STORED (7 days)     │  Result kept in Redis
└──────────────────────────────┘
       │
       ↓
┌──────────────────────────────┐
│   EXPIRED & DELETED           │  Auto-cleanup after 7 days
└──────────────────────────────┘
```

---

## Redis vs PostgreSQL

**Why use Redis instead of just PostgreSQL?**

| Feature | Redis | PostgreSQL |
|---------|-------|------------|
| **Speed** | <1ms (in-memory) | 10-100ms (disk) |
| **Task Queue** | Native LIST operations | Requires polling |
| **Pub/Sub** | Built-in | Limited |
| **Persistence** | Optional (RDB + AOF) | Always (ACID) |
| **Best For** | Temporary data, caching, queues | Permanent data, complex queries |

**In SicargaBox:**

- **Redis:** Task queues, temporary results, real-time updates
- **PostgreSQL:** Partida data, user accounts, task history (long-term)

---

## Redis Persistence Options

### RDB (Redis Database File)

```bash
Snapshots at intervals:
- Every 15 minutes if 1+ key changed
- Every 5 minutes if 10+ keys changed
- Every 60 seconds if 10,000+ keys changed

File: /data/dump.rdb
Pros: Fast, compact
Cons: Data loss possible (last N minutes)
```

### AOF (Append Only File)

```bash
Logs every write operation:
- fsync every second (default)
- Rebuilds database by replaying operations

File: /data/appendonly.aof
Pros: More durable, minimal data loss
Cons: Larger file size, slower recovery
```

**SicargaBox uses BOTH for maximum durability.**

---

## Redis Commands for Monitoring

### Check Task Queue

```bash
# Connect to Redis
docker exec -it sicargabox-redis redis-cli

# Check queue length
LLEN celery
# Returns: 5 (5 pending tasks)

# View pending tasks (without removing)
LRANGE celery 0 -1

# View specific task metadata
HGETALL celery-task-meta-abc-123
```

### Monitor Memory

```bash
# Memory usage
INFO memory

# Key distribution
INFO keyspace

# Slow queries
SLOWLOG GET 10
```

### Real-Time Monitoring

```bash
# Watch all commands in real-time
MONITOR

# Watch specific pattern
PSUBSCRIBE celery-task-meta-*
```

---

## Scaling Considerations

### Multiple Workers

```bash
                    Redis Queue
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
    Worker 1        Worker 2        Worker 3
    (Tasks 1-3)     (Tasks 4-6)     (Tasks 7-9)
```

**Start multiple workers:**

```bash
# Terminal 1
celery -A SicargaBox worker -l info -P solo -Q elasticsearch

# Terminal 2
celery -A SicargaBox worker -l info -P solo -Q ai_generation

# Terminal 3
celery -A SicargaBox worker -l info -P solo -Q learning
```

### Redis Clustering (Production)

```bash
     Redis Sentinel (Monitor)
            │
    ┌───────┼───────┐
    ↓       ↓       ↓
 Master  Slave1  Slave2

- Auto-failover if master dies
- Read replicas for scaling
- Sentinel monitors health
```

---

## Comparison: Without vs With Redis

### Without Redis (Synchronous)

```bash
User clicks [Rebuild Index]
    ↓
Django executes rebuild (45 seconds)
    ↓
Browser waits... ⏳⏳⏳
    ↓
Response received (timeout after 30s!) ❌
```

**Problems:**

- Browser timeout
- User can't do anything else
- Server thread blocked
- No progress tracking

### With Redis + Celery (Asynchronous)

```bash
User clicks [Rebuild Index]
    ↓
Django creates task (0.01s)
    ↓
Returns immediately ✅
    ↓
User sees progress bar updating
    ↓
Celery worker rebuilds index in background
    ↓
User continues working ✅
    ↓
Progress: 25%... 50%... 75%... 100% ✅
```

**Benefits:**

- Instant response
- Real-time progress
- Non-blocking
- Scalable

---

## Summary

**Redis Role in SicargaBox:**

1. ✅ **Message Broker** - Queues background tasks
2. ✅ **Result Backend** - Stores task progress/results
3. ✅ **Real-time Updates** - Enables live progress tracking
4. ✅ **Scalability** - Multiple workers can process tasks in parallel
5. ✅ **Reliability** - Persists tasks to disk (RDB + AOF)

**Key Takeaway:**
Redis acts as the "communication hub" between your Django admin UI and background workers, enabling asynchronous task processing with real-time feedback.

---

**Next:** Follow `REDIS_SETUP_GUIDE.md` to install and configure Redis for your project.
