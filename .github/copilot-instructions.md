---
applyTo: '**'
---

# HDHomeRun EPG to XMLTV - Development and Build Instructions

## Using UV Package Manager

This project uses `uv` instead of traditional pip for dependency management. `uv` is a fast, reliable Python package installer and resolver.

### Installation

#### On macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### On Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### On Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Quick Start

After installing uv, navigate to the project directory and run:

```bash
# Install dependencies from pyproject.toml
uv sync

# Run a Python script using the project environment
uv run python HDHomeRunEPG_To_XmlTv.py --help

# Or directly with uv run
uv run python HDHomeRunEPG_To_XmlTv.py --host 192.168.1.100
```

### Common Tasks

#### Create Virtual Environment
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Install All Dependencies
```bash
uv sync
```

#### Add a New Dependency
```bash
uv add package-name
```

#### Remove a Dependency
```bash
uv remove package-name
```

#### Run Tests or Scripts
```bash
uv run python script.py
uv run pytest
```

#### Lock Dependencies
```bash
uv lock
```

### Docker Usage

The Dockerfile in this project is pre-configured to use uv. When building the Docker image:

```bash
docker build -t hdhomerun-epg:latest .
```

The container will automatically install dependencies using uv during the build process.

### Key Advantages of UV

- **Speed**: Significantly faster than pip, often 5-10x faster
- **Reliability**: Deterministic dependency resolution
- **Python Version Management**: Built-in Python installation without system dependencies
- **Lock File**: `uv.lock` ensures reproducible builds across environments
- **Simple Syntax**: Cleaner commands compared to pip/venv workflows

### Managing Environment Variables

This project uses a `.env` file for configuration:

1. Copy the `.env` file and update variables as needed
2. The application automatically loads these variables on startup
3. Required variables:
   - `HDHOMERUN_HOST`: IP/hostname of HDHomeRun device
   - `EPG_OUTPUT_FILE`: Where to save the XMLTV file
   - `HTTP_PORT`: Port for the HTTP server
   - `CRON_SCHEDULE`: Cron expression for EPG refresh

### Development Workflow

```bash
# 1. Install dependencies
uv sync

# 2. Run the application locally
uv run python HDHomeRunEPG_To_XmlTv.py --host your-hdhomerun-ip

# 3. View server on http://localhost:8000
```

### Troubleshooting

If you encounter issues:

1. **Clear cache**: `uv cache clean`
2. **Reinstall dependencies**: `rm uv.lock && uv sync`
3. **Check Python version**: `uv python --list`
4. **Use specific Python version**: `uv run --python 3.9 python script.py`

For more information, visit [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
