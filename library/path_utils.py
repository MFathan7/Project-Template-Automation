import os
import shutil
import logging
import zipfile
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

def copy_folder(source_path: str, destination_path: str, overwrite: bool = True):
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Folder sumber tidak ditemukan: {source_path}")
        
    try:
        shutil.copytree(source_path, destination_path, dirs_exist_ok=overwrite)
        #logger.info("   ↳ Copy folder berhasil ✅")
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal copy folder: {e}")
        raise

def get_files(folder_path: str, extension: str = None) -> list:
    """Mengambil list file pada folder."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder tidak ditemukan: {folder_path}")
        
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                 if os.path.isfile(os.path.join(folder_path, f))]
                 
    if extension:
        ext = extension if extension.startswith('.') else f'.{extension}'
        all_files = [f for f in all_files if f.lower().endswith(ext.lower())]
        
    #logger.info(f"   ↳ Ditemukan {len(all_files)} file.")
    return all_files

def get_folders(folder_path: str) -> list:
    """Mengambil list folder pada folder."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder tidak ditemukan: {folder_path}")
        
    folders = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
               if os.path.isdir(os.path.join(folder_path, f))]
               
    #logger.info(f"   ↳ Ditemukan {len(folders)} folder.")
    return folders

def rename_item(old_path: str, new_name: str):
    """Merubah nama file atau folder.
    new_name: Nama baru untuk file atau folder.
    """
    if not os.path.exists(old_path):
        raise FileNotFoundError(f"File/Folder tidak ditemukan: {old_path}")
        
    base_dir = os.path.dirname(old_path)
    new_path = os.path.join(base_dir, new_name)
    
    try:
        os.rename(old_path, new_path)
        #logger.info(f"   ↳ Rename berhasil ✅ ({new_path})")
        return new_path
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal rename: {e}")
        raise

def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
        
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        #logger.info("   ↳ File berhasil dibaca ✅")
        return content
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal membaca text file: {e}")
        raise

def write_text_file(file_path: str, text_content: str, append: bool = False, encoding: str = 'utf-8'):
    mode = 'a' if append else 'w'
    action = "Append" if append else "Write"
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    try:
        with open(file_path, mode, encoding=encoding) as f:
            if append:
                f.write("\n" + text_content)
            else:
                f.write(text_content)
        #logger.info(f"   ↳ {action} berhasil ✅")
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal menulis text file: {e}")
        raise

def compress_to_zip(source_path: str, zip_path: str):
    """Bisa mengompresi 1 file atau 1 folder penuh."""
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Sumber tidak ditemukan: {source_path}")
        
    try:
        if not zip_path.lower().endswith('.zip'):
            zip_path += '.zip'
            
        if os.path.isfile(source_path):
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(source_path, os.path.basename(source_path))
        else:
            base_zip_path = zip_path[:-4] if zip_path.lower().endswith('.zip') else zip_path
            shutil.make_archive(base_name=base_zip_path, format='zip', root_dir=source_path)
            
        #logger.info("   ↳ Kompresi berhasil ✅")
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal melakukan kompresi ZIP: {e}")
        raise

def extract_zip(zip_path: str, extract_folder: str):
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"File ZIP tidak ditemukan: {zip_path}")
        
    try:
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_folder)
        #logger.info("   ↳ Ekstraksi berhasil ✅")
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal mengekstrak ZIP: {e}")
        raise