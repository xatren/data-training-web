import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import IncrementalPCA
import matplotlib.pyplot as plt
from typing import Union, List, Dict, Optional, Tuple
import logging
from pathlib import Path
import joblib
from datetime import datetime
import json
from collections import deque

class AutoCluster:
    """Gerçek zamanlı/streaming veri için otomatik kümeleme sınıfı."""
    
    def __init__(self, base_model: Optional[BaseEstimator] = None,
                 config: Optional[Dict] = None,
                 buffer_size: int = 1000):
        """
        Args:
            base_model: Temel kümeleme modeli (varsayılan: MiniBatchKMeans)
            config: Konfigürasyon ayarları
            buffer_size: Tampon bellek boyutu
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        self.buffer_size = buffer_size
        self.data_buffer = deque(maxlen=buffer_size)
        self.label_history = []
        self.metric_history = []
        
        # Varsayılan model MiniBatchKMeans
        self.model = base_model or MiniBatchKMeans(
            n_clusters=self.config.get('n_clusters', 3),
            random_state=42
        )
        
        # Online öğrenme için gerekli dönüştürücüler
        self.scaler = StandardScaler()
        self.ipca = IncrementalPCA(
            n_components=self.config.get('n_components', 0.95)
        )
        
        self.is_initialized = False
        
    def _setup_logger(self) -> logging.Logger:
        """Logger ayarlarını yapılandırır."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _initialize_with_batch(self, X: np.ndarray):
        """İlk batch ile modeli başlatır."""
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.ipca.fit(X_scaled)
        X_pca = self.ipca.transform(X_scaled)
        
        self.model.fit(X_pca)
        self.is_initialized = True
        
        self.logger.info("Model başlatıldı")
        self.logger.info(f"PCA bileşen sayısı: {self.ipca.n_components_}")
        
    def partial_fit(self, X: np.ndarray, update_buffer: bool = True) -> np.ndarray:
        """
        Yeni veriyi kullanarak modeli günceller.
        
        Args:
            X: Yeni veri batch'i
            update_buffer: Tampon belleği güncelle
            
        Returns:
            np.ndarray: Küme etiketleri
        """
        if not self.is_initialized:
            self._initialize_with_batch(X)
        
        # Veriyi ölçeklendir
        X_scaled = self.scaler.transform(X)
        
        # PCA uygula
        X_pca = self.ipca.transform(X_scaled)
        
        # Modeli güncelle ve tahmin yap
        if hasattr(self.model, 'partial_fit'):
            self.model.partial_fit(X_pca)
        else:
            self.model.fit(X_pca)
            
        labels = self.model.predict(X_pca)
        
        # Tampon belleği güncelle
        if update_buffer:
            for sample in X:
                self.data_buffer.append(sample)
        
        # Geçmiş bilgileri kaydet
        self.label_history.append({
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(X),
            'cluster_sizes': np.bincount(labels).tolist()
        })
        
        if hasattr(self.model, 'inertia_'):
            self.metric_history.append({
                'timestamp': datetime.now().isoformat(),
                'inertia': float(self.model.inertia_)
            })
        
        return labels
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Yeni veri için tahmin yapar.
        
        Args:
            X: Tahmin yapılacak veri
            
        Returns:
            np.ndarray: Küme etiketleri
        """
        if not self.is_initialized:
            raise ValueError("Model henüz başlatılmamış!")
            
        X_scaled = self.scaler.transform(X)
        X_pca = self.ipca.transform(X_scaled)
        return self.model.predict(X_pca)
    
    def get_cluster_stats(self) -> Dict:
        """
        Küme istatistiklerini hesaplar.
        
        Returns:
            Dict: Küme istatistikleri
        """
        if not self.label_history:
            return {}
            
        latest = self.label_history[-1]
        historical = pd.DataFrame([h['cluster_sizes'] for h in self.label_history])
        
        stats = {
            'current_distribution': latest['cluster_sizes'],
            'mean_distribution': historical.mean().tolist(),
            'std_distribution': historical.std().tolist(),
            'total_samples_processed': sum(h['n_samples'] for h in self.label_history)
        }
        
        return stats
    
    def plot_cluster_evolution(self, save_path: Optional[Union[str, Path]] = None):
        """Küme boyutlarının zaman içindeki değişimini görselleştirir."""
        if not self.label_history:
            self.logger.warning("Henüz veri işlenmemiş!")
            return
            
        historical = pd.DataFrame([h['cluster_sizes'] for h in self.label_history])
        timestamps = [datetime.fromisoformat(h['timestamp']) for h in self.label_history]
        
        plt.figure(figsize=(12, 6))
        for i in range(historical.shape[1]):
            plt.plot(timestamps, historical[i], label=f'Küme {i}')
            
        plt.xlabel('Zaman')
        plt.ylabel('Küme Boyutu')
        plt.title('Küme Boyutlarının Zamanla Değişimi')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'cluster_evolution.png')
        else:
            plt.show()
            
        plt.close()
        
    def plot_metric_evolution(self, save_path: Optional[Union[str, Path]] = None):
        """Model metriklerinin zaman içindeki değişimini görselleştirir."""
        if not self.metric_history:
            self.logger.warning("Henüz metrik kaydedilmemiş!")
            return
            
        metrics_df = pd.DataFrame(self.metric_history)
        metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
        
        plt.figure(figsize=(12, 6))
        plt.plot(metrics_df['timestamp'], metrics_df['inertia'], 'b-')
        plt.xlabel('Zaman')
        plt.ylabel('Inertia')
        plt.title('Model Performansının Zamanla Değişimi')
        plt.grid(True)
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'metric_evolution.png')
        else:
            plt.show()
            
        plt.close()
        
    def save_state(self, save_path: Union[str, Path]):
        """
        Model durumunu kaydeder.
        
        Args:
            save_path: Kayıt dizini
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Model ve dönüştürücüleri kaydet
        joblib.dump(self.model, save_path / 'model.joblib')
        joblib.dump(self.scaler, save_path / 'scaler.joblib')
        joblib.dump(self.ipca, save_path / 'ipca.joblib')
        
        # Geçmiş bilgileri JSON olarak kaydet
        with open(save_path / 'history.json', 'w') as f:
            json.dump({
                'label_history': self.label_history,
                'metric_history': self.metric_history
            }, f)
            
        # Konfigürasyon
        with open(save_path / 'config.json', 'w') as f:
            json.dump({
                'buffer_size': self.buffer_size,
                'config': self.config,
                'is_initialized': self.is_initialized
            }, f)
            
        self.logger.info(f"Model durumu kaydedildi: {save_path}")
        
    def load_state(self, load_path: Union[str, Path]):
        """
        Model durumunu yükler.
        
        Args:
            load_path: Yükleme dizini
        """
        load_path = Path(load_path)
        
        # Model ve dönüştürücüleri yükle
        self.model = joblib.load(load_path / 'model.joblib')
        self.scaler = joblib.load(load_path / 'scaler.joblib')
        self.ipca = joblib.load(load_path / 'ipca.joblib')
        
        # Geçmiş bilgileri yükle
        with open(load_path / 'history.json', 'r') as f:
            history = json.load(f)
            self.label_history = history['label_history']
            self.metric_history = history['metric_history']
            
        # Konfigürasyon
        with open(load_path / 'config.json', 'r') as f:
            config = json.load(f)
            self.buffer_size = config['buffer_size']
            self.config = config['config']
            self.is_initialized = config['is_initialized']
            
        self.logger.info("Model durumu yüklendi") 