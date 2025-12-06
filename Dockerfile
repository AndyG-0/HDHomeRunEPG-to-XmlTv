# syntax=docker/dockerfile:1.11
FROM python:3.14-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    wget \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project configuration files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application files
COPY HDHomeRunEPG_To_XmlTv.py ./
COPY generate_m3u_from_xmltv.py ./
# Updated for tvg-id fix
COPY http_server.py ./

# Create scripts directory and copy scripts
RUN mkdir -p /app/scripts
COPY scripts/cron_job.sh /app/scripts/
COPY scripts/entrypoint.sh /app/scripts/
COPY scripts/healthcheck.sh /app/scripts/

# Create output directory for EPG files
RUN mkdir -p /app/output

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Create the log file for cron
RUN touch /var/log/cron.log

# Default environment variables
ENV HDHOMERUN_HOST=192.168.1.100 \
    EPG_OUTPUT_FILE=/app/output/epg.xml \
    M3U_OUTPUT_FILE=/app/output/channels.m3u \
    EPG_DAYS=7 \
    EPG_HOURS=3 \
    DEBUG=on \
    HTTP_PORT=9999 \
    HTTP_BIND_ADDRESS=0.0.0.0 \
    CRON_SCHEDULE="0 */4 * * *" \
    CONTAINER_MODE=http

# Add container labels for metadata
LABEL org.opencontainers.image.title="HDHomeRun EPG to XMLTV" \
      org.opencontainers.image.description="Convert HDHomeRun EPG data to XMLTV format with M3U playlist generation" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.source="https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv" \
      org.opencontainers.image.licenses="GPL-3.0-or-later" \
      org.opencontainers.image.vendor="HDHomeRun EPG Project"

# Health check that works for both modes
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /app/scripts/healthcheck.sh

# Expose HTTP port (only used in http mode)
EXPOSE 9999

# Set entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

