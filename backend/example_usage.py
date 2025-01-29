from data_preparation import DataPreparation
import pandas as pd
from pathlib import Path
import numpy as np
def main():
    # Veri hazırlama sınıfını başlat
    prep = DataPreparation()
    
    # CSV okuma
    csv_path = "data/example.csv"  # Buraya okuyacağınız CSV'nin yolunu girin
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Hata: '{csv_path}' dosyası bulunamadı. Örnek bir DataFrame oluşturuluyor.")
        # Örnek veri oluştur
        df = pd.DataFrame({
            'numeric_col': [1, 2, None, 4, 5, 100, 6, 7, 8, 9],
            'category_col': ['A', 'B', 'A', None, 'C', 'B', 'A', 'C', 'B', 'A'],
            'text_col': ['örnek', 'metin', None, 'veri', 'seti', 'test', 'deneme', 'python', 'veri', 'bilimi']
        })
    
    # Sütun tiplerini belirle
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    text_columns = [col for col in df.columns if col not in numeric_columns + categorical_columns]
    
    print("Sütun Tipleri:")
    print(f"Sayısal: {numeric_columns}")
    print(f"Kategorik: {categorical_columns}")
    print(f"Metin: {text_columns}")
    
    # 1. Eksik değer analizi
    missing_stats = prep.analyze_missing_values(df)
    print("\nEksik Değer Analizi:")
    print(missing_stats['missing_percentages'])
    
    # 2. Eksik değerleri doldur
    strategy = {col: 'mean' for col in numeric_columns}
    strategy.update({col: 'mode' for col in categorical_columns + text_columns})
    df_cleaned = prep.handle_missing_values(df, strategy)
    
    # 3. Yinelenen satırları kaldır
    df_unique = prep.remove_duplicates(df_cleaned)
    
    # 4. Aykırı değerleri tespit et ve işle
    outliers = prep.detect_outliers(df_unique, numeric_columns, method='iqr')
    df_no_outliers = prep.handle_outliers(df_unique, outliers, method='clip')
    
    # 5. Normal dağılıma dönüştür
    df_normalized = prep.normalize_distribution(df_no_outliers, numeric_columns)
    
    # 6. Özellikleri ölçeklendir
    df_scaled = prep.scale_features(df_normalized, numeric_columns)
    
    # 7. Kategorik değişkenleri kodla
    df_encoded = prep.encode_categorical(df_scaled, categorical_columns, method='onehot')
    
    # 8. Dağılımları görselleştir
    output_dir = Path("output/plots")
    prep.plot_distributions(df_encoded, numeric_columns, save_path=output_dir)
    
    # 9. Dönüştürücüleri kaydet
    prep.save_transformers("output/transformers")
    
    print("\nVeri hazırlama işlemi tamamlandı!")
    print(f"Son veri seti boyutu: {df_encoded.shape}")
    print("\nİlk birkaç satır:")
    print(df_encoded.head())

if __name__ == "__main__":
    main()
