# HDHomeRun EPG to XMLTV Converter

[![Build Status](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/workflows/Build%20and%20Push%20Docker%20Image/badge.svg)](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/ghcr.io/andyg-0/hdhomerun-epg)](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/pkgs/container/hdhomerun-epg)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub release](https://img.shields.io/github/v/release/AndyG-0/HDHomeRunEPG-to-XmlTv)](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/releases/latest)
[![semantic-release: conventional](https://img.shields.io/badge/semantic--release-conventional-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)

<div align="right">
<a href="https://buymeacoffee.com/incubusvictim" target="_blank"><img align="top" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a> <img align="top" src="https://github.com/IncubusVictim/HDHomeRunEPG-to-XmlTv/blob/main/bmc_qr.png" width="100" />
</div>

A Python application that downloads Electronic Program Guide (EPG) data from HDHomeRun devices and converts it to XMLTV format for use with media servers like Jellyfin, Plex, and IPTV apps like UHF.

## ✨ New Docker Features

### 🐳 Two Container Modes

**HTTP Mode** (Default)
- Runs a web server serving both XMLTV and M3U files
- Perfect for media servers and IPTV apps
- Access files at `http://container:9999/epg.xml` and `http://container:9999/channels.m3u`

**File-Only Mode**
- Generates files to mounted volumes only
- Lower resource usage, no HTTP server
- Great for systems that prefer file-based integration

### ⏱️ Automated Scheduling
- Configurable cron jobs (default: every 4 hours)
- Automatic EPG and M3U generation
- Built-in health checks and monitoring
- Graceful shutdown support

### 🚀 GitHub Container Registry
```bash
# Pull the latest image
docker pull ghcr.io/andyg-0/hdhomerun-epg:latest

# Run in HTTP mode
docker run -d \
  -p 9999:9999 \
  -e HDHOMERUN_HOST=192.168.1.100 \
  -e CONTAINER_MODE=http \
  ghcr.io/andyg-0/hdhomerun-epg:latest

# Run in file-only mode
docker run -d \
  -v ./output:/app/output \
  -e HDHOMERUN_HOST=192.168.1.100 \
  -e CONTAINER_MODE=file-only \
  ghcr.io/andyg-0/hdhomerun-epg:latest
```

## Features

- 📺 Downloads EPG data directly from HDHomeRun devices  
- 🔄 Converts to standard XMLTV format
- 📱 Compatible with IPTV apps (UHF, TiviMate, etc.)
- 🎬 Works with media servers (Jellyfin, Plex)
- ⚡ Built-in HTTP server for easy access
- 🐳 Docker support with automated scheduling
- 🔧 Auto-generates matching M3U playlists

## Quick Start

### Using UV (Recommended)

```bash
# Install dependencies
uv sync

# Generate XMLTV file
uv run python HDHomeRunEPG_To_XmlTv.py --host YOUR_HDHOMERUN_IP

# Start HTTP server (optional)
uv run python http_server.py
```

### Using Docker

```bash
# Update HDHomeRun IP in docker-compose.yml
docker compose up
```

Your XMLTV file will be available at `http://localhost:9999/epg.xml`

## M3U Playlist Integration

### Auto-Generate Matching Playlist (Recommended)

For the best experience with IPTV apps, auto-generate an M3U playlist with correctly matched channel IDs:

```bash
# 1. Generate XMLTV
uv run python HDHomeRunEPG_To_XmlTv.py --host YOUR_HDHOMERUN_IP

# 2. Auto-generate matching M3U
uv run python generate_m3u_from_xmltv.py epg.xml playlist.m3u --server-url http://YOUR_SERVER:9999

# 3. Verify matching (optional)
uv run python tests/test_m3u_xmltv_matching.py playlist.m3u epg.xml
```

### Channel ID Format

The tool uses HDHomeRun's RF channel format with sub-channels:
- `hdhomerun.3.1` - RF Channel 3, Sub-channel 1
- `hdhomerun.3.2` - RF Channel 3, Sub-channel 2  
- `hdhomerun.10.1` - RF Channel 10, Sub-channel 1

### Manual M3U Example

```m3u
#EXTM3U
#EXTINF:-1 tvg-id="hdhomerun.3.1" tvg-name="KTVK-HD",KTVK-HD
http://your-hdhomerun-ip:5004/auto/v3.1
#EXTINF:-1 tvg-id="hdhomerun.3.2" tvg-name="Comet",Comet  
http://your-hdhomerun-ip:5004/auto/v3.2
```

**Important:** The `tvg-id` values must exactly match the channel IDs in your XMLTV file.

## Usage

```
python HDHomeRunEPG_To_XmlTv.py [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | HDHomeRun IP address | `hdhomerun.local` |
| `--filename` | Output file path | `./output/epg.xml` |
| `--days` | Days of EPG data | `7` |
| `--hours` | Hours per request iteration | `3` |
| `--debug` | Debug level (`on`, `full`, `off`) | `on` |

## Installation

### Using UV Package Manager (Recommended)

UV is a fast, reliable Python package installer that's perfect for this project.

#### Install UV

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Install Dependencies

```bash
cd HDHomeRunEPG-to-XmlTv
uv sync
```

#### Run the Application

```bash
uv run python HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100
```

### Traditional Python Setup

If you prefer using pip:

```bash
# Install Python 3.9 or higher
python --version

# Install dependencies
pip install -r pyproject.toml

# Run application  
python HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100
```

## Docker Usage

### Quick Start

1. Edit `docker-compose.yml` and set your HDHomeRun IP:
   ```yaml
   environment:
     - HDHOMERUN_HOST=192.168.1.100
   ```

2. Start the container:
   ```bash
   docker compose up -d
   ```

3. Access your EPG at: `http://localhost:9999/epg.xml`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HDHOMERUN_HOST` | HDHomeRun device IP/hostname | `hdhomerun.local` |
| `EPG_OUTPUT_FILE` | Output file path | `/app/output/epg.xml` |
| `EPG_DAYS` | Days of EPG data | `7` |
| `CRON_SCHEDULE` | Cron schedule for updates | `0 1 * * *` (1 AM daily) |
| `HTTP_PORT` | HTTP server port | `9999` |

The container automatically:
- Updates EPG data on schedule (default: daily at 1 AM)
- Serves XMLTV file via HTTP server
- Saves output to `/app/output/` directory

## App Integration

### UHF (Apple TV/iOS)
1. Generate XMLTV and matching M3U playlist (see above)
2. Host files on HTTP server: `uv run python http_server.py`
3. In UHF: Settings → Add playlist URL and EPG URL

### Jellyfin
1. Settings → Live TV → Add Tuner → HDHomeRun  
2. Settings → Live TV → Guide Data → Add XML guide
3. Point to your XMLTV file or HTTP URL

### Plex
Use HDHomeRun integration or import XMLTV as custom guide data.

## Troubleshooting

### 403 Forbidden Error
HDHomeRun may be blocking requests. This could be due to:
- Rate limiting from too many requests
- Network configuration issues
- Firmware restrictions

### No EPG Data in IPTV App
- Verify `tvg-id` values in M3U match XMLTV channel IDs exactly
- Use auto-generated M3U playlist for guaranteed matching
- Check that both files are accessible to your IPTV app

### HTTP 400 Bad Request
The script handles this gracefully when requesting data beyond device limits (usually 1-2 days).

## Project Structure

```
├── HDHomeRunEPG_To_XmlTv.py    # Main application
├── http_server.py              # HTTP server for XMLTV access  
├── generate_m3u_from_xmltv.py  # M3U playlist generator
├── docs/                       # Documentation
├── examples/                   # Example M3U files
├── scripts/                    # Utility scripts
├── tests/                      # Test suite
└── output/                     # Generated files
```

## Releases & Versioning

### Latest Release
Visit the [Releases page](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/releases) for the latest stable version.

### Docker Image Versions
```bash
# Latest stable release
docker pull ghcr.io/andyg-0/hdhomerunepg-to-xmltv:latest

# Specific version
docker pull ghcr.io/andyg-0/hdhomerunepg-to-xmltv:1.2.3

# Development builds
docker pull ghcr.io/andyg-0/hdhomerunepg-to-xmltv:main
```

### Release Process
This project uses automated releases with semantic versioning:
- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features 
- **Patch** (1.0.0 → 1.0.1): Bug fixes

All releases include:
- ✅ Automated testing and security scanning
- 🐳 Multi-architecture Docker images (amd64/arm64)
- 📋 Auto-generated release notes
- 🔄 GitHub Container Registry publication

For developers, see [Release Guide](docs/RELEASE_GUIDE.md) for creating releases.

## Development

### Running Tests
```bash
uv run python -m unittest discover -s tests -v
```

### UV Advantages
- 5-10x faster than pip
- Deterministic dependency resolution  
- Built-in virtual environment management
- Cross-platform Python installation

## Binaries

Pre-built binaries are available in the `binaries/` directory for:
- Debian Linux
- macOS  
- Windows

Extract and run with: `./HDHomeRunEPG_To_XmlTv --host YOUR_IP`

## Acknowledgments

- [@supitsmike] - Fixed "New" episode bug (#5)
- [@AcSlayter] - Docker support (#13)  
- [@Sujeom] - Status handling fix (#14)

## Important Notice

If you receive a "403 Forbidden" error, HDHomeRun may be blocking requests. This hardware is designed to work with various software solutions, so this would be disappointing if intentionally restricted.

## License

GPL License - See project repository for details.
`
