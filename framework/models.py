from enum import Enum

class State(Enum):
    INIT = "INIT"
    GET_TRANSACTION = "GET_TRANSACTION"
    PROCESS = "PROCESS"
    END_PROCESS = "END_PROCESS"

class BusinessRuleException(Exception):
    """Exception untuk error bisnis (Data tidak valid, dll). Tidak di-retry."""
    def __init__(self, message, error_code="BRE-000"):
        super().__init__(f"[{error_code}] {message}")
        self.error_code = error_code
        self.message = message

class SystemException(Exception):
    """Exception untuk error sistem (Koneksi putus, web timeout, dll). Akan di-retry."""
    def __init__(self, message, error_code="SYS-000"):
        super().__init__(f"[{error_code}] {message}")
        self.error_code = error_code
        self.message = message

class BotContext:
    """
    Menyimpan semua variabel global yang bisa diakses ke semua module.
    """
    def __init__(self):
        self.state = State.INIT
        self.config = {}
        self.transaction_number = 1
        self.transaction_item = None
        self.is_config_loaded = False
        self.retry_number = 0
        self.max_retry_number = 2
        self.transaction_data = [] # List dummy untuk antrean data