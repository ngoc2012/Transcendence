# Use Debian Buster as the base image
FROM debian:buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USERNAME=admin
ENV PASSWORD=admin
ENV EMAIL=admin@gmail.com


# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3 \
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
# Set the working directory

# WORKDIR /app/backend

# Expose the port that Daphne will run on
EXPOSE 8000

# Run Daphne as the default command
#necessaire pour la db?
# CMD ["python3", "manage.py", "migrate"] 
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
CMD ./entrypoint.sh
# CMD python3 manage.py migrate; \
# python3 manage.py createsuperuser --noinput --username $USERNAME --email $EMAIL; \
# python3 changesuperuserpw.py -n $USERNAME -p $PASSWORD; \
# python3 manage.py runserver 0.0.0.0:8000



# CMD ["python3", "manage.py", "createsuperuser", "--noinput", "--username", "admin", "--email", "admin@gmail.com"]

# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["daphne", "-u", "asgi:application", "--port", "8000", "--bind", "0.0.0.0"]
