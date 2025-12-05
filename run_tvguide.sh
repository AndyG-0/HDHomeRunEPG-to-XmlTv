#!/bin/sh
# EPG Generation Script - Runs using uv with environment variables

# Source the .env file if it exists
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '#' | xargs)
fi

# Generate EPG using uv run with environment variables
uv run python /app/HDHomeRunEPG_To_XmlTv.py \
    --host "${HDHOMERUN_HOST:-hdhomerun.local}" \
    --filename "${EPG_OUTPUT_FILE:-/app/output/output.xml}" \
    --days "${EPG_DAYS:-7}" \
    --hours "${EPG_HOURS:-3}" \
    --debug "${DEBUG:-on}" \
    >> /app/output/cron.log 2>&1

echo "TV guide updated at $(date)" >> /app/output/cron.log
