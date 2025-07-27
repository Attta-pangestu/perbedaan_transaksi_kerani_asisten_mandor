#!/usr/bin/env python3
"""
Analisis Detail Transaksi KERANI
Laporan komprehensif untuk transaksi yang dilakukan oleh KERANI dengan:
1. Detail transaksi per TRANSNO dan TRANSDATE
2. Pengelompokan berdasarkan divisi
3. Pasangan kerja KERANI dengan MANDOR/ASISTEN
4. Analisis verifikasi transaksi
"""

import pandas as pd
from datetime import datetime, timedelta
import os
from collections import defaultdict
import json

# Import modul yang sudah ada
from firebird_connector import FirebirdConnector
from analisis_per_karyawan import (
    get_employee_mapping, get_transstatus_mapping, get_division_mapping,
    get_employee_role_from_recordtag, get_employee_role,
    is_transaction_verified, check_transaction_verification_by_duplicates
)

def get_detailed_transaction_data(connector, start_date, end_date, month):
    """
    Mengambil data transaksi detail dengan informasi lengkap.
    """
    table_name = f"FFBSCANNERDATA{month:02d}"
    
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
    
    print(f"Mengambil data dari {table_name}...")
    print(f"Periode: {start_date} sampai {end_date}")
    
    result = connector.execute_query(query)
    df = connector.to_pandas(result)
    
    print(f"✓ Data berhasil diambil: {len(df)} record")
    return df

def analyze_kerani_transactions_detailed(df, employee_mapping, transstatus_mapping, division_mapping):
    """
    Analisis detail transaksi KERANI dengan pengelompokan divisi dan pasangan kerja.
    """
    if df.empty:
        print("❌ Tidak ada data untuk dianalisis")
        return {}, {}, {}
    
    print("🔍 Memulai analisis detail transaksi KERANI...")
    
    # Column mapping
    scanuserid_col = 1   # SCANUSERID
    recordtag_col = 18   # RECORDTAG
    transstatus_col = 19 # TRANSSTATUS
    transno_col = 14     # TRANSNO
    transdate_col = 15   # TRANSDATE
    divname_col = 28     # DIVNAME (adjusted after removing FIELD_NAME column)
    
    # Get verified transactions through duplicate detection (PM + P1/P5 pairs) AND status 704
    verified_transactions = check_transaction_verification_by_duplicates(
        df, transno_col, transdate_col, recordtag_col, transstatus_col)
    
    print(f"✓ Ditemukan {len(verified_transactions)} transaksi terverifikasi melalui deteksi duplikat")
    
    # Data structures untuk analisis
    kerani_transactions = defaultdict(list)  # Transaksi per KERANI
    kerani_by_division = defaultdict(lambda: defaultdict(lambda: {
        'total_transactions': 0,
        'verified_transactions': 0,
        'transno_list': [],
        'verification_rate': 0.0
    }))  # KERANI per divisi
    
    division_groups = defaultdict(lambda: {
        'kerani': set(),
        'mandor_asisten': set(),
        'transactions': [],
        'kerani_transactions': 0,
        'verified_transactions': 0
    })
    
    # Verifier statistics (MANDOR/ASISTEN)
    verifier_stats = defaultdict(lambda: {
        'total_verified': 0,
        'role': 'UNKNOWN',
        'divisions': set(),
        'verified_transactions': []
    })
    
    # Employee role mapping
    employee_roles = {}
    
    # Proses semua transaksi
    for _, row in df.iterrows():
        try:
            creator_id = str(row.iloc[scanuserid_col]).strip() if pd.notna(row.iloc[scanuserid_col]) else ''
            recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
            status = str(row.iloc[transstatus_col]).strip() if pd.notna(row.iloc[transstatus_col]) else '0'
            transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
            transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
            division = str(row.iloc[divname_col]).strip() if pd.notna(row.iloc[divname_col]) else 'UNKNOWN'
            
            if creator_id:
                # Get employee name
                if 'get_name' in employee_mapping:
                    creator_name = employee_mapping['get_name'](creator_id)
                else:
                    creator_name = employee_mapping.get(creator_id, f"KARYAWAN-{creator_id}")
                
                # Determine role using RECORDTAG as primary method
                if recordtag and recordtag != '':
                    role = get_employee_role_from_recordtag(recordtag)
                else:
                    role = get_employee_role(creator_name)
                
                employee_roles[creator_name] = role
                
                # Check verification - berdasarkan duplikat PM + P1/P5 DAN status 704
                is_verified = (transno, transdate) in verified_transactions
                
                # Transaction detail
                transaction_detail = {
                    'transno': transno,
                    'transdate': transdate,
                    'creator_id': creator_id,
                    'creator_name': creator_name,
                    'role': role,
                    'division': division,
                    'status': status,
                    'is_verified': is_verified,
                    'recordtag': recordtag,
                    'row_data': row.to_dict()
                }
                
                # Fokus pada KERANI
                if role == 'KERANI':
                    kerani_transactions[creator_name].append(transaction_detail)
                    division_groups[division]['kerani'].add(creator_name)
                    division_groups[division]['transactions'].append(transaction_detail)
                    division_groups[division]['kerani_transactions'] += 1
                    
                    # Track per divisi
                    kerani_by_division[creator_name][division]['total_transactions'] += 1
                    kerani_by_division[creator_name][division]['transno_list'].append(transno)
                    
                    if is_verified:
                        division_groups[division]['verified_transactions'] += 1
                        kerani_by_division[creator_name][division]['verified_transactions'] += 1
                        
                        # Track verifier information
                        if (transno, transdate) in verified_transactions:
                            verifier_info = verified_transactions[(transno, transdate)]
                            verifier_id = verifier_info['verifier_id']
                            
                            # Get verifier name
                            if 'get_name' in employee_mapping:
                                verifier_name = employee_mapping['get_name'](verifier_id)
                            else:
                                verifier_name = employee_mapping.get(verifier_id, f"VERIFIER-{verifier_id}")
                            
                            verifier_stats[verifier_name]['total_verified'] += 1
                            verifier_stats[verifier_name]['role'] = verifier_info['verifier_role']
                            verifier_stats[verifier_name]['divisions'].add(division)
                            verifier_stats[verifier_name]['verified_transactions'].append({
                                'transno': transno,
                                'transdate': transdate,
                                'kerani': creator_name,
                                'division': division
                            })
                
                # Track MANDOR dan ASISTEN untuk pairing
                elif role in ['MANDOR', 'ASISTEN']:
                    division_groups[division]['mandor_asisten'].add(creator_name)
                    division_groups[division]['transactions'].append(transaction_detail)
                
        except Exception as e:
            print(f"❌ Error memproses baris: {e}")
            continue
    
    # Calculate verification rates per division
    for kerani_name, divisions in kerani_by_division.items():
        for division, stats in divisions.items():
            if stats['total_transactions'] > 0:
                stats['verification_rate'] = (stats['verified_transactions'] / stats['total_transactions']) * 100
    
    print(f"✓ Analisis selesai: {len(kerani_transactions)} KERANI ditemukan")
    print(f"✓ Divisi yang terlibat: {len(division_groups)}")
    print(f"✓ Verifier ditemukan: {len(verifier_stats)} MANDOR/ASISTEN")
    
    return kerani_transactions, division_groups, employee_roles, kerani_by_division, verifier_stats

