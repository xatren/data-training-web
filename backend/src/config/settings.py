"""
Proje için genel ayarlar ve yapılandırma değişkenleri.

Bu modül, projenin temel yapılandırma ayarlarını içerir:
- API bağlantı ayarları
- Dosya yolu yapılandırmaları
- Veri analizi parametreleri

Attributes:
    PROJECT_ROOT (Path): Proje kök dizini
    OUTPUT_DIR (Path): Analiz çıktılarının kaydedileceği dizin
    LOG_DIR (Path): Log dosyalarının kaydedileceği dizin
    DEFAULT_BASE_URL (str): API endpoint'inin varsayılan URL'i
    API_TIMEOUT (int): API istekleri için zaman aşımı süresi
    MAX_RETRIES (int): Başarısız istekler için maksimum deneme sayısı
    RETRY_DELAY (int): Yeniden denemeler arası bekleme süresi
    DEFAULT_ANALYSIS_METHOD (str): Varsayılan veri analizi metodu
"""

from pathlib import Path

# Proje dizin yapılandırması
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

# API ayarları
DEFAULT_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30  # saniye
MAX_RETRIES = 3
RETRY_DELAY = 1  # saniye

# Veri analizi ayarları
DEFAULT_ANALYSIS_METHOD = "standard"

# Dizinleri otomatik oluştur
for directory in [OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 