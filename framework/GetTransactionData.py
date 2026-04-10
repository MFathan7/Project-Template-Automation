import logging

logger = logging.getLogger(__name__)

def execute(context):
    logger.info("Get the transaction item")
    
    # TODO: Ubah ini untuk menyesuaikan kondisi flow process
    if context.transaction_number <= len(context.transaction_data):
        context.transaction_item = context.transaction_data[context.transaction_number - 1]
        logger.info(f"Transaction Item: {context.transaction_item}")
    else:
        # TODO: Untuk mengosongkan data agar tidak masuk ke flow Process
        context.transaction_item = None