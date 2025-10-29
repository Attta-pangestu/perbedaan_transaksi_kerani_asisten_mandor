#!/usr/bin/env python3
"""
Debugging Snippets untuk Estate Loading Error
Cepat identifikasi dan lokasi error
"""

import pandas as pd
import json
from pathlib import Path


def debug_file_structure(file_path: str):
    """
    Debug struktur file dan lokasi error
    """
    print("=" * 60)
    print(f"DEBUGGING FILE: {file_path}")
    print("=" * 60)

    try:
        file_path = Path(file_path)
        print(f"File exists: {file_path.exists()}")
        print(f"File size: {file_path.stat().st_size} bytes")

        # Try different loading methods
        print("\n--- Method 1: pandas.read_csv ---")
        try:
            df_csv = pd.read_csv(file_path)
            print(f"✅ CSV loaded: Shape {df_csv.shape}")
            print(f"Columns: {list(df_csv.columns)}")
            print(f"Data types: {dict(df_csv.dtypes)}")
            print("First 3 rows:")
            print(df_csv.head(3))

            # Check for 'tags' column specifically
            if 'tags' in df_csv.columns:
                print(f"\n--- TAGS COLUMN ANALYSIS ---")
                print(f"Tags column type: {df_csv['tags'].dtype}")
                print(f"Sample tags values: {df_csv['tags'].dropna().head(5).tolist()}")

                # Check for dict values
                dict_count = sum(1 for val in df_csv['tags'].dropna() if isinstance(val, dict))
                if dict_count > 0:
                    print(f"⚠️  FOUND {dict_count} DICT VALUES in tags column!")

            return df_csv

        except Exception as e:
            print(f"❌ CSV failed: {e}")

        print("\n--- Method 2: pandas.read_excel ---")
        try:
            df_excel = pd.read_excel(file_path)
            print(f"✅ Excel loaded: Shape {df_excel.shape}")
            print(f"Columns: {list(df_excel.columns)}")
            return df_excel

        except Exception as e:
            print(f"❌ Excel failed: {e}")

        print("\n--- Method 3: JSON loading ---")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ JSON loaded: Type {type(data)}")

            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                # Check for dict values
                for key, value in data.items():
                    if isinstance(value, dict):
                        print(f"⚠️  FOUND DICT in key '{key}': {list(value.keys())}")

            return pd.DataFrame(data if isinstance(data, list) else [data])

        except Exception as e:
            print(f"❌ JSON failed: {e}")

    except Exception as e:
        print(f"❌ Complete failure: {e}")
        import traceback
        traceback.print_exc()
        return None


def find_tags_column_issues(df: pd.DataFrame):
    """
    Cari spesifik masalah di kolom tags
    """
    print("\n" + "=" * 40)
    print("TAGS COLUMN ANALYSIS")
    print("=" * 40)

    if 'tags' not in df.columns:
        print("❌ 'tags' column NOT FOUND")
        print(f"Available columns: {list(df.columns)}")

        # Suggest alternatives
        similar_columns = [col for col in df.columns if 'tag' in col.lower()]
        if similar_columns:
            print(f"Similar columns found: {similar_columns}")
        return False

    print("✅ 'tags' column found")

    # Analyze tags column
    tags_col = df['tags']
    print(f"Data type: {tags_col.dtype}")
    print(f"Non-null values: {tags_col.count()}/{len(tags_col)}")

    # Sample values
    print(f"\nSample values (first 10):")
    sample_values = tags_col.dropna().head(10).tolist()
    for i, val in enumerate(sample_values, 1):
        print(f"  {i}. {val} (type: {type(val).__name__})")

    # Check for problematic values
    dict_values = [val for val in tags_col.dropna() if isinstance(val, dict)]
    if dict_values:
        print(f"\n⚠️  FOUND {len(dict_values)} DICT VALUES:")
        for i, val in enumerate(dict_values[:5], 1):
            print(f"  {i}. {val}")

    # Check for string representations of dicts
    str_dict_values = []
    for val in tags_col.dropna():
        if isinstance(val, str) and val.startswith('{') and val.endswith('}'):
            str_dict_values.append(val)

    if str_dict_values:
        print(f"\n⚠️  FOUND {len(str_dict_values)} STRING DICT VALUES:")
        for i, val in enumerate(str_dict_values[:5], 1):
            print(f"  {i}. {val}")

    return True


def quick_fix_suggestions(df: pd.DataFrame):
    """
    Berikan saran perbaikan cepat
    """
    print("\n" + "=" * 40)
    print("QUICK FIX SUGGESTIONS")
    print("=" * 40)

    suggestions = []

    # Check missing columns
    expected_cols = ['id', 'name', 'description', 'tags', 'database_path']
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        suggestions.append(f"Add missing columns: {missing_cols}")

    # Check dict columns
    dict_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            dict_count = sum(1 for val in df[col].dropna() if isinstance(val, dict))
            if dict_count > 0:
                dict_cols.append(col)

    if dict_cols:
        suggestions.append(f"Fix dict-type columns: {dict_cols}")

    # Check empty data
    if df.empty:
        suggestions.append("File is empty or no data loaded")

    if suggestions:
        print("Issues found:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    else:
        print("✅ No obvious issues found")


# Main debugging function
def debug_estate_loading_error(file_path: str):
    """
    Comprehensive debugging untuk estate loading error
    """
    print("ESTATE LOADING ERROR DEBUGGER")
    print("=" * 60)

    # Step 1: Debug file structure
    df = debug_file_structure(file_path)

    if df is None:
        print("\n❌ Cannot load file - check file path and format")
        return

    # Step 2: Analyze tags column
    find_tags_column_issues(df)

    # Step 3: Quick fix suggestions
    quick_fix_suggestions(df)

    # Step 4: Test robust loading
    print("\n" + "=" * 40)
    print("TESTING ROBUST LOADING")
    print("=" * 40)

    try:
        from estate_loader_robust import RobustEstateLoader
        loader = RobustEstateLoader(file_path)
        result = loader.load_estate()

        print(f"Robust loading result:")
        print(f"  Success: {result.get('success', False)}")
        if result.get('success'):
            estates = result.get('estates', {})
            print(f"  Estates loaded: {len(estates)}")
            if estates:
                first_estate = list(estates.keys())[0]
                print(f"  Sample estate: {first_estate}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"Robust loading failed: {e}")


if __name__ == "__main__":
    # Test dengan configuration file
    config_file = "config/database_paths.json"

    print("Starting estate loading error debugging...")
    debug_estate_loading_error(config_file)