from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import numpy as np
from agents import DataCollectorAgent, DataProcessorAgent, ResultPresenterAgent
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_preparation import DataPreparation
from clustering_optimizer import ClusteringOptimizer
import shutil
import requests
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

app = FastAPI(
    title="Ajan Tabanlı Kümeleme API",
    description="Veri kümeleme, analiz ve dil modeli entegrasyonu servisi",
    version="1.0.0"
)

# Pydantic modelleri
class DataInput(BaseModel):
    data: List[List[float]]
    method: str = "static"  # "static" veya "streaming"

class UserQuery(BaseModel):
    query: str
    analysis_id: Optional[str] = None

class CSVAnalysisRequest(BaseModel):
    file_url: str = Field(..., min_length=10)
    file_name: str = Field(..., min_length=1)

# Global ajan nesneleri
collector = DataCollectorAgent()
processor = DataProcessorAgent()
presenter = ResultPresenterAgent()

# Analiz sonuçlarını geçici olarak saklamak için
analysis_cache: Dict[str, Dict[str, Any]] = {}

@app.post("/analyze")
async def analyze_data(input_data: DataInput):
    """Veriyi analiz eder ve sonuçları açıklar."""
    try:
        logger.info("Yeni analiz isteği alındı")
        
        # Veriyi numpy array'e dönüştür
        try:
            data = np.array(input_data.data, dtype=np.float64)
            logger.info(f"Veri boyutu: {data.shape}")
        except Exception as e:
            logger.error(f"Veri dönüştürme hatası: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Veri formatı uygun değil: {str(e)}"
            )
        
        # Ajan 1: Veri toplama ve temizleme
        collector_result = await collector.process_data(data)
        if collector_result["status"] != "ok":
            logger.error(f"Veri toplama hatası: {collector_result.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=f"Veri toplama hatası: {collector_result.get('error')}"
            )
        
        # Ajan 2: Kümeleme analizi
        processor_result = await processor.analyze_data(
            collector_result["clean_data"],
            method=input_data.method
        )
        if processor_result["status"] != "ok":
            logger.error(f"Veri işleme hatası: {processor_result.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=f"Veri işleme hatası: {processor_result.get('error')}"
            )
        
        # Ajan 3: Sonuçları açıkla
        presenter_result = await presenter.explain_results(processor_result)
        if presenter_result["status"] != "ok":
            logger.error(f"Sonuç sunumu hatası: {presenter_result.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=f"Sonuç sunumu hatası: {presenter_result.get('error')}"
            )
        
        # Sonuçları önbelleğe al
        analysis_id = f"analysis_{len(analysis_cache) + 1}"
        analysis_cache[analysis_id] = {
            "collector_result": collector_result,
            "processor_result": processor_result,
            "presenter_result": presenter_result
        }
        
        logger.info(f"Analiz tamamlandı. ID: {analysis_id}")
        return {
            "analysis_id": analysis_id,
            "explanation": presenter_result["textual_explanation"],
            "cluster_info": processor_result["best_model_info"],
            "visualization_links": processor_result["visualization_links"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"İşlem sırasında hata oluştu: {str(e)}"
        )

@app.post("/ask")
async def ask_question(query_input: UserQuery):
    """Kullanıcı sorularını yanıtlar."""
    try:
        logger.info(f"Yeni soru alındı. Analiz ID: {query_input.analysis_id}")
        
        if query_input.analysis_id not in analysis_cache:
            logger.error(f"Analiz ID bulunamadı: {query_input.analysis_id}")
            raise HTTPException(
                status_code=404,
                detail="Belirtilen analiz ID'si bulunamadı"
            )
        
        # Önceki analiz sonuçlarını al
        cached_analysis = analysis_cache[query_input.analysis_id]
        processor_result = cached_analysis["processor_result"]
        
        # Ajan 3: Soruyu yanıtla
        presenter_result = await presenter.explain_results(
            processor_result,
            user_query=query_input.query
        )
        
        if presenter_result["status"] != "ok":
            logger.error(f"Soru yanıtlama hatası: {presenter_result.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=f"Soru yanıtlama hatası: {presenter_result.get('error')}"
            )
        
        logger.info("Soru başarıyla yanıtlandı")
        return {
            "answer": presenter_result["textual_explanation"],
            "context": {
                "analysis_id": query_input.analysis_id,
                "original_query": query_input.query
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Soru yanıtlanırken hata oluştu: {str(e)}"
        )

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Belirli bir analiz ID'sine ait sonuçları getirir."""
    try:
        logger.info(f"Analiz sonuçları istendi. ID: {analysis_id}")
        
        if analysis_id not in analysis_cache:
            logger.error(f"Analiz ID bulunamadı: {analysis_id}")
            raise HTTPException(
                status_code=404,
                detail="Belirtilen analiz ID'si bulunamadı"
            )
        
        cached_analysis = analysis_cache[analysis_id]
        
        logger.info("Analiz sonuçları başarıyla getirildi")
        return {
            "analysis_id": analysis_id,
            "collector_metadata": cached_analysis["collector_result"]["metadata"],
            "cluster_info": cached_analysis["processor_result"]["best_model_info"],
            "visualization_links": cached_analysis["processor_result"]["visualization_links"],
            "last_explanation": cached_analysis["presenter_result"]["textual_explanation"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analiz sonuçları getirilirken hata oluştu: {str(e)}"
        )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Uploads klasörünü oluştur
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Dosyayı kaydet
        file_path = upload_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/csv")
async def analyze_csv(request: CSVAnalysisRequest):
    try:
        # URL doğrulama
        if not request.file_url.startswith('https://'):
            raise HTTPException(
                status_code=422,
                detail="Geçersiz dosya URL formatı"
            )
        
        # Dosya indirme
        response = requests.get(request.file_url)
        if not response.ok:
            raise HTTPException(
                status_code=400,
                detail="Dosya indirme başarısız"
            )
        
        # CSV'yi pandas DataFrame'e dönüştür
        try:
            csv_content = StringIO(response.text)
            df = pd.read_csv(csv_content)
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV dosyası okunamadı: {str(e)}"
            )

        # Veri hazırlama
        try:
            prep = DataPreparation()
            df_cleaned = prep.handle_missing_values(df, {col: 'mean' for col in df.columns})
            
            # Kümeleme analizi
            optimizer = ClusteringOptimizer()
            X = df_cleaned.select_dtypes(include=[np.number]).values
            optimizer.fit(X)
            
            # Görselleştirmeler
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            # Departman dağılımı
            if 'Departman' in df.columns:
                plt.figure(figsize=(10, 6))
                df['Departman'].value_counts().plot(kind='bar')
                plt.title('Departman Dağılımı')
                plt.tight_layout()
                plt.savefig(output_dir / 'departman_dagilimi.png')
                plt.close()
            
            # Maaş dağılımı
            if 'Maas' in df.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(data=df, x='Maas')
                plt.title('Maaş Dağılımı')
                plt.tight_layout()
                plt.savefig(output_dir / 'maas_dagilimi.png')
                plt.close()
            
            # Kümeleme görselleştirmesi
            labels = optimizer.predict(X)
            optimizer.plot_clusters_2d(X, labels, save_path=output_dir)
            
            # Gemini analizi
            analysis_results = {
                "cluster_info": {
                    "n_clusters": len(np.unique(labels)),
                    "silhouette_score": optimizer.best_score
                }
            }
            gemini_results = await presenter.explain_results(analysis_results)
            
            return {
                "status": "success",
                "basic_stats": {
                    "toplam_calisan": len(df),
                    "departman_dagilimi": df['Departman'].value_counts().to_dict() if 'Departman' in df.columns else {},
                    "ortalama_maas": float(df['Maas'].mean()) if 'Maas' in df.columns else None
                },
                "clustering_analysis": {
                    "n_clusters": len(np.unique(labels)),
                    "silhouette_score": float(optimizer.best_score)
                },
                "gemini_analysis": gemini_results["textual_explanation"],
                "visualization_files": [
                    str(f) for f in output_dir.glob("*.png")
                ]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Analiz sırasında hata: {str(e)}"
            )
            
    except HTTPException as he:
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sunucu hatası: {str(e)}"
        ) 