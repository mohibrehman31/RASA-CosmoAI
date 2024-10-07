# Build stage
FROM python:3.8-slim-buster as builder

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y nginx
# Set working directory
COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Copy the server manager script
COPY run_servers.py .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# Set environment variables
ENV RASA_MODEL=models/20241007-050844-cerulean-date.tar.gz
ENV ENDPOINTS_FILE=endpoints.yml
ENV CREDENTIALS_FILE=credentials.yml
ENV FLASK_APP=flask_app.py
EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
# Expose ports

# Run the server manager
CMD ["python", "run_servers.py"]