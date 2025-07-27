#!/usr/bin/env python3
"""
Sistem Analisis MANDOR Per Divisi - Versi Diperbaiki
Definisi Role yang Benar:
- P1 = MANDOR
- P5 = ASISTEN  
- PM = KERANI
"""

import os
import sys
import pandas as pd
from datetime import datetime
from collections import defaultdict
import traceback

# Add the all_transaksi directory to Python path
sys.path.append(os.path.dirname(__file__))

from firebird_connector import FirebirdConnector

# Konfigurasi database
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def get_employee_role_corrected(recordtag):
    """
    Menentukan role karyawan berdasarkan RECORDTAG yang benar.
    
    Args:
        recordtag: Field RECORDTAG dari transaksi
    
    Returns:
        str: Role karyawan
    """
    if not recordtag:
        return 'LAINNYA'
    
    recordtag_str = str(recordtag).strip().upper()
    
    # Mapping berdasarkan RECORDTAG yang BENAR
    role_mapping = {
        'PM': 'KERANI',    # Plantation Manager/Kerani (tetap sama)
        'P1': 'MANDOR',    # MANDOR (diperbaiki dari sebelumnya P5)
        'P5': 'ASISTEN',   # ASISTEN (diperbaiki dari sebelumnya P1)
    }
    
    return role_mapping.get(recordtag_str, 'LAINNYA')

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
    
    def get_employee_name(emp_id):
        emp_id_str = str(emp_id).strip()
        if emp_id_str in employee_mapping:
            return employee_mapping[emp_id_str]
        return f"KARYAWAN-{emp_id_str}"
    
    employee_mapping['get_name'] = get_employee_name
    print(f"Total mapping karyawan: {len(employee_mapping)-1}")
    return employee_mapping

def get_divisions(connector):
    """
    Mendapatkan daftar divisi dari database (alias untuk GUI compatibility).
    """
    return get_division_list(connector)

