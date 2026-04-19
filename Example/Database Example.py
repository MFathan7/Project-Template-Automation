import logging
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import database_utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# SIMULASI WORKFLOW / SEQUENCE TERPISAH
# ==========================================

def sequence_a_setup_data(db_connect: database_utils.DatabaseScope):
    """
    Menerima argumen db_connect dan melakukan Insert.
    """
    logger.info("\n▶️ MASUK KE SEQUENCE A (Setup Data)")
    dt_karyawan = pd.DataFrame({
        "ID": ["K001", "K002", "K003"],
        "Nama": ["Budi", "Siti", "Andi"],
        "Departemen": ["IT", "Finance", "IT"],
        "Gaji": [8000, 7500, 6000]
    })
    # Langsung pakai variabel db_connect tanpa perlu connect ulang
    db_connect.insert_datatable("Karyawan", dt_karyawan, behavior="replace")


def sequence_b_proses_data(db_connect: database_utils.DatabaseScope):
    """
    Menerima argumen db_connect dan melakukan Query & Update.
    """
    logger.info("\n▶️ MASUK KE SEQUENCE B (Proses Data)")
    
    # Run Query
    query_select = "SELECT * FROM Karyawan WHERE Departemen = :dept"
    dt_hasil = db_connect.run_query(query_select, {"dept": "IT"})
    logger.info(f"Hasil Query (Anak IT):\n{dt_hasil.to_string(index=False)}")
    
    # Update Data
    query_update = "UPDATE Karyawan SET Gaji = :gaji_baru WHERE ID = :id_karyawan"
    db_connect.execute_non_query(query_update, {"gaji_baru": 9900, "id_karyawan": "K001"})

def sequence_c_bulk_update(db_connect: database_utils.DatabaseScope):
    """
    Menerima argumen db_connect dan melakukan Bulk Update Massal.
    """
    logger.info("\n▶️ MASUK KE SEQUENCE C (Bulk Update)")
    
    # Simulasi DataTable baru (Misal hasil scrape web / baca dari Excel)
    dt_update = pd.DataFrame({
        "ID": ["K002", "K003"],      # Kunci pencarian (match_columns)
        "Departemen": ["HR", "HR"],  # Nilai yang mau diubah
        "Gaji": [8000, 8500]         # Nilai yang mau diubah
    })
    
    logger.info(f"Data yang akan di-bulk update:\n{dt_update.to_string(index=False)}")
    
    # 🔄 ACTIVITY: Bulk Update
    baris_terdampak = db_connect.bulk_update(
        table_name="Karyawan", 
        data=dt_update, 
        match_columns=["ID"]
    )
    
    # Cek hasil akhir tabel di Database untuk memastikan
    dt_final = db_connect.run_query("SELECT * FROM Karyawan")
    logger.info(f"Tabel Karyawan Final Setelah Bulk Update:\n{dt_final.to_string(index=False)}")

def main():
    logger.info("=== Contoh Database Connection ===")

    # 1. Inisialisasi Objek DB
    db_obj = database_utils.DatabaseScope(db_type="sqlserver", server="...", username=",,,,", password=",,,", database=',,,')
    
    try:
        # 2. Activity: CONNECT DATABASE (Menghasilkan variabel aktif)
        db_obj.connect()
        
        # 3. Lempar variabel ke Sequence A
        sequence_a_setup_data(db_connect=db_obj)
        
        # 4. Lempar variabel ke Sequence B
        sequence_b_proses_data(db_connect=db_obj)

        # 5. Lempar variabel ke Sequence C (Test Bulk Update)
        sequence_c_bulk_update(db_connect=db_obj)
        
    except Exception as e:
        logger.error(f"Terjadi error pada proses utama: {e}")
    finally:
        # 5. Activity: DISCONNECT DATABASE (Wajib ditaruh di finally agar selalu tereksekusi)
        db_obj.disconnect()
        logger.info("\n=== Proses Selesai ===")

if __name__ == "__main__":
    main()