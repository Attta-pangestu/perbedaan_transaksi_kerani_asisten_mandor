#!/usr/bin/env python3
"""
Debug Script for April 2025 FFB Scanner Data Verification Discrepancies
Analyzes why actual results don't match expected verification data
"""

import os
import sys
import pandas as pd
from datetime import datetime
from collections import defaultdict

from firebird_connector import FirebirdConnector

# Database configuration
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def debug_april_discrepancies():
    """Debug the discrepancies in April 2025 verification data."""
    print("DEBUG ANALYSIS: APRIL 2025 FFB SCANNER DATA DISCREPANCIES")
    print("="*70)

    try:
        # Setup database connection
        connector = FirebirdConnector(DB_PATH)

        if not connector.test_connection():
            print("✗ Database connection failed!")
            return

        print("✓ Database connection successful")

        # Expected data from user requirements
        expected_data = {
            'Air Batu': {
                'div_id': '15',  # Based on user query example
                'total_receipts': 2322,
                'employees': {
                    'DJULI DARTA (ADDIANI)': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 381},
                    'ERLY (MARDIAH)': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 1941},
                    'SUHAYAT (ZALIAH)': {'conductor': 314, 'assistant': 0, 'manager': 0, 'bunch_counter': 0},
                    'SURANTO (Nurkelumi)': {'conductor': 0, 'assistant': 281, 'manager': 0, 'bunch_counter': 0}
                },
                'verification_rates': {'manager': 0.00, 'assistant': 12.10, 'mandore': 13.52}
            },
            'Air Kundo': {
                'div_id': '16',  # Based on user query example
                'total_receipts': 264,
                'employees': {
                    'DJULI DARTA (ADDIANI)': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 141},
                    'ERLY (MARDIAH)': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 123},
                    'SUHAYAT (ZALIAH)': {'conductor': 14, 'assistant': 0, 'manager': 0, 'bunch_counter': 0},
                    'SURANTO (Nurkelumi)': {'conductor': 0, 'assistant': 2, 'manager': 0, 'bunch_counter': 0}
                },
                'verification_rates': {'manager': 0.00, 'assistant': 0.76, 'mandore': 5.30}
            },
            'Air Hijau': {
                'div_id': '17',  # Estimated based on pattern
                'total_receipts': 2008,
                'employees': {
                    'DARWIS HERMAN': {'conductor': 0, 'assistant': 185, 'manager': 0, 'bunch_counter': 0},
                    'IRWANSYAH ( Agustina )': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 1199},
                    'ZULHARI ( AMINAH )': {'conductor': 297, 'assistant': 0, 'manager': 0, 'bunch_counter': 809}
                },
                'verification_rates': {'manager': 0.00, 'assistant': 9.21, 'mandore': 14.79}
            }
        }

        print("\n1. CHECKING DATE RANGE CONSISTENCY")
        print("-" * 50)

        # Test different date ranges to identify the correct one
        date_ranges = [
            ("2025-04-01", "2025-04-29", "User specified range (<=)"),
            ("2025-04-01", "2025-04-30", "Include April 30"),
            ("2025-04-01", "2025-05-01", "Standard month range (<)")
        ]

        for start_date, end_date, description in date_ranges:
            if "Standard" in description:
                query = f"""
                SELECT COUNT(*) as total
                FROM FFBSCANNERDATA04
                WHERE TRANSDATE >= '{start_date}'
                AND TRANSDATE < '{end_date}'
                """
            else:
                query = f"""
                SELECT COUNT(*) as total
                FROM FFBSCANNERDATA04
                WHERE TRANSDATE >= '{start_date}'
                AND TRANSDATE <= '{end_date}'
                """

            result = connector.execute_query(query)
            df = connector.to_pandas(result)

            if not df.empty:
                total = int(df.iloc[0, 0]) if str(df.iloc[0, 0]).isdigit() else 0
                print(f"  {description}: {total} transactions")

        print("\n2. VERIFYING AIR KUNDO DIVISION (ID=16) - USER EXAMPLE")
        print("-" * 50)

        # Test the exact query provided by user for Air Kundo
        air_kundo_query = """
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
            FFBSCANNERDATA04 a
        JOIN
            OCFIELD b ON a.FIELDID = b.ID
        WHERE
            b.DIVID = '16'
            AND a.RECORDTAG = 'PM'
            AND a.TRANSDATE >= '2025-04-01'
            AND a.TRANSDATE < '2025-04-29'
        """

        result = connector.execute_query(air_kundo_query)
        df = connector.to_pandas(result)

        print(f"Air Kundo PM transactions (user query): {len(df)}")
        print(f"Expected total receipts: 264")
        print(f"Difference: {len(df) - 264}")

        if not df.empty:
            print("\nBreakdown by SCANUSERID:")
            scanuserid_counts = df.groupby(df.iloc[:, 1]).size()  # SCANUSERID is column 1
            for user_id, count in scanuserid_counts.items():
                print(f"  {user_id}: {count} transactions")

        print("\n3. ANALYZING DIVISION-SPECIFIC DATA WITH ROLE BREAKDOWN")
        print("-" * 50)

        # Get employee mapping
        emp_query = "SELECT ID, NAME FROM EMP"
        emp_result = connector.execute_query(emp_query)
        emp_df = connector.to_pandas(emp_result)

        employee_mapping = {}
        if not emp_df.empty:
            for _, row in emp_df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                if emp_id and emp_name:
                    employee_mapping[emp_id] = emp_name

        print(f"✓ Loaded {len(employee_mapping)} employee mappings")

        # Get division mapping
        div_query = """
        SELECT ID, DIVNAME, DIVCODE
        FROM CRDIVISION
        WHERE DIVNAME IN ('Air Batu', 'Air Kundo', 'Air Hijau')
        ORDER BY DIVNAME
        """
        div_result = connector.execute_query(div_query)
        div_df = connector.to_pandas(div_result)

        division_mapping = {}
        if not div_df.empty:
            for _, row in div_df.iterrows():
                div_id = str(row.iloc[0]).strip()
                div_name = str(row.iloc[1]).strip()
                div_code = str(row.iloc[2]).strip()
                division_mapping[div_name] = {'id': div_id, 'code': div_code}

        print(f"✓ Found division mappings: {list(division_mapping.keys())}")

        # Analyze each division with detailed role breakdown
        for div_name in expected_data.keys():
            print(f"\n--- DIVISION: {div_name} ---")

            # Use expected division ID or find it
            if div_name in division_mapping:
                div_id = division_mapping[div_name]['id']
            else:
                div_id = expected_data[div_name].get('div_id', 'UNKNOWN')

            print(f"  Division ID: {div_id}")

            # First, get total receipts (PM transactions only - these are created by KERANI)
            total_query = f"""
            SELECT COUNT(*) as total_receipts
            FROM FFBSCANNERDATA04 a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE b.DIVID = '{div_id}'
                AND a.RECORDTAG = 'PM'
                AND a.TRANSDATE >= '2025-04-01'
                AND a.TRANSDATE < '2025-04-30'
            """

            total_result = connector.execute_query(total_query)
            total_df = connector.to_pandas(total_result)

            actual_total = int(total_df.iloc[0, 0]) if not total_df.empty else 0
            expected_total = expected_data[div_name]['total_receipts']

            print(f"  Total Receipts (PM): {actual_total} (Expected: {expected_total})")
            print(f"  Difference: {actual_total - expected_total}")

            # Get detailed breakdown by role and employee
            detail_query = f"""
            SELECT
                a.SCANUSERID,
                a.RECORDTAG,
                a.TRANSSTATUS,
                COUNT(*) as transaction_count
            FROM FFBSCANNERDATA04 a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE b.DIVID = '{div_id}'
                AND a.TRANSDATE >= '2025-04-01'
                AND a.TRANSDATE < '2025-04-30'
                AND a.RECORDTAG IN ('PM', 'P1', 'P5')
            GROUP BY a.SCANUSERID, a.RECORDTAG, a.TRANSSTATUS
            ORDER BY a.SCANUSERID, a.RECORDTAG
            """

            detail_result = connector.execute_query(detail_query)
            detail_df = connector.to_pandas(detail_result)

            if detail_df.empty:
                print(f"  ✗ No transaction data found for {div_name}")
                continue

            # Analyze by employee and role
            employee_stats = defaultdict(lambda: {
                'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 0
            })

            # Role mapping based on RECORDTAG
            role_mapping = {'PM': 'bunch_counter', 'P1': 'conductor', 'P5': 'assistant'}

            total_pm_transactions = 0  # Only PM transactions count as receipts
            verified_transactions = {'conductor': 0, 'assistant': 0, 'manager': 0}

            print(f"  Detailed Transaction Analysis:")

            for _, row in detail_df.iterrows():
                scanner_id = str(row.iloc[0]).strip()
                recordtag = str(row.iloc[1]).strip()
                transstatus = str(row.iloc[2]).strip()
                count = int(row.iloc[3]) if str(row.iloc[3]).isdigit() else 0

                emp_name = employee_mapping.get(scanner_id, f"UNKNOWN-{scanner_id}")
                role = role_mapping.get(recordtag, 'unknown')

                # Count PM transactions as receipts (created by KERANI)
                if recordtag == 'PM':
                    employee_stats[emp_name]['bunch_counter'] += count
                    total_pm_transactions += count

                # Count verification transactions
                if transstatus == '704':  # Verified status
                    if recordtag == 'P1':  # MANDOR verification
                        employee_stats[emp_name]['conductor'] += count
                        verified_transactions['conductor'] += count
                    elif recordtag == 'P5':  # ASISTEN verification
                        employee_stats[emp_name]['assistant'] += count
                        verified_transactions['assistant'] += count

                print(f"    {emp_name} ({scanner_id}): {recordtag} - {count} transactions (Status: {transstatus})")

            print(f"\n  Summary for {div_name}:")
            print(f"    Total PM Transactions (Receipts): {total_pm_transactions}")
            print(f"    Expected: {expected_data[div_name]['total_receipts']}")
            print(f"    Difference: {total_pm_transactions - expected_data[div_name]['total_receipts']}")

            # Calculate verification rates based on total receipts
            mandore_rate = (verified_transactions['conductor'] / total_pm_transactions * 100) if total_pm_transactions > 0 else 0
            assistant_rate = (verified_transactions['assistant'] / total_pm_transactions * 100) if total_pm_transactions > 0 else 0

            print(f"    Verification Rates:")
            print(f"      Mandore: {mandore_rate:.2f}% (Expected: {expected_data[div_name]['verification_rates']['mandore']:.2f}%)")
            print(f"      Assistant: {assistant_rate:.2f}% (Expected: {expected_data[div_name]['verification_rates']['assistant']:.2f}%)")

            print(f"    Employee Breakdown:")
            for emp_name, roles in employee_stats.items():
                if any(roles.values()):  # Only show employees with transactions
                    conductor = roles['conductor']
                    assistant = roles['assistant']
                    manager = roles['manager']
                    bunch_counter = roles['bunch_counter']
                    print(f"      {emp_name}: Conductor={conductor}, Assistant={assistant}, Manager={manager}, Bunch Counter={bunch_counter}")

                    # Compare with expected data
                    if emp_name in expected_data[div_name]['employees']:
                        expected = expected_data[div_name]['employees'][emp_name]
                        print(f"        Expected: Conductor={expected['conductor']}, Assistant={expected['assistant']}, Manager={expected['manager']}, Bunch Counter={expected['bunch_counter']}")

                        # Check for mismatches
                        mismatches = []
                        if conductor != expected['conductor']:
                            mismatches.append(f"Conductor: {conductor} vs {expected['conductor']}")
                        if assistant != expected['assistant']:
                            mismatches.append(f"Assistant: {assistant} vs {expected['assistant']}")
                        if manager != expected['manager']:
                            mismatches.append(f"Manager: {manager} vs {expected['manager']}")
                        if bunch_counter != expected['bunch_counter']:
                            mismatches.append(f"Bunch Counter: {bunch_counter} vs {expected['bunch_counter']}")

                        if mismatches:
                            print(f"        ⚠️  MISMATCHES: {', '.join(mismatches)}")
                        else:
                            print(f"        ✓ MATCH")

        print("\n4. POTENTIAL ISSUES IDENTIFIED")
        print("-" * 50)
        print("Based on the analysis above, potential issues include:")
        print("• Date range inconsistency (using < vs <= for end date)")
        print("• Division ID mapping differences")
        print("• Employee name variations or ID mismatches")
        print("• Role assignment logic differences")
        print("• Verification status interpretation (TRANSSTATUS = '704')")
        print("• Query filtering logic differences")

        print("\n5. RECOMMENDATIONS")
        print("-" * 50)
        print("1. Verify the correct date range format for April 2025")
        print("2. Confirm division ID mappings in CRDIVISION table")
        print("3. Check employee ID to name mappings in EMP table")
        print("4. Validate RECORDTAG role mappings (PM=KERANI, P1=MANDOR, P5=ASISTEN)")
        print("5. Confirm verification status logic (TRANSSTATUS = '704')")
        print("6. Test with the exact query structure provided by user")

        print("\n" + "="*70)
        print("DEBUG ANALYSIS COMPLETED")
        print("="*70)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def analyze_air_kundo_detailed():
    """Detailed analysis of Air Kundo division as requested by user."""
    print("\nDETAILED ANALYSIS: AIR KUNDO DIVISION")
    print("="*50)

    try:
        connector = FirebirdConnector(DB_PATH)

        if not connector.test_connection():
            print("✗ Database connection failed!")
            return

        # User's exact query for Air Kundo
        query = """
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
            FFBSCANNERDATA04 a
        JOIN
            OCFIELD b ON a.FIELDID = b.ID
        WHERE
            b.DIVID = '16'
            AND a.RECORDTAG = 'PM'
            AND a.TRANSDATE >= '2025-04-01'
            AND a.TRANSDATE < '2025-04-29'
        """

        result = connector.execute_query(query)
        df = connector.to_pandas(result)

        print(f"Total PM transactions in Air Kundo: {len(df)}")
        print(f"Expected: 264")

        if not df.empty:
            # Get employee mapping
            emp_query = "SELECT ID, NAME FROM EMP"
            emp_result = connector.execute_query(emp_query)
            emp_df = connector.to_pandas(emp_result)

            employee_mapping = {}
            if not emp_df.empty:
                for _, row in emp_df.iterrows():
                    emp_id = str(row.iloc[0]).strip()
                    emp_name = str(row.iloc[1]).strip()
                    if emp_id and emp_name:
                        employee_mapping[emp_id] = emp_name

            print("\nBreakdown by SCANUSERID (KERANI who created transactions):")
            scanuserid_counts = df.groupby(df.iloc[:, 1]).size()  # SCANUSERID is column 1

            for user_id, count in scanuserid_counts.items():
                emp_name = employee_mapping.get(str(user_id), f"UNKNOWN-{user_id}")
                print(f"  {emp_name} ({user_id}): {count} transactions")

            # Now get verification data for Air Kundo
            verification_query = """
            SELECT
                a.SCANUSERID,
                a.RECORDTAG,
                a.TRANSSTATUS,
                COUNT(*) as count
            FROM
                FFBSCANNERDATA04 a
            JOIN
                OCFIELD b ON a.FIELDID = b.ID
            WHERE
                b.DIVID = '16'
                AND a.RECORDTAG IN ('P1', 'P5')
                AND a.TRANSDATE >= '2025-04-01'
                AND a.TRANSDATE < '2025-04-29'
            GROUP BY a.SCANUSERID, a.RECORDTAG, a.TRANSSTATUS
            ORDER BY a.SCANUSERID, a.RECORDTAG
            """

            ver_result = connector.execute_query(verification_query)
            ver_df = connector.to_pandas(ver_result)

            print("\nVerification transactions breakdown:")
            if not ver_df.empty:
                for _, row in ver_df.iterrows():
                    user_id = str(row.iloc[0]).strip()
                    recordtag = str(row.iloc[1]).strip()
                    transstatus = str(row.iloc[2]).strip()
                    count = int(row.iloc[3])

                    emp_name = employee_mapping.get(user_id, f"UNKNOWN-{user_id}")
                    role = "MANDOR" if recordtag == "P1" else "ASISTEN" if recordtag == "P5" else recordtag
                    status = "VERIFIED" if transstatus == "704" else f"STATUS-{transstatus}"

                    print(f"  {emp_name} ({user_id}) - {role}: {count} transactions ({status})")
            else:
                print("  No verification transactions found")

    except Exception as e:
        print(f"Error in detailed analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_april_discrepancies()
    print("\n" + "="*70)
    analyze_air_kundo_detailed()
