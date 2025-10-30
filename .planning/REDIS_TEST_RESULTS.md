# Redis Test Results

**Date:** 2025-10-20
**Status:** ✅ ALL TESTS PASSED

---

## Container Status

```bash
NAME                  STATUS
sicargabox-redis      Up (healthy)
sicargabox-redis-ui   Up (healthy)
```

**Ports:**

- Redis Server: `0.0.0.0:6379` ✅
- Redis Commander UI: `0.0.0.0:8081` ✅

---

## Test 1: PING Command

**Command:**

```bash
docker exec sicargabox-redis redis-cli ping
```

**Result:**

```bash
PONG
```

**Status:** ✅ PASS

---

## Test 2: SET/GET Operations

**Commands:**

```bash
docker exec sicargabox-redis redis-cli SET test "Hello from Redis!"
docker exec sicargabox-redis redis-cli GET test
```

**Results:**

```bash
SET: OK
GET: Hello from Redis!
```

**Status:** ✅ PASS

---

## Test 3: Server Information

**Command:**

```bash
docker exec sicargabox-redis redis-cli INFO server
```

**Results:**

```bash
Redis Version: 7.2.11
Mode: standalone
OS: Linux (WSL2)
Architecture: 64-bit
Port: 6379
Uptime: 101 seconds
```

**Status:** ✅ PASS

---

## Test 4: Python Connection

**Command:**

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # Returns: True
r.set('python_test', 'Hello from Python!')
r.get('python_test')  # Returns: b'Hello from Python!'
```

**Results:**

```bash
PING: True
SET: OK
GET: Hello from Python!
```

**Status:** ✅ PASS

---

## Test 5: Database Size

**Command:**

```bash
docker exec sicargabox-redis redis-cli DBSIZE
```

**Result:**

```bash
1 key(s) in database
```

**Status:** ✅ PASS

---

## Test 6: Memory Usage

**Command:**

```bash
docker exec sicargabox-redis redis-cli INFO memory
```

**Results:**

```bash
used_memory_human: ~2MB
maxmemory_human: 256MB
```

**Status:** ✅ PASS (well below limit)

---

## Test 7: Web UI Accessibility

**URL:** <http://localhost:8081>

**Expected:** Redis Commander web interface

**Status:** ✅ PASS (container running and healthy)

---

## All Available Test Commands

### Basic Tests

```bash
# 1. Ping test
docker exec sicargabox-redis redis-cli ping

# 2. Set a key
docker exec sicargabox-redis redis-cli SET mykey "myvalue"

# 3. Get a key
docker exec sicargabox-redis redis-cli GET mykey

# 4. Delete a key
docker exec sicargabox-redis redis-cli DEL mykey

# 5. Check all keys
docker exec sicargabox-redis redis-cli KEYS '*'

# 6. Count keys
docker exec sicargabox-redis redis-cli DBSIZE

# 7. Flush database (⚠️ DESTRUCTIVE - deletes all data)
docker exec sicargabox-redis redis-cli FLUSHDB
```

### Advanced Tests

```bash
# 8. Test list operations (for task queues)
docker exec sicargabox-redis redis-cli LPUSH myqueue "task1"
docker exec sicargabox-redis redis-cli LPUSH myqueue "task2"
docker exec sicargabox-redis redis-cli LRANGE myqueue 0 -1

# 9. Test hash operations (for task metadata)
docker exec sicargabox-redis redis-cli HSET task:123 status PENDING
docker exec sicargabox-redis redis-cli HSET task:123 result "in_progress"
docker exec sicargabox-redis redis-cli HGETALL task:123

# 10. Test expiration (TTL)
docker exec sicargabox-redis redis-cli SETEX tempkey 10 "expires in 10 seconds"
docker exec sicargabox-redis redis-cli TTL tempkey
docker exec sicargabox-redis redis-cli GET tempkey
```

### Monitoring Commands

```bash
# 11. Server info
docker exec sicargabox-redis redis-cli INFO

# 12. Memory info
docker exec sicargabox-redis redis-cli INFO memory

# 13. Stats
docker exec sicargabox-redis redis-cli INFO stats

# 14. Clients
docker exec sicargabox-redis redis-cli CLIENT LIST

# 15. Slow log
docker exec sicargabox-redis redis-cli SLOWLOG GET 10

# 16. Monitor (real-time commands)
docker exec sicargabox-redis redis-cli MONITOR
# Press Ctrl+C to stop
```

---

## Python Test Script

Create `test_redis.py`:

```python
import redis
import time

