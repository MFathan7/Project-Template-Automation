import logging
import os
from O365 import Account

logger = logging.getLogger(__name__)

class OneDriveScope:
    """
    Context manager untuk OneDrive.
    Mendukung dua mode:
    1. 'interactive' (Attended): Login manual via browser satu kali, token disimpan di .txt. (Gak butuh IT Admin)
    2. 'unattended' (App-Only): Tanpa interaksi, tapi butuh persetujuan (Admin Consent) dari tim IT.
    """
    def __init__(self, client_id: str, client_secret: str, tenant_id: str = "", auth_type: str = "interactive"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.auth_type = auth_type.lower()
        self.account = None
        self.storage = None
        self.drive = None

    def connect(self):
        """Membuka koneksi ke Microsoft Graph API."""
        logger.info(f"☁️ ONEDRIVE SCOPE: Connect menggunakan mode '{self.auth_type}'...")
        try:
            credentials = (self.client_id, self.client_secret)
            
            if self.auth_type == "unattended":
                # Mode 1: Unattended (Wajib Tenant ID & Admin Consent IT)
                self.account = Account(credentials, auth_flow='client_credentials', tenant_id=self.tenant_id)
                if not self.account.authenticate():
                    raise PermissionError("Otentikasi gagal. Pastikan sudah di-Grant Admin oleh IT di Azure.")
                    
            elif self.auth_type == "interactive":
                # Mode 2: Interactive (Mirip UiPath, login via Browser)
                # Secara otomatis menyimpan dan membaca 'o365_token.txt' di folder jalannya script
                self.account = Account(credentials)
                if not self.account.is_authenticated:
                    logger.info("⚠️ Token belum ada atau kadaluarsa.")
                    logger.info("👇 SILAKAN COPY LINK DI BAWAH INI KE BROWSER, LOGIN, LALU PASTE URL HASILNYA KEMBALI KE TERMINAL 👇")
                    # Scopes khusus untuk baca-tulis file
                    self.account.authenticate(scopes=['basic', 'onedrive_all'])
                    logger.info("✅ Login berhasil! Token disimpan ke 'o365_token.txt'. Bot tidak akan meminta login lagi selama token valid.")

            logger.info("   ↳ Otentikasi Microsoft Graph berhasil ✅")
            self.storage = self.account.storage()
            self.drive = self.storage.get_default_drive()
            return self
            
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal connect OneDrive: {e}")
            raise

    def disconnect(self):
        """Membersihkan sesi (Token di txt tetap aman untuk run berikutnya)."""
        logger.info("🛑 ONEDRIVE SCOPE: Sesi OneDrive diakhiri.")
        self.account = None
        self.storage = None
        self.drive = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # ==========================================
    # ☁️ ONEDRIVE ACTIVITIES
    # ==========================================

    def upload_file(self, local_file_path: str, cloud_folder_path: str = ""):
        """Upload file ke OneDrive."""
        logger.info(f"📤 UPLOAD ONEDRIVE: Mengunggah '{os.path.basename(local_file_path)}' ke cloud...")
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File lokal tidak ditemukan: {local_file_path}")

        try:
            if cloud_folder_path == "" or cloud_folder_path == "/":
                target_folder = self.drive.get_root_folder()
            else:
                target_folder = self.drive.get_item_by_path(cloud_folder_path)
                
            target_folder.upload_file(local_file_path)
            logger.info(f"   ↳ Upload berhasil ✅ ke '{cloud_folder_path if cloud_folder_path else 'Root'}'")
            
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal upload ke OneDrive: {e}")
            raise

    def download_file(self, cloud_file_path: str, local_download_folder: str):
        """Download file dari OneDrive."""
        logger.info(f"📥 DOWNLOAD ONEDRIVE: Mengunduh '{cloud_file_path}' ke '{local_download_folder}'")
        os.makedirs(local_download_folder, exist_ok=True)

        try:
            file_item = self.drive.get_item_by_path(cloud_file_path)
            if file_item.is_folder:
                raise ValueError(f"Path '{cloud_file_path}' adalah sebuah folder, bukan file!")
                
            file_item.download(local_download_folder)
            logger.info("   ↳ Download berhasil ✅")
            
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal download dari OneDrive: {e}")
            raise

    def get_file_list(self, cloud_folder_path: str = "") -> list:
        """Daftar isi file di dalam folder OneDrive."""
        logger.info(f"📁 GET FILES ONEDRIVE: Membaca isi folder '{cloud_folder_path if cloud_folder_path else 'Root'}'")
        try:
            if cloud_folder_path == "" or cloud_folder_path == "/":
                target_folder = self.drive.get_root_folder()
            else:
                target_folder = self.drive.get_item_by_path(cloud_folder_path)
                
            items = target_folder.get_items()
            file_list = [item.name for item in items if item.is_file]
            
            logger.info(f"   ↳ Ditemukan {len(file_list)} file ✅")
            return file_list
            
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal membaca folder OneDrive: {e}")
            raise