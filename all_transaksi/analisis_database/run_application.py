#!/usr/bin/env python3
"""
FFB Analysis System v2.0 - Application Launcher
Safe launcher with error handling and system checks
"""

import sys
import os
import traceback
from pathlib import Path

def check_system_requirements():
    """Check basic system requirements"""
    print("Checking system requirements...")

    # Check Python version
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        print(f"❌ Python {version_info.major}.{version_info.minor} detected")
        print("   Python 3.8 or higher is required")
        return False

    print(f"✅ Python {version_info.major}.{version_info.minor}.{version_info.micro}")

    # Check operating system
    import platform
    os_name = platform.system()
    if os_name != "Windows":
        print(f"⚠️  {os_name} detected")
        print("   Windows is recommended for ISQL support")
        print("   System may run with limited functionality")
    else:
        print(f"✅ {os_name}")

    # Check required directories
    required_dirs = ['src', 'config', 'reports', 'logs', 'temp']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ Created directory: {dir_name}")
            except Exception as e:
                print(f"❌ Cannot create directory {dir_name}: {e}")
                return False
        else:
            print(f"✅ Directory exists: {dir_name}")

    return True

def check_configuration():
    """Check configuration files"""
    print("\nChecking configuration files...")

    config_files = [
        'config/config.json',
        'config/database_paths.json',
        'config/app_settings.json'
    ]

    all_good = True
    for config_file in config_files:
        file_path = Path(config_file)
        if file_path.exists():
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ {config_file}")
            except json.JSONDecodeError as e:
                print(f"❌ {config_file} - Invalid JSON: {e}")
                all_good = False
            except Exception as e:
                print(f"❌ {config_file} - Error: {e}")
                all_good = False
        else:
            print(f"❌ {config_file} - File not found")
            all_good = False

    return all_good

def check_dependencies():
    """Check Python dependencies"""
    print("\nChecking Python dependencies...")

    required_packages = [
        'pandas',
        'numpy',
        'tkinter',
        'tkcalendar',
        'reportlab',
        'matplotlib',
        'seaborn'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements.txt")
        return False

    return True

def run_system_check():
    """Run comprehensive system check"""
    print("=" * 60)
    print("FFB Analysis System v2.0 - System Check")
    print("=" * 60)

    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met")
        return False

    # Check configuration
    if not check_configuration():
        print("\n❌ Configuration issues found")
        return False

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies")
        return False

    print("\n✅ All system checks passed!")
    return True

def launch_application():
    """Launch the main application"""
    try:
        print("\n" + "=" * 60)
        print("Launching FFB Analysis System v2.0...")
        print("=" * 60)

        # Add src directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

        # Import and run main application
        from main import main as app_main
        app_main()

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        return 0
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   This usually indicates missing dependencies or incorrect installation")
        print("   Try running: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        print("\nDetailed error information:")
        print(traceback.format_exc())
        return 1

def main():
    """Main launcher function"""
    print("FFB Analysis System v2.0")
    print("Portable Multi-Estate FFB Scanner Analysis System")
    print()

    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Ask user what to do
    print("Choose an option:")
    print("1. Run system checks only")
    print("2. Launch application")
    print("3. Run both checks and launch")
    print("4. Exit")

    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            success = run_system_check()
            return 0 if success else 1

        elif choice == "2":
            return launch_application()

        elif choice == "3":
            if run_system_check():
                input("\nPress Enter to launch the application...")
                return launch_application()
            else:
                print("\n❌ System checks failed. Application not launched.")
                return 1

        elif choice == "4":
            print("Exiting...")
            return 0

        else:
            print("Invalid choice. Exiting...")
            return 1

    except KeyboardInterrupt:
        print("\n\nExiting...")
        return 0
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("\nPress Enter to exit...")
    sys.exit(exit_code)