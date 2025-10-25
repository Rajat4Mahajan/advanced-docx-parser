"""
Command-line interface for DOCX Processor.
"""

import json
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

from . import DOCXProcessor, ProcessingMode, ProcessingConfig
from .exceptions import DOCXProcessorError


app = typer.Typer(
    name="docx-processor",
    help="Advanced DOCX document processing with hierarchical content extraction"
)
console = Console()


@app.command()
def process(
    input_file: Path = typer.Argument(..., help="DOCX file to process"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    mode: ProcessingMode = typer.Option(ProcessingMode.BASIC, "--mode", "-m", help="Processing mode"),
    
    # Content options
    save_images: bool = typer.Option(True, "--images/--no-images", help="Save extracted images"),
    save_tables: bool = typer.Option(True, "--tables/--no-tables", help="Save extracted tables"),
    save_content: bool = typer.Option(True, "--content/--no-content", help="Save content files"),
    
    # Enhanced options
    page_screenshots: bool = typer.Option(False, "--screenshots", help="Generate page screenshots"),
    page_numbers: bool = typer.Option(False, "--page-numbers", help="Extract page number mappings"),
    convert_pdf: bool = typer.Option(False, "--pdf", help="Convert to PDF"),
    
    # Professional options
    standardize_headings: bool = typer.Option(False, "--standardize", help="Standardize heading styles"),
    preserve_formatting: bool = typer.Option(False, "--formatting", help="Preserve advanced formatting"),
    generate_html: bool = typer.Option(False, "--html", help="Generate HTML output"),
    
    # Processing options
    max_pages: Optional[int] = typer.Option(None, "--max-pages", help="Maximum pages to process"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Process a DOCX file and extract content, images, and tables.
    
    Example:
        docx-processor process document.docx --output ./output --mode enhanced --screenshots
    """
    # Validate input file
    if not input_file.exists():
        console.print(f"[red]Error: File not found: {input_file}[/red]")
        raise typer.Exit(1)
    
    if not input_file.suffix.lower() == '.docx':
        console.print(f"[red]Error: File must be a DOCX document: {input_file}[/red]")
        raise typer.Exit(1)
    
    # Set default output directory
    if output_dir is None:
        output_dir = Path.cwd() / f"{input_file.stem}_output"
    
    # Create configuration
    config = ProcessingConfig(
        mode=mode,
        output_dir=output_dir,
        save_images=save_images,
        save_tables=save_tables,
        save_content=save_content,
        generate_page_screenshots=page_screenshots,
        extract_page_numbers=page_numbers,
        convert_to_pdf=convert_pdf,
        standardize_headings=standardize_headings,
        preserve_formatting=preserve_formatting,
        generate_html=generate_html,
        max_pages_to_process=max_pages,
    )
    
    # Setup logging level
    if verbose:
        from .utils import setup_logging
        setup_logging("DEBUG")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Processing {input_file.name}...", total=None)
            
            # Initialize processor
            processor = DOCXProcessor(mode=mode, config=config)
            
            # Process the document
            result = processor.process_file(input_file, output_dir=output_dir)
            
            progress.update(task, description="Processing complete!")
        
        # Display results
        _display_results(result, input_file, output_dir)
        
        console.print(f"\n[green]✓ Processing completed successfully![/green]")
        console.print(f"Output saved to: [blue]{output_dir.absolute()}[/blue]")
        
    except DOCXProcessorError as e:
        console.print(f"\n[red]Processing failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def validate(
    files: List[Path] = typer.Argument(..., help="DOCX files to validate")
):
    """
    Validate DOCX files without processing them.
    
    Example:
        docx-processor validate document1.docx document2.docx
    """
    processor = DOCXProcessor()
    
    table = Table(title="DOCX Validation Results")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Size", justify="right")
    
    valid_count = 0
    for file_path in files:
        if not file_path.exists():
            table.add_row(str(file_path), "[red]Not Found[/red]", "-")
            continue
        
        is_valid = processor.validate_file(file_path)
        size = f"{file_path.stat().st_size / 1024:.1f} KB"
        
        if is_valid:
            table.add_row(str(file_path), "[green]Valid[/green]", size)
            valid_count += 1
        else:
            table.add_row(str(file_path), "[red]Invalid[/red]", size)
    
    console.print(table)
    console.print(f"\n[green]{valid_count}/{len(files)} files are valid DOCX documents[/green]")


@app.command()
def info():
    """
    Display information about available processing modes and dependencies.
    """
    console.print("\n[bold blue]DOCX Processor - Processing Modes[/bold blue]\n")
    
    modes_table = Table(title="Available Processing Modes")
    modes_table.add_column("Mode", style="cyan")
    modes_table.add_column("Dependencies", style="yellow")
    modes_table.add_column("Features", style="green")
    
    modes_table.add_row(
        "basic",
        "python-docx, Pillow, BeautifulSoup4",
        "Content extraction, images, tables, TOC"
    )
    modes_table.add_row(
        "enhanced", 
        "PyMuPDF, LibreOffice",
        "Basic + PDF conversion, page screenshots, page numbers"
    )
    modes_table.add_row(
        "professional",
        "aspose-words (license required)",
        "Enhanced + advanced formatting, HTML conversion, citations"
    )
    
    console.print(modes_table)
    
    # Check dependencies
    console.print("\n[bold blue]Dependency Status[/bold blue]\n")
    
    deps_table = Table()
    deps_table.add_column("Dependency", style="cyan")
    deps_table.add_column("Status", style="green")
    deps_table.add_column("Required For")
    
    # Check basic dependencies
    try:
        import docx
        deps_table.add_row("python-docx", "[green]✓ Available[/green]", "Basic processing")
    except ImportError:
        deps_table.add_row("python-docx", "[red]✗ Missing[/red]", "Basic processing")
    
    try:
        import PIL
        deps_table.add_row("Pillow", "[green]✓ Available[/green]", "Image processing")
    except ImportError:
        deps_table.add_row("Pillow", "[red]✗ Missing[/red]", "Image processing")
    
    # Check enhanced dependencies
    try:
        import fitz
        deps_table.add_row("PyMuPDF", "[green]✓ Available[/green]", "Enhanced processing")
    except ImportError:
        deps_table.add_row("PyMuPDF", "[red]✗ Missing[/red]", "Enhanced processing")
    
    # Check professional dependencies
    try:
        import aspose.words
        deps_table.add_row("aspose-words", "[green]✓ Available[/green]", "Professional processing")
    except ImportError:
        deps_table.add_row("aspose-words", "[red]✗ Missing[/red]", "Professional processing")
    
    console.print(deps_table)


def _display_results(result, input_file: Path, output_dir: Path):
    """Display processing results in a formatted table."""
    
    results_table = Table(title=f"Processing Results - {input_file.name}")
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Count", justify="right", style="green")
    
    results_table.add_row("Sections", str(len(result.content)))
    results_table.add_row("Images", str(len(result.images)))
    results_table.add_row("Tables", str(len(result.tables)))
    
    if result.processing_time_seconds:
        results_table.add_row("Processing Time", f"{result.processing_time_seconds:.2f}s")
    
    if result.file_size_bytes:
        size_mb = result.file_size_bytes / (1024 * 1024)
        results_table.add_row("File Size", f"{size_mb:.2f} MB")
    
    console.print(results_table)
    
    # Show warnings/errors if any
    if result.warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            console.print(f"  • {warning}")
    
    if result.errors:
        console.print("\n[red]Errors:[/red]")
        for error in result.errors:
            console.print(f"  • {error}")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()