def get_division_list(connector):
    """
    Mendapatkan daftar divisi dari database.
    """
    print("Mendapatkan daftar divisi...")
    query = """
    SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
    FROM OCFIELD b
    LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
    WHERE b.DIVID IS NOT NULL
    ORDER BY c.DIVNAME
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        divisions = []
        if not df.empty:
            for _, row in df.iterrows():
                div_id = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                div_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                div_code = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
                
                if div_id and div_name:
                    divisions.append({
                        'div_id': div_id,
                        'div_name': div_name,
                        'div_code': div_code
                    })
            
            print(f"Ditemukan {len(divisions)} divisi")
        
        return divisions
    except Exception as e:
        print(f"Error mengambil daftar divisi: {e}")
        return []

def analyze_division_transactions(connector, employee_mapping, div_id, div_name, month=4, year=2025):
    """
    Menganalisis transaksi per divisi dengan role yang benar.
    Updated with corrected date range for April 2025 verification.
    """
    print(f"\nMenganalisis divisi: {div_name} (ID: {div_id})")

    # Corrected date range - use EXACT same query as user provided
    if month == 4 and year == 2025:
        date_filter = f"AND a.TRANSDATE >= '2025-04-01' AND a.TRANSDATE < '2025-04-29'"
        print(f"  Using EXACT user query date range: >= '2025-04-01' AND < '2025-04-29'")
    else:
        # Standard date range for other months
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        date_filter = f"AND a.TRANSDATE >= '{year}-{month:02d}-01' AND a.TRANSDATE < '{next_year}-{next_month:02d}-01'"

    # Query untuk mendapatkan semua transaksi di divisi ini
    query = f"""
    SELECT
        a.ID,
        a.SCANUSERID,
        a.OCID,
        a.WORKERID,
        a.CARRIERID,
        a.FIELDID,
        a.TASKNO,
        a.RIPEBCH,
        a.UNRIPEBCH,
        a.BLACKBCH,
        a.ROTTENBCH,
        a.LONGSTALKBCH,
        a.RATDMGBCH,
        a.LOOSEFRUIT,
        a.TRANSNO,
        a.TRANSDATE,
        a.TRANSTIME,
        a.UPLOADDATETIME,
        a.RECORDTAG,
        a.TRANSSTATUS,
        a.TRANSTYPE,
        a.LASTUSER,
        a.LASTUPDATED,
        a.UNDERRIPEBCH,
        a.OVERRIPEBCH,
        a.ABNORMALBCH,
        a.LOOSEFRUIT2,
        b.DIVID AS DIVISI_ID,
        b.FIELDNO AS FIELD_NO
    FROM
        FFBSCANNERDATA{month:02d} a
    JOIN
        OCFIELD b ON a.FIELDID = b.ID
    WHERE
        b.DIVID = '{div_id}'
        {date_filter}
    ORDER BY a.SCANUSERID, a.TRANSDATE, a.TRANSTIME
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df.empty:
            print(f"  Tidak ada transaksi di divisi {div_name}")
            return None
        
        print(f"  Ditemukan {len(df)} transaksi")
        
        # Enhanced analysis per role with verification-focused logic
        role_stats = defaultdict(lambda: defaultdict(lambda: {
            'employee_id': '',
            'employee_name': '',
            'role': '',
            'total_transactions': 0,
            'verified_transactions': 0,
            'transaction_details': []
        }))

        # Separate tracking for verification calculations
        verification_stats = {
            'total_kerani_transactions': 0,  # Total PM transactions (tanpa filter status)
            'total_mandor_transactions': 0,  # Total P1 transactions (tanpa filter status)
            'total_asisten_transactions': 0,  # Total P5 transactions (tanpa filter status)
            'total_verifications': 0,  # Total P1 + P5 transactions
            'manager_verifications': 0   # Currently not used but kept for completeness
        }

        # Column mapping
        scanuserid_col = 1   # SCANUSERID
        recordtag_col = 18   # RECORDTAG
        transstatus_col = 19 # TRANSSTATUS
        transno_col = 14     # TRANSNO
        transdate_col = 15   # TRANSDATE

        for _, row in df.iterrows():
            try:
                scanner_user_id = str(row.iloc[scanuserid_col]).strip() if pd.notna(row.iloc[scanuserid_col]) else ''
                recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
                transstatus = str(row.iloc[transstatus_col]).strip() if pd.notna(row.iloc[transstatus_col]) else ''
                transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
                transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''

                if scanner_user_id and recordtag:
                    # Determine role dengan mapping yang benar
                    role = get_employee_role_corrected(recordtag)

                    # Get employee name
                    if 'get_name' in employee_mapping:
                        employee_name = employee_mapping['get_name'](scanner_user_id)
                    else:
                        employee_name = employee_mapping.get(scanner_user_id, f"EMPLOYEE-{scanner_user_id}")

                    # Update statistics (hanya sekali, tidak duplikasi)
                    role_stats[role][scanner_user_id]['employee_id'] = scanner_user_id
                    role_stats[role][scanner_user_id]['employee_name'] = employee_name
                    role_stats[role][scanner_user_id]['role'] = role
                    role_stats[role][scanner_user_id]['total_transactions'] += 1

                    # Count ALL transactions by type (TANPA filter status)
                    if recordtag == 'PM':  # KERANI transactions
                        verification_stats['total_kerani_transactions'] += 1
                    elif recordtag == 'P1':  # MANDOR transactions
                        verification_stats['total_mandor_transactions'] += 1
                        verification_stats['total_verifications'] += 1
                    elif recordtag == 'P5':  # ASISTEN transactions
                        verification_stats['total_asisten_transactions'] += 1
                        verification_stats['total_verifications'] += 1

                    # Track verified transactions (status 704) for individual stats
                    if transstatus == '704':
                        role_stats[role][scanner_user_id]['verified_transactions'] += 1

                    role_stats[role][scanner_user_id]['transaction_details'].append({
                        'transno': transno,
                        'transdate': transdate,
                        'transstatus': transstatus,
                        'recordtag': recordtag
                    })

            except Exception as e:
                continue

        # Calculate verification percentage and individual contributions
        total_kerani = verification_stats['total_kerani_transactions']
        total_verifications = verification_stats['total_verifications']

        # Overall verification rate
        verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0

        # Calculate individual contribution percentages
        for role_name, role_data in role_stats.items():
            for emp_id, emp_data in role_data.items():
                emp_transactions = emp_data['total_transactions']
                # Contribution percentage = (individual transactions / total kerani transactions) * 100
                contribution_percentage = (emp_transactions / total_kerani * 100) if total_kerani > 0 else 0
                emp_data['contribution_percentage'] = contribution_percentage

        return {
            'div_id': div_id,
            'div_name': div_name,
            'total_transactions': len(df),
            'role_stats': role_stats,
            'verification_stats': verification_stats,
            'verification_rate': verification_rate
        }
        
    except Exception as e:
        print(f"  Error menganalisis divisi {div_name}: {e}")
        return None

