"""
Test Suite untuk Analysis Modules

Test file untuk memvalidasi functionality dari analysis modules
"""

import unittest
import sys
import os
import pandas as pd
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.business_logic import FFBVerificationEngine, FFBDataProcessor
from analysis.verification_engine import FFBVerificationEngine as AnalysisVerificationEngine
from core.config import FFBConfig

class TestFFBVerificationEngine(unittest.TestCase):
    """
    Test cases untuk FFBVerificationEngine dari core.business_logic
    """

    def setUp(self):
        """
        Setup test environment
        """
        self.engine = FFBVerificationEngine()
        self.sample_data = self._create_sample_data()

    def _create_sample_data(self):
        """
        Create sample data for testing
        """
        return pd.DataFrame({
            'TRANSNO': ['T001', 'T001', 'T002', 'T003', 'T003', 'T004'],
            'SCANUSERID': ['U001', 'U002', 'U001', 'U003', 'U004', 'U001'],
            'RECORDTAG': ['PM', 'P1', 'PM', 'PM', 'P5', 'PM'],
            'TRANSDATE': pd.to_datetime(['2025-09-01', '2025-09-01', '2025-09-02', '2025-09-03', '2025-09-03', '2025-09-04']),
            'FIELDID': ['F001', 'F001', 'F002', 'F003', 'F003', 'F004'],
            'AFD': ['A1', 'A1', 'A2', 'A1', 'A1', 'A2'],
            'BLOCK': ['B1', 'B1', 'B2', 'B1', 'B1', 'B2'],
            'TREECOUNT': [100, 100, 150, 200, 200, 120],
            'BUNCHCOUNT': [50, 50, 75, 100, 100, 60],
            'DIVNAME': ['PGE 1A', 'PGE 1A', 'PGE 1B', 'PGE 1A', 'PGE 1A', 'PGE 1B']
        })

    def test_verify_transactions_basic(self):
        """
        Test basic transaction verification
        """
        results = self.engine.verify_transactions(self.sample_data)

        # Check basic structure
        self.assertIn('verified_transactions', results)
        self.assertIn('unverified_transactions', results)
        self.assertIn('verification_rate', results)
        self.assertIn('verification_details', results)

        # Check verification logic
        self.assertGreater(results['verified_count'], 0)
        self.assertGreaterEqual(results['verification_rate'], 0)
        self.assertLessEqual(results['verification_rate'], 100)

    def test_verification_rules(self):
        """
        Test verification rules application
        """
        results = self.engine.verify_transactions(self.sample_data)

        # T001 should be verified (PM + P1)
        # T003 should be verified (PM + P5)
        # T002 and T004 should be unverified (PM only)

        verified_transnos = [t['TRANSNO'] for t in results['verification_details'] if t['VERIFIED']]
        unverified_transnos = [t['TRANSNO'] for t in results['verification_details'] if not t['VERIFIED']]

        self.assertIn('T001', verified_transnos)
        self.assertIn('T003', verified_transnos)
        self.assertIn('T002', unverified_transnos)
        self.assertIn('T004', unverified_transnos)

    def test_analyze_employee_performance(self):
        """
        Test employee performance analysis
        """
        verification_results = self.engine.verify_transactions(self.sample_data)
        performance_results = self.engine.analyze_employee_performance(self.sample_data, verification_results)

        # Check structure
        self.assertIn('performance_data', performance_results)
        self.assertIn('top_performers', performance_results)
        self.assertIn('average_verification_rate', performance_results)

        if not performance_results['performance_data'].empty:
            # Check performance metrics
            first_employee = performance_results['performance_data'].iloc[0]
            self.assertIn('EMPLOYEE_ID', first_employee)
            self.assertIn('VERIFICATION_RATE', first_employee)
            self.assertIn('PERFORMANCE_SCORE', first_employee)

    def test_detect_discrepancies(self):
        """
        Test discrepancy detection
        """
        # Create data with discrepancies
        discrepancy_data = pd.DataFrame({
            'TRANSNO': ['T001', 'T001'],
            'SCANUSERID': ['U001', 'U002'],
            'RECORDTAG': ['PM', 'P1'],
            'TRANSDATE': pd.to_datetime(['2025-09-01', '2025-09-01']),
            'FIELDID': ['F001', 'F001'],
            'AFD': ['A1', 'A2'],  # Different AFD
            'BLOCK': ['B1', 'B1'],
            'TREECOUNT': [100, 110],  # Different tree count
            'BUNCHCOUNT': [50, 50],
            'DIVNAME': ['PGE 1A', 'PGE 1A']
        })

        discrepancies = self.engine.detect_discrepancies(discrepancy_data)

        self.assertIsInstance(discrepancies, list)
        if discrepancies:  # Only check if discrepancies found
            first_discrepancy = discrepancies[0]
            self.assertIn('TRANSNO', first_discrepancy)
            self.assertIn('DIFFERENCES', first_discrepancy)
            self.assertIn('SEVERITY', first_discrepancy)

    def test_performance_score_calculation(self):
        """
        Test performance score calculation
        """
        # Test different verification rates
        self.assertEqual(self.engine._calculate_performance_score(96), "Excellent")
        self.assertEqual(self.engine._calculate_performance_score(90), "Good")
        self.assertEqual(self.engine._calculate_performance_score(80), "Fair")
        self.assertEqual(self.engine._calculate_performance_score(60), "Poor")
        self.assertEqual(self.engine._calculate_performance_score(40), "Very Poor")

    def test_generate_summary_statistics(self):
        """
        Test summary statistics generation
        """
        verification_results = self.engine.verify_transactions(self.sample_data)
        performance_results = self.engine.analyze_employee_performance(self.sample_data, verification_results)
        discrepancies = self.engine.detect_discrepancies(self.sample_data)

        summary = self.engine.generate_summary_statistics(
            verification_results, performance_results, discrepancies
        )

        # Check structure
        self.assertIn('transaction_summary', summary)
        self.assertIn('performance_summary', summary)
        self.assertIn('quality_summary', summary)

        # Check values
        trans_summary = summary['transaction_summary']
        self.assertEqual(trans_summary['total_transactions'], len(self.sample_data))
        self.assertIn('overall_verification_rate', trans_summary)


