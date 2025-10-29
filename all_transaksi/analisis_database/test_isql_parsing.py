#!/usr/bin/env python3
"""
Test script to verify ISQL parsing fix
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.database.firebird_connector import FirebirdConnector

def test_parsing():
    """Test the ISQL parsing with sample output that contains duplicate headers"""

    # Sample ISQL output that was causing the issue (simplified version)
    sample_output = """Database:  localhost:D:/test/PATH.FDB, User: sysdba
SQL> SQL> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON>
          ID   SCANUSERID         OCID     WORKERID    CARRIERID      FIELDID TASKNO      RIPEBCH    UNRIPEBCH     BLACKBCH    ROTTENBCH LONGSTALKBCH    RATDMGBCH   LOOSEFRUIT TRANSNO      TRANSDATE     TRANSTIME            UPLOADDATETIME RECORDTAG  TRANSSTATUS    TRANSTYPE LASTUSER
=========== ============ ============ ============ ============ ============ ====== ============ ============ ============ ============ ============ ============ ============ ========== =========== ============= ========================= ========= ============ ============ =============== =========================
        24384         4833            8         4014         4014          454 004              47            3            0            0            0            0            0 30572380   2025-09-02  12:12:15.0000 2025-09-02 16:33:03.0000  PM                 704        20001 ZUWIRDA

        24385         4833            8         4014         4014          454 004              47            1            0            0            0            0            0 30572381   2025-09-02  12:12:50.0000 2025-09-02 16:33:04.0000  PM                 704        20001 ZUWIRDA

          ID   SCANUSERID         OCID     WORKERID    CARRIERID      FIELDID TASKNO      RIPEBCH    UNRIPEBCH     BLACKBCH    ROTTENBCH LONGSTALKBCH    RATDMGBCH   LOOSEFRUIT TRANSNO      TRANSDATE     TRANSTIME            UPLOADDATETIME RECORDTAG  TRANSSTATUS    TRANSTYPE LASTUSER
=========== ============ ============ ============ ============ ============ ====== ============ ============ ============ ============ ============ ============ ============ ========== =========== ============= ========================= ========= ============ ============ =============== =========================
        24402         4833            8         4006         4006          454 011             105            4            0            0            0            0            0 30572412   2025-09-02  14:07:08.0000 2025-09-02 16:33:05.0000  XX                 705        20001 ZUWIRDA
SQL>"""

    print("Testing ISQL parsing with sample output that contains duplicate headers...")
    print("=" * 80)

    # Create connector instance (we won't actually connect to database)
    connector = FirebirdConnector("dummy_path.fdb")

    # Test parsing
    try:
        result = connector._parse_isql_output(sample_output, as_dict=True)

        print(f"\nParsing completed!")
        print(f"Found {len(result)} result sets")

        if result:
            result_set = result[0]
            headers = result_set.get('headers', [])
            rows = result_set.get('rows', [])

            print(f"Headers: {headers}")
            print(f"Total rows parsed: {len(rows)}")

            # Check for problematic rows
            problematic_rows = []
            for i, row in enumerate(rows):
                recordtag = row.get('RECORDTAG', '')
                transtype = row.get('TRANSTYPE', '')

                if recordtag in ['RECORDTAG', 'XX'] or transtype in ['RECORDTAG', 'XX']:
                    problematic_rows.append((i, row))

            if problematic_rows:
                print(f"\n[X] FOUND {len(problematic_rows)} PROBLEMATIC ROWS:")
                for i, row in problematic_rows[:5]:  # Show first 5
                    print(f"  Row {i}: RECORDTAG='{row.get('RECORDTAG')}', TRANSTYPE='{row.get('TRANSTYPE')}'")
            else:
                print(f"\n[OK] NO PROBLEMATIC ROWS FOUND - Parsing fix is working!")

            # Show sample good rows
            print(f"\nSample rows:")
            for i, row in enumerate(rows[:3]):
                print(f"  Row {i}: RECORDTAG='{row.get('RECORDTAG')}', TRANSTYPE='{row.get('TRANSTYPE')}', TRANSNO='{row.get('TRANSNO')}'")

        print("=" * 80)

    except Exception as e:
        print(f"[ERROR] PARSING FAILED: {e}")
        return False

    return len(problematic_rows) == 0

if __name__ == "__main__":
    success = test_parsing()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)