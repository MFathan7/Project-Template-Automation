import logging
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import ftp_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh FTP/SFTP Automation ===")
    
    # Ganti kredensial ini dengan server test tim kamu
    HOST = "test.rebex.net"  # Server SFTP dummy publik gratis
    USERNAME = "demo"
    PASSWORD = "password"
    PROTOCOL = "sftp"        # Ubah jadi "ftp" kalau server tujuan adalah FTP standar
    
    # =========================================================
    # 🌐 ACTIVITY: FTP Scope
    # =========================================================
    try:
        with ftp_utils.FTPScope(
            host=HOST, 
            username=USERNAME, 
            password=PASSWORD, 
            protocol=PROTOCOL
        ) as ftp_session:
            
            # --------------------------------------
            # 1. LIST FILES
            # --------------------------------------
            logger.info("\n--- TEST 1: Baca Isi Folder ---")
            daftar_file = ftp_session.get_files(".") # "." artinya root directory
            logger.info(f"Isi folder Root: {daftar_file}")
            
            # --------------------------------------
            # 2. DOWNLOAD FILE
            # --------------------------------------
            logger.info("\n--- TEST 2: Download File ---")
            # Kita coba download salah satu file dummy dari server rebex
            lokasi_simpan = "Data/Input/readme_sftp.txt"
            ftp_session.download_file(remote_path="readme.txt", local_path=lokasi_simpan)
            
            # Karena ini server public read-only, test upload/move/delete tidak bisa dijalankan
            # Namun kalau kamu punya server SFTP sendiri, kamu bisa membuang '#' di bawah ini
            
            """
            # --------------------------------------
            # 3. CREATE FOLDER & UPLOAD
            # --------------------------------------
            logger.info("\n--- TEST 3: Create Folder & Upload ---")
            ftp_session.create_folder("Folder_Bot")
            ftp_session.upload_file(local_path=lokasi_simpan, remote_path="Folder_Bot/hasil.txt")
            
            # --------------------------------------
            # 4. MOVE & DELETE
            # --------------------------------------
            logger.info("\n--- TEST 4: Move & Delete ---")
            ftp_session.move_file("Folder_Bot/hasil.txt", "Folder_Bot/hasil_lama.txt")
            ftp_session.delete_file("Folder_Bot/hasil_lama.txt")
            """

    except Exception as e:
        logger.error(f"Proses SFTP terhenti: {e}")

if __name__ == "__main__":
    main()