"""
Veri analizi için Pydantic model tanımlamaları.

Bu modül, veri analizi işlemlerinde kullanılan veri modellerini tanımlar.
API istekleri ve yanıtları için şema doğrulaması sağlar.

Models:
    AnalysisRequest: Veri analizi isteği için model
    AnalysisResponse: Veri analizi yanıtı için model
    EmployeeData: Çalışan verisi için model
    ClusteringResult: Kümeleme analizi sonuçları için model
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class EmployeeData(BaseModel):
    """
    Çalışan verisi için model.
    
    Attributes:
        ad (str): Çalışanın adı
        soyad (str): Çalışanın soyadı
        departman (str): Çalışanın departmanı
        maas (float): Çalışanın maaşı
        yas (int): Çalışanın yaşı
        sehir (str): Çalışanın çalıştığı şehir
        telefon_turu (str): Çalışanın telefon türü
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    ad: str = Field(..., description="Çalışanın adı")
    soyad: str = Field(..., description="Çalışanın soyadı")
    departman: str = Field(..., description="Çalışanın departmanı")
    maas: float = Field(..., gt=0, description="Çalışanın maaşı")
    yas: int = Field(..., gt=0, description="Çalışanın yaşı")
    sehir: str = Field(..., description="Çalışanın çalıştığı şehir")
    telefon_turu: str = Field(..., description="Çalışanın telefon türü")

class ClusteringResult(BaseModel):
    """
    Kümeleme analizi sonuçları için model.
    
    Attributes:
        optimal_clusters (int): Optimal küme sayısı
        silhouette_score (float): Silhouette skoru
        cluster_labels (List[int]): Küme etiketleri
        cluster_sizes (List[int]): Küme boyutları
        visualization_path (str): Kümeleme görselinin dosya yolu
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    optimal_clusters: int = Field(..., gt=1, description="Optimal küme sayısı")
    silhouette_score: float = Field(..., ge=-1, le=1, description="Silhouette skoru")
    cluster_labels: List[int] = Field(..., description="Küme etiketleri")
    cluster_sizes: List[int] = Field(..., description="Küme boyutları")
    visualization_path: str = Field(..., description="Kümeleme görselinin dosya yolu")

class AnalysisRequest(BaseModel):
    """
    Veri analizi isteği için model.
    
    Attributes:
        data (List[EmployeeData]): Analiz edilecek çalışan verileri
        method (str): Kullanılacak analiz metodu
        parameters (Optional[Dict[str, Any]]): Ek analiz parametreleri
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    data: List[EmployeeData] = Field(..., description="Analiz edilecek çalışan verileri")
    method: str = Field("standard", description="Kullanılacak analiz metodu")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Ek analiz parametreleri")

class AnalysisResponse(BaseModel):
    """
    Veri analizi yanıtı için model.
    
    Attributes:
        status (str): İşlem durumu ('success' veya 'error')
        analysis_id (str): Analiz işleminin benzersiz kimliği
        results (Optional[Dict[str, Any]]): Analiz sonuçları
        error (Optional[str]): Hata durumunda hata mesajı
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    status: str = Field(..., description="İşlem durumu")
    analysis_id: str = Field(..., description="Analiz işleminin benzersiz kimliği")
    results: Optional[Dict[str, Any]] = Field(None, description="Analiz sonuçları")
    error: Optional[str] = Field(None, description="Hata mesajı") 