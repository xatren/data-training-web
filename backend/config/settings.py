from pathlib import Path
import logging

def setup_logging():
    """Loglama ayarlarını yapılandır"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def setup_directories():
    """Gerekli dizinleri oluştur"""
    directories = ['output', 'logs']
    for dir_name in directories:
        path = Path(dir_name)
        path.mkdir(exist_ok=True) 