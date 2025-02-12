from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
from pydantic import BaseModel, Field, HttpUrl, AnyUrl
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

# Router oluştur
router = APIRouter()

# Pydantic modelleri
class DataInput(BaseModel):
    data: List[List[float]]
    method: str = "static"  # "static" veya "streaming"

class UserQuery(BaseModel):
    query: str
    analysis_id: Optional[str] = None

class CSVAnalysisRequest(BaseModel):
    file_url: str
    file_name: str

    class Config:
        # Tüm string değerleri kabul et
        json_schema_extra = {
            "example": {
                "file_url": "https://firebasestorage.googleapis.com/...",
                "file_name": "example.csv"
            }
        }

class DynamicData(BaseModel):
    """Dinamik veri modeli - herhangi bir alanı kabul eder"""
    __root__: Dict[str, Any]

    class Config:
        extra = "allow"  # Tüm ekstra alanları kabul et

class AnalysisRequest(BaseModel):
    """Dinamik veri analizi isteği için model."""
    data: List[Dict[str, Any]]  # Herhangi bir yapıdaki veriyi kabul et
    method: str = "standard"
    parameters: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "column1": "value1",
                        "column2": 123,
                        # Diğer sütunlar dinamik olarak eklenebilir
                    }
                ],
                "method": "standard",
                "parameters": {}
            }
        }

# Global ajan nesneleri
collector = DataCollectorAgent()
processor = DataProcessorAgent()
presenter = ResultPresenterAgent()

# Analiz sonuçlarını geçici olarak saklamak için
analysis_cache: Dict[str, Dict[str, Any]] = {}

# API başlangıcında
for directory in ['output', 'uploads', 'logs']:
    path = Path(directory)
    path.mkdir(exist_ok=True)
    logger.info(f"Directory created/checked: {path}")

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

@router.post("/analyze/csv")
async def analyze_csv(request: CSVAnalysisRequest):
    """CSV dosyasını analiz eder ve sonuçları döndürür."""
    try:
        logger.info(f"CSV analiz isteği: {request.file_name}")

        # Firebase'den dosyayı indir
        try:
            response = requests.get(
                request.file_url,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': '*/*'
                },
                timeout=30,
                verify=False
            )
            
            if not response.ok:
                logger.error(f"Dosya indirme hatası: {response.status_code}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Dosya indirilemedi: {response.status_code}"
                )

            content = response.content.decode('utf-8-sig')
            
        except Exception as e:
            logger.error(f"Dosya indirme hatası: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

        # CSV'yi DataFrame'e dönüştür ve veri tiplerini otomatik belirle
        try:
            df = pd.read_csv(
                StringIO(content),
                dtype=None,  # Otomatik tip belirleme
                na_values=['NA', 'missing', ''],  # Eksik değerleri tanımla
                parse_dates=True,  # Tarih sütunlarını otomatik tanı
            )
            
            if df.empty:
                raise ValueError("CSV dosyası boş")

            # Veri tiplerini belirle
            dtypes = df.dtypes.to_dict()
            column_types = {
                col: str(dtype) for col, dtype in dtypes.items()
            }

            logger.info(f"Sütun tipleri: {column_types}")
            logger.info(f"DataFrame boyutu: {df.shape}")

            # Temel istatistikler
            stats = {
                "satir_sayisi": len(df),
                "sutun_sayisi": len(df.columns),
                "sutunlar": df.columns.tolist(),
                "veri_tipleri": column_types,
                "sayisal_sutunlar": df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                "kategorik_sutunlar": df.select_dtypes(include=['object', 'category']).columns.tolist(),
                "tarih_sutunlari": df.select_dtypes(include=['datetime64']).columns.tolist()
            }

            # Görselleştirmeler
            visualizations = []

            # Her sütun tipi için uygun görselleştirme
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    # Sayısal sütunlar için histogram
                    plt.figure(figsize=(10, 6))
                    sns.histplot(data=df, x=col)
                    plt.title(f'{col} Dağılımı')
                    plt.tight_layout()
                    file_name = f'{col.lower()}_dagilimi.png'
                    plt.savefig(output_dir / file_name)
                    plt.close()
                    visualizations.append(file_name)
                elif df[col].dtype in ['object', 'category']:
                    # Kategorik sütunlar için bar plot (eğer çok fazla unique değer yoksa)
                    if df[col].nunique() <= 20:
                        plt.figure(figsize=(10, 6))
                        df[col].value_counts().plot(kind='bar')
                        plt.title(f'{col} Dağılımı')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        file_name = f'{col.lower()}_dagilimi.png'
                        plt.savefig(output_dir / file_name)
                        plt.close()
                        visualizations.append(file_name)

            # Korelasyon matrisi (sayısal sütunlar için)
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 1:
                plt.figure(figsize=(12, 8))
                sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')
                plt.title('Korelasyon Matrisi')
                plt.tight_layout()
                plt.savefig(output_dir / 'korelasyon_matrisi.png')
                plt.close()
                visualizations.append('korelasyon_matrisi.png')

            # Analiz metni oluştur
            analysis_text = self.create_analysis_text(df, stats)

            # Gemini analizi
            gemini_results = await presenter.explain_results({"analysis": analysis_text})

            return {
                "status": "success",
                "message": "Analiz tamamlandı",
                "data": {
                    "stats": stats,
                    "visualization_files": visualizations,
                    "gemini_analysis": gemini_results["textual_explanation"]
                }
            }

        except Exception as e:
            logger.error(f"CSV analiz hatası: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    def create_analysis_text(self, df: pd.DataFrame, stats: Dict) -> str:
        """Analiz metni oluşturur."""
        text = f"""
        Veri seti analizi:
        - Toplam {stats['satir_sayisi']} satır ve {stats['sutun_sayisi']} sütun
        - Sütunlar ve tipleri:
        """
        
        for col, dtype in stats['veri_tipleri'].items():
            text += f"\n  - {col}: {dtype}"
        
        text += "\n\nİstatistikler:"
        
        # Sayısal sütunlar için istatistikler
        for col in stats['sayisal_sutunlar']:
            text += f"\n\n{col}:"
            text += f"\n  - Ortalama: {df[col].mean():.2f}"
            text += f"\n  - Medyan: {df[col].median():.2f}"
            text += f"\n  - Std: {df[col].std():.2f}"
            text += f"\n  - Min: {df[col].min():.2f}"
            text += f"\n  - Max: {df[col].max():.2f}"

        # Kategorik sütunlar için dağılımlar
        for col in stats['kategorik_sutunlar']:
            if df[col].nunique() <= 10:
                text += f"\n\n{col} dağılımı:"
                value_counts = df[col].value_counts()
                for val, count in value_counts.items():
                    text += f"\n  - {val}: {count} ({(count/len(df)*100):.1f}%)"

        return text 