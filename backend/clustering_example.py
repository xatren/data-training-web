from data_preparation import DataPreparation
from clustering import ClusteringOptimizer
import numpy as np
import pandas as pd
from pathlib import Path

def main():
    # Veri hazırlama sınıfını başlat
    prep = DataPreparation()
    
    # Örnek veri yükle veya oluştur
    try:
        df = prep.load_data("data/example.csv", encoding='utf-8')
    except FileNotFoundError:
        print("Örnek veri oluşturuluyor...")
        # Çok boyutlu örnek veri oluştur
        np.random.seed(42)
        n_samples = 1000
        
        # 3 farklı küme merkezi
        centers = [
            [0, 0, 0, 0],
            [10, 10, 10, 10],
            [-5, -5, -5, -5]
        ]
        
        # Her merkez etrafında normal dağılımlı noktalar oluştur
        X = []
        for center in centers:
            cluster = np.random.normal(loc=center, scale=1.0, size=(n_samples // 3, 4))
            X.append(cluster)
        
        X = np.vstack(X)
        
        # Bazı eksik değerler ekle
        mask = np.random.random(X.shape) < 0.1
        X[mask] = np.nan
        
        # DataFrame oluştur
        df = pd.DataFrame(
            X,
            columns=['feature1', 'feature2', 'feature3', 'feature4']
        )
    
    # 1. Veri Hazırlığı
    print("\n1. Veri Hazırlığı")
    print("-----------------")
    
    # Eksik değer analizi
    missing_stats = prep.analyze_missing_values(df)
    print("\nEksik Değer Analizi:")
    print(missing_stats['missing_percentages'])
    
    # Eksik değerleri doldur
    strategy = {col: 'mean' for col in df.columns}
    df_cleaned = prep.handle_missing_values(df, strategy)
    
    # Yinelenen satırları kaldır
    df_unique = prep.remove_duplicates(df_cleaned)
    
    # Aykırı değerleri tespit et ve işle
    outliers = prep.detect_outliers(df_unique, df_unique.columns.tolist())
    df_no_outliers = prep.handle_outliers(df_unique, outliers, method='clip')
    
    # Normal dağılıma dönüştür
    df_normalized = prep.normalize_distribution(df_no_outliers, df_no_outliers.columns.tolist())
    
    # Özellikleri ölçeklendir
    df_scaled = prep.scale_features(df_normalized, df_normalized.columns.tolist())
    
    # Sadece sayısal sütunları seç
    df_numeric = df_scaled.select_dtypes(include=[np.number])
    
    # 2. Kümeleme
    print("\n2. Kümeleme")
    print("-----------")
    
    # Kümeleme optimize edici başlat
    optimizer = ClusteringOptimizer()
    
    # Veriyi numpy array'e dönüştür
    X = df_numeric.values
    
    # PCA uygula
    X_pca, _ = optimizer.apply_pca(X, variance_ratio=0.95)
    
    # K-Means optimizasyonu
    print("\nK-Means optimizasyonu yapılıyor...")
    kmeans_results = optimizer.find_optimal_kmeans(
        X_pca,
        k_range=range(2, 11)
    )
    
    # DBSCAN optimizasyonu
    print("\nDBSCAN optimizasyonu yapılıyor...")
    eps_range = np.linspace(0.1, 2.0, 10)
    min_samples_range = range(5, 51, 5)
    dbscan_results = optimizer.find_optimal_dbscan(
        X_pca,
        eps_range=eps_range,
        min_samples_range=min_samples_range
    )
    
    # Hiyerarşik kümeleme optimizasyonu
    print("\nHiyerarşik kümeleme optimizasyonu yapılıyor...")
    hierarchical_results = optimizer.find_optimal_hierarchical(
        X_pca,
        k_range=range(2, 11),
        linkage='ward'
    )
    
    # Sonuçları görselleştir
    output_dir = Path("output")
    
    print("\nSonuçlar görselleştiriliyor...")
    optimizer.plot_kmeans_optimization(kmeans_results, save_path=output_dir)
    optimizer.plot_dbscan_optimization(dbscan_results, save_path=output_dir)
    optimizer.plot_hierarchical_optimization(hierarchical_results, save_path=output_dir)
    
    # En iyi modeli kullanarak kümeleri görselleştir
    if optimizer.best_model is not None:
        labels = optimizer.best_model.fit_predict(X_pca)
        optimizer.plot_clusters_2d(X_pca, labels, save_path=output_dir)
        
        # Modeli kaydet
        optimizer.save_model(output_dir / "models")
        
        print(f"\nEn iyi model: {optimizer.best_params['algorithm']}")
        print(f"En iyi parametreler: {optimizer.best_params}")
        print(f"En iyi Silhouette skoru: {optimizer.best_score:.4f}")
    else:
        print("\nHiçbir model başarılı bir şekilde eğitilemedi!")

if __name__ == "__main__":
    main()