def generate_kerani_detailed_report(kerani_transactions, division_groups, employee_roles, kerani_by_division, verifier_stats, output_dir, month, year):
    """
    Membuat laporan detail KERANI dalam format Excel dan PDF.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename_prefix = f"laporan_detail_kerani_{month:02d}_{year}_{timestamp}"
    
    print("📊 Membuat laporan detail KERANI...")
    
    # Excel Report
    excel_filename = f"{filename_prefix}.xlsx"
    excel_path = os.path.join(output_dir, excel_filename)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        
        # Sheet 1: Detail Transaksi KERANI
        kerani_detail_data = []
        for kerani_name, transactions in kerani_transactions.items():
            for trans in transactions:
                kerani_detail_data.append({
                    'Nama KERANI': kerani_name,
                    'Divisi': trans['division'],
                    'TRANSNO': trans['transno'],
                    'TRANSDATE': trans['transdate'],
                    'Status Code': trans['status'],
                    'Verified': 'YA' if trans['is_verified'] else 'TIDAK',
                    'RECORDTAG': trans['recordtag'],
                    'Creator ID': trans['creator_id']
                })
        
        df_kerani_detail = pd.DataFrame(kerani_detail_data)
        df_kerani_detail = df_kerani_detail.sort_values(['Divisi', 'Nama KERANI', 'TRANSDATE', 'TRANSNO'])
        df_kerani_detail.to_excel(writer, sheet_name='Detail Transaksi KERANI', index=False)
        
        # Sheet 2: Summary per KERANI
        kerani_summary_data = []
        for kerani_name, transactions in kerani_transactions.items():
            total_trans = len(transactions)
            verified_trans = sum(1 for t in transactions if t['is_verified'])
            verification_rate = (verified_trans / total_trans * 100) if total_trans > 0 else 0
            
            # Get unique TRANSNO
            unique_transno = set(t['transno'] for t in transactions)
            
            # Get division (ambil yang paling sering muncul)
            divisions = [t['division'] for t in transactions]
            main_division = max(set(divisions), key=divisions.count) if divisions else 'UNKNOWN'
            
            kerani_summary_data.append({
                'Nama KERANI': kerani_name,
                'Divisi Utama': main_division,
                'Total Transaksi': total_trans,
                'Transaksi Verified': verified_trans,
                'Tingkat Verifikasi (%)': round(verification_rate, 2),
                'Unique TRANSNO': len(unique_transno),
                'TRANSNO List': ', '.join(sorted(unique_transno))
            })
        
        df_kerani_summary = pd.DataFrame(kerani_summary_data)
        df_kerani_summary = df_kerani_summary.sort_values('Total Transaksi', ascending=False)
        df_kerani_summary.to_excel(writer, sheet_name='Summary KERANI', index=False)
        
        # Sheet 2B: Summary KERANI per Divisi
        kerani_per_division_data = []
        for kerani_name, divisions in kerani_by_division.items():
            for division, stats in divisions.items():
                kerani_per_division_data.append({
                    'Nama KERANI': kerani_name,
                    'Divisi': division,
                    'Total Transaksi': stats['total_transactions'],
                    'Transaksi Verified': stats['verified_transactions'],
                    'Tingkat Verifikasi (%)': round(stats['verification_rate'], 2),
                    'Unique TRANSNO': len(set(stats['transno_list'])),
                    'TRANSNO List': ', '.join(sorted(set(stats['transno_list'])))
                })
        
        df_kerani_per_division = pd.DataFrame(kerani_per_division_data)
        df_kerani_per_division = df_kerani_per_division.sort_values(['Nama KERANI', 'Divisi'])
        df_kerani_per_division.to_excel(writer, sheet_name='KERANI per Divisi', index=False)
        
        # Sheet 2C: Statistik Verifier (MANDOR/ASISTEN)
        verifier_data = []
        for verifier_name, stats in verifier_stats.items():
            verifier_data.append({
                'Nama Verifier': verifier_name,
                'Role': stats['role'],
                'Total Verified': stats['total_verified'],
                'Divisi Kerja': ', '.join(sorted(stats['divisions'])),
                'Jumlah Divisi': len(stats['divisions'])
            })
        
        df_verifier = pd.DataFrame(verifier_data)
        df_verifier = df_verifier.sort_values('Total Verified', ascending=False)
        df_verifier.to_excel(writer, sheet_name='Statistik Verifier', index=False)
        
        # Sheet 3: Pengelompokan Divisi dan Pasangan Kerja
        division_pairing_data = []
        for division, data in division_groups.items():
            kerani_list = list(data['kerani'])
            mandor_asisten_list = list(data['mandor_asisten'])
            
            division_pairing_data.append({
                'Divisi': division,
                'Jumlah KERANI': len(kerani_list),
                'KERANI': ', '.join(kerani_list) if kerani_list else 'TIDAK ADA',
                'Jumlah MANDOR/ASISTEN': len(mandor_asisten_list),
                'MANDOR/ASISTEN': ', '.join(mandor_asisten_list) if mandor_asisten_list else 'TIDAK ADA',
                'Total Transaksi KERANI': data['kerani_transactions'],
                'Transaksi Verified': data['verified_transactions'],
                'Tingkat Verifikasi (%)': round((data['verified_transactions'] / data['kerani_transactions'] * 100) if data['kerani_transactions'] > 0 else 0, 2)
            })
        
        df_division_pairing = pd.DataFrame(division_pairing_data)
        df_division_pairing = df_division_pairing.sort_values('Total Transaksi KERANI', ascending=False)
        df_division_pairing.to_excel(writer, sheet_name='Pengelompokan Divisi', index=False)
        
        # Sheet 4: Detail TRANSNO per Bulan
        transno_monthly_data = []
        for kerani_name, transactions in kerani_transactions.items():
            # Group by TRANSNO
            transno_groups = defaultdict(list)
            for trans in transactions:
                transno_groups[trans['transno']].append(trans)
            
            for transno, trans_list in transno_groups.items():
                dates = [t['transdate'] for t in trans_list]
                verified_count = sum(1 for t in trans_list if t['is_verified'])
                
                transno_monthly_data.append({
                    'KERANI': kerani_name,
                    'Divisi': trans_list[0]['division'],
                    'TRANSNO': transno,
                    'Jumlah Entry': len(trans_list),
                    'Tanggal Pertama': min(dates) if dates else '',
                    'Tanggal Terakhir': max(dates) if dates else '',
                    'Entry Verified': verified_count,
                    'Status Verifikasi': 'VERIFIED' if verified_count > 0 else 'BELUM VERIFIED'
                })
        
        df_transno_monthly = pd.DataFrame(transno_monthly_data)
        df_transno_monthly = df_transno_monthly.sort_values(['KERANI', 'TRANSNO'])
        df_transno_monthly.to_excel(writer, sheet_name='TRANSNO per Bulan', index=False)
    
    print(f"✓ Laporan Excel disimpan: {excel_path}")
    
    # Generate summary statistics
    total_kerani = len(kerani_transactions)
    total_transactions = sum(len(transactions) for transactions in kerani_transactions.values())
    total_verified = sum(sum(1 for t in transactions if t['is_verified']) for transactions in kerani_transactions.values())
    overall_verification_rate = (total_verified / total_transactions * 100) if total_transactions > 0 else 0
    
    # Print summary to console
    print("\n" + "="*80)
    print("RINGKASAN ANALISIS DETAIL KERANI")
    print("="*80)
    print(f"Periode Analisis: {month:02d}/{year}")
    print(f"Total KERANI: {total_kerani}")
    print(f"Total Transaksi KERANI: {total_transactions}")
    print(f"Total Transaksi Verified: {total_verified}")
    print(f"Tingkat Verifikasi Keseluruhan: {overall_verification_rate:.2f}%")
    print(f"Total Divisi Terlibat: {len(division_groups)}")
    
    print("\nDETAIL PER DIVISI:")
    for division, data in sorted(division_groups.items()):
        if data['kerani_transactions'] > 0:  # Hanya tampilkan divisi yang ada transaksi KERANI
            verification_rate = (data['verified_transactions'] / data['kerani_transactions'] * 100) if data['kerani_transactions'] > 0 else 0
            print(f"📁 {division}:")
            print(f"   - KERANI: {len(data['kerani'])} orang ({', '.join(list(data['kerani']))})")
            print(f"   - MANDOR/ASISTEN: {len(data['mandor_asisten'])} orang ({', '.join(list(data['mandor_asisten']))})")
            print(f"   - Transaksi KERANI: {data['kerani_transactions']}")
            print(f"   - Verified: {data['verified_transactions']} ({verification_rate:.1f}%)")
    
    print("\nDETAIL PER KERANI:")
    for kerani_name, transactions in sorted(kerani_transactions.items()):
        total_trans = len(transactions)
        verified_trans = sum(1 for t in transactions if t['is_verified'])
        verification_rate = (verified_trans / total_trans * 100) if total_trans > 0 else 0
        unique_transno = set(t['transno'] for t in transactions)
        
        print(f"👤 {kerani_name}:")
        print(f"   - Total Transaksi: {total_trans}")
        print(f"   - Verified: {verified_trans} ({verification_rate:.1f}%)")
        print(f"   - Unique TRANSNO: {len(unique_transno)}")
        print(f"   - TRANSNO List: {', '.join(sorted(list(unique_transno)))}")
        
        # Detail per divisi untuk KERANI ini
        if kerani_name in kerani_by_division:
            print(f"   - BREAKDOWN PER DIVISI:")
            for division, stats in kerani_by_division[kerani_name].items():
                print(f"     • {division}: {stats['verified_transactions']}/{stats['total_transactions']} ({stats['verification_rate']:.1f}%)")
    
    print("\nSTATISTIK VERIFIER (MANDOR/ASISTEN):")
    for verifier_name, stats in sorted(verifier_stats.items(), key=lambda x: x[1]['total_verified'], reverse=True):
        print(f"🔍 {verifier_name} ({stats['role']}):")
        print(f"   - Total Verified: {stats['total_verified']} transaksi")
        print(f"   - Divisi Kerja: {', '.join(sorted(stats['divisions']))}")
        print(f"   - Jumlah Divisi: {len(stats['divisions'])}")
    
    print("="*80)
    
    return excel_path

def main():
    """
    Main function untuk analisis detail KERANI.
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
        print("🚀 MEMULAI ANALISIS DETAIL TRANSAKSI KERANI")
        print("="*60)
        
        # Setup database connection
        print("📡 Menghubungkan ke database...")
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("❌ Koneksi database gagal!")
            return
        
        print("✓ Koneksi database berhasil")
        
        # Load mappings
        print("📋 Memuat mapping data...")
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
        df = get_detailed_transaction_data(connector, start_date, end_date, MONTH)
        
        if df.empty:
            print("❌ Tidak ada data transaksi untuk periode yang dipilih")
            return
        
        # Analyze KERANI transactions
        kerani_transactions, division_groups, employee_roles, kerani_by_division, verifier_stats = analyze_kerani_transactions_detailed(
            df, employee_mapping, transstatus_mapping, division_mapping)
        
        if not kerani_transactions:
            print("❌ Tidak ada transaksi KERANI ditemukan")
            return
        
        # Generate detailed report
        report_path = generate_kerani_detailed_report(
            kerani_transactions, division_groups, employee_roles, kerani_by_division, verifier_stats, OUTPUT_DIR, MONTH, YEAR)
        
        print(f"\n🎉 ANALISIS SELESAI!")
        print(f"📄 Laporan disimpan di: {report_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 