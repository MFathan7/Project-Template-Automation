import logging
import pandas as pd
from library import excel_utils

logger = logging.getLogger(__name__)

def execute(context):
    # --------------------------------------
    # 1. INIT ALL SETTINGS
    # --------------------------------------
    logger.info("Initializing settings...")
    
    if not context.is_config_loaded:
        in_config_file = "Data/Config.xlsx"
        in_config_sheets = ["Settings", "Constants"]
        
        try:
            with excel_utils.ExcelApplicationScope(
                file_path=in_config_file, 
                visible=False,           
                create_new_file=False, 
                save_changes=False     
            ) as excel_scope:
                
                for sheet in in_config_sheets:
                    dt_config = excel_scope.read_range(
                        sheet_name=sheet,
                        range_address="",
                        has_headers=True
                    )
                    
                    if not dt_config.empty:
                        for index, row in dt_config.iterrows():
                            name = str(row.get("Name", "")).strip()
                            if name and pd.notna(row.get("Name")) and not name.startswith("#"):
                                value = row.get("Value")
                                final_value = "" if pd.isna(value) else value
                                if name not in context.config:
                                    context.config[name] = final_value
            context.is_config_loaded = True
        except FileNotFoundError:
            logger.error(f"File Config tidak ditemukan di: {in_config_file}")
            raise 
        except Exception as e:
            logger.error(f"Gagal membaca Config.xlsx: {e}")
            raise
        
    # --------------------------------------
    # 2. INIT ALL APPLICATIONS
    # --------------------------------------
    logger.info("Initializing applications...")
    
    # TODO: Panggil module library web automation di sini jika dibutuhkan
    # from library import web_utils
    # web_utils.open_browser(context.config["app_url"])