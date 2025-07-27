#!/usr/bin/env python3
"""
Analisis Detail MANDOR - Sistem Monitoring Transaksi FFB IFESS

Script ini menganalisis aktivitas verifikasi MANDOR dengan fokus pada:
1. Jumlah transaksi verifikasi per MANDOR per bulan
2. Divisi tempat MANDOR bekerja  
3. Persentase verifikasi MANDOR vs total transaksi KERANI di divisi
4. Pasangan MANDOR-KERANI per divisi
5. Detail breakdown transaksi dan verifikasi per pasangan

Author: AI Assistant
Date: 2025-06-26
"""

import os
import sys
import pandas as pd
from datetime import datetime
from collections import defaultdict
import calendar

# Import dari modul yang sudah ada
from firebird_connector import FirebirdConnector
from analisis_per_karyawan import (
    get_employee_mapping, get_transstatus_mapping, get_division_mapping,
    get_employee_role_from_recordtag, check_transaction_verification_by_duplicates
)

def get_detailed_transaction_data_mandor(connector, start_date, end_date, month):
    """
    Mengambil data transaksi detail untuk analisis MANDOR.
    """
    table_name = f"FFBSCANNERDATA{month:02d}"
    
    print(f"Mengambil data dari {table_name}...")
    print(f"Periode: {start_date} sampai {end_date}")
    
    query = f"""
    SELECT 
        a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
        a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
        a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
        a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
        a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
        b.DIVID, c.DIVNAME, c.DIVCODE
    FROM {table_name} a
    LEFT JOIN OCFIELD b ON a.FIELDID = b.ID AND a.OCID = b.OCID
    LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
    WHERE a.TRANSDATE >= '{start_date}' 
    AND a.TRANSDATE < '{end_date}'
    ORDER BY c.DIVNAME, a.TRANSNO, a.TRANSDATE, a.TRANSTIME
    """
    
    result = connector.execute_query(query)
    df = connector.to_pandas(result)
    
    if df is not None and not df.empty:
        print(f"Data berhasil diambil: {len(df)} record")
        return df
    else:
        print("Gagal mengambil data atau data kosong")
        return pd.DataFrame()

