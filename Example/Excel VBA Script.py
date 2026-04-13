import logging
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import excel_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh Invoke VBA (Macro) ===")
    
    # Pastikan path mengarah ke file .xlsm yang sudah kamu buat
    file_macro = "Data/MacroTest.xlsm" 
    
    if not os.path.exists(file_macro):
        logger.error(f"❌ File {file_macro} tidak ditemukan! Buat dulu filenya sesuai instruksi.")
        return

    # ==========================================
    # 🟢 ACTIVITY: Excel Application Scope
    # ==========================================
    with excel_utils.ExcelApplicationScope(
        file_path=file_macro, 
        visible=True,           # Set True agar kelihatan prosesnya
        create_new_file=False,  
        save_changes=True       
    ) as excel_scope:
        
        # --------------------------------------
        # ⚙️ 1. Panggil Function VBA (Return Value)
        # --------------------------------------
        logger.info("\n--- Test 1: Function VBA dengan Return Value ---")
        # Melempar 3 parameter: Nama (String), Gaji (Double), Persentase (Double)
        hasil_kalkulasi = excel_scope.invoke_vba("KalkulasiBonus", "Budi Santoso", 5000000, 15)
        logger.info(f"Menerima balasan dari Macro: {hasil_kalkulasi}")
        
        # --------------------------------------
        # ⚙️ 2. Panggil Sub VBA (Action ke Cell)
        # --------------------------------------
        logger.info("\n--- Test 2: Sub VBA menulis ke Excel ---")
        # Pastikan Sheet1 ada di file Excel kamu
        teks_input = f"Laporan Otomatis: {hasil_kalkulasi}"
        excel_scope.invoke_vba("TulisLaporan", "Sheet1", teks_input)
        
        # --------------------------------------
        # 🔍 3. Validasi (Read Cell)
        # --------------------------------------
        logger.info("\n--- Test 3: Membaca hasil tulisan Macro ---")
        nilai_cell = excel_scope.read_cell("Sheet1", "A1")
        logger.info(f"Isi Cell A1 sekarang adalah: '{nilai_cell}'")

if __name__ == "__main__":
    main()