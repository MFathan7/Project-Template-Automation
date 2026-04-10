import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ==========================================
# FILE & FOLDER ACTIVITIES
# ==========================================

def path_exists(path: str) -> bool:
    exists = os.path.exists(path)
    #tipe = "Folder" if os.path.isdir(path) else "File" if os.path.isfile(path) else "Path"
    #logger.info(f"👁️ PATH EXISTS: Mengecek {tipe} '{path}' -> {exists}")
    return exists

def create_folder(folder_path: str):
    #logger.info(f"📁 CREATE FOLDER: Membuat folder di '{folder_path}'")
    # exist_ok=True artinya tidak akan error jika folder sudah ada (mirip behavior UiPath)
    # parents=True artinya otomatis membuat sub-folder jika belum ada
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def delete_file(file_path: str):
    #logger.info(f"🗑️ DELETE FILE: Menghapus '{file_path}'")
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        logger.warning(f"File '{file_path}' tidak ditemukan, penghapusan dilewati.")

def delete_folder(folder_path: str):
    #logger.info(f"🗑️ DELETE FOLDER: Menghapus '{folder_path}' beserta isinya")
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    else:
        logger.warning(f"Folder '{folder_path}' tidak ditemukan, penghapusan dilewati.")

def move_file(source_path: str, destination_path: str, overwrite: bool = True):
    #logger.info(f"🚚 MOVE FILE: Memindahkan '{source_path}' ke '{destination_path}'")
    
    if overwrite and os.path.exists(destination_path):
        os.remove(destination_path) # Hapus dest sebelumnya jika overwrite = True
        
    shutil.move(source_path, destination_path)

def copy_file(source_path: str, destination_path: str, overwrite: bool = True):
    #logger.info(f"📄 COPY FILE: Menyalin '{source_path}' ke '{destination_path}'")
    
    if overwrite and os.path.exists(destination_path):
        os.remove(destination_path)
        
    shutil.copy2(source_path, destination_path)