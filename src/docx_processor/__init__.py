"""
DOCX Processor - Advanced document processing for DOCX files

A powerful Python library for extracting structured content, images, tables,
and metadata from DOCX documents with support for multiple processing modes.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .processor import DOCXProcessor
from .models import ProcessingResult, ProcessingConfig, ProcessingMode
from .exceptions import DOCXProcessorError, ProcessingError, ConfigurationError

__all__ = [
    "DOCXProcessor",
    "ProcessingResult", 
    "ProcessingConfig",
    "ProcessingMode",
    "DOCXProcessorError",
    "ProcessingError", 
    "ConfigurationError",
]