from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import joblib
from clustering import ClusteringOptimizer
from auto_cluster import AutoCluster
from sklearn.cluster import DBSCAN

app = FastAPI(
    title="Kümeleme API",
    description="Veri kümeleme ve analiz servisi",
    version="1.0.0"
)

class DataPoint(BaseModel):
    features: List[float]

class DataBatch(BaseModel):
    data: List[DataPoint]
    
class ClusteringResponse(BaseModel):
    labels: List[int]
    metrics: Optional[Dict] = None

class ModelConfig(BaseModel):
    model_path: str
    method: str = "static"  # "static" veya "streaming"

class Config:    
    protected_namespaces = ()

# Global model nesneleri
static_model: Optional[ClusteringOptimizer] = None
streaming_model: Optional[AutoCluster] = None

@app.post("/load_model")
async def load_model(config: ModelConfig):
    """Model yükler."""
    global static_model, streaming_model
    
    try:
        if config.method == "static":
            optimizer = ClusteringOptimizer()
            optimizer.load_model(config.model_path)
            static_model = optimizer
        else:
            auto_cluster = AutoCluster()
            auto_cluster.load_state(config.model_path)
            streaming_model = auto_cluster
            
        return {"message": "Model başarıyla yüklendi"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model yüklenirken hata oluştu: {str(e)}"
        )

@app.post("/predict", response_model=ClusteringResponse)
async def predict(data: DataBatch):
    """Verilen örnekler için küme tahminleri yapar."""
    if static_model is None and streaming_model is None:
        raise HTTPException(
            status_code=400,
            detail="Önce bir model yüklenmelidir"
        )
        
    try:
        # Veriyi numpy array'e dönüştür
        X = np.array([point.features for point in data.data])
        
        if static_model is not None:
            # DBSCAN için özel işlem
            if isinstance(static_model.best_model, DBSCAN):
                # DBSCAN için fit_predict kullan
                labels = static_model.best_model.fit_predict(X)
            else:
                labels = static_model.best_model.predict(X)
            
            response = {
                "labels": labels.tolist(),
                "metrics": None
            }
            
        else:
            # Streaming model için tahmin yap
            labels = streaming_model.predict(X)
            stats = streaming_model.get_cluster_stats()
            
            response = {
                "labels": labels.tolist(),
                "metrics": {
                    "cluster_distribution": stats.get('current_distribution', []),
                    "total_samples": stats.get('total_samples_processed', 0)
                }
            }
            
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tahmin yapılırken hata oluştu: {str(e)}"
        )

@app.post("/partial_fit")
async def partial_fit(data: DataBatch):
    """Streaming model için kısmi eğitim yapar."""
    if streaming_model is None:
        raise HTTPException(
            status_code=400,
            detail="Streaming model yüklenmemiş"
        )
        
    try:
        X = np.array([point.features for point in data.data])
        labels = streaming_model.partial_fit(X)
        stats = streaming_model.get_cluster_stats()
        
        return {
            "labels": labels.tolist(),
            "current_distribution": stats.get('current_distribution', []),
            "total_samples": stats.get('total_samples_processed', 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Kısmi eğitim sırasında hata oluştu: {str(e)}"
        )

@app.get("/model_info")
async def get_model_info():
    """Yüklü model hakkında bilgi verir."""
    if static_model is not None:
        return {
            "model_type": "static",
            "algorithm": static_model.best_params.get('algorithm', 'unknown'),
            "parameters": static_model.best_params,
            "score": static_model.best_score
        }
    elif streaming_model is not None:
        stats = streaming_model.get_cluster_stats()
        return {
            "model_type": "streaming",
            "total_samples_processed": stats.get('total_samples_processed', 0),
            "current_distribution": stats.get('current_distribution', []),
            "mean_distribution": stats.get('mean_distribution', [])
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Henüz bir model yüklenmemiş"
        ) 