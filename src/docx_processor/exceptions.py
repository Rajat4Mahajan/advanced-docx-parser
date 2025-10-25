"""
Custom exceptions for the DOCX Processor library.
"""


class DOCXProcessorError(Exception):
    """Base exception for all DOCX Processor errors."""
    pass


class ProcessingError(DOCXProcessorError):
    """Raised when document processing fails."""
    pass


class ConfigurationError(DOCXProcessorError):
    """Raised when configuration is invalid."""
    pass


class DependencyError(DOCXProcessorError):
    """Raised when required dependencies are missing."""
    pass


class FileError(DOCXProcessorError):
    """Raised when file operations fail."""
    pass