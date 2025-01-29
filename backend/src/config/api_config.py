"""
API yapılandırma ayarları.

Bu modül, Gemini API ve diğer harici API'ler için yapılandırma
ayarlarını içerir. API anahtarları, model parametreleri ve bağlantı
ayarları burada yönetilir.

Functions:
    get_gemini_model: Yapılandırılmış Gemini AI modelini döndürür
    
Attributes:
    GEMINI_API_KEY (str): Gemini API anahtarı
    MODEL_NAME (str): Kullanılacak model adı
    TEMPERATURE (float): Model çıktı çeşitliliği parametresi
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from ..utils.logger import logger

# .env dosyasını yükle
load_dotenv()

# API yapılandırma sabitleri
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-pro"
TEMPERATURE = 0.7

def get_gemini_model():
    """
    Yapılandırılmış Gemini AI modelini döndürür.
    
    API anahtarını kontrol eder ve modeli yapılandırır. Model
    parametreleri (sıcaklık, maksimum token vb.) burada ayarlanır.
    
    Returns:
        genai.GenerativeModel: Yapılandırılmış model nesnesi
        
    Raises:
        ValueError: API anahtarı bulunamazsa veya geçersizse
    """
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY bulunamadı")
            
        # API anahtarını ayarla
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Modeli yapılandır
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={
                "temperature": TEMPERATURE,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
        )
        
        logger.info(f"Gemini model başarıyla yapılandırıldı: {MODEL_NAME}")
        return model
        
    except Exception as e:
        logger.error(f"Gemini model yapılandırma hatası: {str(e)}")
        raise ValueError(f"Model yapılandırma hatası: {str(e)}") 