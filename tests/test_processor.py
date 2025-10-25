"""
Tests for the main DOCXProcessor class.
"""

import pytest
from pathlib import Path
from docx_processor import DOCXProcessor, ProcessingMode, ProcessingConfig
from docx_processor.exceptions import DOCXProcessorError, ConfigurationError


class TestDOCXProcessor:
    """Tests for DOCXProcessor class."""
    
    def test_init_basic_mode(self):
        """Test processor initialization in basic mode."""
        processor = DOCXProcessor(mode=ProcessingMode.BASIC)
        assert processor.mode == ProcessingMode.BASIC
        assert processor.basic_processor is not None
        assert processor.enhanced_processor is None
        assert processor.professional_processor is None
    
    def test_init_string_mode(self):
        """Test processor initialization with string mode."""
        processor = DOCXProcessor(mode="basic")
        assert processor.mode == ProcessingMode.BASIC
    
    def test_init_invalid_mode(self):
        """Test processor initialization with invalid mode."""
        with pytest.raises(ConfigurationError):
            DOCXProcessor(mode="invalid")
    
    def test_validate_file_nonexistent(self):
        """Test file validation with nonexistent file."""
        processor = DOCXProcessor()
        assert not processor.validate_file("nonexistent.docx")
    
    def test_validate_file_wrong_extension(self):
        """Test file validation with wrong file extension."""
        processor = DOCXProcessor()
        assert not processor.validate_file("document.txt")
    
    def test_process_file_nonexistent(self):
        """Test processing nonexistent file raises FileNotFoundError."""
        processor = DOCXProcessor()
        with pytest.raises(FileNotFoundError):
            processor.process_file("nonexistent.docx")
    
    # TODO: Add more tests with actual DOCX files
    # This would require creating test fixtures


class TestProcessingConfig:
    """Tests for ProcessingConfig model."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ProcessingConfig()
        assert config.mode == ProcessingMode.BASIC
        assert config.save_images is True
        assert config.save_tables is True
        assert config.save_content is True
        assert config.preserve_hierarchy is True
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = ProcessingConfig(
            mode=ProcessingMode.ENHANCED,
            max_image_size_mb=50
        )
        assert config.mode == ProcessingMode.ENHANCED
        assert config.max_image_size_mb == 50
    
    def test_output_dir_path_conversion(self):
        """Test output_dir is converted to Path object."""
        config = ProcessingConfig(output_dir="./output")
        assert isinstance(config.output_dir, Path)
        assert config.output_dir == Path("./output")


# Add more test classes as needed for other components