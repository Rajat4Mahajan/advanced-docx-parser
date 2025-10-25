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
        Extract the document structure including sections, images, and tables.
        
        This is adapted from your original DOCXProcessor.process_docx method.
        """
        content_dict = {}
        counters = {}
        table_mapping = {}
        final_dict = {}
        table_dict = {}
        
        stack = []
        img_title = []
        title = None
        current_content = None
        table_count = 1
        
        self.logger.debug("Processing document structure")
        
        for block in doc.iter_inner_content():
            paragraph = None
            table = None
            
            if isinstance(block, Paragraph):
                paragraph = block
            elif isinstance(block, Table):
                table = block
            
            if paragraph:
                content = paragraph.text
                image_is_present = self._has_image_in_paragraph(paragraph)
                
                if content.strip() == '' and not image_is_present:
                    continue
                
                heading_level = self._get_heading_level(paragraph)
                
                if heading_level:
                    # Handle heading logic (similar to your original code)
                    if heading_level not in counters:
                        counters[heading_level] = 0
                    counters[heading_level] += 1
                    
                    # Reset counters for sublevels
                    for level in list(counters.keys()):
                        if level > heading_level:
                            counters[level] = 0
                    
                    # Generate numbering
                    numbering = '.'.join(str(counters[level]) for level in sorted(counters) if counters[level] > 0)
                    
                    if current_content is not None:
                        content_dict[current_content["title"]] = current_content
                    
                    # Determine parent
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
                    
                    # Create title with numbering
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
                    
                    # Manage stack for hierarchy
                    while stack and stack[-1]["level"] >= heading_level:
                        stack.pop()
                    
                    if parent:
                        content_dict[parent]["children"].append(current_content["title"])
                    
                    stack.append({"title": current_content["title"], "level": heading_level, "parent": parent})
                    
                else:
                    # Append content to current heading
                    if current_content is not None:
                        current_content["content"] += content + "\n"
                    else:
                        current_content = {
                            "title": 'TITLE PAGE',
                            "level": 1,
                            "content": content,
                            "parent": None,
                            "children": []
                        }
                
                if image_is_present:
                    img_title.append(title)
            
            elif table:
                table_html = self._table_to_html(table)
                table_file_name = f"table_{table_count}.html"
                table_dict[table_file_name] = table_html
                
                if title is None:
                    title = 'TITLE PAGE'
                    current_content = {
                        "title": title,
                        "level": None,
                        "content": "Table\n" + table_html + "\n",
                        "parent": None,
                        "children": []
                    }
                else:
                    current_content["content"] += "Table\n" + table_html + "\n"
                
                if title in table_mapping:
                    table_mapping[title].append(table_file_name)
                else:
                    table_mapping[title] = [table_file_name]
                
                table_count += 1
        
        # Append the last content item
        if current_content is not None:
            content_dict[current_content["title"]] = current_content
        
        # Create content without children first
        final_dict_without_child = {item["title"]: item["content"] for item in content_dict.values()}
        
        # Build table of contents
        toc = self._build_toc(list(content_dict.values()))
        
        # Aggregate content from children to parent
        def aggregate_content(title: str) -> None:
            item = content_dict[title]
            for child_title in item["children"]:
                aggregate_content(child_title)
                item["content"] += content_dict[child_title]["title"] + '\n\n' + content_dict[child_title]["content"]
        
        # Start aggregation from top-level items
        top_level_titles = [title for title, item in content_dict.items() if item["parent"] is None]
        for title in top_level_titles:
            aggregate_content(title)
        
        # Prepare final dictionary
        final_dict = {item["title"]: item["content"] for item in content_dict.values()}
        
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
        
        for title, item in content_dict.items():
            hierarchy[title] = SectionInfo(
                title=item["title"],
                content=item["content"],
                level=item.get("level", 1),
                parent=item.get("parent"),
                children=item.get("children", [])
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