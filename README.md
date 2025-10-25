# DOCX Processor

[![PyPI version](https://badge.fury.io/py/docx-processor.svg)](https://badge.fury.io/py/docx-processor)
[![Python Support](https://img.shields.io/pypi/pyversions/docx-processor.svg)](https://pypi.org/project/docx-processor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful and flexible Python library for advanced DOCX document processing with hierarchical content extraction, image handling, and multiple output formats.

## 🚀 Features

### Core Features (Always Available)
- **Hierarchical Content Extraction**: Automatically detects and preserves document structure
- **Smart Table Processing**: Converts DOCX tables to HTML with styling preservation  
- **Image Extraction**: Supports embedded images, VML graphics, and flowcharts
- **Multiple Image Formats**: Handles JPEG, PNG, EMF with automatic format conversion
- **Content Hierarchy**: Maintains parent-child relationships between sections
- **Table of Contents Generation**: Automatically builds document TOC from structure

### Enhanced Features (with `enhanced` extras)
- **Page Screenshot Generation**: Convert document pages to images
- **Page Number Mapping**: Map content sections to specific page numbers
- **PDF Conversion**: Convert DOCX to PDF using LibreOffice

### Professional Features (with `professional` extras)
- **Advanced Formatting Preservation**: Superscript citations, colored text, complex styling
- **Heading Standardization**: Normalize custom heading styles to standard formats
- **HTML Output**: High-fidelity HTML conversion with embedded images
- **Enterprise-grade Processing**: Handle complex corporate document structures

## 📦 Installation

### Basic Installation
```bash
# Install with uv (recommended)
uv add docx-processor

# Or with pip
pip install docx-processor
```

### With Enhanced Features
```bash
# Includes LibreOffice integration for PDF conversion and page screenshots
uv add "docx-processor[enhanced]"
```

### With Professional Features  
```bash
# Includes Aspose.Words for advanced formatting (license required)
uv add "docx-processor[professional]"
```

### All Features
```bash
# Install everything (requires Aspose license for professional features)
uv add "docx-processor[all]"
```

## 🔧 Quick Start

### Command Line Interface

```bash
# Basic processing
docx-processor process document.docx --output ./output

# Enhanced processing with page screenshots
docx-processor process document.docx --output ./output --mode enhanced

# Professional processing with advanced formatting
docx-processor process document.docx --output ./output --mode professional
```

### Python API

```python
from docx_processor import DOCXProcessor

# Basic usage
processor = DOCXProcessor()
result = processor.process_file("document.docx")

# Access extracted content
print(result.content)  # Hierarchical content dictionary
print(result.images)   # Extracted images
print(result.tables)   # HTML tables
print(result.toc)      # Table of contents

# Enhanced processing
processor = DOCXProcessor(mode="enhanced")
result = processor.process_file("document.docx", 
                               output_dir="./output",
                               include_page_screenshots=True)

# Professional processing  
processor = DOCXProcessor(mode="professional")
result = processor.process_file("document.docx",
                               standardize_headings=True,
                               preserve_formatting=True,
                               generate_html=True)
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- LibreOffice (for enhanced features)
- Aspose.Words license (for professional features)

### Dependencies
- **Core**: `python-docx`, `Pillow`, `BeautifulSoup4`, `fuzzywuzzy`, `pydantic`
- **Enhanced**: `PyMuPDF` 
- **Professional**: `aspose-words`

## 🏗️ Architecture

The library is designed with a modular architecture supporting different processing tiers:

```
┌─────────────────────────────────────┐
│          Professional Mode          │  
│     (Aspose.Words Integration)      │
├─────────────────────────────────────┤
│           Enhanced Mode             │
│     (LibreOffice Integration)       │  
├─────────────────────────────────────┤
│            Basic Mode               │
│      (Pure Python Processing)      │
└─────────────────────────────────────┘
```

Each tier builds upon the previous one, ensuring you only need the dependencies for features you actually use.

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This library builds upon the excellent work of:
- [`python-docx`](https://github.com/python-openxml/python-docx) for core DOCX processing
- [`Aspose.Words`](https://products.aspose.com/words/python-net/) for advanced document features
- [`LibreOffice`](https://www.libreoffice.org/) for document conversion capabilities

## 📊 Project Status

This project is actively maintained and used in production environments. We follow [semantic versioning](https://semver.org/) and maintain a [changelog](CHANGELOG.md).

## 🔗 Related Projects

- [python-docx](https://github.com/python-openxml/python-docx) - Core DOCX manipulation
- [pandoc](https://pandoc.org/) - Universal document converter
- [mammoth](https://github.com/mwilliamson/python-mammoth) - DOCX to HTML converter