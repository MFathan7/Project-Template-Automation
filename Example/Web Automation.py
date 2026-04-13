import logging
import asyncio
import sys
import os
from time import sleep
import pandas as pd

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import web_utils

# Setup Logging agar output terminal terlihat rapi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("=== Memulai Contoh Web Automation ===")
    
    # ==========================================
    # ACTIVITY: Use Application/Browser
    # ==========================================
    async with web_utils.UseApplicationBrowserAsync(
        url="https://practicetestautomation.com/practice-test-login/", 
        headless=False,        # Ubah ke True jika tidak ingin melihat browser terbuka
        close_on_exit=True     # Set False jika ingin browser tetap terbuka setelah selesai
    ) as web_page:
        
        logger.info("Sedang mengisi form login...")
        
        # ACTIVITY: Type Into
        await web_utils.type_into(web_page, "#username", "student", log_name="Username Field")
        await web_utils.type_into(web_page, "#password", "Password123", log_name="Password Field")
        
        # ACTIVITY: Click
        await web_utils.click(web_page, "#submit", log_name="Login Button")
        
        # ACTIVITY: Element Exists (Cek sukses login)
        is_success = await web_utils.element_exists(web_page, ".post-title", timeout=5000)
        
        if is_success:
            # ACTIVITY: Get Text
            text_hasil = await web_utils.get_text(web_page, ".post-title", log_name="Header Sukses")
            logger.info(f"✅ Login Berhasil! Pesan dari web: '{text_hasil}'")
            await web_utils.refresh_browser(web_page)
            # ACTIVITY: Ambil Cookies
            my_cookies = await web_utils.get_auth_data(web_page, auth_type="cookies")
            logger.info(my_cookies)

            # ACTIVITY: Navigate ke URL lain
            await web_utils.Page.goto(self=web_page,url="https://practicetestautomation.com/practice-test-table/", wait_until='networkidle')

            # ACTIVITY: check value
            await web_utils.check(
                web_page, 
                selector='fieldset:has(legend:has-text("Language")) label:has-text("Java") input', 
                check_action=True
            )
            
            # ACTIVITY: pilih value dropdown yang elementnya custom dari website
            await web_utils.click_custom_dropdown(
                web_page, 
                dropdown_selector="#enrollDropdown", 
                item_text="10,000+",
                item_selector_template='li[role="option"]:has-text("{text}")'
            )

            sleep(2)

            # ACTIVITY: Navigate ke URL lain
            await web_utils.Page.goto(self=web_page,url="https://assertqa.com/practice/webtables", wait_until='networkidle')

            # ACTIVITY: Extract Table pada website
            dt_hasil_scrape = await web_utils.extract_table(
                web_page, 
                selector="#employees-table", 
                next_button_selector='[data-cy="pagination-next"]',
                log_name="Tabel Laporan"
            )
            logger.info(dt_hasil_scrape)
        else:
            logger.error("❌ Login gagal atau elemen tidak ditemukan.")

if __name__ == "__main__":
    # Karena Playwright pakai Async, jalankan dengan asyncio.run()
    asyncio.run(main())