#!/usr/bin/env python3
"""
Generate Excel report untuk analisis MANDOR per divisi dengan format yang diminta.
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

def generate_excel_report():
    """
    Generate laporan Excel dengan format seperti yang diminta user.
    """
    # Konfigurasi database
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    
    print("GENERATE LAPORAN EXCEL MANDOR PER DIVISI")
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
        
        # Generate Excel report
        print("Membuat laporan Excel...")
        
        # Create output directory
        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"laporan_mandor_per_divisi_corrected_05_2025_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # Sheet 1: Summary All Divisions
            summary_data = []
            
            for div_id, div_data in division_stats.items():
                if not div_data['div_name']:
                    continue
                    
                div_name = div_data['div_name']
                
                # Calculate totals
                total_kerani_trans = sum(emp['total'] for emp in div_data['kerani'].values())
                total_mandor_trans = sum(emp['total'] for emp in div_data['mandor'].values())
                total_asisten_trans = sum(emp['total'] for emp in div_data['asisten'].values())
                total_receipts = total_kerani_trans + total_mandor_trans + total_asisten_trans
                
                mandor_verification_pct = (total_mandor_trans / total_receipts * 100) if total_receipts > 0 else 0
                asisten_verification_pct = (total_asisten_trans / total_receipts * 100) if total_receipts > 0 else 0
                
                summary_data.append({
                    'Division': div_name,
                    'Division_ID': div_id,
                    'Total_Receipts': total_receipts,
                    'KERANI_Transactions': total_kerani_trans,
                    'MANDOR_Transactions': total_mandor_trans,
                    'ASISTEN_Transactions': total_asisten_trans,
                    'MANDOR_Verification_Rate': f"{mandor_verification_pct:.2f}%",
                    'ASISTEN_Verification_Rate': f"{asisten_verification_pct:.2f}%"
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary All Divisions', index=False)
            
            # Sheet per divisi (format seperti yang diminta)
            for div_id, div_data in division_stats.items():
                if not div_data['div_name']:
                    continue
                    
                div_name = div_data['div_name']
                
                # Buat data seperti format yang diminta
                division_data = []
                
                # KERANI data (Bunch Counter)
                for emp_id, emp_stats in div_data['kerani'].items():
                    division_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_stats['name'],
                        'Scanner_User_ID': emp_id,
                        'Role': 'KERANI',
                        'Conductor': 0,  # KERANI tidak melakukan conduct
                        'Assistant': 0,  # KERANI tidak melakukan assist
                        'Manager': 0,    # KERANI tidak melakukan manage
                        'Bunch_Counter': emp_stats['total']  # KERANI membuat transaksi
                    })
                
                # MANDOR data (Conductor)
                for emp_id, emp_stats in div_data['mandor'].items():
                    division_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_stats['name'],
                        'Scanner_User_ID': emp_id,
                        'Role': 'MANDOR',
                        'Conductor': emp_stats['total'],  # MANDOR melakukan conduct/verify
                        'Assistant': 0,
                        'Manager': 0,
                        'Bunch_Counter': 0
                    })
                
                # ASISTEN data (Assistant)
                for emp_id, emp_stats in div_data['asisten'].items():
                    division_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_stats['name'],
                        'Scanner_User_ID': emp_id,
                        'Role': 'ASISTEN',
                        'Conductor': 0,
                        'Assistant': emp_stats['total'],  # ASISTEN melakukan assist/verify
                        'Manager': 0,
                        'Bunch_Counter': 0
                    })
                
                if division_data:
                    division_df = pd.DataFrame(division_data)
                    
                    # Hitung total dan verification rates
                    total_receipts = sum(emp['total'] for role_data in div_data.values() if isinstance(role_data, dict) for emp in role_data.values() if isinstance(emp, dict) and 'total' in emp)
                    mandor_verified = sum(emp['total'] for emp in div_data['mandor'].values())
                    asisten_verified = sum(emp['total'] for emp in div_data['asisten'].values())
                    
                    mandor_verification_pct = (mandor_verified / total_receipts * 100) if total_receipts > 0 else 0
                    asisten_verification_pct = (asisten_verified / total_receipts * 100) if total_receipts > 0 else 0
                    
                    # Add summary rows
                    summary_row = pd.DataFrame([{
                        'Division': '',
                        'Scanner_User': f'Total Receipt: {total_receipts}',
                        'Scanner_User_ID': '',
                        'Role': '',
                        'Conductor': '',
                        'Assistant': '',
                        'Manager': '',
                        'Bunch_Counter': ''
                    }])
                    
                    verification_row = pd.DataFrame([{
                        'Division': '',
                        'Scanner_User': f'MANDOR Verification: {mandor_verification_pct:.2f}%',
                        'Scanner_User_ID': f'ASISTEN Verification: {asisten_verification_pct:.2f}%',
                        'Role': '',
                        'Conductor': '',
                        'Assistant': '',
                        'Manager': '',
                        'Bunch_Counter': ''
                    }])
                    
                    # Combine all data
                    final_df = pd.concat([division_df, summary_row, verification_row], ignore_index=True)
                    
                    # Clean sheet name
                    sheet_name = div_name.replace('/', '_').replace('\\', '_')[:31]
                    final_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Sheet 3: Detail Employee Mapping
            mapping_data = []
            for div_id, div_data in division_stats.items():
                if not div_data['div_name']:
                    continue
                    
                div_name = div_data['div_name']
                
                for role_name in ['kerani', 'mandor', 'asisten']:
                    role_data = div_data[role_name]
                    for emp_id, emp_stats in role_data.items():
                        verification_rate = (emp_stats['verified'] / emp_stats['total'] * 100) if emp_stats['total'] > 0 else 0
                        mapping_data.append({
                            'Division': div_name,
                            'Division_ID': div_id,
                            'Employee_ID': emp_id,
                            'Employee_Name': emp_stats['name'],
                            'Role': role_name.upper(),
                            'Total_Transactions': emp_stats['total'],
                            'Verified_Transactions': emp_stats['verified'],
                            'Verification_Rate': f"{verification_rate:.2f}%"
                        })
            
            mapping_df = pd.DataFrame(mapping_data)
            mapping_df.to_excel(writer, sheet_name='Employee Mapping Detail', index=False)
            
            # Sheet 4: Role Summary
            role_summary_data = []
            all_kerani = set()
            all_mandor = set()
            all_asisten = set()
            
            for div_data in division_stats.values():
                if not div_data['div_name']:
                    continue
                all_kerani.update(div_data['kerani'].keys())
                all_mandor.update(div_data['mandor'].keys())
                all_asisten.update(div_data['asisten'].keys())
            
            # Add role summary
            for emp_id in all_kerani:
                emp_name = employee_mapping.get(emp_id, f"EMPLOYEE-{emp_id}")
                role_summary_data.append({
                    'Employee_ID': emp_id,
                    'Employee_Name': emp_name,
                    'Role': 'KERANI',
                    'Divisions_Handled': ', '.join([div_data['div_name'] for div_data in division_stats.values() if emp_id in div_data['kerani']])
                })
            
            for emp_id in all_mandor:
                emp_name = employee_mapping.get(emp_id, f"EMPLOYEE-{emp_id}")
                role_summary_data.append({
                    'Employee_ID': emp_id,
                    'Employee_Name': emp_name,
                    'Role': 'MANDOR',
                    'Divisions_Handled': ', '.join([div_data['div_name'] for div_data in division_stats.values() if emp_id in div_data['mandor']])
                })
            
            for emp_id in all_asisten:
                emp_name = employee_mapping.get(emp_id, f"EMPLOYEE-{emp_id}")
                role_summary_data.append({
                    'Employee_ID': emp_id,
                    'Employee_Name': emp_name,
                    'Role': 'ASISTEN',
                    'Divisions_Handled': ', '.join([div_data['div_name'] for div_data in division_stats.values() if emp_id in div_data['asisten']])
                })
            
            role_summary_df = pd.DataFrame(role_summary_data)
            role_summary_df.to_excel(writer, sheet_name='Role Summary', index=False)
        
        print(f"Laporan Excel berhasil dibuat: {filepath}")
        
        # Print summary
        print("\n" + "="*80)
        print("RINGKASAN LAPORAN")
        print("="*80)
        
        total_divisions = len([div for div in division_stats.values() if div['div_name']])
        total_kerani = len(all_kerani)
        total_mandor = len(all_mandor)
        total_asisten = len(all_asisten)
        
        print(f"Total Divisi: {total_divisions}")
        print(f"Total KERANI: {total_kerani} orang")
        print(f"Total MANDOR: {total_mandor} orang")
        print(f"Total ASISTEN: {total_asisten} orang")
        
        print(f"\nFile laporan: {filepath}")
        print("Laporan berisi 4 sheet:")
        print("1. Summary All Divisions - Ringkasan per divisi")
        print("2. [Nama Divisi] - Detail per divisi (format seperti yang diminta)")
        print("3. Employee Mapping Detail - Detail mapping karyawan")
        print("4. Role Summary - Ringkasan role dan divisi yang ditangani")
        
        return filepath
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_excel_report() 