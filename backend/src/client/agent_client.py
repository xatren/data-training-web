"""
Veri analizi için agent tabanlı istemci modülü.

Bu modül, veri analizi işlemlerini yönetmek ve API ile iletişim kurmak için
gerekli sınıf ve fonksiyonları içerir.

Classes:
    AgentClient: Veri analizi işlemlerini yöneten ana sınıf
"""

import asyncio
import numpy as np
import requests
from typing import Dict, Any, Optional
from ..utils.logger import logger
from ..utils.validators import validate_numpy_array, validate_analysis_id
from ..models.data_models import AnalysisRequest, AnalysisResponse
from .exceptions import APIConnectionError, AnalysisError
from ..config.settings import (
    DEFAULT_BASE_URL,
    API_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    DEFAULT_ANALYSIS_METHOD,
    OUTPUT_DIR
)
from ..config.api_config import get_gemini_model
from ..utils.csv_helpers import CSVAnalyzer
from clustering import ClusteringOptimizer
import seaborn

class AgentClient:
    """
    Veri analizi işlemlerini yöneten istemci sınıfı.
    
    Bu sınıf, veri analizi işlemlerini yönetir, API ile iletişim kurar
    ve sonuçları işler. CSV analizi ve Gemini AI entegrasyonu gibi
    özellikleri destekler.
    
    Attributes:
        base_url (str): API endpoint'inin temel URL'i
        _session (Optional[requests.Session]): HTTP istekleri için oturum
        model: Gemini AI modeli
    """
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        """
        AgentClient sınıfını başlatır.
        
        Args:
            base_url (str): API endpoint'inin temel URL'i
        """
        self.base_url = base_url
        self._session: Optional[requests.Session] = None
        self.model = get_gemini_model()
    
    @property
    def session(self) -> requests.Session:
        """
        HTTP istekleri için oturum nesnesini döndürür.
        
        Returns:
            requests.Session: Aktif oturum nesnesi
        """
        if self._session is None:
            self._session = requests.Session()
        return self._session
    
    async def analyze_data(
        self,
        data: np.ndarray,
        method: str = DEFAULT_ANALYSIS_METHOD
    ) -> Dict[str, Any]:
        """
        Verilen veriyi analiz eder.
        
        Args:
            data (np.ndarray): Analiz edilecek veri
            method (str): Analiz metodu
            
        Returns:
            Dict[str, Any]: Analiz sonuçları
            
        Raises:
            ValidationError: Veri doğrulama hatası
            APIConnectionError: API bağlantı hatası
            AnalysisError: Analiz işlemi hatası
        """
        try:
            # Veri doğrulama
            data = validate_numpy_array(data)
            
            # Gemini API ile analiz
            try:
                # Veriyi metin formatına dönüştür
                data_description = f"Shape: {data.shape}, Mean: {np.mean(data)}, Std: {np.std(data)}"
                prompt = f"Veri analizi yap: {data_description}"
                
                # Gemini'den yanıt al
                response = self.model.generate_content(prompt)
                
                analysis_result = {
                    "status": "success",
                    "analysis_id": "gemini-" + str(hash(str(data)))[:8],
                    "results": {
                        "gemini_analysis": response.text,
                        "data_stats": {
                            "shape": data.shape,
                            "mean": float(np.mean(data)),
                            "std": float(np.std(data)),
                            "min": float(np.min(data)),
                            "max": float(np.max(data))
                        }
                    }
                }
                
                logger.info("Gemini analizi başarılı")
                return analysis_result
                
            except Exception as e:
                logger.error(f"Gemini API hatası: {str(e)}")
                raise APIConnectionError(f"Gemini API hatası: {str(e)}")
            
        except Exception as e:
            logger.error(f"Analiz hatası: {str(e)}", exc_info=True)
            raise AnalysisError(str(e))
    
    async def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Analiz sonuçlarını getirir."""
        try:
            analysis_id = validate_analysis_id(analysis_id)
            
            # Eğer Gemini analizi ise, cached sonuçları döndür
            if analysis_id.startswith("gemini-"):
                return {
                    "status": "success",
                    "analysis_id": analysis_id,
                    "message": "Gemini analizi tamamlandı"
                }
            
            # Diğer durumlar için normal akış
            url = f"{self.base_url}/analysis/{analysis_id}"
            logger.info(f"Analiz sonuçları isteniyor. ID: {analysis_id}")
            
            for attempt in range(MAX_RETRIES):
                try:
                    response = self.session.get(url, timeout=API_TIMEOUT)
                    if response.status_code == 404:
                        raise AnalysisError(f"Analiz bulunamadı. ID: {analysis_id}")
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout:
                    if attempt == MAX_RETRIES - 1:
                        raise APIConnectionError("API isteği zaman aşımına uğradı")
                    await asyncio.sleep(RETRY_DELAY)
                except requests.exceptions.RequestException as e:
                    if attempt == MAX_RETRIES - 1:
                        raise APIConnectionError(f"API isteği başarısız: {str(e)}")
                    await asyncio.sleep(RETRY_DELAY)
            
            result = AnalysisResponse(**response.json())
            logger.info("Analiz sonuçları başarıyla alındı")
            return result.dict()
            
        except Exception as e:
            logger.error(f"Analiz sonuçları alma hatası: {str(e)}", exc_info=True)
            raise AnalysisError(str(e))
    
    async def analyze_csv(self, file_path: str) -> Dict[str, Any]:
        """CSV dosyasını analiz eder."""
        try:
            logger.info(f"CSV analizi başlıyor: {file_path}")
            analyzer = CSVAnalyzer(file_path)
            
            # Tüm analizleri yap
            basic_stats = analyzer.get_basic_stats()
            dept_analysis = analyzer.get_department_analysis()
            age_distribution = analyzer.get_age_distribution()
            clustering_results = analyzer.get_clustering_analysis()
            #kümeleme sonuçlarını cluster.py dosyasından yapılmasını sağlayacak şekilde kod entegrasyonu sağlanacaktır.
            #optimal=False
            #if clustering_results is not None:
            #    try:
            #        print("Optimal Kümeleme modeli oluşturuluyor...")
            #        clustering_results_2=ClusteringOptimizer(analyzer)
            #        if clustering_results_2 is not None:
            #            optimal=True
             #           OptimalKumeSayisi=clustering_results_2['best_model']['params']
             #           SilhouetteSkoru=clustering_results_2['best_model']['score']
             #           KümeBoyutları =clustering_results_2['best_model']['pca']
                    
                #except Exception as e:
                    #optimal=False
                #clustering_results_2=clustering_results
            OptimalKumeSayisi=clustering_results['kmeans_analysis']['optimal_clusters']
            SilhouetteSkoru=clustering_results['kmeans_analysis']['silhouette_score']
            KümeBoyutları=clustering_results['kmeans_analysis']['cluster_sizes']
            print("optimal kümeleme süreci gerçekleştirilemedi")
                    
            visualization_files = analyzer.create_visualizations(OUTPUT_DIR)
        
            # Gemini API ile detaylı analiz
            analysis_text = f"""
            Çalışan verileri detaylı analizi:
            
            1. Genel İstatistikler:
            - Toplam çalışan sayısı: {basic_stats['toplam_calisan']}
            - Ortalama maaş: {basic_stats['ortalama_maas']:.2f} TL
            - Maaş standart sapması: {basic_stats['maas_std']:.2f} TL
            
            2. Departman Dağılımı:
            {basic_stats['departman_dagilimi']}
            
            3. Şehir Dağılımı:
            {basic_stats['sehir_dagilimi']}
            
            4. Yaş Analizi:
            - Ortalama yaş: {age_distribution['ortalama_yas']:.1f}
            - En genç: {age_distribution['min_yas']:.1f}
            - En yaşlı: {age_distribution['max_yas']:.1f}
            
            5. Kümeleme Analizi:
            - Optimal küme sayısı: {OptimalKumeSayisi}
            - Silhouette skoru: {SilhouetteSkoru:.3f}
            - Küme boyutları: {KümeBoyutları}
            
            6. Departman Bazlı Maaş Analizi:
            """
            
            for dept, stats in dept_analysis.items():
                analysis_text += f"\n{dept}:"
                analysis_text += f"\n- Çalışan sayısı: {stats['calisan_sayisi']}"
                analysis_text += f"\n- Ortalama maaş: {stats['ortalama_maas']:.2f} TL"
                analysis_text += f"\n- Maaş aralığı: {stats['min_maas']:.2f} - {stats['max_maas']:.2f} TL\n"
            
            response = self.model.generate_content(analysis_text)
            
            # Tüm sonuçları birleştir
            analysis_result = {
                "status": "success",
                "analysis_id": "csv-" + str(hash(file_path))[:8],
                "results": {
                    "basic_stats": basic_stats,
                    "department_analysis": dept_analysis,
                    "age_distribution": age_distribution,
                    "clustering_analysis": clustering_results,
                    "gemini_analysis": response.text,
                    "visualization_files": visualization_files + [clustering_results['cluster_visualization']]
                }
            }
            
            logger.info("CSV analizi başarılı")
            return analysis_result
            
        except Exception as e:
            logger.error(f"CSV analiz hatası: {str(e)}", exc_info=True)
            raise AnalysisError(str(e)) 