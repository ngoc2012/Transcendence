FROM debian:latest

# Update package lists and install Redis
RUN apt-get update && \
    apt-get install -y redis-server && \
    apt-get install -y procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]

# Expose Redis port
EXPOSE 6379

# Start Redis server when the container launches
CMD ["redis-server", "--protected-mode no"]