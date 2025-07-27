#!/usr/bin/env python3
"""
Test Firebird 1.5 compatibility untuk query yang sudah diperbaiki
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def test_firebird_query():
    """Test query yang sudah diperbaiki untuk Firebird 1.5"""
    print("TESTING FIREBIRD 1.5 COMPATIBILITY")
    print("="*50)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("❌ Database connection failed!")
            return False
        
        print("✅ Database connected")
        
        # Test query yang sudah diperbaiki (tanpa alias di COUNT)
        print("\nTesting corrected query for Air Kundo...")
        
        query = """
        SELECT 
            a.SCANUSERID,
            a.RECORDTAG,
            COUNT(*)
        FROM 
            FFBSCANNERDATA04 a
        JOIN 
            OCFIELD b ON a.FIELDID = b.ID
        WHERE 
            b.DIVID = '16'
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        GROUP BY a.SCANUSERID, a.RECORDTAG
        ORDER BY a.SCANUSERID, a.RECORDTAG
        """
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df.empty:
            print("❌ No data found")
            return False
        
        print(f"✅ Query successful! Found {len(df)} records")
        
        # Process results untuk cari Erly
        erly_pm = 0
        total_kerani = 0
        
        for _, row in df.iterrows():
            user_id = str(row.iloc[0]).strip()
            recordtag = str(row.iloc[1]).strip()
            count = int(row.iloc[2])
            
            if recordtag == 'PM':
                total_kerani += count
                if user_id == '4771':
                    erly_pm = count
        
        print(f"\n📊 RESULTS:")
        print(f"Total KERANI (PM) transactions: {total_kerani}")
        print(f"Erly (4771) PM transactions: {erly_pm}")
        print(f"Expected Erly: 123")
        
        if erly_pm == 123:
            print("✅ SUCCESS! Erly shows correct value: 123")
            return True
        else:
            print(f"❌ MISMATCH! Erly shows: {erly_pm}, expected: 123")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_count():
    """Test simple count query"""
    print("\nTESTING SIMPLE COUNT QUERY")
    print("="*40)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        # Test simple count untuk Erly
        query = """
        SELECT COUNT(*)
        FROM FFBSCANNERDATA04 a 
        JOIN OCFIELD b ON a.FIELDID = b.ID 
        WHERE b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        """
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if not df.empty:
            count = int(df.iloc[0, 0])
            print(f"✅ Simple count query successful!")
            print(f"Erly (4771) PM count: {count}")
            print(f"Expected: 123")
            
            if count == 123:
                print("✅ PERFECT! Simple count matches expected value")
                return True
            else:
                print(f"❌ Mismatch in simple count: {count} vs 123")
                return False
        else:
            print("❌ No results from simple count")
            return False
            
    except Exception as e:
        print(f"❌ Error in simple count: {e}")
        return False

def main():
    """Main test function"""
    print("FIREBIRD 1.5 COMPATIBILITY TEST")
    print("="*60)
    print("Testing queries without COUNT(*) alias for compatibility")
    print("="*60)
    
    # Test 1: Complex GROUP BY query
    complex_ok = test_firebird_query()
    
    # Test 2: Simple count query
    simple_ok = test_simple_count()
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Complex GROUP BY query: {'✅ PASS' if complex_ok else '❌ FAIL'}")
    print(f"Simple COUNT query: {'✅ PASS' if simple_ok else '❌ FAIL'}")
    
    if complex_ok and simple_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Firebird 1.5 compatibility fixed")
        print("✅ Erly shows correct value: 123")
        print("✅ System ready for GUI and PDF reports")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Run GUI: python run_simple_gui.py")
        print("2. Or run complete system: python final_corrected_system.py")
        
    else:
        print("\n❌ TESTS FAILED!")
        print("Need to check Firebird compatibility further")
    
    return complex_ok and simple_ok

if __name__ == "__main__":
    main()
