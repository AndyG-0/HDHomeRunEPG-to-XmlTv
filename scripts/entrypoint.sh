#!/bin/bash

# HDHomeRun EPG to XMLTV Container Entrypoint
# Supports two modes: file-only and http

set -e

echo "Starting HDHomeRun EPG to XMLTV Container"
echo "Container mode: ${CONTAINER_MODE}"
echo "Cron schedule: ${CRON_SCHEDULE}"

# Validate required environment variables
if [ -z "${HDHOMERUN_HOST}" ]; then
    echo "ERROR: HDHOMERUN_HOST environment variable is required"
    exit 1
fi

# Create environment file for cron jobs
# Include PATH to ensure uv and python are accessible
printenv | grep -E '^(HDHOMERUN_HOST|EPG_OUTPUT_FILE|M3U_OUTPUT_FILE|EPG_DAYS|EPG_HOURS|DEBUG|HTTP_PORT|HTTP_BIND_ADDRESS|CONTAINER_MODE|PATH)=' > /etc/environment

# Setup cron job with the configured schedule
echo "Setting up cron job with schedule: ${CRON_SCHEDULE}"
echo "${CRON_SCHEDULE} /app/scripts/cron_job.sh" > /tmp/crontab
echo "" >> /tmp/crontab  # Cron requires a newline at the end
crontab /tmp/crontab
rm /tmp/crontab

# Start cron service
echo "Starting cron service"
cron

# Generate initial EPG and M3U files
echo "Running initial EPG and M3U generation"
/app/scripts/cron_job.sh || echo "Initial EPG generation failed, but continuing..."

# SIGTERM handler for graceful shutdown
term_handler() {
    echo "Received SIGTERM, shutting down gracefully..."
    
    # Stop cron service
    service cron stop
    
    # Wait for any running cron jobs to complete (with timeout)
    timeout=30
    count=0
    while [ $count -lt $timeout ]; do
        if ! pgrep -f "cron_job.sh" > /dev/null; then
            break
        fi
        echo "Waiting for cron jobs to complete..."
        sleep 1
        count=$((count + 1))
    done
    
    echo "Shutdown complete"
    exit 0
}

# Set up signal handlers
trap term_handler SIGTERM SIGINT

# Choose execution path based on container mode
if [ "${CONTAINER_MODE}" = "http" ]; then
    echo "Starting HTTP server mode on ${HTTP_BIND_ADDRESS}:${HTTP_PORT}"
    
    # Start HTTP server in the background
    python /app/http_server.py &
    SERVER_PID=$!
    
    # Wait for either the server to exit or a signal
    wait $SERVER_PID
    
elif [ "${CONTAINER_MODE}" = "file-only" ]; then
    echo "Running in file-only mode - EPG and M3U files will be generated via cron"
    echo "Files will be written to ${EPG_OUTPUT_FILE} and ${M3U_OUTPUT_FILE}"
    
    # In file-only mode, just keep the container running and let cron handle everything
    while true; do
        sleep 30
    done
    
else
    echo "ERROR: Invalid CONTAINER_MODE '${CONTAINER_MODE}'. Must be 'http' or 'file-only'"
    exit 1
fi