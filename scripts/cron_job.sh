#!/bin/bash

# HDHomeRun EPG to XMLTV Cron Job Script
# This script generates both the XMLTV file and M3U playlist

set -e

echo "$(date): Starting EPG and M3U generation" >> /app/output/cron.log

# Generate the XMLTV EPG file
echo "$(date): Generating XMLTV EPG file" >> /app/output/cron.log
if uv run python /app/HDHomeRunEPG_To_XmlTv.py \
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
    if [ "${CONTAINER_MODE}" = "http" ]; then
        SERVER_URL="http://${HTTP_BIND_ADDRESS}:${HTTP_PORT}"
        # If bind address is 0.0.0.0, use localhost for internal generation
        if [ "${HTTP_BIND_ADDRESS}" = "0.0.0.0" ]; then
            SERVER_URL="http://localhost:${HTTP_PORT}"
        fi
    else
        # In file-only mode, use a placeholder URL
        SERVER_URL="http://localhost:8000"
    fi
    
    if uv run python /app/generate_m3u_from_xmltv.py \
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