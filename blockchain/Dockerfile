# Use Debian Buster as the base image
FROM debian:buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3 \
        wget \
        python3-pip \
        python3-dev \
        libffi-dev \
        libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --upgrade pip \
    && pip3 install Django && \
    pip3 install channels daphne \
    && pip3 install requests

#Blockchain

RUN     apt-get update
RUN     apt-get install netcat -y
RUN     pip3 install web3
RUN     pip3 install pyjwt
RUN     pip3 install --no-cache-dir psycopg2-binary sqlalchemy

RUN     pip3 install Flask

RUN apt-get update && apt-get install -y curl

RUN apt-get update && \
 apt-get install -y \
    nodejs npm

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

RUN npm install -g truffle -y


#pour netstat
RUN apt update
RUN apt install net-tools

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh


COPY web3_handling.py .

ENTRYPOINT [ "./entrypoint.sh" ]

EXPOSE 7000

# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["sleep", "infinity"]