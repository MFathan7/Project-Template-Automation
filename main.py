import logging, os
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

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if root_logger.hasHandlers():
    root_logger.handlers.clear()

console_handler = logging.StreamHandler()
console_handler.setFormatter(EmojiFormatter())
root_logger.addHandler(console_handler)

os.makedirs("Data/Logs", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"Data/Logs/robot_execution_{timestamp}.txt"

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
# Format untuk txt dibuat lebih bersih tanpa emoji agar mudah dibaca oleh sistem analitik
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(module)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

logger = logging.getLogger("Main")

PROJECT_NAME = "Robotic Enterprise Framework"
def run_reframework():
    logger.info(f"{PROJECT_NAME} execution started.")
    
    # Inisialisasi Context (Variabel global)
    context = BotContext()

    while context.state != State.END_PROCESS:
        try:
            # ==============================
            # STATE: INIT
            # ==============================
            if context.state == State.INIT:
                InitAllSettings.execute(context)
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
    run_reframework()