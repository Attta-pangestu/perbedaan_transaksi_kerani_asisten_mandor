"""
Verification Engine untuk FFB Scanner Analysis System

Modul ini mengimplementasikan logika verifikasi transaksi
dan analisis kualitas data untuk sistem FFB Scanner.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FFBVerificationEngine:
    """
    Main verification engine untuk FFB transaction analysis
    """

    def __init__(self, config: Dict = None):
        """
        Initialize verification engine

        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.verification_rules = self.config.get('verification', {})
        self.record_tags = self.verification_rules.get('record_tags', {
            'PM': 'Kerani (Scanner)',
            'P1': 'Mandor (Supervisor)',
            'P5': 'Asisten (Assistant)'
        })

    def _get_default_config(self) -> Dict:
        """
        Get default configuration untuk verification engine

        Returns:
            Default configuration dict
        """
        return {
            'verification': {
                'record_tags': {
                    'PM': 'Kerani (Scanner)',
                    'P1': 'Mandor (Supervisor)',
                    'P5': 'Asisten (Assistant)'
                },
                'verification_rules': {
                    'require_pm': True,
                    'accept_p1_or_p5': True,
                    'both_p1_and_p5': False
                },
                'confidence_levels': {
                    'high': 0.95,
                    'medium': 0.80,
                    'low': 0.60
                }
            },
            'analysis': {
                'min_transaction_threshold': 5,
                'date_range_days': 30,
                'discrepancy_threshold': 0.05
            }
        }

    def verify_transactions(self, df: pd.DataFrame) -> Dict:
        """
        Verifikasi transaksi dan identifikasi yang terverifikasi

        Args:
            df: DataFrame dengan transaksi data

        Returns:
            Dict dengan hasil verifikasi
        """
        logger.info(f"Starting verification for {len(df)} transactions")

        if df.empty:
            logger.warning("Empty dataframe provided to verification engine")
            return self._empty_verification_result()

        # Group transactions by TRANSNO
        grouped = df.groupby('TRANSNO')

        verification_results = {
            'verified_transactions': [],
            'unverified_transactions': [],
            'partial_verified_transactions': [],
            'verification_details': [],
            'summary_stats': {}
        }

        total_pm_count = 0
        verified_pm_count = 0

        for transno, group in grouped:
            result = self._verify_single_transaction(transno, group)
            verification_results['verification_details'].append(result)

            # Process PM records (kerani transactions)
            pm_records = group[group['RECORDTAG'] == 'PM']
            if not pm_records.empty:
                total_pm_count += len(pm_records)

                if result['is_verified']:
                    verified_pm_count += len(pm_records)
                    verification_results['verified_transactions'].extend(pm_records.to_dict('records'))
                elif result['verification_level'] == 'Partial':
                    verification_results['partial_verified_transactions'].extend(pm_records.to_dict('records'))
                else:
                    verification_results['unverified_transactions'].extend(pm_records.to_dict('records'))

        # Calculate summary statistics
        verification_rate = (verified_pm_count / total_pm_count * 100) if total_pm_count > 0 else 0

        verification_results['summary_stats'] = {
            'total_transactions': len(df),
            'total_pm_transactions': total_pm_count,
            'verified_count': len(verification_results['verified_transactions']),
            'partial_verified_count': len(verification_results['partial_verified_transactions']),
            'unverified_count': len(verification_results['unverified_transactions']),
            'verification_rate': verification_rate,
            'unique_transno_count': len(grouped),
            'verification_rules_applied': self.verification_rules
        }

        logger.info(f"Verification complete: {verification_rate:.2f}% verification rate")
        return verification_results

    def _verify_single_transaction(self, transno: str, group: pd.DataFrame) -> Dict:
        """
        Verifikasi transaksi tunggal berdasarkan TRANSNO

        Args:
            transno: Transaction number
            group: DataFrame dengan semua records untuk TRANSNO ini

        Returns:
            Dict dengan hasil verifikasi untuk transaksi ini
        """
        record_tags = group['RECORDTAG'].unique()
        has_pm = 'PM' in record_tags
        has_p1 = 'P1' in record_tags
        has_p5 = 'P5' in record_tags

        # Apply verification rules
        is_verified = False
        verification_level = 'None'
        confidence_score = 0.0
        verification_reasons = []

        if has_pm:
            if has_p1 and has_p5:
                # Complete verification
                is_verified = True
                verification_level = 'Complete'
                confidence_score = 1.0
                verification_reasons.append('Verified by both Mandor and Asisten')

            elif has_p1 or has_p5:
                # Partial verification
                is_verified = True
                verification_level = 'Partial'
                confidence_score = 0.8
                verifier = 'Mandor' if has_p1 else 'Asisten'
                verification_reasons.append(f'Verified by {verifier}')

            else:
                # No verification
                verification_reasons.append('No verification from Mandor or Asisten')

        else:
            # No PM record - cannot be verified in traditional sense
            if has_p1 or has_p5:
                verification_level = 'NonPM_Verified'
                verification_reasons.append('Transaction without Kerani record')
            else:
                verification_reasons.append('Unknown record type combination')

        # Calculate confidence based on record consistency
        consistency_score = self._calculate_record_consistency(group)
        final_confidence = min(confidence_score * consistency_score, 1.0)

        result = {
            'TRANSNO': transno,
            'is_verified': is_verified,
            'verification_level': verification_level,
            'confidence_score': final_confidence,
            'record_tags_present': list(record_tags),
            'has_pm': has_pm,
            'has_p1': has_p1,
            'has_p5': has_p5,
            'verification_reasons': verification_reasons,
            'record_count': len(group),
            'data_consistency': consistency_score
        }

        return result

    def _calculate_record_consistency(self, group: pd.DataFrame) -> float:
        """
        Calculate consistency score untuk multiple records dengan TRANSNO sama

        Args:
            group: DataFrame dengan records untuk satu TRANSNO

        Returns:
            Consistency score (0.0 - 1.0)
        """
        if len(group) <= 1:
            return 1.0

        # Get PM record as baseline
        pm_record = group[group['RECORDTAG'] == 'PM']
        if pm_record.empty:
            return 0.5  # No baseline for comparison

        pm_record = pm_record.iloc[0]

        # Key fields to compare
        comparable_fields = ['AFD', 'BLOCK', 'TREECOUNT', 'BUNCHCOUNT', 'WEIGHT', 'TBS']
        consistency_scores = []

        for _, record in group.iterrows():
            if record['RECORDTAG'] == 'PM':
                continue

            # Compare with PM record
            matches = 0
            total_comparable = 0

            for field in comparable_fields:
                if field in group.columns:
                    total_comparable += 1
                    pm_value = pm_record[field]
                    other_value = record[field]

                    # Handle null values
                    if pd.isna(pm_value) and pd.isna(other_value):
                        matches += 1
                    elif pd.isna(pm_value) or pd.isna(other_value):
                        continue
                    elif pm_value == other_value:
                        matches += 1

            if total_comparable > 0:
                consistency_scores.append(matches / total_comparable)

        if not consistency_scores:
            return 1.0

        return sum(consistency_scores) / len(consistency_scores)

    def analyze_discrepancies(self, df: pd.DataFrame) -> Dict:
        """
        Analisis discrepancies antar records dengan TRANSNO sama

        Args:
            df: DataFrame dengan transaksi data

        Returns:
            Dict dengan analisis discrepancies
        """
        logger.info("Starting discrepancy analysis")

        discrepancies = {
            'field_discrepancies': [],
            'summary': {
                'total_transno_with_discrepancies': 0,
                'total_discrepancies': 0,
                'critical_discrepancies': 0,
                'most_common_discrepancies': {}
            }
        }

        # Group by TRANSNO
        grouped = df.groupby('TRANSNO')

        critical_fields = ['WEIGHT', 'TREECOUNT', 'BUNCHCOUNT']
        field_discrepancy_counts = {}

        for transno, group in grouped:
            if len(group) > 1:  # Multiple records for same TRANSNO
                transno_discrepancies = self._analyze_transno_discrepancies(transno, group, critical_fields)

                if transno_discrepancies:
                    discrepancies['field_discrepancies'].extend(transno_discrepancies)
                    discrepancies['summary']['total_transno_with_discrepancies'] += 1

                    # Count field discrepancies
                    for disc in transno_discrepancies:
                        field_name = disc['field_name']
                        field_discrepancy_counts[field_name] = field_discrepancy_counts.get(field_name, 0) + 1

                        if disc['severity'] == 'Critical':
                            discrepancies['summary']['critical_discrepancies'] += 1

        # Calculate totals
        discrepancies['summary']['total_discrepancies'] = len(discrepancies['field_discrepancies'])
        discrepancies['summary']['most_common_discrepancies'] = dict(
            sorted(field_discrepancy_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        logger.info(f"Discrepancy analysis complete: {discrepancies['summary']['total_discrepancies']} discrepancies found")

        return discrepancies

    def _analyze_transno_discrepancies(self, transno: str, group: pd.DataFrame, critical_fields: List[str]) -> List[Dict]:
        """
        Analisis discrepancies untuk satu TRANSNO

        Args:
            transno: Transaction number
            group: DataFrame dengan records untuk TRANSNO ini
            critical_fields: List of critical field names

        Returns:
            List of discrepancy details
        """
        discrepancies = []

        if len(group) < 2:
            return discrepancies

        # Get PM record as baseline
        pm_record = group[group['RECORDTAG'] == 'PM']
        if pm_record.empty:
            return discrepancies

        pm_record = pm_record.iloc[0]

        # Compare with other records
        for _, record in group.iterrows():
            if record['RECORDTAG'] == 'PM':
                continue

            # Compare each field
            for field in group.columns:
                if field in ['TRANSNO', 'RECORDTAG', 'SCANUSERID', 'TRANSDATE']:
                    continue

                pm_value = pm_record[field]
                other_value = record[field]

                # Check for discrepancy
                if not self._values_equal(pm_value, other_value):
                    severity = 'Critical' if field in critical_fields else 'Minor'

                    discrepancy = {
                        'TRANSNO': transno,
                        'field_name': field,
                        'pm_value': pm_value,
                        'other_value': other_value,
                        'other_record_tag': record['RECORDTAG'],
                        'other_user_id': record['SCANUSERID'],
                        'severity': severity,
                        'discrepancy_type': self._classify_discrepancy_type(field, pm_value, other_value)
                    }

                    discrepancies.append(discrepancy)

        return discrepancies

    def _values_equal(self, value1, value2) -> bool:
        """
        Check if two values are equal (handling null values and numeric comparison)

        Args:
            value1, value2: Values to compare

        Returns:
            True if values are considered equal
        """
        # Handle null values
        if pd.isna(value1) and pd.isna(value2):
            return True
        elif pd.isna(value1) or pd.isna(value2):
            return False

        # Convert to appropriate types for comparison
        try:
            # Try numeric comparison
            num1 = float(value1)
            num2 = float(value2)
            return abs(num1 - num2) < 0.001  # Small tolerance for floating point
        except (ValueError, TypeError):
            # String comparison
            return str(value1).strip() == str(value2).strip()

    def _classify_discrepancy_type(self, field: str, value1, value2) -> str:
        """
        Classify discrepancy type

        Args:
            field: Field name
            value1, value2: Values that differ

        Returns:
            Discrepancy type string
        """
        if pd.isna(value1) or pd.isna(value2):
            return 'Missing Value'
        elif field in ['WEIGHT', 'TREECOUNT', 'BUNCHCOUNT']:
            return 'Numeric Mismatch'
        elif field in ['AFD', 'BLOCK', 'HARVESTER', 'TAKENBY']:
            return 'Code Mismatch'
        else:
            return 'General Mismatch'

    def _empty_verification_result(self) -> Dict:
        """
        Return empty verification result for empty input

        Returns:
            Dict with empty verification result
        """
        return {
            'verified_transactions': [],
            'unverified_transactions': [],
            'partial_verified_transactions': [],
            'verification_details': [],
            'summary_stats': {
                'total_transactions': 0,
                'total_pm_transactions': 0,
                'verified_count': 0,
                'partial_verified_count': 0,
                'unverified_count': 0,
                'verification_rate': 0.0,
                'unique_transno_count': 0
            }
        }

    def get_verification_summary(self, verification_results: Dict) -> str:
        """
        Generate human-readable verification summary

        Args:
            verification_results: Results from verify_transactions()

        Returns:
            Formatted summary string
        """
        stats = verification_results['summary_stats']

        summary = f"""
FFB Transaction Verification Summary
=====================================
Total Transactions: {stats['total_transactions']}
Unique TRANSNO: {stats['unique_transno_count']}
Kerani (PM) Transactions: {stats['total_pm_transactions']}

Verification Results:
- Verified: {stats['verified_count']} ({stats['verification_rate']:.1f}%)
- Partially Verified: {stats['partial_verified_count']}
- Unverified: {stats['unverified_count']}

Verification Rate: {stats['verification_rate']:.2f}%
        """

        return summary.strip()