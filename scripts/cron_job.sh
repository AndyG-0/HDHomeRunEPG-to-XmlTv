#!/bin/bash

# HDHomeRun EPG to XMLTV Cron Job Script
# This script generates both the XMLTV file and M3U playlist

set -e

# Source environment variables from /etc/environment
if [ -f /etc/environment ]; then
    set -a  # automatically export all variables
    source /etc/environment
    set +a
fi

# Explicitly set PATH to include virtual environment
export PATH="/app/.venv/bin:$PATH"

echo "$(date): Starting EPG and M3U generation" >> /app/output/cron.log
echo "$(date): Using Python: $(which python)" >> /app/output/cron.log
echo "$(date): PATH: $PATH" >> /app/output/cron.log

# Generate the XMLTV EPG file
echo "$(date): Generating XMLTV EPG file" >> /app/output/cron.log
if python /app/HDHomeRunEPG_To_XmlTv.py \
    --host "${HDHOMERUN_HOST}" \
    --filename "${EPG_OUTPUT_FILE}" \
    --days "${EPG_DAYS}" \
    --hours "${EPG_HOURS}" \
    --debug "${DEBUG}" \
    >> /app/output/cron.log 2>&1; then
    echo "$(date): XMLTV EPG file generated successfully" >> /app/output/cron.log
else
    echo "$(date): ERROR: Failed to generate XMLTV EPG file" >> /app/output/cron.log
    echo "$(date): EPG generation failed" > /proc/1/fd/1 2>/proc/1/fd/2
    exit 0  # Don't exit the container, just skip M3U generation
fi

# Generate the M3U playlist if XMLTV was successful
if [ -f "${EPG_OUTPUT_FILE}" ]; then
    echo "$(date): Generating M3U playlist" >> /app/output/cron.log
    
    # Determine server URL for M3U generation
    # Use HDHomeRun device for streaming URLs
    SERVER_URL="http://${HDHOMERUN_HOST}:5004"
    
    if python /app/generate_m3u_from_xmltv.py \
        "${EPG_OUTPUT_FILE}" \
        "${M3U_OUTPUT_FILE}" \
        --server-url "${SERVER_URL}" \
        >> /app/output/cron.log 2>&1; then
        echo "$(date): M3U playlist generated successfully" >> /app/output/cron.log
    else
        echo "$(date): ERROR: Failed to generate M3U playlist" >> /app/output/cron.log
    fi
else
    echo "$(date): WARNING: XMLTV file not found, skipping M3U generation" >> /app/output/cron.log
fi

echo "$(date): EPG and M3U generation completed" >> /app/output/cron.log

# Output to container logs as well
echo "$(date): EPG and M3U generation completed" > /proc/1/fd/1 2>/proc/1/fd/2