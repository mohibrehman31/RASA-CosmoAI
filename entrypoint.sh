#!/bin/bash
set -e

# Start Nginx
nginx

# Run your Python script
exec python /app/run_servers.py