"""
Program untuk menganalisis kinerja transaksi per individu karyawan.
Analisis meliputi:
- Total transaksi per karyawan berdasarkan RECORDTAG
- Tingkat verifikasi per karyawan
- Breakdown status transaksi
- Analisis kinerja berdasarkan role (Kerani, Mandor, Asisten)
- Integrasi dengan data divisi
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, date
import calendar
import argparse
import numpy as np
from collections import defaultdict

# Tambahkan parent directory ke path untuk import modul
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from firebird_connector import FirebirdConnector
from pdf_report_advanced import generate_advanced_pdf_report

# Set style untuk matplotlib dengan font yang mendukung Unicode
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

def get_employee_mapping(connector):
    """
    Mendapatkan mapping antara ID dan NAME dari tabel EMP.
    """
    print("Mendapatkan data mapping ID ke NAME dari tabel EMP...")
    query = """
    SELECT ID, NAME
    FROM EMP
    """

    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        employee_mapping = {}
        
        if not df.empty:
            print(f"Berhasil mendapatkan {len(df)} data karyawan dari database.")
            
            # Cari kolom ID dan NAME
            id_col = None
            name_col = None
            
            for col in df.columns:
                if 'ID' in col.upper() and id_col is None:
                    id_col = col
                if 'NAME' in col.upper() and name_col is None:
                    name_col = col
            
            if id_col and name_col:
                for _, row in df.iterrows():
                    emp_id = str(row[id_col]).strip()
                    emp_name = str(row[name_col]).strip()
                    if emp_id and emp_name:
                        employee_mapping[emp_id] = emp_name
                        
                print(f"Berhasil membuat mapping untuk {len(employee_mapping)} karyawan.")
        else:
            print("Tidak dapat mendapatkan data EMP dari database.")
    except Exception as e:
        print(f"Error saat mengambil data EMP: {e}")
    
    # Tambahkan mapping default untuk ID yang sering muncul
    default_mapping = {
        '4771': 'KERANI_DEFAULT',
        '5044': 'ASISTEN_DEFAULT',
        '20001': 'ADMIN_DEFAULT',
        '40389': 'KERANI-40389',
        '40584': 'ASISTEN-40584',
        '40587': 'ASISTEN-40587',
        '40388': 'KERANI-40388',
        '40581': 'ASISTEN-40581',
        '40390': 'KERANI-40390',
        '40583': 'ASISTEN-40583',
        '40391': 'KERANI-40391',
        '40565': 'ASISTEN-40565',
        '40392': 'KERANI-40392'
    }
    
    # Update mapping dengan default jika belum ada
    for emp_id, emp_name in default_mapping.items():
        if emp_id not in employee_mapping:
            employee_mapping[emp_id] = emp_name
    
    def get_employee_name(emp_id):
        emp_id_str = str(emp_id).strip()
        if emp_id_str in employee_mapping:
            return employee_mapping[emp_id_str]
        return f"KARYAWAN-{emp_id_str}"
    
    employee_mapping['get_name'] = get_employee_name
    print(f"Total mapping karyawan: {len(employee_mapping)-1}")
    return employee_mapping

def get_transstatus_mapping(connector):
    """
    Mendapatkan mapping kode TRANSSTATUS ke deskripsi dari tabel LOOKUP.
    """
    print("Mendapatkan data mapping TRANSSTATUS dari tabel LOOKUP...")
    query = """
    SELECT ID, SHORTCODE, NAME
    FROM LOOKUP
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        transstatus_mapping = {}
        
        if not df.empty:
            for col in df.columns:
                if 'ID' == col.upper():
                    id_col = col
                if 'NAME' == col.upper():
                    name_col = col
            
            if 'id_col' in locals() and 'name_col' in locals():
                for _, row in df.iterrows():
                    status_id = str(row[id_col]).strip()
                    status_name = str(row[name_col]).strip()
                    if status_id and status_name:
                        transstatus_mapping[status_id] = status_name
                        
                print(f"Berhasil membuat mapping untuk {len(transstatus_mapping)} status.")
    except Exception as e:
        print(f"Error saat mengambil data LOOKUP: {e}")
    
    # Tambahkan mapping default
    default_mapping = {
        '1': 'Verified',
        '2': 'Pending',
        '3': 'Rejected',
        '4': 'Cancelled',
        '5': 'Deleted',
        '0': 'Draft'
    }
    
    for status_id, status_name in default_mapping.items():
        if status_id not in transstatus_mapping:
            transstatus_mapping[status_id] = status_name
    
    def get_status_name(status_id):
        status_id_str = str(status_id).strip()
        return transstatus_mapping.get(status_id_str, f"STATUS-{status_id_str}")
    
    transstatus_mapping['get_status_name'] = get_status_name
    return transstatus_mapping

