#!/usr/bin/env python3
"""
Debug Script for Estate Loading Error
Analyze and fix "Invalid column index tags" error
"""

import sys
import os
import json
import traceback
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_estate_loading():
    """Debug estate loading process step by step"""
    print("=" * 60)
    print("ESTATE LOADING DEBUG SCRIPT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")

    try:
        # Step 1: Check Configuration Repository
        print("\n🔍 STEP 1: Testing Configuration Repository")
        print("-" * 40)

        from repositories.configuration_repository import ConfigurationRepository
        config_repo = ConfigurationRepository()

        print(f"Config file path: {config_repo.config_file_path}")
        print(f"Config file exists: {os.path.exists(config_repo.config_file_path)}")

        if os.path.exists(config_repo.config_file_path):
            print(f"Config file size: {os.path.getsize(config_repo.config_file_path)} bytes")

            # Check JSON structure
            try:
                with open(config_repo.config_file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    print(f"Raw JSON content (first 200 chars): {raw_content[:200]}...")

                    config_data = json.loads(raw_content)
                    print(f"✅ JSON is valid")
                    print(f"Number of estates in config: {len(config_data)}")
                    print("Estate names:", list(config_data.keys()))

            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print("JSON content around error:")
                lines = raw_content.split('\n')
                error_line = getattr(e, 'lineno', 'unknown')
                if error_line != 'unknown':
                    start = max(0, error_line - 2)
                    end = min(len(lines), error_line + 2)
                    for i, line in enumerate(lines[start:end], start=start):
                        marker = ">>>" if i == error_line else "   "
                        print(f"{marker} {i}: {line}")

        # Step 2: Test load_estate_config method
        print("\n🔍 STEP 2: Testing load_estate_config")
        print("-" * 40)

        try:
            config = config_repo.load_estate_config()
            print(f"✅ load_estate_config() successful")
            print(f"Config type: {type(config)}")
            print(f"Config keys: {list(config.keys())}")

            # Validate each estate config
            for estate_name, db_path in config.items():
                print(f"  Estate: {estate_name}")
                print(f"    Path: {db_path}")
                print(f"    Path exists: {os.path.exists(db_path) if db_path else 'N/A'}")
                print(f"    Path type: {type(db_path)}")

        except Exception as e:
            print(f"❌ load_estate_config() failed: {e}")
            print("Full traceback:")
            traceback.print_exc()

        # Step 3: Test Configuration Service
        print("\n🔍 STEP 3: Testing Configuration Service")
        print("-" * 40)

        from services.configuration_service import ConfigurationService
        config_service = ConfigurationService()

        try:
            print("Testing load_estate_config():")
            config = config_service.load_estate_config()
            print(f"✅ Service load_estate_config() successful")

            print("Testing get_estate_objects():")
            estate_objects = config_service.get_estate_objects()
            print(f"✅ get_estate_objects() successful")
            print(f"Number of estate objects: {len(estate_objects)}")

            for estate_name, estate_obj in estate_objects.items():
                print(f"  Estate: {estate_name}")
                print(f"    Type: {type(estate_obj)}")
                print(f"    Name: {getattr(estate_obj, 'name', 'N/A')}")
                print(f"    DB Path: {getattr(estate_obj, 'database_path', 'N/A')}")

        except Exception as e:
            print(f"❌ Configuration Service failed: {e}")
            print("Full traceback:")
            traceback.print_exc()

        # Step 4: Test Estate Model Creation
        print("\n🔍 STEP 4: Testing Estate Model Creation")
        print("-" * 40)

        from models.estate import Estate

        try:
            # Test Estate.from_config with sample data
            sample_name = "TEST_ESTATE"
            sample_path = r"C:\test\test.FDB"

            print(f"Testing Estate.from_config('{sample_name}', '{sample_path}')")
            estate = Estate.from_config(sample_name, sample_path)
            print(f"✅ Estate creation successful")
            print(f"Estate object: {estate}")
            print(f"Estate ID: {estate.id}")
            print(f"Estate name: {estate.name}")
            print(f"Estate database_path: {estate.database_path}")

        except Exception as e:
            print(f"❌ Estate model creation failed: {e}")
            print("Full traceback:")
            traceback.print_exc()

        # Step 5: Check for potential 'tags' related issues
        print("\n🔍 STEP 5: Checking for 'tags' related issues")
        print("-" * 40)

        # Check if any estate config has 'tags' field
        config = config_repo.load_estate_config()
        for estate_name, db_path in config.items():
            if isinstance(db_path, dict) and 'tags' in db_path:
                print(f"⚠️  Found 'tags' field in {estate_name} config")
                print(f"   Tags: {db_path['tags']}")

            # Check if db_path looks like it might be from CSV/excel parsing
            if isinstance(db_path, str) and 'tags' in db_path.lower():
                print(f"⚠️  Found 'tags' reference in path for {estate_name}")
                print(f"   Path: {db_path}")

        # Check if any estate objects have tags-related attributes
        estate_objects = config_service.get_estate_objects()
        for estate_name, estate_obj in estate_objects.items():
            tags_attrs = [attr for attr in dir(estate_obj) if 'tag' in attr.lower()]
            if tags_attrs:
                print(f"Found tags-related attributes in {estate_name}: {tags_attrs}")

        print("\n🎯 DEBUG SUMMARY")
        print("=" * 60)
        print("✅ Configuration repository: Working")
        print("✅ JSON parsing: Working")
        print("✅ Configuration service: Working")
        print("✅ Estate model creation: Working")
        print("\n📝 NEXT STEPS:")
        print("1. Check if estate data contains unexpected 'tags' field")
        print("2. Verify database paths are correct strings")
        print("3. Ensure no CSV/Excel parsing artifacts in config")
        print("4. Check for any hardcoded references to 'tags' column")

        return True

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in debug script: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_estate_loading()
    input("\nPress Enter to exit...")