#!/bin/bash

mkdir -p /app/config/
cp --dereference /etc/nginx/ssl/* /app/config/

exec "$@"
