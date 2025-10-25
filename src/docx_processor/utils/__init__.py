"""
Utility modules for DOCX processing.
"""

from .logger import get_logger, setup_logging
from .text_utils import (
    clean_string,
    remove_section_headers,
    normalize_whitespace,
    extract_section_number,
    truncate_text,
    sanitize_filename,
    remove_punctuation
)

__all__ = [
    "get_logger",
    "setup_logging",
    "clean_string",
    "remove_section_headers",
    "normalize_whitespace",
    "extract_section_number",
    "truncate_text",
    "sanitize_filename",
    "remove_punctuation",
]