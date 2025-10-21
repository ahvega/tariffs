FROM docker.elastic.co/elasticsearch/elasticsearch:8.19.5

# Set environment variables (can be overridden by docker-compose.yml)
ENV discovery.type=single-node
ENV xpack.security.enabled=false
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

# Expose the Elasticsearch HTTP and TCP ports
EXPOSE 9200
EXPOSE 9300

# Run Elasticsearch when the container starts
CMD ["elasticsearch"]
