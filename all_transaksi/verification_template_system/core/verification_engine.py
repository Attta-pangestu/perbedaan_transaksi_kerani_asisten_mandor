"""
Verification Engine
Engine utama untuk menjalankan proses verifikasi menggunakan template.
"""

import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import json

from .template_loader import TemplateLoader
from ..config.database_config import DatabaseConfig
from ..config.settings import Settings


class VerificationEngine:
    """
    Engine utama untuk menjalankan verifikasi menggunakan template.
    Mengkoordinasikan template loader, database config, dan logging.
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize verification engine.
        
        Args:
            config_path: Path ke file konfigurasi database (opsional)
        """
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.template_loader = TemplateLoader()
        self.db_config = DatabaseConfig(config_path)
        
        # Runtime state
        self.current_template = None
        self.current_template_instance = None
        self.verification_results = {}
        self.verification_metadata = {}
        
        # Setup logging untuk verification
        self._setup_verification_logging()
    
    def _setup_verification_logging(self):
        """
        Setup logging khusus untuk proses verifikasi.
        """
        # Buat handler untuk file log verifikasi
        log_file = self.settings.get_log_path("verification_engine.log")
        
        # Pastikan direktori log ada
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Format log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Tambahkan handler ke logger
        self.logger.addHandler(file_handler)
        
        self.logger.info("Verification engine initialized")
    
    def get_available_templates(self) -> List[str]:
        """
        Dapatkan daftar template yang tersedia.
        
        Returns:
            List: Nama template yang tersedia
        """
        return self.template_loader.get_available_templates()
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Dapatkan informasi template.
        
        Args:
            template_name: Nama template
        
        Returns:
            Dict: Informasi template
        """
        return self.template_loader.get_template_info(template_name)
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validasi template sebelum digunakan.
        
        Args:
            template_name: Nama template
        
        Returns:
            Dict: Hasil validasi
        """
        return self.template_loader.validate_template(template_name)
    
    def load_template(self, template_name: str, **template_kwargs) -> bool:
        """
        Load template untuk digunakan dalam verifikasi.
        
        Args:
            template_name: Nama template
            **template_kwargs: Parameter tambahan untuk template
        
        Returns:
            bool: True jika berhasil load
        """
        try:
            # Validasi template terlebih dahulu
            validation = self.validate_template(template_name)
            if not validation['valid']:
                self.logger.error(f"Template {template_name} tidak valid: {validation['errors']}")
                return False
            
            # Load template instance
            self.current_template_instance = self.template_loader.create_template_instance(
                template_name, **template_kwargs
            )
            
            if not self.current_template_instance:
                self.logger.error(f"Gagal membuat instance template: {template_name}")
                return False
            
            self.current_template = template_name
            self.logger.info(f"Template loaded: {template_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading template {template_name}: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def prepare_verification(self, 
                           estate_name: str,
                           start_date: Union[str, datetime],
                           end_date: Union[str, datetime],
                           **verification_params) -> bool:
        """
        Persiapan verifikasi dengan parameter yang diberikan.
        
        Args:
            estate_name: Nama estate
            start_date: Tanggal mulai
            end_date: Tanggal akhir
            **verification_params: Parameter verifikasi tambahan
        
        Returns:
            bool: True jika persiapan berhasil
        """
        try:
            if not self.current_template_instance:
                self.logger.error("Template belum di-load")
                return False
            
            # Konversi tanggal jika perlu
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Setup metadata verifikasi
            self.verification_metadata = {
                'template_name': self.current_template,
                'estate_name': estate_name,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'verification_params': verification_params,
                'prepared_at': datetime.now().isoformat(),
                'database_path': self.db_config.get_database_path()
            }
            
            # Setup database connection di template
            db_path = self.db_config.get_database_path()
            if not db_path:
                self.logger.error("Database path tidak ditemukan")
                return False
            
            # Connect ke database
            if hasattr(self.current_template_instance, 'connect_database'):
                success = self.current_template_instance.connect_database(db_path)
                if not success:
                    self.logger.error("Gagal connect ke database")
                    return False
            
            self.logger.info(f"Verification prepared for estate: {estate_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error preparing verification: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def run_verification(self) -> Dict[str, Any]:
        """
        Jalankan proses verifikasi.
        
        Returns:
            Dict: Hasil verifikasi
        """
        if not self.current_template_instance:
            return {
                'success': False,
                'error': 'Template belum di-load',
                'results': {}
            }
        
        if not self.verification_metadata:
            return {
                'success': False,
                'error': 'Verifikasi belum dipersiapkan',
                'results': {}
            }
        
        start_time = datetime.now()
        
        try:
            self.logger.info("Memulai proses verifikasi...")
            
            # Jalankan verifikasi menggunakan template
            if hasattr(self.current_template_instance, 'run_verification'):
                # Template dengan method run_verification
                results = self.current_template_instance.run_verification(
                    estate_name=self.verification_metadata['estate_name'],
                    start_date=self.verification_metadata['start_date'],
                    end_date=self.verification_metadata['end_date'],
                    **self.verification_metadata['verification_params']
                )
            else:
                # Template tanpa method run_verification, coba method lain
                if hasattr(self.current_template_instance, 'analyze_estate'):
                    results = self.current_template_instance.analyze_estate(
                        estate_name=self.verification_metadata['estate_name'],
                        start_date=self.verification_metadata['start_date'],
                        end_date=self.verification_metadata['end_date']
                    )
                else:
                    raise AttributeError("Template tidak memiliki method verifikasi yang dikenali")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Compile hasil verifikasi
            verification_result = {
                'success': True,
                'results': results,
                'metadata': self.verification_metadata.copy(),
                'execution_info': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration,
                    'template_used': self.current_template
                }
            }
            
            # Simpan hasil
            self.verification_results = verification_result
            
            self.logger.info(f"Verifikasi selesai dalam {duration:.2f} detik")
            
            return verification_result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_result = {
                'success': False,
                'error': str(e),
                'error_traceback': traceback.format_exc(),
                'metadata': self.verification_metadata.copy(),
                'execution_info': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration,
                    'template_used': self.current_template
                }
            }
            
            self.logger.error(f"Error dalam verifikasi: {e}")
            self.logger.error(traceback.format_exc())
            
            return error_result
    
    def save_results(self, output_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Simpan hasil verifikasi ke file.
        
        Args:
            output_path: Path output (opsional, default ke reports directory)
        
        Returns:
            bool: True jika berhasil simpan
        """
        try:
            if not self.verification_results:
                self.logger.error("Tidak ada hasil verifikasi untuk disimpan")
                return False
            
            # Tentukan path output
            if output_path:
                output_file = Path(output_path)
            else:
                # Generate nama file berdasarkan metadata
                metadata = self.verification_results.get('metadata', {})
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"verification_{metadata.get('estate_name', 'unknown')}_{timestamp}.json"
                output_file = self.settings.get_report_path(filename)
            
            # Pastikan direktori ada
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Simpan hasil
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.verification_results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Hasil verifikasi disimpan ke: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error menyimpan hasil: {e}")
            return False
    
    def cleanup(self):
        """
        Cleanup resources setelah verifikasi selesai.
        """
        try:
            # Disconnect database jika ada
            if self.current_template_instance and hasattr(self.current_template_instance, 'disconnect_database'):
                self.current_template_instance.disconnect_database()
            
            # Reset state
            self.current_template = None
            self.current_template_instance = None
            self.verification_metadata = {}
            
            self.logger.info("Verification engine cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """
        Dapatkan ringkasan hasil verifikasi.
        
        Returns:
            Dict: Ringkasan hasil
        """
        if not self.verification_results:
            return {'status': 'no_results'}
        
        results = self.verification_results.get('results', {})
        metadata = self.verification_results.get('metadata', {})
        execution_info = self.verification_results.get('execution_info', {})
        
        summary = {
            'status': 'success' if self.verification_results.get('success') else 'failed',
            'estate_name': metadata.get('estate_name'),
            'template_used': execution_info.get('template_used'),
            'duration_seconds': execution_info.get('duration_seconds'),
            'start_date': metadata.get('start_date'),
            'end_date': metadata.get('end_date')
        }
        
        # Tambahkan statistik dari hasil jika ada
        if isinstance(results, dict):
            if 'total_divisions' in results:
                summary['total_divisions'] = results['total_divisions']
            if 'total_employees' in results:
                summary['total_employees'] = len(results['total_employees'])
            if 'differences_found' in results:
                summary['differences_found'] = results['differences_found']
        
        return summary
    
    def export_verification_report(self, format_type: str = 'json') -> Optional[str]:
        """
        Export laporan verifikasi dalam format tertentu.
        
        Args:
            format_type: Format export ('json', 'summary')
        
        Returns:
            str: Path file yang di-export atau None jika gagal
        """
        try:
            if not self.verification_results:
                self.logger.error("Tidak ada hasil verifikasi untuk di-export")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata = self.verification_results.get('metadata', {})
            estate_name = metadata.get('estate_name', 'unknown')
            
            if format_type == 'json':
                # Export full JSON
                filename = f"verification_report_{estate_name}_{timestamp}.json"
                output_file = self.settings.get_report_path(filename)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.verification_results, f, indent=2, ensure_ascii=False, default=str)
                
            elif format_type == 'summary':
                # Export summary saja
                filename = f"verification_summary_{estate_name}_{timestamp}.json"
                output_file = self.settings.get_report_path(filename)
                
                summary = self.get_verification_summary()
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            
            else:
                self.logger.error(f"Format export tidak didukung: {format_type}")
                return None
            
            self.logger.info(f"Report exported: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            return None


class VerificationBatch:
    """
    Helper class untuk menjalankan verifikasi batch (multiple estates/periods).
    """
    
    def __init__(self, engine: VerificationEngine):
        """
        Initialize batch processor.
        
        Args:
            engine: Instance VerificationEngine
        """
        self.engine = engine
        self.logger = logging.getLogger(__name__)
        self.batch_results = []
    
    def add_verification_job(self, 
                           estate_name: str,
                           start_date: Union[str, datetime],
                           end_date: Union[str, datetime],
                           **params):
        """
        Tambahkan job verifikasi ke batch.
        
        Args:
            estate_name: Nama estate
            start_date: Tanggal mulai
            end_date: Tanggal akhir
            **params: Parameter tambahan
        """
        job = {
            'estate_name': estate_name,
            'start_date': start_date,
            'end_date': end_date,
            'params': params
        }
        
        if not hasattr(self, 'jobs'):
            self.jobs = []
        
        self.jobs.append(job)
        self.logger.info(f"Added verification job: {estate_name}")
    
    def run_batch(self, template_name: str, **template_kwargs) -> List[Dict[str, Any]]:
        """
        Jalankan semua job dalam batch.
        
        Args:
            template_name: Nama template yang digunakan
            **template_kwargs: Parameter template
        
        Returns:
            List: Hasil semua verifikasi
        """
        if not hasattr(self, 'jobs') or not self.jobs:
            self.logger.error("Tidak ada job untuk dijalankan")
            return []
        
        # Load template sekali untuk semua job
        if not self.engine.load_template(template_name, **template_kwargs):
            self.logger.error(f"Gagal load template: {template_name}")
            return []
        
        batch_results = []
        
        try:
            for i, job in enumerate(self.jobs):
                self.logger.info(f"Running job {i+1}/{len(self.jobs)}: {job['estate_name']}")
                
                # Prepare verification
                success = self.engine.prepare_verification(
                    estate_name=job['estate_name'],
                    start_date=job['start_date'],
                    end_date=job['end_date'],
                    **job['params']
                )
                
                if not success:
                    result = {
                        'job_index': i,
                        'estate_name': job['estate_name'],
                        'success': False,
                        'error': 'Failed to prepare verification'
                    }
                    batch_results.append(result)
                    continue
                
                # Run verification
                result = self.engine.run_verification()
                result['job_index'] = i
                batch_results.append(result)
                
                # Save individual result
                self.engine.save_results()
                
                self.logger.info(f"Job {i+1} completed: {result.get('success', False)}")
        
        finally:
            # Cleanup
            self.engine.cleanup()
        
        self.batch_results = batch_results
        self.logger.info(f"Batch completed: {len(batch_results)} jobs processed")
        
        return batch_results
    
    def get_batch_summary(self) -> Dict[str, Any]:
        """
        Dapatkan ringkasan hasil batch.
        
        Returns:
            Dict: Ringkasan batch
        """
        if not self.batch_results:
            return {'status': 'no_results'}
        
        total_jobs = len(self.batch_results)
        successful_jobs = sum(1 for result in self.batch_results if result.get('success'))
        failed_jobs = total_jobs - successful_jobs
        
        return {
            'total_jobs': total_jobs,
            'successful_jobs': successful_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': successful_jobs / total_jobs if total_jobs > 0 else 0,
            'results': self.batch_results
        }


if __name__ == "__main__":
    # Test verification engine
    print("=== Verification Engine Test ===")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize engine
        engine = VerificationEngine()
        
        print(f"Available templates: {engine.get_available_templates()}")
        
        # Test dengan template transaction_verification jika ada
        template_name = "transaction_verification"
        if template_name in engine.get_available_templates():
            print(f"\n--- Testing template: {template_name} ---")
            
            # Get template info
            info = engine.get_template_info(template_name)
            if info:
                print(f"Template info: {info.get('name')} v{info.get('version')}")
            
            # Validate template
            validation = engine.validate_template(template_name)
            print(f"Template valid: {validation['valid']}")
            
            if validation['valid']:
                # Load template
                if engine.load_template(template_name):
                    print("Template loaded successfully")
                    
                    # Test prepare verification (dengan data dummy)
                    if engine.prepare_verification(
                        estate_name="TEST_ESTATE",
                        start_date="2024-01-01",
                        end_date="2024-01-31"
                    ):
                        print("Verification prepared")
                        
                        # Note: Tidak menjalankan verifikasi actual karena butuh database
                        print("Verification engine test completed (database connection not tested)")
                    else:
                        print("Failed to prepare verification")
                else:
                    print("Failed to load template")
            else:
                print(f"Template validation errors: {validation['errors']}")
        else:
            print(f"Template {template_name} not found")
        
        # Cleanup
        engine.cleanup()
        
    except Exception as e:
        print(f"Verification engine test failed: {e}")
        raise