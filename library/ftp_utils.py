import logging
import os
import ftplib
import paramiko

logger = logging.getLogger(__name__)

class FTPScope:
    """
    Mendukung protokol 'ftp' (port 21) dan 'sftp' (port 22).
    """
    def __init__(self, host: str, username: str, password: str, port: int = None, protocol: str = "sftp"):
        self.host = host
        self.username = username
        self.password = password
        self.protocol = protocol.lower()
        
        # Auto-set port jika tidak diisi
        if port is None:
            self.port = 22 if self.protocol == "sftp" else 21
        else:
            self.port = port
            
        self.ftp = None          # Untuk FTP biasa
        self.sftp = None         # Untuk SFTP
        self.transport = None    # Bawaan paramiko untuk SFTP

    def connect(self):
        """Membuka koneksi ke server FTP/SFTP."""
        #logger.info(f"🌐 FTP SCOPE: Mengkoneksikan ke {self.host}:{self.port} via {self.protocol.upper()}...")
        try:
            if self.protocol == "sftp":
                self.transport = paramiko.Transport((self.host, self.port))
                self.transport.connect(username=self.username, password=self.password)
                self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            elif self.protocol == "ftp":
                self.ftp = ftplib.FTP()
                self.ftp.connect(self.host, self.port)
                self.ftp.login(self.username, self.password)
            else:
                raise ValueError("Protocol harus 'ftp' atau 'sftp'")
                
            #logger.info("   ↳ Koneksi berhasil ✅")
            return self
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal connect ke server: {e}")
            raise

    def disconnect(self):
        """Menutup koneksi."""
        #logger.info("🛑 FTP SCOPE: Menutup koneksi server.")
        if self.sftp:
            self.sftp.close()
            self.sftp = None
        if self.transport:
            self.transport.close()
            self.transport = None
        if self.ftp:
            self.ftp.quit()
            self.ftp = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # ==========================================
    # FTP ACTIVITIES
    # ==========================================

    def upload_file(self, local_path: str, remote_path: str):
        #logger.info(f"📤 FTP UPLOAD: Mengunggah '{os.path.basename(local_path)}' ke '{remote_path}'")
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"File lokal tidak ditemukan: {local_path}")

        try:
            if self.protocol == "sftp":
                self.sftp.put(local_path, remote_path)
            elif self.protocol == "ftp":
                with open(local_path, 'rb') as f:
                    self.ftp.storbinary(f'STOR {remote_path}', f)
            #logger.info("   ↳ Upload berhasil ✅")
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal upload: {e}")
            raise

    def download_file(self, remote_path: str, local_path: str):
        #logger.info(f"📥 FTP DOWNLOAD: Mengunduh '{remote_path}' ke '{local_path}'")
        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)

        try:
            if self.protocol == "sftp":
                self.sftp.get(remote_path, local_path)
            elif self.protocol == "ftp":
                with open(local_path, 'wb') as f:
                    self.ftp.retrbinary(f'RETR {remote_path}', f.write)
            #logger.info("   ↳ Download berhasil ✅")
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal download: {e}")
            raise

    def get_files(self, remote_folder: str = ".") -> list:
        #logger.info(f"📁 FTP GET FILES: Membaca isi folder '{remote_folder}'")
        try:
            if self.protocol == "sftp":
                files = self.sftp.listdir(remote_folder)
                # Filter agar mengembalikan array nama
                #logger.info(f"   ↳ Ditemukan {len(files)} item ✅")
                return files
            elif self.protocol == "ftp":
                files = self.ftp.nlst(remote_folder)
                #logger.info(f"   ↳ Ditemukan {len(files)} item ✅")
                return files
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal membaca folder: {e}")
            raise

    def create_folder(self, remote_folder: str):
        #logger.info(f"📁 FTP CREATE FOLDER: Membuat folder '{remote_folder}'")
        try:
            if self.protocol == "sftp":
                self.sftp.mkdir(remote_folder)
            elif self.protocol == "ftp":
                self.ftp.mkd(remote_folder)
            #logger.info("   ↳ Pembuatan folder berhasil ✅")
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal membuat folder: {e}")
            raise

    def move_file(self, source_path: str, dest_path: str):
        """Bisa dipakai untuk rename file juga."""
        #logger.info(f"🚚 FTP MOVE: Memindahkan '{source_path}' ke '{dest_path}'")
        try:
            if self.protocol == "sftp":
                self.sftp.rename(source_path, dest_path)
            elif self.protocol == "ftp":
                self.ftp.rename(source_path, dest_path)
            #logger.info("   ↳ Pemindahan berhasil ✅")
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal memindahkan file: {e}")
            raise

    def delete_file(self, remote_path: str):
        #logger.info(f"🗑️ FTP DELETE: Menghapus file '{remote_path}'")
        try:
            if self.protocol == "sftp":
                self.sftp.remove(remote_path)
            elif self.protocol == "ftp":
                self.ftp.delete(remote_path)
            #logger.info("   ↳ Penghapusan berhasil ✅")
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal menghapus file: {e}")
            raise