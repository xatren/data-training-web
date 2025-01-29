"""
Çalışan verilerinin kümeleme analizi için yardımcı modül.

Bu modül, çalışan verilerinin kümeleme analizini gerçekleştirmek için
gerekli sınıf ve fonksiyonları içerir. K-means ve diğer kümeleme
algoritmaları kullanılarak çalışanların gruplandırılması yapılır.

Classes:
    ClusterAnalyzer: Kümeleme analizi için ana sınıf.
geliştirmeler:
clustring.py kodunda yer alan çoklu model oluşturma işlemi bu alana gerektiği gibi entegre edilerek proje bağlamında yer alan ana işlev sağlanacaktır. 
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Tuple
from pathlib import Path

class ClusterAnalyzer:
    """
    Kümeleme analizi için yardımcı sınıf.
    
    Bu sınıf, çalışan verilerini kümelemek için çeşitli algoritmalar kullanır.
    Veriyi ölçeklendirir, optimal küme sayısını belirler ve sonuçları
    görselleştirir.
    
    Attributes:
        df (pd.DataFrame): Analiz edilecek veri çerçevesi
        scaler (StandardScaler): Veri ölçeklendirme nesnesi
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        ClusterAnalyzer sınıfını başlatır.
        
        Args:
            df (pd.DataFrame): Analiz edilecek veri çerçevesi. 'Maas' ve 'Yas'
                             sütunlarını içermelidir.
        """
        self.df = df
        self.scaler = StandardScaler()
        
    def prepare_data(self) -> np.ndarray:
        """
        Veriyi kümeleme için hazırlar.
        
        'Maas' ve 'Yas' özelliklerini seçer ve standartlaştırır.
        
        Returns:
            np.ndarray: Ölçeklendirilmiş veri matrisi
        """
        numeric_features = ['Maas', 'Yas']
        X = self.df[numeric_features].values
        return self.scaler.fit_transform(X)
    
    def kmeans_analysis(self, max_clusters: int = 10) -> Dict[str, Any]:
        """
        K-means kümeleme analizi yapar.
        
        Optimal küme sayısını belirlemek için Elbow metodu ve Silhouette
        skorunu kullanır. Her küme sayısı için model performansını değerlendirir.
        
        Args:
            max_clusters (int): Denenecek maksimum küme sayısı
            
        Returns:
            Dict[str, Any]: Analiz sonuçları
            {
                'optimal_clusters': int,  # Optimal küme sayısı
                'silhouette_score': float,  # En iyi silhouette skoru
                'cluster_labels': List[int],  # Her veri noktası için küme etiketi
                'cluster_sizes': List[int]  # Her kümenin boyutu
            }
        """
        X = self.prepare_data()
        
        # Optimal küme sayısını bul
        inertias = []
        silhouette_scores = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, kmeans.labels_))
        
        # En iyi silhouette skoruna sahip küme sayısını seç
        optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
        
        # Final model
        final_model = KMeans(n_clusters=optimal_k, random_state=42)
        clusters = final_model.fit_predict(X)
        
        # Görselleştirme
        plt.figure(figsize=(15, 5))
        
        # Elbow eğrisi
        plt.subplot(1, 2, 1)
        plt.plot(range(2, max_clusters + 1), inertias, marker='o')
        plt.xlabel('Küme Sayısı')
        plt.ylabel('Inertia')
        plt.title('Elbow Metodu')
        
        # Silhouette skorları
        plt.subplot(1, 2, 2)
        plt.plot(range(2, max_clusters + 1), silhouette_scores, marker='o')
        plt.xlabel('Küme Sayısı')
        plt.ylabel('Silhouette Skoru')
        plt.title('Silhouette Analizi')
        
        plt.tight_layout()
        
        return {
            "optimal_clusters": optimal_k,
            "silhouette_score": max(silhouette_scores),
            "cluster_labels": clusters.tolist(),
            "cluster_sizes": np.bincount(clusters).tolist()
        }
    
    def visualize_clusters(self, output_dir: Path) -> str:
        """
        Kümeleme sonuçlarını görselleştirir.
        
        Maaş ve yaş özelliklerini kullanarak kümeleri 2 boyutlu düzlemde
        görselleştirir.
        
        Args:
            output_dir (Path): Görselin kaydedileceği dizin
            
        Returns:
            str: Oluşturulan görsel dosyasının yolu
            
        Raises:
            Exception: Görselleştirme veya dosya kaydetme hatası durumunda
        """
        X = self.prepare_data()
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(X[:, 0], X[:, 1], c=clusters, cmap='viridis')
        plt.xlabel('Maaş (Ölçeklendirilmiş)')
        plt.ylabel('Yaş (Ölçeklendirilmiş)')
        plt.title('Çalışan Kümeleri')
        plt.colorbar(scatter)
        
        output_file = output_dir / 'employee_clusters.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_file) 