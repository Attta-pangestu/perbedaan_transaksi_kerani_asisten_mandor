"""
Transaction Verification Template
Template untuk verifikasi transaksi FFB yang diekstrak dari gui_multi_estate_ffb_analysis.py
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

from ..config.database_config import DatabaseConfig
from ..config.settings import Settings


class TransactionVerificationTemplate:
    """
    Template untuk verifikasi transaksi FFB.
    Mengimplementasikan logika yang diekstrak dari GUI application.
    """
    
    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize template verifikasi transaksi.
        
        Args:
            template_path: Path ke file template JSON (opsional)
        """
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)
        
        # Load template configuration
        if template_path:
            self.template_path = Path(template_path)
        else:
            self.template_path = self.settings.get_template_path('transaction_verification')
        
        self.template_config = self._load_template()
        
        # Initialize database config
        self.db_config = None
        self.connection = None
        
        # Cache untuk employee mapping
        self._employee_mapping = None
    
    def _load_template(self) -> Dict[str, Any]:
        """
        Load template configuration dari file JSON.
        
        Returns:
            Dict: Template configuration
        """
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Template file tidak ditemukan: {self.template_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing template JSON: {e}")
            raise
    
    def set_database_config(self, db_config: DatabaseConfig):
        """
        Set konfigurasi database.
        
        Args:
            db_config: Instance DatabaseConfig
        """
        self.db_config = db_config
        self.connection = None  # Reset connection
    
    def connect_database(self):
        """
        Buat koneksi ke database.
        """
        if not self.db_config:
            raise ValueError("Database config belum di-set. Gunakan set_database_config() terlebih dahulu.")
        
        try:
            self.connection = self.db_config.create_connection()
            self.logger.info("Koneksi database berhasil dibuat")
        except Exception as e:
            self.logger.error(f"Gagal membuat koneksi database: {e}")
            raise
    
    def disconnect_database(self):
        """
        Tutup koneksi database.
        """
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.logger.info("Koneksi database ditutup")
            except Exception as e:
                self.logger.error(f"Error menutup koneksi database: {e}")
    
    def get_employee_mapping(self) -> Dict[str, str]:
        """
        Dapatkan mapping employee ID ke nama.
        Implementasi dari get_employee_mapping() di GUI original.
        
        Returns:
            Dict: Mapping employee ID ke nama
        """
        if self._employee_mapping is not None:
            return self._employee_mapping
        
        if not self.connection:
            raise ValueError("Koneksi database belum dibuat. Gunakan connect_database() terlebih dahulu.")
        
        query_config = self.template_config['queries']['employee_mapping']
        sql = query_config['sql']
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            mapping = {}
            for row in cursor.fetchall():
                emp_id = str(row[0]).strip() if row[0] else None
                emp_name = str(row[1]).strip() if row[1] else None
                
                if emp_id and emp_name:
                    mapping[emp_id] = emp_name
            
            cursor.close()
            
            self._employee_mapping = mapping
            self.logger.info(f"Employee mapping berhasil dimuat: {len(mapping)} employees")
            
            return mapping
            
        except Exception as e:
            self.logger.error(f"Error mendapatkan employee mapping: {e}")
            raise
    
    def get_division_tables(self, start_date: str, end_date: str) -> List[str]:
        """
        Dapatkan daftar tabel FFBSCANNERDATA berdasarkan rentang tanggal.
        
        Args:
            start_date: Tanggal mulai (format YYYYMMDD)
            end_date: Tanggal akhir (format YYYYMMDD)
        
        Returns:
            List: Daftar nama tabel
        """
        if not self.connection:
            raise ValueError("Koneksi database belum dibuat.")
        
        query_config = self.template_config['queries']['division_tables']
        sql = query_config['sql_template'].format(
            start_date=start_date,
            end_date=end_date
        )
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            tables = []
            for row in cursor.fetchall():
                table_name = str(row[0]).strip()
                tables.append(table_name)
            
            cursor.close()
            
            self.logger.info(f"Ditemukan {len(tables)} tabel FFBSCANNERDATA")
            return tables
            
        except Exception as e:
            self.logger.error(f"Error mendapatkan division tables: {e}")
            raise
    
    def get_divisions(self, tables: List[str]) -> List[str]:
        """
        Dapatkan daftar divisi dari tabel-tabel FFBSCANNERDATA.
        
        Args:
            tables: Daftar nama tabel
        
        Returns:
            List: Daftar divisi
        """
        if not self.connection:
            raise ValueError("Koneksi database belum dibuat.")
        
        if not tables:
            return []
        
        query_config = self.template_config['queries']['divisions_from_tables']
        union_template = query_config['union_template']
        
        # Buat UNION query untuk semua tabel
        union_queries = []
        for table in tables:
            union_queries.append(union_template.format(table_name=table))
        
        table_unions = ' UNION '.join(union_queries)
        sql = query_config['sql_template'].format(table_unions=table_unions)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            divisions = []
            for row in cursor.fetchall():
                division = str(row[0]).strip() if row[0] else None
                if division:
                    divisions.append(division)
            
            cursor.close()
            
            self.logger.info(f"Ditemukan {len(divisions)} divisi")
            return divisions
            
        except Exception as e:
            self.logger.error(f"Error mendapatkan divisions: {e}")
            raise
    
    def analyze_division(self, division: str, table_name: str, month: Optional[int] = None) -> Dict[str, Any]:
        """
        Analisis divisi untuk verifikasi transaksi.
        Implementasi dari analyze_division() di GUI original.
        
        Args:
            division: Nama divisi
            table_name: Nama tabel FFBSCANNERDATA
            month: Bulan untuk filter khusus (opsional)
        
        Returns:
            Dict: Hasil analisis divisi
        """
        if not self.connection:
            raise ValueError("Koneksi database belum dibuat.")
        
        self.logger.info(f"Menganalisis divisi: {division} dari tabel: {table_name}")
        
        # Tentukan apakah perlu filter khusus untuk bulan Mei
        use_special_filter = (month == 5)
        
        # Ambil data FFB
        if use_special_filter:
            df = self._get_ffb_data_with_filter(table_name, division, "704")
            self.logger.info(f"Menggunakan filter TRANSSTATUS 704 untuk bulan {month}")
        else:
            df = self._get_ffb_data(table_name, division)
        
        if df.empty:
            self.logger.warning(f"Tidak ada data untuk divisi {division}")
            return self._create_empty_result(division, table_name)
        
        # Dapatkan employee mapping
        employee_mapping = self.get_employee_mapping()
        
        # Analisis data
        kerani_data = self._calculate_kerani_data(df, employee_mapping)
        mandor_data = self._calculate_mandor_data(df, employee_mapping)
        asisten_data = self._calculate_asisten_data(df, employee_mapping)
        
        # Hitung tingkat verifikasi
        verification_rates = self._calculate_verification_rates(kerani_data, mandor_data, asisten_data)
        
        # Identifikasi perbedaan
        differences = self._identify_differences(kerani_data, mandor_data, asisten_data)
        
        result = {
            'division': division,
            'table_name': table_name,
            'kerani_data': kerani_data,
            'mandor_data': mandor_data,
            'asisten_data': asisten_data,
            'verification_rates': verification_rates,
            'differences': differences,
            'summary': {
                'total_records': len(df),
                'unique_employees': len(set(df['EMPID'].dropna())),
                'unique_transno': len(set(df['TRANSNO'].dropna())),
                'special_filter_applied': use_special_filter
            }
        }
        
        self.logger.info(f"Analisis divisi {division} selesai")
        return result
    
    def _get_ffb_data(self, table_name: str, division: str) -> pd.DataFrame:
        """
        Ambil data FFB granular dari tabel.
        
        Args:
            table_name: Nama tabel
            division: Nama divisi
        
        Returns:
            DataFrame: Data FFB
        """
        query_config = self.template_config['queries']['ffb_granular_data']
        sql = query_config['sql_template'].format(table_name=table_name)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (division,))
            
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            
            cursor.close()
            
            df = pd.DataFrame(data, columns=columns)
            
            # Convert numeric columns
            numeric_fields = self.template_config['validation_rules']['numeric_fields']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error mengambil data FFB: {e}")
            raise
    
    def _get_ffb_data_with_filter(self, table_name: str, division: str, transstatus: str) -> pd.DataFrame:
        """
        Ambil data FFB granular dengan filter TRANSSTATUS.
        
        Args:
            table_name: Nama tabel
            division: Nama divisi
            transstatus: Status transaksi untuk filter
        
        Returns:
            DataFrame: Data FFB yang difilter
        """
        query_config = self.template_config['queries']['ffb_granular_data_with_filter']
        sql = query_config['sql_template'].format(table_name=table_name)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (division, transstatus))
            
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            
            cursor.close()
            
            df = pd.DataFrame(data, columns=columns)
            
            # Convert numeric columns
            numeric_fields = self.template_config['validation_rules']['numeric_fields']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error mengambil data FFB dengan filter: {e}")
            raise
    
    def _calculate_kerani_data(self, df: pd.DataFrame, employee_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Hitung data kerani berdasarkan duplikasi TRANSNO.
        Implementasi logika kerani dari GUI original.
        
        Args:
            df: DataFrame data FFB
            employee_mapping: Mapping employee ID ke nama
        
        Returns:
            Dict: Data kerani
        """
        comparison_fields = self.template_config['calculation_logic']['duplicate_handling']['comparison_fields']
        
        # Filter data PM (kerani)
        kerani_df = df[df['RECORDTAG'] == 'PM'].copy()
        
        if kerani_df.empty:
            return {'employees': {}, 'totals': {field: 0 for field in comparison_fields}}
        
        # Identifikasi duplikasi TRANSNO
        duplicate_transno = kerani_df.groupby('TRANSNO').size()
        duplicate_transno = duplicate_transno[duplicate_transno > 1].index.tolist()
        
        employees_data = {}
        
        for emp_id in kerani_df['EMPID'].unique():
            if pd.isna(emp_id):
                continue
                
            emp_id_str = str(emp_id).strip()
            emp_name = employee_mapping.get(emp_id_str, f"Unknown ({emp_id_str})")
            
            emp_data = kerani_df[kerani_df['EMPID'] == emp_id]
            
            # Hitung total dan perbedaan untuk employee ini
            totals = {}
            differences = {}
            
            for field in comparison_fields:
                if field in emp_data.columns:
                    totals[field] = emp_data[field].sum()
                    
                    # Hitung perbedaan dari duplikasi
                    emp_duplicates = emp_data[emp_data['TRANSNO'].isin(duplicate_transno)]
                    if not emp_duplicates.empty:
                        # Group by TRANSNO dan hitung perbedaan
                        diff_sum = 0
                        for transno in emp_duplicates['TRANSNO'].unique():
                            transno_data = emp_duplicates[emp_duplicates['TRANSNO'] == transno]
                            if len(transno_data) > 1:
                                values = transno_data[field].values
                                diff_sum += abs(max(values) - min(values))
                        differences[field] = diff_sum
                    else:
                        differences[field] = 0
                else:
                    totals[field] = 0
                    differences[field] = 0
            
            employees_data[emp_id_str] = {
                'employee_id': emp_id_str,
                'employee_name': emp_name,
                'totals': totals,
                'differences': differences
            }
        
        # Hitung total keseluruhan
        overall_totals = {}
        for field in comparison_fields:
            overall_totals[field] = sum(emp['totals'][field] for emp in employees_data.values())
        
        return {
            'employees': employees_data,
            'totals': overall_totals
        }
    
    def _calculate_mandor_data(self, df: pd.DataFrame, employee_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Hitung data mandor berdasarkan RECORDTAG P1.
        
        Args:
            df: DataFrame data FFB
            employee_mapping: Mapping employee ID ke nama
        
        Returns:
            Dict: Data mandor
        """
        comparison_fields = self.template_config['calculation_logic']['duplicate_handling']['comparison_fields']
        
        # Filter data P1 (mandor)
        mandor_df = df[df['RECORDTAG'] == 'P1'].copy()
        
        if mandor_df.empty:
            return {'employees': {}, 'totals': {field: 0 for field in comparison_fields}}
        
        employees_data = {}
        
        # Group by EMPID
        for emp_id in mandor_df['EMPID'].unique():
            if pd.isna(emp_id):
                continue
                
            emp_id_str = str(emp_id).strip()
            emp_name = employee_mapping.get(emp_id_str, f"Unknown ({emp_id_str})")
            
            emp_data = mandor_df[mandor_df['EMPID'] == emp_id]
            
            # Hitung total untuk employee ini
            totals = {}
            for field in comparison_fields:
                if field in emp_data.columns:
                    totals[field] = emp_data[field].sum()
                else:
                    totals[field] = 0
            
            employees_data[emp_id_str] = {
                'employee_id': emp_id_str,
                'employee_name': emp_name,
                'totals': totals
            }
        
        # Hitung total keseluruhan
        overall_totals = {}
        for field in comparison_fields:
            overall_totals[field] = sum(emp['totals'][field] for emp in employees_data.values())
        
        return {
            'employees': employees_data,
            'totals': overall_totals
        }
    
    def _calculate_asisten_data(self, df: pd.DataFrame, employee_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Hitung data asisten berdasarkan RECORDTAG P5.
        
        Args:
            df: DataFrame data FFB
            employee_mapping: Mapping employee ID ke nama
        
        Returns:
            Dict: Data asisten
        """
        comparison_fields = self.template_config['calculation_logic']['duplicate_handling']['comparison_fields']
        
        # Filter data P5 (asisten)
        asisten_df = df[df['RECORDTAG'] == 'P5'].copy()
        
        if asisten_df.empty:
            return {'employees': {}, 'totals': {field: 0 for field in comparison_fields}}
        
        employees_data = {}
        
        # Group by EMPID
        for emp_id in asisten_df['EMPID'].unique():
            if pd.isna(emp_id):
                continue
                
            emp_id_str = str(emp_id).strip()
            emp_name = employee_mapping.get(emp_id_str, f"Unknown ({emp_id_str})")
            
            emp_data = asisten_df[asisten_df['EMPID'] == emp_id]
            
            # Hitung total untuk employee ini
            totals = {}
            for field in comparison_fields:
                if field in emp_data.columns:
                    totals[field] = emp_data[field].sum()
                else:
                    totals[field] = 0
            
            employees_data[emp_id_str] = {
                'employee_id': emp_id_str,
                'employee_name': emp_name,
                'totals': totals
            }
        
        # Hitung total keseluruhan
        overall_totals = {}
        for field in comparison_fields:
            overall_totals[field] = sum(emp['totals'][field] for emp in employees_data.values())
        
        return {
            'employees': employees_data,
            'totals': overall_totals
        }
    
    def _calculate_verification_rates(self, kerani_data: Dict, mandor_data: Dict, asisten_data: Dict) -> Dict[str, Any]:
        """
        Hitung tingkat verifikasi dan perbedaan.
        
        Args:
            kerani_data: Data kerani
            mandor_data: Data mandor
            asisten_data: Data asisten
        
        Returns:
            Dict: Tingkat verifikasi
        """
        comparison_fields = self.template_config['calculation_logic']['duplicate_handling']['comparison_fields']
        
        rates = {}
        
        for field in comparison_fields:
            kerani_total = kerani_data['totals'].get(field, 0)
            mandor_total = mandor_data['totals'].get(field, 0)
            asisten_total = asisten_data['totals'].get(field, 0)
            
            # Hitung perbedaan
            kerani_mandor_diff = abs(kerani_total - mandor_total)
            kerani_asisten_diff = abs(kerani_total - asisten_total)
            mandor_asisten_diff = abs(mandor_total - asisten_total)
            
            # Hitung persentase perbedaan
            kerani_mandor_pct = (kerani_mandor_diff / max(kerani_total, 1)) * 100
            kerani_asisten_pct = (kerani_asisten_diff / max(kerani_total, 1)) * 100
            mandor_asisten_pct = (mandor_asisten_diff / max(mandor_total, 1)) * 100
            
            rates[field] = {
                'kerani_total': kerani_total,
                'mandor_total': mandor_total,
                'asisten_total': asisten_total,
                'kerani_mandor_diff': kerani_mandor_diff,
                'kerani_asisten_diff': kerani_asisten_diff,
                'mandor_asisten_diff': mandor_asisten_diff,
                'kerani_mandor_pct': kerani_mandor_pct,
                'kerani_asisten_pct': kerani_asisten_pct,
                'mandor_asisten_pct': mandor_asisten_pct
            }
        
        return rates
    
    def _identify_differences(self, kerani_data: Dict, mandor_data: Dict, asisten_data: Dict) -> List[Dict]:
        """
        Identifikasi perbedaan yang signifikan.
        
        Args:
            kerani_data: Data kerani
            mandor_data: Data mandor
            asisten_data: Data asisten
        
        Returns:
            List: Daftar perbedaan
        """
        differences = []
        comparison_fields = self.template_config['calculation_logic']['duplicate_handling']['comparison_fields']
        tolerance = self.template_config['calculation_logic']['verification_calculation']['tolerance']
        
        for field in comparison_fields:
            kerani_total = kerani_data['totals'].get(field, 0)
            mandor_total = mandor_data['totals'].get(field, 0)
            asisten_total = asisten_data['totals'].get(field, 0)
            
            # Check perbedaan kerani vs mandor
            diff = abs(kerani_total - mandor_total)
            pct_diff = (diff / max(kerani_total, 1)) * 100
            
            if diff > tolerance['absolute'] and pct_diff > tolerance['percentage']:
                differences.append({
                    'field': field,
                    'type': 'kerani_vs_mandor',
                    'kerani_value': kerani_total,
                    'mandor_value': mandor_total,
                    'difference': diff,
                    'percentage_diff': pct_diff
                })
            
            # Check perbedaan kerani vs asisten
            diff = abs(kerani_total - asisten_total)
            pct_diff = (diff / max(kerani_total, 1)) * 100
            
            if diff > tolerance['absolute'] and pct_diff > tolerance['percentage']:
                differences.append({
                    'field': field,
                    'type': 'kerani_vs_asisten',
                    'kerani_value': kerani_total,
                    'asisten_value': asisten_total,
                    'difference': diff,
                    'percentage_diff': pct_diff
                })
        
        return differences
    
    def _create_empty_result(self, division: str, table_name: str) -> Dict[str, Any]:
        """
        Buat hasil kosong untuk divisi tanpa data.
        
        Args:
            division: Nama divisi
            table_name: Nama tabel
        
        Returns:
            Dict: Hasil kosong
        """
        comparison_fields = self.template_config['calculation_logic']['duplicate_handling']['comparison_fields']
        empty_totals = {field: 0 for field in comparison_fields}
        
        return {
            'division': division,
            'table_name': table_name,
            'kerani_data': {'employees': {}, 'totals': empty_totals},
            'mandor_data': {'employees': {}, 'totals': empty_totals},
            'asisten_data': {'employees': {}, 'totals': empty_totals},
            'verification_rates': {},
            'differences': [],
            'summary': {
                'total_records': 0,
                'unique_employees': 0,
                'unique_transno': 0,
                'special_filter_applied': False
            }
        }
    
    def run_verification(self, start_date: str, end_date: str, target_divisions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Jalankan verifikasi transaksi lengkap.
        
        Args:
            start_date: Tanggal mulai (format YYYYMMDD)
            end_date: Tanggal akhir (format YYYYMMDD)
            target_divisions: Daftar divisi target (opsional, jika None akan memproses semua)
        
        Returns:
            Dict: Hasil verifikasi lengkap
        """
        self.logger.info(f"Memulai verifikasi transaksi dari {start_date} sampai {end_date}")
        
        if not self.connection:
            raise ValueError("Koneksi database belum dibuat.")
        
        # Dapatkan daftar tabel
        tables = self.get_division_tables(start_date, end_date)
        if not tables:
            self.logger.warning("Tidak ada tabel FFBSCANNERDATA ditemukan")
            return {'divisions': {}, 'summary': {'total_divisions': 0, 'total_tables': 0}}
        
        # Dapatkan daftar divisi
        all_divisions = self.get_divisions(tables)
        if target_divisions:
            divisions = [d for d in all_divisions if d in target_divisions]
        else:
            divisions = all_divisions
        
        if not divisions:
            self.logger.warning("Tidak ada divisi ditemukan")
            return {'divisions': {}, 'summary': {'total_divisions': 0, 'total_tables': len(tables)}}
        
        # Tentukan bulan untuk filter khusus
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        month = start_dt.month
        
        # Proses setiap divisi
        results = {}
        
        for division in divisions:
            self.logger.info(f"Memproses divisi: {division}")
            
            # Cari tabel yang sesuai untuk divisi ini
            division_results = []
            
            for table in tables:
                try:
                    result = self.analyze_division(division, table, month)
                    if result['summary']['total_records'] > 0:
                        division_results.append(result)
                except Exception as e:
                    self.logger.error(f"Error menganalisis divisi {division} di tabel {table}: {e}")
                    continue
            
            if division_results:
                results[division] = division_results
        
        # Buat summary
        summary = {
            'total_divisions': len(results),
            'total_tables': len(tables),
            'processed_divisions': list(results.keys()),
            'start_date': start_date,
            'end_date': end_date,
            'special_filter_month': month if month == 5 else None
        }
        
        self.logger.info(f"Verifikasi selesai. Diproses {len(results)} divisi dari {len(tables)} tabel")
        
        return {
            'divisions': results,
            'summary': summary
        }


if __name__ == "__main__":
    # Test template
    print("=== Transaction Verification Template Test ===")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize template
        template = TransactionVerificationTemplate()
        print(f"Template loaded: {template.template_config['template_info']['name']}")
        print(f"Version: {template.template_config['template_info']['version']}")
        
        # Test database config (akan error jika tidak ada config.json)
        try:
            db_config = DatabaseConfig.from_config_file()
            template.set_database_config(db_config)
            print(f"Database config loaded: {db_config.database_path}")
        except Exception as e:
            print(f"Database config error (expected): {e}")
        
        print("Template test completed successfully!")
        
    except Exception as e:
        print(f"Template test failed: {e}")
        raise