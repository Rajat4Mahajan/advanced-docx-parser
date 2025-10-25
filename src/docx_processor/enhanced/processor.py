"""
Enhanced DOCX processor with LibreOffice integration.
Adds PDF conversion, page screenshots, and page number mapping.
"""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, List

from ..models import ProcessingResult, ProcessingConfig
from ..exceptions import ProcessingError, DependencyError


class EnhancedProcessor:
    """
    Enhanced processor that adds LibreOffice-based features to basic processing.
    
    Features:
    - PDF conversion using LibreOffice
    - Page screenshot generation
    - Page number to section mapping
    """
    
    def __init__(self, config: ProcessingConfig, logger: logging.Logger):
        """
        Initialize the enhanced processor.
        
        Args:
            config: Processing configuration
            logger: Logger instance
            
        Raises:
            DependencyError: If required dependencies are not available
        """
        self.config = config
        self.logger = logger
        
        # Check dependencies - store availability for graceful fallback
        self.libreoffice_available = self._is_libreoffice_available()
        self.pymupdf_available = self._is_pymupdf_available()
        
        if not self.pymupdf_available:
            raise DependencyError("PyMuPDF is required for enhanced processing")
            
        if not self.libreoffice_available:
            self.logger.warning("LibreOffice not available - PDF conversion features will be disabled")
    
    def _is_pymupdf_available(self) -> bool:
        """Check if PyMuPDF is available."""
        try:
            import fitz  # PyMuPDF
            return True
        except ImportError:
            return False
    

    
    def _is_libreoffice_available(self) -> bool:
        """Check if LibreOffice is available on the system."""
        # Try common LibreOffice executables
        libreoffice_commands = [
            'libreoffice',  # Linux/macOS
            'soffice',      # Alternative Linux/macOS
            'libreoffice.exe',  # Windows
            'soffice.exe',      # Alternative Windows
        ]
        
        for cmd in libreoffice_commands:
            if shutil.which(cmd):
                self.logger.debug(f"Found LibreOffice at: {shutil.which(cmd)}")
                return True
        
        self.logger.warning("LibreOffice not found in PATH")
        return False
    
    def process(
        self, 
        file_path: Path, 
        config: ProcessingConfig, 
        result: ProcessingResult
    ) -> ProcessingResult:
        """
        Enhance the basic processing result with LibreOffice features.
        
        Args:
            file_path: Path to the DOCX file
            config: Processing configuration
            result: Basic processing result to enhance
            
        Returns:
            Enhanced processing result
        """
        self.logger.info("Starting enhanced processing")
        
        try:
            # Check if LibreOffice-dependent features are requested
            requires_libreoffice = (
                config.convert_to_pdf or 
                config.generate_page_screenshots or 
                config.extract_page_numbers
            )
            
            if requires_libreoffice and not self.libreoffice_available:
                warning = "LibreOffice not available - skipping PDF-based features"
                self.logger.warning(warning)
                result.warnings.append(warning)
                return result
            
            # Convert DOCX to PDF if requested and LibreOffice is available
            if requires_libreoffice:
                pdf_path = self._convert_docx_to_pdf(file_path, config.output_dir)
                
                if config.generate_page_screenshots:
                    page_screenshots = self._generate_page_screenshots(pdf_path, config.output_dir)
                    result.page_screenshots = page_screenshots
                
                if config.extract_page_numbers:
                    page_numbers = self._extract_page_numbers(pdf_path, result.content)
                    result.page_numbers = page_numbers
                
                # Clean up temporary PDF
                if not config.convert_to_pdf and pdf_path.exists():
                    pdf_path.unlink()
            
            # Handle HTML generation (doesn't require LibreOffice)
            if config.generate_html:
                html_content = self._generate_html_content(result.content)
                result.html_content = html_content
            
            self.logger.info("Enhanced processing completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced processing failed: {e}")
            # Don't fail completely - return the basic result with warnings
            result.warnings.append(f"Enhanced processing failed: {e}")
            return result
    
    def _convert_docx_to_pdf(self, docx_path: Path, output_dir: Optional[Path]) -> Path:
        """Convert DOCX to PDF using LibreOffice."""
        self.logger.info(f"Converting DOCX to PDF: {docx_path}")
        
        # Use temporary directory for conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # LibreOffice command for headless conversion
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(temp_dir_path),
                str(docx_path)
            ]
            
            try:
                # Try primary command first
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # Fallback to soffice if libreoffice not found
                cmd[0] = 'soffice'
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                except Exception as e:
                    raise ProcessingError(f"Failed to run LibreOffice conversion: {e}")
            
            if result.returncode != 0:
                raise ProcessingError(f"LibreOffice conversion failed: {result.stderr}")
            
            # Find the generated PDF
            pdf_name = docx_path.stem + '.pdf'
            temp_pdf_path = temp_dir_path / pdf_name
            
            if not temp_pdf_path.exists():
                raise ProcessingError(f"PDF was not generated: {temp_pdf_path}")
            
            # Move PDF to final location
            if output_dir:
                final_pdf_path = output_dir / pdf_name
                final_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                final_pdf_path = docx_path.parent / pdf_name
            
            shutil.move(str(temp_pdf_path), str(final_pdf_path))
            
            self.logger.info(f"PDF generated: {final_pdf_path}")
            return final_pdf_path
    
    def _generate_page_screenshots(self, pdf_path: Path, output_dir: Optional[Path]) -> Dict[int, str]:
        """Generate page screenshots from PDF using PyMuPDF."""
        import fitz  # PyMuPDF
        
        self.logger.info(f"Generating page screenshots from: {pdf_path}")
        
        screenshots = {}
        
        # Create screenshots directory
        if output_dir:
            screenshots_dir = output_dir / 'pages'
        else:
            screenshots_dir = pdf_path.parent / 'pages'
        
        screenshots_dir.mkdir(exist_ok=True)
        
        try:
            # Open PDF document
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Render page to image
                # Use matrix for good quality (2x scaling)
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                
                # Save image
                image_filename = f"page_{page_num + 1:03d}.png"
                image_path = screenshots_dir / image_filename
                pix.save(str(image_path))
                
                # Store relative path for portability
                screenshots[page_num + 1] = f"pages/{image_filename}"
                
                self.logger.debug(f"Generated screenshot for page {page_num + 1}")
            
            doc.close()
            
            self.logger.info(f"Generated {len(screenshots)} page screenshots")
            return screenshots
            
        except Exception as e:
            raise ProcessingError(f"Failed to generate page screenshots: {e}")
    
    def _extract_page_numbers(self, pdf_path: Path, content: Dict) -> Dict[str, int]:
        """Extract page number mappings for content sections."""
        import fitz  # PyMuPDF
        
        self.logger.info("Extracting page number mappings")
        
        page_mappings = {}
        
        try:
            doc = fitz.open(str(pdf_path))
            
            # Extract all text with page information
            page_texts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                page_texts.append((page_num + 1, text))
            
            doc.close()
            
            # Map sections to pages
            if 'sections' in content:
                for section_idx, section in enumerate(content['sections']):
                    section_id = f"section_{section_idx}"
                    section_text = section.get('content', '')
                    
                    # Find which page contains the most of this section's text
                    best_page = 1
                    best_match_ratio = 0
                    
                    if section_text.strip():
                        # Take first significant chunk of section text for matching
                        search_text = section_text[:500].strip()
                        
                        for page_num, page_text in page_texts:
                            # Simple text matching - could be improved with fuzzy matching
                            if search_text in page_text:
                                # Calculate how much of the section appears on this page
                                match_ratio = len(search_text) / len(page_text) if page_text else 0
                                if match_ratio > best_match_ratio:
                                    best_match_ratio = match_ratio
                                    best_page = page_num
                    
                    page_mappings[section_id] = best_page
                    self.logger.debug(f"Mapped {section_id} to page {best_page}")
            
            self.logger.info(f"Generated page mappings for {len(page_mappings)} sections")
            return page_mappings
            
        except Exception as e:
            self.logger.error(f"Failed to extract page numbers: {e}")
            return {}
    
    def _generate_html_content(self, content: Dict) -> str:
        """Generate HTML representation of the document content."""
        self.logger.info("Generating HTML content")
        
        html_parts = ['<!DOCTYPE html>', '<html>', '<head>']
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<title>Document Content</title>')
        html_parts.append('<style>')
        html_parts.append('body { font-family: Arial, sans-serif; margin: 40px; }')
        html_parts.append('h1 { color: #333; border-bottom: 2px solid #333; }')
        html_parts.append('h2 { color: #666; border-bottom: 1px solid #666; }')
        html_parts.append('h3 { color: #999; }')
        html_parts.append('.section { margin-bottom: 30px; }')
        html_parts.append('</style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # Handle both old structure (content['sections']) and new structure (flat dict)
        if 'sections' in content:
            # Old structure - list of section objects
            for i, section in enumerate(content['sections']):
                section_title = section.get('title', f'Section {i + 1}')
                section_content = section.get('content', '')
                
                # Determine heading level based on title patterns
                if any(keyword in section_title.lower() for keyword in ['chapter', 'part']):
                    heading_tag = 'h1'
                elif any(keyword in section_title.lower() for keyword in ['section', 'subsection']):
                    heading_tag = 'h2' 
                else:
                    heading_tag = 'h3'
                
                html_parts.append('<div class="section">')
                html_parts.append(f'<{heading_tag}>{section_title}</{heading_tag}>')
                
                # Convert line breaks and basic formatting
                formatted_content = section_content.replace('\n', '<br>')
                html_parts.append(f'<p>{formatted_content}</p>')
                html_parts.append('</div>')
        else:
            # New structure - flat dictionary with section names as keys
            for section_title, section_content in content.items():
                # Determine heading level based on title patterns and numbering
                if any(keyword in section_title.lower() for keyword in ['chapter', 'part']) or section_title.count('.') == 0:
                    heading_tag = 'h1'
                elif section_title.count('.') == 1:
                    heading_tag = 'h2' 
                else:
                    heading_tag = 'h3'
                
                html_parts.append('<div class="section">')
                html_parts.append(f'<{heading_tag}>{section_title}</{heading_tag}>')
                
                # Convert line breaks and basic formatting
                formatted_content = section_content.replace('\n', '<br>')
                html_parts.append(f'<p>{formatted_content}</p>')
                html_parts.append('</div>')
        
        html_parts.extend(['</body>', '</html>'])
        
        html_content = '\n'.join(html_parts)
        self.logger.info("HTML content generation completed")
        return html_content