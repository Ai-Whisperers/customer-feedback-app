"""
Test script for parser integration with pipeline.
"""

import os
import sys
import pandas as pd
import tempfile
from pathlib import Path

sys.path.append('.')

from app.core.file_parser import get_parser, BaseFileParser
from app.core.flexible_parser import FlexibleFileParser
from app.services.analysis_service import load_and_validate_file


def create_test_files():
    """Create test CSV and Excel files."""

    # Test data with different column configurations
    test_cases = []

    # Case 1: Standard columns
    df1 = pd.DataFrame({
        'Nota': [9, 8, 5, 10, 3, 7],
        'Comentario Final': [
            'Excelente servicio',
            'Muy buen producto',
            'Regular experiencia',
            'Increíble atención',
            'Mal servicio',
            'Buena calidad'
        ]
    })

    # Case 2: With NPS column (numeric)
    df2 = pd.DataFrame({
        'Nota': [9, 8, 5, 10, 3, 7],
        'Comentario Final': [
            'Great service',
            'Good product',
            'Average experience',
            'Amazing support',
            'Poor service',
            'Decent quality'
        ],
        'NPS': [75, 50, -20, 85, -50, 25]
    })

    # Case 3: With NPS column (categories)
    df3 = pd.DataFrame({
        'Nota': [9, 8, 5, 10, 3, 7],
        'Comentario Final': [
            'Servicio excelente',
            'Producto muy bueno',
            'Experiencia regular',
            'Soporte increíble',
            'Servicio deficiente',
            'Calidad decente'
        ],
        'NPS': ['promoter', 'passive', 'detractor', 'promoter', 'detractor', 'passive']
    })

    # Case 4: Alternative column names (for flexible parser)
    df4 = pd.DataFrame({
        'Rating': [9, 8, 5, 10, 3, 7],
        'Feedback': [
            'Excellent service',
            'Very good product',
            'Regular experience',
            'Incredible attention',
            'Bad service',
            'Good quality'
        ]
    })

    # Save test files
    files = []

    # CSV files
    csv_path1 = Path(tempfile.gettempdir()) / "test_standard.csv"
    df1.to_csv(csv_path1, index=False)
    files.append(("standard_csv", csv_path1, df1))

    csv_path2 = Path(tempfile.gettempdir()) / "test_with_nps.csv"
    df2.to_csv(csv_path2, index=False)
    files.append(("with_nps_csv", csv_path2, df2))

    # Excel files
    excel_path1 = Path(tempfile.gettempdir()) / "test_standard.xlsx"
    df1.to_excel(excel_path1, index=False)
    files.append(("standard_excel", excel_path1, df1))

    excel_path3 = Path(tempfile.gettempdir()) / "test_nps_categories.xlsx"
    df3.to_excel(excel_path3, index=False)
    files.append(("nps_categories_excel", excel_path3, df3))

    excel_path4 = Path(tempfile.gettempdir()) / "test_alternative_cols.xlsx"
    df4.to_excel(excel_path4, index=False)
    files.append(("alternative_cols", excel_path4, df4))

    return files


def test_base_parser(files):
    """Test base parser functionality."""
    print("\n" + "="*60)
    print("Testing Base Parser")
    print("="*60)

    parser = BaseFileParser()

    for name, file_path, original_df in files:
        if "alternative" in name:
            continue  # Skip alternative columns for base parser

        print(f"\nTest case: {name}")
        print("-"*40)

        try:
            df, metadata = parser.parse_file(file_path)

            print(f"✓ File parsed successfully")
            print(f"  Total rows: {metadata['total_rows']}")
            print(f"  Columns: {metadata['columns']}")
            print(f"  Has NPS: {metadata['has_nps_column']}")

            # Validate data quality
            quality = parser.validate_data_quality(df)
            print(f"  Valid rows: {quality['valid_rows']}")
            print(f"  Issues: {quality.get('issues', 'None')}")

        except Exception as e:
            print(f"✗ Error: {str(e)}")


def test_flexible_parser(files):
    """Test flexible parser functionality."""
    print("\n" + "="*60)
    print("Testing Flexible Parser")
    print("="*60)

    parser = FlexibleFileParser()

    for name, file_path, original_df in files:
        print(f"\nTest case: {name}")
        print("-"*40)

        try:
            df, metadata = parser.parse_file(file_path)

            print(f"✓ File parsed successfully")
            print(f"  Original columns: {metadata['original_columns']}")
            print(f"  Mapped columns: {metadata['mapped_columns']}")
            print(f"  Has NPS: {metadata['has_nps_column']}")
            print(f"  NPS strategy: {metadata.get('nps_strategy', 'N/A')}")

            # Validate data quality
            quality = parser.validate_data_quality_flexible(df)
            print(f"  Valid rows: {quality['valid_rows']}")

            if 'text_quality' in quality:
                print(f"  Language: {quality['text_quality']['language_detected']}")

        except Exception as e:
            print(f"✗ Error: {str(e)}")


def test_service_integration(files):
    """Test integration with analysis service."""
    print("\n" + "="*60)
    print("Testing Service Integration")
    print("="*60)

    for name, file_path, original_df in files:
        if "alternative" in name:
            continue  # Skip alternative columns for service

        print(f"\nTest case: {name}")
        print("-"*40)

        try:
            df = load_and_validate_file(str(file_path))

            print(f"✓ Service loaded file successfully")
            print(f"  Loaded rows: {len(df)}")
            print(f"  Columns: {list(df.columns)}")

            # Check NPS handling
            if 'NPS' in df.columns:
                print(f"  NPS column present: {df['NPS'].dtype}")
            else:
                print(f"  NPS will be calculated from Nota")

        except Exception as e:
            print(f"✗ Error: {str(e)}")


def test_parser_modes():
    """Test parser mode switching."""
    print("\n" + "="*60)
    print("Testing Parser Mode Switching")
    print("="*60)

    # Test default mode
    os.environ['FILE_PARSER_MODE'] = 'base'
    parser1 = get_parser()
    print(f"Mode 'base': {type(parser1).__name__}")

    # Test flexible mode
    os.environ['FILE_PARSER_MODE'] = 'flexible'
    parser2 = get_parser()
    print(f"Mode 'flexible': {type(parser2).__name__}")

    # Test explicit mode
    parser3 = get_parser(mode='flexible')
    print(f"Explicit flexible: {type(parser3).__name__}")


def main():
    """Run all tests."""
    print("\nParser Integration Test Suite")
    print("="*60)

    # Create test files
    print("Creating test files...")
    files = create_test_files()
    print(f"Created {len(files)} test files")

    # Run tests
    test_base_parser(files)
    test_flexible_parser(files)
    test_service_integration(files)
    test_parser_modes()

    # Cleanup
    print("\n" + "="*60)
    print("Cleaning up test files...")
    for _, file_path, _ in files:
        try:
            file_path.unlink()
            print(f"  Removed: {file_path.name}")
        except:
            pass

    print("\n✓ All tests completed!")


if __name__ == "__main__":
    main()