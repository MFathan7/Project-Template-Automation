import logging
import pandas as pd
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import excel_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh Excel Automation ===")
    
    file_excel = "Data_Test.xlsx"
    
    # Siapkan data dummy menggunakan Pandas (pengganti Build DataTable)
    data_karyawan = pd.DataFrame({
        "ID": ["K001", "K002", "K003"],
        "Nama": ["Budi", "Siti", "Andi"],
        "Status": ["Aktif", "Cuti", "Aktif"]
    })
    
    # ==========================================
    # 🟢 ACTIVITY: Excel Application Scope
    # ==========================================
    with excel_utils.ExcelApplicationScope(
        file_path=file_excel, 
        visible=True,           # Set True untuk melihat Excel terbuka, False untuk background
        create_new_file=True,   # Otomatis buat file jika belum ada
        save_changes=True       # Otomatis save saat selesai
    ) as excel_scope:
        
        # --------------------------------------
        # ✍️ ACTIVITY: Write Range
        # --------------------------------------
        logger.info("Menulis data ke sheet 'HR_Data'...")
        excel_scope.write_range(
            sheet_name="HR_Data",
            data=data_karyawan,
            start_cell="A1",
            add_headers=True
        )
        
        # --------------------------------------
        # 📥 ACTIVITY: Read Range (Full / Auto Expand)
        # --------------------------------------
        logger.info("Membaca kembali data dari sheet 'HR_Data' mulai dari A1...")
        df_hasil = excel_scope.read_range(
            sheet_name="HR_Data",
            range_address="A1",
            has_headers=True
        )
        
        # Tampilkan hasil bacaan di terminal
        logger.info("\nData (Auto Expand A1):")
        print(df_hasil.to_string(index=False))

        # --------------------------------------
        # 📥 ACTIVITY: Read Range (Spesifik Kotak)
        # --------------------------------------
        logger.info("Membaca spesifik range 'A1:B2'...")
        df_spesifik = excel_scope.read_range(
            sheet_name="HR_Data",
            range_address="A1:B2", # Hanya baca sampai baris 2, kolom B
            has_headers=True
        )
        logger.info("\nData (Spesifik A1:B2):")
        print(df_spesifik.to_string(index=False))

if __name__ == "__main__":
    main()