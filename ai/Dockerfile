# Use Debian Buster as the base image
FROM debian:buster

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --upgrade pip \
    && pip3 install Flask

# Expose the port that Daphne will run on
EXPOSE 5000

COPY ai.py .

CMD ["python3", "-m", "flask", "--app", "ai", "run", "--host=0.0.0.0", "--debug"]
