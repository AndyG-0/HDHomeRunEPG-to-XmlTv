#!/bin/bash

# Release script for HDHomeRun EPG to XMLTV project
# Usage: ./scripts/create_release.sh [version]
# Example: ./scripts/create_release.sh 1.2.3

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get version from argument or prompt
if [ -z "$1" ]; then
    echo -e "${BLUE}Enter the new version (e.g., 1.2.3):${NC}"
    read -r VERSION
else
    VERSION=$1
fi

# Validate version format (semantic versioning)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$ ]]; then
    echo -e "${RED}❌ Error: Version must follow semantic versioning format (e.g., 1.2.3 or 1.2.3-beta.1)${NC}"
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  Warning: You're not on the main branch. Current branch: $CURRENT_BRANCH${NC}"
    echo -e "${BLUE}Do you want to continue? (y/N):${NC}"
    read -r CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Aborted${NC}"
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${RED}❌ Error: You have uncommitted changes. Please commit or stash them first.${NC}"
    git status --short
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^v${VERSION}$"; then
    echo -e "${RED}❌ Error: Tag v${VERSION} already exists${NC}"
    exit 1
fi

# Update to latest main
echo -e "${BLUE}🔄 Updating to latest main...${NC}"
git fetch origin
git pull origin main

# Run tests to ensure everything is working
echo -e "${BLUE}🧪 Running tests...${NC}"
if command -v uv &> /dev/null; then
    uv run pytest tests/ -v || {
        echo -e "${RED}❌ Tests failed. Please fix issues before releasing.${NC}"
        exit 1
    }
else
    echo -e "${YELLOW}⚠️  Warning: uv not found, skipping tests${NC}"
fi

# Create and push the tag
echo -e "${BLUE}🏷️  Creating tag v${VERSION}...${NC}"
git tag -a "v${VERSION}" -m "Release version ${VERSION}

## Features in this release
- Automated EPG to XMLTV conversion
- M3U playlist generation
- Docker containerization with HTTP and file-only modes
- Configurable cron scheduling
- Multi-architecture support (amd64/arm64)

## Quick Start
\`\`\`bash
# HTTP Mode
docker run -d -p 8000:8000 -e CONTAINER_MODE=http -e HDHOMERUN_HOST=192.168.1.100 ghcr.io/andyg-0/hdhomerunepg-to-xmltv:${VERSION}

# File-Only Mode
docker run -d -v ./output:/app/output -e CONTAINER_MODE=file-only -e HDHOMERUN_HOST=192.168.1.100 ghcr.io/andyg-0/hdhomerunepg-to-xmltv:${VERSION}
\`\`\`

For more information, see the documentation at https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv"

echo -e "${BLUE}📤 Pushing tag to GitHub...${NC}"
git push origin "v${VERSION}"

echo -e "${GREEN}✅ Release v${VERSION} created successfully!${NC}"
echo -e "${BLUE}🔗 GitHub Actions will now:${NC}"
echo -e "   • Run tests and security scans"
echo -e "   • Build and push multi-architecture Docker images"
echo -e "   • Create a GitHub release with release notes"
echo -e "   • Update the latest tag"
echo -e ""
echo -e "${BLUE}📋 You can monitor the progress at:${NC}"
echo -e "   https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/actions"
echo -e ""
echo -e "${BLUE}📦 Once complete, the Docker images will be available at:${NC}"
echo -e "   ghcr.io/andyg-0/hdhomerunepg-to-xmltv:${VERSION}"
echo -e "   ghcr.io/andyg-0/hdhomerunepg-to-xmltv:latest"