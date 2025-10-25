#!/usr/bin/env python3
"""
Basic usage example for DOCX Processor.

This example shows how to process a DOCX file and extract content,
images, and tables using the basic processing mode.
"""

from pathlib import Path
from docx_processor import DOCXProcessor, ProcessingConfig, ProcessingMode


def basic_processing_example():
    """Example of basic DOCX processing."""
    
    # Initialize processor in basic mode
    processor = DOCXProcessor(mode=ProcessingMode.BASIC)
    
    # Configure processing options
    config = ProcessingConfig(
        mode=ProcessingMode.BASIC,
        save_images=True,
        save_tables=True,
        save_content=True,
        preserve_hierarchy=True,
        extract_toc=True
    )
    
    # Process a document
    input_file = Path("sample_document.docx")
    output_dir = Path("./output")
    
    if input_file.exists():
        print(f"Processing {input_file}...")
        
        result = processor.process_file(
            input_file, 
            output_dir=output_dir,
            **config.dict()
        )
        
        # Display results
        print(f"✓ Processing completed!")
        print(f"  - Extracted {len(result.content)} sections")
        print(f"  - Extracted {len(result.images)} images") 
        print(f"  - Extracted {len(result.tables)} tables")
        print(f"  - Processing time: {result.processing_time_seconds:.2f}s")
        print(f"  - Output saved to: {output_dir}")
        
        # Access specific content
        if "TITLE PAGE" in result.content:
            print(f"\nTitle page content preview:")
            print(result.content["TITLE PAGE"][:200] + "...")
        
        # List all sections
        print(f"\nDocument sections:")
        for i, section_title in enumerate(result.content.keys(), 1):
            print(f"  {i}. {section_title}")
        
        # Show image information
        if result.images:
            print(f"\nExtracted images:")
            for filename, info in result.images.items():
                print(f"  - {filename}: {info.size_bytes} bytes ({info.format})")
        
        # Show table information
        if result.tables:
            print(f"\nExtracted tables:")
            for filename, info in result.tables.items():
                print(f"  - {filename}: {info.rows} rows × {info.columns} columns")
        
        return result
    
    else:
        print(f"Sample document not found: {input_file}")
        print("Please place a DOCX file named 'sample_document.docx' in this directory.")
        return None


def enhanced_processing_example():
    """Example of enhanced DOCX processing with LibreOffice features."""
    
    try:
        # Initialize processor in enhanced mode
        processor = DOCXProcessor(mode=ProcessingMode.ENHANCED)
        
        input_file = Path("sample_document.docx")
        output_dir = Path("./enhanced_output")
        
        if input_file.exists():
            print(f"Processing {input_file} with enhanced features...")
            
            result = processor.process_file(
                input_file,
                output_dir=output_dir,
                generate_page_screenshots=True,
                extract_page_numbers=True,
                convert_to_pdf=True
            )
            
            print(f"✓ Enhanced processing completed!")
            print(f"  - Total pages: {result.total_pages}")
            
            if result.page_screenshots:
                print(f"  - Generated {len(result.page_screenshots)} page screenshots")
            
            if result.page_numbers:
                print(f"  - Mapped {len(result.page_numbers)} sections to page numbers")
            
            return result
        
        else:
            print(f"Sample document not found: {input_file}")
            return None
    
    except Exception as e:
        print(f"Enhanced processing failed: {e}")
        print("This likely means LibreOffice or PyMuPDF dependencies are missing.")
        print("Install with: pip install 'docx-processor[enhanced]'")
        return None


def professional_processing_example():
    """Example of professional DOCX processing with Aspose.Words features."""
    
    try:
        # Initialize processor in professional mode  
        processor = DOCXProcessor(mode=ProcessingMode.PROFESSIONAL)
        
        input_file = Path("sample_document.docx")
        output_dir = Path("./professional_output")
        
        if input_file.exists():
            print(f"Processing {input_file} with professional features...")
            
            result = processor.process_file(
                input_file,
                output_dir=output_dir,
                standardize_headings=True,
                preserve_formatting=True,
                generate_html=True,
                process_citations=True
            )
            
            print(f"✓ Professional processing completed!")
            
            if result.html_content:
                print(f"  - Generated HTML output with preserved formatting")
            
            if result.html_content_hierarchy:
                print(f"  - Created hierarchical HTML content structure")
            
            return result
        
        else:
            print(f"Sample document not found: {input_file}")
            return None
    
    except Exception as e:
        print(f"Professional processing failed: {e}")
        print("This likely means Aspose.Words license or dependencies are missing.")
        print("Install with: pip install 'docx-processor[professional]'")
        return None


if __name__ == "__main__":
    print("DOCX Processor Examples")
    print("=" * 50)
    
    # Run basic example
    print("\n1. Basic Processing Example:")
    print("-" * 30)
    basic_result = basic_processing_example()
    
    # Run enhanced example if basic worked
    if basic_result:
        print("\n2. Enhanced Processing Example:")
        print("-" * 35)
        enhanced_result = enhanced_processing_example()
        
        # Run professional example if enhanced worked
        if enhanced_result:
            print("\n3. Professional Processing Example:")
            print("-" * 40)
            professional_result = professional_processing_example()
    
    print("\n" + "=" * 50)
    print("Examples completed!")