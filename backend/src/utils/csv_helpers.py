"""
Çalışan verilerinin CSV dosyasından analizi için yardımcı modül.

Bu modül, çalışan verilerinin analizi, istatistiklerin hesaplanması ve
görselleştirilmesi için gerekli fonksiyonları içerir.

Classes:
    CSVAnalyzer: CSV dosyası analizi için ana sınıf.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
from ..utils.logger import logger
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import locale
from .clustering_helpers import ClusterAnalyzer
from ..config.settings import OUTPUT_DIR
from clustering import ClusteringOptimizer

class CSVAnalyzer:
    """
    CSV dosyası analizi için yardımcı sınıf.
    
    Bu sınıf, çalışan verilerini içeren CSV dosyasını okur, analiz eder
    ve görselleştirir. Temel istatistikler, departman analizleri ve
    yaş dağılımı gibi çeşitli analizler sunar.
    
    Attributes:
        file_path (Path): CSV dosyasının yolu
        df (pd.DataFrame): Yüklenen CSV verisi
    """
    
    def __init__(self, file_path: str):
        """
        CSVAnalyzer sınıfını başlatır.
        
        Args:
            file_path (str): Analiz edilecek CSV dosyasının yolu
            
        Raises:
            FileNotFoundError: Dosya bulunamazsa
            ValueError: CSV dosyası okunamazsa
        """
        self.file_path = Path(file_path)
        self.df = None
        # Türkçe tarih formatı için locale ayarı
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
        self._load_data()
        
    def _load_data(self):
        """CSV dosyasını yükler."""
        try:
            self.df = pd.read_csv(self.file_path, encoding='utf-8')
            logger.info(f"CSV dosyası başarıyla yüklendi: {self.file_path}")
        except Exception as e:
            logger.error(f"CSV dosyası yüklenirken hata: {str(e)}")
            raise
            
    def _convert_turkish_date(self, date_str: str) -> datetime:
        """
        Türkçe tarih stringini datetime objesine çevirir.
        
        Args:
            date_str (str): "GG Ay YYYY" formatında tarih stringi
            
        Returns:
            datetime: Dönüştürülmüş tarih objesi
            
        Example:
            >>> _convert_turkish_date("22 Nisan 1985")
            datetime(1985, 4, 22)
        """
        tr_months = {
            'Ocak': '01', 'Şubat': '02', 'Mart': '03', 'Nisan': '04',
            'Mayıs': '05', 'Haziran': '06', 'Temmuz': '07', 'Ağustos': '08',
            'Eylül': '09', 'Ekim': '10', 'Kasım': '11', 'Aralık': '12'
        }
        
        day, month, year = date_str.split()
        month = tr_months[month]
        return datetime.strptime(f"{day} {month} {year}", "%d %m %Y")
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """
        Veri setinin temel istatistiklerini hesaplar.
        
        Returns:
            Dict[str, Any]: Temel istatistikleri içeren sözlük
            {
                'toplam_calisan': int,
                'departman_dagilimi': Dict[str, int],
                'sehir_dagilimi': Dict[str, int],
                'ortalama_maas': float,
                'maas_std': float,
                'telefon_turu_dagilimi': Dict[str, int]
            }
        """
        stats = {
            "toplam_calisan": len(self.df),
            "departman_dagilimi": self.df['Departman'].value_counts().to_dict(),
            "sehir_dagilimi": self.df['Sehir'].value_counts().to_dict(),
            "ortalama_maas": float(self.df['Maas'].mean()),
            "maas_std": float(self.df['Maas'].std()),
            "telefon_turu_dagilimi": self.df['TelefonTuru'].value_counts().to_dict()
        }
        return stats
    
    def get_department_analysis(self) -> Dict[str, Any]:
        """
        Departman bazlı detaylı analiz yapar.
        
        Her departman için çalışan sayısı, ortalama maaş ve
        maaş aralığı gibi istatistikleri hesaplar.
        
        Returns:
            Dict[str, Any]: Departman analizlerini içeren sözlük
            {
                'departman_adi': {
                    'calisan_sayisi': int,
                    'ortalama_maas': float,
                    'min_maas': float,
                    'max_maas': float
                }
            }
        """
        dept_analysis = {}
        for dept in self.df['Departman'].unique():
            dept_data = self.df[self.df['Departman'] == dept]
            dept_analysis[dept] = {
                "calisan_sayisi": len(dept_data),
                "ortalama_maas": float(dept_data['Maas'].mean()),
                "min_maas": float(dept_data['Maas'].min()),
                "max_maas": float(dept_data['Maas'].max())
            }
        return dept_analysis
    
    def get_age_distribution(self) -> Dict[str, Any]:
        """
        Çalışanların yaş dağılımını analiz eder.
        
        Doğum tarihlerini kullanarak yaş hesaplar ve
        yaş gruplarına göre dağılımı çıkarır.
        
        Returns:
            Dict[str, Any]: Yaş dağılımı analizini içeren sözlük
            {
                'ortalama_yas': float,
                'min_yas': float,
                'max_yas': float,
                'yas_dagilimi': {
                    '20-30': int,
                    '31-40': int,
                    '41-50': int,
                    '51+': int
                }
            }
        """
        self.df['DogumTarihi'] = self.df['DogumTarihi'].apply(self._convert_turkish_date)
        self.df['Yas'] = (datetime.now() - self.df['DogumTarihi']).dt.days / 365.25
        
        return {
            "ortalama_yas": float(self.df['Yas'].mean()),
            "min_yas": float(self.df['Yas'].min()),
            "max_yas": float(self.df['Yas'].max()),
            "yas_dagilimi": {
                "20-30": len(self.df[self.df['Yas'].between(20, 30)]),
                "31-40": len(self.df[self.df['Yas'].between(31, 40)]),
                "41-50": len(self.df[self.df['Yas'].between(41, 50)]),
                "51+": len(self.df[self.df['Yas'] > 50])
            }
        }
    
    def create_visualizations(self, output_dir: Path) -> List[str]:
        """
        Veri analizi sonuçlarını görselleştirir.
        
        Çeşitli grafik ve görselleştirmeler oluşturarak bunları
        belirtilen dizine kaydeder.
        
        Args:
            output_dir (Path): Görsellerin kaydedileceği dizin
            
        Returns:
            List[str]: Oluşturulan görsel dosyalarının yollarını içeren liste
            
        Raises:
            Exception: Görselleştirme oluşturma hatası durumunda
        """
        # Seaborn stil ayarları
        sns.set_theme(style="whitegrid")
        generated_files = []
        
        try:
            # Output dizinini oluştur
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Departman Dağılımı
            plt.figure(figsize=(12, 6))
            sns.barplot(x=self.df['Departman'].value_counts().index, 
                       y=self.df['Departman'].value_counts().values)
            plt.title('Departmanlara Göre Çalışan Dağılımı', pad=20)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            dept_plot = output_dir / 'departman_dagilimi.png'
            plt.savefig(dept_plot, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(str(dept_plot))
            
            # 2. Maaş Dağılımı
            plt.figure(figsize=(10, 6))
            sns.histplot(data=self.df, x='Maas', bins=20, kde=True)
            plt.title('Maaş Dağılımı', pad=20)
            plt.xlabel('Maaş (TL)')
            plt.ylabel('Çalışan Sayısı')
            maas_plot = output_dir / 'maas_dagilimi.png'
            plt.savefig(maas_plot, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(str(maas_plot))
            
            # 3. Şehir Dağılımı
            plt.figure(figsize=(10, 8))
            sehir_counts = self.df['Sehir'].value_counts()
            plt.pie(sehir_counts.values, labels=sehir_counts.index, 
                   autopct='%1.1f%%', startangle=90)
            plt.title('Şehirlere Göre Çalışan Dağılımı', pad=20)
            sehir_plot = output_dir / 'sehir_dagilimi.png'
            plt.savefig(sehir_plot, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(str(sehir_plot))
            
            # 4. Yaş-Maaş İlişkisi
            plt.figure(figsize=(12, 8))
            sns.scatterplot(data=self.df, x='Yas', y='Maas', 
                          hue='Departman', size='Maas',
                          sizes=(50, 400), alpha=0.6)
            plt.title('Yaş-Maaş İlişkisi (Departmanlara Göre)', pad=20)
            plt.xlabel('Yaş')
            plt.ylabel('Maaş (TL)')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            yas_maas_plot = output_dir / 'yas_maas_iliskisi.png'
            plt.savefig(yas_maas_plot, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(str(yas_maas_plot))
            
            # 5. Departmanlara Göre Maaş Dağılımı (Box Plot)
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=self.df, x='Departman', y='Maas')
            plt.title('Departmanlara Göre Maaş Dağılımı', pad=20)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            dept_maas_plot = output_dir / 'departman_maas_dagilimi.png'
            plt.savefig(dept_maas_plot, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(str(dept_maas_plot))
            
            # 6. Telefon Türü Dağılımı
            plt.figure(figsize=(8, 6))
            sns.countplot(data=self.df, x='TelefonTuru')
            plt.title('Telefon Türü Dağılımı', pad=20)
            plt.xticks(rotation=45)
            plt.tight_layout()
            telefon_plot = output_dir / 'telefon_turu_dagilimi.png'
            plt.savefig(telefon_plot, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(str(telefon_plot))
            
            logger.info(f"{len(generated_files)} adet görsel oluşturuldu")
            return generated_files
            
        except Exception as e:
            logger.error(f"Görselleştirme oluşturulurken hata: {str(e)}")
            raise 
    
    def get_clustering_analysis(self) -> Dict[str, Any]:
        """
        Çalışan verilerinin kümeleme analizini yapar.
        
        Returns:
            Dict[str, Any]: Kümeleme analizi sonuçları
        """
        cluster_analyzer = ClusterAnalyzer(self.df)
        #clustering_results_2=ClusteringOptimizer(self.df)
        #best=False
        #try :
        #    BestModel=clustering_results_2.fit()
        #    if BestModel is not None:
        #        best =True
        #   except Exception as e :
        #       print(f"En iyi model şu hata sebebi ile bulunamadı {e}")
#en iyi modeli seçmesini clustering.py aracılığı ile yapmasını sağlayacak şekilde kullanım geliştirlilecektir.
        #if best is True:
        #    return {
        #        "Best Model":fit.best_model,  # bu alanda clustering.py aracılığı ile oluşturulan ve en optimal olarak seçilen modelin ilgili sonuçlarının gönderilmesi sağlanacaktır.
        #        "cluster_visualization":cluster_analyzer.visualize_clusters(OUTPUT_DIR)
        #        }
        kmeans_results = cluster_analyzer.kmeans_analysis()
        return {
                "kmeans_analysis": kmeans_results,
                "cluster_visualization": cluster_analyzer.visualize_clusters(OUTPUT_DIR)
            } 
        
    # iki taraflı olarak tasaralanan return işlemi daha algoritmik bir çözüm ile tek return bloğu ile ilgili bilgilerin return edilmesini sağlayacak şekilde bir yapı sağlanacaktır.