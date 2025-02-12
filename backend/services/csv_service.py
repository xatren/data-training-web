import pandas as pd
from pathlib import Path
import logging
from .firebase_service import FirebaseService

class CSVService:
    def __init__(self):
        self.firebase = FirebaseService()

    async def get_dataframe_from_url(self, file_url: str, file_name: str) -> pd.DataFrame:
        """Firebase'den CSV dosyasını indir ve DataFrame'e dönüştür"""
        temp_file = None
        try:
            # Firebase'den dosyayı indir
            temp_file = await self.firebase.download_file(file_url, file_name)

            if not temp_file.exists():
                raise Exception("Downloaded file does not exist")

            # CSV'yi DataFrame'e dönüştür
            try:
                df = pd.read_csv(
                    temp_file,
                    dtype=None,  # Otomatik tip belirleme
                    na_values=['NA', 'missing', ''],
                    encoding='utf-8',  # UTF-8 encoding kullan
                    on_bad_lines='skip'  # Hatalı satırları atla
                )
            except UnicodeDecodeError:
                # UTF-8 çalışmazsa diğer encoding'leri dene
                df = pd.read_csv(
                    temp_file,
                    dtype=None,
                    na_values=['NA', 'missing', ''],
                    encoding='latin1',
                    on_bad_lines='skip'
                )

            if df.empty:
                raise ValueError("CSV dosyası boş")

            logging.info(f"CSV loaded successfully with {len(df)} rows and {len(df.columns)} columns")
            return df

        except Exception as e:
            logging.error(f"CSV okuma hatası: {str(e)}")
            raise Exception(f"CSV okuma hatası: {str(e)}")

        finally:
            # Geçici dosyayı temizle
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    logging.error(f"Temp file cleanup error: {str(e)}") 