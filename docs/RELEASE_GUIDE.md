# Release Management Guide

This document explains how to create and manage releases for the HDHomeRun EPG to XMLTV project.

## Overview

The project uses automated GitHub Actions workflows to create releases, build Docker images, and publish them to GitHub Container Registry. The system supports semantic versioning and automatically generates release notes.

## Release Types

### Automated Release Drafts
- **Trigger**: Pull requests merged to `main` branch
- **Action**: Automatically updates draft release with categorized changes
- **Workflow**: `.github/workflows/release-drafter.yml`

### Official Releases
- **Trigger**: Git tags pushed to repository (format: `v1.2.3`)
- **Action**: Creates GitHub release and publishes Docker images
- **Workflow**: `.github/workflows/ci-cd.yml` (release job)

## Creating a Release

### Method 1: Using the Release Script (Recommended)

```bash
# Create a new release
./scripts/create_release.sh 1.2.3

# Or let the script prompt you
./scripts/create_release.sh
```

The script will:
1. Validate the version format
2. Check you're on the main branch
3. Ensure no uncommitted changes
4. Run tests (if uv is available)
5. Create and push the git tag
6. Trigger the automated release workflow

### Method 2: Manual Git Tagging

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create and push a tag
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

### Method 3: GitHub Web Interface

1. Go to the [Releases page](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/releases)
2. Click "Draft a new release"
3. Choose or create a tag (format: `v1.2.3`)
4. GitHub will auto-generate release notes
5. Review and publish

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (`1.0.0` → `2.0.0`): Breaking changes
- **MINOR** (`1.0.0` → `1.1.0`): New features, backward compatible
- **PATCH** (`1.0.0` → `1.0.1`): Bug fixes, backward compatible

### Pre-release Versions
For beta/alpha releases, append a pre-release identifier:
- `1.2.3-alpha.1`
- `1.2.3-beta.2`
- `1.2.3-rc.1`

## Docker Image Tagging

When a release is created, the following Docker images are built and pushed:

### Release Tags
```bash
# Specific version
ghcr.io/andyg-0/hdhomerunepg-to-xmltv:1.2.3

# Major version
ghcr.io/andyg-0/hdhomerunepg-to-xmltv:1

# Major.minor version
ghcr.io/andyg-0/hdhomerunepg-to-xmltv:1.2

# Latest (always points to the latest stable release)
ghcr.io/andyg-0/hdhomerunepg-to-xmltv:latest
```

### Development Tags
For non-release builds:
```bash
# Branch-based tags
ghcr.io/andyg-0/hdhomerunepg-to-xmltv:main
ghcr.io/andyg-0/hdhomerunepg-to-xmltv:main-20231205
ghcr.io/andyg-0/hdhomerunepg-to-xmltv:main-abc1234
```

## Pull Request Labels

The release system uses labels to categorize changes. Add appropriate labels to PRs:

### Release Impact
- `major`: Breaking changes (bumps major version)
- `minor` or `feature`: New features (bumps minor version) 
- `patch`, `fix`, or `bug`: Bug fixes (bumps patch version)

### Category Labels
- `🚀 feature`, `enhancement`: New features
- `🐛 fix`, `bug`, `bugfix`, `hotfix`: Bug fixes
- `📚 docs`, `documentation`: Documentation changes
- `🔧 chore`, `maintenance`: Maintenance work
- `🚢 docker`, `ci`, `infrastructure`: Container/CI changes
- `🔒 security`, `vulnerability`: Security fixes
- `🎯 performance`, `perf`: Performance improvements
- `🧪 test`, `testing`: Test additions/changes
- `💥 breaking`, `breaking-change`: Breaking changes

### Special Labels
- `ignore-for-release`: Exclude from release notes
- `dependencies`: Dependency updates

## Automated Features

### Release Notes Generation
- Automatically categorizes changes by label
- Includes Docker installation commands
- Links to full changelog
- Lists contributors

### Container Images
- Multi-architecture builds (amd64, arm64)
- Comprehensive metadata labels
- Health check validation
- Platform-specific manifests

### Quality Assurance
- Automated testing before release
- Security scanning
- Docker image testing
- Linting and type checking

## Monitoring Releases

### GitHub Actions
Monitor release progress at:
- [Actions Tab](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/actions)
- [Releases Page](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/releases)

### Container Registry
View published images at:
- [GHCR Package Page](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/pkgs/container/hdhomerunepg-to-xmltv)

### Release Status
Each release includes:
- ✅ Automated testing passed
- ✅ Security scanning completed  
- ✅ Multi-architecture images built
- ✅ Container functionality verified
- ✅ Images published to GHCR

## Troubleshooting

### Release Failed
1. Check the [Actions page](https://github.com/AndyG-0/HDHomeRunEPG-to-XmlTv/actions) for errors
2. Common issues:
   - Test failures
   - Docker build errors
   - Registry authentication problems
   - Duplicate tag creation

### Fix and Retry
```bash
# Delete the failed tag locally and remotely
git tag -d v1.2.3
git push origin :refs/tags/v1.2.3

# Fix the issue, commit changes, then retry
./scripts/create_release.sh 1.2.3
```

### Manual Release Creation
If automation fails, create release manually:
1. Ensure Docker images are built and tagged
2. Go to GitHub Releases page  
3. Create release from existing tag
4. Copy generated release notes from draft release

## Configuration Files

- `.github/release.yml`: GitHub's native release notes config
- `.github/release-drafter.yml`: Release Drafter configuration
- `.github/workflows/release-drafter.yml`: Draft release workflow
- `.github/workflows/ci-cd.yml`: Main CI/CD with release job
- `scripts/create_release.sh`: Release creation helper script

## Best Practices

1. **Always test before releasing**: Run tests locally before creating a release
2. **Use descriptive commit messages**: They become part of the release notes
3. **Label PRs appropriately**: Ensures proper categorization
4. **Review draft releases**: Check auto-generated notes before publishing
5. **Monitor release progress**: Watch Actions to ensure successful completion
6. **Test released images**: Verify containers work as expected

## Example Workflow

```bash
# 1. Develop feature on feature branch
git checkout -b feature/new-endpoint
# ... make changes ...
git commit -m "feat: add health check endpoint"

# 2. Create PR with appropriate labels
# Add labels: feature, enhancement

# 3. Merge PR to main
# Release Drafter automatically updates draft release

# 4. When ready to release, create tag
./scripts/create_release.sh 1.3.0

# 5. Monitor GitHub Actions
# 6. Verify Docker images are available
docker pull ghcr.io/andyg-0/hdhomerunepg-to-xmltv:1.3.0
```