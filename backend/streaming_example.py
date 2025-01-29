from auto_cluster import AutoCluster
import numpy as np
import pandas as pd
from pathlib import Path
import time
from sklearn.cluster import MiniBatchKMeans

def generate_stream_data(n_samples: int = 100, n_features: int = 4,
                        n_clusters: int = 3, noise: float = 0.1) -> np.ndarray:
    """
    Streaming veri simülasyonu için veri üretir.
    
    Args:
        n_samples: Örnek sayısı
        n_features: Özellik sayısı
        n_clusters: Küme sayısı
        noise: Gürültü seviyesi
        
    Returns:
        np.ndarray: Üretilen veri
    """
    centers = []
    for _ in range(n_clusters):
        center = np.random.uniform(-10, 10, size=n_features)
        centers.append(center)
    
    # Rastgele bir merkez seç ve etrafında noktalar oluştur
    selected_center = centers[np.random.randint(0, n_clusters)]
    X = np.random.normal(loc=selected_center, scale=noise, size=(n_samples, n_features))
    
    return X

def main():
    # Çıktı dizini oluştur
    output_dir = Path("output/streaming")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # AutoCluster'ı başlat
    config = {
        'n_clusters': 3,
        'n_components': 2  # PCA için bileşen sayısı
    }
    
    # MiniBatchKMeans modelini oluştur
    base_model = MiniBatchKMeans(
        n_clusters=config['n_clusters'],
        batch_size=100,
        random_state=42
    )
    
    auto_cluster = AutoCluster(
        base_model=base_model,
        config=config,
        buffer_size=1000
    )
    
    # Streaming veri simülasyonu
    n_batches = 20
    batch_size = 100
    
    print("\nStreaming veri simülasyonu başlıyor...")
    print(f"Toplam batch sayısı: {n_batches}")
    print(f"Her batch'te örnek sayısı: {batch_size}")
    
    try:
        for i in range(n_batches):
            # Yeni veri batch'i üret
            X = generate_stream_data(n_samples=batch_size)
            
            # Modeli güncelle
            labels = auto_cluster.partial_fit(X)
            
            # Her 5 batch'te bir istatistikleri göster
            if (i + 1) % 5 == 0:
                stats = auto_cluster.get_cluster_stats()
                print(f"\nBatch {i+1} / {n_batches}")
                print("Küme dağılımı:", stats['current_distribution'])
                print("Toplam işlenen örnek:", stats['total_samples_processed'])
                
                # Grafikleri güncelle
                auto_cluster.plot_cluster_evolution(save_path=output_dir)
                auto_cluster.plot_metric_evolution(save_path=output_dir)
            
            # Simüle edilmiş gecikme
            time.sleep(0.5)
        
        # Son durumu kaydet
        auto_cluster.save_state(output_dir / "model_state")
        
        print("\nSimülasyon tamamlandı!")
        print("Sonuçlar output/streaming dizininde")
        
    except KeyboardInterrupt:
        print("\nSimülasyon kullanıcı tarafından durduruldu!")
        # Son durumu kaydet
        auto_cluster.save_state(output_dir / "model_state")

if __name__ == "__main__":
    main() 