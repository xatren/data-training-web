import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
import aiohttp
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import pandas as pd
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CSVAnalyzerAPI")

# Ana sunucu (main.py) URL'i
MAIN_SERVER_URL = "http://127.0.0.1:8000"

# FastAPI application instance
app = FastAPI(
    title="CSV Analyzer API",
    description="Çalışan verilerinin CSV analizi için API.",
    version="1.0.0"
)

# Models
class AnalysisResponse(BaseModel):
    status: str
    analysis_id: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CSVAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """CSV dosyasını yükler."""
        try:
            self.df = pd.read_csv(self.file_path, encoding='utf-8')
            logger.info(f"CSV dosyası başarıyla yüklendi: {self.file_path}")
        except Exception as e:
            logger.error(f"CSV dosyası yüklenirken hata: {str(e)}")
            raise
    
    def analyze(self) -> Dict[str, Any]:
        """
        CSV verilerini analiz eder ve sonuçları döndürür.
        """
        try:
            results = {
                "temel_istatistikler": self._get_basic_stats(),
                "departman_analizi": self._get_department_analysis(),
                "sehir_analizi": self._get_city_analysis(),
                "maas_analizi": self._get_salary_analysis(),
                "analiz_zamani": datetime.now().isoformat()
            }
            return results
        except Exception as e:
            logger.error(f"Analiz hatası: {str(e)}")
            raise
    
    def _get_basic_stats(self) -> Dict[str, Any]:
        """Temel istatistikleri hesaplar."""
        return {
            "toplam_calisan": len(self.df),
            "ortalama_maas": float(self.df['Maas'].mean()),
            "medyan_maas": float(self.df['Maas'].median()),
            "min_maas": float(self.df['Maas'].min()),
            "max_maas": float(self.df['Maas'].max())
        }
    
    def _get_department_analysis(self) -> Dict[str, Any]:
        """Departman bazlı analiz yapar."""
        dept_stats = self.df.groupby('Departman').agg({
            'Maas': ['count', 'mean', 'min', 'max']
        }).round(2)
        
        return {
            dept: {
                "calisan_sayisi": int(stats[('Maas', 'count')]),
                "ortalama_maas": float(stats[('Maas', 'mean')]),
                "min_maas": float(stats[('Maas', 'min')]),
                "max_maas": float(stats[('Maas', 'max')])
            }
            for dept, stats in dept_stats.iterrows()
        }
    
    def _get_city_analysis(self) -> Dict[str, Any]:
        """Şehir bazlı analiz yapar."""
        city_counts = self.df['Sehir'].value_counts()
        return {
            "sehir_dagilimi": city_counts.to_dict(),
            "toplam_sehir": len(city_counts)
        }
    
    def _get_salary_analysis(self) -> Dict[str, Any]:
        """Maaş dağılımı analizi yapar."""
        salary_ranges = [
            (0, 10000),
            (10000, 20000),
            (20000, 30000),
            (30000, float('inf'))
        ]
        
        salary_dist = {}
        for start, end in salary_ranges:
            if end == float('inf'):
                label = f"{start}+ TL"
            else:
                label = f"{start}-{end} TL"
            count = len(self.df[
                (self.df['Maas'] >= start) & 
                (self.df['Maas'] < end)
            ])
            salary_dist[label] = count
            
        return {
            "maas_dagilimi": salary_dist,
            "maas_istatistikleri": {
                "ortalama": float(self.df['Maas'].mean()),
                "medyan": float(self.df['Maas'].median()),
                "std": float(self.df['Maas'].std())
            }
        }

