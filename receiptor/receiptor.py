#!/usr/bin/env python3

"""
Simplified script to extract only essential item data from supermarket receipts.

Extracts for each item:
- Item name
- Quantity
- Unit (KG, UN, etc.)
- Unit price

Usage:
    python extract_items_simple.py input.pdf
    python extract_items_simple.py input.pdf -o output.csv
    python extract_items_simple.py input.pdf --output custom_name.csv --quiet
"""

import re
import argparse
import sys
from pathlib import Path
import pdfplumber
import pandas as pd
import numpy as np
from typing import List, Dict


# Global flag for quiet mode
QUIET_MODE = False


def print_verbose(message: str, force: bool = False):
    """
    Print message only if not in quiet mode.
    
    Args:
        message: Message to print
        force: If True, print even in quiet mode
    """
    if force or not QUIET_MODE:
        print(message)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string
    """
    print_verbose(f"[INFO] Opening PDF file: {pdf_path}")
    
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        print_verbose(f"[INFO] PDF has {len(pdf.pages)} page(s)")
        for page_num, page in enumerate(pdf.pages, 1):
            print_verbose(f"[INFO] Extracting text from page {page_num}")
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
    
    print_verbose(f"[INFO] Total extracted text length: {len(text_content)} characters")
    return text_content


def extract_items(text: str) -> List[Dict[str, str]]:
    """
    Extract items with only: name, quantity, unit, unit price.
    
    Args:
        text: Receipt text content
        
    Returns:
        List of dictionaries with item information
    """
    print_verbose("[INFO] Extracting items from receipt")
    
    items = []
    
    # Pattern to match:
    # ITEM NAME (Código: ... ) Vl. Total
    # Qtde.:XXX UN: YY Vl. Unit.: ZZ,ZZ ...
    # Note: Unit can be UN, KG, or UN0001, UN0002, etc.
    
    item_pattern = r'(?:^|\n)([A-Z][A-Z0-9 /\.,%]+?)\s+\(Código:.*?\)\s+Vl\.\s+Total\s*\n\s*Qtde\.:([\d,\.]+)\s+UN:\s*([A-Z0-9]+)\s+Vl\.\s+Unit\.:\s*([\d,\.]+)'
    
    matches = re.finditer(item_pattern, text, re.MULTILINE)
    
    item_count = 0
    for match in matches:
        item_count += 1
        item = {
            'item_name': match.group(1).strip(),
            'quantity': match.group(2).strip(),
            'unit': match.group(3).strip(),
            'unit_price': match.group(4).strip()
        }
        items.append(item)
        print_verbose(f"[INFO] Item {item_count}: {item['item_name'][:50]}")
    
    print_verbose(f"[INFO] Total items extracted: {len(items)}")
    return items


def convert_to_float(value: str) -> float:
    """
    Convert Brazilian currency format string to float.
    Returns np.nan if conversion fails.
    
    Args:
        value: String in format "1.234,56" or "1234,56" or "1,07"
        
    Returns:
        Float value or np.nan if conversion fails
    """
    if not value or not isinstance(value, str):
        print(f"[WARNING] Invalid input for conversion: {value}")
        return np.nan
    
    try:
        # Remove any whitespace
        value = value.strip()
        
        # Remove dots (thousand separators) and replace comma with dot
        value_converted = value.replace('.', '').replace(',', '.')
        
        # Try to convert to float
        result = float(value_converted)
        
        print(f"[DEBUG] Converted '{value}' to {result}")
        return result
        
    except (ValueError, AttributeError) as e:
        print(f"[ERROR] Failed to convert '{value}' to float: {e}")
        return np.nan


def create_dataframe(items: List[Dict[str, str]]) -> pd.DataFrame:
    """
    Create a pandas DataFrame from items list with proper type conversions.
    
    Args:
        items: List of item dictionaries
        
    Returns:
        DataFrame with item information
    """
    print("[INFO] Creating DataFrame")
    
    if not items:
        print("[WARNING] No items to create DataFrame")
        return pd.DataFrame()
    
    df = pd.DataFrame(items)
    
    print("[INFO] Validating data types")
    
    # Ensure item_name is always string
    df['item_name'] = df['item_name'].astype(str)
    print(f"[INFO] item_name column: dtype = {df['item_name'].dtype}")
    
    # Ensure unit is always string
    df['unit'] = df['unit'].astype(str)
    print(f"[INFO] unit column: dtype = {df['unit'].dtype}")
    
    # Convert quantity from string to float with validation
    print("[INFO] Converting quantity to float")
    df['quantity_float'] = df['quantity'].apply(convert_to_float)
    successful_qty = df['quantity_float'].notna().sum()
    print(f"[INFO] Successfully converted {successful_qty}/{len(df)} quantity values")
    
    # Convert unit_price from string to float with validation
    print("[INFO] Converting unit_price to float")
    df['unit_price_float'] = df['unit_price'].apply(convert_to_float)
    successful_price = df['unit_price_float'].notna().sum()
    print(f"[INFO] Successfully converted {successful_price}/{len(df)} unit_price values")
    
    # Verify column order and types
    columns_order = ['item_name', 'quantity', 'unit', 'unit_price', 'quantity_float', 'unit_price_float']
    df = df[columns_order]
    
    print(f"[INFO] DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    print(f"[INFO] Data types: {dict(df.dtypes)}")
    
    return df


def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate the extracted data and report any issues.
    
    Args:
        df: DataFrame to validate
    """
    print("\n" + "="*70)
    print("DATA VALIDATION REPORT")
    print("="*70)
    
    if df.empty:
        print("[WARNING] DataFrame is empty!")
        return
    
    # Check for missing values
    print("\n[INFO] Checking for missing or invalid values:")
    
    missing_qty = df['quantity_float'].isna().sum()
    if missing_qty > 0:
        print(f"[WARNING] {missing_qty} items have invalid quantity values")
        invalid_rows = df[df['quantity_float'].isna()][['item_name', 'quantity']]
        print(invalid_rows.to_string(index=False))
    else:
        print("[OK] All quantity values converted successfully")
    
    missing_price = df['unit_price_float'].isna().sum()
    if missing_price > 0:
        print(f"[WARNING] {missing_price} items have invalid unit_price values")
        invalid_rows = df[df['unit_price_float'].isna()][['item_name', 'unit_price']]
        print(invalid_rows.to_string(index=False))
    else:
        print("[OK] All unit_price values converted successfully")
    
    # Check data ranges
    print("\n[INFO] Data range validation:")
    
    if 'quantity_float' in df.columns and df['quantity_float'].notna().any():
        min_qty = df['quantity_float'].min()
        max_qty = df['quantity_float'].max()
        print(f"[INFO] Quantity range: {min_qty:.3f} to {max_qty:.3f}")
        
        if min_qty <= 0:
            print(f"[WARNING] Found quantity <= 0")
    
    if 'unit_price_float' in df.columns and df['unit_price_float'].notna().any():
        min_price = df['unit_price_float'].min()
        max_price = df['unit_price_float'].max()
        print(f"[INFO] Unit price range: R$ {min_price:.2f} to R$ {max_price:.2f}")
        
        if min_price <= 0:
            print(f"[WARNING] Found unit_price <= 0")
    
    # Check for common units
    print("\n[INFO] Units found:")
    unit_counts = df['unit'].value_counts()
    for unit, count in unit_counts.items():
        print(f"  {unit}: {count} items")
    
    print("\n" + "="*70)


