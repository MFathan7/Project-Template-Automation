import logging
import random
import asyncio
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library.retry_utils import retry_scope

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 1. CONTOH UNTUK FUNGSI BIASA (SYNC)
# ==========================================

# Cukup tempelkan decorator ini! Jika gagal, akan diulang max 3 kali dengan jeda 2 detik.
@retry_scope(max_attempts=3, delay_seconds=2)
def download_laporan_api():
    logger.info("Mencoba mendownload laporan dari API...")
    
    # Simulasi API kadang error (peluang sukses cuma 30%)
    if random.random() < 0.7:
        raise ConnectionError("Server API sedang sibuk (Simulasi Error)!")
        
    logger.info("✅ Laporan berhasil didownload!")
    return "DataLaporan_2024.pdf"


# ==========================================
# 2. CONTOH UNTUK FUNGSI ASYNC (WEB)
# ==========================================

# Kita bisa atur spesifik error apa yang mau di-retry
@retry_scope(max_attempts=4, delay_seconds=1, exceptions=(TimeoutError,))
async def klik_tombol_web():
    logger.info("Mencari tombol 'Submit' di halaman web...")
    await asyncio.sleep(0.5) # Simulasi loading web
    
    # Simulasi elemen web telat muncul (peluang sukses 20%)
    if random.random() < 0.8:
        raise TimeoutError("Elemen '#btn-submit' tidak ditemukan dalam 5 detik (Simulasi)!")
        
    logger.info("✅ Tombol Submit berhasil diklik!")
    return True


# ==========================================
# MAIN EXECUTION
# ==========================================
async def main():
    logger.info("=== Memulai Contoh Auto-Retry Scope ===")
    
    logger.info("\n--- TEST 1: Fungsi Sync (API/Database) ---")
    try:
        hasil = download_laporan_api()
        logger.info(f"Hasil Eksekusi: {hasil}")
    except Exception as e:
        logger.error(f"Gagal total setelah semua percobaan: {e}")
        
    logger.info("\n--- TEST 2: Fungsi Async (Web Automation) ---")
    try:
        await klik_tombol_web()
    except Exception as e:
        logger.error(f"Gagal total setelah semua percobaan: {e}")

if __name__ == "__main__":
    asyncio.run(main())