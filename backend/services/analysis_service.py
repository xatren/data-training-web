import pandas as pd
import numpy as np
from typing import Dict, Any

class AnalysisService:
    async def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """DataFrame'i analiz et ve istatistikleri döndür"""
        try:
            # Veri tipleri
            dtypes = df.dtypes.to_dict()
            column_types = {col: str(dtype) for col, dtype in dtypes.items()}
            
            # Temel istatistikler
            stats = {
                "satir_sayisi": len(df),
                "sutun_sayisi": len(df.columns),
                "sutunlar": df.columns.tolist(),
                "veri_tipleri": column_types,
                "sayisal_sutunlar": df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                "kategorik_sutunlar": df.select_dtypes(include=['object']).columns.tolist()
            }
            
            # Sayısal sütunlar için istatistikler
            numeric_stats = {}
            for col in stats["sayisal_sutunlar"]:
                numeric_stats[col] = {
                    "ortalama": float(df[col].mean()),
                    "medyan": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
            
            # Kategorik sütunlar için istatistikler
            categorical_stats = {}
            for col in stats["kategorik_sutunlar"]:
                if df[col].nunique() <= 20:
                    value_counts = df[col].value_counts()
                    categorical_stats[col] = {
                        str(val): int(count) 
                        for val, count in value_counts.items()
                    }
            
            return {
                **stats,
                "numeric_stats": numeric_stats,
                "categorical_stats": categorical_stats
            }
            
        except Exception as e:
            raise Exception(f"Analiz hatası: {str(e)}") 