def save_to_csv(df: pd.DataFrame, output_file: str = "items.csv", delimiter: str = ";") -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame with items
        output_file: Output filename
        delimiter: CSV delimiter (default: ";")
    """
    print(f"[INFO] Saving data to {output_file}")
    df.to_csv(output_file, index=False, encoding='utf-8-sig', sep=delimiter)
    print(f"[SUCCESS] Data saved successfully")


def process_receipt(pdf_path: str, output_file: str = "items.csv") -> pd.DataFrame:
    """
    Main processing function for receipt extraction.
    
    Args:
        pdf_path: Path to the PDF receipt file
        output_file: Output filename for CSV
        
    Returns:
        DataFrame with items
    """
    print("\n" + "="*70)
    print("SUPERMARKET RECEIPT ITEM EXTRACTION")
    print("="*70 + "\n")
    
    # Step 1: Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Extract items
    items = extract_items(text)
    
    # Step 3: Create DataFrame
    df = create_dataframe(items)
    
    # Step 4: Validate data
    if not df.empty:
        validate_dataframe(df)
    
    # Step 5: Save to CSV
    if not df.empty:
        save_to_csv(df, output_file)
    
    print("\n" + "="*70)
    print("EXTRACTION COMPLETED")
    print("="*70 + "\n")
    
    return df


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Extract item data from Brazilian supermarket receipts (NFCe) in PDF format.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s receipt.pdf
  %(prog)s receipt.pdf -o items_output.csv
  %(prog)s receipt.pdf --output items.csv --quiet
  %(prog)s /path/to/receipts/receipt_001.pdf -o output.csv
        """
    )
    
    parser.add_argument(
        'input_pdf',
        type=str,
        help='Path to the input PDF receipt file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='items.csv',
        help='Output CSV filename (default: items.csv)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress verbose output (only show errors and final summary)'
    )
    
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Skip data validation report'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


