#!/usr/bin/env python3
"""
Cek ketersediaan data FFB di berbagai bulan untuk estate 1A
"""
from firebird_connector import FirebirdConnector

def check_available_months(db_path):
    """Cek data di semua bulan yang tersedia"""
    print(f"Checking database: {db_path}")

    try:
        connector = FirebirdConnector(db_path)

        # Cek semua bulan dari FFBSCANNERDATA01 - FFBSCANNERDATA12
        for month in range(1, 13):
            table_name = f"FFBSCANNERDATA{month:02d}"
            print(f"\n--- Checking {table_name} ---")

            try:
                # Cek total records
                count_query = f"SELECT COUNT(*) as TOTAL FROM {table_name}"
                result = connector.execute_query(count_query)

                if result and result[0]["rows"]:
                    total = result[0]["rows"][0]["TOTAL"]
                    print(f"Total records: {total}")

                    if int(total) > 0:
                        # Cek rentang tanggal
                        date_query = f"""
                        SELECT MIN(TRANSDATE) as MIN_DATE, MAX(TRANSDATE) as MAX_DATE,
                               COUNT(DISTINCT TRANSDATE) as UNIQUE_DAYS
                        FROM {table_name}
                        """
                        date_result = connector.execute_query(date_query)

                        if date_result and date_result[0]["rows"]:
                            row = date_result[0]["rows"][0]
                            print(f"Date range: {row.get('MIN_DATE', 'N/A')} to {row.get('MAX_DATE', 'N/A')}")
                            print(f"Unique days: {row.get('UNIQUE_DAYS', 'N/A')}")

                        # Sample data
                        sample_query = f"SELECT FIRST 3 TRANSNO, TRANSDATE, SCANUSERID FROM {table_name}"
                        sample_result = connector.execute_query(sample_query)

                        if sample_result and sample_result["rows"]:
                            print("Sample records:")
                            for row in sample_result["rows"]:
                                print(f"  - {row.get('TRANSNO', 'N/A')} | {row.get('TRANSDATE', 'N/A')} | {row.get('SCANUSERID', 'N/A')}")

            except Exception as e:
                print(f"Error checking {table_name}: {e}")

    except Exception as e:
        print(f"Connection error: {e}")

def main():
    print("=== CEK KETERSEDIAAN DATA FFB ESTATE 1A ===")

    # Path database yang benar
    db_path_1a = "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1a/PTRJ_P1A.FDB"
    db_path_1b = "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1b/PTRJ_P1B.FDB"

    print("\n** ESTATE PGE 1A **")
    check_available_months(db_path_1a)

    print("\n\n** ESTATE PGE 1B **")
    check_available_months(db_path_1b)

if __name__ == "__main__":
    main()