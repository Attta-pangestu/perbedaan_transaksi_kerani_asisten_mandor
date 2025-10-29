#!/usr/bin/env python3
"""
Test Cases untuk Estate Loading Error Validation
Menguji berbagai skenario error dan expected behavior
"""

import unittest
import pandas as pd
import json
import tempfile
from pathlib import Path
from estate_loader_robust import RobustEstateLoader
from estate_loader_best_practices import EstateConfigurationManager, EstateSchema


class TestEstateLoading(unittest.TestCase):
    """Test cases untuk estate loading functionality"""

    def setUp(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.schema = EstateSchema()

    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_csv_loading(self):
        """Test loading valid CSV file"""
        # Create test CSV
        csv_data = """id,name,description,tags,database_path
1,PGE 1A,Primary Estate A,palm_oil,production,/path/to/pge1a.fdb
2,PGE 1B,Primary Estate B,palm_oil,production,/path/to/pge1b.fdb
3,IJL,Special Estate,special,production,/path/to/ijl.fdb"""

        csv_file = self.temp_dir / "valid_estates.csv"
        csv_file.write_text(csv_data)

        # Test loading
        loader = RobustEstateLoader(str(csv_file))
        result = loader.load_estate()

        # Assertions
        self.assertTrue(result.get('success', False))
        self.assertEqual(len(result.get('estates', {})), 3)
        self.assertIn('PGE 1A', result.get('estates', {}))

    def test_missing_tags_column(self):
        """Test CSV missing tags column"""
        csv_data = """id,name,description,database_path
1,PGE 1A,Primary Estate A,/path/to/pge1a.fdb
2,PGE 1B,Primary Estate B,/path/to/pge1b.fdb"""

        csv_file = self.temp_dir / "missing_tags.csv"
        csv_file.write_text(csv_data)

        loader = RobustEstateLoader(str(csv_file))
        result = loader.load_estate()

        # Should still work with empty tags
        self.assertTrue(result.get('success', False))
        estates = result.get('estates', {})
        self.assertEqual(len(estates), 2)

        # Check tags are handled gracefully
        for estate_data in estates.values():
            self.assertIsInstance(estate_data.get('tags', []), list)

    def test_dict_parsing_artifacts(self):
        """Test handling of dict parsing artifacts"""
        # Create JSON with dict artifacts
        json_data = {
            "estates": {
                "PGE 1A": {"path": "/path/to/pge1a.fdb", "tags": {"tags": ["palm_oil", "production"]}},
                "database_settings": {"connection": "localhost"},
                "table_configurations": {"tables": ["table1", "table2"]},
                "PGE 1B": "/path/to/pge1b.fdb"  # Correct string
            }
        }

        json_file = self.temp_dir / "dict_artifacts.json"
        json_file.write_text(json.dumps(json_data, indent=2))

        loader = RobustEstateLoader(str(json_file))
        result = loader.load_estate()

        # Should handle dict artifacts gracefully
        self.assertTrue(result.get('success', False))

        # Check validation results indicate dict columns found
        validation_results = result.get('validation_results', {})
        self.assertIn('dict_columns', validation_results)

    def test_empty_file(self):
        """Test handling of empty file"""
        empty_file = self.temp_dir / "empty.json"
        empty_file.write_text("{}")

        loader = RobustEstateLoader(str(empty_file))
        result = loader.load_estate()

        # Should handle gracefully with fallback response
        self.assertFalse(result.get('success', True))
        self.assertIn('error', result)

    def test_invalid_json_structure(self):
        """Test invalid JSON structure"""
        invalid_json = """{"invalid": "structure", "missing": "estates"}"""
        json_file = self.temp_dir / "invalid.json"
        json_file.write_text(invalid_json)

        loader = RobustEstateLoader(str(json_file))
        result = loader.load_estate()

        # Should handle with appropriate error
        self.assertFalse(result.get('success', True))

    def test_excel_file_loading(self):
        """Test Excel file loading"""
        # Create test Excel data
        data = {
            'id': [1, 2],
            'name': ['PGE 1A', 'PGE 1B'],
            'description': ['Estate A', 'Estate B'],
            'tags': ['palm_oil', 'palm_oil'],
            'database_path': ['/path/a.fdb', '/path/b.fdb']
        }

        df = pd.DataFrame(data)
        excel_file = self.temp_dir / "test_estates.xlsx"
        df.to_excel(excel_file, index=False)

        loader = RobustEstateLoader(str(excel_file))
        result = loader.load_estate()

        self.assertTrue(result.get('success', False))
        self.assertEqual(len(result.get('estates', {})), 2)

    def test_configuration_manager_valid_config(self):
        """Test EstateConfigurationManager with valid config"""
        config_data = {
            "PGE 1A": "/path/to/pge1a.fdb",
            "PGE 1B": "/path/to/pge1b.fdb",
            "IJL": "/path/to/ijl.fdb"
        }

        config_file = self.temp_dir / "valid_config.json"
        config_file.write_text(json.dumps(config_data, indent=2))

        manager = EstateConfigurationManager(str(config_file))
        success = manager.load_configuration()

        self.assertTrue(success)
        self.assertTrue(manager.validation_results.get('valid', False))

        configs = manager.get_estate_configurations()
        self.assertEqual(len(configs), 3)
        self.assertIn("PGE 1A", configs)

    def test_configuration_manager_mixed_types(self):
        """Test configuration manager with mixed data types"""
        config_data = {
            "PGE 1A": "/path/to/pge1a.fdb",  # String (correct)
            "invalid_data": {"tags": ["tag1"]},  # Dict (should be ignored)
            "PGE 1B": "",  # Empty string (should be ignored)
            "IJL": None  # None (should be ignored)
        }

        config_file = self.temp_dir / "mixed_config.json"
        config_file.write_text(json.dumps(config_data, indent=2))

        manager = EstateConfigurationManager(str(config_file))
        success = manager.load_configuration()

        self.assertTrue(success)
        configs = manager.get_estate_configurations()

        # Should only load valid string configurations
        self.assertEqual(len(configs), 1)
        self.assertIn("PGE 1A", configs)

    def test_specific_estate_loading(self):
        """Test loading specific estate"""
        csv_data = """id,name,description,tags,database_path
1,PGE 1A,Primary Estate A,palm_oil,/path/to/pge1a.fdb
2,PGE 1B,Primary Estate B,palm_oil,/path/to/pge1b.fdb"""

        csv_file = self.temp_dir / "specific_test.csv"
        csv_file.write_text(csv_data)

        loader = RobustEstateLoader(str(csv_file))
        result = loader.load_estate("PGE 1A")

        self.assertTrue(result.get('success', False))
        self.assertEqual(result.get('name'), 'PGE 1A')

        # Test non-existent estate
        result = loader.load_estate("NonExistent")
        self.assertFalse(result.get('success', True))

    def test_debug_structure_functionality(self):
        """Test debug structure functionality"""
        csv_data = """id,name,description,tags,database_path
1,PGE 1A,Primary Estate A,palm_oil,/path/to/pge1a.fdb"""

        csv_file = self.temp_dir / "debug_test.csv"
        csv_file.write_text(csv_data)

        loader = RobustEstateLoader(str(csv_file))

        # This should not raise an exception
        loader.debug_print_structure()


def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("=" * 60)
    print("COMPREHENSIVE ESTATE LOADING TEST SUITE")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEstateLoading)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  ❌ {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  ❌ {test}: {traceback.split('Exception:')[-1].strip()}")

    return result.wasSuccessful()


def demonstrate_error_scenarios():
    """Demonstrate various error scenarios and their handling"""
    print("\n" + "=" * 60)
    print("ERROR SCENARIO DEMONSTRATIONS")
    print("=" * 60)

    temp_dir = Path(tempfile.mkdtemp())

    try:
        scenarios = [
            {
                'name': 'Valid Configuration',
                'data': {"PGE 1A": "/path/to/pge1a.fdb", "PGE 1B": "/path/to/pge1b.fdb"},
                'expected_success': True
            },
            {
                'name': 'Dict Parsing Artifacts',
                'data': {
                    "PGE 1A": "/path/to/pge1a.fdb",
                    "settings": {"tags": ["tag1", "tag2"]},
                    "config": {"database": "value"}
                },
                'expected_success': True  # Should handle gracefully
            },
            {
                'name': 'Empty Configuration',
                'data': {},
                'expected_success': True  # Should handle gracefully
            },
            {
                'name': 'Mixed Valid/Invalid Data',
                'data': {
                    "PGE 1A": "/path/to/pge1a.fdb",  # Valid
                    "Invalid": {"tags": ["tag1"]},    # Invalid dict
                    "PGE 1B": "",                      # Empty
                    "IJL": None                        # None
                },
                'expected_success': True
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\nScenario {i}: {scenario['name']}")
            print("-" * 40)

            # Create test file
            config_file = temp_dir / f"scenario_{i}.json"
            config_file.write_text(json.dumps(scenario['data'], indent=2))

            # Test with both loaders
            try:
                # Test RobustEstateLoader
                print("Testing RobustEstateLoader...")
                loader = RobustEstateLoader(str(config_file))
                result = loader.load_estate()
                print(f"  Result: {'✅ SUCCESS' if result.get('success') else '❌ FAILED'}")
                if not result.get('success'):
                    print(f"  Error: {result.get('error', 'Unknown')}")

                # Test EstateConfigurationManager
                print("Testing EstateConfigurationManager...")
                manager = EstateConfigurationManager(str(config_file))
                success = manager.load_configuration()
                print(f"  Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
                print(f"  Valid estates: {len(manager.get_estate_configurations())}")

            except Exception as e:
                print(f"  ❌ EXCEPTION: {e}")

    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run comprehensive tests
    success = run_comprehensive_test()

    # Demonstrate error scenarios
    demonstrate_error_scenarios()

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    if success:
        print("✅ All tests passed! The estate loading system is robust.")
    else:
        print("❌ Some tests failed. Please review the implementation.")

    print("\nKey Features Implemented:")
    print("  • Dynamic column validation")
    print("  • CSV/Excel/JSON format support")
    print("  • Dict parsing artifact detection and fixing")
    print("  • Missing column handling with defaults")
    print("  • Comprehensive error reporting")
    print("  • Schema validation")
    print("  • Backup and recovery mechanisms")
    print("  • Debug and diagnostic tools")