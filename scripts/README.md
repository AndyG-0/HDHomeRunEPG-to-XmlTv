# Scripts Directory

This directory contains utility scripts for the HDHomeRunEPG-to-XmlTv project. Most of these scripts are **not required for normal operation**.

## Essential Scripts (Used Automatically)

These scripts are automatically used by the Docker container and main workflow:

### `cron_job.sh` ✅ **Required**
- Automatically runs EPG and M3U generation on schedule
- Used by the Docker container's cron system
- Generates both XMLTV and M3U files in sequence

### `entrypoint.sh` ✅ **Required** 
- Docker container startup script
- Sets up cron scheduling and environment
- Manages container lifecycle

### `healthcheck.sh` ✅ **Required**
- Docker container health monitoring
- Used by Docker's health check system

## Utility Scripts (Manual/Optional)

These scripts are utilities for specific use cases and troubleshooting:

### `uhf_epg_diagnostic.py` 🔧 **Diagnostic Tool**
- **Purpose**: Troubleshoot IPTV app issues (like UHF showing wrong EPG data)
- **When to use**: Only if your IPTV app shows duplicate programs or wrong EPG data
- **Usage**: `python uhf_epg_diagnostic.py channels.m3u epg.xml`
- **Note**: The main generation scripts create correct files - use this only for troubleshooting

## Development Scripts

### `create_release.sh` 🛠️ **Development Only**
- Used for creating project releases
- Not needed for end users

## Normal Workflow (No Manual Scripts Required)

For normal operation, you don't need to run any of these scripts manually:

1. **Container Mode**: 
   - Docker automatically runs `entrypoint.sh` → `cron_job.sh` → generates files
   - Files served via HTTP endpoints

2. **Manual Mode**:
   ```bash
   # Generate XMLTV
   python HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100
   
   # Generate M3U from XMLTV
   python generate_m3u_from_xmltv.py output/epg.xml output/channels.m3u
   
   # Serve files (optional)
   python http_server.py
   ```

## When to Use Utility Scripts

- **Rarely**: Use `uhf_epg_diagnostic.py` only if IPTV app shows problems
- **Development**: Use `create_release.sh` only if you're a maintainer

The main generation scripts automatically create properly formatted files that work with IPTV apps like UHF, Jellyfin, Plex, etc.