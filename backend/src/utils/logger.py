"""
Proje genelinde kullanılan loglama yapılandırması.

Bu modül, projenin loglama sistemini yapılandırır ve merkezi bir logger
nesnesi sağlar. Tüm modüller bu logger'ı kullanarak tutarlı bir loglama
yapar.

Attributes:
    logger (logging.Logger): Yapılandırılmış logger nesnesi

Example:
    >>> from ..utils.logger import logger
    >>> logger.info("İşlem başarılı")
    >>> logger.error("Bir hata oluştu", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from ..config.settings import PROJECT_ROOT

# Log dizinini oluştur
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    """
    Logger nesnesini yapılandırır.
    
    Hem dosyaya hem de konsola log yazacak şekilde ayarlanır.
    Log formatı tarih, seviye ve mesajı içerir.
    
    Args:
        name (str): Logger'ın adı
        
    Returns:
        logging.Logger: Yapılandırılmış logger nesnesi
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Log formatı
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Dosyaya yazma handler'ı
    file_handler = logging.FileHandler(
        LOG_DIR / "app.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Konsola yazma handler'ı
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Merkezi logger nesnesini oluştur
logger = setup_logger("src.utils.logger") 