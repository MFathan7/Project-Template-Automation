import logging
from framework.models import SystemException, BusinessRuleException

logger = logging.getLogger(__name__)


def execute(context):
    logger.info("Processing transaction...")
    # NOTE: Contoh pemanggilan global variable
    item_data = context.transaction_item
    
    try:
        # TODO: Tambahkan flow apapun disini
        pass
    except BusinessRuleException as be:
        raise be
    except SystemException as se:
        raise se
    except Exception as e:
        raise SystemException(f"Error tidak terduga: {str(e)}", error_code="SYS-000")