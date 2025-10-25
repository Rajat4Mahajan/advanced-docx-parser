# DOCX Processor

[![PyPI version](https://badge.fury.io/py/docx-processor.svg)](https://badge.fury.io/py/docx-processor)
[![Python Support](https://img.shields.io/pypi/pyversions/docx-processor.svg)](https://pypi.org/project/docx-processor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful and flexible Python library for advanced DOCX document processing with hierarchical content extraction, image handling, and multiple output formats.

## 🚀 Features

### Basic Mode (Default)
- **Hierarchical Content Extraction**: Automatically detects and preserves document structure
- **Smart Table Processing**: Converts DOCX tables to HTML with styling preservation  
- **Image Extraction**: Supports embedded images, VML graphics, and flowcharts
- **Multiple Image Formats**: Handles JPEG, PNG, EMF with automatic format conversion
- **Content Hierarchy**: Maintains parent-child relationships between sections
- **Table of Contents Generation**: Automatically builds document TOC from structure
- **Headers & Footers**: Extract unique headers and footers from document
- **Endnotes Processing**: Extract and process document endnotes

### Enhanced Mode (with LibreOffice integration)
- **All Basic Mode Features**: Everything from basic mode plus:
- **PDF Conversion**: Convert DOCX to PDF using LibreOffice
- **Page Screenshot Generation**: Convert document pages to PNG images
- **Page Number Mapping**: Map content sections to specific page numbers  
- **HTML Export**: Generate clean HTML representation of document content
- **Graceful Fallbacks**: Works without LibreOffice (disables PDF-based features)

## 📦 Installation

> **Note**: This package is currently in development and not yet published to PyPI.

### Development Installation

#### From Source (Current Method)
```bash
# Clone the repository
git clone https://github.com/yourusername/docx-processor.git
cd docx-processor

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

#### With Enhanced Features
```bash
# Install with enhanced dependencies (PyMuPDF for PDF processing)
uv pip install -e .[enhanced]

# Don't forget to install LibreOffice for PDF conversion features:
# Ubuntu/Debian: sudo apt-get install libreoffice
# macOS: brew install --cask libreoffice  
# Windows: Download from https://www.libreoffice.org/
```

#### All Features
```bash
# Install everything (all optional dependencies)
uv pip install -e .[all]
```

### Future PyPI Installation (Coming Soon)
Once published to PyPI, you'll be able to install with:
```bash
# Will be available after PyPI publication
pip install docx-processor
pip install "docx-processor[enhanced]"
```

### Quick Development Setup
```bash
# Clone and setup for development
git clone https://github.com/bms-corp/docgen-repo.git
cd docgen-repo/docx-processor

# Install dependencies
uv pip install -e .[enhanced]

# Test the installation
uv run docx-processor info

# Process a document (if you have a sample DOCX file)
uv run docx-processor process your-document.docx --output ./output --verbose
```

## 🔧 Quick Start

### Command Line Interface

#### Development Usage (Current)
```bash
# Run from source directory using uv
cd docx-processor
uv run docx-processor process document.docx --output ./output

# Enhanced processing with HTML generation
uv run docx-processor process document.docx --output ./output --mode enhanced --html

# Enhanced processing with PDF conversion and page screenshots  
uv run docx-processor process document.docx --output ./output --mode enhanced --pdf --screenshots

# Check dependency status
uv run docx-processor info
```

#### Future Usage (After PyPI Publication)
```bash
# Will work after pip/uv installation
docx-processor process document.docx --output ./output
docx-processor process document.docx --output ./output --mode enhanced --html
docx-processor info
```

### Python API

```python
from docx_processor import DOCXProcessor

# Basic processing
processor = DOCXProcessor()
result = processor.process_file("document.docx")

# Access extracted content
print(result.content)  # Hierarchical content dictionary
print(result.images)   # Extracted images
print(result.tables)   # HTML tables
print(result.toc)      # Table of contents
print(result.headers_footers)  # Headers and footers
print(result.endnotes)  # Document endnotes

# Enhanced processing with LibreOffice features
from docx_processor import ProcessingConfig

config = ProcessingConfig(
    mode="enhanced",
    generate_html=True,
    convert_to_pdf=True,
    generate_page_screenshots=True
)

processor = DOCXProcessor(mode="enhanced", config=config)
result = processor.process_file("document.docx", output_dir="./output")

# Access enhanced features
print(result.html_content)  # HTML representation
print(result.page_screenshots)  # Page screenshot paths
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- LibreOffice (optional - for PDF conversion and page screenshots)

### Dependencies
- **Basic Mode**: `python-docx`, `Pillow`, `BeautifulSoup4`, `fuzzywuzzy`, `pydantic`
- **Enhanced Mode**: All basic dependencies plus `PyMuPDF`, LibreOffice (system dependency)

## 🏗️ Architecture

The library is designed with a clean two-tier architecture:

```
┌─────────────────────────────────────┐
│           Enhanced Mode             │
│   (LibreOffice + PyMuPDF Features) │  
├─────────────────────────────────────┤
│            Basic Mode               │
│      (Pure Python Processing)      │
└─────────────────────────────────────┘
```

- **Basic Mode**: Self-contained with pure Python dependencies
- **Enhanced Mode**: Builds on Basic Mode with optional LibreOffice integration
- **Graceful Degradation**: Enhanced mode falls back gracefully when LibreOffice unavailable

## 📖 Documentation

- **[User Guide](docs/user-guide.md)**: Complete usage examples and tutorials
- **[API Reference](docs/api-reference.md)**: Detailed API documentation  
- **[Configuration](docs/configuration.md)**: Configuration options and settings
- **[Contributing](CONTRIBUTING.md)**: How to contribute to the project

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/docx-processor.git
cd docx-processor

# Install with development dependencies using uv
uv sync --extra dev

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run with coverage
pytest --cov=docx_processor --cov-report=html
```

## � Publishing to PyPI

When ready to publish this package:

```bash
# Build the package
uv build

# Upload to PyPI (requires PyPI account and API token)
uv publish

# Or for testing on Test PyPI first
uv publish --repository testpypi
```

Make sure to update the repository URLs in `pyproject.toml` before publishing.

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This library builds upon the excellent work of:
- [`python-docx`](https://github.com/python-openxml/python-docx) for core DOCX processing
- [`PyMuPDF`](https://pymupdf.readthedocs.io/) for PDF processing and page screenshots
- [`LibreOffice`](https://www.libreoffice.org/) for document conversion capabilities

## 📊 Project Status

This project is actively maintained and used in production environments. We follow [semantic versioning](https://semver.org/) and maintain a [changelog](CHANGELOG.md).

## 🔗 Related Projects

- [python-docx](https://github.com/python-openxml/python-docx) - Core DOCX manipulation
- [pandoc](https://pandoc.org/) - Universal document converter
- [mammoth](https://github.com/mwilliamson/python-mammoth) - DOCX to HTML converter