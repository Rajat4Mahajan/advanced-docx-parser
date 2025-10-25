"""
Basic DOCX processor using pure python-docx.
This is the foundation that works without any external dependencies.
"""

import logging
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from io import BytesIO

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from PIL import Image
import re

from ..models import (
    ProcessingResult, ProcessingConfig, ProcessingMode,
    SectionInfo, ImageInfo, TableInfo, TOCEntry
)
from ..exceptions import ProcessingError
from ..utils.text_utils import clean_string, remove_section_headers


class BasicProcessor:
    """
    Pure python-docx processor for basic DOCX document processing.
    
    This processor handles:
    - Document structure extraction
    - Text content extraction with hierarchy
    - Table extraction and HTML conversion
    - Basic image extraction
    - Table of contents generation
    """
    
    def __init__(self, config: ProcessingConfig, logger: logging.Logger):
        """
        Initialize the basic processor.
        
        Args:
            config: Processing configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.image_count = 0
    
    def process(self, file_path: Path, config: ProcessingConfig) -> ProcessingResult:
        """
        Process a DOCX document using basic python-docx functionality.
        
        Args:
            file_path: Path to the DOCX file
            config: Processing configuration
            
        Returns:
            ProcessingResult with extracted content
        """
        self.logger.info(f"Starting basic processing of {file_path}")
        
        try:
            # Load the document
            doc = Document(file_path)
            
            # Extract structured content
            content_dict, content_without_children, image_sections, table_mapping, table_dict, toc = self._process_document_structure(doc)
            
            # Extract images
            images_dict = {}
            if config.save_images:
                images_dict = self._extract_images(doc, image_sections, config.output_dir)
            
            # Process tables
            tables_dict = {}
            if config.save_tables:
                tables_dict = self._process_tables(table_dict, config.output_dir)
            
            # Build TOC if requested
            toc_entries = None
            if config.extract_toc and toc:
                toc_entries = self._build_toc_entries(toc)
            
            # Create section info hierarchy
            content_hierarchy = self._build_content_hierarchy(content_dict)
            
            # Create result
            result = ProcessingResult(
                content=content_dict,
                content_without_children=content_without_children,
                content_hierarchy=content_hierarchy,
                images=images_dict,
                tables=tables_dict,
                toc=toc_entries,
                processing_mode=ProcessingMode.BASIC
            )
            
            # Save outputs if output directory is specified
            if config.output_dir:
                self._save_outputs(result, config.output_dir, config)
            
            self.logger.info(f"Basic processing completed. Extracted {len(content_dict)} sections, {len(images_dict)} images, {len(tables_dict)} tables")
            return result
            
        except Exception as e:
            self.logger.error(f"Basic processing failed: {e}")
            raise ProcessingError(f"Failed to process document: {e}") from e
    
    def _process_document_structure(self, doc: Document) -> Tuple[Dict, Dict, List, Dict, Dict, Any]:
        """
        Extract the document structure with proper hierarchy.
        
        This is adapted from the original DOCXProcessor.process_docx method.
        """
        content_dict = {}
        counters = {}
        table_mapping = {}
        table_dict = {}
        
        stack = []
        img_title = []
        title = None
        current_content = None
        table_count = 1
        
        self.logger.debug("Processing document structure with hierarchy")
        
        # Process paragraphs and tables together to preserve order
        # We'll iterate through the document elements in order
        for paragraph in doc.paragraphs:
            content = paragraph.text
            
            # Skip empty paragraphs without images
            image_is_present = self._has_image_in_paragraph(paragraph)
            if content.strip() == '' and not image_is_present:
                continue
            
            heading_level = self._get_heading_level(paragraph)
            
            if heading_level:
                # Initialize or reset counters for deeper levels
                if heading_level not in counters:
                    counters[heading_level] = 0
                counters[heading_level] += 1
                
                # Reset counters for sublevels
                for level in list(counters.keys()):
                    if level > heading_level:
                        counters[level] = 0
                
                # Generate the numbering for the current heading
                numbering = '.'.join(str(counters[level]) for level in sorted(counters) if counters[level] > 0)
                
                # If we are encountering a new heading level, save the previous content
                if current_content is not None:
                    content_dict[current_content["title"]] = current_content
                
                # Determine the parent
                parent = None
                if stack:
                    if stack[-1]["level"] < heading_level:
                        parent = stack[-1]["title"]
                    elif stack[-1]["level"] == heading_level:
                        parent = stack[-1]['parent']
                    else:
                        while stack and stack[-1]["level"] >= heading_level:
                            stack.pop()
                        parent = stack[-1]["title"] if stack else None
                
                # Create title with numbering if needed
                pattern = r'^\s*\d+(\.\d+)*\.?\s*'
                if re.match(pattern, paragraph.text):
                    title = f"{paragraph.text}"
                else:
                    title = f"{numbering} {paragraph.text}"
                
                if title.strip() == '':
                    title = 'Orphaned Section'
                
                current_content = {
                    "title": title,
                    "level": heading_level,
                    "content": "",
                    "parent": parent,
                    "children": []
                }
                
                # Manage the stack to handle hierarchy
                while stack and stack[-1]["level"] >= heading_level:
                    stack.pop()
                
                if parent and parent in content_dict:
                    content_dict[parent]["children"].append(current_content["title"])
                
                stack.append({"title": current_content["title"], "level": heading_level, "parent": parent})
                
            else:
                # Append content to the current heading
                if current_content is not None:
                    current_content["content"] += content + "\n"
                else:
                    # If we haven't encountered any heading yet, create a title page
                    current_content = {
                        "title": 'TITLE PAGE',
                        "level": 1,
                        "content": content + "\n",
                        "parent": None,
                        "children": []
                    }
            
            # Create a dict for the sections that contain images
            if image_is_present:
                current_title = current_content["title"] if current_content else 'TITLE PAGE'
                if current_title not in img_title:
                    img_title.append(current_title)
        
        # Process tables (simplified for now - we'll enhance this later)
        for table in doc.tables:
            table_html = self._table_to_html(table)
            table_file_name = f"table_{table_count}.html"
            table_dict[table_file_name] = table_html
            
            # Add table to current section
            if current_content is not None:
                current_content["content"] += f"Table\n{table_html}\n"
                
                # Track table mapping
                section_title = current_content["title"]
                if section_title in table_mapping:
                    table_mapping[section_title].append(table_file_name)
                else:
                    table_mapping[section_title] = [table_file_name]
            
            table_count += 1
        
        # Append the last content item
        if current_content is not None:
            content_dict[current_content["title"]] = current_content
        
        # Create content without children (individual sections only)
        final_dict_without_child = {item["title"]: item["content"] for item in content_dict.values()}
        
        # Build table of contents (simplified for now)
        toc = self._build_toc(list(content_dict.values()))
        
        # Recursive function to aggregate content from children to parent
        def aggregate_content(title: str) -> None:
            item = content_dict[title]
            for child_title in item["children"]:
                if child_title in content_dict:  # Safety check
                    aggregate_content(child_title)
                    item["content"] += f"\n\n{content_dict[child_title]['title']}\n\n{content_dict[child_title]['content']}"
        
        # Start aggregation from the top-level items
        top_level_titles = [title for title, item in content_dict.items() if item["parent"] is None]
        for title in top_level_titles:
            aggregate_content(title)
        
        # Prepare the final dictionary with title as key and combined content as value
        final_dict = {item["title"]: item["content"] for item in content_dict.values()}
        
        self.logger.debug(f"Extracted {len(final_dict)} sections with hierarchy")
        
        return final_dict, final_dict_without_child, img_title, table_mapping, table_dict, toc
    
    def _has_image_in_paragraph(self, paragraph: Paragraph) -> bool:
        """Check if a paragraph contains an image."""
        try:
            return (
                'w:drawing' in paragraph._p.xml and (
                    ("graphicData" in paragraph._p.xml) or
                    ("wp:anchor" in paragraph._p.xml)
                )
                or ("imagedata" in paragraph._p.xml)
            )
        except Exception:
            return False
    
    def _get_heading_level(self, paragraph: Paragraph) -> Optional[int]:
        """Get the heading level of a paragraph."""
        try:
            if paragraph.style.name.startswith('Heading'):
                try:
                    return int(paragraph.style.name.split()[-1])
                except:
                    # Handle ill-formatted heading styles
                    return int(list(set(re.findall(r'\d+', paragraph.style.name)))[0])
            return None
        except Exception:
            return None
    
    def _table_to_html(self, table: Table) -> str:
        """
        Convert a DOCX table to HTML representation.
        Simplified version of your original method.
        """
        try:
            html_output = "<table style='border-collapse: collapse; border: 1px solid black;'>"
            
            # Table header
            if table.rows:
                html_output += "<thead><tr>"
                for cell in table.rows[0].cells:
                    html_output += f"<th style='border: 1px solid black; padding: 5px;'>"
                    for para in cell.paragraphs:
                        html_output += f"<p>{para.text}</p>"
                    html_output += "</th>"
                html_output += "</tr></thead>"
            
            # Table body
            html_output += "<tbody>"
            for row in table.rows[1:]:
                html_output += "<tr>"
                for cell in row.cells:
                    html_output += f"<td style='border: 1px solid black; padding: 5px;'>"
                    for para in cell.paragraphs:
                        html_output += f"<p>{para.text}</p>"
                    html_output += "</td>"
                html_output += "</tr>"
            html_output += "</tbody>"
            html_output += "</table>"
            
            return html_output
        except Exception as e:
            self.logger.error(f"Error converting table to HTML: {e}")
            return f"<p>Error processing table: {e}</p>"
    
    def _build_toc(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a table of contents from section hierarchy."""
        toc = {}
        
        # Sort sections by level to build hierarchy
        sorted_sections = sorted(sections, key=lambda x: x.get('level', 1))
        
        for section in sorted_sections:
            title = section['title']
            level = section.get('level', 1)
            parent = section.get('parent')
            
            toc[title] = {
                'level': level,
                'parent': parent,
                'children': section.get('children', [])
            }
        
        return toc
    
    def _extract_images(self, doc: Document, image_sections: List[str], output_dir: Optional[Path]) -> Dict[str, ImageInfo]:
        """Extract images from the document."""
        images_dict = {}
        
        try:
            for element in doc.element.body.iter():
                if element.tag == qn('w:drawing'):
                    for child in element.iter():
                        if child.tag == qn('a:blip'):
                            image_info = self._extract_blip_image(child, doc, output_dir)
                            if image_info:
                                images_dict[image_info.filename] = image_info
        except Exception as e:
            self.logger.error(f"Error extracting images: {e}")
        
        return images_dict
    
    def _extract_blip_image(self, blip_child, doc: Document, output_dir: Optional[Path]) -> Optional[ImageInfo]:
        """Extract a single blip image."""
        try:
            rId = blip_child.attrib[qn('r:embed')]
            image = doc.part.related_parts[rId]
            image_filename = f"image_{self.image_count}.{image.content_type.split('/')[-1]}"
            image_bytes = image.blob
            
            # Save image if output directory is provided
            if output_dir:
                images_dir = output_dir / "images"
                images_dir.mkdir(parents=True, exist_ok=True)
                image_path = images_dir / image_filename
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
            
            # Get image dimensions
            try:
                img = Image.open(BytesIO(image_bytes))
                width, height = img.size
            except:
                width, height = None, None
            
            self.image_count += 1
            
            return ImageInfo(
                filename=image_filename,
                size_bytes=len(image_bytes),
                width=width,
                height=height,
                format=image.content_type.split('/')[-1]
            )
        except Exception as e:
            self.logger.error(f"Error extracting blip image: {e}")
            return None
    
    def _process_tables(self, table_dict: Dict[str, str], output_dir: Optional[Path]) -> Dict[str, TableInfo]:
        """Process and save tables."""
        tables_info = {}
        
        if output_dir:
            tables_dir = output_dir / "tables"
            tables_dir.mkdir(parents=True, exist_ok=True)
            
            for filename, html_content in table_dict.items():
                table_path = tables_dir / filename
                with open(table_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                # Create table info
                tables_info[filename] = TableInfo(
                    filename=filename,
                    rows=html_content.count("<tr>"),
                    columns=html_content.count("<th>") or html_content.count("<td>")
                )
        
        return tables_info
    
    def _build_toc_entries(self, toc: Any) -> List[TOCEntry]:
        """Convert TOC structure to TOCEntry objects."""
        # This would need to be implemented based on your TOC structure
        return []
    
    def _build_content_hierarchy(self, content_dict: Dict) -> Dict[str, SectionInfo]:
        """Build content hierarchy from the content dictionary."""
        hierarchy = {}
        
        for title, content in content_dict.items():
            # For now, create simple hierarchy since our content_dict is just title->content
            hierarchy[title] = SectionInfo(
                title=title,
                content=content,
                level=1,  # Default level
                parent=None,
                children=[]
            )
        
        return hierarchy
    
    def _build_toc(self, elements: List[Dict]) -> Any:
        """Build table of contents from document elements."""
        # Simplified version - you can adapt your original build_toc method here
        return None
    
    def _save_outputs(self, result: ProcessingResult, output_dir: Path, config: ProcessingConfig) -> None:
        """Save processing outputs to files."""
        if config.save_content:
            # Save content as JSON
            content_path = output_dir / "content.json"
            with open(content_path, "w", encoding="utf-8") as f:
                json.dump(result.content, f, indent=2, ensure_ascii=False)
            
            if result.content_without_children:
                content_without_children_path = output_dir / "content_without_children.json"
                with open(content_without_children_path, "w", encoding="utf-8") as f:
                    json.dump(result.content_without_children, f, indent=2, ensure_ascii=False)
        
        # Update result with output paths
        result.output_paths = {
            "content": output_dir / "content.json",
            "images": output_dir / "images",
            "tables": output_dir / "tables"
        }