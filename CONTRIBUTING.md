# Contributing to DOCX Processor

We welcome contributions to the DOCX Processor project! This document provides guidelines for contributing.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/docx-processor.git
   cd docx-processor
   ```

2. **Install dependencies with uv**
   ```bash
   # Install all dependencies including dev tools
   uv sync --extra dev --extra enhanced --extra professional
   
   # Or install only what you need
   uv sync --extra dev  # Basic development setup
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Run tests to verify setup**
   ```bash
   pytest
   ```

## Development Workflow

### Code Style
We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all checks:
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Testing

We use pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=docx_processor --cov-report=html

# Run specific test file
pytest tests/test_processor.py

# Run tests with specific marker
pytest -m "not slow"
```

### Adding New Features

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first** (TDD approach preferred)
   - Add tests in the `tests/` directory
   - Follow existing test patterns
   - Ensure good test coverage

3. **Implement the feature**
   - Follow the existing code structure
   - Add proper type hints
   - Include docstrings for public methods

4. **Update documentation**
   - Update README.md if needed
   - Add docstrings to new functions/classes
   - Update CHANGELOG.md

5. **Run the full test suite**
   ```bash
   pytest --cov=docx_processor
   ```

6. **Submit a pull request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all CI checks pass

## Project Structure

```
docx-processor/
├── src/docx_processor/          # Main package
│   ├── core/                    # Basic processing (pure python-docx)
│   ├── enhanced/                # Enhanced features (LibreOffice + PyMuPDF)
│   ├── utils/                   # Utility modules
│   ├── models.py                # Data models
│   ├── exceptions.py            # Custom exceptions
│   ├── processor.py             # Main processor class
│   └── cli.py                   # Command-line interface
├── tests/                       # Test suite
├── docs/                        # Documentation
└── examples/                    # Usage examples
```

## Adding New Processing Modes

The project is designed to support different processing tiers:

1. **Basic Mode** (`core/`): Pure python-docx processing with headers/footers and endnotes
2. **Enhanced Mode** (`enhanced/`): Adds LibreOffice integration, PyMuPDF, and HTML export

To add features to a specific mode:

1. Add functionality to the appropriate processor class
2. Update the configuration models if new options are needed
3. Add corresponding CLI options
4. Write comprehensive tests
5. Update documentation

## Testing Guidelines

### Test Categories
- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Performance tests**: Test with large documents (marked as `slow`)

### Test Data
- Use small, synthetic DOCX files for most tests
- Put test files in `tests/fixtures/`
- Don't commit large binary files to the repository

### Mocking External Dependencies
- Mock LibreOffice calls in enhanced mode tests
- Mock PyMuPDF operations for page processing tests  
- Use `pytest-mock` for mocking external dependencies

## Documentation

### Docstrings
Use Google-style docstrings:

```python
def process_document(file_path: Path, config: ProcessingConfig) -> ProcessingResult:
    """
    Process a DOCX document.
    
    Args:
        file_path: Path to the DOCX file
        config: Processing configuration
        
    Returns:
        Processing result with extracted content
        
    Raises:
        ProcessingError: If document processing fails
    """
```

### Type Hints
- Use type hints for all public methods
- Import types from `typing` module
- Use `Optional[T]` for nullable values

## Performance Considerations

- Profile code with large documents
- Avoid loading entire documents into memory when possible
- Use generators for processing large content streams
- Consider memory usage in image processing

## Dependency Management

### Adding Dependencies
1. Add to appropriate section in `pyproject.toml`
2. Consider which processing mode needs the dependency
3. Update dependency validation in processors
4. Update installation instructions in README

### Optional Dependencies
- Keep basic mode dependency-free except for core libraries
- Enhanced/professional features should gracefully handle missing dependencies
- Provide clear error messages when dependencies are missing

## Release Process

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Update CHANGELOG.md** with release notes
3. **Create release branch** `release/v0.x.x`
4. **Run full test suite** including slow tests
5. **Build and test package** locally
6. **Create GitHub release** with changelog
7. **Publish to PyPI** (maintainers only)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please be respectful and inclusive in all interactions.

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions about usage or development
- Check existing issues before creating new ones

Thank you for contributing to DOCX Processor!