def get_division_mapping(connector):
    """
    Mendapatkan mapping divisi dari tabel CRDIVISION.
    """
    print("Mendapatkan data mapping divisi...")
    query = """
    SELECT ID, DIVCODE, DIVNAME
    FROM CRDIVISION
    ORDER BY DIVNAME
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        division_mapping = {}
        
        if not df.empty:
            for _, row in df.iterrows():
                div_id = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                div_code = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                div_name = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
                
                if div_id and div_name:
                    division_mapping[div_id] = div_name
                    
                print(f"Berhasil membuat mapping untuk {len(division_mapping)} divisi.")
        else:
            print("Tidak dapat mendapatkan data divisi.")
    except Exception as e:
        print(f"Error saat mengambil data divisi: {e}")
    
    def get_division_name(div_id):
        div_id_str = str(div_id).strip()
        return division_mapping.get(div_id_str, f"DIVISI-{div_id_str}")
    
    division_mapping['get_name'] = get_division_name
    return division_mapping

def get_employee_role_from_recordtag(recordtag):
    """
    Menentukan role karyawan berdasarkan RECORDTAG.
    Metode ini lebih akurat karena menggunakan field yang spesifik untuk role.
    
    Args:
        recordtag: Field RECORDTAG dari transaksi
    
    Returns:
        str: Role karyawan
    """
    if not recordtag:
        return 'LAINNYA'
    
    recordtag_str = str(recordtag).strip().upper()
    
    # Mapping berdasarkan RECORDTAG seperti di analisis_perbedaan_panen.py
    # PM = Kerani (Plantation Manager), P1 = Asisten, P5 = Mandor
    role_mapping = {
        'PM': 'KERANI',    # Plantation Manager/Kerani
        'P1': 'ASISTEN',   # Asisten
        'P5': 'MANDOR',    # Mandor
    }
    
    return role_mapping.get(recordtag_str, 'LAINNYA')

def get_employee_role(employee_name):
    """
    Menentukan role karyawan berdasarkan nama (fallback method).
    Digunakan jika RECORDTAG tidak tersedia.
    
    Args:
        employee_name: Nama karyawan
    
    Returns:
        str: Role karyawan
    """
    if not employee_name:
        return 'LAINNYA'
    
    name_upper = employee_name.upper()
    if 'KERANI' in name_upper:
        return 'KERANI'
    elif 'ASISTEN' in name_upper:
        return 'ASISTEN'
    elif 'MANDOR' in name_upper:
        return 'MANDOR'
    elif 'ADMIN' in name_upper:
        return 'ADMIN'
    else:
        return 'LAINNYA'

def get_all_transactions_data_with_divisions(connector, start_date, end_date, limit=None):
    """
    Mendapatkan semua data transaksi dengan informasi divisi dalam periode tertentu.
    """
    # Tentukan tabel berdasarkan bulan
    month_num = int(start_date.split('-')[1])
    ffb_table = f"FFBSCANNERDATA{month_num:02d}"
    print(f"Menggunakan tabel {ffb_table} untuk bulan {month_num}")
    
    # Query dengan join untuk mendapatkan data divisi
    # Menggunakan FIRST untuk Firebird 1.5 compatibility
    limit_clause = f"FIRST {limit}" if limit else ""
    
    query = f"""
    SELECT {limit_clause}
        a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
        a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
        a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
        a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
        a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
        b.FIELDNO, b.DIVID, c.DIVNAME
    FROM {ffb_table} a
    LEFT JOIN OCFIELD b ON a.FIELDID = b.ID AND a.OCID = b.OCID
    LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
    WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE < '{end_date}'
    ORDER BY a.TRANSNO, a.TRANSDATE, a.TRANSTIME
    """
    
    print(f"Mengambil data transaksi dengan divisi dari {start_date} hingga {end_date}...")
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        print(f"Berhasil mengambil {len(df)} record transaksi dengan data divisi.")
        return df
    except Exception as e:
        print(f"Error saat mengambil data transaksi: {e}")
        return pd.DataFrame()

def analyze_employee_performance_comprehensive(df, employee_mapping, transstatus_mapping, division_mapping):
    """
    Menganalisis kinerja per karyawan secara komprehensif dengan RECORDTAG dan divisi.
    Implementasi verifikasi berdasarkan multiple records dengan TRANSNO dan TRANSDATE yang sama.
    """
    if df.empty:
        print("Tidak ada data untuk dianalisis.")
        return {}, {}
    
    print("Memulai analisis kinerja per karyawan komprehensif...")
    
    # Mapping kolom berdasarkan posisi yang benar dari output database
    scanuserid_col = 1   # SCANUSERID
    recordtag_col = 18   # RECORDTAG (posisi 18, bukan 19)
    transstatus_col = 19 # TRANSSTATUS (posisi 19, bukan 20)
    transno_col = 14     # TRANSNO
    transdate_col = 15   # TRANSDATE (posisi 15)
    divname_col = 29     # DIVNAME (posisi 29, bukan -1)
    
    print(f"Menggunakan kolom:")
    print(f"  - SCANUSERID: posisi {scanuserid_col}")
    print(f"  - RECORDTAG: posisi {recordtag_col}")
    print(f"  - TRANSSTATUS: posisi {transstatus_col}")
    print(f"  - TRANSNO: posisi {transno_col}")
    print(f"  - TRANSDATE: posisi {transdate_col}")
    print(f"  - DIVNAME: posisi {divname_col}")
    
    # Identifikasi transaksi yang verified berdasarkan duplikat PM + P1/P5 DAN status 704
    verified_transactions = check_transaction_verification_by_duplicates(
        df, transno_col, transdate_col, recordtag_col, transstatus_col)
    
    print(f"Ditemukan {len(verified_transactions)} transaksi verified berdasarkan multiple records")
    
    # Analisis per karyawan berdasarkan RECORDTAG dengan breakdown per divisi
    employee_stats = defaultdict(lambda: defaultdict(lambda: {
        'total_created': 0,
        'total_verified': 0,
        'status_breakdown': defaultdict(int),
        'transactions_created': set(),
        'transactions_verified': set(),
        'role': 'UNKNOWN',
        'division': 'Unknown'
    }))
    
    # Analisis verifier (MANDOR/ASISTEN)
    verifier_stats = defaultdict(lambda: {
        'total_verified': 0,
        'role': 'UNKNOWN',
        'verified_transactions': set(),
        'divisions': set()
    })
    
    # Analisis semua transaksi
    for _, row in df.iterrows():
        try:
            creator_id = str(row.iloc[scanuserid_col]).strip() if pd.notna(row.iloc[scanuserid_col]) else ''
            recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
            status = str(row.iloc[transstatus_col]).strip() if pd.notna(row.iloc[transstatus_col]) else '0'
            transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
            transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
            division = str(row.iloc[divname_col]).strip() if pd.notna(row.iloc[divname_col]) else 'Unknown'
            
            if creator_id:
                # Dapatkan nama karyawan
                if 'get_name' in employee_mapping:
                    creator_name = employee_mapping['get_name'](creator_id)
                else:
                    creator_name = employee_mapping.get(creator_id, f"KARYAWAN-{creator_id}")
                
                # Tentukan role karyawan menggunakan RECORDTAG sebagai metode utama
                if recordtag and recordtag != '':
                    role = get_employee_role_from_recordtag(recordtag)
                else:
                    # Fallback ke metode nama jika RECORDTAG tidak tersedia
                    role = get_employee_role(creator_name)
                
                # Tentukan divisi
                if not division or division == 'None' or division == 'nan':
                    division = 'UNKNOWN'
                
                # Update statistik karyawan per divisi
                employee_stats[creator_name][division]['total_created'] += 1
                employee_stats[creator_name][division]['transactions_created'].add((transno, transdate))
                employee_stats[creator_name][division]['status_breakdown'][status] += 1
                employee_stats[creator_name][division]['role'] = role
                employee_stats[creator_name][division]['division'] = division
                
                # Cek verifikasi berdasarkan duplikat PM + P1/P5 DAN status 704
                is_verified = (transno, transdate) in verified_transactions
                
                if is_verified:
                    employee_stats[creator_name][division]['total_verified'] += 1
                    employee_stats[creator_name][division]['transactions_verified'].add((transno, transdate))
                    
                    # Update statistik verifier
                    verifier_info = verified_transactions[(transno, transdate)]
                    verifier_id = verifier_info['verifier_id']
                    
                    if 'get_name' in employee_mapping:
                        verifier_name = employee_mapping['get_name'](verifier_id)
                    else:
                        verifier_name = employee_mapping.get(verifier_id, f"VERIFIER-{verifier_id}")
                    
                    verifier_stats[verifier_name]['total_verified'] += 1
                    verifier_stats[verifier_name]['role'] = verifier_info['verifier_role']
                    verifier_stats[verifier_name]['verified_transactions'].add((transno, transdate))
                    verifier_stats[verifier_name]['divisions'].add(division)
                
        except Exception as e:
            print(f"Error memproses baris: {e}")
            continue
    
    # Konversi ke format final dan hitung verification rate per divisi
    verification_stats = {}
    verification_stats_by_division = {}
    
    for emp_name, divisions_data in employee_stats.items():
        # Gabungan semua divisi
        total_created_all = sum(div_stats['total_created'] for div_stats in divisions_data.values())
        total_verified_all = sum(div_stats['total_verified'] for div_stats in divisions_data.values())
        verification_rate_all = (total_verified_all / total_created_all * 100) if total_created_all > 0 else 0
        
        # Ambil role dari divisi pertama
        first_division = list(divisions_data.values())[0]
        role = first_division['role']
        
        # Gabungan semua transaksi
        all_transactions_created = set()
        all_transactions_verified = set()
        all_status_breakdown = defaultdict(int)
        divisions_list = []
        
        for div_name, div_stats in divisions_data.items():
            all_transactions_created.update(div_stats['transactions_created'])
            all_transactions_verified.update(div_stats['transactions_verified'])
            for status, count in div_stats['status_breakdown'].items():
                all_status_breakdown[status] += count
            divisions_list.append(div_name)
        
        verification_stats[emp_name] = {
            'employee_name': emp_name,
            'role': role,
            'divisions': divisions_list,
            'total_created': total_created_all,
            'total_verified': total_verified_all,
            'verification_rate': verification_rate_all,
            'unique_transactions': len(all_transactions_created),
            'unique_verified_transactions': len(all_transactions_verified),
            'status_breakdown': dict(all_status_breakdown),
            'by_division': {}
        }
        
        # Detail per divisi
        for div_name, div_stats in divisions_data.items():
            verification_rate_div = (div_stats['total_verified'] / div_stats['total_created'] * 100) if div_stats['total_created'] > 0 else 0
            
            verification_stats[emp_name]['by_division'][div_name] = {
                'division': div_name,
                'total_created': div_stats['total_created'],
                'total_verified': div_stats['total_verified'],
                'verification_rate': verification_rate_div,
                'unique_transactions': len(div_stats['transactions_created']),
                'unique_verified_transactions': len(div_stats['transactions_verified']),
                'status_breakdown': dict(div_stats['status_breakdown'])
            }
            
            # Juga simpan di verification_stats_by_division untuk kemudahan
            key = f"{emp_name} - {div_name}"
            verification_stats_by_division[key] = verification_stats[emp_name]['by_division'][div_name].copy()
            verification_stats_by_division[key]['employee_name'] = emp_name
            verification_stats_by_division[key]['role'] = role
    
    print(f"Analisis selesai untuk {len(verification_stats)} karyawan di {len(verification_stats_by_division)} kombinasi divisi.")
    
    # Tampilkan contoh hasil untuk debugging
    print("\nContoh hasil analisis per karyawan:")
    count = 0
    for emp_name, stats in verification_stats.items():
        if count < 3:
            print(f"  - {emp_name}: {stats['role']}, {len(stats['by_division'])} divisi, "
                  f"{stats['total_created']} transaksi total, {stats['verification_rate']:.1f}% verified")
            for div_name, div_stats in stats['by_division'].items():
                print(f"    * {div_name}: {div_stats['total_created']} transaksi, {div_stats['verification_rate']:.1f}% verified")
            count += 1
    
    print(f"\nStatistik Verifier:")
    for verifier_name, v_stats in verifier_stats.items():
        print(f"  - {verifier_name} ({v_stats['role']}): {v_stats['total_verified']} transaksi verified di {len(v_stats['divisions'])} divisi")
    
    return verification_stats, verification_stats_by_division, verifier_stats

def generate_summary_statistics(verification_stats):
    """
    Membuat statistik ringkasan berdasarkan role dan divisi.
    """
    role_summary = defaultdict(lambda: {
        'employee_count': 0,
        'total_transactions_created': 0,
        'total_transactions_verified': 0,
        'avg_verification_rate': 0,
        'employees': []
    })
    
    division_summary = defaultdict(lambda: {
        'employee_count': 0,
        'total_transactions_created': 0,
        'total_transactions_verified': 0,
        'avg_verification_rate': 0,
        'employees': []
    })
    
    for emp_name, stats in verification_stats.items():
        role = stats['role']
        division = stats['division']
        
        # Summary per role
        role_summary[role]['employee_count'] += 1
        role_summary[role]['total_transactions_created'] += stats['total_created']
        role_summary[role]['total_transactions_verified'] += stats['total_verified']
        role_summary[role]['employees'].append(emp_name)
        
        # Summary per division
        division_summary[division]['employee_count'] += 1
        division_summary[division]['total_transactions_created'] += stats['total_created']
        division_summary[division]['total_transactions_verified'] += stats['total_verified']
        division_summary[division]['employees'].append(emp_name)
    
    # Hitung rata-rata tingkat verifikasi per role
    for role in role_summary:
        employees_in_role = [verification_stats[emp] for emp in role_summary[role]['employees']]
        if employees_in_role:
            avg_rate = sum(emp['verification_rate'] for emp in employees_in_role) / len(employees_in_role)
            role_summary[role]['avg_verification_rate'] = avg_rate
    
    # Hitung rata-rata tingkat verifikasi per division
    for division in division_summary:
        employees_in_division = [verification_stats[emp] for emp in division_summary[division]['employees']]
        if employees_in_division:
            avg_rate = sum(emp['verification_rate'] for emp in employees_in_division) / len(employees_in_division)
            division_summary[division]['avg_verification_rate'] = avg_rate
    
    return dict(role_summary), dict(division_summary)

def create_visualizations(verification_stats, role_summary, division_summary, output_dir, filename_prefix):
    """
    Membuat visualisasi data dengan informasi role dan divisi.
    """
    print("Membuat visualisasi...")
    
    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create 2x3 subplot layout for more comprehensive visualization
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Analisis Kinerja Karyawan FFB Scanner - Komprehensif', fontsize=16, fontweight='bold')
    
    # 1. Chart tingkat verifikasi per karyawan (top 15)
    sorted_employees = sorted(verification_stats.items(), 
                            key=lambda x: x[1]['total_created'], reverse=True)[:15]
    
    if sorted_employees:
        names = [emp[0][:20] + '...' if len(emp[0]) > 20 else emp[0] for emp, _ in sorted_employees]
        rates = [stats['verification_rate'] for _, stats in sorted_employees]
        colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in rates]
        
        axes[0,0].barh(names, rates, color=colors)
        axes[0,0].set_xlabel('Tingkat Verifikasi (%)')
        axes[0,0].set_title('Top 15 Karyawan - Tingkat Verifikasi')
        axes[0,0].grid(axis='x', alpha=0.3)
        
        # Tambahkan nilai di ujung bar
        for i, rate in enumerate(rates):
            axes[0,0].text(rate + 1, i, f'{rate:.1f}%', va='center', fontsize=8)
    
    # 2. Chart total transaksi dibuat per karyawan (top 15)
    if sorted_employees:
        names = [emp[0][:20] + '...' if len(emp[0]) > 20 else emp[0] for emp, _ in sorted_employees]
        totals = [stats['total_created'] for _, stats in sorted_employees]
        
        axes[0,1].barh(names, totals, color='skyblue')
        axes[0,1].set_xlabel('Jumlah Transaksi Dibuat')
        axes[0,1].set_title('Top 15 Karyawan - Total Transaksi Dibuat')
        axes[0,1].grid(axis='x', alpha=0.3)
        
        # Tambahkan nilai di ujung bar
        for i, total in enumerate(totals):
            axes[0,1].text(total + max(totals)*0.01, i, str(total), va='center', fontsize=8)
    
    # 3. Summary per role
    if role_summary:
        roles = list(role_summary.keys())
        emp_counts = [role_summary[role]['employee_count'] for role in roles]
        
        axes[0,2].bar(roles, emp_counts, color=['lightcoral', 'lightblue', 'lightgreen', 'gold'][:len(roles)])
        axes[0,2].set_ylabel('Jumlah Karyawan')
        axes[0,2].set_title('Jumlah Karyawan per Role')
        axes[0,2].grid(axis='y', alpha=0.3)
        
        # Tambahkan nilai di atas bar
        for i, count in enumerate(emp_counts):
            axes[0,2].text(i, count + max(emp_counts)*0.01, str(count), 
                          ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 4. Rata-rata tingkat verifikasi per role
    if role_summary:
        roles = list(role_summary.keys())
        avg_rates = [role_summary[role]['avg_verification_rate'] for role in roles]
        colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in avg_rates]
        
        axes[1,0].bar(roles, avg_rates, color=colors)
        axes[1,0].set_ylabel('Rata-rata Tingkat Verifikasi (%)')
        axes[1,0].set_title('Rata-rata Tingkat Verifikasi per Role')
        axes[1,0].grid(axis='y', alpha=0.3)
        axes[1,0].set_ylim(0, 100)
        
        # Tambahkan nilai di atas bar
        for i, rate in enumerate(avg_rates):
            axes[1,0].text(i, rate + 2, f'{rate:.1f}%', 
                          ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 5. Summary per division (top 10)
    if division_summary:
        # Sort divisions by employee count and take top 10
        sorted_divisions = sorted(division_summary.items(), 
                                key=lambda x: x[1]['employee_count'], reverse=True)[:10]
        
        if sorted_divisions:
            div_names = [div[:15] + '...' if len(div) > 15 else div for div, _ in sorted_divisions]
            div_counts = [stats['employee_count'] for _, stats in sorted_divisions]
            
            axes[1,1].bar(div_names, div_counts, color='lightseagreen')
            axes[1,1].set_ylabel('Jumlah Karyawan')
            axes[1,1].set_title('Top 10 Divisi - Jumlah Karyawan')
            axes[1,1].grid(axis='y', alpha=0.3)
            axes[1,1].tick_params(axis='x', rotation=45)
            
            # Tambahkan nilai di atas bar
            for i, count in enumerate(div_counts):
                axes[1,1].text(i, count + max(div_counts)*0.01, str(count), 
                              ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 6. Rata-rata tingkat verifikasi per division (top 10)
    if division_summary:
        # Sort divisions by verification rate and take top 10
        sorted_divisions = sorted(division_summary.items(), 
                                key=lambda x: x[1]['avg_verification_rate'], reverse=True)[:10]
        
        if sorted_divisions:
            div_names = [div[:15] + '...' if len(div) > 15 else div for div, _ in sorted_divisions]
            div_rates = [stats['avg_verification_rate'] for _, stats in sorted_divisions]
            colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in div_rates]
            
            axes[1,2].bar(div_names, div_rates, color=colors)
            axes[1,2].set_ylabel('Rata-rata Tingkat Verifikasi (%)')
            axes[1,2].set_title('Top 10 Divisi - Tingkat Verifikasi')
            axes[1,2].grid(axis='y', alpha=0.3)
            axes[1,2].set_ylim(0, 100)
            axes[1,2].tick_params(axis='x', rotation=45)
            
            # Tambahkan nilai di atas bar
            for i, rate in enumerate(div_rates):
                axes[1,2].text(i, rate + 2, f'{rate:.1f}%', 
                              ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    # Simpan chart
    chart_filename = f"{filename_prefix}_kinerja_karyawan.png"
    chart_path = os.path.join(output_dir, chart_filename)
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Chart disimpan: {chart_path}")
    return chart_path

def save_excel_report(verification_stats, role_summary, division_summary, output_dir, filename_prefix):
    """
    Menyimpan laporan ke file Excel dengan informasi role dan divisi.
    """
    print("Menyimpan laporan Excel...")
    
    excel_filename = f"{filename_prefix}_laporan_karyawan.xlsx"
    excel_path = os.path.join(output_dir, excel_filename)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Sheet 1: Detail per karyawan
        emp_data = []
        for emp_name, stats in verification_stats.items():
            emp_data.append({
                'Nama Karyawan': emp_name,
                'Role': stats['role'],
                'Divisi': stats['division'],
                'Total Transaksi Dibuat': stats['total_created'],
                'Transaksi Unik Dibuat': stats['unique_transactions'],
                'Total Verifikasi Dilakukan': stats['total_verified'],
                'Tingkat Verifikasi (%)': round(stats['verification_rate'], 2)
            })
        
        df_employees = pd.DataFrame(emp_data)
        df_employees = df_employees.sort_values('Total Transaksi Dibuat', ascending=False)
        df_employees.to_excel(writer, sheet_name='Detail Karyawan', index=False)
        
        # Sheet 2: Summary per role
        role_data = []
        for role, stats in role_summary.items():
            role_data.append({
                'Role': role,
                'Jumlah Karyawan': stats['employee_count'],
                'Total Transaksi Dibuat': stats['total_transactions_created'],
                'Total Verifikasi Dilakukan': stats['total_transactions_verified'],
                'Rata-rata Tingkat Verifikasi (%)': round(stats['avg_verification_rate'], 2)
            })
        
        df_roles = pd.DataFrame(role_data)
        df_roles.to_excel(writer, sheet_name='Summary Role', index=False)
        
        # Sheet 3: Summary per division
        division_data = []
        for division, stats in division_summary.items():
            division_data.append({
                'Divisi': division,
                'Jumlah Karyawan': stats['employee_count'],
                'Total Transaksi Dibuat': stats['total_transactions_created'],
                'Total Verifikasi Dilakukan': stats['total_transactions_verified'],
                'Rata-rata Tingkat Verifikasi (%)': round(stats['avg_verification_rate'], 2)
            })
        
        df_divisions = pd.DataFrame(division_data)
        df_divisions = df_divisions.sort_values('Jumlah Karyawan', ascending=False)
        df_divisions.to_excel(writer, sheet_name='Summary Divisi', index=False)
        
        # Sheet 4: Status breakdown per karyawan
        status_data = []
        for emp_name, stats in verification_stats.items():
            for status, count in stats['status_breakdown'].items():
                status_data.append({
                    'Nama Karyawan': emp_name,
                    'Role': stats['role'],
                    'Divisi': stats['division'],
                    'Status': status,
                    'Jumlah': count
                })
        
        if status_data:
            df_status = pd.DataFrame(status_data)
            df_status.to_excel(writer, sheet_name='Breakdown Status', index=False)
    
    print(f"Laporan Excel disimpan: {excel_path}")
    return excel_path

def generate_pdf_report(verification_stats, role_summary, chart_path, output_dir, filename_prefix):
    """
    Membuat laporan PDF.
    """
    print("Membuat laporan PDF...")
    
    # Siapkan data untuk PDF
    summary_data = {
        'total_employees': len(verification_stats),
        'total_roles': len(role_summary),
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Top performers
    top_performers = sorted(verification_stats.items(), 
                          key=lambda x: x[1]['verification_rate'], reverse=True)[:10]
    
    # Most active creators
    most_active = sorted(verification_stats.items(), 
                        key=lambda x: x[1]['total_created'], reverse=True)[:10]
    
    pdf_filename = f"{filename_prefix}_laporan_karyawan.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    # Gunakan fungsi PDF yang sudah ada (simplified version)
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                   fontSize=16, spaceAfter=30, alignment=1)
        story.append(Paragraph("LAPORAN ANALISIS KINERJA KARYAWAN", title_style))
        story.append(Paragraph(f"Tanggal Analisis: {summary_data['analysis_date']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph("RINGKASAN EKSEKUTIF", styles['Heading2']))
        summary_text = f"""
        Total Karyawan: {summary_data['total_employees']}<br/>
        Total Role: {summary_data['total_roles']}<br/>
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Top Performers Table
        story.append(Paragraph("TOP 10 KARYAWAN - TINGKAT VERIFIKASI TERTINGGI", styles['Heading2']))
        top_data = [['No', 'Nama Karyawan', 'Role', 'Tingkat Verifikasi (%)', 'Total Transaksi']]
        for i, (name, stats) in enumerate(top_performers, 1):
            top_data.append([
                str(i),
                name[:30] + '...' if len(name) > 30 else name,
                stats['role'],
                f"{stats['verification_rate']:.1f}%",
                str(stats['total_created'])
            ])
        
        top_table = Table(top_data)
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(top_table)
        story.append(Spacer(1, 20))
        
        # Add chart if available
        if chart_path and os.path.exists(chart_path):
            story.append(Paragraph("VISUALISASI DATA", styles['Heading2']))
            img = Image(chart_path, width=6*inch, height=4.5*inch)
            story.append(img)
        
        doc.build(story)
        print(f"Laporan PDF disimpan: {pdf_path}")
        return pdf_path
        
    except ImportError:
        print("ReportLab tidak tersedia, melewati pembuatan PDF.")
        return None
    except Exception as e:
        print(f"Error saat membuat PDF: {e}")
        return None

