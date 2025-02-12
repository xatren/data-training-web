import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class VisualizationService:
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    async def create_visualizations(self, df: pd.DataFrame) -> list:
        """DataFrame için görselleştirmeler oluştur"""
        try:
            visualizations = []
            
            # Sayısal sütunlar için histogram
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            for col in numeric_cols:
                plt.figure(figsize=(10, 6))
                sns.histplot(data=df, x=col)
                plt.title(f'{col} Dağılımı')
                file_name = f'{col.lower()}_dagilimi.png'
                plt.savefig(self.output_dir / file_name)
                plt.close()
                visualizations.append(file_name)
            
            # Kategorik sütunlar için bar plot
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df[col].nunique() <= 20:
                    plt.figure(figsize=(10, 6))
                    df[col].value_counts().plot(kind='bar')
                    plt.title(f'{col} Dağılımı')
                    plt.xticks(rotation=45)
                    file_name = f'{col.lower()}_dagilimi.png'
                    plt.savefig(self.output_dir / file_name)
                    plt.close()
                    visualizations.append(file_name)
            
            return visualizations
            
        except Exception as e:
            raise Exception(f"Görselleştirme hatası: {str(e)}") 