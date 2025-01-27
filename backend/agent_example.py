import asyncio
import numpy as np
import requests
import json
from typing import Dict, Any
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentClient:
    """Ajan tabanlı sistemi kullanmak için istemci sınıfı."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def analyze_data(self, data: np.ndarray, method: str = "static") -> Dict[str, Any]:
        """Veriyi analiz eder."""
        try:
            # Veriyi kontrol et
            if not isinstance(data, np.ndarray):
                raise ValueError("Veri numpy array formatında olmalıdır")
            
            if data.size == 0:
                raise ValueError("Veri boş olamaz")
            
            if not np.isfinite(data).all():
                raise ValueError("Veri içinde sonsuz veya NaN değerler var")
            
            url = f"{self.base_url}/analyze"
            payload = {
                "data": data.tolist(),
                "method": method
            }
            
            logger.info(f"Analiz isteği gönderiliyor. Veri boyutu: {data.shape}")
            
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                logger.error("API isteği zaman aşımına uğradı")
                raise TimeoutError("API isteği zaman aşımına uğradı")
            except requests.exceptions.RequestException as e:
                logger.error(f"API isteği başarısız: {str(e)}")
                raise
            
            result = response.json()
            logger.info("Analiz isteği başarılı")
            return result
            
        except Exception as e:
            logger.error(f"Analiz hatası: {str(e)}", exc_info=True)
            raise
    
    async def ask_question(self, query: str, analysis_id: str) -> Dict[str, Any]:
        """Analiz hakkında soru sorar."""
        try:
            if not query.strip():
                raise ValueError("Soru boş olamaz")
                
            if not analysis_id.strip():
                raise ValueError("Analiz ID boş olamaz")
            
            url = f"{self.base_url}/ask"
            payload = {
                "query": query,
                "analysis_id": analysis_id
            }
            
            logger.info(f"Soru gönderiliyor. Analiz ID: {analysis_id}")
            
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                logger.error("API isteği zaman aşımına uğradı")
                raise TimeoutError("API isteği zaman aşımına uğradı")
            except requests.exceptions.RequestException as e:
                logger.error(f"API isteği başarısız: {str(e)}")
                raise
            
            result = response.json()
            logger.info("Soru başarıyla gönderildi")
            return result
            
        except Exception as e:
            logger.error(f"Soru gönderme hatası: {str(e)}", exc_info=True)
            raise
    
    async def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Analiz sonuçlarını getirir."""
        try:
            if not analysis_id.strip():
                raise ValueError("Analiz ID boş olamaz")
            
            url = f"{self.base_url}/analysis/{analysis_id}"
            max_retries = 3
            retry_delay = 1  # saniye
            
            logger.info(f"Analiz sonuçları isteniyor. ID: {analysis_id}")
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 404:
                        logger.error(f"Analiz bulunamadı. ID: {analysis_id}")
                        return {
                            "status": "error",
                            "error": "Analiz bulunamadı",
                            "analysis_id": analysis_id
                        }
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    if not result:
                        logger.warning(f"Analiz sonuçları boş. ID: {analysis_id}")
                        return {
                            "status": "warning",
                            "message": "Analiz sonuçları henüz hazır değil",
                            "analysis_id": analysis_id
                        }
                    
                    logger.info("Analiz sonuçları başarıyla alındı")
                    return result
                    
                except requests.exceptions.Timeout:
                    if attempt == max_retries - 1:
                        logger.error("API isteği zaman aşımına uğradı")
                        raise TimeoutError("API isteği zaman aşımına uğradı")
                    logger.warning(f"Zaman aşımı, yeniden deneniyor... Deneme: {attempt + 1}")
                    await asyncio.sleep(retry_delay)
                    
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logger.error(f"API isteği başarısız: {str(e)}")
                        raise
                    logger.warning(f"İstek başarısız, yeniden deneniyor... Deneme: {attempt + 1}")
                    await asyncio.sleep(retry_delay)
            
        except Exception as e:
            logger.error(f"Analiz sonuçları alma hatası: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "analysis_id": analysis_id
            }

async def main():
    # Output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # İstemciyi oluştur
    client = AgentClient()
    
    try:
        # Örnek veri oluştur
        logger.info("Örnek veri oluşturuluyor")
        np.random.seed(42)
        n_samples = 1000
        
        # İki farklı küme oluştur
        cluster1 = np.random.normal(0, 1, (n_samples // 2, 2))
        cluster2 = np.random.normal(3, 1, (n_samples // 2, 2))
        data = np.vstack([cluster1, cluster2])
        
        # Veriyi kontrol et
        if not np.isfinite(data).all():
            raise ValueError("Oluşturulan veride sonsuz veya NaN değerler var")
        
        # Veriyi analiz et
        logger.info("Veri analizi başlıyor")
        try:
            analysis_result = await client.analyze_data(data)
            
            if analysis_result.get("status") == "error":
                logger.error(f"Analiz hatası: {analysis_result.get('error')}")
                return
                
            analysis_id = analysis_result.get("analysis_id")
            if not analysis_id:
                logger.error("Analiz ID bulunamadı")
                return
            
            print("\nAnaliz Sonucu:")
            print(json.dumps(analysis_result, indent=2, ensure_ascii=False))
            
            # Sorular sor
            questions = [
                "Bu veri setindeki kümelerin genel özellikleri neler?",
                "Hangi kümeleme algoritması kullanıldı ve neden?",
                "Kümelerin birbirinden ayrışması ne kadar başarılı?",
                "Genel olarak verimin bu özelliklerine göre bu analizlerle ilgili ne gibi sonuçlar çıkarılabilir?"
            ]
            
            logger.info("Sorular soruluyor")
            for question in questions:
                try:
                    print(f"\nSoru: {question}")
                    answer = await client.ask_question(question, analysis_id)
                    if answer.get("status") == "error":
                        logger.error(f"Soru yanıtlama hatası: {answer.get('error')}")
                        continue
                    print(f"Yanıt: {answer.get('answer', 'Yanıt alınamadı')}")
                except Exception as e:
                    logger.error(f"Soru yanıtlanırken hata: {str(e)}")
                    print(f"Soru yanıtlanamadı: {str(e)}")
            
            # Son analiz sonuçlarını getir
            logger.info("Son analiz sonuçları getiriliyor")
            final_analysis = await client.get_analysis(analysis_id)
            
            if final_analysis.get("status") == "error":
                logger.error(f"Son analiz sonuçları alınamadı: {final_analysis.get('error')}")
                return
                
            print("\nSon Analiz Sonuçları:")
            print(json.dumps(final_analysis, indent=2, ensure_ascii=False))
            
        except Exception as e:
            logger.error(f"Analiz sırasında hata: {str(e)}")
            raise
        
    except Exception as e:
        logger.error(f"Program hatası: {str(e)}", exc_info=True)
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    # Asenkron ana fonksiyonu çalıştır
    asyncio.run(main()) 