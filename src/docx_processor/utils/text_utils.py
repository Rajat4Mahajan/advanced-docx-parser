"""
Text processing utilities for DOCX content.
"""

import re
from typing import Optional


def clean_string(text: str) -> str:
    """
    Clean a string by removing excessive whitespace and normalizing characters.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove non-breaking spaces
    text = text.replace('\xa0', ' ')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def remove_section_headers(text: str) -> str:
    """
    Remove section numbering from headers (e.g., "1.2.3 Title" -> "Title").
    
    Args:
        text: Header text that may contain numbering
        
    Returns:
        Text with section numbering removed
    """
    if not text:
        return ""
    
    # Pattern to match section numbering like "1.", "1.2.", "1.2.3.", etc.
    pattern = r'^\s*\d+(\.\d+)*\.?\s*'
    
    # Remove the numbering
    cleaned = re.sub(pattern, '', text).strip()
    
    return cleaned if cleaned else text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text by converting all whitespace to single spaces.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    return ' '.join(text.split())


def extract_section_number(text: str) -> Optional[str]:
    """
    Extract section number from text like "1.2.3 Title".
    
    Args:
        text: Text that may contain section numbering
        
    Returns:
        Section number if found, None otherwise
    """
    if not text:
        return None
    
    pattern = r'^\s*(\d+(?:\.\d+)*)'
    match = re.match(pattern, text.strip())
    
    return match.group(1) if match else None


def truncate_text(text: str, max_length: int = 5000, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove excessive whitespace and dots
    filename = re.sub(r'[\s.]+', '_', filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    return filename or 'unnamed'


def remove_punctuation(text: str) -> str:
    """
    Remove punctuation from text, keeping only alphanumeric and spaces.
    
    Args:
        text: Input text
        
    Returns:
        Text with punctuation removed
    """
    if not text:
        return ""
    
    # Keep alphanumeric, spaces, and common separators
    cleaned = re.sub(r'[^\w\s\-_]', '', text)
    
    return normalize_whitespace(cleaned)