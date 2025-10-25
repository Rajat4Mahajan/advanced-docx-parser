# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced mode with LibreOffice integration
- PDF conversion capabilities (requires LibreOffice)
- Page screenshot generation using PyMuPDF
- HTML export functionality
- Headers and footers processing
- Endnotes extraction and processing
- Graceful fallback when LibreOffice unavailable
- Development installation instructions

### Changed
- Simplified architecture from three-tier to two-tier (Basic/Enhanced)
- Updated documentation for development installation
- Enhanced CLI with new feature flags

### Removed
- Professional mode and Aspose dependencies
- Hardcoded dependency references

### Security
- Removed potential license key exposure paths
- Clean dependency management

## [0.1.0] - 2025-10-25

### Added
- Initial release
- Basic DOCX document processing capabilities
- Content extraction with section hierarchy preservation
- Image extraction and processing
- Table extraction with HTML conversion
- Table of contents generation
- Command-line interface with rich output
- Comprehensive documentation and examples