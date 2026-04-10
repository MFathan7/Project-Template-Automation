import logging
import pandas as pd
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import datatable_utils, path_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh DataTable & File/Folder Automation ===")
    
    # =========================================================
    # 1. CONTOH FILE & FOLDER MANAGEMENT
    # =========================================================
    logger.info("\n--- BAGIAN 1: FOLDER & FILE MANAGEMENT ---")
    temp_folder = "Data/Temp_Example"
    
    # 📁 Create Folder
    path_utils.create_folder(temp_folder)
    
    # 👁️ Cek Path Exists
    is_exists = path_utils.path_exists(temp_folder)
    logger.info(f"Apakah folder '{temp_folder}' berhasil dibuat? {is_exists}")
    
    # Bikin file teks dummy untuk dicopy
    dummy_file = os.path.join(temp_folder, "dummy.txt")
    with open(dummy_file, "w") as f:
        f.write("Halo, ini file dummy!")
        
    # 📄 Copy File
    copy_file_path = os.path.join(temp_folder, "dummy_copy.txt")
    path_utils.copy_file(dummy_file, copy_file_path)

    # =========================================================
    # 2. CONTOH DATATABLE MANAGEMENT
    # =========================================================
    logger.info("\n--- BAGIAN 2: DATATABLE MANAGEMENT ---")
    
    # Buat Build DataTable awal (Data Dummy)
    dt_karyawan = pd.DataFrame({
        "ID": ["K001", "K002", "K003", "K004"],
        "Nama": ["Budi", "Siti", "Andi", "Ratna"],
        "Status": ["Aktif", "Cuti", "Aktif", "Resign"],
        "Gaji": [5000, 6000, 4500, 5500]
    })
    logger.info("Tabel Awal:\n" + dt_karyawan.to_string(index=False))
    
    # 🗃️ Filter DataTable (Gaji > 4500)
    dt_filtered = datatable_utils.filter_datatable(dt_karyawan, "Gaji", ">", 4500)
    logger.info("\nTabel setelah difilter (Gaji > 4500):\n" + dt_filtered.to_string(index=False))
    
    # 🗃️ Sort DataTable (Berdasarkan Gaji Descending)
    dt_sorted = datatable_utils.sort_datatable(dt_filtered, "Gaji", ascending=False)
    logger.info("\nTabel setelah disortir (Gaji Descending):\n" + dt_sorted.to_string(index=False))
    
    # 🗃️ Add Data Row (Tambah Karyawan Baru)
    dt_sorted = datatable_utils.add_data_row(dt_sorted, ["K005", "Joko", "Aktif", 7000])
    logger.info("\nTabel setelah ditambah 'Joko':\n" + dt_sorted.to_string(index=False))
    
    # 🗃️ Remove Data Row (Hapus baris index ke-0 / Paling atas)
    dt_sorted = datatable_utils.remove_data_row(dt_sorted, row_index=0)
    logger.info("\nTabel setelah menghapus index 0:\n" + dt_sorted.to_string(index=False))
    
    # 🗃️ Merge DataTable (Gabung tabel lain)
    dt_tambahan = pd.DataFrame({
        "ID": ["K006"], "Nama": ["Dewi"], "Status": ["Aktif"], "Gaji": [8000]
    })
    dt_merged = datatable_utils.merge_datatable(dt_sorted, dt_tambahan)
    logger.info("\nTabel setelah di-merge dengan data baru ('Dewi'):\n" + dt_merged.to_string(index=False))
    
    # 🗃️ Clear DataTable
    dt_cleared = datatable_utils.clear_datatable(dt_merged)
    logger.info("\nTabel setelah di-clear (Kosong tapi header utuh):\n" + dt_cleared.to_string(index=False))

    # =========================================================
    # 3. CLEAN UP FOLDER
    # =========================================================
    logger.info("\n--- BAGIAN 3: CLEAN UP ---")
    
    # 🗑️ Delete Folder beserta isinya
    path_utils.delete_folder(temp_folder)
    logger.info(f"Folder '{temp_folder}' telah dihapus untuk mengembalikan state semula.")

if __name__ == "__main__":
    main()