"""
Data models and configuration classes for DOCX Processor.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict, validator


class ProcessingMode(str, Enum):
    """Available processing modes."""
    BASIC = "basic"
    ENHANCED = "enhanced"


class ProcessingConfig(BaseModel):
    """Configuration for document processing."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
    
    # Processing mode
    mode: ProcessingMode = ProcessingMode.BASIC
    
    # Output configuration
    output_dir: Optional[Path] = None
    save_images: bool = True
    save_tables: bool = True
    save_content: bool = True
    
    # Content processing options
    preserve_hierarchy: bool = True
    extract_toc: bool = True
    include_headers_footers: bool = True
    max_image_size_mb: int = Field(default=10, ge=1, le=100)
    
    # Enhanced mode options (requires LibreOffice)
    generate_page_screenshots: bool = False
    extract_page_numbers: bool = False
    convert_to_pdf: bool = False
    generate_html: bool = False
    
    # Performance options
    max_pages_to_process: Optional[int] = Field(default=None, ge=1)
    enable_parallel_processing: bool = False
    
    @validator('output_dir', pre=True)
    def validate_output_dir(cls, v):
        """Ensure output_dir is a Path object."""
        if v is not None:
            return Path(v)
        return v
    
    @validator('mode')
    def validate_mode_dependencies(cls, v, values):
        """Validate that required dependencies are available for selected mode."""
        # Note: Actual dependency checking will be done at runtime
        return v


class ImageInfo(BaseModel):
    """Information about an extracted image."""
    
    filename: str
    size_bytes: int
    width: Optional[int] = None
    height: Optional[int] = None
    format: str
    section: Optional[str] = None
    page_number: Optional[int] = None


class TableInfo(BaseModel):
    """Information about an extracted table."""
    
    filename: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    rows: int
    columns: int


class SectionInfo(BaseModel):
    """Information about a document section."""
    
    title: str
    content: str
    level: int
    parent: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    images: List[str] = Field(default_factory=list)
    tables: List[str] = Field(default_factory=list)


class TOCEntry(BaseModel):
    """Table of contents entry."""
    
    section_id: str
    section_name: str
    level: int
    page_number: Optional[int] = None
    children: List['TOCEntry'] = Field(default_factory=list)


# Enable forward references
TOCEntry.model_rebuild()


class ProcessingResult(BaseModel):
    """Result of document processing."""
    
    model_config = ConfigDict(
        extra="allow",  # Allow extra fields for extensibility
        arbitrary_types_allowed=True,
    )
    
    # Basic processing results
    content: Dict[str, str] = Field(default_factory=dict)
    content_hierarchy: Dict[str, SectionInfo] = Field(default_factory=dict)
    
    # Content without child aggregation
    content_without_children: Optional[Dict[str, str]] = None
    
    # Images and tables
    images: Dict[str, ImageInfo] = Field(default_factory=dict)
    tables: Dict[str, TableInfo] = Field(default_factory=dict)
    
    # Document structure
    toc: Optional[List[TOCEntry]] = None
    
    # Enhanced processing results  
    page_screenshots: Optional[Dict[str, str]] = None
    page_numbers: Optional[Dict[str, Dict[str, int]]] = None
    html_content: Optional[str] = None
    html_content_hierarchy: Optional[Dict[str, str]] = None
    
    # Headers and footers
    headers_footers: Optional[Dict[str, Any]] = None
    
    # Endnotes and references
    endnotes: Optional[Dict[str, str]] = None
    
    # Processing metadata
    processing_mode: ProcessingMode
    processing_time_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    total_pages: Optional[int] = None
    
    # Error information
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    # Output paths
    output_paths: Dict[str, Path] = Field(default_factory=dict)


class ProcessingStats(BaseModel):
    """Statistics about the processing operation."""
    
    total_sections: int = 0
    total_images: int = 0
    total_tables: int = 0
    total_pages: int = 0
    processing_time_seconds: float = 0.0
    memory_used_mb: Optional[float] = None