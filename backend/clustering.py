import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, silhouette_samples
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, List, Dict, Optional, Tuple, Literal
import logging
from pathlib import Path
import joblib
from tqdm import tqdm

class DimensionalityReducer:
    """Boyut azaltma yöntemlerini yöneten sınıf."""
    
    def __init__(self, method: Literal['pca', 'tsne', 'umap'] = 'pca',
                 n_components: Optional[int] = None,
                 random_state: int = 42,
                 **kwargs):
        """
        Args:
            method: Kullanılacak boyut azaltma yöntemi
            n_components: Hedef boyut sayısı
            random_state: Rastgele sayı üreteci için tohum değeri
            **kwargs: Seçilen yönteme özel parametreler
        """
        self.method = method
        self.n_components = n_components
        self.random_state = random_state
        self.kwargs = kwargs
        self.model = None
        self._setup_model()
        
    def _setup_model(self):
        """Seçilen yönteme göre modeli yapılandırır."""
        if self.method == 'pca':
            self.model = PCA(
                n_components=self.n_components,
                random_state=self.random_state,
                **self.kwargs
            )
        elif self.method == 'tsne':
            self.model = TSNE(
                n_components=self.n_components or 2,
                random_state=self.random_state,
                **self.kwargs
            )
        elif self.method == 'umap':
            self.model = umap.UMAP(
                n_components=self.n_components or 2,
                random_state=self.random_state,
                **self.kwargs
            )
        else:
            raise ValueError(f"Desteklenmeyen boyut azaltma yöntemi: {self.method}")
            
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Veriyi dönüştürür."""
        return self.model.fit_transform(X)
        
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Yeni veriyi dönüştürür."""
        if self.method == 'tsne':
            # t-SNE için yeni veri noktaları direkt dönüştürülemez
            return self.fit_transform(X)
        return self.model.transform(X)
        
    @property
    def explained_variance_ratio_(self) -> Optional[np.ndarray]:
        """Açıklanan varyans oranı (sadece PCA için)."""
        if self.method == 'pca':
            return self.model.explained_variance_ratio_
        return None

