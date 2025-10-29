#!/usr/bin/env python3
"""
Example Usage - Verification Template System
Contoh penggunaan lengkap sistem template verifikasi.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add the verification_template_system to Python path
sys.path.append(str(Path(__file__).parent))

from verification_template_system.core import VerificationEngine, setup_logging
from verification_template_system.core.verification_engine import VerificationBatch
from verification_template_system.config.database_config import DatabaseConfig


def example_basic_usage():
    """
    Contoh penggunaan dasar sistem verifikasi.
    """
    print("=== BASIC USAGE EXAMPLE ===")
    
    try:
        # 1. Setup logging
        logger = setup_logging(log_level="INFO")
        print("✓ Logging system initialized")
        
        # 2. Load database configuration
        config_path = "config.json"
        if not Path(config_path).exists():
            print(f"⚠ Config file not found: {config_path}")
            print("Creating template config...")
            DatabaseConfig.create_template_config(config_path)
            print(f"✓ Template config created: {config_path}")
            print("Please update the config file with your database path and run again.")
            return
        
        db_config = DatabaseConfig.load_from_config(config_path)
        print(f"✓ Database config loaded: {db_config.estate_name}")
        
        # 3. Test database connection
        if db_config.test_connection():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            return
        
        # 4. Initialize verification engine
        engine = VerificationEngine(db_config=db_config, verbose=True)
        print("✓ Verification engine initialized")
        
        # 5. List available templates
        templates = engine.get_available_templates()
        print(f"✓ Available templates: {templates}")
        
        if not templates:
            print("⚠ No templates found")
            return
        
        # 6. Validate template
        template_name = "transaction_verification"
        if template_name in templates:
            if engine.validate_template(template_name):
                print(f"✓ Template '{template_name}' is valid")
            else:
                print(f"✗ Template '{template_name}' validation failed")
                return
        else:
            print(f"⚠ Template '{template_name}' not found")
            return
        
        # 7. Run verification
        print(f"\n--- Running verification for {db_config.estate_name} ---")
        
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = engine.run_verification(
            template_name=template_name,
            estate_name=db_config.estate_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # 8. Process results
        if result['success']:
            print("✓ Verification completed successfully!")
            
            # Display summary
            if 'summary' in result:
                summary = result['summary']
                print(f"  - Total employees: {summary.get('total_employees', 'N/A')}")
                print(f"  - Total divisions: {summary.get('total_divisions', 'N/A')}")
                print(f"  - Verification rate: {summary.get('verification_rate', 'N/A'):.2f}%")
            
            # Save results
            output_file = f"verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            engine.save_results(result, output_file)
            print(f"✓ Results saved to: {output_file}")
            
        else:
            print(f"✗ Verification failed: {result.get('error', 'Unknown error')}")
        
        # 9. Cleanup
        engine.cleanup()
        print("✓ Cleanup completed")
        
    except Exception as e:
        print(f"✗ Error in basic usage example: {e}")
        import traceback
        traceback.print_exc()


def example_batch_processing():
    """
    Contoh batch processing untuk multiple estates/periods.
    """
    print("\n=== BATCH PROCESSING EXAMPLE ===")
    
    try:
        # Setup
        logger = setup_logging(log_level="INFO")
        db_config = DatabaseConfig.load_from_config("config.json")
        
        # Initialize batch processor
        batch = VerificationBatch()
        print("✓ Batch processor initialized")
        
        # Add multiple jobs
        estates = [db_config.estate_name]  # Add more estates if available
        
        # Create jobs for different date ranges
        end_date = datetime.now()
        
        for i, months_back in enumerate([1, 2, 3]):  # Last 3 months
            start_date = end_date - timedelta(days=30 * months_back)
            period_end = end_date - timedelta(days=30 * (months_back - 1))
            
            for estate in estates:
                job_id = batch.add_job(
                    template_name="transaction_verification",
                    estate_name=estate,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=period_end.strftime("%Y-%m-%d"),
                    custom_config={
                        'batch_size': 500,
                        'enable_detailed_logging': True
                    }
                )
                print(f"✓ Added job {job_id}: {estate} ({start_date.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')})")
        
        # Display jobs
        jobs = batch.get_jobs()
        print(f"✓ Total jobs queued: {len(jobs)}")
        
        # Run all jobs
        print("\n--- Running batch jobs ---")
        results = batch.run_all()
        
        # Process results
        successful_jobs = [r for r in results if r['success']]
        failed_jobs = [r for r in results if not r['success']]
        
        print(f"\n--- Batch Results ---")
        print(f"✓ Successful jobs: {len(successful_jobs)}")
        print(f"✗ Failed jobs: {len(failed_jobs)}")
        
        # Save batch results
        batch_results = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs': len(results),
            'successful_jobs': len(successful_jobs),
            'failed_jobs': len(failed_jobs),
            'results': results
        }
        
        batch_output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ Batch results saved to: {batch_output_file}")
        
        # Display failed jobs details
        if failed_jobs:
            print("\n--- Failed Jobs Details ---")
            for job in failed_jobs:
                print(f"✗ Job {job['job_id']}: {job.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"✗ Error in batch processing example: {e}")
        import traceback
        traceback.print_exc()


def example_custom_configuration():
    """
    Contoh penggunaan dengan konfigurasi custom.
    """
    print("\n=== CUSTOM CONFIGURATION EXAMPLE ===")
    
    try:
        # Setup
        logger = setup_logging(log_level="DEBUG")  # More verbose logging
        db_config = DatabaseConfig.load_from_config("config.json")
        engine = VerificationEngine(db_config=db_config, verbose=True)
        
        # Custom configuration
        custom_config = {
            'batch_size': 200,  # Smaller batch size
            'enable_special_filters': True,
            'timeout_seconds': 300,
            'retry_attempts': 3,
            'output_format': 'detailed',
            'enable_performance_monitoring': True,
            'comparison_fields': ['RIPEBCH', 'UNRIPEBCH', 'EMPTYBNCH', 'LOOSEFRUIT'],
            'special_month_filter': {
                'enabled': True,
                'months': ['10', '11', '12'],
                'transstatus': 704
            }
        }
        
        print("✓ Custom configuration prepared")
        print(f"  - Batch size: {custom_config['batch_size']}")
        print(f"  - Special filters: {custom_config['enable_special_filters']}")
        print(f"  - Timeout: {custom_config['timeout_seconds']}s")
        
        # Run with custom config
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # Last 2 months
        
        result = engine.run_verification(
            template_name="transaction_verification",
            estate_name=db_config.estate_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            custom_config=custom_config
        )
        
        if result['success']:
            print("✓ Custom configuration verification completed!")
            
            # Display detailed results
            if 'performance_metrics' in result:
                metrics = result['performance_metrics']
                print(f"  - Execution time: {metrics.get('total_time', 'N/A')}s")
                print(f"  - Database queries: {metrics.get('query_count', 'N/A')}")
                print(f"  - Records processed: {metrics.get('records_processed', 'N/A')}")
            
            # Save with custom filename
            output_file = f"custom_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            engine.save_results(result, output_file)
            print(f"✓ Results saved to: {output_file}")
            
        else:
            print(f"✗ Custom configuration verification failed: {result.get('error')}")
        
        engine.cleanup()
        
    except Exception as e:
        print(f"✗ Error in custom configuration example: {e}")
        import traceback
        traceback.print_exc()


def example_logging_and_monitoring():
    """
    Contoh penggunaan logging dan monitoring yang advanced.
    """
    print("\n=== LOGGING AND MONITORING EXAMPLE ===")
    
    try:
        # Setup advanced logging
        logger = setup_logging(
            log_level="DEBUG",
            enable_file_logging=True,
            enable_console_logging=True
        )
        
        # Start verification session
        session_info = {
            'template_name': 'transaction_verification',
            'estate_name': 'PGE 2B',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'purpose': 'Example monitoring session'
        }
        
        logger.start_verification_session(session_info)
        print("✓ Verification session started")
        
        # Simulate verification steps with logging
        logger.log_verification_step("initialization", {
            'message': 'Initializing verification system',
            'config_loaded': True,
            'templates_available': 1
        })
        
        logger.log_verification_step("database_connection", {
            'message': 'Connecting to database',
            'database_path': 'example.fdb',
            'connection_timeout': 30
        })
        
        # Simulate database operations
        logger.log_database_operation(
            operation="SELECT",
            query="SELECT EMP_ID, EMP_NAME FROM EMP WHERE ESTATE = ?",
            params={'estate': 'PGE 2B'},
            result_count=150,
            duration=0.245
        )
        
        logger.log_database_operation(
            operation="SELECT",
            query="SELECT * FROM FFBSCANNERDATA_202401 WHERE DIVISION = ?",
            params={'division': 'DIV001'},
            result_count=500,
            duration=1.123
        )
        
        # Simulate template operations
        logger.log_template_operation(
            template_name="transaction_verification",
            operation="analyze_division",
            details={
                'division': 'DIV001',
                'records_processed': 500,
                'duplicates_found': 25,
                'verification_rate': 95.5
            }
        )
        
        # Simulate error handling
        try:
            raise ValueError("Example error for logging demonstration")
        except Exception as e:
            logger.log_error_with_context(e, {
                'operation': 'example_operation',
                'parameters': {'test': True},
                'step': 'error_simulation'
            })
        
        # End session
        session_result = {
            'success': True,
            'total_divisions': 5,
            'total_employees': 150,
            'total_records': 2500,
            'verification_rate': 94.2,
            'execution_time': 45.7
        }
        
        logger.end_verification_session(session_result)
        print("✓ Verification session completed")
        
        # Export session logs
        export_path = logger.export_session_logs()
        if export_path:
            print(f"✓ Session logs exported to: {export_path}")
        
        # Get session logs for analysis
        session_logs = logger.get_session_logs()
        print(f"✓ Session generated {len(session_logs)} log entries")
        
        # Analyze logs
        error_logs = [log for log in session_logs if 'error' in log.get('step_data', {})]
        db_operations = [log for log in session_logs if log.get('step_name', '').startswith('database')]
        
        print(f"  - Error logs: {len(error_logs)}")
        print(f"  - Database operations: {len(db_operations)}")
        
    except Exception as e:
        print(f"✗ Error in logging example: {e}")
        import traceback
        traceback.print_exc()


def example_template_management():
    """
    Contoh manajemen template.
    """
    print("\n=== TEMPLATE MANAGEMENT EXAMPLE ===")
    
    try:
        # Setup
        engine = VerificationEngine()
        
        # List available templates
        templates = engine.get_available_templates()
        print(f"✓ Available templates: {templates}")
        
        # Get template information
        for template_name in templates:
            try:
                template_info = engine.template_loader.get_template_info(template_name)
                print(f"\n--- Template: {template_name} ---")
                print(f"  Version: {template_info.get('version', 'N/A')}")
                print(f"  Description: {template_info.get('description', 'N/A')}")
                print(f"  Author: {template_info.get('author', 'N/A')}")
                print(f"  Created: {template_info.get('created_date', 'N/A')}")
                
                # Validate template
                is_valid = engine.validate_template(template_name)
                print(f"  Valid: {'✓' if is_valid else '✗'}")
                
            except Exception as e:
                print(f"  ✗ Error loading template info: {e}")
        
        # Reload templates (useful for development)
        engine.template_loader.reload_templates()
        print("✓ Templates reloaded")
        
    except Exception as e:
        print(f"✗ Error in template management example: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Main function untuk menjalankan semua contoh.
    """
    print("=== VERIFICATION TEMPLATE SYSTEM - EXAMPLE USAGE ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Working directory: {Path.cwd()}")
    
    # Check if config file exists
    config_path = Path("config.json")
    if not config_path.exists():
        print(f"\n⚠ Config file not found: {config_path}")
        print("Creating template config file...")
        DatabaseConfig.create_template_config(str(config_path))
        print(f"✓ Template config created: {config_path}")
        print("\nPlease update the config file with your actual database path:")
        print('  {"Your Estate Name": "path/to/your/database.fdb"}')
        print("\nThen run this script again.")
        return
    
    try:
        # Run examples
        example_basic_usage()
        example_template_management()
        example_logging_and_monitoring()
        example_custom_configuration()
        example_batch_processing()
        
        print("\n=== ALL EXAMPLES COMPLETED ===")
        print("Check the generated files for results and logs.")
        
    except KeyboardInterrupt:
        print("\n⚠ Examples interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()