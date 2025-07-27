#!/usr/bin/env python3
"""
Test script untuk memverifikasi query Erly di divisi Air Kundo
"""

from firebird_connector import FirebirdConnector

# Database configuration
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def test_erly_query():
    """Test query untuk Erly (SCANUSERID = 4771) di Air Kundo"""
    print("TESTING ERLY QUERY - AIR KUNDO")
    print("="*50)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # Query yang diberikan user
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
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        """
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        print(f"\nHasil query untuk Erly (SCANUSERID = 4771):")
        print(f"Total transaksi PM: {len(df)}")
        print(f"Expected: 123")
        print(f"Status: {'✓ MATCH' if len(df) == 123 else '✗ MISMATCH'}")
        
        if not df.empty:
            print(f"\nDetail transaksi:")
            print(f"SCANUSERID: {df.iloc[0, 1]}")
            print(f"RECORDTAG: {df.iloc[0, 18]}")
            print(f"DIVISI_ID: {df.iloc[0, 28]}")
            
            # Cek rentang tanggal
            dates = df.iloc[:, 15].unique()  # TRANSDATE column
            print(f"Rentang tanggal: {min(dates)} to {max(dates)}")
            
            # Cek status transaksi
            statuses = df.iloc[:, 19].value_counts()  # TRANSSTATUS column
            print(f"Status transaksi:")
            for status, count in statuses.items():
                print(f"  Status {status}: {count} transaksi")
        
        # Test juga untuk semua kerani di Air Kundo
        print(f"\n" + "="*50)
        print("TESTING ALL KERANI - AIR KUNDO")
        print("="*50)
        
        all_kerani_query = """
        SELECT  
            a.SCANUSERID,
            COUNT(*) as total_transactions
        FROM  
            FFBSCANNERDATA04 a 
        JOIN  
            OCFIELD b ON a.FIELDID = b.ID 
        WHERE  
            b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        GROUP BY a.SCANUSERID
        ORDER BY a.SCANUSERID
        """
        
        result2 = connector.execute_query(all_kerani_query)
        df2 = connector.to_pandas(result2)
        
        if not df2.empty:
            print(f"Semua KERANI di Air Kundo:")
            total_all = 0
            for _, row in df2.iterrows():
                scanuserid = row.iloc[0]
                count = row.iloc[1]
                total_all += count
                print(f"  SCANUSERID {scanuserid}: {count} transaksi")
            
            print(f"\nTotal semua transaksi PM: {total_all}")
            print(f"Expected total: 264")
            print(f"Status: {'✓ MATCH' if total_all == 264 else '✗ MISMATCH'}")
        
        # Get employee names
        print(f"\n" + "="*50)
        print("EMPLOYEE NAME MAPPING")
        print("="*50)
        
        emp_query = "SELECT ID, NAME FROM EMP WHERE ID IN ('183', '4771')"
        emp_result = connector.execute_query(emp_query)
        emp_df = connector.to_pandas(emp_result)
        
        if not emp_df.empty:
            for _, row in emp_df.iterrows():
                emp_id = row.iloc[0]
                emp_name = row.iloc[1]
                print(f"ID {emp_id}: {emp_name}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_erly_query()
