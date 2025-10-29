#!/usr/bin/env python3
"""
Simple Debug Script for Estate Loading Error
"""

import sys
import os
import json
import traceback

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_estate_loading():
    """Debug estate loading process step by step"""
    print("=" * 60)
    print("ESTATE LOADING DEBUG SCRIPT")
    print("=" * 60)

    try:
        # Step 1: Test Configuration Repository
        print("\nSTEP 1: Testing Configuration Repository")
        print("-" * 40)

        from repositories.configuration_repository import ConfigurationRepository
        config_repo = ConfigurationRepository()

        print(f"Config file path: {config_repo.config_file_path}")
        print(f"Config file exists: {os.path.exists(config_repo.config_file_path)}")

        # Step 2: Test load_estate_config method
        print("\nSTEP 2: Testing load_estate_config")
        print("-" * 40)

        try:
            config = config_repo.load_estate_config()
            print("SUCCESS: load_estate_config() successful")
            print(f"Config type: {type(config)}")
            print(f"Config keys: {list(config.keys())}")

            # Check for any dict values (potential CSV parsing artifacts)
            for estate_name, db_path in config.items():
                print(f"  Estate: {estate_name}")
                print(f"    Type: {type(db_path)}")
                if isinstance(db_path, dict):
                    print(f"    WARNING: db_path is dict instead of string!")
                    print(f"    Keys: {list(db_path.keys())}")
                    if 'tags' in db_path:
                        print(f"    ERROR: Found 'tags' field in dict!")

        except Exception as e:
            print(f"ERROR: load_estate_config() failed: {e}")
            traceback.print_exc()

        # Step 3: Test Configuration Service
        print("\nSTEP 3: Testing Configuration Service")
        print("-" * 40)

        from services.configuration_service import ConfigurationService
        config_service = ConfigurationService()

        try:
            print("Testing get_estate_objects():")
            estate_objects = config_service.get_estate_objects()
            print("SUCCESS: get_estate_objects() successful")
            print(f"Number of estate objects: {len(estate_objects)}")

        except Exception as e:
            print(f"ERROR: Configuration Service failed: {e}")
            traceback.print_exc()

        return True

    except Exception as e:
        print(f"\nCRITICAL ERROR in debug script: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_estate_loading()
    input("\nPress Enter to exit...")