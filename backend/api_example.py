import requests
import numpy as np
import pandas as pd
from pathlib import Path
import time
import json

def generate_sample_data(n_samples: int = 10, n_features: int = 4, scale: float = 0.5):
    """Örnek veri oluşturur."""
    # Çok boyutlu normal dağılımlı veri oluştur
    centers = [
        [0] * n_features,
        [3] * n_features,
        [-3] * n_features
    ]
    
    X = []
    samples_per_center = n_samples // len(centers)
    for center in centers:
        cluster = np.random.normal(loc=center, scale=scale, 
                                 size=(samples_per_center, n_features))
        X.append(cluster)
    
    return np.vstack(X)

def test_static_clustering():
    """Test static clustering API endpoints."""
    print("\nTesting Static Clustering API...")
    
    # Model yükleme
    response = requests.post(
        "http://localhost:8000/load_model",
        json={
            "model_path": "output/models/best_clustering_model.joblib",
            "method": "static"
        }
    )
    print("Model Yükleme:", response.json())
    
    # Model bilgisi alma
    response = requests.get("http://localhost:8000/model_info")
    print("Model Bilgisi:", response.json())
    
    # Örnek veri oluştur - PCA boyutunda (2 özellik)
    X = generate_sample_data(n_samples=30, n_features=2, scale=0.1)
    
    # Tahmin yap
    data = {
        "data": [{"features": row.tolist()} for row in X]
    }
    response = requests.post(
        "http://localhost:8000/predict",
        json=data
    )
    print("Tahmin Sonuçları:", response.json())

def test_streaming_clustering():
    """Test streaming clustering API endpoints."""
    print("\nTesting Streaming Clustering API...")
    
    # Model yükleme
    response = requests.post(
        "http://localhost:8000/load_model",
        json={
            "model_path": "output/streaming/model_state",
            "method": "streaming"
        }
    )
    print("Model Yükleme:", response.json())
    
    # Model bilgisi alma
    response = requests.get("http://localhost:8000/model_info")
    print("Model Bilgisi:", response.json())
    
    # Streaming veri simülasyonu
    for batch in range(3):
        print(f"\nBatch {batch + 1}")
        
        # Örnek veri oluştur - Streaming model için 4 özellik
        X = generate_sample_data(n_samples=15, n_features=4, scale=0.5)
        
        # Veriyi gönder ve model güncelle
        data = {
            "data": [{"features": row.tolist()} for row in X]
        }
        response = requests.post(
            "http://localhost:8000/partial_fit",
            json=data
        )
        print("Kısmi Eğitim Sonuçları:", response.json())
        
        # Tahmin yap
        response = requests.post(
            "http://localhost:8000/predict",
            json=data
        )
        print("Tahmin Sonuçları:", response.json())
        
        time.sleep(1)  # Simüle edilmiş gecikme

if __name__ == "__main__":
    print("API Test Başlıyor...")
    print("Not: API servisinin çalışır durumda olduğundan emin olun (uvicorn api_service:app --reload)")
    
    try:
        # Statik kümeleme testi
        test_static_clustering()
        
        # Streaming kümeleme testi
        test_streaming_clustering()
        
    except requests.exceptions.ConnectionError:
        print("\nHata: API servisine bağlanılamadı!")
        print("Lütfen API servisinin çalıştığından emin olun:")
        print("Terminal'de şu komutu çalıştırın: uvicorn api_service:app --reload") 