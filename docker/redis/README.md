# Redis Setup for SicargaBox

This directory contains Redis Docker configuration for the SicargaBox project.

## What is Redis?

Redis is an in-memory data structure store used as:
- **Message Broker** for Celery task queue
- **Result Backend** for storing task progress and results
- **Cache** for frequently accessed data (optional)

## Quick Start

### 1. Start Redis Container

```bash
# Navigate to redis directory
cd E:/MyDevTools/tariffs/docker/redis

# Start Redis (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f redis
```

### 2. Verify Redis is Running

```bash
# Check container status
docker-compose ps

# Test Redis connection
docker exec -it sicargabox-redis redis-cli ping
# Should return: PONG

# Check Redis info
docker exec -it sicargabox-redis redis-cli INFO
```

### 3. Stop Redis

```bash
# Stop container
docker-compose down

# Stop and remove data (⚠️ DESTRUCTIVE)
docker-compose down -v
```

## Configuration

### Files

- **Dockerfile** - Builds Redis image with custom config
- **docker-compose.yml** - Orchestrates Redis container
- **redis.conf** - Redis server configuration
- **.env.example** - Environment variables template

### Environment Setup

```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (default values work for development)
```

### Ports

- **6379** - Redis server (accessible at localhost:6379)
- **8081** - Redis Commander web UI (optional)

## Using Redis Commander (Web UI)

Redis Commander is a web-based GUI for managing Redis.

**Access:** http://localhost:8081

**Features:**
- Browse keys and values
- Execute Redis commands
- Monitor memory usage
- View database statistics

To disable Redis Commander:

```yaml
# In docker-compose.yml, comment out redis-commander service
```

## Django Integration

### 1. Install Python Dependencies

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
pip install redis celery django-celery-results django-celery-beat
pip freeze > requirements.txt
```

### 2. Update Django Settings

Add to `backend/sicargabox/SicargaBox/settings.py`:

```python
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
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 28 * 60  # 28 minutes

# Installed Apps
INSTALLED_APPS = [
    # ... existing apps ...
    'django_celery_results',
    'django_celery_beat',
]
```

### 3. Test Connection from Django

```bash
cd backend/sicargabox
python manage.py shell
```

```python
import redis

# Test Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()
# Should return: True

# Set and get a test value
r.set('test_key', 'Hello Redis!')
print(r.get('test_key'))
# Should return: b'Hello Redis!'

# Delete test key
r.delete('test_key')
```

## Monitoring

### View Redis Statistics

```bash
# Connect to Redis CLI
docker exec -it sicargabox-redis redis-cli

# Inside Redis CLI:
INFO                  # Full server info
INFO stats            # Statistics
INFO memory           # Memory usage
INFO clients          # Connected clients
DBSIZE                # Number of keys
MONITOR               # Real-time command monitoring (Ctrl+C to exit)
```

### Monitor Celery Tasks in Redis

```bash
# List all keys
redis-cli KEYS '*'

# List Celery task keys
redis-cli KEYS 'celery-task-meta-*'

# Get task result
redis-cli GET celery-task-meta-<task-id>
```

## Persistence

Redis is configured with two persistence mechanisms:

1. **RDB (Snapshots)**
   - Creates point-in-time snapshots
   - File: `/data/dump.rdb`
   - Saves every 15 min if 1+ keys changed

2. **AOF (Append Only File)**
   - Logs every write operation
   - File: `/data/appendonly.aof`
   - More durable than RDB

**Data Location:** Stored in Docker volume `redis-data`

**Backup:**
```bash
# Create backup
docker exec sicargabox-redis redis-cli BGSAVE

# Copy backup file
docker cp sicargabox-redis:/data/dump.rdb ./backup-$(date +%Y%m%d).rdb
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs redis

# Common issues:
# - Port 6379 already in use
# - Insufficient memory
# - Corrupted data files
```

### Connection Refused

```bash
# Check Redis is running
docker-compose ps

# Check if port is accessible
telnet localhost 6379

# Check firewall settings
# Ensure port 6379 is not blocked
```

### High Memory Usage

```bash
# Check memory
docker exec -it sicargabox-redis redis-cli INFO memory

# Flush database (⚠️ DESTRUCTIVE)
docker exec -it sicargabox-redis redis-cli FLUSHDB

# Flush all databases (⚠️ DESTRUCTIVE)
docker exec -it sicargabox-redis redis-cli FLUSHALL
```

### Performance Issues

```bash
# Check slow queries
docker exec -it sicargabox-redis redis-cli SLOWLOG GET 10

# Monitor latency
docker exec -it sicargabox-redis redis-cli --latency

# Monitor commands in real-time
docker exec -it sicargabox-redis redis-cli MONITOR
```

## Security (Production)

For production deployment:

1. **Set Password:**
   ```bash
   # In redis.conf, uncomment:
   requirepass your_secure_password_here
   ```

2. **Update Connection URLs:**
   ```python
   CELERY_BROKER_URL = 'redis://:password@localhost:6379/0'
   ```

3. **Enable Protected Mode:**
   ```conf
   protected-mode yes
   bind 127.0.0.1
   ```

4. **Use TLS/SSL:**
   - Configure Redis with SSL certificates
   - Use `rediss://` protocol

## Resources

- [Redis Documentation](https://redis.io/docs/)
- [Redis Commands Reference](https://redis.io/commands/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## Common Commands Reference

```bash
# Start Redis
docker-compose up -d

# Stop Redis
docker-compose down

# Restart Redis
docker-compose restart

# View logs
docker-compose logs -f

# Access Redis CLI
docker exec -it sicargabox-redis redis-cli

# Check health
docker exec -it sicargabox-redis redis-cli ping

# Monitor memory
docker exec -it sicargabox-redis redis-cli INFO memory

# List all keys
docker exec -it sicargabox-redis redis-cli KEYS '*'

# Backup database
docker exec sicargabox-redis redis-cli BGSAVE

# Flush database (⚠️ DESTRUCTIVE)
docker exec -it sicargabox-redis redis-cli FLUSHDB
```
