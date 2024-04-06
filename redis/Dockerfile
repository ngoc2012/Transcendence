FROM debian:latest

# Update package lists and install Redis
RUN apt-get update && \
    apt-get install -y redis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Expose Redis port
EXPOSE 6379

# Start Redis server when the container launches
CMD ["redis-server"]