def analyze_mandor_activities_detailed(df, employee_mapping, transstatus_mapping, division_mapping):
    """
    Menganalisis aktivitas MANDOR secara detail dengan fokus pada verifikasi.
    """
    print("Memulai analisis detail aktivitas MANDOR...")
    
    # Column mapping based on headers from query result
    # Headers: ['ID', 'SCANUSERID', 'OCID', 'WORKERID', 'CARRIERID', 'FIELDID', 'TASKNO', 'RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT', 'TRANSNO', 'TRANSDATE', 'TRANSTIME', 'UPLOADDATETIME', 'RECORDTAG', 'TRANSSTATUS', 'TRANSTYPE', 'LASTUSER', 'LASTUPDATED', 'OVERRIPEBCH', 'UNDERRIPEBCH', 'ABNORMALBCH', 'LOOSEFRUIT2', 'DIVID', 'DIVNAME', 'DIVCODE']
    scanuserid_col = 1   # SCANUSERID
    recordtag_col = 18   # RECORDTAG  
    transstatus_col = 19 # TRANSSTATUS
    transno_col = 14     # TRANSNO
    transdate_col = 15   # TRANSDATE
    divname_col = 28     # DIVNAME
    
    print(f"DEBUG: Column mapping - SCANUSERID: {scanuserid_col}, RECORDTAG: {recordtag_col}, TRANSSTATUS: {transstatus_col}")
    print(f"DEBUG: Sample data - RECORDTAG values in first 10 rows:")
    for i in range(min(10, len(df))):
        recordtag_val = str(df.iloc[i, recordtag_col]).strip() if pd.notna(df.iloc[i, recordtag_col]) else ''
        scanuserid_val = str(df.iloc[i, scanuserid_col]).strip() if pd.notna(df.iloc[i, scanuserid_col]) else ''
        print(f"  Row {i}: SCANUSERID={scanuserid_val}, RECORDTAG={recordtag_val}")
    
    # Get verified transactions through duplicate detection
    verified_transactions = check_transaction_verification_by_duplicates(
        df, transno_col, transdate_col, recordtag_col, transstatus_col)
    
    print(f"Ditemukan {len(verified_transactions)} transaksi terverifikasi")
    
    # Data structures untuk analisis MANDOR
    mandor_activities = defaultdict(lambda: {
        'employee_id': '',
        'employee_name': '',
        'role': 'MANDOR',
        'divisions': set(),
        'total_verifications': 0,
        'monthly_verifications': defaultdict(int),
        'kerani_partnerships': defaultdict(lambda: {
            'kerani_total_transactions': 0,
            'mandor_verified_for_kerani': 0,
            'verification_rate': 0.0,
            'transactions_detail': []
        }),
        'division_summary': defaultdict(lambda: {
            'total_kerani_transactions': 0,
            'mandor_verifications': 0,
            'verification_coverage': 0.0,
            'kerani_list': set()
        })
    })
    
    # Data structure untuk tracking KERANI per divisi
    division_kerani_data = defaultdict(lambda: {
        'kerani_transactions': defaultdict(int),
        'total_transactions': 0,
        'mandor_name': '',
        'mandor_id': ''
    })
    
    # First pass: Collect all KERANI transactions per division
    for _, row in df.iterrows():
        try:
            creator_id = str(row.iloc[scanuserid_col]).strip() if pd.notna(row.iloc[scanuserid_col]) else ''
            recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
            transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
            transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
            division = str(row.iloc[divname_col]).strip() if pd.notna(row.iloc[divname_col]) else 'Unknown'
            
            if creator_id and recordtag:
                # Get employee name
                if 'get_name' in employee_mapping:
                    creator_name = employee_mapping['get_name'](creator_id)
                else:
                    creator_name = employee_mapping.get(creator_id, f"EMPLOYEE-{creator_id}")
                
                # Determine role
                role = get_employee_role_from_recordtag(recordtag)
                
                # Track KERANI transactions per division
                if role == 'KERANI':
                    division_kerani_data[division]['kerani_transactions'][creator_name] += 1
                    division_kerani_data[division]['total_transactions'] += 1
                
                # Track MANDOR per division
                elif role == 'MANDOR':
                    if not division_kerani_data[division]['mandor_name']:
                        division_kerani_data[division]['mandor_name'] = creator_name
                        division_kerani_data[division]['mandor_id'] = creator_id
                        
        except Exception as e:
            continue
    
    # Second pass: Analyze MANDOR verification activities
    for _, row in df.iterrows():
        try:
            creator_id = str(row.iloc[scanuserid_col]).strip() if pd.notna(row.iloc[scanuserid_col]) else ''
            recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
            transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
            transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
            division = str(row.iloc[divname_col]).strip() if pd.notna(row.iloc[divname_col]) else 'Unknown'
            
            if creator_id and recordtag:
                # Get employee name
                if 'get_name' in employee_mapping:
                    creator_name = employee_mapping['get_name'](creator_id)
                else:
                    creator_name = employee_mapping.get(creator_id, f"EMPLOYEE-{creator_id}")
                
                # Determine role
                role = get_employee_role_from_recordtag(recordtag)
                
                # Process MANDOR verification activities
                if role == 'MANDOR':
                    print(f"DEBUG: Processing MANDOR {creator_name} (ID: {creator_id}) with TRANSNO: {transno}, TRANSDATE: {transdate}")
                    
                    # Check if this transaction is in the verified transactions list
                    if (transno, transdate) in verified_transactions:
                        verif_info = verified_transactions[(transno, transdate)]
                        print(f"DEBUG: MANDOR {creator_name} (ID: {creator_id}) found verified transaction {transno} on {transdate}")
                        print(f"DEBUG: Verification info: {verif_info}")
                        
                        # Check if this MANDOR is the verifier for this transaction
                        if verif_info.get('verifier_id') == creator_id:
                            print(f"DEBUG: ✓ MANDOR {creator_name} is the verifier for transaction {transno}")
                            
                            mandor_activities[creator_name]['employee_id'] = creator_id
                            mandor_activities[creator_name]['employee_name'] = creator_name
                            mandor_activities[creator_name]['divisions'].add(division)
                            mandor_activities[creator_name]['total_verifications'] += 1
                            
                            # Monthly tracking
                            try:
                                month_key = transdate[:7]  # YYYY-MM format
                                mandor_activities[creator_name]['monthly_verifications'][month_key] += 1
                            except:
                                pass
                            
                            # Find the original KERANI for this transaction
                            # We need to find PM (KERANI) record with same TRANSNO+TRANSDATE
                            original_kerani_id = None
                            original_kerani_name = None
                            
                            # Search for PM record with same TRANSNO+TRANSDATE
                            for _, search_row in df.iterrows():
                                try:
                                    search_transno = str(search_row.iloc[transno_col]).strip() if pd.notna(search_row.iloc[transno_col]) else ''
                                    search_transdate = str(search_row.iloc[transdate_col]).strip() if pd.notna(search_row.iloc[transdate_col]) else ''
                                    search_recordtag = str(search_row.iloc[recordtag_col]).strip() if pd.notna(search_row.iloc[recordtag_col]) else ''
                                    search_creator_id = str(search_row.iloc[scanuserid_col]).strip() if pd.notna(search_row.iloc[scanuserid_col]) else ''
                                    
                                    if (search_transno == transno and search_transdate == transdate and 
                                        search_recordtag == 'PM' and search_creator_id != creator_id):
                                        original_kerani_id = search_creator_id
                                        if 'get_name' in employee_mapping:
                                            original_kerani_name = employee_mapping['get_name'](original_kerani_id)
                                        else:
                                            original_kerani_name = employee_mapping.get(original_kerani_id, f"KERANI-{original_kerani_id}")
                                        break
                                except Exception:
                                    continue
                            
                            if not original_kerani_name:
                                original_kerani_name = f"KERANI-UNKNOWN-{transno}"
                            
                            print(f"DEBUG: Found KERANI {original_kerani_name} for MANDOR {creator_name} verification")
                            
                            # Track KERANI partnership
                            partnership_key = original_kerani_name
                            mandor_activities[creator_name]['kerani_partnerships'][partnership_key]['mandor_verified_for_kerani'] += 1
                            mandor_activities[creator_name]['kerani_partnerships'][partnership_key]['transactions_detail'].append({
                                'transno': transno,
                                'transdate': transdate,
                                'division': division
                            })
                            
                            # Track division summary
                            mandor_activities[creator_name]['division_summary'][division]['mandor_verifications'] += 1
                            mandor_activities[creator_name]['division_summary'][division]['kerani_list'].add(original_kerani_name)
                        else:
                            print(f"DEBUG: ✗ MANDOR {creator_name} (ID: {creator_id}) is NOT the verifier for transaction {transno} (verifier_id: {verif_info.get('verifier_id')})")
                    else:
                        print(f"DEBUG: MANDOR {creator_name} (ID: {creator_id}) transaction {transno} NOT in verified transactions list")
        except Exception as e:
            continue
    
    # Third pass: Complete partnership analysis
    for mandor_name, mandor_data in mandor_activities.items():
        for division in mandor_data['divisions']:
            # Get KERANI data for this division
            if division in division_kerani_data:
                div_data = division_kerani_data[division]
                
                # Update division summary
                mandor_data['division_summary'][division]['total_kerani_transactions'] = div_data['total_transactions']
                if div_data['total_transactions'] > 0:
                    mandor_data['division_summary'][division]['verification_coverage'] = (
                        mandor_data['division_summary'][division]['mandor_verifications'] / 
                        div_data['total_transactions'] * 100
                    )
                
                # Update KERANI partnerships
                for kerani_name, kerani_trans_count in div_data['kerani_transactions'].items():
                    if kerani_name in mandor_data['kerani_partnerships']:
                        mandor_data['kerani_partnerships'][kerani_name]['kerani_total_transactions'] = kerani_trans_count
                        
                        verified_count = mandor_data['kerani_partnerships'][kerani_name]['mandor_verified_for_kerani']
                        if kerani_trans_count > 0:
                            mandor_data['kerani_partnerships'][kerani_name]['verification_rate'] = (
                                verified_count / kerani_trans_count * 100
                            )
    
    print(f"Analisis selesai: {len(mandor_activities)} MANDOR ditemukan")
    
    return mandor_activities, division_kerani_data