def generate_division_report(division_results, output_dir, month, year):
    """
    Membuat laporan per divisi dalam format Excel seperti yang diminta.
    """
    print("\nMembuat laporan per divisi...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"laporan_mandor_per_divisi_{month:02d}_{year}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        
        # Sheet 1: Summary All Divisions
        summary_data = []

        for div_result in division_results:
            if div_result is None:
                continue

            div_name = div_result['div_name']
            role_stats = div_result['role_stats']
            verification_stats = div_result.get('verification_stats', {})

            # Use verification_stats for accurate calculations (TANPA filter status)
            total_kerani = verification_stats.get('total_kerani_transactions', 0)
            total_mandor = verification_stats.get('total_mandor_transactions', 0)
            total_asisten = verification_stats.get('total_asisten_transactions', 0)
            total_verifications = verification_stats.get('total_verifications', 0)

            # Calculate verification rate: (mandor + asisten) / kerani * 100
            verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
            mandor_contribution_pct = (total_mandor / total_kerani * 100) if total_kerani > 0 else 0
            asisten_contribution_pct = (total_asisten / total_kerani * 100) if total_kerani > 0 else 0
            manager_contribution_pct = 0.0  # Currently not used

            summary_data.append({
                'Division': div_name,
                'Total_KERANI_Transactions': total_kerani,
                'Total_MANDOR_Transactions': total_mandor,
                'Total_ASISTEN_Transactions': total_asisten,
                'Total_Verifications': total_verifications,
                'Verification_Rate': f"{verification_rate:.2f}%",
                'Manager_Contribution': f"{manager_contribution_pct:.2f}%",
                'Assistant_Contribution': f"{asisten_contribution_pct:.2f}%",
                'Mandore_Contribution': f"{mandor_contribution_pct:.2f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary All Divisions', index=False)
        
        # Sheet per divisi (format sesuai dengan verification data yang diharapkan)
        for div_result in division_results:
            if div_result is None:
                continue

            div_name = div_result['div_name']
            role_stats = div_result['role_stats']
            verification_stats = div_result.get('verification_stats', {})

            # Buat data seperti format verification yang diminta
            division_data = []

            # KERANI data (PM transactions - Bunch Counter)
            for emp_id, emp_data in role_stats.get('KERANI', {}).items():
                division_data.append({
                    'Division': div_name,
                    'Scanner_User': emp_data['employee_name'],
                    'Scanner_User_ID': emp_id,
                    'Role': 'KERANI',
                    'Conductor': 0,  # KERANI tidak melakukan conduct
                    'Assistant': 0,  # KERANI tidak melakukan assist
                    'Manager': 0,    # KERANI tidak melakukan manage
                    'Bunch_Counter': emp_data['total_transactions']  # KERANI membuat transaksi (PM)
                })

            # MANDOR data (P1 transactions - Conductor)
            for emp_id, emp_data in role_stats.get('MANDOR', {}).items():
                division_data.append({
                    'Division': div_name,
                    'Scanner_User': emp_data['employee_name'],
                    'Scanner_User_ID': emp_id,
                    'Role': 'MANDOR',
                    'Conductor': emp_data['total_transactions'],  # MANDOR transactions (all status)
                    'Assistant': 0,
                    'Manager': 0,
                    'Bunch_Counter': 0
                })

            # ASISTEN data (P5 transactions - Assistant)
            for emp_id, emp_data in role_stats.get('ASISTEN', {}).items():
                division_data.append({
                    'Division': div_name,
                    'Scanner_User': emp_data['employee_name'],
                    'Scanner_User_ID': emp_id,
                    'Role': 'ASISTEN',
                    'Conductor': 0,
                    'Assistant': emp_data['total_transactions'],  # ASISTEN transactions (all status)
                    'Manager': 0,
                    'Bunch_Counter': 0
                })

            if division_data:
                division_df = pd.DataFrame(division_data)

                # Use verification_stats for accurate calculations (TANPA filter status)
                total_kerani = verification_stats.get('total_kerani_transactions', 0)
                total_mandor = verification_stats.get('total_mandor_transactions', 0)
                total_asisten = verification_stats.get('total_asisten_transactions', 0)
                total_verifications = verification_stats.get('total_verifications', 0)

                # Calculate contribution rates: individual transactions / total kerani transactions * 100
                verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
                mandor_contribution_pct = (total_mandor / total_kerani * 100) if total_kerani > 0 else 0
                asisten_contribution_pct = (total_asisten / total_kerani * 100) if total_kerani > 0 else 0
                manager_contribution_pct = 0.0

                # Add summary rows in the expected format
                summary_row = pd.DataFrame([{
                    'Division': '',
                    'Scanner_User': f'Total KERANI Transactions: {total_kerani}',
                    'Scanner_User_ID': f'Total Verifications: {total_verifications}',
                    'Role': f'Verification Rate: {verification_rate:.2f}%',
                    'Conductor': '',
                    'Assistant': '',
                    'Manager': '',
                    'Bunch_Counter': ''
                }])

                # Contribution rates in the expected format
                contribution_row = pd.DataFrame([{
                    'Division': '',
                    'Scanner_User': f'Manager Contribution: {manager_contribution_pct:.2f}%',
                    'Scanner_User_ID': f'Assistant Contribution: {asisten_contribution_pct:.2f}%',
                    'Role': f'Mandore Contribution: {mandor_contribution_pct:.2f}%',
                    'Conductor': '',
                    'Assistant': '',
                    'Manager': '',
                    'Bunch_Counter': ''
                }])

                # Combine all data
                final_df = pd.concat([division_df, summary_row, contribution_row], ignore_index=True)
                
                # Clean sheet name
                sheet_name = div_name.replace('/', '_').replace('\\', '_')[:31]
                final_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Sheet 3: Detail Employee Mapping
        mapping_data = []
        for div_result in division_results:
            if div_result is None:
                continue
                
            div_name = div_result['div_name']
            role_stats = div_result['role_stats']
            
            for role, employees in role_stats.items():
                for emp_id, emp_data in employees.items():
                    mapping_data.append({
                        'Division': div_name,
                        'Employee_ID': emp_id,
                        'Employee_Name': emp_data['employee_name'],
                        'Role': role,
                        'Total_Transactions': emp_data['total_transactions'],
                        'Transaction_Rate': f"{(emp_data['total_transactions']/emp_data['total_transactions']*100):.2f}%" if emp_data['total_transactions'] > 0 else "0%"
                    })
        
        mapping_df = pd.DataFrame(mapping_data)
        mapping_df.to_excel(writer, sheet_name='Employee Mapping', index=False)
    
    print(f"Laporan disimpan: {filepath}")
    return filepath

def generate_specific_division_analysis(connector, employee_mapping, div_id, div_name, month=4, year=2025):
    """
    Generate detailed analysis for a specific division using corrected date range.
    Returns formatted results matching verification data structure.
    """
    print(f"\nAnalyzing {div_name} (Division ID: {div_id}) with corrected date range")
    print("-" * 60)

    # Use corrected date range for April 2025
    if month == 4 and year == 2025:
        date_filter = "AND a.TRANSDATE >= '2025-04-01' AND a.TRANSDATE < '2025-04-29'"
    else:
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        date_filter = f"AND a.TRANSDATE >= '{year}-{month:02d}-01' AND a.TRANSDATE < '{next_year}-{next_month:02d}-01'"

    # Query for total receipts (PM transactions only)
    receipts_query = f"""
    SELECT COUNT(*) as total_receipts
    FROM FFBSCANNERDATA{month:02d} a
    JOIN OCFIELD b ON a.FIELDID = b.ID
    WHERE b.DIVID = '{div_id}'
        AND a.RECORDTAG = 'PM'
        {date_filter}
    """

    try:
        result = connector.execute_query(receipts_query)
        receipts_df = connector.to_pandas(result)
        total_receipts = int(receipts_df.iloc[0, 0]) if not receipts_df.empty else 0

        print(f"Total Receipts (PM transactions): {total_receipts}")

        # Query for detailed breakdown by employee and role
        detail_query = f"""
        SELECT
            a.SCANUSERID,
            a.RECORDTAG,
            a.TRANSSTATUS,
            COUNT(*) as transaction_count
        FROM FFBSCANNERDATA{month:02d} a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        WHERE b.DIVID = '{div_id}'
            {date_filter}
            AND a.RECORDTAG IN ('PM', 'P1', 'P5')
        GROUP BY a.SCANUSERID, a.RECORDTAG, a.TRANSSTATUS
        ORDER BY a.SCANUSERID, a.RECORDTAG
        """

        detail_result = connector.execute_query(detail_query)
        detail_df = connector.to_pandas(detail_result)

        if detail_df.empty:
            print(f"No transaction data found for {div_name}")
            return None

        # Process employee breakdown
        employee_breakdown = defaultdict(lambda: {
            'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 0
        })

        transaction_counts = {'mandor': 0, 'asisten': 0, 'manager': 0}

        for _, row in detail_df.iterrows():
            user_id = str(row.iloc[0]).strip()
            recordtag = str(row.iloc[1]).strip()
            transstatus = str(row.iloc[2]).strip()
            count = int(row.iloc[3])

            emp_name = employee_mapping.get(user_id, f"UNKNOWN-{user_id}")

            if recordtag == 'PM':
                employee_breakdown[emp_name]['bunch_counter'] += count
            elif recordtag == 'P1':  # MANDOR - all transactions
                employee_breakdown[emp_name]['conductor'] += count
                transaction_counts['mandor'] += count
            elif recordtag == 'P5':  # ASISTEN - all transactions
                employee_breakdown[emp_name]['assistant'] += count
                transaction_counts['asisten'] += count

        # Calculate transaction rates
        mandor_rate = (transaction_counts['mandor'] / total_receipts * 100) if total_receipts > 0 else 0
        asisten_rate = (transaction_counts['asisten'] / total_receipts * 100) if total_receipts > 0 else 0
        manager_rate = (transaction_counts['manager'] / total_receipts * 100) if total_receipts > 0 else 0

        print(f"\nEmployee Breakdown:")
        for emp_name, counts in employee_breakdown.items():
            if any(counts.values()):
                print(f"  {emp_name}: {counts['conductor']} Conductor, {counts['assistant']} Assistant, {counts['manager']} Manager, {counts['bunch_counter']} Bunch Counter")

        print(f"\nTransaction Rates:")
        print(f"  Manager: {manager_rate:.2f}%")
        print(f"  Assistant: {asisten_rate:.2f}%")
        print(f"  Mandore: {mandor_rate:.2f}%")

        return {
            'division': div_name,
            'total_receipts': total_receipts,
            'employee_breakdown': dict(employee_breakdown),
            'transaction_rates': {
                'manager': manager_rate,
                'assistant': asisten_rate,
                'mandore': mandor_rate
            },
            'transaction_counts': transaction_counts
        }

    except Exception as e:
        print(f"Error analyzing {div_name}: {e}")
        return None

def main():
    """
    Fungsi utama untuk menjalankan analisis MANDOR per divisi yang diperbaiki.
    """
    try:
        print("ANALISIS MANDOR PER DIVISI - VERSI DIPERBAIKI")
        print("="*60)
        print("Role Definition:")
        print("- P1 = MANDOR")
        print("- P5 = ASISTEN") 
        print("- PM = KERANI")
        print("="*60)
        print("Note: Menghitung SEMUA transaksi (tanpa filter status)")
        print("="*60)
        
        # Setup database connection
        print("Menghubungkan ke database...")
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("Koneksi database gagal!")
            return
        
        print("Koneksi database berhasil")
        
        # Load employee mapping
        employee_mapping = get_employee_mapping(connector)
        
        # Get division list
        divisions = get_division_list(connector)
        
        if not divisions:
            print("Tidak ada divisi ditemukan!")
            return
        
        # Set period untuk analisis (April 2025 with corrected date range)
        year = 2025
        month = 4

        print(f"\nPeriode analisis: {month:02d}/{year} (Corrected Date Range: < 2025-04-30)")
        print(f"Menganalisis {len(divisions)} divisi...")

        # Test specific divisions with corrected date range first
        target_divisions = [
            {'div_id': '15', 'div_name': 'Air Batu'},
            {'div_id': '16', 'div_name': 'Air Kundo'},
            {'div_id': '17', 'div_name': 'Air Hijau'}
        ]

        print("\n" + "="*70)
        print("TESTING CORRECTED DATE RANGE ON TARGET DIVISIONS")
        print("(Menghitung semua transaksi tanpa filter status)")
        print("="*70)

        for target_div in target_divisions:
            result = generate_specific_division_analysis(
                connector, employee_mapping,
                target_div['div_id'], target_div['div_name'], month, year)

            if result:
                print(f"\n✓ {target_div['div_name']} analysis completed successfully")
            else:
                print(f"\n✗ {target_div['div_name']} analysis failed")

        print("\n" + "="*70)
        print("FULL DIVISION ANALYSIS")
        print("(Menghitung semua transaksi tanpa filter status)")
        print("="*70)

        # Analyze each division
        division_results = []

        for division in divisions:
            div_id = division['div_id']
            div_name = division['div_name']

            result = analyze_division_transactions(
                connector, employee_mapping, div_id, div_name, month, year)

            if result:
                division_results.append(result)

                # Print summary for this division
                role_stats = result['role_stats']
                verification_stats = result.get('verification_stats', {})

                total_kerani = verification_stats.get('total_kerani_transactions', 0)
                total_mandor = verification_stats.get('total_mandor_transactions', 0)
                total_asisten = verification_stats.get('total_asisten_transactions', 0)
                total_verifications = verification_stats.get('total_verifications', 0)

                print(f"  📍 Divisi {div_name}:")
                print(f"    - KERANI: {len(role_stats.get('KERANI', {}))} orang")
                print(f"    - MANDOR: {len(role_stats.get('MANDOR', {}))} orang")
                print(f"    - ASISTEN: {len(role_stats.get('ASISTEN', {}))} orang")
                print(f"    - Total transaksi KERANI (PM): {total_kerani}")
                print(f"    - Total verifikasi MANDOR (P1): {total_mandor}")
                print(f"    - Total verifikasi ASISTEN (P5): {total_asisten}")
                print(f"    - Total verifikasi: {total_verifications}")

                # Calculate and display verification rates (CORRECTED)
                if total_kerani > 0:
                    verification_rate = (total_verifications / total_kerani * 100)
                    mandor_contribution = (total_mandor / total_kerani * 100)
                    asisten_contribution = (total_asisten / total_kerani * 100)
                    print(f"    - Tingkat verifikasi: {verification_rate:.2f}%")
                    print(f"    - Kontribusi MANDOR: {mandor_contribution:.2f}%")
                    print(f"    - Kontribusi ASISTEN: {asisten_contribution:.2f}%")

                # Special check for Erly in Air Kundo
                if div_name == 'Air Kundo':
                    kerani_data = role_stats.get('KERANI', {})
                    for emp_id, emp_data in kerani_data.items():
                        if emp_id == '4771':  # Erly
                            emp_name = emp_data['employee_name']
                            transactions = emp_data['total_transactions']
                            print(f"    ⭐ {emp_name} (ID: {emp_id}): {transactions} transaksi")
                            print(f"       Expected: 123 - {'✓ MATCH' if transactions == 123 else '✗ MISMATCH'}")

        if not division_results:
            print("Tidak ada data transaksi ditemukan!")
            return

        # Generate report
        output_dir = "reports"
        report_path = generate_division_report(division_results, output_dir, month, year)
        
        # Generate console summary
        print("\n" + "="*80)
        print("RINGKASAN ANALISIS MANDOR PER DIVISI")
        print("(Menghitung semua transaksi tanpa filter status)")
        print("="*80)
        
        total_divisions = len(division_results)
        total_transactions = sum(result['total_transactions'] for result in division_results)
        
        print(f"Total Divisi Dianalisis: {total_divisions}")
        print(f"Total Transaksi: {total_transactions}")
        
        # Summary per role across all divisions
        all_kerani = set()
        all_mandor = set()
        all_asisten = set()
        
        for result in division_results:
            role_stats = result['role_stats']
            all_kerani.update(role_stats.get('KERANI', {}).keys())
            all_mandor.update(role_stats.get('MANDOR', {}).keys())
            all_asisten.update(role_stats.get('ASISTEN', {}).keys())
        
        print(f"\nTotal Unique Employees:")
        print(f"- KERANI: {len(all_kerani)} orang")
        print(f"- MANDOR: {len(all_mandor)} orang") 
        print(f"- ASISTEN: {len(all_asisten)} orang")
        
        print(f"\nLAPORAN SELESAI!")
        print(f"File disimpan di: {report_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 