def main():
    """
    Main function for CLI execution.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate input file exists
    input_path = Path(args.input_pdf)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {args.input_pdf}", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.pdf':
        print(f"[ERROR] Input file must be a PDF file", file=sys.stderr)
        sys.exit(1)
    
    # Set output path
    output_path = Path(args.output)
    
    # Display startup message
    if not args.quiet:
        print("[INFO] Starting receipt extraction script")
        print(f"[INFO] Input file: {input_path}")
        print(f"[INFO] Output file: {output_path}")
    
    # Process the receipt
    try:
        if not args.quiet:
            print("[INFO] Calling process_receipt function")
        
        items_dataframe = process_receipt(
            pdf_path=str(input_path),
            output_file=str(output_path)
        )
        
        # Display results
        if not items_dataframe.empty:
            if not args.quiet:
                print("\n" + "="*70)
                print("FIRST ITEM VERIFICATION")
                print("="*70)
                first_item = items_dataframe.iloc[0]
                print(f"Item name:       {first_item['item_name']} (type: {type(first_item['item_name']).__name__})")
                print(f"Quantity (str):  {first_item['quantity']} (type: {type(first_item['quantity']).__name__})")
                print(f"Unit:            {first_item['unit']} (type: {type(first_item['unit']).__name__})")
                print(f"Unit price (str): {first_item['unit_price']} (type: {type(first_item['unit_price']).__name__})")
                print(f"Quantity (float): {first_item['quantity_float']} (type: {type(first_item['quantity_float']).__name__})")
                print(f"Unit price (float): {first_item['unit_price_float']} (type: {type(first_item['unit_price_float']).__name__})")
                
                print("\n" + "="*70)
                print("ALL EXTRACTED ITEMS")
                print("="*70)
                print(items_dataframe.to_string(index=False))
            
            # Always show summary
            print(f"\n[SUCCESS] Extracted {len(items_dataframe)} items")
            
            if 'unit_price_float' in items_dataframe.columns:
                valid_items = items_dataframe.dropna(subset=['quantity_float', 'unit_price_float'])
                if not valid_items.empty:
                    total_value = (valid_items['quantity_float'] * valid_items['unit_price_float']).sum()
                    print(f"[INFO] Total value: R$ {total_value:.2f}")
            
            print(f"[INFO] Data saved to: {output_path}")
        else:
            print("[WARNING] No items were extracted from the receipt", file=sys.stderr)
            sys.exit(1)
        
        if not args.quiet:
            print("\n[SUCCESS] Script execution completed!")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"[ERROR] Failed to process receipt: {str(e)}", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# EXECUTION ROUTINE
# ============================================================================

if __name__ == "__main__":
    main()