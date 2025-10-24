#!/usr/bin/env python3
"""
Debug script untuk testing koneksi database 1A dan 1B
"""
import os
from firebird_connector import FirebirdConnector
from datetime import datetime, date

def test_estate_connection(estate_name, db_path):
    """Test koneksi dan query untuk satu estate"""
    print(f"\n{'='*60}")
    print(f"TESTING ESTATE: {estate_name}")
    print(f"Database Path: {db_path}")
    print(f"{'='*60}")

    # Check if file exists
    if not os.path.exists(db_path):
        print(f"[ERROR] FILE TIDAK DITEMUKAN: {db_path}")
        return False

    print(f"[OK] File database ditemukan")

    try:
        # Test connection
        connector = FirebirdConnector(db_path)

        # Test basic connection
        print("Testing basic connection...")
        if connector.test_connection():
            print("[OK] Koneksi berhasil")
        else:
            print("[ERROR] Koneksi gagal")
            return False

        # Test employee table
        print("\nTesting EMP table...")
        try:
            result = connector.execute_query("SELECT COUNT(*) as TOTAL_EMP FROM EMP")
            if result and result[0]["rows"]:
                emp_count = result[0]["rows"][0]["TOTAL_EMP"]
                print(f"[OK] Total EMP: {emp_count}")
            else:
                print("[ERROR] Tidak ada data di EMP table")
        except Exception as e:
            print(f"[ERROR] Error query EMP: {e}")

        # Test division tables
        print("\nTesting division tables...")
        try:
            result = connector.execute_query("SELECT COUNT(*) as TOTAL_DIV FROM CRDIVISION")
            if result and result[0]["rows"]:
                div_count = result[0]["rows"][0]["TOTAL_DIV"]
                print(f"[OK] Total Divisions: {div_count}")
            else:
                print("[ERROR] Tidak ada data di CRDIVISION table")
        except Exception as e:
            print(f"[ERROR] Error query CRDIVISION: {e}")

        # Test FFB tables for September
        print("\nTesting FFBSCANNERDATA09 (September)...")
        try:
            result = connector.execute_query("""
                SELECT COUNT(*) as TOTAL_RECORDS
                FROM FFBSCANNERDATA09
                WHERE TRANSDATE >= '2025-09-01' AND TRANSDATE <= '2025-09-30'
            """)
            if result and result[0]["rows"]:
                ffb_count = result[0]["rows"][0]["TOTAL_RECORDS"]
                print(f"[OK] Total FFB September: {ffb_count}")

                if ffb_count > 0:
                    # Test detailed query
                    result2 = connector.execute_query("""
                        SELECT a.TRANSNO, a.TRANSDATE, a.SCANUSERID, a.RECORDTAG
                        FROM FFBSCANNERDATA09 a
                        JOIN OCFIELD b ON a.FIELDID = b.ID
                        WHERE a.TRANSDATE >= '2025-09-01' AND a.TRANSDATE <= '2025-09-30'
                        AND b.DIVID IS NOT NULL
                        LIMIT 5
                    """)
                    if result2 and result2["rows"]:
                        print(f"[OK] Sample records found:")
                        for row in result2["rows"]:
                            print(f"   - {row.get('TRANSNO', 'N/A')} | {row.get('TRANSDATE', 'N/A')} | {row.get('SCANUSERID', 'N/A')} | {row.get('RECORDTAG', 'N/A')}")
                    else:
                        print("[ERROR] No detailed records found")
                else:
                    print("[ERROR] No September data found")
            else:
                print("[ERROR] Error query FFB September")
        except Exception as e:
            print(f"[ERROR] Error query FFB September: {e}")

        return True

    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("DEBUG KONEKSI DATABASE ESTATE 1A & 1B")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test current config paths
    estates_to_test = {
        "PGE 1A": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1a/PTRJ_P1A.FDB",
        "PGE 1B": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1a/PTRJ_P1A.FDB",  # This is the problem!
    }

    # Also test correct paths
    correct_paths = {
        "PGE 1A (Correct)": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1a/PTRJ_P1A.FDB",
        "PGE 1B (Correct)": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1b/PTRJ_P1B.FDB",
    }

    print("\n" + "="*80)
    print("TESTING CURRENT CONFIGURATION")
    print("="*80)

    for estate_name, db_path in estates_to_test.items():
        test_estate_connection(estate_name, db_path)

    print("\n" + "="*80)
    print("TESTING CORRECT CONFIGURATION")
    print("="*80)

    for estate_name, db_path in correct_paths.items():
        test_estate_connection(estate_name, db_path)

    print("\n" + "="*80)
    print("ANALISIS SELESAI")
    print("="*80)

if __name__ == "__main__":
    main()