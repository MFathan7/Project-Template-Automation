import logging
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import web_utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def sequence_a_buka_web(browser_app: web_utils.UseApplicationBrowserAsync) -> any:
    """Sequence A bertugas hanya membuka web dan mereturn object page."""
    logger.info("\n▶️ SEQUENCE A: Buka Browser")
    # Membuka browser secara manual (tanpa 'with')
    web_page = await browser_app.open()
    return web_page

async def sequence_b_proses_login(web_page):
    """Sequence B menerima variabel 'web_page' dari A, dan langsung mengeksekusi login."""
    logger.info("\n▶️ SEQUENCE B: Proses Login (Reuse Browser)")
    
    await web_utils.type_into(web_page, "#username", "student", log_name="Username Field")
    await web_utils.type_into(web_page, "#password", "Password123", log_name="Password Field")
    await web_utils.click(web_page, "#submit", log_name="Login Button")
    
    is_success = await web_utils.element_exists(web_page, ".post-title", timeout=5000)
    if is_success:
        logger.info("✅ Login Berhasil di Sequence B!")

async def sequence_c_inject_js(web_page):
    """Sequence C menerima variabel 'web_page' dan mengeksekusi custom JS."""
    logger.info("\n▶️ SEQUENCE C: Inject JS Script")
    
    # Contoh 1: JS Sederhana tanpa kembalian (Ubah background web jadi merah)
    js_merah = "document.body.style.backgroundColor = 'red';"
    await web_utils.inject_js_script(web_page, js_merah, log_name="Ubah BG Merah")
    await asyncio.sleep(2) # Jeda agar kamu bisa lihat efeknya
    
    # Contoh 2: JS Kompleks pakai parameter dan return value
    js_hitung = """(angkaDariPython) => {
        let hasil = angkaDariPython * 10;
        return "Hasil perkalian di browser: " + hasil;
    }"""
    
    hasil_js = await web_utils.inject_js_script(
        page=web_page, 
        script_code=js_hitung, 
        arg=5, # Melempar angka 5 ke dalam JavaScript!
        log_name="Hitung Perkalian JS"
    )
    logger.info(f"Kembalian dari JavaScript: {hasil_js}")

async def main():
    logger.info("=== Memulai Contoh Web Automation (Passing Browser) ===")
    
    # Inisialisasi Aplikasi (Jangan ditaruh di dalam 'with' jika ingin passing antar fungsi)
    browser_app = web_utils.UseApplicationBrowserAsync(
        url="https://practicetestautomation.com/practice-test-login/",
        headless=False
    )
    
    try:
        # 1. Buka di Sequence A
        page_aktif = await sequence_a_buka_web(browser_app)
        
        # 2. Oper ke Sequence B
        await sequence_b_proses_login(page_aktif)
        
        # 3. Oper ke Sequence C (Test JS)
        await sequence_c_inject_js(page_aktif)
        
    except Exception as e:
        logger.error(f"Terjadi error: {e}")
    finally:
        # Wajib di-close di finally agar browser tidak nyangkut saat error
        await browser_app.close()
        logger.info("\n=== Proses Selesai ===")

if __name__ == "__main__":
    asyncio.run(main())