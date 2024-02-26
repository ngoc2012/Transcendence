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
    
RUN     pip3 install pyjwt

RUN     pip3 install google-auth google-auth-oauthlib google-auth-httplib2
RUN     pip3 install pyotp
RUN     pip3 install sendgrid

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]

# Expose the port that Daphne will run on
EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
