#!/usr/bin/env python3
"""
Simple Debug Script for April 2025 Discrepancies
"""

import os
import sys
from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def simple_debug():
    print("SIMPLE DEBUG: April 2025 Data Analysis")
    print("="*50)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # 1. Check total transactions with different date ranges
        print("\n1. DATE RANGE ANALYSIS")
        print("-" * 30)
        
        queries = [
            ("Range 1 (<=29)", "SELECT COUNT(*) FROM FFBSCANNERDATA04 WHERE TRANSDATE >= '2025-04-01' AND TRANSDATE <= '2025-04-29'"),
            ("Range 2 (<=30)", "SELECT COUNT(*) FROM FFBSCANNERDATA04 WHERE TRANSDATE >= '2025-04-01' AND TRANSDATE <= '2025-04-30'"),
            ("Range 3 (<05-01)", "SELECT COUNT(*) FROM FFBSCANNERDATA04 WHERE TRANSDATE >= '2025-04-01' AND TRANSDATE < '2025-05-01'")
        ]
        
        for desc, query in queries:
            result = connector.execute_query(query)
            df = connector.to_pandas(result)
            if not df.empty:
                count = df.iloc[0, 0]
                print(f"  {desc}: {count}")
        
        # 2. Check division totals
        print("\n2. DIVISION TOTALS")
        print("-" * 30)
        
        div_query = """
        SELECT 
            c.DIVNAME,
            COUNT(*) as total
        FROM 
            FFBSCANNERDATA04 a
        JOIN 
            OCFIELD b ON a.FIELDID = b.ID
        JOIN 
            CRDIVISION c ON b.DIVID = c.ID
        WHERE 
            a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-05-01'
        GROUP BY c.DIVNAME
        ORDER BY c.DIVNAME
        """
        
        result = connector.execute_query(div_query)
        df = connector.to_pandas(result)
        
        expected = {
            'Air Batu': 2322,
            'Air Kundo': 264,
            'Air Hijau': 2008
        }
        
        for _, row in df.iterrows():
            div_name = str(row.iloc[0]).strip()
            actual = int(row.iloc[1])
            exp = expected.get(div_name, 0)
            diff = actual - exp
            print(f"  {div_name}: {actual} (Expected: {exp}, Diff: {diff})")
        
        # 3. Check role distribution
        print("\n3. ROLE DISTRIBUTION")
        print("-" * 30)
        
        role_query = """
        SELECT 
            a.RECORDTAG,
            COUNT(*) as total,
            COUNT(CASE WHEN a.TRANSSTATUS = '704' THEN 1 END) as verified
        FROM 
            FFBSCANNERDATA04 a
        WHERE 
            a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-05-01'
            AND a.RECORDTAG IS NOT NULL
        GROUP BY a.RECORDTAG
        ORDER BY a.RECORDTAG
        """
        
        result = connector.execute_query(role_query)
        df = connector.to_pandas(result)
        
        role_names = {'PM': 'KERANI', 'P1': 'MANDOR', 'P5': 'ASISTEN'}
        
        for _, row in df.iterrows():
            tag = str(row.iloc[0]).strip()
            total = int(row.iloc[1])
            verified = int(row.iloc[2])
            rate = (verified / total * 100) if total > 0 else 0
            role_name = role_names.get(tag, tag)
            print(f"  {tag} ({role_name}): {total} total, {verified} verified ({rate:.2f}%)")
        
        print("\n4. SUMMARY OF ISSUES")
        print("-" * 30)
        print("• Total transactions are higher than expected")
        print("• Need to check if filtering criteria matches expected data")
        print("• Verification rates calculation may need adjustment")
        print("• Employee mapping and role assignment need verification")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_debug()