class ClusteringOptimizer:
    """Kümeleme algoritmalarını optimize eden ve değerlendiren sınıf."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Args:
            config: Konfigürasyon ayarları
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        self.best_model = None
        self.best_score = -1
        self.best_params = {}
        self.pca = None
        self.scaler = StandardScaler()
        
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
    
    def apply_pca(self, X: np.ndarray, n_components: Optional[int] = None,
                  variance_ratio: float = 0.95) -> Tuple[np.ndarray, PCA]:
        """
        PCA uygular.
        
        Args:
            X: Veri matrisi
            n_components: Bileşen sayısı (None ise variance_ratio kullanılır)
            variance_ratio: Korunacak varyans oranı
            
        Returns:
            Tuple[np.ndarray, PCA]: Dönüştürülmüş veri ve PCA nesnesi
        """
        if n_components is None:
            pca = PCA(n_components=variance_ratio, svd_solver='full')
        else:
            pca = PCA(n_components=n_components)
            
        X_pca = pca.fit_transform(X)
        self.pca = pca
        
        explained_var = np.sum(pca.explained_variance_ratio_)
        self.logger.info(f"PCA sonrası açıklanan varyans: {explained_var:.4f}")
        self.logger.info(f"Seçilen bileşen sayısı: {pca.n_components_}")
        
        return X_pca, pca
    
    def compute_sample_weights(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """
        Veri dengesizliğini ele almak için örnek ağırlıkları hesaplar.
        
        Args:
            X: Veri matrisi
            labels: Küme etiketleri
            
        Returns:
            np.ndarray: Örnek ağırlıkları
        """
        # Küme boyutlarını hesapla
        unique_labels, counts = np.unique(labels, exclude=[-1], return_counts=True)
        
        if len(unique_labels) == 0:
            return np.ones(len(X))
            
        # Her küme için ağırlık hesapla (küçük kümeler daha yüksek ağırlık alır)
        weights_per_cluster = {
            label: 1.0 / count
            for label, count in zip(unique_labels, counts)
        }
        
        # Her örnek için ağırlık ata
        sample_weights = np.ones(len(X))
        for label in unique_labels:
            mask = labels == label
            sample_weights[mask] = weights_per_cluster[label]
            
        # Gürültü noktaları (-1) için ortalama ağırlık kullan
        noise_mask = labels == -1
        if np.any(noise_mask):
            sample_weights[noise_mask] = np.mean(list(weights_per_cluster.values()))
            
        # Ağırlıkları normalize et
        sample_weights /= np.sum(sample_weights)
        sample_weights *= len(X)
        
        return sample_weights
    
    def find_optimal_kmeans(self, X: np.ndarray, k_range: List[int],
                           n_init: int = 10, handle_imbalance: bool = False) -> Dict:
        """
        K-Means için optimal küme sayısını bulur.
        
        Args:
            X: Veri matrisi
            k_range: Denenecek k değerleri
            n_init: Her k için kaç kez farklı başlangıç noktasıyla deneneceği
            handle_imbalance: Veri dengesizliğini ele al
            
        Returns:
            Dict: Her k değeri için metrikler
        """
        results = {
            'k_values': k_range,
            'inertia': [],
            'silhouette': [],
            'calinski': [],
            'davies': []
        }
        
        for k in tqdm(k_range, desc="K-Means optimizasyonu"):
            model = KMeans(n_clusters=k, n_init=n_init, random_state=42)
            labels = model.fit_predict(X)
            
            if handle_imbalance:
                sample_weights = self.compute_sample_weights(X, labels)
            else:
                sample_weights = None
            
            results['inertia'].append(model.inertia_)
            
            if k > 1:  # Silhouette score en az 2 küme gerektirir
                # Silhouette score için sample_weight'i sadece ortalama hesaplamada kullan
                sil_samples = silhouette_samples(X, labels)
                if sample_weights is not None:
                    results['silhouette'].append(np.average(sil_samples, weights=sample_weights))
                else:
                    results['silhouette'].append(np.mean(sil_samples))
                    
                # Calinski-Harabasz ve Davies-Bouldin skorları için ağırlık kullanma
                results['calinski'].append(calinski_harabasz_score(X, labels))
                results['davies'].append(davies_bouldin_score(X, labels))
            else:
                results['silhouette'].append(0)
                results['calinski'].append(0)
                results['davies'].append(float('inf'))
                
            if (results['silhouette'][-1] > self.best_score and k > 1):
                self.best_score = results['silhouette'][-1]
                self.best_model = model
                self.best_params = {'n_clusters': k, 'algorithm': 'kmeans'}
                
        return results
    
    def find_optimal_dbscan(self, X: np.ndarray, eps_range: List[float],
                           min_samples_range: List[int],
                           handle_imbalance: bool = False) -> Dict:
        """
        DBSCAN için optimal parametreleri bulur.
        
        Args:
            X: Veri matrisi
            eps_range: Denenecek eps değerleri
            min_samples_range: Denenecek min_samples değerleri
            handle_imbalance: Veri dengesizliğini ele al
            
        Returns:
            Dict: Her parametre kombinasyonu için metrikler
        """
        results = {
            'eps': [],
            'min_samples': [],
            'n_clusters': [],
            'silhouette': [],
            'calinski': [],
            'davies': []
        }
        
        total_combinations = len(eps_range) * len(min_samples_range)
        pbar = tqdm(total=total_combinations, desc="DBSCAN optimizasyonu")
        
        for eps in eps_range:
            for min_samples in min_samples_range:
                model = DBSCAN(eps=eps, min_samples=min_samples)
                labels = model.fit_predict(X)
                
                # Gürültü noktalarını (-1) hariç tut
                valid_points = labels != -1
                if sum(valid_points) > 1:  # En az 2 geçerli nokta olmalı
                    X_valid = X[valid_points]
                    labels_valid = labels[valid_points]
                    
                    if handle_imbalance:
                        sample_weights = self.compute_sample_weights(X_valid, labels_valid)
                    else:
                        sample_weights = None
                    
                    n_clusters = len(set(labels_valid))
                    if n_clusters > 1:  # En az 2 küme olmalı
                        # Silhouette score için sample_weight'i sadece ortalama hesaplamada kullan
                        sil_samples = silhouette_samples(X_valid, labels_valid)
                        if sample_weights is not None:
                            silhouette = np.average(sil_samples, weights=sample_weights)
                        else:
                            silhouette = np.mean(sil_samples)
                            
                        # Diğer metrikler için ağırlık kullanma
                        calinski = calinski_harabasz_score(X_valid, labels_valid)
                        davies = davies_bouldin_score(X_valid, labels_valid)
                    else:
                        silhouette = 0
                        calinski = 0
                        davies = float('inf')
                else:
                    n_clusters = 0
                    silhouette = 0
                    calinski = 0
                    davies = float('inf')
                
                results['eps'].append(eps)
                results['min_samples'].append(min_samples)
                results['n_clusters'].append(n_clusters)
                results['silhouette'].append(silhouette)
                results['calinski'].append(calinski)
                results['davies'].append(davies)
                
                if silhouette > self.best_score and n_clusters > 1:
                    self.best_score = silhouette
                    self.best_model = model
                    self.best_params = {
                        'eps': eps,
                        'min_samples': min_samples,
                        'algorithm': 'dbscan'
                    }
                
                pbar.update(1)
                
        pbar.close()
        return results
    
    def find_optimal_hierarchical(self, X: np.ndarray, k_range: List[int],
                                linkage: str = 'ward') -> Dict:
        """
        Hiyerarşik kümeleme için optimal parametreleri bulur.
        
        Args:
            X: Veri matrisi
            k_range: Denenecek küme sayıları
            linkage: Bağlantı kriteri ('ward', 'complete', 'average', 'single')
            
        Returns:
            Dict: Her parametre kombinasyonu için metrikler
        """
        results = {
            'k_values': k_range,
            'silhouette': [],
            'calinski': [],
            'davies': []
        }
        
        for k in tqdm(k_range, desc="Hiyerarşik kümeleme optimizasyonu"):
            model = AgglomerativeClustering(n_clusters=k, linkage=linkage)
            labels = model.fit_predict(X)
            
            if k > 1:
                silhouette = silhouette_score(X, labels)
                calinski = calinski_harabasz_score(X, labels)
                davies = davies_bouldin_score(X, labels)
            else:
                silhouette = 0
                calinski = 0
                davies = float('inf')
                
            results['silhouette'].append(silhouette)
            results['calinski'].append(calinski)
            results['davies'].append(davies)
            
            if silhouette > self.best_score and k > 1:
                self.best_score = silhouette
                self.best_model = model
                self.best_params = {
                    'n_clusters': k,
                    'linkage': linkage,
                    'algorithm': 'hierarchical'
                }
                
        return results
    
    def plot_kmeans_optimization(self, results: Dict, save_path: Optional[Union[str, Path]] = None):
        """K-Means optimizasyon sonuçlarını görselleştirir."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Elbow curve (inertia)
        ax1.plot(results['k_values'], results['inertia'], 'bo-')
        ax1.set_xlabel('Küme Sayısı (k)')
        ax1.set_ylabel('Inertia')
        ax1.set_title('Elbow Method')
        
        # Silhouette score
        ax2.plot(results['k_values'], results['silhouette'], 'ro-')
        ax2.set_xlabel('Küme Sayısı (k)')
        ax2.set_ylabel('Silhouette Score')
        ax2.set_title('Silhouette Analysis')
        
        # Calinski-Harabasz score
        ax3.plot(results['k_values'], results['calinski'], 'go-')
        ax3.set_xlabel('Küme Sayısı (k)')
        ax3.set_ylabel('Calinski-Harabasz Score')
        ax3.set_title('Calinski-Harabasz Analysis')
        
        # Davies-Bouldin score
        ax4.plot(results['k_values'], results['davies'], 'mo-')
        ax4.set_xlabel('Küme Sayısı (k)')
        ax4.set_ylabel('Davies-Bouldin Score')
        ax4.set_title('Davies-Bouldin Analysis')
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'kmeans_optimization.png')
        else:
            plt.show()
            
        plt.close()
            
    def plot_dbscan_optimization(self, results: Dict, save_path: Optional[Union[str, Path]] = None):
        """DBSCAN optimizasyon sonuçlarını görselleştirir."""
        unique_eps = sorted(list(set(results['eps'])))
        unique_min_samples = sorted(list(set(results['min_samples'])))
        
        # Silhouette score heatmap için matrix oluştur
        silhouette_matrix = np.zeros((len(unique_min_samples), len(unique_eps)))
        n_clusters_matrix = np.zeros((len(unique_min_samples), len(unique_eps)))
        
        for i, eps in enumerate(results['eps']):
            eps_idx = unique_eps.index(eps)
            min_samples_idx = unique_min_samples.index(results['min_samples'][i])
            silhouette_matrix[min_samples_idx, eps_idx] = results['silhouette'][i]
            n_clusters_matrix[min_samples_idx, eps_idx] = results['n_clusters'][i]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Silhouette score heatmap
        sns.heatmap(silhouette_matrix, annot=True, fmt='.2f', cmap='viridis',
                   xticklabels=[f'{eps:.2f}' for eps in unique_eps],
                   yticklabels=unique_min_samples, ax=ax1)
        ax1.set_xlabel('Epsilon')
        ax1.set_ylabel('Min Samples')
        ax1.set_title('Silhouette Score')
        
        # Number of clusters heatmap
        sns.heatmap(n_clusters_matrix, annot=True, fmt='.0f', cmap='viridis',
                   xticklabels=[f'{eps:.2f}' for eps in unique_eps],
                   yticklabels=unique_min_samples, ax=ax2)
        ax2.set_xlabel('Epsilon')
        ax2.set_ylabel('Min Samples')
        ax2.set_title('Number of Clusters')
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'dbscan_optimization.png')
        else:
            plt.show()
            
        plt.close()
        
    def plot_hierarchical_optimization(self, results: Dict,
                                     save_path: Optional[Union[str, Path]] = None):
        """Hiyerarşik kümeleme optimizasyon sonuçlarını görselleştirir."""
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
        
        # Silhouette score
        ax1.plot(results['k_values'], results['silhouette'], 'ro-')
        ax1.set_xlabel('Küme Sayısı (k)')
        ax1.set_ylabel('Silhouette Score')
        ax1.set_title('Silhouette Analysis')
        
        # Calinski-Harabasz score
        ax2.plot(results['k_values'], results['calinski'], 'go-')
        ax2.set_xlabel('Küme Sayısı (k)')
        ax2.set_ylabel('Calinski-Harabasz Score')
        ax2.set_title('Calinski-Harabasz Analysis')
        
        # Davies-Bouldin score
        ax3.plot(results['k_values'], results['davies'], 'mo-')
        ax3.set_xlabel('Küme Sayısı (k)')
        ax3.set_ylabel('Davies-Bouldin Score')
        ax3.set_title('Davies-Bouldin Analysis')
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'hierarchical_optimization.png')
        else:
            plt.show()
            
        plt.close()
        
    def plot_clusters_2d(self, X: np.ndarray, labels: np.ndarray,
                        save_path: Optional[Union[str, Path]] = None):
        """
        Kümeleri 2 boyutta görselleştirir.
        
        Args:
            X: Veri matrisi
            labels: Küme etiketleri
            save_path: Grafik kayıt yolu
        """
        if X.shape[1] > 2:
            if self.pca is None:
                X_2d, _ = self.apply_pca(X, n_components=2)
            else:
                X_2d = self.pca.transform(X)[:, :2]
        else:
            X_2d = X
            
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='viridis')
        plt.colorbar(scatter)
        
        plt.xlabel('Birinci Bileşen' if X.shape[1] > 2 else 'X')
        plt.ylabel('İkinci Bileşen' if X.shape[1] > 2 else 'Y')
        plt.title('Küme Dağılımı')
        
        if save_path:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path / 'cluster_distribution_2d.png')
        else:
            plt.show()
            
        plt.close()
        
    def save_model(self, save_path: Union[str, Path]):
        """
        En iyi modeli kaydeder.
        
        Args:
            save_path: Kayıt dizini
        """
        if self.best_model is None:
            raise ValueError("Henüz bir model eğitilmemiş!")
            
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        model_info = {
            'model': self.best_model,
            'params': self.best_params,
            'score': self.best_score,
            'pca': self.pca
        }
        
        joblib.dump(model_info, save_path / 'best_clustering_model.joblib')
        self.logger.info(f"Model kaydedildi: {save_path / 'best_clustering_model.joblib'}")
        
    def load_model(self, load_path: Union[str, Path]):
        """
        Kaydedilmiş modeli yükler.
        
        Args:
            load_path: Yükleme dizini
        """
        load_path = Path(load_path)
        model_info = joblib.load(load_path)
        
        self.best_model = model_info['model']
        self.best_params = model_info['params']
        self.best_score = model_info['score']
        self.pca = model_info['pca']
        
        self.logger.info("Model yüklendi")
        self.logger.info(f"En iyi parametreler: {self.best_params}")
        self.logger.info(f"En iyi skor: {self.best_score}")
        
    def apply_dimensionality_reduction(self, X: np.ndarray,
                                     method: Literal['pca', 'tsne', 'umap'] = 'pca',
                                     n_components: Optional[int] = None,
                                     **kwargs) -> Tuple[np.ndarray, DimensionalityReducer]:
        """
        Boyut azaltma uygular.
        
        Args:
            X: Veri matrisi
            method: Kullanılacak yöntem ('pca', 'tsne', 'umap')
            n_components: Hedef boyut sayısı
            **kwargs: Seçilen yönteme özel parametreler
            
        Returns:
            Tuple[np.ndarray, DimensionalityReducer]: Dönüştürülmüş veri ve model
        """
        reducer = DimensionalityReducer(
            method=method,
            n_components=n_components,
            **kwargs
        )
        
        X_reduced = reducer.fit_transform(X)
        
        if method == 'pca':
            explained_var = np.sum(reducer.explained_variance_ratio_)
            self.logger.info(f"PCA sonrası açıklanan varyans: {explained_var:.4f}")
            
        self.logger.info(f"Boyut azaltma sonrası şekil: {X_reduced.shape}")
        
        return X_reduced, reducer
    
    def fit(self, X: np.ndarray) -> 'ClusteringOptimizer':
        """
        Veriyi eğitir ve en iyi modeli bulur.
        
        Args:
            X: Eğitim verisi
            
        Returns:
            self: Eğitilmiş model
        """
        try:
            self.logger.info("Model eğitimi başlıyor")
            
            # Veriyi ölçeklendir
            X_scaled = self.scaler.fit_transform(X)
            
            # PCA uygula
            if X.shape[1] > 2:
                X_reduced, self.pca = self.apply_pca(X_scaled)
            else:
                X_reduced = X_scaled
            
            # K-Means optimizasyonu
            k_range = range(2, min(11, len(X) // 2))
            kmeans_results = self.find_optimal_kmeans(X_reduced, k_range)
            
            # DBSCAN optimizasyonu
            eps_range = np.linspace(0.1, 2.0, 20)
            min_samples_range = [3, 5, 7, 10]
            dbscan_results = self.find_optimal_dbscan(X_reduced, eps_range, min_samples_range)
            
            # En iyi modeli seç
            if self.best_model is None:
                # Varsayılan olarak K-Means kullan
                self.best_model = KMeans(n_clusters=3, random_state=42)
                self.best_model.fit(X_reduced)
                self.best_params = {"algorithm": "kmeans", "n_clusters": 3}
                labels = self.best_model.labels_
                self.best_score = silhouette_score(X_reduced, labels) if len(np.unique(labels)) > 1 else 0
            
            self.logger.info(f"Model eğitimi tamamlandı. En iyi skor: {self.best_score:.4f}")
            return self
            
        except Exception as e:
            self.logger.error(f"Model eğitimi hatası: {str(e)}", exc_info=True)
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Yeni veri için tahmin yapar.
        
        Args:
            X: Tahmin yapılacak veri
            
        Returns:
            np.ndarray: Küme etiketleri
        """
        try:
            if self.best_model is None:
                raise ValueError("Model henüz eğitilmemiş!")
            
            # Veriyi ölçeklendir
            X_scaled = self.scaler.transform(X)
            
            # Gerekirse PCA uygula
            if self.pca is not None:
                X_reduced = self.pca.transform(X_scaled)
            else:
                X_reduced = X_scaled
            
            # Tahmin yap
            labels = self.best_model.predict(X_reduced)
            return labels
            
        except Exception as e:
            self.logger.error(f"Tahmin hatası: {str(e)}", exc_info=True)
            raise 