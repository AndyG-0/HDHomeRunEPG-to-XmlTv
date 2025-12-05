#!/bin/bash

# Health check script for HDHomeRun EPG to XMLTV Container
# Works for both file-only and http modes

set -e

if [ "${CONTAINER_MODE}" = "http" ]; then
    # In HTTP mode, check if the HTTP server is responding
    if curl -f -s "http://localhost:${HTTP_PORT}/epg.xml" > /dev/null 2>&1; then
        echo "HTTP server is healthy"
        exit 0
    else
        echo "HTTP server is not responding"
        exit 1
    fi
elif [ "${CONTAINER_MODE}" = "file-only" ]; then
    # In file-only mode, check if cron is running and EPG file exists
    if pgrep cron > /dev/null 2>&1; then
        echo "Cron service is running"
        
        # Check if EPG file was generated recently (within last 6 hours)
        if [ -f "${EPG_OUTPUT_FILE}" ]; then
            # Get file modification time in seconds since epoch
            file_mtime=$(stat -c %Y "${EPG_OUTPUT_FILE}" 2>/dev/null || echo 0)
            current_time=$(date +%s)
            age=$((current_time - file_mtime))
            
            # 21600 seconds = 6 hours
            if [ $age -lt 21600 ]; then
                echo "EPG file exists and is recent"
                exit 0
            else
                echo "EPG file is too old (age: ${age} seconds)"
                exit 1
            fi
        else
            echo "EPG file does not exist"
            exit 1
        fi
    else
        echo "Cron service is not running"
        exit 1
    fi
else
    echo "Invalid CONTAINER_MODE: ${CONTAINER_MODE}"
    exit 1
fi