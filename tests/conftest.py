"""
Test configuration and fixtures.
"""

import pytest
from pathlib import Path
from docx_processor import ProcessingConfig, ProcessingMode


@pytest.fixture
def sample_config():
    """Basic processing configuration for testing."""
    return ProcessingConfig(
        mode=ProcessingMode.BASIC,
        save_images=True,
        save_tables=True,
        save_content=True
    )


@pytest.fixture
def output_dir(tmp_path):
    """Temporary output directory for tests."""
    return tmp_path / "output"


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "enhanced: marks tests requiring enhanced mode dependencies"
    )
    config.addinivalue_line(
        "markers", "professional: marks tests requiring professional mode dependencies"
    )