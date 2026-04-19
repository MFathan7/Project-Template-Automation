import logging
import sys
import os

# Setup agar file di dalam folder Example bisa membaca folder library di luarnya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import http_utils

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Memulai Contoh HTTP API Automation ===")
    
    # =========================================================
    # 1. HTTP GET REQUEST
    # =========================================================
    logger.info("\n--- 1. HTTP GET REQUEST ---")
    url_get = "https://jsonplaceholder.typicode.com/posts/1"
    
    response_get = http_utils.send_request(url=url_get, method="GET")
    
    if response_get["is_success"]:
        # Robot otomatis mem-parsing JSON menjadi Dictionary Python
        data_json = response_get["json"]
        logger.info(f"Judul Post: {data_json['title']}")
        logger.info(f"Body: {data_json['body']}")
    
    # =========================================================
    # 2. HTTP POST REQUEST (Kirim Data)
    # =========================================================
    logger.info("\n--- 2. HTTP POST REQUEST ---")
    url_post = "https://jsonplaceholder.typicode.com/posts"
    payload = {
        "title": "Laporan Baru",
        "body": "Isi laporan bot RPA",
        "userId": 99
    }
    
    response_post = http_utils.send_request(
        url=url_post, 
        method="POST", 
        json_data=payload # Otomatis set header Content-Type: application/json
    )
    logger.info(f"Status Buat Data: {response_post['status_code']}")
    logger.info(f"Response Server: {response_post['text']}")

    # =========================================================
    # 3. DOWNLOAD FILE
    # =========================================================
    logger.info("\n--- 3. DOWNLOAD FILE DARI URL ---")
    # Contoh download gambar dummy
    url_download = "https://httpbin.org/image/jpeg"
    lokasi_simpan = "Example/Data/Output/gambar_dummy.jpg"
    
    file_hasil = http_utils.download_file(url=url_download, destination_path=lokasi_simpan)
    logger.info(f"File berhasil diselamatkan ke: {file_hasil}")

    # =========================================================
    # 4. UPLOAD FILE
    # =========================================================
    logger.info("\n--- 4. UPLOAD FILE (MULTIPART) ---")
    url_upload = "https://httpbin.org/post"
    
    # Kita buat file teks kecil secara on-the-fly untuk di-upload
    file_upload_path = "Example/Data/Output/laporan_rahasia.txt"
    with open(file_upload_path, "w") as f:
        f.write("Ini adalah dokumen rahasia perusahaan!")
        
    response_upload = http_utils.upload_file(
        url=url_upload, 
        file_path=file_upload_path, 
        file_param_name="dokumen_penting" # Sesuaikan dengan field API
    )
    
    logger.info(f"Status Upload: {response_upload['status_code']}")
    # httpbin.org/post akan mengembalikan data yang kita kirim
    logger.info(f"Bukti File Masuk API: {response_upload['json']['files']}")

if __name__ == "__main__":
    main()