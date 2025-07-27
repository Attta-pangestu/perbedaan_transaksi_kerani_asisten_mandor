"""
Script untuk testing koneksi database dan validasi setup 
sebelum menjalankan analisis kinerja karyawan.
"""
import os
import sys
import pandas as pd
from datetime import datetime, date

# Tambahkan parent directory ke path untuk import modul
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from firebird_connector import FirebirdConnector
    print("✓ Import FirebirdConnector berhasil")
except ImportError as e:
    print(f"✗ Error import FirebirdConnector: {e}")
    sys.exit(1)

def test_python_dependencies():
    """Test ketersediaan dependencies Python."""
    print("\n" + "="*50)
    print("TESTING PYTHON DEPENDENCIES")
    print("="*50)
    
    dependencies = [
        ('pandas', 'Data manipulation'),
        ('matplotlib', 'Plotting dan visualisasi'),
        ('seaborn', 'Statistical plotting'),
        ('openpyxl', 'Excel file handling'),
        ('reportlab', 'PDF generation (optional)'),
        ('numpy', 'Numerical operations')
    ]
    
    missing_deps = []
    
    for dep_name, description in dependencies:
        try:
            __import__(dep_name)
            print(f"✓ {dep_name} - {description}")
        except ImportError:
            print(f"✗ {dep_name} - {description} (MISSING)")
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"\nDependencies yang hilang: {', '.join(missing_deps)}")
        print(f"Install dengan: pip install {' '.join(missing_deps)}")
        return False
    else:
        print("\n✓ Semua dependencies tersedia!")
        return True

def test_database_connection(db_path=None):
    """Test koneksi ke database Firebird."""
    print("\n" + "="*50)
    print("TESTING DATABASE CONNECTION")
    print("="*50)
    
    # Default database path
    if not db_path:
        db_path = r'D:\IFESS Firebird Database\MILL04.FDB'
    
    print(f"Database path: {db_path}")
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"✗ File database tidak ditemukan: {db_path}")
        return False
    
    print("✓ File database ditemukan")
    
    try:
        # Test koneksi
        connector = FirebirdConnector(db_path)
        
        if connector.test_connection():
            print("✓ Koneksi database berhasil")
            return connector
        else:
            print("✗ Koneksi database gagal")
            return None
            
    except Exception as e:
        print(f"✗ Error saat koneksi database: {e}")
        return None

def test_employee_mapping(connector):
    """Test pengambilan data mapping karyawan."""
    print("\n" + "="*50)
    print("TESTING EMPLOYEE MAPPING")
    print("="*50)
    
    try:
        query = "SELECT COUNT(*) as TOTAL FROM EMP"
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if not df.empty:
            total_emp = df.iloc[0, 0] if len(df.columns) > 0 else 0
            print(f"✓ Tabel EMP ditemukan dengan {total_emp} record")
            
            # Test sample data
            query_sample = "SELECT FIRST 5 ID, NAME FROM EMP"
            result_sample = connector.execute_query(query_sample)
            df_sample = connector.to_pandas(result_sample)
            
            if not df_sample.empty:
                print("✓ Sample data karyawan:")
                for i, row in df_sample.iterrows():
                    emp_id = row.iloc[0] if len(row) > 0 else 'N/A'
                    emp_name = row.iloc[1] if len(row) > 1 else 'N/A'
                    print(f"   - ID: {emp_id}, Name: {emp_name}")
            
            return True
        else:
            print("✗ Tabel EMP kosong atau tidak dapat diakses")
            return False
            
    except Exception as e:
        print(f"✗ Error saat mengakses tabel EMP: {e}")
        print("   Tabel EMP mungkin tidak tersedia, akan menggunakan mapping default")
        return False

def test_transaction_data(connector):
    """Test ketersediaan data transaksi."""
    print("\n" + "="*50)
    print("TESTING TRANSACTION DATA")
    print("="*50)
    
    # Test bulan ini
    current_month = date.today().month
    ffb_table = f"FFBSCANNERDATA{current_month:02d}"
    
    try:
        query = f"SELECT COUNT(*) as TOTAL FROM {ffb_table}"
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if not df.empty:
            total_trans = df.iloc[0, 0] if len(df.columns) > 0 else 0
            print(f"✓ Tabel {ffb_table} ditemukan dengan {total_trans} record")
            
            if total_trans > 0:
                # Test sample data
                query_sample = f"""
                SELECT FIRST 3 TRANSNO, SCANUSERID, TRANSSTATUS, TRANSDATE 
                FROM {ffb_table} 
                WHERE TRANSDATE >= '{date.today().strftime('%Y-%m-01')}'
                """
                result_sample = connector.execute_query(query_sample)
                df_sample = connector.to_pandas(result_sample)
                
                if not df_sample.empty:
                    print("✓ Sample data transaksi:")
                    for i, row in df_sample.iterrows():
                        transno = row.iloc[0] if len(row) > 0 else 'N/A'
                        userid = row.iloc[1] if len(row) > 1 else 'N/A'
                        status = row.iloc[2] if len(row) > 2 else 'N/A'
                        transdate = row.iloc[3] if len(row) > 3 else 'N/A'
                        print(f"   - TRANSNO: {transno}, USER: {userid}, STATUS: {status}, DATE: {transdate}")
                
                return True
            else:
                print(f"⚠ Tabel {ffb_table} tidak memiliki data untuk bulan ini")
                return False
        else:
            print(f"✗ Tabel {ffb_table} tidak ditemukan atau tidak dapat diakses")
            return False
            
    except Exception as e:
        print(f"✗ Error saat mengakses tabel {ffb_table}: {e}")
        
        # Coba tabel alternatif
        alt_tables = ['FFBSCANNERDATA04', 'FFBSCANNERDATA05', 'FFBSCANNERDATA06']
        for table in alt_tables:
            try:
                query_alt = f"SELECT COUNT(*) as TOTAL FROM {table}"
                result_alt = connector.execute_query(query_alt)
                df_alt = connector.to_pandas(result_alt)
                
                if not df_alt.empty:
                    total_alt = df_alt.iloc[0, 0] if len(df_alt.columns) > 0 else 0
                    if total_alt > 0:
                        print(f"✓ Tabel alternatif {table} ditemukan dengan {total_alt} record")
                        return True
                        
            except:
                continue
        
        print("✗ Tidak ada tabel transaksi yang dapat diakses")
        return False

