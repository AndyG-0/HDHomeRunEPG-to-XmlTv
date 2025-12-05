# HDHomeRun EPG to XMLTV - Docker Architecture Guide

## Overview

This document describes the new Docker architecture supporting two operational modes: HTTP and file-only, with automated scheduling and proper containerization best practices.

## Container Modes

### HTTP Mode (Default)
- Runs a web server on port 8000
- Serves both XMLTV EPG data and M3U playlists
- Perfect for media servers and IPTV applications
- Includes status and health check endpoints

**Endpoints:**
- `/epg.xml` - XMLTV EPG data
- `/channels.m3u` - M3U playlist
- `/status` - Server status information
- `/health` - Health check endpoint

### File-Only Mode
- Generates files to mounted volumes only
- No HTTP server, lower resource usage
- Suitable for file-based integrations
- Ideal for systems that prefer direct file access

## Environment Variables

### Required
- `HDHOMERUN_HOST` - IP address or hostname of HDHomeRun device

### Container Configuration
- `CONTAINER_MODE` - Set to `http` or `file-only` (default: `http`)
- `CRON_SCHEDULE` - Cron expression for EPG refresh (default: `0 */4 * * *`)

### EPG Generation
- `EPG_OUTPUT_FILE` - Path to XMLTV output file (default: `/app/output/epg.xml`)
- `M3U_OUTPUT_FILE` - Path to M3U playlist file (default: `/app/output/channels.m3u`)
- `EPG_DAYS` - Number of days of EPG data (default: `7`)
- `EPG_HOURS` - Hours of EPG data per request (default: `3`)
- `DEBUG` - Debug mode: `on`, `off`, or `full` (default: `on`)

### HTTP Server (HTTP mode only)
- `HTTP_PORT` - Port for HTTP server (default: `8000`)
- `HTTP_BIND_ADDRESS` - Bind address (default: `0.0.0.0`)

## Docker Compose Examples

### HTTP Mode
```yaml
services:
  tvguide-http:
    image: ghcr.io/andyg-0/hdhomerun-epg:latest
    container_name: tvguide-http
    ports:
      - "8000:8000"
    volumes:
      - tvguide_data:/app/output
    environment:
      - CONTAINER_MODE=http
      - HDHOMERUN_HOST=192.168.1.100
      - CRON_SCHEDULE=0 */4 * * *
    restart: unless-stopped

volumes:
  tvguide_data:
```

### File-Only Mode
```yaml
services:
  tvguide-file-only:
    image: ghcr.io/andyg-0/hdhomerun-epg:latest
    container_name: tvguide-file-only
    volumes:
      - ./output:/app/output
    environment:
      - CONTAINER_MODE=file-only
      - HDHOMERUN_HOST=192.168.1.100
      - CRON_SCHEDULE=0 */4 * * *
    restart: unless-stopped
```

## Health Checks

### HTTP Mode Health Check
- Tests HTTP server response at `/epg.xml`
- Verifies server accessibility and file generation

### File-Only Mode Health Check
- Checks cron service status
- Validates EPG file existence and freshness (within 6 hours)

## Logging

### Container Logs
- Startup and configuration information
- Cron job execution status
- Health check results
- Error messages

### Application Logs
- Detailed EPG generation logs in `/app/output/cron.log`
- HTTP server access logs (HTTP mode)
- Debug information based on DEBUG setting

## File Outputs

### XMLTV File (`epg.xml`)
- Standard XMLTV format EPG data
- Compatible with Jellyfin, Plex, and other media servers
- Contains channel and program information

### M3U Playlist (`channels.m3u`)
- IPTV playlist with tvg-id matching XMLTV channels
- Compatible with UHF, TiviMate, and other IPTV apps
- Automatically generated URLs for HTTP mode

## Scheduling

### Default Schedule
- Runs every 4 hours: `0 */4 * * *`
- Configurable via `CRON_SCHEDULE` environment variable

### Schedule Examples
```bash
# Every hour
CRON_SCHEDULE="0 * * * *"

# Twice daily (6 AM and 6 PM)
CRON_SCHEDULE="0 6,18 * * *"

# Daily at 2 AM
CRON_SCHEDULE="0 2 * * *"

# Every 30 minutes
CRON_SCHEDULE="*/30 * * * *"
```

## Signal Handling

### Graceful Shutdown
- Responds to SIGTERM and SIGINT signals
- Waits for running cron jobs to complete (30-second timeout)
- Properly stops cron and HTTP services

### Container Restart Policies
- `unless-stopped` recommended for production
- Automatically restarts on failure
- Preserves data in mounted volumes

## Security Considerations

### Network Access
- HTTP mode exposes port 8000
- File-only mode requires no exposed ports
- Consider firewall rules for HTTP access

### File Permissions
- Container runs as root (required for cron)
- Output directory should have appropriate permissions
- Volume mounts should consider host permissions

## Troubleshooting

### Common Issues

1. **Container exits immediately**
   - Check HDHOMERUN_HOST is reachable
   - Verify HDHomeRun device is accessible
   - Review container logs for error messages

2. **EPG file not generated**
   - Verify HDHomeRun device IP/hostname
   - Check network connectivity from container
   - Review cron.log for detailed error messages

3. **HTTP server not accessible**
   - Ensure CONTAINER_MODE=http
   - Check port mapping in docker run/compose
   - Verify HTTP_BIND_ADDRESS and HTTP_PORT settings

4. **Health checks failing**
   - Check if EPG generation is working
   - Verify files are being created in output directory
   - Review health check logs in container output

### Debug Commands

```bash
# Check container status
docker ps -a

# View container logs
docker logs container-name

# Execute commands in running container
docker exec -it container-name /bin/bash

# Check cron service
docker exec container-name pgrep cron

# View EPG generation logs
docker exec container-name cat /app/output/cron.log

# Manual EPG generation test
docker exec container-name /app/scripts/cron_job.sh
```

## Performance Considerations

### Resource Usage
- HTTP mode: ~50-100MB RAM, minimal CPU
- File-only mode: ~30-50MB RAM, minimal CPU
- Disk usage depends on EPG data size

### Scaling
- Single HDHomeRun device per container
- Multiple containers for multiple devices
- Consider load balancing for HTTP mode

### Caching
- HTTP mode includes 5-minute cache headers
- EPG data refreshes based on cron schedule
- M3U playlist regenerated with each EPG update

## Migration from Previous Versions

### Environment Variable Changes
- `EPG_OUTPUT_FILE` replaces previous file naming
- New `CONTAINER_MODE` variable required
- `CRON_SCHEDULE` replaces hardcoded scheduling

### Volume Mount Updates
- Use `/app/output` as mount point
- Previous scripts in `/app` are now in `/app/scripts`
- Log files now in output directory

### Docker Compose Updates
- Update image to use GitHub Container Registry
- Add CONTAINER_MODE environment variable
- Consider using profiles for different modes

## CI/CD Pipeline

### GitHub Actions Workflow
- Automated testing with pytest and linting
- Security scanning with Trivy
- Multi-architecture builds (amd64, arm64)
- Automatic image publishing to ghcr.io

### Quality Assurance
- Code formatting with ruff and black
- Type checking with mypy
- Test coverage reporting
- Container security scanning

### Release Process
- Semantic versioning with git tags
- Automated releases on version tags
- Latest tag for main branch
- Development images for feature branches