def generate_mandor_detailed_report(mandor_activities, division_kerani_data, output_dir, month, year):
    """
    Membuat laporan detail MANDOR dalam format Excel.
    """
    print("Membuat laporan detail MANDOR...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"laporan_detail_mandor_{month:02d}_{year}_{timestamp}.xlsx"
    excel_path = os.path.join(output_dir, excel_filename)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        
        # Sheet 1: Summary MANDOR per Divisi
        mandor_summary_data = []
        for mandor_name, mandor_data in mandor_activities.items():
            for division in mandor_data['divisions']:
                div_summary = mandor_data['division_summary'][division]
                mandor_summary_data.append({
                    'Nama MANDOR': mandor_name,
                    'Employee ID': mandor_data['employee_id'],
                    'Divisi': division,
                    'Total Transaksi KERANI di Divisi': div_summary['total_kerani_transactions'],
                    'Verifikasi oleh MANDOR': div_summary['mandor_verifications'],
                    'Coverage Verifikasi (%)': round(div_summary['verification_coverage'], 2),
                    'Jumlah KERANI di Divisi': len(div_summary['kerani_list']),
                    'KERANI List': ', '.join(sorted(div_summary['kerani_list']))
                })
        
        df_mandor_summary = pd.DataFrame(mandor_summary_data)
        df_mandor_summary = df_mandor_summary.sort_values(['Coverage Verifikasi (%)', 'Verifikasi oleh MANDOR'], ascending=[False, False])
        df_mandor_summary.to_excel(writer, sheet_name='Summary MANDOR', index=False)
        
        # Sheet 2: Pasangan MANDOR-KERANI Detail
        partnership_data = []
        for mandor_name, mandor_data in mandor_activities.items():
            for kerani_name, partnership in mandor_data['kerani_partnerships'].items():
                if partnership['kerani_total_transactions'] > 0:  # Only include active partnerships
                    # Find division for this partnership
                    partnership_division = 'Unknown'
                    for trans_detail in partnership['transactions_detail']:
                        partnership_division = trans_detail['division']
                        break
                    
                    partnership_data.append({
                        'MANDOR': mandor_name,
                        'KERANI': kerani_name,
                        'Divisi': partnership_division,
                        'Total Transaksi KERANI': partnership['kerani_total_transactions'],
                        'Verifikasi oleh MANDOR': partnership['mandor_verified_for_kerani'],
                        'Tingkat Verifikasi (%)': round(partnership['verification_rate'], 2),
                        'Transaksi Belum Verified': partnership['kerani_total_transactions'] - partnership['mandor_verified_for_kerani']
                    })
        
        df_partnership = pd.DataFrame(partnership_data)
        df_partnership = df_partnership.sort_values(['Divisi', 'MANDOR', 'Tingkat Verifikasi (%)'], ascending=[True, True, False])
        df_partnership.to_excel(writer, sheet_name='Pasangan MANDOR-KERANI', index=False)
        
        # Sheet 3: Breakdown per Divisi Detail
        division_breakdown_data = []
        for division, div_data in division_kerani_data.items():
            mandor_name = div_data['mandor_name']
            mandor_verifications = 0
            
            # Get MANDOR verification count for this division
            if mandor_name in mandor_activities:
                mandor_verifications = mandor_activities[mandor_name]['division_summary'][division]['mandor_verifications']
            
            # Add division summary row
            division_breakdown_data.append({
                'Divisi': division,
                'MANDOR': mandor_name,
                'KERANI': 'TOTAL DIVISI',
                'Transaksi Dibuat': div_data['total_transactions'],
                'Verifikasi MANDOR': mandor_verifications,
                'Persentase (%)': round((mandor_verifications / div_data['total_transactions'] * 100) if div_data['total_transactions'] > 0 else 0, 2),
                'Status': 'SUMMARY'
            })
            
            # Add individual KERANI breakdown
            for kerani_name, kerani_count in div_data['kerani_transactions'].items():
                kerani_verified = 0
                if mandor_name in mandor_activities and kerani_name in mandor_activities[mandor_name]['kerani_partnerships']:
                    kerani_verified = mandor_activities[mandor_name]['kerani_partnerships'][kerani_name]['mandor_verified_for_kerani']
                
                division_breakdown_data.append({
                    'Divisi': division,
                    'MANDOR': mandor_name,
                    'KERANI': kerani_name,
                    'Transaksi Dibuat': kerani_count,
                    'Verifikasi MANDOR': kerani_verified,
                    'Persentase (%)': round((kerani_verified / kerani_count * 100) if kerani_count > 0 else 0, 2),
                    'Status': 'DETAIL'
                })
        
        df_division_breakdown = pd.DataFrame(division_breakdown_data)
        df_division_breakdown = df_division_breakdown.sort_values(['Divisi', 'Status', 'Persentase (%)'], ascending=[True, True, False])
        df_division_breakdown.to_excel(writer, sheet_name='Breakdown per Divisi', index=False)
        
        # Sheet 4: Aktivitas MANDOR Bulanan
        monthly_activity_data = []
        for mandor_name, mandor_data in mandor_activities.items():
            for month_key, verification_count in mandor_data['monthly_verifications'].items():
                try:
                    year_month = month_key.split('-')
                    month_name = calendar.month_name[int(year_month[1])]
                    monthly_activity_data.append({
                        'MANDOR': mandor_name,
                        'Tahun': year_month[0],
                        'Bulan': month_name,
                        'Bulan-Tahun': month_key,
                        'Jumlah Verifikasi': verification_count,
                        'Divisi Kerja': ', '.join(sorted(mandor_data['divisions'])),
                        'Total Verifikasi Keseluruhan': mandor_data['total_verifications']
                    })
                except:
                    continue
        
        df_monthly = pd.DataFrame(monthly_activity_data)
        if not df_monthly.empty:
            df_monthly = df_monthly.sort_values(['MANDOR', 'Bulan-Tahun'])
        df_monthly.to_excel(writer, sheet_name='Aktivitas Bulanan', index=False)
        
        # Sheet 5: Detail Transaksi Verifikasi
        verification_detail_data = []
        for mandor_name, mandor_data in mandor_activities.items():
            for kerani_name, partnership in mandor_data['kerani_partnerships'].items():
                for trans_detail in partnership['transactions_detail']:
                    verification_detail_data.append({
                        'MANDOR': mandor_name,
                        'KERANI': kerani_name,
                        'Divisi': trans_detail['division'],
                        'TRANSNO': trans_detail['transno'],
                        'TRANSDATE': trans_detail['transdate'],
                        'Bulan': trans_detail['transdate'][:7] if len(trans_detail['transdate']) >= 7 else ''
                    })
        
        df_verification_detail = pd.DataFrame(verification_detail_data)
        if not df_verification_detail.empty:
            df_verification_detail = df_verification_detail.sort_values(['Divisi', 'MANDOR', 'TRANSDATE', 'TRANSNO'])
        df_verification_detail.to_excel(writer, sheet_name='Detail Verifikasi', index=False)
    
    print(f"Laporan Excel disimpan: {excel_path}")
    
    # Generate console summary
    print("\n" + "="*80)
    print("RINGKASAN ANALISIS DETAIL MANDOR")
    print("="*80)
    print(f"Periode Analisis: {month:02d}/{year}")
    print(f"Total MANDOR Aktif: {len(mandor_activities)}")
    
    total_verifications = sum(mandor_data['total_verifications'] for mandor_data in mandor_activities.values())
    total_kerani_transactions = sum(div_data['total_transactions'] for div_data in division_kerani_data.values())
    
    print(f"Total Verifikasi MANDOR: {total_verifications}")
    print(f"Total Transaksi KERANI: {total_kerani_transactions}")
    print(f"Coverage Verifikasi Keseluruhan: {(total_verifications/total_kerani_transactions*100):.2f}%" if total_kerani_transactions > 0 else "0%")
    print(f"Total Divisi Terlibat: {len(division_kerani_data)}")
    
    print("\nDETAIL PER MANDOR:")
    for mandor_name, mandor_data in sorted(mandor_activities.items(), key=lambda x: x[1]['total_verifications'], reverse=True):
        print(f"MANDOR {mandor_name}:")
        print(f"   - Total Verifikasi: {mandor_data['total_verifications']}")
        print(f"   - Divisi Kerja: {', '.join(sorted(mandor_data['divisions']))}")
        print(f"   - Jumlah KERANI Partner: {len(mandor_data['kerani_partnerships'])}")
        
        for division in sorted(mandor_data['divisions']):
            div_summary = mandor_data['division_summary'][division]
            print(f"   - {division}: {div_summary['mandor_verifications']}/{div_summary['total_kerani_transactions']} ({div_summary['verification_coverage']:.1f}%)")
    
    print("\nDETAIL PER DIVISI:")
    for division, div_data in sorted(division_kerani_data.items()):
        mandor_name = div_data['mandor_name']
        mandor_verifications = 0
        if mandor_name in mandor_activities:
            mandor_verifications = mandor_activities[mandor_name]['division_summary'][division]['mandor_verifications']
        
        coverage = (mandor_verifications / div_data['total_transactions'] * 100) if div_data['total_transactions'] > 0 else 0
        
        print(f"DIVISI {division}:")
        print(f"   - MANDOR: {mandor_name}")
        print(f"   - Total Transaksi KERANI: {div_data['total_transactions']}")
        print(f"   - Verifikasi MANDOR: {mandor_verifications} ({coverage:.1f}%)")
        print(f"   - KERANI di Divisi: {len(div_data['kerani_transactions'])}")
        
        for kerani_name, kerani_count in sorted(div_data['kerani_transactions'].items(), key=lambda x: x[1], reverse=True):
            kerani_verified = 0
            if mandor_name in mandor_activities and kerani_name in mandor_activities[mandor_name]['kerani_partnerships']:
                kerani_verified = mandor_activities[mandor_name]['kerani_partnerships'][kerani_name]['mandor_verified_for_kerani']
            
            kerani_rate = (kerani_verified / kerani_count * 100) if kerani_count > 0 else 0
            print(f"     - {kerani_name}: {kerani_count} transaksi -> {kerani_verified} verified ({kerani_rate:.1f}%)")
    
    print("="*80)
    
    return excel_path

def main():
    """
    Main function untuk analisis detail MANDOR.
    """
    # Konfigurasi
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    OUTPUT_DIR = "reports"
    
    # Periode analisis (contoh: Mei 2025)
    MONTH = 5
    YEAR = 2025
    
    # Buat direktori output jika belum ada
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        print("MEMULAI ANALISIS DETAIL MANDOR")
        print("="*60)
        
        # Setup database connection
        print("Menghubungkan ke database...")
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("Koneksi database gagal!")
            return
        
        print("Koneksi database berhasil")
        
        # Load mappings
        print("Memuat mapping data...")
        employee_mapping = get_employee_mapping(connector)
        transstatus_mapping = get_transstatus_mapping(connector)
        division_mapping = get_division_mapping(connector)
        
        # Calculate date range
        start_date = f"{YEAR}-{MONTH:02d}-01"
        if MONTH == 12:
            end_date = f"{YEAR + 1}-01-01"
        else:
            end_date = f"{YEAR}-{MONTH + 1:02d}-01"
        
        # Get transaction data
        df = get_detailed_transaction_data_mandor(connector, start_date, end_date, MONTH)
        
        if df.empty:
            print("Tidak ada data transaksi untuk periode yang dipilih")
            return
        
        # Analyze MANDOR activities
        mandor_activities, division_kerani_data = analyze_mandor_activities_detailed(
            df, employee_mapping, transstatus_mapping, division_mapping)
        
        if not mandor_activities:
            print("Tidak ada aktivitas MANDOR ditemukan")
            return
        
        # Generate detailed report
        report_path = generate_mandor_detailed_report(
            mandor_activities, division_kerani_data, OUTPUT_DIR, MONTH, YEAR)
        
        print(f"\nANALISIS SELESAI!")
        print(f"Laporan disimpan di: {report_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 