def is_transaction_verified(status_code, status_mapping=None):
    """
    Menentukan apakah transaksi sudah diverifikasi berdasarkan status code.
    
    Args:
        status_code: Status code dari TRANSSTATUS
        status_mapping: Optional mapping dari status code ke nama status
    
    Returns:
        bool: True jika transaksi sudah diverifikasi
    """
    if not status_code:
        return False
    
    status_str = str(status_code).strip()
    
    # Status codes yang dianggap sebagai "verified"
    # Status 704 memiliki NAME='OK' dalam tabel LOOKUP dan dianggap sebagai verified
    verified_status_codes = {
        '1',     # Standard verified status
        '704',   # Status OK - dianggap sebagai VERIFIED berdasarkan LOOKUP table
    }
    
    # Cek berdasarkan status code langsung
    if status_str in verified_status_codes:
        return True
    
    # Cek berdasarkan nama status jika mapping tersedia
    if status_mapping and 'get_status_name' in status_mapping:
        status_name = status_mapping['get_status_name'](status_str).upper()
        verified_status_names = {'VERIFIED', 'APPROVED', 'CONFIRMED', 'VALID', 'OK'}
        if any(verified_name in status_name for verified_name in verified_status_names):
            return True
    
    return False

def check_transaction_verification_by_duplicates(df, transno_col, transdate_col, recordtag_col, transstatus_col):
    """
    Menentukan verifikasi transaksi berdasarkan duplikat TRANSNO+TRANSDATE dengan RECORDTAG berbeda DAN status 704.
    
    LOGIKA VERIFIKASI YANG BENAR:
    - PM (KERANI) membuat transaksi
    - P1 (ASISTEN) atau P5 (MANDOR) memverifikasi dengan membuat record duplikat
    - DAN status code harus 704 (verified)
    
    Args:
        df: DataFrame dengan data transaksi
        transno_col: Index kolom TRANSNO
        transdate_col: Index kolom TRANSDATE  
        recordtag_col: Index kolom RECORDTAG
        transstatus_col: Index kolom TRANSSTATUS
    
    Returns:
        dict: {(transno, transdate): {'verifier_name': str, 'verifier_role': str}}
    """
    verified_transactions = {}
    
    # Group by TRANSNO dan TRANSDATE
    transaction_groups = defaultdict(list)
    
    for _, row in df.iterrows():
        try:
            transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
            transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
            recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
            transstatus = str(row.iloc[transstatus_col]).strip() if pd.notna(row.iloc[transstatus_col]) else ''
            scanuserid = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''  # SCANUSERID
            
            if transno and transdate:
                transaction_groups[(transno, transdate)].append({
                    'transno': transno,
                    'transdate': transdate,
                    'recordtag': recordtag,
                    'transstatus': transstatus,
                    'scanuserid': scanuserid,
                    'row_index': row.name,
                    'full_row': row
                })
        except Exception as e:
            continue
    
    # Identifikasi transaksi yang verified berdasarkan RECORDTAG pairs DAN status 704
    for (transno, transdate), records in transaction_groups.items():
        if len(records) > 1:  # Multiple records dengan TRANSNO+TRANSDATE sama
            recordtags = [r['recordtag'] for r in records]
            
            # Cek apakah ada pasangan PM (KERANI) dengan P1/P5 (ASISTEN/MANDOR)
            has_pm = 'PM' in recordtags
            has_verifier = any(tag in ['P1', 'P5'] for tag in recordtags)
            
            if has_pm and has_verifier:
                # Cek apakah ada status 704 di salah satu record
                has_status_704 = any(r['transstatus'] == '704' for r in records)
                
                if has_status_704:
                    # Cari verifier (P1/P5) dengan status 704
                    verifier_info = None
                    for record in records:
                        if record['recordtag'] in ['P1', 'P5'] and record['transstatus'] == '704':
                            verifier_role = 'ASISTEN' if record['recordtag'] == 'P1' else 'MANDOR'
                            verifier_info = {
                                'verifier_id': record['scanuserid'],
                                'verifier_role': verifier_role,
                                'recordtag': record['recordtag']
                            }
                            break
                    
                    if verifier_info:
                        verified_transactions[(transno, transdate)] = verifier_info
                
    return verified_transactions

