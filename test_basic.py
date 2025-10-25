#!/usr/bin/env python3
"""
Simple test script to verify the basic processor works.
"""

from pathlib import Path
import sys

# Add the src directory to the path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from docx_processor import DOCXProcessor, ProcessingMode
    print("✓ Successfully imported DOCXProcessor")
    
    # Test initialization
    processor = DOCXProcessor(mode=ProcessingMode.BASIC)
    print("✓ Successfully initialized processor")
    
    # Test CLI import
    from docx_processor.cli import app
    print("✓ Successfully imported CLI")
    
    print("\n🎉 Basic setup is working!")
    print("\nNext steps:")
    print("1. Create a sample DOCX file")
    print("2. Test processing with: uv run docx-processor process sample.docx")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Some dependencies might be missing")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()