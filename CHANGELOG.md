# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2024

### Added
- UV package manager support with pyproject.toml
- Auto-generation of M3U playlists from XMLTV files
- Docker support with automated scheduling
- Built-in HTTP server for EPG access
- Comprehensive test suite
- Channel ID matching validation tools

### Changed
- **BREAKING**: Channel IDs now use format `hdhomerun.{channel}` for better M3U compatibility
- Improved error handling for HTTP 400 responses from HDHomeRun API
- Default output location changed to `./output/` directory
- Reorganized project structure with proper directories for tests, docs, examples

### Fixed
- HTTP 400 error handling when API limits are reached
- Directory creation for nested output paths
- **CRITICAL**: XMLTV format compliance - Added DOCTYPE declaration for Jellyfin and UHF compatibility
- **CRITICAL**: Channel IDs now properly use `hdhomerun.{GuideNumber}` format
- M3U channel ID matching for IPTV applications
- "New" episode bug where all episodes were marked as new (#5)
- Status handling bug (#14)

### Documentation
- Complete rewrite of README with modern setup instructions
- Added comprehensive M3U integration guide
- UHF app setup documentation
- Docker usage guide

### Technical Improvements
- Migrated from pip/requirements.txt to UV package manager
- Added proper Python packaging configuration
- Organized utility scripts into scripts/ directory
- Added examples/ directory for reference files
- Implemented proper test structure with unittest

## [1.x] - Previous Versions

Previous versions used basic numeric channel IDs and pip-based dependency management. See repository history for detailed changes.

## Acknowledgments

- [@supitsmike] - Fixed "New" episode bug (#5)
- [@AcSlayter] - Docker support (#13)
- [@Sujeom] - Status handling fix (#14)
- All contributors who helped improve XMLTV DTD compliance and timezone handling