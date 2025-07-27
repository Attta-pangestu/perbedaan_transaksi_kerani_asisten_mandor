"""
Script untuk menguji koneksi ke database Firebird.
"""
import argparse
from firebird_connector import FirebirdConnector

def main():
    """
    Fungsi utama untuk menguji koneksi database.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Uji koneksi ke database Firebird.')
    parser.add_argument('--db-path', type=str, 
                        default="D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\PTRJ_P1A_08042025\\PTRJ_P1A.FDB",
                        help='Path ke file database Firebird')
    parser.add_argument('--isql-path', type=str, 
                        default="C:\\Program Files (x86)\\Firebird\\Firebird_1_5\\bin\\isql.exe",
                        help='Path ke executable isql')
    parser.add_argument('--username', type=str, default='sysdba', help='Username database')
    parser.add_argument('--password', type=str, default='masterkey', help='Password database')
    parser.add_argument('--use-localhost', action='store_true',
                        help='Gunakan format localhost:path untuk koneksi')
    
    args = parser.parse_args()
    
    print("=== Uji Koneksi Database Firebird ===")
    print(f"Database path: {args.db_path}")
    print(f"ISQL path: {args.isql_path}")
    print(f"Username: {args.username}")
    print(f"Use localhost: {args.use_localhost}")
    
    # Inisialisasi koneksi database
    connector = FirebirdConnector(
        db_path=args.db_path,
        username=args.username,
        password=args.password,
        isql_path=args.isql_path,
        use_localhost=args.use_localhost
    )
    
    # Tes koneksi
    print("\nMenguji koneksi database...")
    if connector.test_connection():
        print("✓ Koneksi berhasil!")
        
        # Coba dapatkan daftar tabel
        print("\nMendapatkan daftar tabel...")
        tables = connector.get_tables()
        if tables:
            print(f"Ditemukan {len(tables)} tabel:")
            for i, table in enumerate(tables[:10], 1):
                print(f"  {i}. {table}")
            if len(tables) > 10:
                print(f"  ... dan {len(tables) - 10} tabel lainnya")
        else:
            print("Tidak dapat mendapatkan daftar tabel.")
        
        # Coba jalankan query contoh
        print("\nMenjalankan query contoh...")
        example_table = tables[0] if tables else "FFBSCANNERDATA04"
        example_query = f"SELECT FIRST 5 * FROM {example_table}"
        try:
            result = connector.execute_query(example_query)
            if result and result[0]["rows"]:
                print(f"Query berhasil! Ditemukan {len(result[0]['rows'])} baris.")
                print("Contoh data:")
                for i, row in enumerate(result[0]["rows"][:3], 1):
                    print(f"  Baris {i}: {row}")
            else:
                print("Query berhasil tetapi tidak ada data yang ditemukan.")
        except Exception as e:
            print(f"Error menjalankan query: {e}")
    else:
        print("✗ Koneksi gagal!")
        print("\nSaran troubleshooting:")
        print("1. Pastikan path database dan isql benar")
        print("2. Coba gunakan opsi --use-localhost untuk format koneksi alternatif")
        print("3. Periksa apakah username dan password benar")
        print("4. Pastikan database tidak sedang digunakan oleh aplikasi lain")
        print("5. Periksa apakah Firebird server berjalan")

if __name__ == "__main__":
    main()
