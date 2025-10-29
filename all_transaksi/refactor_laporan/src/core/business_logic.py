"""
Core Business Logic untuk FFB Scanner Analysis System

Modul ini mengandung semua logika bisnis inti untuk:
1. Verifikasi transaksi antara Kerani (PM), Mandor (P1), dan Asisten (P5)
2. Deteksi duplikasi berdasarkan TRANSNO
3. Perhitungan tingkat verifikasi
4. Analisis kualitas data
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FFBVerificationEngine:
    """
    Engine utama untuk verifikasi transaksi FFB Scanner
    """

    # Record tag definitions
    RECORD_TAGS = {
        'PM': 'Kerani (Scanner)',
        'P1': 'Mandor (Supervisor)',
        'P5': 'Asisten (Assistant)'
    }

    # Verification rules
    VERIFICATION_RULES = {
        'kerani_to_mandor': ('PM', 'P1'),
        'kerani_to_asisten': ('PM', 'P5'),
        'mandor_to_asisten': ('P1', 'P5')
    }

    def __init__(self):
        self.verification_results = {}
        self.analysis_stats = {}

    def verify_transactions(self, df: pd.DataFrame) -> Dict:
        """
        Verifikasi transaksi dan identifikasi yang terverifikasi

        Args:
            df: DataFrame dengan data transaksi dari database

        Returns:
            Dict dengan hasil verifikasi
        """
        logger.info(f"Memulai verifikasi {len(df)} transaksi")

        # Group by TRANSNO untuk identifikasi duplikat
        grouped = df.groupby('TRANSNO')

        verified_transactions = []
        unverified_transactions = []
        verification_details = []

        for transno, group in grouped:
            record_tags = group['RECORDTAG'].unique()

            # Logika verifikasi: transaksi dianggap verified jika ada PM + P1/P5
            if 'PM' in record_tags and any(tag in record_tags for tag in ['P1', 'P5']):
                # Transaksi terverifikasi
                pm_record = group[group['RECORDTAG'] == 'PM'].iloc[0]
                verified_transactions.append(pm_record)

                # Tambahkan detail verifikasi
                detail = {
                    'TRANSNO': transno,
                    'VERIFIED': True,
                    'KERANI_DATA': pm_record.to_dict(),
                    'VERIFIER_TAGS': [tag for tag in record_tags if tag in ['P1', 'P5']]
                }
                verification_details.append(detail)

            else:
                # Transaksi tidak terverifikasi
                if 'PM' in record_tags:
                    pm_record = group[group['RECORDTAG'] == 'PM'].iloc[0]
                    unverified_transactions.append(pm_record)

                    detail = {
                        'TRANSNO': transno,
                        'VERIFIED': False,
                        'KERANI_DATA': pm_record.to_dict(),
                        'VERIFIER_TAGS': []
                    }
                    verification_details.append(detail)

        # Calculate verification rate
        total_pm_transactions = len(verified_transactions) + len(unverified_transactions)
        verification_rate = (len(verified_transactions) / total_pm_transactions * 100) if total_pm_transactions > 0 else 0

        results = {
            'total_transactions': len(df),
            'total_pm_transactions': total_pm_transactions,
            'verified_count': len(verified_transactions),
            'unverified_count': len(unverified_transactions),
            'verification_rate': verification_rate,
            'verified_transactions': pd.DataFrame(verified_transactions),
            'unverified_transactions': pd.DataFrame(unverified_transactions),
            'verification_details': verification_details
        }

        logger.info(f"Verifikasi selesai: {len(verified_transactions)} verified, {len(unverified_transactions)} unverified")

        return results

    def analyze_employee_performance(self, df: pd.DataFrame, verification_results: Dict) -> Dict:
        """
        Analisis performa karyawan berdasarkan hasil verifikasi

        Args:
            df: DataFrame transaksi original
            verification_results: Hasil verifikasi dari verify_transactions()

        Returns:
            Dict dengan analisis performa per karyawan
        """
        logger.info("Menganalisis performa karyawan")

        # Group by employee (SCANUSERID)
        kerani_data = df[df['RECORDTAG'] == 'PM']

        if kerani_data.empty:
            logger.warning("Tidak ada data kerani (PM) untuk dianalisis")
            return {}

        performance_data = []

        for employee_id, employee_transactions in kerani_data.groupby('SCANUSERID'):
            # Hitung statistik per employee
            total_transactions = len(employee_transactions)

            # Cek berapa yang verified
            verified_count = 0
            for _, transaction in employee_transactions.iterrows():
                transno = transaction['TRANSNO']
                is_verified = any(
                    detail['TRANSNO'] == transno and detail['VERIFIED']
                    for detail in verification_results['verification_details']
                )
                if is_verified:
                    verified_count += 1

            verification_rate = (verified_count / total_transactions * 100) if total_transactions > 0 else 0

            # Get employee info
            emp_info = employee_transactions.iloc[0]

            performance = {
                'EMPLOYEE_ID': employee_id,
                'EMPLOYEE_NAME': emp_info.get('EMPNAME', 'Unknown'),
                'DIVISION': emp_info.get('DIVNAME', 'Unknown'),
                'TOTAL_TRANSACTIONS': total_transactions,
                'VERIFIED_COUNT': verified_count,
                'UNVERIFIED_COUNT': total_transactions - verified_count,
                'VERIFICATION_RATE': verification_rate,
                'PERFORMANCE_SCORE': self._calculate_performance_score(verification_rate)
            }

            performance_data.append(performance)

        # Convert to DataFrame untuk easier processing
        performance_df = pd.DataFrame(performance_data)

        # Sort by performance
        performance_df = performance_df.sort_values('VERIFICATION_RATE', ascending=False)

        logger.info(f"Analisis performa selesai untuk {len(performance_df)} karyawan")

        return {
            'performance_data': performance_df,
            'top_performers': performance_df.head(10).to_dict('records'),
            'bottom_performers': performance_df.tail(10).to_dict('records'),
            'average_verification_rate': performance_df['VERIFICATION_RATE'].mean()
        }

    def _calculate_performance_score(self, verification_rate: float) -> str:
        """
        Calculate performance score based on verification rate

        Args:
            verification_rate: Percentage of verified transactions

        Returns:
            Performance score category
        """
        if verification_rate >= 95:
            return "Excellent"
        elif verification_rate >= 85:
            return "Good"
        elif verification_rate >= 70:
            return "Fair"
        elif verification_rate >= 50:
            return "Poor"
        else:
            return "Very Poor"

    def detect_discrepancies(self, df: pd.DataFrame) -> List[Dict]:
        """
        Deteksi perbedaan data antar transaksi dengan TRANSNO sama

        Args:
            df: DataFrame transaksi

        Returns:
            List dari discrepancies yang ditemukan
        """
        logger.info("Mendeteksi perbedaan data transaksi")

        discrepancies = []

        # Group by TRANSNO
        grouped = df.groupby('TRANSNO')

        for transno, group in grouped:
            if len(group) > 1:  # Ada duplikat
                # Get different record types
                record_types = group['RECORDTAG'].unique()

                if len(record_types) > 1:  # Beda record type
                    # Compare key fields
                    pm_record = group[group['RECORDTAG'] == 'PM'].iloc[0] if 'PM' in record_types else None

                    if pm_record is not None:
                        # Compare with other records
                        for _, other_record in group.iterrows():
                            if other_record['RECORDTAG'] != 'PM':
                                differences = self._compare_records(pm_record, other_record)
                                if differences:
                                    discrepancies.append({
                                        'TRANSNO': transno,
                                        'PM_RECORD': pm_record.to_dict(),
                                        'OTHER_RECORD': other_record.to_dict(),
                                        'DIFFERENCES': differences,
                                        'SEVERITY': self._calculate_discrepancy_severity(differences)
                                    })

        logger.info(f"Ditemukan {len(discrepancies)} perbedaan data")

        return discrepancies

    def _compare_records(self, record1: pd.Series, record2: pd.Series) -> List[Dict]:
        """
        Bandingkan dua record dan identifikasi perbedaan

        Args:
            record1, record2: Dua pandas Series untuk dibandingkan

        Returns:
            List dari perbedaan yang ditemukan
        """
        differences = []

        # Key fields to compare
        key_fields = ['AFD', 'BLOCK', 'TREECOUNT', 'BUNCHCOUNT', 'LOOSEFRUIT',
                     'WEIGHT', 'TBS', 'HARVESTER', 'TAKENBY']

        for field in key_fields:
            if field in record1.index and field in record2.index:
                val1 = record1[field]
                val2 = record2[field]

                if pd.isna(val1) and pd.isna(val2):
                    continue
                elif pd.isna(val1) or pd.isna(val2) or val1 != val2:
                    differences.append({
                        'FIELD': field,
                        'VALUE_PM': val1,
                        'VALUE_OTHER': val2,
                        'DIFFERENCE_TYPE': 'Value Mismatch'
                    })

        return differences

    def _calculate_discrepancy_severity(self, differences: List[Dict]) -> str:
        """
        Calculate severity level for discrepancies

        Args:
            differences: List dari field differences

        Returns:
            Severity level (Low, Medium, High, Critical)
        """
        if not differences:
            return "None"

        # Critical fields
        critical_fields = ['WEIGHT', 'TREECOUNT', 'BUNCHCOUNT']

        has_critical = any(diff['FIELD'] in critical_fields for diff in differences)

        if has_critical:
            return "Critical"
        elif len(differences) >= 3:
            return "High"
        elif len(differences) >= 2:
            return "Medium"
        else:
            return "Low"

    def generate_summary_statistics(self, verification_results: Dict, performance_results: Dict, discrepancies: List) -> Dict:
        """
        Generate summary statistics untuk reporting

        Args:
            verification_results: Hasil verifikasi transaksi
            performance_results: Hasil analisis performa
            discrepancies: List dari discrepancies

        Returns:
            Dict dengan summary statistics
        """
        summary = {
            'transaction_summary': {
                'total_transactions': verification_results.get('total_transactions', 0),
                'total_pm_transactions': verification_results.get('total_pm_transactions', 0),
                'verified_count': verification_results.get('verified_count', 0),
                'unverified_count': verification_results.get('unverified_count', 0),
                'overall_verification_rate': verification_results.get('verification_rate', 0)
            },
            'performance_summary': {
                'total_employees': len(performance_results.get('performance_data', pd.DataFrame())),
                'average_verification_rate': performance_results.get('average_verification_rate', 0),
                'excellent_performers': len([p for p in performance_results.get('performance_data', pd.DataFrame()).to_dict('records') if p.get('PERFORMANCE_SCORE') == 'Excellent']),
                'poor_performers': len([p for p in performance_results.get('performance_data', pd.DataFrame()).to_dict('records') if p.get('PERFORMANCE_SCORE') in ['Poor', 'Very Poor']])
            },
            'quality_summary': {
                'total_discrepancies': len(discrepancies),
                'critical_discrepancies': len([d for d in discrepancies if d.get('SEVERITY') == 'Critical']),
                'high_discrepancies': len([d for d in discrepancies if d.get('SEVERITY') == 'High']),
                'discrepancy_rate': (len(discrepancies) / verification_results.get('total_pm_transactions', 1) * 100)
            }
        }

        return summary


class FFBDataProcessor:
    """
    Data processor untuk preprocessing dan cleaning data FFB
    """

    def __init__(self):
        self.required_columns = [
            'TRANSNO', 'SCANUSERID', 'RECORDTAG', 'TRANSDATE',
            'FIELDID', 'AFD', 'BLOCK', 'TREECOUNT', 'BUNCHCOUNT'
        ]

    def preprocess_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess raw data dari database

        Args:
            raw_data: Raw DataFrame dari database query

        Returns:
            Cleaned DataFrame yang siap untuk analisis
        """
        logger.info(f"Preprocessing {len(raw_data)} records")

        # Make a copy to avoid SettingWithCopyWarning
        df = raw_data.copy()

        # Convert date columns
        if 'TRANSDATE' in df.columns:
            df['TRANSDATE'] = pd.to_datetime(df['TRANSDATE'], errors='coerce')

        # Clean numeric columns
        numeric_columns = ['TREECOUNT', 'BUNCHCOUNT', 'LOOSEFRUIT', 'WEIGHT', 'TBS']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Clean text columns
        text_columns = ['AFD', 'BLOCK', 'HARVESTER', 'TAKENBY']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # Remove rows with essential missing data
        essential_columns = ['TRANSNO', 'SCANUSERID', 'RECORDTAG']
        df = df.dropna(subset=essential_columns)

        logger.info(f"Preprocessing complete: {len(df)} clean records")

        return df

    def filter_by_date_range(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter data berdasarkan rentang tanggal

        Args:
            df: DataFrame yang akan difilter
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Filtered DataFrame
        """
        if 'TRANSDATE' not in df.columns:
            logger.warning("Column TRANSDATE not found, skipping date filter")
            return df

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        mask = (df['TRANSDATE'] >= start_date) & (df['TRANSDATE'] <= end_date)
        filtered_df = df[mask]

        logger.info(f"Date filter: {len(filtered_df)} records from {len(df)} total")

        return filtered_df

    def filter_by_estates(self, df: pd.DataFrame, estates: List[str]) -> pd.DataFrame:
        """
        Filter data berdasarkan estates tertentu

        Args:
            df: DataFrame yang akan difilter
            estates: List dari estate names

        Returns:
            Filtered DataFrame
        """
        if 'DIVNAME' not in df.columns:
            logger.warning("Column DIVNAME not found, skipping estate filter")
            return df

        mask = df['DIVNAME'].isin(estates)
        filtered_df = df[mask]

        logger.info(f"Estate filter: {len(filtered_df)} records from {len(df)} total")

        return filtered_df