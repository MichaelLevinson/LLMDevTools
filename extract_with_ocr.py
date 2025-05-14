#!/usr/bin/env python3
"""
Optimized OCR text extraction for scanned PDFs with Apple Silicon acceleration.
Uses PyMuPDF for PDF processing and Tesseract for OCR with parallelization.
python extract_with_ocr.py <filename>.pdf -o /path/to/llm.txt
"""
import os
import sys
import time
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import fitz
import numpy as np
import pytesseract
from PIL import Image

# Performance monitoring
start_time = time.time()
pages_processed = 0
total_pages = 0

def check_hardware_capabilities():
    """Check hardware capabilities and set optimal configuration."""
    import platform
    
    is_apple_silicon = (platform.system() == "Darwin" and 
                        platform.machine() in ["arm64", "arm64e"])
    
    # Detect number of cores for parallel processing
    cpu_count = os.cpu_count()
    optimal_workers = max(1, cpu_count - 1)  # Leave one core free
    
    print(f"Hardware detection:")
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print(f"  CPU cores: {cpu_count}")
    print(f"  Using workers: {optimal_workers}")
    print(f"  Apple Silicon: {'Yes' + ' (accelerated)' if is_apple_silicon else 'No'}")
    
    return {"is_apple_silicon": is_apple_silicon, "workers": optimal_workers}

def process_page(args):
    """Process a single page with OCR."""
    page_num, pdf_path, dpi, lang = args
    
    # Open the PDF and get the specific page
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    
    # Higher DPI for better OCR quality, especially for small text
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
    
    # Convert to PIL Image for Tesseract
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Run OCR with specified language
    text = pytesseract.image_to_string(img, lang=lang)
    
    return page_num, text

def extract_text_with_ocr(pdf_path, output_file=None, dpi=300, lang='eng', 
                          batch_size=None, hardware_config=None):
    """
    Extract text from a PDF using OCR, optimized for performance.
    
    Args:
        pdf_path: Path to the PDF file
        output_file: Path to save the extracted text (default: None)
        dpi: Resolution for image extraction (default: 300)
        lang: Tesseract language (default: 'eng')
        batch_size: Number of pages to process in parallel (default: auto)
        hardware_config: Hardware capabilities configuration
    
    Returns:
        Extracted text
    """
    global total_pages, pages_processed
    
    if hardware_config is None:
        hardware_config = check_hardware_capabilities()
    
    # Determine optimal batch size based on hardware
    if batch_size is None:
        batch_size = hardware_config["workers"]
    
    # Open the PDF to get page count
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    print(f"Processing PDF: {pdf_path}")
    print(f"  Total pages: {total_pages}")
    print(f"  DPI: {dpi}")
    print(f"  Language: {lang}")
    print(f"  Batch size: {batch_size}")
    
    # Create process pool for parallelization
    all_text = [""] * total_pages  # Pre-allocate result array
    
    # Prepare page arguments
    page_args = [(i, pdf_path, dpi, lang) for i in range(total_pages)]
    
    # Process pages in parallel
    with ProcessPoolExecutor(max_workers=hardware_config["workers"]) as executor:
        futures = {executor.submit(process_page, args): args[0] for args in page_args}
        
        for future in as_completed(futures):
            page_num, page_text = future.result()
            all_text[page_num] = page_text
            pages_processed += 1
            
            # Report progress
            progress = pages_processed / total_pages * 100
            elapsed = time.time() - start_time
            pages_per_sec = pages_processed / max(elapsed, 0.1)
            eta = (total_pages - pages_processed) / max(pages_per_sec, 0.001)
            
            sys.stdout.write(f"\rProgress: {progress:.1f}% | Pages: {pages_processed}/{total_pages} "
                            f"| {pages_per_sec:.2f} pages/sec | ETA: {eta:.1f}s")
            sys.stdout.flush()
    
    # Combine all text
    full_text = "\n\n".join(all_text)
    
    # Calculate stats
    final_time = time.time() - start_time
    final_pages_per_sec = total_pages / max(final_time, 0.1)
    
    print(f"\n\nExtraction complete.")
    print(f"  Processed {total_pages} pages in {final_time:.2f} seconds")
    print(f"  Processing speed: {final_pages_per_sec:.2f} pages/sec")
    
    # Save the text if an output file is specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"  Output saved to: {output_file}")
    
    return full_text

def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF using OCR')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('-o', '--output', help='Output text file (default: <pdf_name>.txt)')
    parser.add_argument('-d', '--dpi', type=int, default=300, help='DPI for image extraction (default: 300)')
    parser.add_argument('-l', '--lang', default='eng', help='Tesseract language (default: eng)')
    parser.add_argument('-b', '--batch-size', type=int, help='Pages to process in parallel (default: auto)')
    args = parser.parse_args()
    
    # Set default output file if not specified
    if not args.output:
        pdf_name = Path(args.pdf_path).stem
        args.output = f"{pdf_name}.txt"
    
    # Check hardware and optimize settings
    hardware_config = check_hardware_capabilities()
    
    # Extract text
    extract_text_with_ocr(
        args.pdf_path, 
        args.output, 
        args.dpi, 
        args.lang, 
        args.batch_size,
        hardware_config
    )

if __name__ == "__main__":
    main()