async def forward_to_main_server(file_path: str) -> Dict[str, Any]:
    """
    Ana sunucuya (main.py) CSV analiz isteğini iletir.
    
    Args:
        file_path (str): Analiz edilecek CSV dosyasının yolu
        
    Returns:
        Dict[str, Any]: Analiz sonuçları
        
    Raises:
        HTTPException: Sunucu bağlantı hatası veya analiz hatası durumunda
    """
    try:
        params = {"file_path": str(file_path)}
        
        async with aiohttp.ClientSession() as session:
            # Query parametresi olarak gönder
            async with session.post(
                f"{MAIN_SERVER_URL}/analyze/csv",
                params=params,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    logger.info(f"Ana sunucudan başarılı yanıt alındı: {response_data.get('analysis_id')}")
                    return response_data
                else:
                    error_msg = response_data.get("detail", "Ana sunucu hatası")
                    logger.error(f"Ana sunucu hatası: {error_msg}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Ana sunucu hatası: {error_msg}"
                    )
                    
    except aiohttp.ClientError as e:
        error_msg = f"Ana sunucuya bağlanırken hata: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=503,
            detail=error_msg
        )
    except asyncio.TimeoutError:
        error_msg = "Ana sunucu yanıt zaman aşımı"
        logger.error(error_msg)
        raise HTTPException(
            status_code=504,
            detail=error_msg
        )
    except Exception as e:
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

def save_analysis_results(analysis_id: str, results: Dict[str, Any]) -> str:
    """Analiz sonuçlarını JSON dosyası olarak kaydeder."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"analysis_result_{analysis_id}_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    logger.info(f"Analiz sonuçları kaydedildi: {output_file}")
    return str(output_file)

@app.get("/analyze/csv", response_model=AnalysisResponse)
@app.post("/analyze/csv", response_model=AnalysisResponse)
async def analyze_csv(
    file_path: str = Query(..., description="Analiz edilecek CSV dosyasının yolu")
) -> AnalysisResponse:
    """
    CSV dosyasını analiz eder ve sonuçları JSON olarak kaydeder.
    
    Args:
        file_path (str): Analiz edilecek CSV dosyasının yolu
        
    Returns:
        AnalysisResponse: Analiz sonuçları ve durum bilgisi
        
    Raises:
        HTTPException: Dosya bulunamadığında veya analiz hatası durumunda
    """
    try:
        # CSV dosyasını doğrula
        csv_path = Path(file_path)
        if not csv_path.exists():
            error_msg = f"CSV dosyası bulunamadı: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not csv_path.is_file():
            error_msg = f"Belirtilen yol bir dosya değil: {file_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if csv_path.suffix.lower() != '.csv':
            error_msg = f"Dosya CSV formatında değil: {file_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Ana sunucuya isteği ilet
        logger.info(f"CSV analizi başlatılıyor: {file_path}")
        main_server_response = await forward_to_main_server(str(csv_path))
        
        # Analiz sonuçlarını kaydet
        if main_server_response.get("status") == "success":
            try:
                output_file = save_analysis_results(
                    main_server_response["analysis_id"],
                    main_server_response.get("results", {})
                )
                
                logger.info(f"Analiz başarıyla tamamlandı: {output_file}")
                
                return AnalysisResponse(
                    status="success",
                    analysis_id=main_server_response["analysis_id"],
                    results={
                        "analysis_file": output_file,
                        "summary": main_server_response.get("results", {}).get("temel_istatistikler", {})
                    }
                )
            except Exception as e:
                error_msg = f"Sonuçlar kaydedilirken hata: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
        else:
            error_msg = main_server_response.get("error", "Analiz hatası")
            logger.error(f"Ana sunucu analiz hatası: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check():
    """API ve ana sunucu sağlık kontrolü."""
    try:
        # Ana sunucunun sağlık durumunu kontrol et
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{MAIN_SERVER_URL}/health") as response:
                main_server_health = await response.json()
                
                return {
                    "status": "healthy",
                    "version": app.version,
                    "timestamp": datetime.now().isoformat(),
                    "main_server_status": main_server_health
                }
    except Exception as e:
        return {
            "status": "degraded",
            "version": app.version,
            "timestamp": datetime.now().isoformat(),
            "main_server_status": {
                "status": "unreachable",
                "error": str(e)
            }
        }

def main():
    """API uygulamasını çalıştırır."""
    import uvicorn
    
    try:
        logger.info("CSV Analiz API'si başlatılıyor...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8001)),
            log_level="info"
        )
    except Exception as e:
        logger.exception(f"Uygulama başlatma hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
