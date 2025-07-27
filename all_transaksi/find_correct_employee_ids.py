#!/usr/bin/env python3
"""
Script untuk mencari ID karyawan yang benar berdasarkan nama
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector
from datetime import date
import pandas as pd

def find_correct_employee_ids():
    """Mencari ID karyawan yang benar"""
    
    print("=== MENCARI ID KARYAWAN YANG BENAR ===\n")
    
    # Koneksi ke database Estate 1A
    db_path = r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB"
    
    try:
        connector = FirebirdConnector(db_path)
        if not connector.test_connection():
            print("❌ Koneksi database gagal")
            return
        
        print("✅ Koneksi database berhasil")
        
        # Get employee mapping
        emp_query = "SELECT ID, NAME FROM EMP"
        emp_result = connector.execute_query(emp_query)
        emp_df = connector.to_pandas(emp_result)
        employee_mapping = {}
        if not emp_df.empty:
            for _, row in emp_df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                employee_mapping[emp_id] = emp_name
        
        # Target names dari data pembanding
        target_names = [
            'DARWIS HERMAN SIANTURI',
            'DJULI DARTA',
            'ERLY',
            'IRWANSYAH',
            'SUHAYAT',
            'SURANTO',
            'ZULHARI'
        ]
        
        print("🔍 MENCARI ID BERDASARKAN NAMA:")
        found_employees = {}
        
        for target_name in target_names:
            print(f"\n🔍 Mencari: {target_name}")
            matches = []
            
            for emp_id, emp_name in employee_mapping.items():
                if target_name.upper() in emp_name.upper():
                    matches.append((emp_id, emp_name))
            
            if matches:
                print(f"  Ditemukan {len(matches)} matches:")
                for emp_id, emp_name in matches:
                    print(f"    ID: {emp_id} -> {emp_name}")
                    found_employees[emp_id] = emp_name
            else:
                print(f"  ❌ Tidak ditemukan")
        
        # Analisis data Mei 2025 untuk ID yang ditemukan
        start_date = '2025-05-01'
        end_date = '2025-05-31'
        month_num = 5
        ffb_table = f"FFBSCANNERDATA{month_num:02d}"
        
        # Query untuk mendapatkan data transaksi
        query = f"""
        SELECT a.SCANUSERID, a.RECORDTAG, a.TRANSSTATUS, COUNT(*) as TOTAL
        FROM {ffb_table} a
        WHERE a.TRANSDATE >= '{start_date}' 
            AND a.TRANSDATE <= '{end_date}'
            AND a.RECORDTAG = 'PM'
        GROUP BY a.SCANUSERID, a.RECORDTAG, a.TRANSSTATUS
        ORDER BY a.SCANUSERID, a.TRANSSTATUS
        """
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        print(f"\n📊 ANALISIS TRANSAKSI KERANI (PM) BULAN MEI 2025:")
        
        for emp_id, emp_name in found_employees.items():
            emp_id_int = int(emp_id)
            emp_transactions = df[df['SCANUSERID'] == emp_id_int]
            
            if not emp_transactions.empty:
                total_transactions = emp_transactions['TOTAL'].sum()
                print(f"\n👤 {emp_name} (ID: {emp_id}):")
                print(f"  Total transaksi Kerani: {total_transactions}")
                
                for _, row in emp_transactions.iterrows():
                    print(f"    Status {row['TRANSSTATUS']}: {row['TOTAL']} transaksi")
            else:
                print(f"\n👤 {emp_name} (ID: {emp_id}): Tidak ada transaksi Kerani")
        
        # Cari semua Kerani dengan transaksi terbanyak
        print(f"\n📊 TOP 10 KERANI DENGAN TRANSAKSI TERBANYAK:")
        kerani_summary = df.groupby('SCANUSERID')['TOTAL'].sum().sort_values(ascending=False).head(10)
        
        for emp_id_int, total in kerani_summary.items():
            emp_id_str = str(emp_id_int)
            emp_name = employee_mapping.get(emp_id_str, f"KARYAWAN-{emp_id_str}")
            print(f"  ID: {emp_id_str} -> {emp_name}: {total} transaksi")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_correct_employee_ids() 