class TestFFBDataProcessor(unittest.TestCase):
    """
    Test cases untuk FFBDataProcessor
    """

    def setUp(self):
        """
        Setup test environment
        """
        self.processor = FFBDataProcessor()
        self.sample_raw_data = self._create_sample_raw_data()

    def _create_sample_raw_data(self):
        """
        Create sample raw data with quality issues
        """
        return pd.DataFrame({
            'TRANSNO': ['T001', 'T002', 'T003', '', 'T004'],
            'SCANUSERID': ['U001', 'U002', '', 'U004', 'U005'],
            'RECORDTAG': ['PM', 'P1', 'PM', 'PM', 'P5'],
            'TRANSDATE': ['2025-09-01', '2025-09-01', 'invalid-date', '2025-09-03', '2025-09-04'],
            'FIELDID': ['F001', 'F002', 'F003', 'F004', 'F005'],
            'AFD': ['A1', 'A2', 'A3', 'A4', 'A5'],
            'BLOCK': ['B1', 'B2', 'B3', 'B4', 'B5'],
            'TREECOUNT': ['100', '150', 'invalid', '200', '120'],
            'BUNCHCOUNT': [50, 75, 60, 100, 60],
            'WEIGHT': ['1000.5', '1500.2', '1200', '2000.1', '1200.3']
        })

    def test_preprocess_data(self):
        """
        Test data preprocessing
        """
        processed_data = self.processor.preprocess_data(self.sample_raw_data)

        # Check data cleaning
        self.assertLessEqual(len(processed_data), len(self.sample_raw_data))

        # Check essential columns are preserved
        essential_columns = ['TRANSNO', 'SCANUSERID', 'RECORDTAG', 'TRANSDATE', 'FIELDID']
        for col in essential_columns:
            self.assertIn(col, processed_data.columns)

        # Check date conversion
        if 'TRANSDATE' in processed_data.columns:
            self.assertTrue(
                all(isinstance(x, pd.Timestamp) or pd.isna(x) for x in processed_data['TRANSDATE'])
            )

        # Check numeric conversion
        numeric_columns = ['TREECOUNT', 'BUNCHCOUNT', 'WEIGHT']
        for col in numeric_columns:
            if col in processed_data.columns:
                self.assertTrue(
                    all(isinstance(x, (int, float)) or pd.isna(x) for x in processed_data[col])
                )

    def test_filter_by_date_range(self):
        """
        Test date range filtering
        """
        # Create data with valid dates
        valid_data = pd.DataFrame({
            'TRANSNO': ['T001', 'T002', 'T003', 'T004'],
            'TRANSDATE': pd.to_datetime(['2025-09-01', '2025-09-15', '2025-10-01', '2025-10-15'])
        })

        filtered_data = self.processor.filter_by_date_range(
            valid_data, '2025-09-01', '2025-09-30'
        )

        # Should only include September dates
        expected_dates = pd.to_datetime(['2025-09-01', '2025-09-15'])
        self.assertTrue(all(date in expected_dates for date in filtered_data['TRANSDATE']))

    def test_filter_by_estates(self):
        """
        Test estate filtering
        """
        data_with_estates = pd.DataFrame({
            'TRANSNO': ['T001', 'T002', 'T003', 'T004'],
            'DIVNAME': ['PGE 1A', 'PGE 1B', 'PGE 1A', 'PGE 2A']
        })

        filtered_data = self.processor.filter_by_estates(data_with_estates, ['PGE 1A'])

        # Should only include PGE 1A records
        self.assertTrue(all(estate == 'PGE 1A' for estate in filtered_data['DIVNAME']))
        self.assertEqual(len(filtered_data), 2)


