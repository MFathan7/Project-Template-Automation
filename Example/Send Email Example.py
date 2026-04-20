import logging
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import mail_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh Pengiriman Email (SMTP) ===")
    
    # ⚠️ PERHATIAN PENTING SEBELUM RUN:
    # 1. Jangan gunakan password akun aslimu jika kamu mengaktifkan 2FA (Two-Factor Auth).
    # 2. Gunakan "App Passwords" (Sandi Aplikasi).
    #    - Gmail: Manage Google Account -> Security -> 2-Step Verification -> App Passwords.
    #    - Microsoft/Outlook: Security -> Advanced security options -> App passwords.
    
    # Konfigurasi Server (Contoh pakai Gmail, ganti smtp.office365.com untuk Outlook)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_SENDER = "emailkamu@gmail.com"  # Ganti dengan emailmu
    EMAIL_PASSWORD = "app_password_kamu_di_sini" # Ganti dengan App Password
    
    EMAIL_RECEIVER = "email.tujuan@domain.com"
    
    # =========================================================
    # TEST 1: EMAIL TEKS BIASA
    # =========================================================
    logger.info("\n--- TEST 1: Kirim Email Teks ---")
    try:
        mail_utils.send_smtp_mail(
            server=SMTP_SERVER,
            port=SMTP_PORT,
            username=EMAIL_SENDER,
            password=EMAIL_PASSWORD,
            to_email=EMAIL_RECEIVER,
            subject="[RPA] Notifikasi Bot Sukses 🤖",
            body="Halo!\n\nRobot berhasil memproses 100 data hari ini tanpa error.\n\nSalam,\nPython REFramework Bot"
        )
    except Exception as e:
        logger.error(f"Test 1 Gagal: {e}")

    # =========================================================
    # TEST 2: EMAIL HTML + ATTACHMENT
    # =========================================================
    logger.info("\n--- TEST 2: Kirim Email HTML + Attachment ---")
    
    # Siapkan file dummy untuk dilampirkan
    dummy_file = "Data/Report_Akhir.txt"
    os.makedirs(os.path.dirname(dummy_file), exist_ok=True)
    with open(dummy_file, "w") as f:
        f.write("Ini adalah laporan akhir hasil scrape bot hari ini.")
        
    html_body = """
    <html>
        <body>
            <h2 style="color: green;">Proses Berhasil Selesai! 🎉</h2>
            <p>Berikut adalah rincian proses hari ini:</p>
            <table border="1" cellpadding="5">
                <tr><th>Status</th><th>Jumlah</th></tr>
                <tr><td>Sukses</td><td>45</td></tr>
                <tr><td>Gagal</td><td>2</td></tr>
            </table>
            <br>
            <p>Lengkapnya bisa dicek pada file terlampir.</p>
        </body>
    </html>
    """
    
    try:
        mail_utils.send_smtp_mail(
            server=SMTP_SERVER,
            port=SMTP_PORT,
            username=EMAIL_SENDER,
            password=EMAIL_PASSWORD,
            to_email=[EMAIL_RECEIVER], # Bisa berupa list jika penerima lebih dari satu
            subject="[RPA] Daily Report dengan Attachment 📊",
            body=html_body,
            is_html=True,
            attachments=[dummy_file]
        )
    except Exception as e:
        logger.error(f"Test 2 Gagal: {e}")

if __name__ == "__main__":
    main()