def test_output_directory():
    """Test direktori output."""
    print("\n" + "="*50)
    print("TESTING OUTPUT DIRECTORY")
    print("="*50)
    
    output_dir = os.path.join(os.path.dirname(__file__), 'reports')
    
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✓ Direktori output dibuat: {output_dir}")
        else:
            print(f"✓ Direktori output sudah ada: {output_dir}")
        
        # Test write permission
        test_file = os.path.join(output_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        print("✓ Permission menulis ke direktori output OK")
        return True
        
    except Exception as e:
        print(f"✗ Error dengan direktori output: {e}")
        return False

def run_sample_analysis(connector):
    """Jalankan analisis sample untuk testing."""
    print("\n" + "="*50)
    print("RUNNING SAMPLE ANALYSIS")
    print("="*50)
    
    try:
        # Import functions dari script utama
        from analisis_per_karyawan import (
            get_employee_mapping, 
            get_transstatus_mapping,
            get_all_transactions_data,
            analyze_employee_performance
        )
        
        print("✓ Import fungsi analisis berhasil")
        
        # Test mapping
        employee_mapping = get_employee_mapping(connector)
        print(f"✓ Employee mapping: {len(employee_mapping)-1} entries")
        
        transstatus_mapping = get_transstatus_mapping(connector)
        print(f"✓ Status mapping: {len(transstatus_mapping)-1} entries")
        
        # Test data dengan limit kecil
        today = date.today()
        start_date = date(today.year, today.month, 1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        print(f"✓ Testing data dari {start_date} hingga {end_date} (limit: 100)")
        
        df = get_all_transactions_data(connector, start_date, end_date, limit=100)
        
        if not df.empty:
            print(f"✓ Sample data retrieved: {len(df)} records")
            
            # Test analisis
            verification_stats, employee_stats = analyze_employee_performance(
                df, employee_mapping, transstatus_mapping)
            
            if verification_stats:
                print(f"✓ Analisis berhasil: {len(verification_stats)} karyawan dianalisis")
                
                # Tampilkan top 3 hasil
                sorted_employees = sorted(verification_stats.items(), 
                                        key=lambda x: x[1]['total_created'], reverse=True)[:3]
                
                print("✓ Top 3 karyawan berdasarkan total transaksi:")
                for i, (name, stats) in enumerate(sorted_employees, 1):
                    print(f"   {i}. {name}: {stats['total_created']} transaksi, "
                          f"verifikasi {stats['verification_rate']:.1f}%")
                
                return True
            else:
                print("✗ Analisis gagal - tidak ada statistik yang dihasilkan")
                return False
        else:
            print("✗ Tidak ada sample data yang ditemukan")
            return False
            
    except Exception as e:
        print(f"✗ Error saat sample analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fungsi utama testing."""
    print("="*60)
    print("      TESTING SETUP ANALISIS KINERJA KARYAWAN")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Python Dependencies
    results['dependencies'] = test_python_dependencies()
    
    # Test 2: Database Connection
    connector = test_database_connection()
    results['database'] = connector is not None
    
    if connector:
        # Test 3: Employee Mapping
        results['employee_mapping'] = test_employee_mapping(connector)
        
        # Test 4: Transaction Data
        results['transaction_data'] = test_transaction_data(connector)
        
        # Test 5: Sample Analysis
        if results['transaction_data']:
            results['sample_analysis'] = run_sample_analysis(connector)
        else:
            results['sample_analysis'] = False
    else:
        results['employee_mapping'] = False
        results['transaction_data'] = False
        results['sample_analysis'] = False
    
    # Test 6: Output Directory
    results['output_directory'] = test_output_directory()
    
    # Summary
    print("\n" + "="*60)
    print("                    RINGKASAN TESTING")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name.replace('_', ' ').title():.<40} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("🎉 SEMUA TEST BERHASIL! Sistem siap digunakan.")
        print("\nUntuk menjalankan analisis:")
        print("1. Double-click run_analisis_karyawan.bat")
        print("2. Atau: python analisis_per_karyawan.py")
    else:
        print("⚠ BEBERAPA TEST GAGAL! Perbaiki masalah di atas sebelum menjalankan analisis.")
        
        # Saran perbaikan
        print("\nSaran perbaikan:")
        if not results['dependencies']:
            print("- Install missing Python dependencies")
        if not results['database']:
            print("- Periksa koneksi database dan path file")
        if not results['transaction_data']:
            print("- Pastikan ada data transaksi untuk periode yang dianalisis")
        if not results['output_directory']:
            print("- Periksa permission direktori output")
    
    print("\nUntuk informasi lengkap, baca README_ANALISIS_KARYAWAN.md")

if __name__ == "__main__":
    main()