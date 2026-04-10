import logging
from playwright.async_api import async_playwright, Page, Browser, Playwright

logger = logging.getLogger(__name__)

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
# 🧩 UI AUTOMATION ACTIVITIES
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
        