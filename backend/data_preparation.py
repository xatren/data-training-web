import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer, StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, List, Dict, Optional
import logging
from pathlib import Path
import joblib
from tqdm import tqdm
import numpy as np
class DataPreparation:
    def __init__(self, config: Optional[Dict] = None):
        """
        Veri hazırlama ve temizleme pipeline'ı.
        
        Args:
            config: Konfigürasyon ayarları içeren sözlük
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        self.transformers = {}
        
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

    def load_data(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Veriyi yükler.
        
        Args:
            file_path: Veri dosyasının yolu
            **kwargs: pandas.read_csv veya read_excel için ek parametreler
            
        Returns:
            pd.DataFrame: Yüklenen veri
        """
        file_path = Path(file_path)
        self.logger.info(f"Veri yükleniyor: {file_path}")
        
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path, **kwargs)
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, **kwargs)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_path.suffix}")
            
        self.logger.info(f"Veri yüklendi. Boyut: {df.shape}")
        return df

    def analyze_missing_values(self, df: pd.DataFrame) -> Dict:
        """
        Eksik değerleri analiz eder.
        
        Args:
            df: Analiz edilecek DataFrame
            
        Returns:
            Dict: Eksik değer analizi sonuçları
        """
        missing_stats = {
            'missing_counts': df.isnull().sum(),
            'missing_percentages': (df.isnull().sum() / len(df)) * 100,
            'total_missing': df.isnull().sum().sum()
        }
        
        self.logger.info(f"Toplam eksik değer sayısı: {missing_stats['total_missing']}")
        return missing_stats

    def handle_missing_values(self, df: pd.DataFrame, strategy: Dict[str, str]) -> pd.DataFrame:
        """
        Eksik değerleri doldurur.
        
        Args:
            df: İşlenecek DataFrame
            strategy: Sütun bazında doldurma stratejileri
            
        Returns:
            pd.DataFrame: Eksik değerleri doldurulmuş DataFrame
        """
        df_cleaned = df.copy()
        
        for column, method in strategy.items():
            if column not in df.columns:
                self.logger.warning(f"Sütun bulunamadı: {column}")
                continue
                
            if method == 'mean':
                imputer = SimpleImputer(strategy='mean')
            elif method == 'median':
                imputer = SimpleImputer(strategy='median')
            elif method == 'mode':
                imputer = SimpleImputer(strategy='most_frequent')
            else:
                self.logger.warning(f"Geçersiz strateji: {method}")
                continue
                
            if df[column].dtype in ['int64', 'float64']:
                df_cleaned[column] = imputer.fit_transform(df[[column]])
                
        return df_cleaned

    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Yinelenen satırları kaldırır.
        
        Args:
            df: İşlenecek DataFrame
            subset: Kontrol edilecek sütunlar
            
        Returns:
            pd.DataFrame: Tekil satırlar içeren DataFrame
        """
        initial_rows = len(df)
        df_unique = df.drop_duplicates(subset=subset)
        removed_rows = initial_rows - len(df_unique)
        
        self.logger.info(f"Kaldırılan yinelenen satır sayısı: {removed_rows}")
        return df_unique

    def detect_outliers(self, df: pd.DataFrame, columns: List[str], method: str = 'iqr',
                       threshold: float = 1.5) -> Dict[str, np.ndarray]:
        """
        Aykırı değerleri tespit eder.
        
        Args:
            df: İşlenecek DataFrame
            columns: İncelenecek sayısal sütunlar
            method: Kullanılacak yöntem ('iqr' veya 'zscore')
            threshold: Eşik değeri
            
        Returns:
            Dict: Sütun bazında aykırı değer indeksleri
        """
        outliers = {}
        
        for column in columns:
            if df[column].dtype not in ['int64', 'float64']:
                continue
                
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers[column] = df[
                    (df[column] < lower_bound) | 
                    (df[column] > upper_bound)
                ].index
            
            elif method == 'zscore':
                z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                outliers[column] = df[z_scores > threshold].index
                
        return outliers

    def handle_outliers(self, df: pd.DataFrame, outliers: Dict[str, np.ndarray],
                       method: str = 'clip') -> pd.DataFrame:
        """
        Aykırı değerleri işler.
        
        Args:
            df: İşlenecek DataFrame
            outliers: Aykırı değer indeksleri
            method: İşleme yöntemi ('clip' veya 'remove')
            
        Returns:
            pd.DataFrame: Aykırı değerleri işlenmiş DataFrame
        """
        df_cleaned = df.copy()
        
        if method == 'clip':
            for column, indices in outliers.items():
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df_cleaned.loc[indices, column] = df_cleaned.loc[indices, column].clip(
                    lower=lower_bound, upper=upper_bound
                )
        
        elif method == 'remove':
            all_indices = np.unique(np.concatenate(list(outliers.values())))
            df_cleaned = df_cleaned.drop(index=all_indices)
            
        return df_cleaned

    def normalize_distribution(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Veriyi normal dağılıma dönüştürür.
        
        Args:
            df: İşlenecek DataFrame
            columns: Dönüştürülecek sütunlar
            
        Returns:
            pd.DataFrame: Dönüştürülmüş DataFrame
        """
        df_transformed = df.copy()
        
        for column in columns:
            if df[column].dtype not in ['int64', 'float64']:
                continue
                
            transformer = PowerTransformer(method='yeo-johnson')
            df_transformed[column] = transformer.fit_transform(
                df[[column]].fillna(df[column].mean())
            )
            self.transformers[f"{column}_normalizer"] = transformer
            
        return df_transformed

    def scale_features(self, df: pd.DataFrame, columns: List[str],
                      scaler_type: str = 'standard') -> pd.DataFrame:
        """
        Özellikleri ölçeklendirir.
        
        Args:
            df: İşlenecek DataFrame
            columns: Ölçeklendirilecek sütunlar
            scaler_type: Ölçeklendirme yöntemi
            
        Returns:
            pd.DataFrame: Ölçeklendirilmiş DataFrame
        """
        df_scaled = df.copy()
        
        for column in columns:
            if df[column].dtype not in ['int64', 'float64']:
                continue
                
            if scaler_type == 'standard':
                scaler = StandardScaler()
            else:
                raise ValueError(f"Desteklenmeyen ölçeklendirme yöntemi: {scaler_type}")
                
            df_scaled[column] = scaler.fit_transform(
                df[[column]].fillna(df[column].mean())
            )
            self.transformers[f"{column}_scaler"] = scaler
            
        return df_scaled

    def encode_categorical(self, df: pd.DataFrame, columns: List[str],
                         method: str = 'label') -> pd.DataFrame:
        """
        Kategorik değişkenleri kodlar.
        
        Args:
            df: İşlenecek DataFrame
            columns: Kodlanacak sütunlar
            method: Kodlama yöntemi ('label' veya 'onehot')
            
        Returns:
            pd.DataFrame: Kodlanmış DataFrame
        """
        df_encoded = df.copy()
        
        for column in columns:
            if method == 'label':
                encoder = LabelEncoder()
                df_encoded[column] = encoder.fit_transform(df[column].astype(str))
                self.transformers[f"{column}_encoder"] = encoder
                
            elif method == 'onehot':
                encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
                encoded_data = encoder.fit_transform(df[[column]])
                encoded_df = pd.DataFrame(
                    encoded_data,
                    columns=[f"{column}_{cat}" for cat in encoder.categories_[0]],
                    index=df.index
                )
                df_encoded = pd.concat([df_encoded.drop(columns=[column]), encoded_df], axis=1)
                self.transformers[f"{column}_encoder"] = encoder
                
        return df_encoded

    def plot_distributions(self, df: pd.DataFrame, columns: List[str],
                         save_path: Optional[Union[str, Path]] = None):
        """
        Dağılımları görselleştirir.
        
        Args:
            df: Görselleştirilecek DataFrame
            columns: Görselleştirilecek sütunlar
            save_path: Grafiklerin kaydedileceği dizin
        """
        for column in columns:
            if df[column].dtype not in ['int64', 'float64']:
                continue
                
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Histogram
            sns.histplot(data=df, x=column, ax=ax1)
            ax1.set_title(f"{column} - Histogram")
            
            # Box plot
            sns.boxplot(data=df, y=column, ax=ax2)
            ax2.set_title(f"{column} - Box Plot")
            
            plt.tight_layout()
            
            if save_path:
                save_path = Path(save_path)
                save_path.mkdir(parents=True, exist_ok=True)
                plt.savefig(save_path / f"{column}_distribution.png")
            else:
                plt.show()
                
            plt.close()

    def save_transformers(self, save_path: Union[str, Path]):
        """
        Dönüştürücüleri kaydeder.
        
        Args:
            save_path: Kayıt dizini
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        for name, transformer in self.transformers.items():
            joblib.dump(transformer, save_path / f"{name}.joblib")
            
    def load_transformers(self, load_path: Union[str, Path]):
        """
        Dönüştürücüleri yükler.
        
        Args:
            load_path: Yükleme dizini
        """
        load_path = Path(load_path)
        
        for file_path in load_path.glob("*.joblib"):
            name = file_path.stem
            self.transformers[name] = joblib.load(file_path) 