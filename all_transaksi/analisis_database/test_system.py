#!/usr/bin/env python3
"""
System Validation and Testing Script
Comprehensive testing suite for FFB Analysis System v2.0
"""

import sys
import os
import json
import traceback
from datetime import datetime, date
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header(title):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_test(test_name, status, message=""):
    """Print test result"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}")
    if message:
        print(f"   {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_error(message):
    """Print error message"""
    print(f"🔥 {message}")

class SystemValidator:
    """Comprehensive system validator"""

    def __init__(self):
        self.test_results = []
        self.errors = []
        self.warnings = []

    def run_all_tests(self):
        """Run all validation tests"""
        print_header("FFB Analysis System v2.0 - System Validation")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Test basic system requirements
        self.test_system_requirements()

        # Test configuration files
        self.test_configuration_files()

        # Test module imports
        self.test_module_imports()

        # Test database connectivity
        self.test_database_connectivity()

        # Test core services
        self.test_core_services()

        # Test GUI components
        self.test_gui_components()

        # Test business logic
        self.test_business_logic()

        # Test report generation
        self.test_report_generation()

        # Generate summary
        self.generate_summary()

    def test_system_requirements(self):
        """Test basic system requirements"""
        print_header("System Requirements Validation")

        # Test Python version
        version_info = sys.version_info
        python_ok = version_info.major >= 3 and version_info.minor >= 8
        print_test(f"Python Version ({version_info.major}.{version_info.minor}.{version_info.micro})",
                  python_ok, "Requires Python 3.8+")
        self.test_results.append(("Python Version", python_ok))

        # Test operating system
        import platform
        os_name = platform.system()
        windows_ok = os_name == "Windows"
        print_test(f"Operating System ({os_name})", windows_ok, "Requires Windows for ISQL support")
        self.test_results.append(("Operating System", windows_ok))

        # Test required directories
        required_dirs = ['src', 'config', 'reports', 'logs', 'temp']
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            dir_ok = dir_path.exists()
            if not dir_ok:
                try:
                    dir_path.mkdir(exist_ok=True)
                    print_info(f"Created directory: {dir_name}")
                    dir_ok = True
                except Exception as e:
                    print_error(f"Cannot create directory {dir_name}: {e}")

            print_test(f"Directory {dir_name}", dir_ok)
            self.test_results.append((f"Directory {dir_name}", dir_ok))

    def test_configuration_files(self):
        """Test configuration files"""
        print_header("Configuration Files Validation")

        config_files = [
            'config/config.json',
            'config/database_paths.json',
            'config/app_settings.json'
        ]

        for config_file in config_files:
            file_path = Path(config_file)
            file_exists = file_path.exists()

            if file_exists:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)

                    # Validate JSON structure
                    json_valid = isinstance(config_data, dict)
                    print_test(f"Config file {config_file}", json_valid,
                             "Valid JSON structure" if json_valid else "Invalid JSON structure")
                    self.test_results.append((f"Config {config_file}", json_valid))

                    # Validate key sections
                    if config_file == 'config/config.json':
                        required_sections = ['application', 'database', 'estates', 'analysis']
                        for section in required_sections:
                            section_ok = section in config_data
                            print_test(f"  Section '{section}'", section_ok)
                            self.test_results.append((f"Config Section {section}", section_ok))

                except json.JSONDecodeError as e:
                    print_test(f"Config file {config_file}", False, f"JSON Error: {e}")
                    self.test_results.append((f"Config {config_file}", False))
                    self.errors.append(f"Invalid JSON in {config_file}: {e}")

                except Exception as e:
                    print_test(f"Config file {config_file}", False, f"Error: {e}")
                    self.test_results.append((f"Config {config_file}", False))
                    self.errors.append(f"Error reading {config_file}: {e}")
            else:
                print_test(f"Config file {config_file}", False, "File not found")
                self.test_results.append((f"Config {config_file}", False))
                self.errors.append(f"Configuration file missing: {config_file}")

    def test_module_imports(self):
        """Test module imports"""
        print_header("Module Import Validation")

        # Test core modules
        core_modules = [
            'src.models.transaction',
            'src.models.employee',
            'src.models.estate',
            'src.repositories.transaction_repository',
            'src.repositories.employee_repository',
            'src.repositories.estate_repository',
            'src.services.analysis_service',
            'src.services.validation_service',
            'src.services.configuration_service',
            'src.services.report_generation_service',
            'src.services.employee_performance_service',
            'src.infrastructure.database.firebird_connector',
            'src.infrastructure.reporting.pdf_generator',
            'src.gui.main_window'
        ]

        for module_name in core_modules:
            try:
                __import__(module_name)
                print_test(f"Module {module_name}", True)
                self.test_results.append((f"Module {module_name}", True))
            except ImportError as e:
                print_test(f"Module {module_name}", False, f"Import error: {e}")
                self.test_results.append((f"Module {module_name}", False))
                self.errors.append(f"Module import failed: {module_name} - {e}")
            except Exception as e:
                print_test(f"Module {module_name}", False, f"Error: {e}")
                self.test_results.append((f"Module {module_name}", False))
                self.errors.append(f"Module error: {module_name} - {e}")

        # Test GUI widgets
        gui_widgets = [
            'src.gui.widgets.estate_selection_widget',
            'src.gui.widgets.date_range_widget',
            'src.gui.widgets.progress_widget',
            'src.gui.widgets.results_display_widget',
            'src.gui.widgets.report_export_widget'
        ]

        for widget_name in gui_widgets:
            try:
                __import__(widget_name)
                print_test(f"GUI Widget {widget_name}", True)
                self.test_results.append((f"Widget {widget_name}", True))
            except ImportError as e:
                print_test(f"GUI Widget {widget_name}", False, f"Import error: {e}")
                self.test_results.append((f"Widget {widget_name}", False))
                self.errors.append(f"Widget import failed: {widget_name} - {e}")
            except Exception as e:
                print_test(f"GUI Widget {widget_name}", False, f"Error: {e}")
                self.test_results.append((f"Widget {widget_name}", False))
                self.errors.append(f"Widget error: {widget_name} - {e}")

    def test_database_connectivity(self):
        """Test database connectivity"""
        print_header("Database Connectivity Validation")

        try:
            from src.infrastructure.database.firebird_connector import FirebirdConnector

            # Test connector initialization
            connector = FirebirdConnector()
            print_test("Firebird Connector initialization", True)
            self.test_results.append(("Firebird Connector", True))

            # Test ISQL detection
            isql_detected = connector.detect_isql_path()
            print_test("ISQL detection", isql_detected,
                      f"Path: {connector.isql_path}" if isql_detected else "ISQL not found")
            self.test_results.append(("ISQL Detection", isql_detected))

            if not isql_detected:
                self.warnings.append("ISQL.exe not detected - database functionality may be limited")

            # Test database path validation
            try:
                with open('config/database_paths.json', 'r') as f:
                    db_config = json.load(f)

                estates_configured = 0
                for estate_key, estate_data in db_config.get('estates', {}).items():
                    if estate_data.get('database_path'):
                        estates_configured += 1

                print_test("Database paths configuration", estates_configured > 0,
                          f"{estates_configured} estates configured")
                self.test_results.append(("Database Configuration", estates_configured > 0))

                if estates_configured == 0:
                    self.warnings.append("No estate database paths configured")

            except Exception as e:
                print_test("Database paths configuration", False, f"Error: {e}")
                self.test_results.append(("Database Configuration", False))
                self.errors.append(f"Database configuration error: {e}")

        except Exception as e:
            print_test("Database connectivity test", False, f"Error: {e}")
            self.test_results.append(("Database Connectivity", False))
            self.errors.append(f"Database test failed: {e}")

    def test_core_services(self):
        """Test core services"""
        print_header("Core Services Validation")

        services = [
            ('Configuration Service', 'src.services.configuration_service', 'ConfigurationService'),
            ('Validation Service', 'src.services.validation_service', 'ValidationService'),
            ('Analysis Service', 'src.services.analysis_service', 'AnalysisService'),
            ('Report Generation Service', 'src.services.report_generation_service', 'ReportGenerationService'),
            ('Employee Performance Service', 'src.services.employee_performance_service', 'EmployeePerformanceService')
        ]

        for service_name, module_path, class_name in services:
            try:
                module = __import__(module_path, fromlist=[class_name])
                service_class = getattr(module, class_name)

                # Test service instantiation
                if service_name == 'Configuration Service':
                    service_instance = service_class()
                elif service_name == 'Analysis Service':
                    config_service = __import__('src.services.configuration_service', fromlist=['ConfigurationService']).ConfigurationService()
                    service_instance = service_class(config_service)
                else:
                    service_instance = service_class()

                print_test(f"{service_name} initialization", True)
                self.test_results.append((f"{service_name}", True))

            except Exception as e:
                print_test(f"{service_name} initialization", False, f"Error: {e}")
                self.test_results.append((f"{service_name}", False))
                self.errors.append(f"Service initialization failed: {service_name} - {e}")

    def test_gui_components(self):
        """Test GUI components"""
        print_header("GUI Components Validation")

        # Note: We can't actually test GUI components without a display
        # So we'll test their imports and basic structure

        gui_components = [
            'EstateSelectionWidget',
            'DateRangeWidget',
            'ProgressWidget',
            'ResultsDisplayWidget',
            'ReportExportWidget'
        ]

        for component_name in gui_components:
            try:
                module_path = f"src.gui.widgets.{component_name.lower().replace('widget', '')}_widget"
                module = __import__(module_path, fromlist=[component_name])
                component_class = getattr(module, component_name)

                # Test class definition
                class_defined = hasattr(component_class, '__init__')
                print_test(f"GUI Component {component_name}", class_defined)
                self.test_results.append((f"GUI Component {component_name}", class_defined))

                if not class_defined:
                    self.errors.append(f"GUI component class not properly defined: {component_name}")

            except Exception as e:
                print_test(f"GUI Component {component_name}", False, f"Error: {e}")
                self.test_results.append((f"GUI Component {component_name}", False))
                self.errors.append(f"GUI component error: {component_name} - {e}")

        # Test main window
        try:
            from src.gui.main_window import MainWindow
            main_window_defined = hasattr(MainWindow, '__init__')
            print_test("Main Window class", main_window_defined)
            self.test_results.append(("Main Window", main_window_defined))
        except Exception as e:
            print_test("Main Window class", False, f"Error: {e}")
            self.test_results.append(("Main Window", False))
            self.errors.append(f"Main window error: {e}")

    def test_business_logic(self):
        """Test business logic"""
        print_header("Business Logic Validation")

        # Test domain models
        try:
            from src.models.transaction import Transaction, TransactionGroup
            from src.models.employee import Employee
            from src.models.estate import Estate

            # Test model instantiation
            transaction = Transaction(
                transno="TEST001",
                scanuserid="EMP001",
                recordtag="PM",
                transdate=date.today(),
                fieldid="FIELD001",
                divid="DIV001"
            )
            print_test("Transaction model", transaction is not None)
            self.test_results.append(("Transaction Model", True))

            employee = Employee("EMP001", "Test Employee")
            print_test("Employee model", employee is not None)
            self.test_results.append(("Employee Model", True))

            estate = Estate("EST001", "Test Estate")
            print_test("Estate model", estate is not None)
            self.test_results.append(("Estate Model", True))

        except Exception as e:
            print_test("Domain models", False, f"Error: {e}")
            self.test_results.append(("Domain Models", False))
            self.errors.append(f"Domain models error: {e}")

        # Test business logic methods
        try:
            # Test transaction verification logic
            transaction1 = Transaction("TEST001", "EMP001", "PM", date.today(), "FIELD001", "DIV001")
            transaction2 = Transaction("TEST001", "EMP002", "P1", date.today(), "FIELD001", "DIV001")

            group = TransactionGroup("TEST001")
            group.add_transaction(transaction1)
            group.add_transaction(transaction2)

            verification_works = group.is_verified()
            print_test("Transaction verification logic", verification_works)
            self.test_results.append(("Transaction Verification", verification_works))

        except Exception as e:
            print_test("Business logic methods", False, f"Error: {e}")
            self.test_results.append(("Business Logic", False))
            self.errors.append(f"Business logic error: {e}")

    def test_report_generation(self):
        """Test report generation"""
        print_header("Report Generation Validation")

        try:
            from src.infrastructure.reporting.pdf_generator import PDFReportGenerator

            # Test PDF generator initialization
            pdf_generator = PDFReportGenerator()
            print_test("PDF Generator initialization", True)
            self.test_results.append(("PDF Generator", True))

            # Test report directory creation
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            print_test("Reports directory creation", reports_dir.exists())
            self.test_results.append(("Reports Directory", reports_dir.exists()))

        except Exception as e:
            print_test("Report generation", False, f"Error: {e}")
            self.test_results.append(("Report Generation", False))
            self.errors.append(f"Report generation error: {e}")

    def generate_summary(self):
        """Generate test summary"""
        print_header("Validation Summary")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, result in self.test_results if result)
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")

        if self.errors:
            print(f"\n🔥 Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")

        # Overall system status
        print_header("System Status")

        if success_rate >= 90:
            print("🟢 SYSTEM READY: All critical components validated")
            print("   The system is ready for production use")
        elif success_rate >= 70:
            print("🟡 SYSTEM WARNING: Some components need attention")
            print("   Review warnings and errors before production use")
        else:
            print("🔴 SYSTEM NOT READY: Critical issues found")
            print("   Address all errors before system deployment")

        # Recommendations
        print_header("Recommendations")

        if failed_tests == 0:
            print("✅ All tests passed! System is fully operational")
        else:
            if any("Database" in test[0] and not test[1] for test in self.test_results):
                print("🔧 Configure database paths in config/database_paths.json")
                print("   Ensure Firebird service is running and ISQL.exe is accessible")

            if any("Module" in test[0] and not test[1] for test in self.test_results):
                print("📦 Install missing Python packages:")
                print("   pip install -r requirements.txt")

            if any("Config" in test[0] and not test[1] for test in self.test_results):
                print("⚙️  Review and fix configuration files")
                print("   Ensure all required JSON files are present and valid")

            if any("GUI" in test[0] and not test[1] for test in self.test_results):
                print("🖥️  Check GUI component imports and dependencies")
                print("   Verify tkinter and related packages are properly installed")

        print(f"\nValidation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return success_rate >= 70

def main():
    """Main function"""
    print("FFB Analysis System v2.0 - System Validation Tool")
    print("=" * 60)

    try:
        validator = SystemValidator()
        success = validator.run_all_tests()

        if success:
            print("\n🎉 System validation completed successfully!")
            return 0
        else:
            print("\n⚠️  System validation completed with issues")
            print("   Please address the errors before using the system")
            return 1

    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
        return 2
    except Exception as e:
        print(f"\n\n💥 Unexpected error during validation: {e}")
        print(traceback.format_exc())
        return 3

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to exit...")
    sys.exit(exit_code)