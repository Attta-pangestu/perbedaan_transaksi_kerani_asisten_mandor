#!/usr/bin/env python3
"""
Debug script untuk memeriksa mengapa script analisis menghasilkan 117 bukan 123
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from firebird_connector import FirebirdConnector
from analisis_mandor_per_divisi_corrected import get_employee_mapping, analyze_division_transactions

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def debug_analysis():
    print("DEBUG ANALYSIS SCRIPT")
    print("="*40)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("Connection failed!")
            return
        
        print("Connected!")
        
        # Get employee mapping
        employee_mapping = get_employee_mapping(connector)
        print(f"Employee mapping loaded: {len(employee_mapping)} entries")
        
        # Test the exact query used in analysis
        print("\n1. TESTING ANALYSIS QUERY:")
        
        # This is the query from analyze_division_transactions
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
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        ORDER BY a.SCANUSERID, a.TRANSDATE, a.TRANSTIME
        """
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        print(f"Total rows from analysis query: {len(df)}")
        
        if not df.empty:
            # Filter for Erly PM transactions
            erly_pm = df[(df.iloc[:, 1] == '4771') & (df.iloc[:, 18] == 'PM')]
            print(f"Erly PM transactions: {len(erly_pm)}")
            
            # Check all Erly transactions
            erly_all = df[df.iloc[:, 1] == '4771']
            print(f"Erly all transactions: {len(erly_all)}")
            
            if len(erly_all) > 0:
                print("\nErly transaction breakdown:")
                recordtag_counts = erly_all.iloc[:, 18].value_counts()
                for tag, count in recordtag_counts.items():
                    print(f"  {tag}: {count}")
        
        print("\n2. TESTING ANALYZE_DIVISION_TRANSACTIONS:")
        
        # Test the actual function
        result = analyze_division_transactions(connector, employee_mapping, '16', 'Air Kundo', 4, 2025)
        
        if result:
            role_stats = result['role_stats']
            verification_stats = result.get('verification_stats', {})
            
            print(f"Function result:")
            print(f"  Total kerani: {verification_stats.get('total_kerani_transactions', 0)}")
            print(f"  Total mandor: {verification_stats.get('total_mandor_transactions', 0)}")
            print(f"  Total asisten: {verification_stats.get('total_asisten_transactions', 0)}")
            
            # Check Erly specifically
            kerani_data = role_stats.get('KERANI', {})
            if '4771' in kerani_data:
                erly_data = kerani_data['4771']
                print(f"\nErly data from function:")
                print(f"  Name: {erly_data['employee_name']}")
                print(f"  Transactions: {erly_data['total_transactions']}")
                print(f"  Expected: 123")
                print(f"  Match: {'YES' if erly_data['total_transactions'] == 123 else 'NO'}")
            else:
                print("\nErly not found in KERANI data!")
                print("Available KERANI IDs:", list(kerani_data.keys()))
        else:
            print("Function returned None!")
        
        print("\n3. DIRECT COUNT CHECK:")
        
        # Direct count for comparison
        count_query = """
        SELECT COUNT(*) 
        FROM FFBSCANNERDATA04 a 
        JOIN OCFIELD b ON a.FIELDID = b.ID 
        WHERE b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        """
        
        count_result = connector.execute_query(count_query)
        count_df = connector.to_pandas(count_result)
        
        if not count_df.empty:
            direct_count = int(count_df.iloc[0, 0])
            print(f"Direct count: {direct_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_analysis()
