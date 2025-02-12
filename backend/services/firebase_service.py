import requests
from pathlib import Path
import logging
from urllib.parse import unquote, quote

class FirebaseService:
    def __init__(self):
        self.base_url = "https://firebasestorage.googleapis.com"

    async def download_file(self, file_url: str, file_name: str) -> Path:
        """Firebase Storage'dan dosyayı indir"""
        try:
            # URL'yi düzgün şekilde decode et ve yeniden encode et
            decoded_url = unquote(file_url)
            
            # URL'deki path kısmını düzelt
            if 'uploads%2F' in decoded_url:
                # URL'deki path'i düzelt
                path_part = decoded_url.split('/o/')[1].split('?')[0]
                token_part = decoded_url.split('token=')[1]
                
                # Yeni URL oluştur
                fixed_url = f"{self.base_url}/v0/b/tera11.firebasestorage.app/o/{path_part}?alt=media&token={token_part}"
            else:
                fixed_url = decoded_url

            logging.info(f"Downloading file from: {fixed_url}")

            # Dosyayı indir
            response = requests.get(
                fixed_url,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache'
                },
                stream=True,  # Büyük dosyalar için streaming kullan
                verify=False  # SSL doğrulamasını devre dışı bırak
            )

            if response.status_code != 200:
                logging.error(f"Download failed with status code: {response.status_code}")
                logging.error(f"Response content: {response.text}")
                raise Exception(f"Download failed with status code: {response.status_code}")

            # Geçici dosya oluştur
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            temp_file = temp_dir / file_name

            # Dosyayı chunk'lar halinde kaydet
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            if not temp_file.exists() or temp_file.stat().st_size == 0:
                raise Exception("Downloaded file is empty or does not exist")

            logging.info(f"File downloaded successfully: {temp_file}")
            return temp_file

        except Exception as e:
            logging.error(f"Firebase download error: {str(e)}")
            if 'response' in locals():
                logging.error(f"Response status code: {response.status_code}")
                logging.error(f"Response headers: {dict(response.headers)}")
            raise Exception(f"File download error: {str(e)}") 