def main():
    """Fungsi utama program."""
    parser = argparse.ArgumentParser(description='Analisis Kinerja Karyawan FFB Scanner')
    parser.add_argument('--start-date', type=str, help='Tanggal mulai (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='Tanggal akhir (YYYY-MM-DD)')
    parser.add_argument('--month', type=str, help='Bulan analisis (YYYY-MM)')
    parser.add_argument('--limit', type=int, help='Batasi jumlah data yang diproses')
    parser.add_argument('--output-dir', type=str, default='reports', help='Direktori output')
    parser.add_argument('--db-path', type=str, help='Path ke database Firebird')
    
    args = parser.parse_args()
    
    # Tentukan periode analisis
    if args.month:
        year, month = map(int, args.month.split('-'))
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
    elif args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    else:
        # Default: bulan ini
        today = date.today()
        start_date = date(today.year, today.month, 1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1)
        else:
            end_date = date(today.year, today.month + 1, 1)
    
    print(f"Periode analisis: {start_date} hingga {end_date}")
    
    # Setup direktori output
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Koneksi database
    db_path = args.db_path or r'D:\IFESS Firebird Database\MILL04.FDB'
    
    try:
        print(f"Menghubungkan ke database: {db_path}")
        connector = FirebirdConnector(db_path)
        
        if not connector.test_connection():
            print("Gagal terhubung ke database!")
            return
        
        print("Koneksi database berhasil!")
        
        # Ambil mapping data
        employee_mapping = get_employee_mapping(connector)
        transstatus_mapping = get_transstatus_mapping(connector)
        division_mapping = get_division_mapping(connector)
        
        # Ambil data transaksi
        df = get_all_transactions_data_with_divisions(connector, start_date.strftime('%Y-%m-%d'), 
                                     end_date.strftime('%Y-%m-%d'), args.limit)
        
        if df.empty:
            print("Tidak ada data transaksi yang ditemukan!")
            return
        
        # Analisis data
        verification_stats, verification_stats_by_division, verifier_stats = analyze_employee_performance_comprehensive(
            df, employee_mapping, transstatus_mapping, division_mapping)
        
        if not verification_stats:
            print("Tidak ada statistik yang dapat dihasilkan!")
            return
        
        # Generate summary
        role_summary, division_summary = generate_summary_statistics(verification_stats)
        
        # Buat nama file
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_prefix = f"analisis_karyawan_{date_str}"
        
        # Buat visualisasi
        chart_path = create_visualizations(verification_stats, role_summary, division_summary,
                                         args.output_dir, filename_prefix)
        
        # Simpan laporan Excel
        excel_path = save_excel_report(verification_stats, role_summary, division_summary,
                                     args.output_dir, filename_prefix)
        
        # Buat laporan PDF
        pdf_path = generate_pdf_report(verification_stats, role_summary, chart_path,
                                     args.output_dir, filename_prefix)
        
        # Tampilkan ringkasan
        print("\n" + "="*60)
        print("RINGKASAN ANALISIS KINERJA KARYAWAN")
        print("="*60)
        print(f"Total karyawan dianalisis: {len(verification_stats)}")
        print(f"Total role: {len(role_summary)}")
        print(f"Total divisi: {len(division_summary)}")
        
        print("\nSummary per Role:")
        for role, stats in role_summary.items():
            print(f"  {role}: {stats['employee_count']} orang, "
                  f"rata-rata verifikasi {stats['avg_verification_rate']:.1f}%")
        
        print("\nTop 5 Divisi (berdasarkan jumlah karyawan):")
        sorted_divisions = sorted(division_summary.items(), 
                                key=lambda x: x[1]['employee_count'], reverse=True)[:5]
        for division, stats in sorted_divisions:
            print(f"  {division}: {stats['employee_count']} orang, "
                  f"rata-rata verifikasi {stats['avg_verification_rate']:.1f}%")
        
        print(f"\nLaporan disimpan:")
        print(f"  - Excel: {excel_path}")
        if pdf_path:
            print(f"  - PDF: {pdf_path}")
        print(f"  - Chart: {chart_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()