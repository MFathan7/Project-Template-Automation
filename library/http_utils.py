import logging
import requests
import os

logger = logging.getLogger(__name__)

# ==========================================
# 🌐 HTTP REQUEST ACTIVITIES
# ==========================================

def send_request(url: str, method: str = "GET", headers: dict = None, 
                 params: dict = None, json_data: dict = None, data: dict = None, 
                 timeout: int = 30) -> dict:
    """
    :param url: Endpoint API.
    :param method: GET, POST, PUT, DELETE, PATCH.
    :param headers: Dictionary untuk header (misal: {"Authorization": "Bearer token"}).
    :param params: Dictionary untuk Query String (?key=value).
    :param json_data: Dictionary untuk Body bertipe application/json.
    :param data: Dictionary untuk Body bertipe form-urlencoded.
    :return: Dictionary berisi status_code, text, json (jika ada), dan headers response.
    """
    method = method.upper()
    #logger.info(f"🌐 HTTP {method}: Mengirim request ke '{url}'")
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            data=data,
            timeout=timeout
        )
        
        status = response.status_code
        #logger.info(f"   ↳ Status Code: {status} ({response.reason})")
        
        parsed_json = None
        try:
            parsed_json = response.json()
        except ValueError:
            pass
            
        result = {
            "status_code": status,
            "text": response.text,
            "json": parsed_json,
            "headers": dict(response.headers),
            "is_success": response.ok
        }
        
        # if not response.ok:
        #     logger.warning(f"   ↳ ⚠️ HTTP Request tidak sukses. Cek detail response: {response.text[:200]}...")
            
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"   ↳ ❌ Gagal melakukan request: {e}")
        raise


def download_file(url: str, destination_path: str, headers: dict = None, timeout: int = 60) -> str:
    """
    Mengunduh file dari URL langsung ke folder lokal.
    """
    os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
    
    try:
        with requests.get(url, headers=headers, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
        #logger.info(f"   ↳ Download berhasil ✅")
        return destination_path
        
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal download file: {e}")
        raise


def upload_file(url: str, file_path: str, file_param_name: str = "file", 
                method: str = "POST", headers: dict = None, data: dict = None, 
                timeout: int = 60) -> dict:
    """
    Mengunggah file (Multipart Form-Data) ke server/API.
    
    :param file_param_name: Nama key parameter yang diminta oleh API (biasanya 'file' atau 'document').
    :param data: Tambahan payload text/form jika API butuh data selain file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
        
    try:
        with open(file_path, 'rb') as f:
            files = {file_param_name: f}
            
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                data=data,
                files=files,
                timeout=timeout
            )
            
        logger.info(f"   ↳ Status Code: {response.status_code}")
        
        parsed_json = None
        try:
            parsed_json = response.json()
        except ValueError:
            pass
            
        return {
            "status_code": response.status_code,
            "text": response.text,
            "json": parsed_json,
            "is_success": response.ok
        }
        
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal upload file: {e}")
        raise