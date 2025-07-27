#!/usr/bin/env python3
"""
Script Test untuk Verifikasi Data April 2025
"""

import os
import sys
import pandas as pd
from datetime import datetime

from firebird_connector import FirebirdConnector

# Konfigurasi database
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def test_april_data():
    """Test data April 2025."""
    print("TESTING APRIL 2025 DATA")
    print("="*50)
    
    try:
        # Setup database connection
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # Test data exists
        query = """
        SELECT COUNT(*) as total_transactions
        FROM FFBSCANNERDATA04 
        WHERE TRANSDATE >= '2025-04-01' 
        AND TRANSDATE <= '2025-04-29'
        """
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if not df.empty:
            total = df.iloc[0, 0]
            print(f"✓ Found {total} total transactions in April 2025")
        
        # Test per division
        query_divisions = """
        SELECT 
            c.DIVCODE,
            c.DIVNAME,
            COUNT(*) as transaction_count
        FROM 
            FFBSCANNERDATA04 a
        JOIN 
            OCFIELD b ON a.FIELDID = b.ID
        JOIN 
            CRDIVISION c ON b.DIVID = c.ID
        WHERE 
            a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE <= '2025-04-29'
        GROUP BY c.DIVCODE, c.DIVNAME
        ORDER BY c.DIVCODE
        """
        
        result = connector.execute_query(query_divisions)
        df = connector.to_pandas(result)
        
        print("\nDivision breakdown:")
        for _, row in df.iterrows():
            div_code = row.iloc[0]
            div_name = row.iloc[1]
            count = row.iloc[2]
            print(f"  {div_code} ({div_name}): {count} transactions")
        
        # Test role breakdown
        query_roles = """
        SELECT 
            a.RECORDTAG,
            COUNT(*) as transaction_count,
            COUNT(CASE WHEN a.TRANSSTATUS = '704' THEN 1 END) as verified_count
        FROM 
            FFBSCANNERDATA04 a
        WHERE 
            a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE <= '2025-04-29'
            AND a.RECORDTAG IS NOT NULL
        GROUP BY a.RECORDTAG
        ORDER BY a.RECORDTAG
        """
        
        result = connector.execute_query(query_roles)
        df = connector.to_pandas(result)
        
        print("\nRole breakdown:")
        role_mapping = {'PM': 'KERANI', 'P1': 'MANDOR', 'P5': 'ASISTEN'}
        
        for _, row in df.iterrows():
            recordtag = row.iloc[0]
            total_count = int(row.iloc[1]) if str(row.iloc[1]).isdigit() else 0
            verified_count = int(row.iloc[2]) if str(row.iloc[2]).isdigit() else 0

            role_name = role_mapping.get(recordtag, recordtag)
            verification_rate = (verified_count / total_count * 100) if total_count > 0 else 0

            print(f"  {recordtag} ({role_name}): {total_count} total, {verified_count} verified ({verification_rate:.2f}%)")
        
        print("\n" + "="*50)
        print("TEST COMPLETED")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_april_data() 