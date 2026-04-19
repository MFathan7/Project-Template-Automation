import logging
from playwright.async_api import async_playwright, Page, Browser, Playwright
import pandas as pd

logger = logging.getLogger(__name__)

# ==========================================
# BROWSER ACTIVITIES
# ==========================================

class UseApplicationBrowserAsync:
    def __init__(self, url: str, headless: bool = False, close_on_exit: bool = True, timeout_ms: int = 30000):
        self.url = url
        self.headless = headless
        self.close_on_exit = close_on_exit
        self.timeout_ms = timeout_ms
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.page: Page = None
        self._playwright_context_manager = None

    async def __aenter__(self) -> Page:
        #logger.info(f"🌐 USE APPLICATION BROWSER: Membuka {self.url} (Headless: {self.headless})")
        self._playwright_context_manager = async_playwright()
        self.playwright = await self._playwright_context_manager.__aenter__()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        self.page.set_default_timeout(self.timeout_ms)
        await self.page.goto(self.url)
        return self.page

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.close_on_exit:
            #logger.info("🛑 CLOSE APPLICATION BROWSER: Menutup Browser.")
            if self.browser:
                await self.browser.close()
            if self._playwright_context_manager:
                await self._playwright_context_manager.__aexit__(exc_type, exc_val, exc_tb)

# ==========================================
# UI AUTOMATION ACTIVITIES
# ==========================================

async def type_into(page: Page, selector: str, text: str, log_name: str = ""):
    #name = log_name if log_name else selector
    #logger.info(f"📝 TYPE INTO: Mengetik rahasia/teks ke '{name}'")
    
    await page.locator(selector).fill(text)

async def click(page: Page, selector: str, log_name: str = ""):
    name = log_name if log_name else selector
    #logger.info(f"👆 CLICK: Mengklik elemen '{name}'")
    
    await page.locator(selector).click()

async def get_text(page: Page, selector: str, log_name: str = "") -> str:
    #name = log_name if log_name else selector
    #logger.info(f"📥 GET TEXT: Mengambil teks dari '{name}'")
    
    await page.locator(selector).wait_for(state="visible")
    text_result = await page.locator(selector).inner_text()
    
    #logger.info(f"Hasil: '{text_result}'")
    return text_result

async def element_exists(page: Page, selector: str, timeout: int = 5000) -> bool:
    #logger.info(f"👁️ ELEMENT EXISTS: Mengecek keberadaan '{selector}' (Timeout: {timeout}ms)")
    try:
        await page.locator(selector).wait_for(state="visible", timeout=timeout)
        #logger.info("Elemen Ditemukan ✅")
        return True
    except:
        logger.warning("Elemen Tidak Ditemukan ❌")
        return False

async def select_item(page: Page, selector: str, item_text: str, log_name: str = ""):
    """Untuk memilih opsi dari Dropdown <select>."""
    name = log_name if log_name else selector
    #logger.info(f"🔽 SELECT ITEM: Memilih '{item_text}' pada '{name}'")
    await page.locator(selector).wait_for(state="visible")
    await page.locator(selector).select_option(label=item_text)

async def click_custom_dropdown(page: Page, dropdown_selector: str, item_text: str, item_selector_template: str = None, log_name: str = ""):
    """
    - dropdown_selector: Selector kotak yang diklik untuk membuka menu.
    - item_text: Teks yang mau dipilih (misal: "10,000+").
    - item_selector_template: (Opsional) Jika struktur web rumit, masukkan format selector. Gunakan {text} sebagai penanda.
    """
    name = log_name if log_name else dropdown_selector
    #logger.info(f"🔽 CLICK CUSTOM DROPDOWN: Memilih '{item_text}' pada '{name}'")
    
    await page.locator(dropdown_selector).click()
    await page.wait_for_timeout(500)
    
    if item_selector_template:
        option_selector = item_selector_template.replace("{text}", item_text)
        await page.locator(option_selector).click()
    else:
        option_locator = page.get_by_text(item_text, exact=True).filter(state="visible").last
        await option_locator.click()
        
    #logger.info(f"   ↳ Berhasil memilih '{item_text}' ✅")

async def check(page: Page, selector: str, check_action: bool = True, log_name: str = ""):
    """Untuk memilih : True untuk centang, False untuk hapus centang pada element website."""
    name = log_name if log_name else selector
    action_str = "Mencentang" if check_action else "Menghapus centang"
    #logger.info(f"☑️ CHECK: {action_str} pada '{name}'")
    await page.locator(selector).wait_for(state="visible")
    if check_action:
        await page.locator(selector).check()
    else:
        await page.locator(selector).uncheck()
        
