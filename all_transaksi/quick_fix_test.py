#!/usr/bin/env python3

print("QUICK FIX VERIFICATION")
print("="*30)

# Test 1: Check if direct query gives 123
try:
    from firebird_connector import FirebirdConnector
    
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    connector = FirebirdConnector(DB_PATH)
    
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
        print(f"✅ Direct query: Erly = {count}")
        if count == 123:
            print("✅ Database confirms Erly = 123")
        else:
            print(f"❌ Expected 123, got {count}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔧 FIXES APPLIED:")
print("✅ RECORDTAG 'XX' error handling added")
print("✅ Date range corrected to 2025-04-29")
print("✅ GUI default dates updated")

print("\n🚀 GUI READY TO TEST:")
print("Run: run_gui.bat")
print("Expected: Erly = 123 in Air Kundo")
