"""
Özel hata sınıfları.

Bu modül, proje genelinde kullanılan özel hata sınıflarını tanımlar.
Her hata türü için özel bir sınıf sağlanarak hata yönetimi kolaylaştırılır.

Classes:
    AgentClientError: Temel hata sınıfı
    ValidationError: Veri doğrulama hataları
    APIConnectionError: API bağlantı hataları
    AnalysisError: Veri analizi hataları
"""

class AgentClientError(Exception):
    """
    Temel hata sınıfı.
    
    Diğer tüm özel hata sınıfları bu sınıftan türetilir.
    
    Attributes:
        message (str): Hata mesajı
    """
    def __init__(self, message: str):
        """
        Args:
            message (str): Hata mesajı
        """
        self.message = message
        super().__init__(self.message)

class ValidationError(AgentClientError):
    """
    Veri doğrulama hatalarını temsil eden sınıf.
    
    Geçersiz veri formatı, eksik alanlar veya uyumsuz veri tipleri
    gibi doğrulama hatalarında kullanılır.
    """
    pass

class APIConnectionError(AgentClientError):
    """
    API bağlantı hatalarını temsil eden sınıf.
    
    Ağ bağlantısı, zaman aşımı veya sunucu yanıt vermeme
    gibi durumlarda kullanılır.
    """
    pass

class AnalysisError(AgentClientError):
    """
    Veri analizi hatalarını temsil eden sınıf.
    
    Analiz işlemi sırasında oluşan hatalar, geçersiz parametreler
    veya hesaplama hataları gibi durumlarda kullanılır.
    """
    pass 