async def refresh_browser(page: Page):
    await page.reload()
    await page.wait_for_load_state("networkidle")

async def get_auth_data(page: Page, auth_type: str = "cookies", token_key: str = "authToken"):
    """
    Mengambil Cookies atau Auth Token (Local/Session Storage).
    - auth_type: "cookies", "local_storage", atau "session_storage"
    - token_key: Nama key jika mengambil dari storage (misal: 'access_token')
    """
    
    if auth_type.lower() == "cookies":
        # Return list of dictionaries berisi cookies
        return await page.context.cookies()
        
    elif auth_type.lower() == "local_storage":
        # Eksekusi JavaScript untuk tarik dari Local Storage
        token = await page.evaluate(f"window.localStorage.getItem('{token_key}')")
        logger.info(f"   ↳ Token {token_key} {'berhasil' if token else 'gagal'} diambil.")
        return token
        
    elif auth_type.lower() == "session_storage":
        # Eksekusi JavaScript untuk tarik dari Session Storage
        token = await page.evaluate(f"window.sessionStorage.getItem('{token_key}')")
        logger.info(f"   ↳ Token {token_key} {'berhasil' if token else 'gagal'} diambil.")
        return token
        
    else:
        raise ValueError("auth_type harus 'cookies', 'local_storage', atau 'session_storage'")

async def extract_table(page: Page, selector: str, next_button_selector: str = None, max_pages: int = 0, log_name: str = "", extract_links: bool = True) -> pd.DataFrame:
    """
    max_pages: 0 berarti tidak ada batasan (akan scrape terus sampai tombol Next habis/disabled).
    extract_links = True akan mengambil href dari tag <a> atau src dari tag <img> di dalam tabel.
    """
    name = log_name if log_name else selector
    #logger.info(f"📊 EXTRACT TABLE: Menarik data tabel dari '{name}' - {limit_text}")
    all_dataframes = []
    current_page = 1
    while True:
        try:
            await page.locator(selector).wait_for(state="visible", timeout=10000)

            js_script = """(el, extract_links) => {
                let clone = el.cloneNode(true);
                if (extract_links) {
                    clone.querySelectorAll('a').forEach(a => {
                        if (a.href && !a.href.startsWith('javascript:')) {
                            a.innerText = a.innerText.trim() + ' (' + a.href + ')';
                        }
                    });
                    clone.querySelectorAll('img').forEach(img => {
                        if (img.src) {
                            img.innerText = (img.alt ? img.alt : 'Image') + ' (' + img.src + ')';
                        }
                    });
                }
                return clone.outerHTML;
            }"""

            table_html = await page.locator(selector).evaluate(js_script, extract_links)
            df_list = pd.read_html(table_html)
            
            if df_list:
                df_current = df_list[0]
                all_dataframes.append(df_current)
                #logger.info(f"   ↳ Halaman {current_page}: Berhasil mengekstrak {len(df_current)} baris data.")
            else:
                logger.warning(f"   ↳ Halaman {current_page}: Tidak ada format tabel yang valid.")
            
            if max_pages > 0 and current_page >= max_pages:
                logger.info(f"   ↳ 🛑 Batas max_pages ({max_pages}) tercapai. Berhenti.")
                break
                
            if next_button_selector:
                is_next_visible = await element_exists(page, next_button_selector, timeout=3000)
                is_disabled = False
                
                if is_next_visible:
                    is_disabled = await page.locator(next_button_selector).evaluate(
                        "el => el.disabled || el.classList.contains('disabled') || el.getAttribute('aria-disabled') === 'true'"
                    )
                
                if is_next_visible and not is_disabled:
                    logger.info(f"   ↳ Mengklik Next Page menuju halaman {current_page + 1}...")
                    await page.locator(next_button_selector).click()
                    await page.wait_for_timeout(2000) # Jeda render web
                    current_page += 1
                else:
                    logger.info("   ↳ 🛑 Tombol Next tidak ada atau ter-disable. Ekstraksi selesai (Mentok).")
                    break
            else:
                break
                
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal ekstrak di halaman {current_page}: {e}")
            break
            
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        logger.info(f"   ↳ TOTAL DATA: {len(final_df)} baris berhasil diekstrak dari {current_page} halaman ✅")
        return final_df
        
    return pd.DataFrame()