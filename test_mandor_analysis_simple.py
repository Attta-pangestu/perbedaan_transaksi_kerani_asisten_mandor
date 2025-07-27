#!/usr/bin/env python3
"""
Script sederhana untuk analisis MANDOR dengan query yang sudah terbukti bekerja.
"""

import sys
import os
import pandas as pd
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), 'all_transaksi'))

from firebird_connector import FirebirdConnector

def get_employee_role_corrected(recordtag):
    """
    Menentukan role karyawan berdasarkan RECORDTAG yang benar.
    P1 = MANDOR, P5 = ASISTEN, PM = KERANI
    """
    if not recordtag:
        return 'LAINNYA'
    
    recordtag_str = str(recordtag).strip().upper()
    
    role_mapping = {
        'PM': 'KERANI',    # Plantation Manager/Kerani
        'P1': 'MANDOR',    # MANDOR (diperbaiki)
        'P5': 'ASISTEN',   # ASISTEN (diperbaiki)
    }
    
    return role_mapping.get(recordtag_str, 'LAINNYA')

def analyze_mandor_corrected():
    """
    Analisis MANDOR yang diperbaiki dengan role definition yang benar.
    """
    # Konfigurasi database
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    
    print("ANALISIS MANDOR DENGAN ROLE DEFINITION YANG BENAR")
    print("="*60)
    print("Role Definition:")
    print("- P1 = MANDOR")
    print("- P5 = ASISTEN") 
    print("- PM = KERANI")
    print("="*60)
    
    # Setup database connection
    print("Menghubungkan ke database...")
    connector = FirebirdConnector(DB_PATH)
    
    if not connector.test_connection():
        print("Koneksi database gagal!")
        return
    
    print("Koneksi database berhasil")
    
    # Get employee mapping
    print("Mendapatkan mapping karyawan...")
    emp_query = "SELECT ID, NAME FROM EMP"
    
    try:
        result = connector.execute_query(emp_query)
        emp_df = connector.to_pandas(result)
        
        employee_mapping = {}
        if not emp_df.empty:
            for _, row in emp_df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                if emp_id and emp_name:
                    employee_mapping[emp_id] = emp_name
            print(f"Berhasil mapping {len(employee_mapping)} karyawan")
        
    except Exception as e:
        print(f"Error mengambil data EMP: {e}")
        employee_mapping = {}
    
    # Query untuk mendapatkan semua transaksi dengan divisi
    print("Mengambil data transaksi...")
    query = """
    SELECT 
        a.ID, 
        a.SCANUSERID, 
        a.RECORDTAG, 
        a.TRANSSTATUS, 
        a.TRANSNO, 
        a.TRANSDATE,
        b.DIVID,
        c.DIVNAME
    FROM 
        FFBSCANNERDATA05 a
    LEFT JOIN 
        OCFIELD b ON a.FIELDID = b.ID
    LEFT JOIN 
        CRDIVISION c ON b.DIVID = c.ID
    WHERE 
        a.TRANSDATE >= '2025-05-01'
        AND a.TRANSDATE < '2025-06-01'
        AND a.RECORDTAG IN ('PM', 'P1', 'P5')
    ORDER BY c.DIVNAME, a.SCANUSERID, a.TRANSDATE
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df.empty:
            print("Tidak ada data transaksi ditemukan!")
            return
        
        print(f"Berhasil mengambil {len(df)} transaksi")
        
        # Analisis per divisi
        division_stats = defaultdict(lambda: {
            'div_name': '',
            'kerani': defaultdict(lambda: {'total': 0, 'verified': 0, 'name': ''}),
            'mandor': defaultdict(lambda: {'total': 0, 'verified': 0, 'name': ''}),
            'asisten': defaultdict(lambda: {'total': 0, 'verified': 0, 'name': ''})
        })
        
        # Process each transaction
        for _, row in df.iterrows():
            try:
                scanner_user_id = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                recordtag = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
                transstatus = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
                div_id = str(row.iloc[6]).strip() if pd.notna(row.iloc[6]) else ''
                div_name = str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else 'Unknown'
                
                if not scanner_user_id or not recordtag:
                    continue
                
                # Get employee name
                emp_name = employee_mapping.get(scanner_user_id, f"EMPLOYEE-{scanner_user_id}")
                
                # Determine role
                role = get_employee_role_corrected(recordtag)
                
                if role in ['KERANI', 'MANDOR', 'ASISTEN']:
                    division_stats[div_id]['div_name'] = div_name
                    
                    # Update statistics
                    role_key = role.lower()
                    division_stats[div_id][role_key][scanner_user_id]['total'] += 1
                    division_stats[div_id][role_key][scanner_user_id]['name'] = emp_name
                    
                    # Count verifications (status 704)
                    if transstatus == '704':
                        division_stats[div_id][role_key][scanner_user_id]['verified'] += 1
                        
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        # Generate report
        print("\n" + "="*80)
        print("LAPORAN ANALISIS MANDOR PER DIVISI")
        print("="*80)
        
        total_divisions = 0
        total_kerani = set()
        total_mandor = set()
        total_asisten = set()
        
        for div_id, div_data in division_stats.items():
            if not div_data['div_name']:
                continue
                
            total_divisions += 1
            div_name = div_data['div_name']
            
            print(f"\nDIVISI: {div_name} (ID: {div_id})")
            print("-" * 60)
            
            # KERANI
            kerani_data = div_data['kerani']
            if kerani_data:
                print("KERANI:")
                for emp_id, emp_stats in kerani_data.items():
                    total_kerani.add(emp_id)
                    verification_rate = (emp_stats['verified'] / emp_stats['total'] * 100) if emp_stats['total'] > 0 else 0
                    print(f"  - {emp_stats['name']} (ID: {emp_id})")
                    print(f"    Total Transaksi: {emp_stats['total']}")
                    print(f"    Verified: {emp_stats['verified']} ({verification_rate:.1f}%)")
            
            # MANDOR
            mandor_data = div_data['mandor']
            if mandor_data:
                print("MANDOR:")
                for emp_id, emp_stats in mandor_data.items():
                    total_mandor.add(emp_id)
                    verification_rate = (emp_stats['verified'] / emp_stats['total'] * 100) if emp_stats['total'] > 0 else 0
                    print(f"  - {emp_stats['name']} (ID: {emp_id})")
                    print(f"    Total Verifikasi: {emp_stats['total']}")
                    print(f"    Verified Status: {emp_stats['verified']} ({verification_rate:.1f}%)")
            
            # ASISTEN
            asisten_data = div_data['asisten']
            if asisten_data:
                print("ASISTEN:")
                for emp_id, emp_stats in asisten_data.items():
                    total_asisten.add(emp_id)
                    verification_rate = (emp_stats['verified'] / emp_stats['total'] * 100) if emp_stats['total'] > 0 else 0
                    print(f"  - {emp_stats['name']} (ID: {emp_id})")
                    print(f"    Total Verifikasi: {emp_stats['total']}")
                    print(f"    Verified Status: {emp_stats['verified']} ({verification_rate:.1f}%)")
            
            # Calculate division totals
            total_kerani_trans = sum(emp['total'] for emp in kerani_data.values())
            total_mandor_trans = sum(emp['total'] for emp in mandor_data.values())
            total_asisten_trans = sum(emp['total'] for emp in asisten_data.values())
            total_div_trans = total_kerani_trans + total_mandor_trans + total_asisten_trans
            
            mandor_verification_pct = (total_mandor_trans / total_div_trans * 100) if total_div_trans > 0 else 0
            asisten_verification_pct = (total_asisten_trans / total_div_trans * 100) if total_div_trans > 0 else 0
            
            print(f"\nRINGKASAN DIVISI {div_name}:")
            print(f"  Total Receipts: {total_div_trans}")
            print(f"  MANDOR Verification: {mandor_verification_pct:.2f}%")
            print(f"  ASISTEN Verification: {asisten_verification_pct:.2f}%")
        
        # Overall summary
        print("\n" + "="*80)
        print("RINGKASAN KESELURUHAN")
        print("="*80)
        print(f"Total Divisi: {total_divisions}")
        print(f"Total KERANI: {len(total_kerani)} orang")
        print(f"Total MANDOR: {len(total_mandor)} orang")
        print(f"Total ASISTEN: {len(total_asisten)} orang")
        
        # Detail employees
        print(f"\nDETAIL KARYAWAN:")
        print(f"KERANI: {[employee_mapping.get(emp_id, f'EMPLOYEE-{emp_id}') for emp_id in total_kerani]}")
        print(f"MANDOR: {[employee_mapping.get(emp_id, f'EMPLOYEE-{emp_id}') for emp_id in total_mandor]}")
        print(f"ASISTEN: {[employee_mapping.get(emp_id, f'EMPLOYEE-{emp_id}') for emp_id in total_asisten]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_mandor_corrected() 