class TestAnalysisVerificationEngine(unittest.TestCase):
    """
    Test cases untuk AnalysisVerificationEngine dari analysis.verification_engine
    """

    def setUp(self):
        """
        Setup test environment
        """
        self.engine = AnalysisVerificationEngine()
        self.sample_data = self._create_sample_data()

    def _create_sample_data(self):
        """
        Create sample data for testing
        """
        return pd.DataFrame({
            'TRANSNO': ['T001', 'T001', 'T002', 'T003', 'T003', 'T004'],
            'SCANUSERID': ['U001', 'U002', 'U001', 'U003', 'U004', 'U001'],
            'RECORDTAG': ['PM', 'P1', 'PM', 'PM', 'P5', 'PM'],
            'TRANSDATE': pd.to_datetime(['2025-09-01', '2025-09-01', '2025-09-02', '2025-09-03', '2025-09-03', '2025-09-04']),
            'FIELDID': ['F001', 'F001', 'F002', 'F003', 'F003', 'F004'],
            'AFD': ['A1', 'A1', 'A2', 'A1', 'A1', 'A2'],
            'BLOCK': ['B1', 'B1', 'B2', 'B1', 'B1', 'B2'],
            'TREECOUNT': [100, 100, 150, 200, 200, 120],
            'BUNCHCOUNT': [50, 50, 75, 100, 100, 60]
        })

    def test_verify_transactions_advanced(self):
        """
        Test advanced transaction verification
        """
        results = self.engine.verify_transactions(self.sample_data)

        # Check comprehensive structure
        required_keys = [
            'verified_transactions', 'unverified_transactions',
            'partial_verified_transactions', 'verification_details', 'summary_stats'
        ]
        for key in required_keys:
            self.assertIn(key, results)

        # Check summary statistics
        summary = results['summary_stats']
        self.assertIn('total_transactions', summary)
        self.assertIn('verification_rate', summary)
        self.assertIn('unique_transno_count', summary)

    def test_verify_single_transaction(self):
        """
        Test single transaction verification
        """
        # Test verified transaction (PM + P1)
        verified_group = self.sample_data[self.sample_data['TRANSNO'] == 'T001']
        result = self.engine._verify_single_transaction('T001', verified_group)

        self.assertTrue(result['is_verified'])
        self.assertEqual(result['verification_level'], 'Complete')
        self.assertEqual(result['confidence_score'], 1.0)
        self.assertTrue(result['has_pm'])
        self.assertTrue(result['has_p1'])

        # Test unverified transaction (PM only)
        unverified_group = self.sample_data[self.sample_data['TRANSNO'] == 'T002']
        result = self.engine._verify_single_transaction('T002', unverified_group)

        self.assertFalse(result['is_verified'])
        self.assertTrue(result['has_pm'])
        self.assertFalse(result['has_p1'])
        self.assertFalse(result['has_p5'])

    def test_calculate_record_consistency(self):
        """
        Test record consistency calculation
        """
        # Perfect match
        perfect_match = pd.DataFrame({
            'RECORDTAG': ['PM', 'P1'],
            'AFD': ['A1', 'A1'],
            'BLOCK': ['B1', 'B1'],
            'TREECOUNT': [100, 100]
        })
        consistency = self.engine._calculate_record_consistency(perfect_match)
        self.assertEqual(consistency, 1.0)

        # Partial match
        partial_match = pd.DataFrame({
            'RECORDTAG': ['PM', 'P1'],
            'AFD': ['A1', 'A1'],
            'BLOCK': ['B1', 'B2'],  # Different
            'TREECOUNT': [100, 100]
        })
        consistency = self.engine._calculate_record_consistency(partial_match)
        self.assertGreater(consistency, 0.5)
        self.assertLess(consistency, 1.0)

    def test_analyze_discrepancies(self):
        """
        Test discrepancy analysis
        """
        # Create data with discrepancies
        discrepancy_data = pd.DataFrame({
            'TRANSNO': ['T001', 'T001', 'T002', 'T002'],
            'RECORDTAG': ['PM', 'P1', 'PM', 'P1'],
            'TREECOUNT': [100, 110, 200, 190],  # Discrepancies
            'WEIGHT': [1000, 1000, 2000, 2100]  # Discrepancy
        })

        results = self.engine.analyze_discrepancies(discrepancy_data)

        # Check structure
        self.assertIn('field_discrepancies', results)
        self.assertIn('summary', results)

        # Check summary
        summary = results['summary']
        self.assertIn('total_discrepancies', summary)
        self.assertIn('critical_discrepancies', summary)
        self.assertIn('most_common_discrepancies', summary)

    def test_values_equal(self):
        """
        Test value equality checking
        """
        # Test equal values
        self.assertTrue(self.engine._values_equal(100, 100))
        self.assertTrue(self.engine._values_equal("A1", "A1"))
        self.assertTrue(self.engine._values_equal(None, None))

        # Test unequal values
        self.assertFalse(self.engine._values_equal(100, 200))
        self.assertFalse(self.engine._values_equal("A1", "A2"))

        # Test null handling
        self.assertFalse(self.engine._values_equal(100, None))
        self.assertFalse(self.engine._values_equal(None, "A1"))

        # Test numeric tolerance
        self.assertTrue(self.engine._values_equal(100.0, 100.001))
        self.assertFalse(self.engine._values_equal(100.0, 100.1))

    def test_classify_discrepancy_type(self):
        """
        Test discrepancy type classification
        """
        # Test missing values
        self.assertEqual(
            self.engine._classify_discrepancy_type('TREECOUNT', 100, None),
            'Missing Value'
        )

        # Test numeric mismatch
        self.assertEqual(
            self.engine._classify_discrepancy_type('TREECOUNT', 100, 110),
            'Numeric Mismatch'
        )

        # Test code mismatch
        self.assertEqual(
            self.engine._classify_discrepancy_type('AFD', 'A1', 'A2'),
            'Code Mismatch'
        )

    def test_get_verification_summary(self):
        """
        Test verification summary generation
        """
        # Create mock results
        mock_results = {
            'summary_stats': {
                'total_transactions': 100,
                'total_pm_transactions': 80,
                'verified_count': 60,
                'partial_verified_count': 10,
                'unverified_count': 10,
                'verification_rate': 75.0,
                'unique_transno_count': 50
            }
        }

        summary = self.engine.get_verification_summary(mock_results)

        self.assertIn('FFB Transaction Verification Summary', summary)
        self.assertIn('Total Transactions: 100', summary)
        self.assertIn('Verification Rate: 75.00%', summary)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)