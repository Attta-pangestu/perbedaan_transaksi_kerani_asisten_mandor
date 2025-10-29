#!/usr/bin/env python3
"""
FFB Analysis Engine untuk Sistem Laporan Verifikasi
Logic inti untuk analisis transaksi FFB scanner (sama dengan codebase asli)
"""

import pandas as pd
import os
import sys
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import logging

# Add parent directory to path for firebird_connector
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from firebird_connector import FirebirdConnector

class FFBAnalysisEngine:
    """Engine untuk analisis data FFB scanner"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_estate(self, estate_name: str, db_path: str, start_date: date, end_date: date,
                      use_status_704_filter: bool = False) -> Optional[List[Dict]]:
        """Analyze single estate (sama dengan logic asli gui_multi_estate_ffb_analysis.py)"""
        try:
            # Handle path that is a folder (like PGE 2A)
            if os.path.isdir(db_path):
                for file in os.listdir(db_path):
                    if file.upper().endswith('.FDB'):
                        db_path = os.path.join(db_path, file)
                        break
                else:
                    self.logger.warning(f"No .FDB file found in {db_path}")
                    return None

            if not os.path.exists(db_path):
                self.logger.warning(f"Database not found: {db_path}")
                return None

            connector = FirebirdConnector(db_path)
            if not connector.test_connection():
                return None

            employee_mapping = self.get_employee_mapping(connector)
            divisions, month_tables = self.get_divisions(connector, start_date, end_date)

            month_num = start_date.month
            # Aktif jika rentang menyentuh bulan Mei
            use_status_704_filter = use_status_704_filter and (start_date.month == 5 or end_date.month == 5)

            if use_status_704_filter:
                self.logger.info(f"*** FILTER TRANSSTATUS 704 AKTIF untuk {estate_name} bulan {month_num} ***")
                self.logger.info(f"Menggunakan analisis transaksi real (bukan nilai statis)")

            # Akumulasi per karyawan dari semua divisi
            estate_employee_totals = {}

            estate_results = []
            for div_id, div_name in divisions.items():
                result = self.analyze_division(
                    connector, estate_name, div_id, div_name,
                    start_date, end_date, employee_mapping, use_status_704_filter, month_tables
                )
                if result:
                    # Akumulasi per karyawan
                    for emp_id, emp_data in result['employee_details'].items():
                        if emp_id not in estate_employee_totals:
                            estate_employee_totals[emp_id] = {
                                'name': emp_data['name'],
                                'kerani': 0,
                                'kerani_verified': 0,
                                'kerani_differences': 0,
                                'mandor': 0,
                                'asisten': 0
                            }

                        estate_employee_totals[emp_id]['kerani'] += emp_data['kerani']
                        estate_employee_totals[emp_id]['kerani_verified'] += emp_data['kerani_verified']
                        estate_employee_totals[emp_id]['kerani_differences'] += emp_data['kerani_differences']
                        estate_employee_totals[emp_id]['mandor'] += emp_data['mandor']
                        estate_employee_totals[emp_id]['asisten'] += emp_data['asisten']

                    estate_results.append(result)

            # Log untuk filter status 704
            if use_status_704_filter:
                total_actual_differences = sum(emp_data['kerani_differences'] for emp_data in estate_employee_totals.values())
                self.logger.info(f"HASIL ANALISIS REAL: {total_actual_differences} total perbedaan ditemukan")

                # Log detail per karyawan
                for emp_id, emp_data in estate_employee_totals.items():
                    if emp_data['kerani_differences'] > 0:
                        user_name = emp_data['name']
                        differences = emp_data['kerani_differences']
                        verified = emp_data['kerani_verified']
                        percentage = (differences / verified * 100) if verified > 0 else 0
                        self.logger.info(f"    {user_name}: {differences} perbedaan dari {verified} transaksi terverifikasi ({percentage:.1f}%)")

            return estate_results

        except Exception as e:
            self.logger.error(f"Error analyzing estate {estate_name}: {e}")
            return None

    def get_employee_mapping(self, connector: FirebirdConnector) -> Dict[str, str]:
        """Get employee ID to name mapping"""
        query = "SELECT ID, NAME FROM EMP"
        try:
            result = connector.execute_query(query)
            df = connector.to_pandas(result)
            mapping = {}
            if not df.empty:
                for _, row in df.iterrows():
                    emp_id = str(row.iloc[0]).strip()
                    emp_name = str(row.iloc[1]).strip()
                    mapping[emp_id] = emp_name
            return mapping
        except Exception as e:
            self.logger.error(f"Error getting employee mapping: {e}")
            return {}

    def get_divisions(self, connector: FirebirdConnector, start_date: date, end_date: date) -> Tuple[Dict[str, str], List[str]]:
        """Get divisions and monthly tables for date range"""
        # Generate all month tables within the date range
        month_tables = []
        current_date = start_date
        while current_date <= end_date:
            month_tables.append(f"FFBSCANNERDATA{current_date.month:02d}")
            # Move to the next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)

        month_tables = list(set(month_tables))  # Remove duplicates
        self.logger.info(f"Tabel yang akan di-query: {', '.join(month_tables)}")

        all_divisions = {}
        for ffb_table in month_tables:
            query = f"""
            SELECT DISTINCT b.DIVID, c.DIVNAME
            FROM {ffb_table} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE b.DIVID IS NOT NULL AND c.DIVNAME IS NOT NULL
            """

            try:
                result = connector.execute_query(query)
                df = connector.to_pandas(result)
                if not df.empty:
                    for _, row in df.iterrows():
                        div_id = str(row.iloc[0]).strip()
                        div_name = str(row.iloc[1]).strip()
                        if div_id not in all_divisions:
                            all_divisions[div_id] = div_name
            except Exception as e:
                self.logger.warning(f"Peringatan saat mengambil divisi dari {ffb_table}: {e}")
                continue

        return all_divisions, month_tables

    def analyze_division(self, connector: FirebirdConnector, estate_name: str, div_id: str, div_name: str,
                        start_date: date, end_date: date, employee_mapping: Dict[str, str],
                        use_status_704_filter: bool, month_tables: List[str]) -> Optional[Dict]:
        """Analyze single division (sama dengan logic asli)"""
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        all_data_df = pd.DataFrame()

        for ffb_table in month_tables:
            # Query untuk mendapatkan data granular untuk analisis duplikat
            query = f"""
            SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
                   a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
                   a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
                   a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
                   a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
            FROM {ffb_table} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE b.DIVID = '{div_id}'
                AND a.TRANSDATE >= '{start_str}'
                AND a.TRANSDATE <= '{end_str}'
            """
            try:
                result = connector.execute_query(query)
                df_monthly = connector.to_pandas(result)
                if not df_monthly.empty:
                    all_data_df = pd.concat([all_data_df, df_monthly], ignore_index=True)
            except Exception as e:
                self.logger.warning(f"Peringatan saat mengambil data dari {ffb_table}: {e}")
                continue

        df = all_data_df
        if df.empty:
            return None

        # Hapus duplikat jika ada data yang tumpang tindih
        df.drop_duplicates(subset=['ID'], inplace=True)

        # Logika dari analisis_perbedaan_panen.py: cari duplikat berdasarkan TRANSNO
        duplicated_rows = df[df.duplicated(subset=['TRANSNO'], keep=False)]
        verified_transnos = set(duplicated_rows['TRANSNO'].tolist())

        employee_details = {}

        # Inisialisasi struktur detail karyawan
        all_user_ids = df['SCANUSERID'].unique()
        for user_id in all_user_ids:
            user_id_str = str(user_id).strip()
            employee_details[user_id_str] = {
                'name': employee_mapping.get(user_id_str, f"EMP-{user_id_str}"),
                'kerani': 0,
                'kerani_verified': 0,
                'kerani_differences': 0,
                'mandor': 0,
                'asisten': 0
            }

        # Hitung data Kerani berdasarkan duplikat dan perbedaan input
        kerani_df = df[df['RECORDTAG'] == 'PM']
        if not kerani_df.empty:
            for user_id, group in kerani_df.groupby('SCANUSERID'):
                user_id_str = str(user_id).strip()
                total_created = len(group)

                # Hitung jumlah perbedaan input untuk transaksi yang terverifikasi
                differences_count = 0
                for _, kerani_row in group.iterrows():
                    if kerani_row['TRANSNO'] in verified_transnos:
                        # Cari transaksi dengan TRANSNO yang sama tapi RECORDTAG berbeda
                        matching_transactions = df[(df['TRANSNO'] == kerani_row['TRANSNO']) &
                                                  (df['RECORDTAG'] != 'PM')]

                        # FILTER KHUSUS: Untuk bulan Mei, hanya hitung perbedaan jika
                        # Mandor/Asisten memiliki TRANSSTATUS = 704
                        if use_status_704_filter:
                            matching_transactions = matching_transactions[matching_transactions['TRANSSTATUS'] == '704']

                        if not matching_transactions.empty:
                            # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor)
                            p1_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P1']
                            p5_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P5']

                            if not p1_records.empty:
                                other_row = p1_records.iloc[0]
                            elif not p5_records.empty:
                                other_row = p5_records.iloc[0]
                            else:
                                continue

                            # Hitung perbedaan untuk setiap field
                            fields_to_compare = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH',
                                               'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']

                            # Count as 1 transaction difference if ANY field differs
                            has_difference = False
                            for field in fields_to_compare:
                                try:
                                    kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
                                    other_val = float(other_row[field]) if other_row[field] else 0
                                    if kerani_val != other_val:
                                        has_difference = True
                                        break
                                except (ValueError, TypeError):
                                    continue

                            # Count as 1 transaction difference if any field differs
                            if has_difference:
                                differences_count += 1

                # Hitung persentase terverifikasi
                verified_count = len(group[group['TRANSNO'].isin(verified_transnos)])

                if user_id_str in employee_details:
                    employee_details[user_id_str]['kerani'] = total_created
                    employee_details[user_id_str]['kerani_verified'] = verified_count
                    employee_details[user_id_str]['kerani_differences'] = differences_count

        # Hitung data Mandor
        mandor_df = df[df['RECORDTAG'] == 'P1']
        if not mandor_df.empty:
            mandor_counts = mandor_df.groupby('SCANUSERID').size()
            for user_id, count in mandor_counts.items():
                user_id_str = str(user_id).strip()
                if user_id_str in employee_details:
                    employee_details[user_id_str]['mandor'] = count

        # Hitung data Asisten
        asisten_df = df[df['RECORDTAG'] == 'P5']
        if not asisten_df.empty:
            asisten_counts = asisten_df.groupby('SCANUSERID').size()
            for user_id, count in asisten_counts.items():
                user_id_str = str(user_id).strip()
                if user_id_str in employee_details:
                    employee_details[user_id_str]['asisten'] = count

        # Hitung total divisi
        kerani_total = sum(d['kerani'] for d in employee_details.values())
        mandor_total = sum(d['mandor'] for d in employee_details.values())
        asisten_total = sum(d['asisten'] for d in employee_details.values())

        # Verifikasi keseluruhan berdasarkan logika duplikat
        div_kerani_verified_total = sum(d['kerani_verified'] for d in employee_details.values())
        verification_rate = (div_kerani_verified_total / kerani_total * 100) if kerani_total > 0 else 0

        # Log informasi untuk analisis dengan filter status 704
        if use_status_704_filter:
            self.logger.info(f"*** FILTER TRANSSTATUS 704 AKTIF untuk {estate_name} ***")
            total_differences = sum(d['kerani_differences'] for d in employee_details.values())
            self.logger.info(f"Total perbedaan transaksi dengan filter 704: {total_differences}")

            # Log detail per karyawan untuk transparansi
            for emp_id, emp_data in employee_details.items():
                if emp_data['kerani_differences'] > 0:
                    verified = emp_data.get('kerani_verified', 0)
                    differences = emp_data['kerani_differences']
                    percentage = (differences / verified * 100) if verified > 0 else 0
                    self.logger.info(f"    👤 {emp_data['name']}: {differences} perbedaan dari {verified} terverifikasi ({percentage:.1f}%)")

        return {
            'estate': estate_name,
            'division': div_name,
            'kerani_total': kerani_total,
            'mandor_total': mandor_total,
            'asisten_total': asisten_total,
            'verifikasi_total': div_kerani_verified_total,
            'verification_rate': verification_rate,
            'employee_details': employee_details
        }