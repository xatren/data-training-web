import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import numpy as np
import json
from pathlib import Path
from data_preparation import DataPreparation
from clustering import ClusteringOptimizer
from auto_cluster import AutoCluster
import pandas as pd
import logging

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollectorAgent:
    """Ajan 1: Veri toplama ve ön işleme."""
    
    def __init__(self):
        self.preprocessor = DataPreparation()
        
    async def process_data(self, data: np.ndarray) -> Dict[str, Any]:
        """Ham veriyi işler ve temizler."""
        try:
            logger.info(f"Veri işleniyor. Giriş boyutu: {data.shape}")
            
            # Veriyi DataFrame'e dönüştür
            df = pd.DataFrame(data)
            logger.info("DataFrame oluşturuldu")
            
            # Eksik değerleri kontrol et ve doldur
            missing_stats = self.preprocessor.analyze_missing_values(df)
            logger.info(f"Eksik değer analizi: {missing_stats}")
            
            if missing_stats['total_missing'] > 0:
                strategy = {col: 'mean' for col in df.columns}
                df = self.preprocessor.handle_missing_values(df, strategy)
                logger.info("Eksik değerler dolduruldu")
            
            # Aykırı değerleri tespit et ve işle
            try:
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                outliers = self.preprocessor.detect_outliers(df, numeric_cols)
                if any(len(indices) > 0 for indices in outliers.values()):
                    df = self.preprocessor.handle_outliers(df, outliers)
                logger.info("Aykırı değerler işlendi")
            except Exception as e:
                logger.warning(f"Aykırı değer işleme hatası: {str(e)}")
            
            # Özellikleri ölçeklendir
            try:
                df = self.preprocessor.scale_features(df, numeric_cols)
                logger.info("Özellikler ölçeklendirildi")
            except Exception as e:
                logger.warning(f"Ölçeklendirme hatası: {str(e)}")
            
            # Metadata oluştur
            metadata = {
                "original_shape": data.shape,
                "cleaned_shape": df.shape,
                "missing_values_handled": missing_stats['total_missing'] > 0,
                "outliers_handled": True,
                "feature_names": df.columns.tolist()
            }
            
            logger.info("Veri işleme tamamlandı")
            return {
                "status": "ok",
                "metadata": metadata,
                "clean_data": df.values
            }
            
        except Exception as e:
            logger.error(f"Veri işleme hatası: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

class DataProcessorAgent:
    """Ajan 2: Kümeleme analizi ve model yönetimi."""
    
    def __init__(self):
        self.static_optimizer = ClusteringOptimizer()
        self.streaming_model = AutoCluster()
        
    async def analyze_data(self, data: np.ndarray, method: str = "static") -> Dict[str, Any]:
        """Veriyi analiz eder ve kümeleme yapar."""
        try:
            logger.info(f"Kümeleme analizi başlıyor. Metod: {method}")
            
            if method == "static":
                # Statik kümeleme
                try:
                    # Modeli eğit
                    self.static_optimizer.fit(data)
                    logger.info("Model eğitimi tamamlandı")
                    
                    # Tahmin yap
                    labels = self.static_optimizer.predict(data)
                    logger.info("Tahminler yapıldı")
                    
                    # Metrikleri hesapla
                    metrics = {
                        "silhouette_score": float(self.static_optimizer.best_score),
                        "best_algorithm": self.static_optimizer.best_params.get("algorithm", "unknown"),
                        "n_clusters": len(np.unique(labels))
                    }
                    logger.info(f"Metrikler hesaplandı: {metrics}")
                    
                except Exception as e:
                    logger.error(f"Statik kümeleme hatası: {str(e)}", exc_info=True)
                    raise
                
            else:
                # Streaming kümeleme
                try:
                    labels = self.streaming_model.partial_fit(data)
                    stats = self.streaming_model.get_cluster_stats()
                    metrics = {
                        "cluster_distribution": stats.get("current_distribution", []),
                        "total_samples": stats.get("total_samples_processed", 0),
                        "n_clusters": len(stats.get("current_distribution", []))
                    }
                    logger.info(f"Streaming kümeleme tamamlandı: {metrics}")
                    
                except Exception as e:
                    logger.error(f"Streaming kümeleme hatası: {str(e)}", exc_info=True)
                    raise
            
            # Görselleştirmeleri oluştur
            plot_paths = self._generate_plot_paths()
            logger.info(f"Görselleştirmeler oluşturuldu: {len(plot_paths)} adet")
            
            logger.info("Kümeleme analizi tamamlandı")
            return {
                "status": "ok",
                "cluster_labels": labels.tolist(),
                "best_model_info": metrics,
                "visualization_links": plot_paths
            }
            
        except Exception as e:
            logger.error(f"Kümeleme analizi hatası: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_plot_paths(self) -> List[str]:
        """Görselleştirme dosyalarının yollarını döndürür."""
        try:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            return [str(p) for p in output_dir.glob("*.png")]
        except Exception as e:
            logger.error(f"Görselleştirme hatası: {str(e)}")
            return []

class ResultPresenterAgent:
    """Ajan 3: Dil modeli entegrasyonu ve sonuç sunumu."""
    
    def __init__(self):
        try:
            self.model = genai.GenerativeModel("gemini-pro")
        except Exception as e:
            logger.error(f"Gemini API başlatma hatası: {str(e)}")
            raise
        
    async def explain_results(self, analysis_results: Dict[str, Any], user_query: Optional[str] = None) -> Dict[str, Any]:
        """Analiz sonuçlarını açıklar ve kullanıcı sorularını yanıtlar."""
        try:
            logger.info("Sonuçlar açıklanıyor")
            
            # Temel prompt oluştur
            base_prompt = self._create_base_prompt(analysis_results)
            
            # Kullanıcı sorusu varsa ekle
            if user_query:
                prompt = f"{base_prompt}\n\nKullanıcı Sorusu: {user_query}"
            else:
                prompt = base_prompt
            
            # Gemini API'yi çağır
            response = await self._generate_response(prompt)
            
            logger.info("Sonuçlar başarıyla açıklandı")
            return {
                "status": "ok",
                "textual_explanation": response,
                "raw_analysis": analysis_results
            }
            
        except Exception as e:
            logger.error(f"Sonuç açıklama hatası: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _create_base_prompt(self, results: Dict[str, Any]) -> str:
        """Temel prompt'u oluşturur."""
        cluster_info = results.get('best_model_info', {})
        n_clusters = cluster_info.get('n_clusters', 0)
        algorithm = cluster_info.get('best_algorithm', 'bilinmiyor')
        
        return f"""Aşağıdaki kümeleme analizi sonuçlarını detaylı bir şekilde açıkla:

Kümeleme Sonuçları:
- Algoritma: {algorithm}
- Küme Sayısı: {n_clusters}
- Model Bilgisi: {cluster_info}

Lütfen şunları açıkla:
1. Kümelerin genel dağılımı nasıl?
2. Her kümenin belirgin özellikleri neler?
3. Bu sonuçlardan çıkarılabilecek önemli içgörüler neler?"""
    
    async def _generate_response(self, prompt: str) -> str:
        """Gemini API'yi kullanarak yanıt üretir."""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API hatası: {str(e)}")
            return f"Yanıt üretilirken hata oluştu: {str(e)}" 