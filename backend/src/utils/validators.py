"""
Veri doğrulama fonksiyonları.

Bu modül, veri analizi işlemlerinde kullanılan girdilerin doğruluğunu
kontrol eden fonksiyonları içerir. Numpy dizileri, analiz kimlikleri ve
diğer parametreler için doğrulama sağlar.

Functions:
    validate_numpy_array: Numpy dizisi doğrulama
    validate_analysis_id: Analiz kimliği doğrulama
    validate_employee_data: Çalışan verisi doğrulama
"""

import numpy as np
from typing import Any
import re
from .logger import logger
from ..models.data_models import EmployeeData

def validate_numpy_array(data: Any) -> np.ndarray:
    """
    Verilen veriyi numpy dizisi olarak doğrular.
    
    Veri numpy dizisi değilse dönüştürmeye çalışır. Boyut ve tip
    kontrolü yapar.
    
    Args:
        data (Any): Doğrulanacak veri
        
    Returns:
        np.ndarray: Doğrulanmış numpy dizisi
        
    Raises:
        ValueError: Veri numpy dizisine dönüştürülemezse veya
                  uygun formatta değilse
    """
    try:
        # Numpy dizisine dönüştür
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=np.float64)
        
        # Boyut kontrolü
        if data.ndim not in [1, 2]:
            raise ValueError("Veri 1 veya 2 boyutlu olmalıdır")
            
        # Boş veri kontrolü
        if data.size == 0:
            raise ValueError("Veri boş olamaz")
            
        logger.debug(f"Numpy dizisi doğrulandı: shape={data.shape}, dtype={data.dtype}")
        return data
        
    except Exception as e:
        logger.error(f"Numpy dizisi doğrulama hatası: {str(e)}")
        raise ValueError(f"Geçersiz veri formatı: {str(e)}")

def validate_analysis_id(analysis_id: str) -> str:
    """
    Analiz kimliğini doğrular.
    
    Kimliğin uygun formatta olduğunu kontrol eder (alfanumerik ve tire).
    
    Args:
        analysis_id (str): Doğrulanacak analiz kimliği
        
    Returns:
        str: Doğrulanmış analiz kimliği
        
    Raises:
        ValueError: Kimlik geçersiz formattaysa
    """
    if not isinstance(analysis_id, str):
        raise ValueError("Analiz kimliği string olmalıdır")
        
    # Format kontrolü: alfanumerik ve tire
    if not re.match(r'^[a-zA-Z0-9\-]+$', analysis_id):
        raise ValueError("Analiz kimliği sadece harf, rakam ve tire içerebilir")
        
    # Uzunluk kontrolü
    if not (4 <= len(analysis_id) <= 32):
        raise ValueError("Analiz kimliği 4-32 karakter uzunluğunda olmalıdır")
        
    return analysis_id

def validate_employee_data(data: dict) -> EmployeeData:
    """
    Çalışan verisini doğrular.
    
    Verinin EmployeeData modeline uygunluğunu kontrol eder.
    
    Args:
        data (dict): Doğrulanacak çalışan verisi
        
    Returns:
        EmployeeData: Doğrulanmış çalışan verisi
        
    Raises:
        ValueError: Veri geçersiz formattaysa
    """
    try:
        # Pydantic modeli ile doğrula
        employee = EmployeeData(**data)
        
        # Ek doğrulamalar
        if employee.yas < 18:
            raise ValueError("Çalışan yaşı 18'den küçük olamaz")
            
        if employee.maas < 0:
            raise ValueError("Maaş negatif olamaz")
            
        logger.debug(f"Çalışan verisi doğrulandı: {employee.ad} {employee.soyad}")
        return employee
        
    except Exception as e:
        logger.error(f"Çalışan verisi doğrulama hatası: {str(e)}")
        raise ValueError(f"Geçersiz çalışan verisi: {str(e)}") 