"""
Program untuk menganalisis perbedaan data panen antara Kerani dan Asisten.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import calendar
import argparse
from firebird_connector import FirebirdConnector
from pdf_report_advanced import generate_advanced_pdf_report

def get_employee_mapping(connector):
    """
    Mendapatkan mapping antara ID dan NAME dari tabel EMP.

    Args:
        connector: FirebirdConnector instance

    Returns:
        dict: Mapping dari ID ke NAME
    """
    print("Mendapatkan data mapping ID ke NAME dari tabel EMP...")
    query = """
    SELECT ID, NAME
    FROM EMP
    """

    result = connector.execute_query(query)
    df = connector.to_pandas(result)

    # Buat mapping dari ID ke NAME
    employee_mapping = {}

    # Jika berhasil mendapatkan data dari database
    if not df.empty:
        print(f"Berhasil mendapatkan {len(df)} data karyawan dari database.")

        # Cari kolom yang berisi ID dan NAME
        id_col = None
        name_col = None

        # Cari kolom ID
        for col in df.columns:
            if 'ID' in col.upper() and id_col is None:
                id_col = col
                print(f"Menggunakan kolom {col} sebagai ID")

        # Cari kolom NAME
        for col in df.columns:
            if 'NAME' in col.upper() and name_col is None:
                name_col = col
                print(f"Menggunakan kolom {col} sebagai NAME")

        # Jika kedua kolom ditemukan, buat mapping
        if id_col is not None and name_col is not None:
            for _, row in df.iterrows():
                emp_id = str(row[id_col]).strip()
                emp_name = str(row[name_col]).strip()
                if emp_id and emp_name:
                    employee_mapping[emp_id] = emp_name

            print(f"Berhasil membuat mapping untuk {len(employee_mapping)} karyawan dari database.")
    else:
        print("Tidak dapat mendapatkan data EMP dari database.")

    # Tambahkan mapping default untuk ID yang sering muncul (sebagai fallback)
    default_mapping = {
        '4771': 'KERANI',
        '5044': 'ASISTEN',
        '20001': 'ADMIN',
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

    # Fungsi untuk mendapatkan nama karyawan berdasarkan ID
    def get_employee_name(emp_id):
        emp_id_str = str(emp_id).strip()
        if emp_id_str in employee_mapping:
            return employee_mapping[emp_id_str]
        return f"KARYAWAN-{emp_id_str}"

    # Tambahkan fungsi ke mapping untuk memudahkan akses
    employee_mapping['get_name'] = get_employee_name

    print(f"Berhasil membuat mapping total untuk {len(employee_mapping)-1} karyawan.")
    return employee_mapping

def get_transstatus_mapping(connector):
    """
    Mendapatkan mapping kode TRANSSTATUS ke deskripsi dari tabel LOOKUP.

    Args:
        connector: FirebirdConnector instance

    Returns:
        dict: Mapping kode TRANSSTATUS ke deskripsi
    """
    print("Mendapatkan data mapping TRANSSTATUS dari tabel LOOKUP...")
    query = """
    SELECT a.ID, a.SHORTCODE, a.NAME
    FROM LOOKUP a
    """
    result = connector.execute_query(query)
    df = connector.to_pandas(result)

    if df.empty:
        print("Tidak dapat mendapatkan data LOOKUP.")
        return {}

    # Buat mapping dari ID ke NAME
    transstatus_mapping = {}

    # Cari kolom ID dan NAME
    id_col = None
    name_col = None

    # Cari kolom ID
    for col in df.columns:
        if 'ID' == col.upper() or col.upper() == 'ID':
            id_col = col
            print(f"Menggunakan kolom {col} sebagai ID")
            break

    # Jika tidak ditemukan, coba cari dengan cara lain
    if id_col is None:
        for col in df.columns:
            if 'ID' in col.upper() and id_col is None:
                id_col = col
                print(f"Menggunakan kolom {col} sebagai ID")
                break

    # Cari kolom NAME
    for col in df.columns:
        if 'NAME' == col.upper() or col.upper() == 'NAME':
            name_col = col
            print(f"Menggunakan kolom {col} sebagai NAME")
            break

    # Jika tidak ditemukan, coba cari dengan cara lain
    if name_col is None:
        for col in df.columns:
            if 'NAME' in col.upper() and name_col is None:
                name_col = col
                print(f"Menggunakan kolom {col} sebagai NAME")
                break

    # Jika kedua kolom ditemukan, buat mapping
    if id_col is not None and name_col is not None:
        for _, row in df.iterrows():
            status_id = str(row[id_col]).strip() if row[id_col] else ''
            status_name = str(row[name_col]).strip() if row[name_col] else ''

            # Hanya tambahkan jika kedua nilai tidak kosong
            if status_id and status_name:
                transstatus_mapping[status_id] = status_name

        print(f"Berhasil membuat mapping untuk {len(transstatus_mapping)} status dari database.")
    else:
        print("Tidak dapat menemukan kolom ID atau NAME dalam hasil query.")

    # Tambahkan beberapa mapping default untuk status yang sering digunakan (sebagai fallback)
    default_mapping = {
        '1': 'Verified',
        '2': 'Pending',
        '3': 'Rejected',
        '4': 'Cancelled',
        '5': 'Deleted'
    }

    # Update mapping dengan default jika belum ada
    for status_id, status_name in default_mapping.items():
        if status_id not in transstatus_mapping:
            transstatus_mapping[status_id] = status_name

    # Fungsi untuk mendapatkan nama status berdasarkan ID
    def get_status_name(status_id):
        status_id_str = str(status_id).strip()
        if status_id_str in transstatus_mapping:
            return transstatus_mapping[status_id_str]
        return f"STATUS-{status_id_str}"

    # Tambahkan fungsi ke mapping untuk memudahkan akses
    transstatus_mapping['get_status_name'] = get_status_name

    print(f"Berhasil membuat mapping total untuk {len(transstatus_mapping)-1} status.")
    return transstatus_mapping

def get_field_mapping(connector):
    """
    Mendapatkan mapping antara FieldID dan FieldNo dari tabel OCFIELD.

    Args:
        connector: FirebirdConnector instance

    Returns:
        dict: Mapping dari FieldID ke FieldNo
    """
    print("Mendapatkan data mapping FieldID ke FieldNo...")
    query = """
    SELECT ID, FIELDNO
    FROM OCFIELD
    """

    result = connector.execute_query(query)
    df = connector.to_pandas(result)

    if df.empty:
        print("Tidak dapat mendapatkan data OCFIELD.")
        return {}

    # Buat mapping dari FieldID ke FieldNo
    field_mapping = {}

    # Cari kolom ID dan FIELDNO
    id_col = None
    fieldno_col = None

    # Cari kolom ID
    for col in df.columns:
        if 'ID' == col.upper() or col.upper() == 'ID':
            id_col = col
            print(f"Menggunakan kolom {col} sebagai ID")
            break

    # Jika tidak ditemukan, coba cari dengan cara lain
    if id_col is None:
        for col in df.columns:
            if 'ID' in col.upper() and id_col is None:
                id_col = col
                print(f"Menggunakan kolom {col} sebagai ID")
                break

    # Cari kolom FIELDNO
    for col in df.columns:
        if 'FIELDNO' == col.upper() or col.upper() == 'FIELDNO':
            fieldno_col = col
            print(f"Menggunakan kolom {col} sebagai FIELDNO")
            break

    # Jika tidak ditemukan, coba cari dengan cara lain
    if fieldno_col is None:
        for col in df.columns:
            if 'FIELDNO' in col.upper() and fieldno_col is None:
                fieldno_col = col
                print(f"Menggunakan kolom {col} sebagai FIELDNO")
                break

    # Jika kedua kolom ditemukan, buat mapping
    if id_col is not None and fieldno_col is not None:
        for _, row in df.iterrows():
            field_id = str(row[id_col]).strip() if row[id_col] else ''
            field_no = str(row[fieldno_col]).strip() if row[fieldno_col] else ''

            # Hanya tambahkan jika kedua nilai tidak kosong
            if field_id and field_no:
                field_mapping[field_id] = field_no

        print(f"Berhasil membuat mapping untuk {len(field_mapping)} field dari database.")
    else:
        print("Tidak dapat menemukan kolom ID atau FIELDNO dalam hasil query.")

        # Jika ada kolom 'ID FIELDNO' yang berisi data dalam format "ID FIELDNO"
        if 'ID FIELDNO' in df.columns:
            for _, row in df.iterrows():
                value = row['ID FIELDNO']
                if value and isinstance(value, str):
                    parts = value.strip().split()
                    if len(parts) >= 2:
                        field_id = parts[0].strip()
                        field_no = ' '.join(parts[1:]).strip()
                        if field_id.isdigit() and field_no:
                            field_mapping[field_id] = field_no

    # Tambahkan beberapa mapping default untuk field yang sering digunakan (sebagai fallback)
    default_mapping = {
        '155': 'PM0807F1',
        '156': 'PM0808F1',
        '157': 'PM0809F1',
        '158': 'PM0810F1',
        '159': 'PM0811F1'
    }

    # Update mapping dengan default jika belum ada
    for field_id, field_no in default_mapping.items():
        if field_id not in field_mapping:
            field_mapping[field_id] = field_no

    print(f"Berhasil mendapatkan mapping total untuk {len(field_mapping)} field.")
    return field_mapping

def get_duplicate_transno_data(connector, start_date, end_date, limit=None):
    """
    Mendapatkan data dengan TRANSNO yang sama.

    Args:
        connector: FirebirdConnector instance
        start_date: Tanggal awal (format: YYYY-MM-DD)
        end_date: Tanggal akhir (format: YYYY-MM-DD)
        limit: Batasan jumlah data yang diambil (opsional)

    Returns:
        pandas.DataFrame: Data dengan TRANSNO yang sama
    """
    # Langkah 1: Dapatkan daftar TRANSNO yang memiliki lebih dari satu record dengan pendekatan yang lebih efisien
    print("Langkah 1: Mencari TRANSNO yang duplikat...")

    # Determine the correct table name based on the month
    month_num = int(start_date.split('-')[1])
    ffb_table = f"FFBSCANNERDATA{month_num:02d}"
    print(f"Using table {ffb_table} for month {month_num}")

    # Simplified query that finds TRANSNOs with multiple records on the same date
    transno_query = f"""
    SELECT a.TRANSNO, COUNT(*) AS JUMLAH
    FROM {ffb_table} a
    WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE < '{end_date}'
    GROUP BY a.TRANSNO
    HAVING COUNT(*) > 1
    """

    transno_result = connector.execute_query(transno_query)
    transno_df = connector.to_pandas(transno_result)

    if transno_df.empty:
        print("Tidak ditemukan TRANSNO duplikat.")
        return pd.DataFrame()

    # Dapatkan daftar TRANSNO yang duplikat
    duplicate_transnos = transno_df['TRANSNO'].tolist()
    print(f"Ditemukan {len(duplicate_transnos)} TRANSNO duplikat.")

    # Jika ada batasan, batasi jumlahnya untuk query yang lebih cepat
    if limit and len(duplicate_transnos) > limit:
        print(f"Membatasi analisis untuk {limit} TRANSNO pertama dari {len(duplicate_transnos)} total.")
        duplicate_transnos = duplicate_transnos[:limit]
    else:
        print(f"Menganalisis semua {len(duplicate_transnos)} TRANSNO yang ditemukan.")

    # Langkah 2: Dapatkan data lengkap untuk TRANSNO yang duplikat
    print("Langkah 2: Mengambil data lengkap untuk TRANSNO duplikat...")

    # Firebird 1.5 has a limit of 1500 values in an IN clause
    # Split the query into smaller batches
    BATCH_SIZE = 1000  # Safely under the 1500 limit
    all_results = []

    # Process in batches
    for i in range(0, len(duplicate_transnos), BATCH_SIZE):
        batch = duplicate_transnos[i:i+BATCH_SIZE]
        transno_list = ", ".join([f"'{tn}'" for tn in batch])

        query = f"""
        SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
               a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
               a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
               a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
               a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
        FROM {ffb_table} a
        WHERE a.TRANSNO IN ({transno_list})
        AND a.TRANSDATE >= '{start_date}' AND a.TRANSDATE < '{end_date}'
        ORDER BY a.TRANSNO, a.TRANSDATE
        """

        print(f"Executing query batch {i//BATCH_SIZE + 1} with {len(batch)} TRANSNO values...")
        batch_result = connector.execute_query(query)
        all_results.extend(batch_result)

    print(f"Total records retrieved: {len(all_results)}")

    # Convert to pandas DataFrame
    df = connector.to_pandas(all_results)

    return df

def analyze_differences(df, field_mapping=None, employee_mapping=None, transstatus_mapping=None):
    """
    Menganalisis perbedaan antara data dengan TRANSNO yang sama.

    Args:
        df: pandas.DataFrame dengan data TRANSNO duplikat

    Returns:
        tuple: (DataFrame dengan analisis, dictionary statistik)
    """
    if df.empty:
        print("No data to analyze.")
        return pd.DataFrame(), {}

    # Periksa dan perbaiki nama kolom
    print("Kolom yang tersedia dalam data:")
    for col in df.columns:
        print(f"  - {col}")

    # Cari kolom TRANSNO
    transno_col = None
    # Coba cari dengan nama yang tepat terlebih dahulu
    if 'TRANSNO' in df.columns:
        transno_col = 'TRANSNO'
        print(f"Menggunakan kolom TRANSNO sebagai TRANSNO")
    elif 'TRANSDA' in df.columns:
        # Berdasarkan output isql yang kita lihat, TRANSNO ada di kolom TRANSDA
        transno_col = 'TRANSDA'
        print(f"Menggunakan kolom TRANSDA sebagai TRANSNO (manual mapping)")
    else:
        # Jika tidak ditemukan, cari dengan cara biasa
        for col in df.columns:
            if 'TRANSNO' in col.upper():
                transno_col = col
                print(f"Menggunakan kolom {col} sebagai TRANSNO")
                break

    if not transno_col:
        print("Tidak dapat menemukan kolom TRANSNO. Analisis tidak dapat dilanjutkan.")
        return pd.DataFrame(), {}

    # Cari kolom tanggal dan waktu
    transdate_col = None
    transtime_col = None

    # Mapping manual berdasarkan output isql
    if 'E     TRANS' in df.columns:
        transdate_col = 'E     TRANS'
        print(f"Menggunakan kolom 'E     TRANS' sebagai TRANSDATE (manual mapping)")
    elif 'TRANSDATE' in df.columns:
        transdate_col = 'TRANSDATE'
        print(f"Menggunakan kolom TRANSDATE sebagai TRANSDATE")
    else:
        # Jika tidak ditemukan, cari dengan cara biasa
        for col in df.columns:
            if 'DATE' in col.upper() and not transdate_col:
                transdate_col = col
                print(f"Menggunakan kolom {col} sebagai TRANSDATE")
                break

    # Cari kolom waktu
    if 'IME' in df.columns:
        transtime_col = 'IME'
        print(f"Menggunakan kolom 'IME' sebagai TRANSTIME (manual mapping)")
    elif 'TRANSTIME' in df.columns:
        transtime_col = 'TRANSTIME'
        print(f"Menggunakan kolom TRANSTIME sebagai TRANSTIME")
    else:
        # Jika tidak ditemukan, cari dengan cara biasa
        for col in df.columns:
            if 'TIME' in col.upper() and 'DATE' not in col.upper() and not transtime_col:
                transtime_col = col
                print(f"Menggunakan kolom {col} sebagai TRANSTIME")
                break

    # Cari kolom yang akan dibandingkan
    comparison_mapping = {
        'RIPEBCH': None,
        'UNRIPEBCH': None,
        'BLACKBCH': None,
        'ROTTENBCH': None,
        'LONGSTALKBCH': None,
        'RATDMGBCH': None,
        'LOOSEFRUIT': None
    }

    # Mapping manual berdasarkan output isql yang kita lihat
    manual_mapping = {
        'RIPEBCH': 'RIPE',
        'UNRIPEBCH': 'CH    UNRIPE',
        'BLACKBCH': 'CH     BLACK',
        'ROTTENBCH': 'CH    ROTTEN',
        'LONGSTALKBCH': 'CH LONGSTALK',
        'RATDMGBCH': 'CH    RATDMG',
        'LOOSEFRUIT': 'CH   LOOSEFR'
    }

    # Coba gunakan mapping manual terlebih dahulu
    for target_col, mapped_col in manual_mapping.items():
        if mapped_col in df.columns:
            comparison_mapping[target_col] = mapped_col
            print(f"Menggunakan kolom {mapped_col} sebagai {target_col} (manual mapping)")

    # Jika masih ada yang belum ter-mapping, coba dengan cara otomatis
    for target_col in comparison_mapping.keys():
        if comparison_mapping[target_col] is None:
            for col in df.columns:
                if target_col.upper() in col.upper():
                    comparison_mapping[target_col] = col
                    print(f"Menggunakan kolom {col} sebagai {target_col} (auto mapping)")
                    break

    # Kolom yang akan dibandingkan (yang ditemukan)
    comparison_columns = [col for col, mapped in comparison_mapping.items() if mapped]

    # Pastikan kolom numerik
    for col in comparison_columns:
        mapped_col = comparison_mapping[col]
        if mapped_col in df.columns:
            df[mapped_col] = pd.to_numeric(df[mapped_col], errors='coerce').fillna(0)

    # Cari kolom SCANUSERID
    scanuserid_col = None
    if 'ID   SCANUSE' in df.columns:
        scanuserid_col = 'ID   SCANUSE'
        print(f"Menggunakan kolom 'ID   SCANUSE' sebagai SCANUSERID (manual mapping)")
    elif 'SCANUSERID' in df.columns:
        scanuserid_col = 'SCANUSERID'
        print(f"Menggunakan kolom SCANUSERID sebagai SCANUSERID")
    else:
        for col in df.columns:
            if 'SCANUSER' in col.upper() or 'USER' in col.upper():
                scanuserid_col = col
                print(f"Menggunakan kolom {col} sebagai SCANUSERID")
                break

    # Cari kolom FIELDID
    fieldid_col = None
    if 'ID      FIEL' in df.columns:
        fieldid_col = 'ID      FIEL'
        print(f"Menggunakan kolom 'ID      FIEL' sebagai FIELDID (manual mapping)")
    elif 'FIELDID' in df.columns:
        fieldid_col = 'FIELDID'
        print(f"Menggunakan kolom FIELDID sebagai FIELDID")
    else:
        for col in df.columns:
            if 'FIELD' in col.upper():
                fieldid_col = col
                print(f"Menggunakan kolom {col} sebagai FIELDID")
                break

    # Cari kolom TRANSSTATUS
    transstatus_col = None
    if 'TRANSSTATUS' in df.columns:
        transstatus_col = 'TRANSSTATUS'
        print(f"Menggunakan kolom TRANSSTATUS sebagai TRANSSTATUS")
    else:
        for col in df.columns:
            if 'STATUS' in col.upper():
                transstatus_col = col
                print(f"Menggunakan kolom {col} sebagai TRANSSTATUS")
                break

    # Group by TRANSNO and TRANSDATE to ensure we only compare records from the same date
    if transdate_col:
        print(f"Grouping by both {transno_col} and {transdate_col} to ensure proper matching")
        grouped = df.groupby([transno_col, transdate_col])
    else:
        print(f"Warning: No TRANSDATE column found, grouping only by {transno_col}")
        grouped = df.groupby(transno_col)

    # Initialize list untuk menyimpan hasil
    results = []

    # Proses setiap grup
    for group_key, group in grouped:
        # Extract transno (and transdate if available)
        if isinstance(group_key, tuple):
            transno = group_key[0]
            transdate = group_key[1] if len(group_key) > 1 else None
        else:
            transno = group_key
            transdate = None
        # Skip jika hanya ada satu record
        if len(group) <= 1:
            continue

        # Cari kolom RECORDTAG
        recordtag_col = None
        if 'RECORDTAG' in group.columns:
            recordtag_col = 'RECORDTAG'
            print(f"Menggunakan kolom RECORDTAG sebagai RECORDTAG")
        else:
            for col in group.columns:
                if 'RECORDTAG' in col.upper() or 'TAG' in col.upper():
                    recordtag_col = col
                    print(f"Menggunakan kolom {col} sebagai RECORDTAG")
                    break

        # Jika tidak ada kolom RECORDTAG, gunakan sort by date/time
        if not recordtag_col:
            # Sort by TRANSDATE and TRANSTIME untuk memastikan urutan konsisten
            sort_cols = []
            if transdate_col:
                sort_cols.append(transdate_col)
            if transtime_col:
                sort_cols.append(transtime_col)

            # Jika tidak ada kolom untuk sort, gunakan indeks
            if sort_cols:
                group = group.sort_values(sort_cols)
            else:
                # Jika tidak ada kolom untuk sort, gunakan indeks saja
                group = group.copy()

            # Ambil dua record pertama (diasumsikan Kerani dan Asisten)
            record1 = group.iloc[0]
            record2 = group.iloc[1]
        else:
            # Pisahkan berdasarkan RECORDTAG
            pm_records = group[group[recordtag_col] == 'PM']
            p1_records = group[group[recordtag_col] == 'P1']
            p5_records = group[group[recordtag_col] == 'P5']

            # Jika tidak ada record PM, gunakan cara default
            if pm_records.empty:
                print(f"Tidak ditemukan record PM untuk TRANSNO {group[transno_col].iloc[0]}")
                # Ambil dua record pertama saja
                record1 = group.iloc[0]
                record2 = group.iloc[1]
            # Jika tidak ada record P1 atau P5, gunakan cara default
            elif p1_records.empty and p5_records.empty:
                print(f"Tidak ditemukan record P1 atau P5 untuk TRANSNO {group[transno_col].iloc[0]}")
                # Ambil dua record pertama saja
                record1 = group.iloc[0]
                record2 = group.iloc[1]
            else:
                # Ambil record PM sebagai record1 (Kerani)
                record1 = pm_records.iloc[0]

                # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor)
                if not p1_records.empty:
                    record2 = p1_records.iloc[0]
                else:
                    record2 = p5_records.iloc[0]

        # Buat dictionary hasil dasar
        result = {
            'TRANSNO': transno
        }

        # Tambahkan kolom tanggal jika tersedia dari grouping
        if transdate:
            result['TRANSDATE'] = transdate
        # Atau dari record jika tidak tersedia dari grouping
        elif transdate_col:
            result['TRANSDATE'] = record1[transdate_col]

        # Tambahkan kolom field jika tersedia
        if fieldid_col:
            field_id = str(record1[fieldid_col]).strip() if record1[fieldid_col] else ''

            # Tambahkan FieldNo jika mapping tersedia
            if field_mapping and field_id in field_mapping:
                result['FIELDNO'] = field_mapping[field_id]
            else:
                # Jika tidak ada mapping, gunakan field_id sebagai fallback
                result['FIELDNO'] = f"FIELD-{field_id}"

        # Tambahkan kolom RECORDTAG jika tersedia
        if recordtag_col:
            recordtag_1 = str(record1[recordtag_col]).strip() if record1[recordtag_col] else ''
            recordtag_2 = str(record2[recordtag_col]).strip() if record2[recordtag_col] else ''
            result['RECORDTAG_1'] = recordtag_1
            result['RECORDTAG_2'] = recordtag_2

        # Tambahkan kolom TRANSSTATUS jika tersedia
        if transstatus_col:
            status_id_1 = str(record1[transstatus_col]).strip() if record1[transstatus_col] else ''
            status_id_2 = str(record2[transstatus_col]).strip() if record2[transstatus_col] else ''

            # Tambahkan status ID
            result['TRANSSTATUS_1'] = status_id_1
            result['TRANSSTATUS_2'] = status_id_2

            # Tambahkan status name jika mapping tersedia
            if transstatus_mapping:
                if 'get_status_name' in transstatus_mapping:
                    result['TRANSSTATUS_NAME_1'] = transstatus_mapping['get_status_name'](status_id_1)
                    result['TRANSSTATUS_NAME_2'] = transstatus_mapping['get_status_name'](status_id_2)
                else:
                    result['TRANSSTATUS_NAME_1'] = transstatus_mapping.get(status_id_1, f"STATUS-{status_id_1}")
                    result['TRANSSTATUS_NAME_2'] = transstatus_mapping.get(status_id_2, f"STATUS-{status_id_2}")

        # Tambahkan kolom user jika tersedia
        if scanuserid_col:
            user_id_1 = str(record1[scanuserid_col]).strip() if record1[scanuserid_col] else ''
            user_id_2 = str(record2[scanuserid_col]).strip() if record2[scanuserid_col] else ''

            # Tambahkan nama karyawan langsung (tidak perlu menampilkan ID)
            if employee_mapping:
                # Gunakan fungsi get_name jika tersedia, atau fallback ke dictionary lookup
                if 'get_name' in employee_mapping:
                    result['NAME_1'] = employee_mapping['get_name'](user_id_1)
                    result['NAME_2'] = employee_mapping['get_name'](user_id_2)
                else:
                    result['NAME_1'] = employee_mapping.get(user_id_1, f"KARYAWAN-{user_id_1}")
                    result['NAME_2'] = employee_mapping.get(user_id_2, f"KARYAWAN-{user_id_2}")

        # Hitung perbedaan untuk setiap kolom perbandingan
        for col in comparison_columns:
            mapped_col = comparison_mapping[col]
            if mapped_col in record1 and mapped_col in record2:
                value1 = float(record1[mapped_col]) if record1[mapped_col] else 0
                value2 = float(record2[mapped_col]) if record2[mapped_col] else 0

                result[f'{col}_1'] = value1
                result[f'{col}_2'] = value2
                result[f'{col}_DIFF'] = value2 - value1

        # Tambahkan total perbedaan
        total1 = sum(float(record1[comparison_mapping[col]]) if record1[comparison_mapping[col]] else 0
                    for col in comparison_columns if comparison_mapping[col] in record1)
        total2 = sum(float(record2[comparison_mapping[col]]) if record2[comparison_mapping[col]] else 0
                    for col in comparison_columns if comparison_mapping[col] in record2)

        result['TOTAL_1'] = total1
        result['TOTAL_2'] = total2
        result['TOTAL_DIFF'] = total2 - total1

        results.append(result)

    # Convert results to DataFrame
    if not results:
        return pd.DataFrame(), {}

    df_results = pd.DataFrame(results)

    # Sort by absolute total difference
    df_results['ABS_TOTAL_DIFF'] = df_results['TOTAL_DIFF'].abs()
    df_results = df_results.sort_values('ABS_TOTAL_DIFF', ascending=False)
    df_results = df_results.drop('ABS_TOTAL_DIFF', axis=1)

    # Generate summary statistics
    summary = {
        'total_transactions': len(df_results),
        'transactions_with_differences': len(df_results[df_results['TOTAL_DIFF'] != 0]),
        'avg_total_diff': df_results['TOTAL_DIFF'].mean(),
        'max_total_diff': df_results['TOTAL_DIFF'].max(),
        'min_total_diff': df_results['TOTAL_DIFF'].min(),
    }

    # Add statistics for each comparison column
    for col in comparison_columns:
        diff_col = f'{col}_DIFF'
        if diff_col in df_results.columns:
            summary[f'avg_{col.lower()}_diff'] = df_results[diff_col].mean()
            summary[f'max_{col.lower()}_diff'] = df_results[diff_col].max()
            summary[f'min_{col.lower()}_diff'] = df_results[diff_col].min()
            summary[f'transactions_with_{col.lower()}_diff'] = len(df_results[df_results[diff_col] != 0])

    # Jika tidak ada transaksi, kembalikan DataFrame kosong
    if df_results.empty:
        print("Tidak ditemukan transaksi untuk dianalisis.")
        return df_results, summary

    # Kembalikan semua transaksi, tidak hanya yang memiliki perbedaan
    print(f"Ditemukan {len(df_results)} transaksi untuk dianalisis, {summary['transactions_with_differences']} di antaranya memiliki perbedaan.")
    return df_results, summary

def generate_preview(analyzed_data, summary_stats):
    """
    Menghasilkan preview dari hasil analisis.

    Args:
        analyzed_data: pandas.DataFrame dengan hasil analisis
        summary_stats: Dictionary dengan statistik ringkasan

    Returns:
        str: Teks preview
    """
    if analyzed_data.empty:
        return "Tidak ada data untuk dianalisis."

    # Buat string preview
    preview = "=== Preview Analisis ===\n\n"

    # Tambahkan statistik ringkasan
    preview += "Statistik Ringkasan:\n"
    preview += f"Total Transaksi: {summary_stats['total_transactions']}\n"
    preview += f"Transaksi dengan Perbedaan: {summary_stats['transactions_with_differences']}\n"
    preview += f"Transaksi tanpa Perbedaan: {summary_stats['total_transactions'] - summary_stats['transactions_with_differences']}\n"
    preview += f"Rata-rata Perbedaan Total: {summary_stats['avg_total_diff']:.2f}\n"
    preview += f"Perbedaan Total Maksimum: {summary_stats['max_total_diff']}\n"
    preview += f"Perbedaan Total Minimum: {summary_stats['min_total_diff']}\n\n"

    # Tambahkan preview data (5 baris pertama)
    preview += "Preview Data (5 baris teratas):\n"

    # Jika ada perbedaan, tampilkan 5 baris dengan perbedaan terbesar terlebih dahulu
    # Hanya tampilkan kolom diff saja, tanpa nilai bunch dari masing-masing record
    if summary_stats['transactions_with_differences'] > 0:
        diff_data = analyzed_data[analyzed_data['TOTAL_DIFF'] != 0].copy()
        if not diff_data.empty:
            # Pilih kolom yang akan ditampilkan (hanya kolom dasar dan kolom diff)
            diff_cols = [col for col in diff_data.columns if col.endswith('_DIFF') or
                         col in ['TRANSNO', 'TRANSDATE', 'FIELDNO', 'RECORDTAG_1', 'RECORDTAG_2', 'NAME_1', 'NAME_2', 'TOTAL_DIFF']]
            diff_data_simplified = diff_data[diff_cols]
            preview += "Data dengan perbedaan (5 baris teratas, hanya kolom diff):\n"
            preview += diff_data_simplified.head(5).to_string() + "\n\n"

    # Tampilkan 5 baris pertama dari semua data
    preview += "Semua data (5 baris teratas):\n"
    preview += analyzed_data.head(5).to_string() + "\n\n"

    # Tambahkan statistik spesifik kolom
    preview += "Statistik per Kolom:\n"
    for col in ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']:
        diff_col = f'{col}_DIFF'
        if diff_col in analyzed_data.columns:
            preview += f"{col}:\n"
            preview += f"  Rata-rata Perbedaan: {summary_stats.get(f'avg_{col.lower()}_diff', 0):.2f}\n"
            preview += f"  Transaksi dengan Perbedaan: {summary_stats.get(f'transactions_with_{col.lower()}_diff', 0)}\n"

    return preview

def save_excel_report(analyzed_data, summary_stats, output_dir, filename=None):
    """
    Menyimpan hasil analisis ke file Excel.

    Args:
        analyzed_data: pandas.DataFrame dengan hasil analisis
        summary_stats: Dictionary dengan statistik ringkasan
        output_dir: Direktori output
        filename: Nama file output (opsional)

    Returns:
        str: Path ke file yang disimpan
    """
    if analyzed_data.empty:
        return "Tidak ada data untuk disimpan."

    # Generate filename jika tidak disediakan
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analisis_perbedaan_panen_{timestamp}.xlsx"

    # Pastikan filename memiliki ekstensi .xlsx
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'

    # Path lengkap ke file output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, filename)

    # Buat writer object
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Tulis semua data analisis
        analyzed_data.to_excel(writer, sheet_name='Semua Data', index=False)

        # Jika ada perbedaan, buat sheet terpisah untuk data dengan perbedaan
        # Hanya tampilkan kolom diff saja, tanpa nilai bunch dari masing-masing record
        if summary_stats['transactions_with_differences'] > 0:
            diff_data = analyzed_data[analyzed_data['TOTAL_DIFF'] != 0].copy()
            if not diff_data.empty:
                # Pilih kolom yang akan ditampilkan (hanya kolom dasar dan kolom diff)
                diff_cols = [col for col in diff_data.columns if col.endswith('_DIFF') or
                             col in ['TRANSNO', 'TRANSDATE', 'FIELDNO', 'RECORDTAG_1', 'RECORDTAG_2', 'NAME_1', 'NAME_2', 'TOTAL_DIFF']]
                diff_data_simplified = diff_data[diff_cols]
                diff_data_simplified.to_excel(writer, sheet_name='Data Dengan Perbedaan', index=False)

        # Buat sheet terpisah untuk data tanpa perbedaan (selisih 0)
        no_diff_data = analyzed_data[analyzed_data['TOTAL_DIFF'] == 0].copy()
        if not no_diff_data.empty:
            print(f"Ditemukan {len(no_diff_data)} transaksi tanpa perbedaan (selisih 0).")
            no_diff_data.to_excel(writer, sheet_name='Data Tanpa Perbedaan', index=False)

        # Buat sheet ringkasan
        summary_df = pd.DataFrame({
            'Metrik': list(summary_stats.keys()),
            'Nilai': list(summary_stats.values())
        })
        summary_df.to_excel(writer, sheet_name='Ringkasan', index=False)

    return output_path

def generate_charts(analyzed_data, summary_stats, output_dir, filename=None):
    """
    Menghasilkan grafik dari data yang dianalisis dan menyimpannya ke file.

    Args:
        analyzed_data: pandas.DataFrame dengan hasil analisis
        summary_stats: Dictionary dengan statistik ringkasan
        output_dir: Direktori output
        filename: Nama file output (opsional)

    Returns:
        str: Path ke file yang disimpan
    """
    if analyzed_data.empty:
        return "Tidak ada data untuk dibuat grafiknya."

    # Generate filename jika tidak disediakan
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grafik_perbedaan_panen_{timestamp}.png"

    # Pastikan filename memiliki ekstensi .png
    if not filename.endswith('.png'):
        filename += '.png'

    # Path lengkap ke file output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, filename)

    # Buat figure dengan multiple subplots
    _, axs = plt.subplots(2, 2, figsize=(15, 10))

    # Plot 1: Distribusi perbedaan total
    if 'TOTAL_DIFF' in analyzed_data.columns:
        axs[0, 0].hist(analyzed_data['TOTAL_DIFF'], bins=20)
        axs[0, 0].set_title('Distribusi Perbedaan Total')
        axs[0, 0].set_xlabel('Perbedaan')
        axs[0, 0].set_ylabel('Frekuensi')
    else:
        axs[0, 0].text(0.5, 0.5, 'Data tidak tersedia', ha='center', va='center')
        axs[0, 0].set_title('Distribusi Perbedaan Total')

    # Plot 2: Rata-rata perbedaan per kolom
    cols = [col for col in ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
            if f'{col}_DIFF' in analyzed_data.columns]

    if cols:
        avg_diffs = [summary_stats.get(f'avg_{col.lower()}_diff', 0) for col in cols]
        axs[0, 1].bar(cols, avg_diffs)
        axs[0, 1].set_title('Rata-rata Perbedaan per Kolom')
        axs[0, 1].set_xlabel('Kolom')
        axs[0, 1].set_ylabel('Rata-rata Perbedaan')
        plt.setp(axs[0, 1].get_xticklabels(), rotation=45, ha='right')
    else:
        axs[0, 1].text(0.5, 0.5, 'Data tidak tersedia', ha='center', va='center')
        axs[0, 1].set_title('Rata-rata Perbedaan per Kolom')

    # Plot 3: Transaksi dengan perbedaan per kolom
    if cols:
        txn_with_diffs = [summary_stats.get(f'transactions_with_{col.lower()}_diff', 0) for col in cols]
        axs[1, 0].bar(cols, txn_with_diffs)
        axs[1, 0].set_title('Transaksi dengan Perbedaan per Kolom')
        axs[1, 0].set_xlabel('Kolom')
        axs[1, 0].set_ylabel('Jumlah Transaksi')
        plt.setp(axs[1, 0].get_xticklabels(), rotation=45, ha='right')
    else:
        axs[1, 0].text(0.5, 0.5, 'Data tidak tersedia', ha='center', va='center')
        axs[1, 0].set_title('Transaksi dengan Perbedaan per Kolom')

    # Plot 4: Scatter plot nilai total
    if 'TOTAL_1' in analyzed_data.columns and 'TOTAL_2' in analyzed_data.columns:
        # Pisahkan data dengan perbedaan dan tanpa perbedaan
        diff_data = analyzed_data[analyzed_data['TOTAL_DIFF'] != 0]
        no_diff_data = analyzed_data[analyzed_data['TOTAL_DIFF'] == 0]

        # Plot data tanpa perbedaan dengan warna berbeda
        if not no_diff_data.empty:
            axs[1, 1].scatter(no_diff_data['TOTAL_1'], no_diff_data['TOTAL_2'], color='blue', alpha=0.5, label='Tanpa Perbedaan')

        # Plot data dengan perbedaan dengan warna berbeda
        if not diff_data.empty:
            axs[1, 1].scatter(diff_data['TOTAL_1'], diff_data['TOTAL_2'], color='red', alpha=0.7, label='Dengan Perbedaan')

        axs[1, 1].set_title('Perbandingan Nilai Total')
        axs[1, 1].set_xlabel('Total Record Pertama')
        axs[1, 1].set_ylabel('Total Record Kedua')
        axs[1, 1].legend()

        # Tambahkan garis diagonal untuk referensi
        min_val = min(analyzed_data['TOTAL_1'].min(), analyzed_data['TOTAL_2'].min())
        max_val = max(analyzed_data['TOTAL_1'].max(), analyzed_data['TOTAL_2'].max())
        axs[1, 1].plot([min_val, max_val], [min_val, max_val], 'g--', label='Nilai Sama')
    else:
        axs[1, 1].text(0.5, 0.5, 'Data tidak tersedia', ha='center', va='center')
        axs[1, 1].set_title('Perbandingan Nilai Total')

    # Sesuaikan layout dan simpan
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path

def main():
    """
    Fungsi utama untuk menjalankan aplikasi.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Analisis perbedaan data panen antara Kerani dan Asisten.')
    parser.add_argument('--db-path', type=str,
                        default="D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\PTRJ_P1A_08042025\\PTRJ_P1A.FDB",
                        help='Path ke file database Firebird')
    parser.add_argument('--isql-path', type=str,
                        default="C:\\Program Files (x86)\\Firebird\\Firebird_1_5\\bin\\isql.exe",
                        help='Path ke executable isql')
    parser.add_argument('--username', type=str, default='sysdba', help='Username database')
    parser.add_argument('--password', type=str, default='masterkey', help='Password database')
    parser.add_argument('--month', type=int, default=datetime.now().month,
                        help='Bulan untuk analisis (1-12)')
    parser.add_argument('--year', type=int, default=datetime.now().year,
                        help='Tahun untuk analisis (YYYY)')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Tanggal mulai untuk analisis (YYYY-MM-DD), jika diisi akan mengabaikan bulan dan tahun')
    parser.add_argument('--end-date', type=str, default=None,
                        help='Tanggal akhir untuk analisis (YYYY-MM-DD), jika diisi akan mengabaikan bulan dan tahun')
    parser.add_argument('--output-dir', type=str, default='reports',
                        help='Direktori untuk menyimpan laporan')
    parser.add_argument('--use-localhost', action='store_true',
                        help='Gunakan format localhost:path untuk koneksi')
    parser.add_argument('--limit', type=int, default=None,
                        help='Batasan jumlah TRANSNO yang dianalisis (default: tidak ada batasan)')
    parser.add_argument('--excel', action='store_true',
                        help='Generate laporan Excel')
    parser.add_argument('--pdf', action='store_true',
                        help='Generate laporan PDF')

    args = parser.parse_args()

    # Buat direktori output jika belum ada
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Tentukan tanggal awal dan akhir berdasarkan bulan dan tahun jika tidak ada tanggal spesifik
    if args.start_date is None or args.end_date is None:
        # Dapatkan tanggal awal dan akhir bulan
        year = args.year
        month = args.month

        # Validasi bulan
        if month < 1 or month > 12:
            print(f"Error: Bulan harus antara 1-12, nilai yang diberikan: {month}")
            return

        # Tanggal awal adalah hari pertama bulan
        start_date = date(year, month, 1)

        # Tanggal akhir adalah hari pertama bulan berikutnya
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        # Format tanggal untuk query SQL
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        print(f"Menganalisis data untuk bulan {month}/{year} (dari {start_date_str} sampai {end_date_str})")
    else:
        # Gunakan tanggal yang diberikan langsung
        start_date_str = args.start_date
        end_date_str = args.end_date
        print(f"Menganalisis data dari {start_date_str} sampai {end_date_str}")

    # Inisialisasi koneksi database
    print(f"Menghubungkan ke database: {args.db_path}")
    connector = FirebirdConnector(
        db_path=args.db_path,
        username=args.username,
        password=args.password,
        isql_path=args.isql_path,
        use_localhost=args.use_localhost
    )

    # Tes koneksi
    print("Menguji koneksi database...")
    if not connector.test_connection():
        print("Gagal terhubung ke database. Silakan periksa parameter koneksi Anda.")
        return

    print("Koneksi berhasil!")

    # Dapatkan mapping FieldID ke FieldNo
    field_mapping = get_field_mapping(connector)

    # Dapatkan mapping ID ke NAME dari tabel EMP
    employee_mapping = get_employee_mapping(connector)

    # Dapatkan mapping TRANSSTATUS ke deskripsi dari tabel LOOKUP
    transstatus_mapping = get_transstatus_mapping(connector)

    # Dapatkan data dengan TRANSNO duplikat
    print(f"Mengambil data dengan TRANSNO duplikat antara {start_date_str} dan {end_date_str}...")
    data = get_duplicate_transno_data(connector, start_date_str, end_date_str, args.limit)

    if data.empty:
        print("Tidak ditemukan TRANSNO duplikat dalam rentang tanggal yang ditentukan.")
        return

    print(f"Ditemukan {len(data)} record dengan TRANSNO duplikat.")

    # Analisis data
    print("Menganalisis data...")
    analyzed_data, summary_stats = analyze_differences(data, field_mapping, employee_mapping, transstatus_mapping)

    if analyzed_data.empty:
        print("Tidak ditemukan transaksi untuk dianalisis.")
        return

    # Generate laporan
    print("Menghasilkan laporan...")

    # Tampilkan preview
    preview = generate_preview(analyzed_data, summary_stats)
    print("\n" + preview)

    # Timestamp untuk nama file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Simpan laporan Excel jika diminta
    if args.excel:
        excel_path = save_excel_report(
            analyzed_data,
            summary_stats,
            args.output_dir,
            f"analisis_perbedaan_panen_{timestamp}.xlsx"
        )
        print(f"Laporan Excel disimpan ke: {excel_path}")

    # Hasilkan grafik
    chart_path = generate_charts(
        analyzed_data,
        summary_stats,
        args.output_dir,
        f"grafik_perbedaan_panen_{timestamp}.png"
    )
    print(f"Grafik disimpan ke: {chart_path}")

    # Extract database name from path
    db_name = os.path.splitext(os.path.basename(args.db_path))[0]

    # Get month name
    month_name = calendar.month_name[args.month]

    # Generate laporan PDF jika diminta
    if args.pdf:
        pdf_path = generate_advanced_pdf_report(
            analyzed_data,
            summary_stats,
            args.output_dir,
            database_name=db_name,
            bulan=month_name,
            tahun=str(args.year)
        )
        if pdf_path:
            print(f"Laporan PDF disimpan ke: {pdf_path}")
        else:
            print("Gagal membuat laporan PDF.")

    print("\nAnalisis selesai!")

if __name__ == "__main__":
    main()
