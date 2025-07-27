#!/usr/bin/env python3
"""
Corrected April 2025 FFB Scanner Data Analysis
Based on debug findings - uses correct date range and query structure
"""

import os
import sys
import pandas as pd
from datetime import datetime
from collections import defaultdict

from firebird_connector import FirebirdConnector

# Database configuration
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def analyze_air_kundo_corrected():
    """
    Corrected analysis for Air Kundo division using the exact user query structure.
    """
    print("CORRECTED ANALYSIS: AIR KUNDO DIVISION")
    print("="*60)
    print("Using user's exact query structure with correct date range")
    print("="*60)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # User's exact query for Air Kundo with correct date range
        total_receipts_query = """
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
        
        result = connector.execute_query(total_receipts_query)
        df = connector.to_pandas(result)
        
        print(f"\n1. TOTAL RECEIPTS VERIFICATION")
        print("-" * 40)
        print(f"Total PM transactions in Air Kundo: {len(df)}")
        print(f"Expected: 264")
        print(f"Status: {'✓ MATCH' if len(df) == 264 else '✗ MISMATCH'}")
        
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
            
            print(f"\n2. EMPLOYEE BREAKDOWN (KERANI - PM Transactions)")
            print("-" * 50)
            
            # Count by SCANUSERID (column 1)
            scanuserid_counts = df.groupby(df.iloc[:, 1]).size()
            
            expected_employees = {
                'DJULI DARTA (ADDIANI)': 141,
                'ERLY (MARDIAH)': 123
            }
            
            total_found = 0
            for user_id, count in scanuserid_counts.items():
                emp_name = employee_mapping.get(str(user_id), f"UNKNOWN-{user_id}")
                print(f"  {emp_name} (ID: {user_id}): {count} transactions")
                total_found += count
                
                # Check against expected
                for expected_name, expected_count in expected_employees.items():
                    if expected_name in emp_name:
                        status = "✓ MATCH" if count == expected_count else f"✗ DIFF: {count - expected_count}"
                        print(f"    Expected: {expected_count} - {status}")
                        break
            
            print(f"\nTotal found: {total_found}")
            
            # Now get verification data (P1 and P5 transactions)
            print(f"\n3. VERIFICATION TRANSACTIONS ANALYSIS")
            print("-" * 50)
            
            verification_query = """
            SELECT 
                a.SCANUSERID,
                a.RECORDTAG,
                a.TRANSSTATUS,
                a.TRANSNO,
                a.TRANSDATE
            FROM 
                FFBSCANNERDATA04 a
            JOIN 
                OCFIELD b ON a.FIELDID = b.ID
            WHERE 
                b.DIVID = '16'
                AND a.RECORDTAG IN ('P1', 'P5')
                AND a.TRANSDATE >= '2025-04-01'
                AND a.TRANSDATE < '2025-04-29'
            ORDER BY a.SCANUSERID, a.RECORDTAG, a.TRANSDATE
            """
            
            ver_result = connector.execute_query(verification_query)
            ver_df = connector.to_pandas(ver_result)
            
            if not ver_df.empty:
                print(f"Found {len(ver_df)} verification transactions")
                
                # Group by employee and role
                verification_stats = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'verified': 0}))
                
                for _, row in ver_df.iterrows():
                    user_id = str(row.iloc[0]).strip()
                    recordtag = str(row.iloc[1]).strip()
                    transstatus = str(row.iloc[2]).strip()
                    
                    emp_name = employee_mapping.get(user_id, f"UNKNOWN-{user_id}")
                    role = "MANDOR" if recordtag == "P1" else "ASISTEN" if recordtag == "P5" else recordtag
                    
                    verification_stats[emp_name][role]['total'] += 1
                    if transstatus == '704':
                        verification_stats[emp_name][role]['verified'] += 1
                
                # Display verification breakdown
                total_mandor_verified = 0
                total_asisten_verified = 0
                
                for emp_name, roles in verification_stats.items():
                    print(f"\n  {emp_name}:")
                    for role, stats in roles.items():
                        verified = stats['verified']
                        total = stats['total']
                        print(f"    {role}: {verified} verified out of {total} total")
                        
                        if role == "MANDOR":
                            total_mandor_verified += verified
                        elif role == "ASISTEN":
                            total_asisten_verified += verified
                
                # Calculate verification rates
                total_receipts = len(df)
                mandor_rate = (total_mandor_verified / total_receipts * 100) if total_receipts > 0 else 0
                asisten_rate = (total_asisten_verified / total_receipts * 100) if total_receipts > 0 else 0
                
                print(f"\n4. VERIFICATION RATES COMPARISON")
                print("-" * 40)
                print(f"Mandor Verification: {mandor_rate:.2f}% (Expected: 5.30%)")
                print(f"Asisten Verification: {asisten_rate:.2f}% (Expected: 0.76%)")
                
                mandor_match = abs(mandor_rate - 5.30) < 0.1
                asisten_match = abs(asisten_rate - 0.76) < 0.1
                
                print(f"Mandor Rate: {'✓ MATCH' if mandor_match else '✗ MISMATCH'}")
                print(f"Asisten Rate: {'✓ MATCH' if asisten_match else '✗ MISMATCH'}")
                
                # Expected verification breakdown
                print(f"\n5. EXPECTED vs ACTUAL VERIFICATION BREAKDOWN")
                print("-" * 55)
                print("Expected:")
                print("  DJULI DARTA (ADDIANI): 0 Conductor, 0 Assistant, 0 Manager, 141 Bunch Counter")
                print("  ERLY (MARDIAH): 0 Conductor, 0 Assistant, 0 Manager, 123 Bunch Counter")
                print("  SUHAYAT (ZALIAH): 14 Conductor, 0 Assistant, 0 Manager, 0 Bunch Counter")
                print("  SURANTO (Nurkelumi): 0 Conductor, 2 Assistant, 0 Manager, 0 Bunch Counter")
                
                print("\nActual:")
                for emp_name, roles in verification_stats.items():
                    conductor = roles.get('MANDOR', {}).get('verified', 0)
                    assistant = roles.get('ASISTEN', {}).get('verified', 0)
                    print(f"  {emp_name}: {conductor} Conductor, {assistant} Assistant, 0 Manager")
                
                # Also show bunch counter (PM) data
                for user_id, count in scanuserid_counts.items():
                    emp_name = employee_mapping.get(str(user_id), f"UNKNOWN-{user_id}")
                    print(f"  {emp_name}: 0 Conductor, 0 Assistant, 0 Manager, {count} Bunch Counter")
                
            else:
                print("No verification transactions found")
        
        print(f"\n" + "="*60)
        print("ANALYSIS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"Error in corrected analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_air_kundo_corrected()
