"""
Main DOCX Processor class - the primary entry point for document processing.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO

from .models import ProcessingConfig, ProcessingResult, ProcessingMode, ProcessingStats
from .exceptions import DOCXProcessorError, ProcessingError, ConfigurationError, DependencyError
from .core import BasicProcessor
from .utils.logger import get_logger


class DOCXProcessor:
    """
    Main processor class for advanced DOCX document processing.
    
    Supports multiple processing modes:
    - Basic: Pure python-docx processing
    - Enhanced: Adds LibreOffice integration for PDF conversion and page screenshots
    - Professional: Adds Aspose.Words for advanced formatting preservation
    
    Example:
        >>> processor = DOCXProcessor(mode="enhanced")
        >>> result = processor.process_file("document.docx", output_dir="./output")
        >>> print(result.content)
    """
    
    def __init__(
        self, 
        mode: Union[ProcessingMode, str] = ProcessingMode.BASIC,
        config: Optional[ProcessingConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the DOCX processor.
        
        Args:
            mode: Processing mode (basic, enhanced, or professional)
            config: Optional processing configuration
            logger: Optional custom logger
            
        Raises:
            DependencyError: If required dependencies for the mode are not available
            ConfigurationError: If configuration is invalid
        """
        self.logger = logger or get_logger(__name__)
        
        # Convert string mode to enum
        if isinstance(mode, str):
            try:
                mode = ProcessingMode(mode.lower())
            except ValueError:
                raise ConfigurationError(f"Invalid processing mode: {mode}")
        
        self.mode = mode
        self.config = config or ProcessingConfig(mode=mode)
        
        # Validate dependencies for the selected mode
        self._validate_dependencies()
        
        # Initialize processors based on mode
        self._init_processors()
        
        self.logger.info(f"Initialized DOCXProcessor in {mode.value} mode")
    
    def _validate_dependencies(self) -> None:
        """Validate that required dependencies are available for the selected mode."""
        missing_deps = []
        
        if self.mode in [ProcessingMode.ENHANCED, ProcessingMode.PROFESSIONAL]:
            try:
                import fitz  # PyMuPDF
            except ImportError:
                missing_deps.append("PyMuPDF (for enhanced/professional modes)")
        
        if self.mode == ProcessingMode.PROFESSIONAL:
            try:
                import aspose.words
            except ImportError:
                missing_deps.append("aspose-words (for professional mode)")
        
        if missing_deps:
            raise DependencyError(
                f"Missing dependencies for {self.mode.value} mode: {', '.join(missing_deps)}. "
                f"Install with: pip install 'docx-processor[{self.mode.value}]'"
            )
    
    def _init_processors(self) -> None:
        """Initialize the appropriate processors based on mode."""
        # Always initialize basic processor
        self.basic_processor = BasicProcessor(config=self.config, logger=self.logger)
        
        # Initialize enhanced processor if needed
        if self.mode in [ProcessingMode.ENHANCED, ProcessingMode.PROFESSIONAL]:
            from .enhanced import EnhancedProcessor
            self.enhanced_processor = EnhancedProcessor(config=self.config, logger=self.logger)
        else:
            self.enhanced_processor = None
        
        # Initialize professional processor if needed
        if self.mode == ProcessingMode.PROFESSIONAL:
            from .professional import ProfessionalProcessor
            self.professional_processor = ProfessionalProcessor(config=self.config, logger=self.logger)
        else:
            self.professional_processor = None
    
    def process_file(
        self,
        file_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> ProcessingResult:
        """
        Process a DOCX file and extract content, images, tables, and metadata.
        
        Args:
            file_path: Path to the DOCX file to process
            output_dir: Optional output directory for extracted files
            **kwargs: Additional processing options that override config
            
        Returns:
            ProcessingResult containing all extracted content and metadata
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            ProcessingError: If processing fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if output_dir is not None:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Processing file: {file_path}")
        start_time = time.time()
        
        try:
            # Update config with any kwargs
            runtime_config = self.config.model_copy()
            if output_dir is not None:
                runtime_config.output_dir = output_dir
            for key, value in kwargs.items():
                if hasattr(runtime_config, key):
                    setattr(runtime_config, key, value)
            
            # Process the document
            result = self._process_document(file_path, runtime_config)
            
            # Add processing metadata
            result.processing_time_seconds = time.time() - start_time
            result.file_size_bytes = file_path.stat().st_size
            
            self.logger.info(f"Processing completed in {result.processing_time_seconds:.2f} seconds")
            return result
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            if isinstance(e, DOCXProcessorError):
                raise
            else:
                raise ProcessingError(f"Unexpected error during processing: {e}") from e
    
    def process_bytes(
        self,
        docx_bytes: bytes,
        filename: Optional[str] = None,
        output_dir: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> ProcessingResult:
        """
        Process DOCX content from bytes.
        
        Args:
            docx_bytes: DOCX file content as bytes
            filename: Optional filename for reference
            output_dir: Optional output directory for extracted files
            **kwargs: Additional processing options
            
        Returns:
            ProcessingResult containing all extracted content and metadata
        """
        # Create a temporary file and process it
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            tmp_file.write(docx_bytes)
            tmp_path = Path(tmp_file.name)
        
        try:
            result = self.process_file(tmp_path, output_dir, **kwargs)
            return result
        finally:
            # Clean up temporary file
            if tmp_path.exists():
                tmp_path.unlink()
    
    def _process_document(self, file_path: Path, config: ProcessingConfig) -> ProcessingResult:
        """
        Internal method to process a document through the appropriate processors.
        
        Args:
            file_path: Path to the DOCX file
            config: Runtime configuration
            
        Returns:
            ProcessingResult with all extracted content
        """
        # Start with basic processing
        self.logger.debug("Starting basic processing")
        result = self.basic_processor.process(file_path, config)
        
        # Add enhanced processing if available
        if self.enhanced_processor is not None:
            self.logger.debug("Starting enhanced processing")
            result = self.enhanced_processor.process(file_path, config, result)
        
        # Add professional processing if available  
        if self.professional_processor is not None:
            self.logger.debug("Starting professional processing")
            result = self.professional_processor.process(file_path, config, result)
        
        return result
    
    def get_processing_stats(self) -> ProcessingStats:
        """
        Get statistics about the last processing operation.
        
        Returns:
            ProcessingStats with operation metrics
        """
        # Implementation would track stats during processing
        return ProcessingStats()
    
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that a file is a valid DOCX document.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file is a valid DOCX document
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False
        
        if file_path.suffix.lower() not in ['.docx']:
            return False
        
        try:
            # Try to open with python-docx
            from docx import Document
            Document(file_path)
            return True
        except Exception:
            return False