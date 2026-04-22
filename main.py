import logging
import logging.handlers # Penting untuk MemoryHandler
import os, argparse
from datetime import datetime
from framework.models import State, BotContext, BusinessRuleException
from framework import InitAllSettings, GetTransactionData, CloseAllApplications, Process

class EmojiFormatter(logging.Formatter):
    EMOJIS = {
        logging.DEBUG: "🐛 DEBUG",
        logging.INFO: "ℹ️ INFO",
        logging.WARNING: "⚠️ WARNING",
        logging.ERROR: "❌ ERROR",
        logging.CRITICAL: "🚨 CRITICAL"
    }

    def format(self, record):
        levelname_emoji = self.EMOJIS.get(record.levelno, record.levelname)
        log_fmt = f"%(asctime)s - {levelname_emoji} - %(message)s"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

# ==========================================
# SETUP GLOBAL LOGGING HANDLERS
# ==========================================
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if root_logger.hasHandlers():
    root_logger.handlers.clear()

console_handler = logging.StreamHandler()
console_handler.setFormatter(EmojiFormatter())
root_logger.addHandler(console_handler)

memory_handler = logging.handlers.MemoryHandler(capacity=1000, target=None)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(module)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
memory_handler.setFormatter(file_formatter)
root_logger.addHandler(memory_handler)

logger = logging.getLogger("Main")

def setup_file_logger(config: dict):
    """
    Setup File Log ke file txt.
    Tambah key "Folder Log" di Config file untuk merubah path location folder untuk data Log robot.
    """
    global memory_handler
    
    has_file_handler = any(isinstance(h, logging.FileHandler) for h in root_logger.handlers)
    if has_file_handler:
        return

    log_folder = config.get("Folder Log", "Data/Logs/")
    os.makedirs(log_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(log_folder, f"robot_execution_{timestamp}.txt")

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    
    root_logger.addHandler(file_handler)

    if memory_handler in root_logger.handlers:
        memory_handler.setTarget(file_handler)
        memory_handler.flush()
        memory_handler.close()
        root_logger.removeHandler(memory_handler)


PROJECT_NAME = "Robotic Enterprise Framework"
def run_reframework(in_arguments: dict = None):
    logger.info(f"{PROJECT_NAME} execution started.")
    
    context = BotContext()
    if in_arguments:
        context.config.update(in_arguments)

    while context.state != State.END_PROCESS:
        try:
            # ==============================
            # STATE: INIT
            # ==============================
            if context.state == State.INIT:
                InitAllSettings.execute(context)
                
                setup_file_logger(context.config)
                
                context.state = State.GET_TRANSACTION

            # ==============================
            # STATE: GET TRANSACTION
            # ==============================
            elif context.state == State.GET_TRANSACTION:
                GetTransactionData.execute(context)
                
                if context.transaction_item is None:
                    logger.info("Process finished due to no more transaction data")
                    context.state = State.END_PROCESS
                else:
                    context.state = State.PROCESS

            # ==============================
            # STATE: PROCESS
            # ==============================
            elif context.state == State.PROCESS:
                try:
                    Process.execute(context)
                    
                    logger.info("Transaction Successful.")
                    context.transaction_number += 1
                    context.retry_number = 0
                    context.state = State.GET_TRANSACTION

                except BusinessRuleException as be:
                    logger.error(f"Business exception at processing: {be}")
                    context.transaction_number += 1
                    context.retry_number = 0
                    context.state = State.GET_TRANSACTION
                    
                except Exception as se:
                    logger.error(f"System exception at processing: {se}")
                    
                    max_consecutive = int(context.config.get("MaxConsecutiveSystemExceptions", 0))
                    
                    if max_consecutive > 0 and context.retry_number >= max_consecutive:
                        error_msg = context.config.get("ExceptionMessage_ConsecutiveErrors", "Max consecutive system exceptions hit.")
                        logger.error(f"{error_msg} Consecutive retry number: {context.retry_number}")
                        context.transaction_number += 1
                        context.retry_number = 0
                        context.state = State.INIT 
                    else:
                        context.retry_number += 1
                        logger.info(f"System Exception. Retry number: {context.retry_number}")
                        context.state = State.INIT

        except Exception as main_e:
            logger.error(f"Fatal error in REFramework main loop: {main_e}")
            context.state = State.END_PROCESS

    # ==============================
    # STATE: END PROCESS
    # ==============================
    CloseAllApplications.execute(context)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # Tambahkan argument yang kamu inginkan di sini
    parser.add_argument("--env", type=str, default="DEV", help="Environment (DEV/UAT/PROD)")
    parser.add_argument("--input_file", type=str, default="", help="Path spesifik file input")
    parser.add_argument("--headless", action="store_true", help="Jalankan browser di background jika ditambah flag ini")
    #Contoh execute : python main.py --env PROD --input_file "Data/data_penting.xlsx"
    
    args = parser.parse_args()
    
    run_reframework(in_arguments=vars(args))