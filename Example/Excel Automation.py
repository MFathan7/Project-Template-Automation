import logging, sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import excel_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh Invoke VBA (Macro) ===")
    
    # Konfigurasi Path
    base_dir = os.path.dirname(__file__) # Path folder 'Example'
    file_macro = os.path.abspath(os.path.join(base_dir, "Data", "MacroTest.xlsm"))
    file_vbs = os.path.abspath(os.path.join(base_dir, "Data", "export_pdf.vbs"))
    file_pdf_hasil = os.path.abspath(os.path.join(base_dir, "Data", "Hasil_Laporan.pdf"))

    
    if not os.path.exists(file_macro):
        logger.error(f"❌ File {file_macro} tidak ditemukan! Buat dulu filenya sesuai instruksi sebelumnya.")
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
        hasil_kalkulasi = excel_scope.invoke_vba("KalkulasiBonus", "Budi Santoso", 5000000, 15)
        logger.info(f"Menerima balasan dari Macro: {hasil_kalkulasi}")
        
        # --------------------------------------
        # ⚙️ 2. Panggil Sub VBA (Action ke Cell)
        # --------------------------------------
        logger.info("\n--- Test 2: Sub VBA menulis ke Excel ---")
        teks_input = f"Laporan Otomatis: {hasil_kalkulasi}"
        excel_scope.invoke_vba("TulisLaporan", "Sheet1", teks_input)
        
        # --------------------------------------
        # 🔍 3. Validasi (Read Cell)
        # --------------------------------------
        logger.info("\n--- Test 3: Membaca hasil tulisan Macro ---")
        nilai_cell = excel_scope.read_cell("Sheet1", "A1")
        logger.info(f"Isi Cell A1 sekarang adalah: '{nilai_cell}'")

        # --------------------------------------
        # 💉 4. Test Inject Script VBS (Ekspor PDF)
        # --------------------------------------
        logger.info("\n--- Test 4: Invoke VBA From File (Ekspor PDF) ---")
        
        
        try:
            excel_scope.invoke_vba_from_file(
                file_vbs,           # Parameter 1: vba_file_path
                "ExportToPDF",      # Parameter 2: entry_method
                file_pdf_hasil      # Parameter 3 dan seterusnya akan otomatis masuk ke *args (argumen VBA)
            )
            logger.info(f"✅ Sukses! File PDF berhasil di-generate di: {file_pdf_hasil}")
        except Exception as e:
            logger.error(f"Gagal melakukan Ekspor PDF. Sudah centang 'Trust access to VBA' di Excel? Error: {e}")

if __name__ == "__main__":
    main()