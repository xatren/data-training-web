"""
Merkezi Yönetim ve API Sunucusu.

Bu modül, projenin tüm bileşenlerini tek bir noktadan yöneten ana modüldür.
API sunucusunu başlatır, veri analizlerini yönetir ve sonuçları raporlar.

Kullanım:
    python main.py [--port PORT] [--host HOST] [--debug] [--csv CSV_PATH]
"""

import argparse
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# .env dosyasını yükle
load_dotenv()

# Proje modüllerini import et
from src.client.agent_client import AgentClient
from src.config.api_config import get_gemini_model
from src.config.settings import (
    PROJECT_ROOT, OUTPUT_DIR, LOG_DIR,
    DEFAULT_BASE_URL, API_TIMEOUT
)
from src.models.data_models import (
    AnalysisRequest, AnalysisResponse,
    EmployeeData, ClusteringResult
)
from src.utils.logger import logger, setup_logger
from src.utils.csv_helpers import CSVAnalyzer
from src.utils.validators import validate_analysis_id
from src.client.exceptions import (
    AgentClientError, ValidationError,
    APIConnectionError, AnalysisError
)

# FastAPI uygulamasını oluştur
app = FastAPI(
    title="Veri Analiz API",
    description="Verilerinin analizi için REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS ayarlarını ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik dosyalar ve şablonlar için dizinleri ayarla
static_dir = PROJECT_ROOT / "static"
templates_dir = PROJECT_ROOT / "templates"
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Statik dosyaları ve şablonları yapılandır
app.mount("/static", StaticFiles(directory="output"), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Global değişkenler
client: Optional[AgentClient] = None
logger = setup_logger("main")

# Ana sayfa HTML şablonu
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Veri Analiz API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .endpoints { margin: 20px 0; }
        .endpoint { margin: 10px 0; padding: 10px; background: #f5f5f5; }
        .method { font-weight: bold; color: #0066cc; }
        .docs-link { margin-top: 20px; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Veri Analiz API</h1>
    <p>Çalışan verilerinin analizi için REST API servisi.</p>
    
    <div class="endpoints">
        <h2>Kullanılabilir Endpoint'ler:</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> /health
            <p>API servisinin durumunu kontrol eder.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /analyze
            <p>Veri analizi gerçekleştirir.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /analyze/csv
            <p>CSV dosyası analizi gerçekleştirir.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /analysis/{analysis_id}
            <p>Analiz sonuçlarını sorgular.</p>
        </div>
    </div>
    
    <div class="docs-link">
        <p>Detaylı API dokümantasyonu için:</p>
        <ul>
            <li><a href="/docs">Swagger UI</a></li>
            <li><a href="/redoc">ReDoc</a></li>
        </ul>
    </div>
</body>
</html>
"""

def check_environment() -> None:
    """Çevresel değişkenleri kontrol eder."""
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY çevresel değişkeni tanımlanmamış!")
        sys.exit(1)

def setup_directories() -> None:
    """Gerekli dizinleri oluşturur ve kontrol eder."""
    try:
        for directory in [OUTPUT_DIR, LOG_DIR, static_dir, templates_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Ana sayfa şablonunu oluştur
        index_path = templates_dir / "index.html"
        if not index_path.exists():
            index_path.write_text(INDEX_HTML)

        logger.info(f"Dizinler hazır: {OUTPUT_DIR}, {LOG_DIR}, {static_dir}, {templates_dir}")
    except Exception as e:
        logger.error(f"Dizin oluşturma hatası: {str(e)}")
        sys.exit(1)

def initialize_client() -> None:
    """AgentClient nesnesini başlatır ve yapılandırır."""
    global client
    try:
        client = AgentClient()
        logger.info("AgentClient başarıyla başlatıldı")
    except Exception as e:
        logger.error(f"AgentClient başlatma hatası: {str(e)}")
        sys.exit(1)

@app.on_event("startup")
async def startup_event():
    """API sunucusu başlangıç olayı."""
    try:
        check_environment()
        setup_directories()
        initialize_client()
        logger.info("API sunucusu başarıyla başlatıldı")
    except Exception as e:
        logger.error(f"Başlangıç hatası: {str(e)}")
        sys.exit(1)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Ana sayfa endpoint'i."""
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Ana sayfa hatası: {str(e)}")
        return HTMLResponse(INDEX_HTML)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Sağlık kontrolü endpoint'i."""
    return {
        "status": "healthy",
        "client_status": "ready" if client else "not_initialized",
        "version": "1.0.0"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest) -> AnalysisResponse:
    """Veri analizi endpoint'i."""
    try:
        if not client:
            raise APIConnectionError("AgentClient başlatılmamış")
            
        result = await client.analyze_data(request.data)
        logger.info(f"Analiz tamamlandı: {result['analysis_id']}")
        return AnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Analiz hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/csv", response_model=AnalysisResponse)
async def analyze_csv(file_path: str) -> AnalysisResponse:
    """CSV dosyası analizi endpoint'i."""
    try:
        if not client:
            raise APIConnectionError("AgentClient başlatılmamış")
            
        # Dosya yolunu doğrula
        csv_path = Path(file_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV dosyası bulunamadı: {file_path}")
            
        result = await client.analyze_csv(str(csv_path))
        logger.info(f"CSV analizi tamamlandı: {result['analysis_id']}")
        return AnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"CSV analiz hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str) -> AnalysisResponse:
    """Analiz sonuçları sorgulama endpoint'i."""
    try:
        if not client:
            raise APIConnectionError("AgentClient başlatılmamış")
            
        analysis_id = validate_analysis_id(analysis_id)
        result = await client.get_analysis(analysis_id)
        return AnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Analiz sorgulama hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """404 hatası için özel işleyici."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Sayfa bulunamadı",
            "message": "İstenen sayfa mevcut değil",
            "docs": "/docs veya /redoc adreslerini ziyaret edin"
        }
    )

def parse_args() -> argparse.Namespace:
    """Komut satırı argümanlarını ayrıştırır."""
    parser = argparse.ArgumentParser(
        description="Veri Analiz API Sunucusu",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--port", type=int, default=8000,
                       help="Sunucu port numarası")
    parser.add_argument("--host", type=str, default="127.0.0.1",
                       help="Sunucu host adresi")
    parser.add_argument("--debug", action="store_true",
                       help="Debug modu")
    parser.add_argument("--csv", type=str,
                       help="Analiz edilecek CSV dosyasının yolu")
    return parser.parse_args()

async def run_analysis_example(csv_path: Optional[str] = None) -> None:
    """Örnek CSV analizi çalıştırır."""
    try:
        if not client:
            raise APIConnectionError("AgentClient başlatılmamış")
            
        # CSV dosyasını belirle
        if csv_path:
            file_path = Path(csv_path)
        elif csv_path is None:
            file_path = PROJECT_ROOT / "Sample_01.csv"
        else:
            file_path = Path("Sample_01.csv")
            raise ValueError("CSV dosyası belirtilmedi")
               
        if not file_path.exists():
            raise FileNotFoundError(f"CSV dosyası bulunamadı: {file_path}")
            
        logger.info(f"CSV analizi başlıyor: {file_path}")
        result = await client.analyze_csv(str(file_path))
        
        logger.info("CSV analizi tamamlandı")
        logger.info(f"Analiz ID: {result['analysis_id']}")
        logger.info(f"Sonuçlar: {result}")
        
    except Exception as e:
        logger.error(f"Örnek analiz hatası: {str(e)}")
        sys.exit(1)

def main() -> None:
    """Ana uygulama fonksiyonu."""
    try:
        args = parse_args()
        
        # Çevresel değişkenleri ve dizinleri kontrol et
        check_environment()
        setup_directories()
        initialize_client()
        
        if args.debug or args.csv:
            # Debug modunda veya CSV analizi modunda
            asyncio.run(run_analysis_example(args.csv))
        else:
            # API sunucusunu başlat
            logger.info(f"API sunucusu başlatılıyor: {args.host}:{args.port}")
            uvicorn.run(
                "main:app",
                host=args.host,
                port=args.port,
                reload=True,
                log_level="info"
            )
            
    except Exception as e:
        logger.error(f"Program hatası: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 