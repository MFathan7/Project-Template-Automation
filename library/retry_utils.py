import logging
import time
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

def retry_scope(max_attempts: int = 3, delay_seconds: int = 2, exceptions: tuple = (Exception,)):
    """
    Bisa diketik (decorator) ke fungsi biasa (sync) maupun async.
    
    :param max_attempts: Maksimal percobaan sebelum menyerah.
    :param delay_seconds: Jeda waktu (detik) antar percobaan.
    :param exceptions: Tuple tipe exception yang mau ditangkap (default: semua Exception).
    """
    def decorator(func):
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"⚠️ [Retry {attempt}/{max_attempts}] Fungsi '{func.__name__}' gagal: {e}")
                    if attempt == max_attempts:
                        logger.error(f"❌ Maksimal retry tercapai untuk fungsi '{func.__name__}'.")
                        raise
                    
                    #logger.info(f"   ↳ Menunggu {delay_seconds} detik sebelum mencoba lagi...")
                    await asyncio.sleep(delay_seconds)
                    attempt += 1

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"⚠️ [Retry {attempt}/{max_attempts}] Fungsi '{func.__name__}' gagal: {e}")
                    if attempt == max_attempts:
                        logger.error(f"❌ Maksimal retry tercapai untuk fungsi '{func.__name__}'.")
                        raise # Lempar error jika sudah mentok
                    
                    #logger.info(f"   ↳ Menunggu {delay_seconds} detik sebelum mencoba lagi...")
                    time.sleep(delay_seconds)
                    attempt += 1

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator