# Redis Dockerfile for SicargaBox Project
# Based on official Redis Alpine image (lightweight)

FROM redis:7.2-alpine

# Add custom configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Create data directory for persistence
RUN mkdir -p /data

# Expose Redis port
EXPOSE 6379

# Run Redis with custom configuration
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
