import logging
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import onedrive_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh Otomatisasi OneDrive (Mode Interactive) ===")
    
    # =====================================================================
    # 💡 CARA CEPAT (Tanpa Minta Tolong IT):
    # 1. Buka portal.azure.com -> Microsoft Entra ID -> App registrations -> New registration.
    # 2. Nama bebas. "Supported account types" pilih opsi ke-3 (Any organizational directory and personal Microsoft accounts).
    # 3. Pada menu "Authentication", klik "Add a platform" -> pilih "Web".
    # 4. Masukkan Redirect URI: https://login.microsoftonline.com/common/oauth2/nativeclient
    # 5. Ke "Certificates & secrets", buat New client secret.
    # =====================================================================
    
    CLIENT_ID = "masukkan-client-id-aplikasi-azure-kamu-disini"
    CLIENT_SECRET = "masukkan-client-secret-kamu-disini"
    
    if CLIENT_ID.startswith("masukkan"):
        logger.warning("Silakan isi CLIENT_ID dan CLIENT_SECRET terlebih dahulu di script ini!")
        return

    # =========================================================
    # ☁️ ACTIVITY: OneDrive Scope (Interactive Mode)
    # =========================================================
    try:
        # Kita set auth_type ke "interactive" (Tidak perlu TENANT_ID)
        with onedrive_utils.OneDriveScope(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET,
            auth_type="interactive" 
        ) as od:
            
            # --------------------------------------
            # 1. UPLOAD FILE
            # --------------------------------------
            logger.info("\n--- TEST 1: Upload File ---")
            
            file_lokal = "Data/Output/Laporan_OneDrive.txt"
            os.makedirs(os.path.dirname(file_lokal), exist_ok=True)
            with open(file_lokal, "w") as f:
                f.write("Laporan ini di-generate oleh Python RPA dan diupload ke OneDrive (Interactive Mode)!")
                
            od.upload_file(local_file_path=file_lokal, cloud_folder_path="/Laporan_Bot")
            
            # --------------------------------------
            # 2. LIST & DOWNLOAD
            # --------------------------------------
            logger.info("\n--- TEST 2: Baca Isi & Download ---")
            daftar_file = od.get_file_list(cloud_folder_path="/Laporan_Bot")
            logger.info(f"Isi folder OneDrive: {daftar_file}")
            
            od.download_file(
                cloud_file_path="/Laporan_Bot/Laporan_OneDrive.txt", 
                local_download_folder="Data/Input/"
            )
            
    except Exception as e:
        logger.error(f"Proses OneDrive terhenti: {e}")

if __name__ == "__main__":
    main()