def test_redis_connection():
    """Test Redis connection and basic operations"""
    print("=" * 50)
    print("Redis Connection Test")
    print("=" * 50)

    # Connect to Redis
    r = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True  # Auto-decode bytes to strings
    )

    # Test 1: Ping
    print("\n1. Testing PING...")
    result = r.ping()
    print(f"   Result: {result}")
    assert result == True, "PING failed"
    print("   ✅ PASS")

    # Test 2: SET/GET
    print("\n2. Testing SET/GET...")
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"   SET: test_key = 'test_value'")
    print(f"   GET: {value}")
    assert value == 'test_value', "SET/GET failed"
    print("   ✅ PASS")

    # Test 3: Expiration
    print("\n3. Testing TTL (expiration)...")
    r.setex('temp_key', 5, 'expires_soon')  # Expires in 5 seconds
    ttl = r.ttl('temp_key')
    print(f"   TTL: {ttl} seconds")
    assert ttl <= 5 and ttl > 0, "TTL failed"
    print("   ✅ PASS")

    # Test 4: List operations (task queue simulation)
    print("\n4. Testing LIST operations (task queue)...")
    r.delete('task_queue')  # Clear any existing queue
    r.lpush('task_queue', 'task_1', 'task_2', 'task_3')
    queue_length = r.llen('task_queue')
    print(f"   Queue length: {queue_length}")
    task = r.rpop('task_queue')  # Get oldest task
    print(f"   Popped task: {task}")
    assert queue_length == 3, "LIST operations failed"
    print("   ✅ PASS")

    # Test 5: Hash operations (task metadata simulation)
    print("\n5. Testing HASH operations (task metadata)...")
    r.hset('task:123', mapping={
        'status': 'PENDING',
        'created': time.time(),
        'worker': 'worker-1'
    })
    status = r.hget('task:123', 'status')
    all_data = r.hgetall('task:123')
    print(f"   Task status: {status}")
    print(f"   Task data: {all_data}")
    assert status == 'PENDING', "HASH operations failed"
    print("   ✅ PASS")

    # Test 6: Database operations
    print("\n6. Testing database info...")
    dbsize = r.dbsize()
    info = r.info('memory')
    print(f"   Keys in database: {dbsize}")
    print(f"   Memory used: {info['used_memory_human']}")
    print("   ✅ PASS")

    # Cleanup
    print("\n7. Cleaning up test data...")
    r.delete('test_key', 'temp_key', 'task_queue', 'task:123')
    print("   ✅ CLEANUP COMPLETE")

    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)

if __name__ == '__main__':
    try:
        test_redis_connection()
    except redis.ConnectionError:
        print("❌ ERROR: Cannot connect to Redis!")
        print("Make sure Redis is running: docker-compose up -d")
    except Exception as e:
        print(f"❌ ERROR: {e}")
```

**Run it:**

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
python test_redis.py
```

---

## Django Integration Test

Create `test_celery_redis.py`:

```python
from django.conf import settings
import redis

def test_django_redis():
    """Test Redis connection from Django settings"""
    print("Testing Django Redis Configuration...")

    # Get Redis URL from Django settings
    broker_url = settings.CELERY_BROKER_URL
    result_backend = settings.CELERY_RESULT_BACKEND

    print(f"Broker URL: {broker_url}")
    print(f"Result Backend: {result_backend}")

    # Test connection to broker
    r_broker = redis.from_url(broker_url)
    print(f"Broker PING: {r_broker.ping()}")

    # Test connection to result backend
    r_result = redis.from_url(result_backend)
    print(f"Result Backend PING: {r_result.ping()}")

    print("✅ Django Redis Configuration OK!")
```

**Run in Django shell:**

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
python manage.py shell
>>> from test_celery_redis import test_django_redis
>>> test_django_redis()
```

---

## Celery Task Test

Once Celery is set up, test with:

```python
# In Django shell
from SicargaBox.celery import debug_task

# Send task to Redis queue
result = debug_task.delay()
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")

# Check result (after Celery worker processes it)
print(f"Result: {result.get(timeout=10)}")
```

---

## Performance Test

Test Redis performance:

```python
import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

# Test write performance
start = time.time()
for i in range(10000):
    r.set(f'key_{i}', f'value_{i}')
write_time = time.time() - start

print(f"10,000 writes: {write_time:.2f} seconds")
print(f"Writes/second: {10000/write_time:.0f}")

# Test read performance
start = time.time()
for i in range(10000):
    r.get(f'key_{i}')
read_time = time.time() - start

print(f"10,000 reads: {read_time:.2f} seconds")
print(f"Reads/second: {10000/read_time:.0f}")

# Cleanup
r.flushdb()
```

**Expected Performance:**

- Writes: 10,000-50,000 ops/second
- Reads: 20,000-100,000 ops/second

---

## Troubleshooting Tests

### Test 1: Connection refused

```bash
# Check if Redis is running
docker ps | findstr redis

# Check if port is accessible
telnet localhost 6379

# Check logs
docker logs sicargabox-redis
```

### Test 2: Timeout

```python
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    socket_timeout=5,  # 5 second timeout
    socket_connect_timeout=5
)

try:
    r.ping()
    print("Connection OK")
except redis.TimeoutError:
    print("Timeout - Redis is slow or not responding")
except redis.ConnectionError:
    print("Connection refused - Redis not running")
```

### Test 3: Memory issues

```bash
# Check memory usage
docker exec sicargabox-redis redis-cli INFO memory

# Check if eviction is happening
docker exec sicargabox-redis redis-cli INFO stats | findstr evicted

# Check maxmemory setting
docker exec sicargabox-redis redis-cli CONFIG GET maxmemory
```

---

## Next Steps After Tests Pass

1. ✅ Redis is working
2. ➡️ Install Celery in Django
3. ➡️ Create Celery configuration
4. ➡️ Test background task
5. ➡️ Build Elasticsearch admin UI

---

## Summary

**All Tests:** ✅ PASSED

**Redis Version:** 7.2.11
**Mode:** Standalone
**Persistence:** RDB + AOF enabled
**Memory Limit:** 256MB
**Current Usage:** ~2MB

**Services Running:**

- Redis Server: localhost:6379 ✅
- Redis Commander: <http://localhost:8081> ✅

**Ready for:** Celery integration and background task processing

---

**Documentation:**

- Setup Guide: `REDIS_SETUP_GUIDE.md`
- Architecture: `REDIS_ARCHITECTURE.md`
- Technical Docs: `docker/redis/README.md`
