import React from 'react';
import { Link } from 'react-router-dom';

const InformationPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-400 py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Muneccim
          </h1>
          <Link to="/" className="text-blue-600 dark:text-blue-400 hover:underline">
            Ana Sayfaya Dön
          </Link>
        </div>

        <div className="space-y-8 text-gray-600 dark:text-gray-300">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">📑 Sistem Özeti</h2>
            <div className="bg-white dark:bg-dark-200 p-6 rounded-lg shadow-sm">
              <p className="mb-4 text-lg">
                🚀 Teknik uzmanlık gerektirmeden veri analizi yapabilmeniz için tasarlanan platformumuzda:
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-blue-100 dark:bg-blue-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10M12 4v16M20 7v10" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="font-semibold">Kolay Veri Yönetimi</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      CSV/JSON dosyalarınızı sürükle-bırak ile yükleyin, otomatik temizlik ve düzenleme araçlarımızla hazır hale getirin.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-green-100 dark:bg-green-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-green-600 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="font-semibold">Akıllı Analiz</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      Verileriniz otomatik olarak analiz edilsin, en uygun kümeleme yöntemini sistemimiz sizin için belirlesin.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-purple-100 dark:bg-purple-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-purple-600 dark:text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="font-semibold">Görsel Raporlama</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      Sonuçlarınızı interaktif grafiklerle görüntüleyin, anında paylaşılabilir raporlar oluşturun.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-yellow-100 dark:bg-yellow-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="font-semibold">Model Eğitimi</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      Kendi yapay zeka modellerinizi tek tıkla eğitin, performansını gerçek zamanlı takip edin.
                    </p>
                  </div>
                </div>
              </div>

              <p className="mt-6 text-blue-600 dark:text-blue-400 font-medium">
                💡 Hiçbir kod yazmadan, sadece birkaç tıklamayla profesyonel veri analizi yapın!
              </p>
            </div>
          </section>
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">💡 Kullanım Senaryoları</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg shadow-sm">
                <div className="flex items-center mb-3">
                  <div className="bg-blue-100 dark:bg-blue-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <h3 className="ml-3 text-lg font-semibold">Müşteri Segmentasyonu</h3>
                </div>
                <ul className="list-disc pl-6 space-y-2 text-gray-600 dark:text-gray-300">
                  <li>Demografik özelliklere göre gruplandırma</li>
                  <li>Satın alma alışkanlıkları analizi</li>
                  <li>Kişiselleştirilmiş pazarlama kampanyaları</li>
                </ul>
              </div>

              <div className="p-4 bg-red-50 dark:bg-red-900 rounded-lg shadow-sm">
                <div className="flex items-center mb-3">
                  <div className="bg-red-100 dark:bg-red-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-red-600 dark:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.618 5.984A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016zM12 9v2m0 4h.01" />
                    </svg>
                  </div>
                  <h3 className="ml-3 text-lg font-semibold">Anomali Tespiti</h3>
                </div>
                <ul className="list-disc pl-6 space-y-2 text-gray-600 dark:text-gray-300">
                  <li>Şüpheli finansal işlem uyarıları</li>
                  <li>Ağ trafiğinde olağandışı aktiviteler</li>
                  <li>Üretim hattı anormallikleri</li>
                </ul>
              </div>

              <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg shadow-sm">
                <div className="flex items-center mb-3">
                  <div className="bg-green-100 dark:bg-green-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-green-600 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                    </svg>
                  </div>
                  <h3 className="ml-3 text-lg font-semibold">Ürün Kategorizasyonu</h3>
                </div>
                <ul className="list-disc pl-6 space-y-2 text-gray-600 dark:text-gray-300">
                  <li>Otomatik ürün gruplandırma</li>
                  <li>Stok yönetimi optimizasyonu</li>
                  <li>Raf düzeni optimizasyonu</li>
                </ul>
              </div>

              <div className="p-4 bg-purple-50 dark:bg-purple-900 rounded-lg shadow-sm">
                <div className="flex items-center mb-3">
                  <div className="bg-purple-100 dark:bg-purple-800 p-2 rounded-lg">
                    <svg className="w-6 h-6 text-purple-600 dark:text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <h3 className="ml-3 text-lg font-semibold">Sağlık Analizi</h3>
                </div>
                <ul className="list-disc pl-6 space-y-2 text-gray-600 dark:text-gray-300">
                  <li>Hasta gruplandırma ve risk analizi</li>
                  <li>Tıbbi görüntü sınıflandırması</li>
                  <li>Tedavi sonuçları kümeleme</li>
                </ul>
              </div>
            </div>
          </section>
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">🚀 Başlarken</h2>
            <div className="bg-white dark:bg-dark-200 p-6 rounded-lg shadow-sm">
              <ol className="list-decimal pl-6 space-y-3">
                <li>Veri setinizi CSV veya JSON formatında yükleyin</li>
                <li>İhtiyacınıza uygun ön işleme adımlarını seçin</li>
                <li>Kümeleme algoritması ve parametreleri belirleyin</li>
                <li>Analiz sonuçlarını gerçek zamanlı izleyin</li>
                <li>Raporları PDF veya CSV olarak indirin</li>
              </ol>
            </div>
          </section>
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">📁 Veri Analiz İşlevleri</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Veri Yükleme & İşleme
                </h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>CSV/JSON formatında veri yükleme</li>
                  <li>Otomatik veri tipi tanıma</li>
                  <li>Gerçek zamanlı veri önizleme</li>
                  <li>Etkileşimli veri temizleme araçları</li>
                </ul>
              </div>

              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Görselleştirme
                </h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>İnteraktif veri plotları</li>
                  <li>Özelleştirilebilir grafikler</li>
                  <li>3B veri görüntüleme</li>
                  <li>Gerçek zamanlı veri akışı görselleştirme</li>
                </ul>
              </div>
            </div>
          </section>
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">🤖 Model Eğitimi</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Model Oluşturma
                </h3>
                <ol className="list-decimal pl-6 space-y-1">
                  <li>Veri setinizi seçin</li>
                  <li>Model tipini belirleyin (Sınıflandırma/Regresyon)</li>
                  <li>Hiperparametreleri ayarlayın</li>
                  <li>Eğitim sürecini başlatın</li>
                </ol>
              </div>

              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                  </svg>
                  Model Yönetimi
                </h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Eğitilmiş modellerinizi kaydedin</li>
                  <li>Model performans karşılaştırması</li>
                  <li>API entegrasyonu ile dağıtım</li>
                  <li>Otomatik model güncelleme</li>
                </ul>
              </div>
            </div>
          </section>
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">🔬 Temel Özellikler</h2>
            <div className="space-y-4">
              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2">Veri Hazırlama</h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Eksik veri analizi ve otomatik doldurma</li>
                  <li>Aykırı değer tespiti (IQR ve Z-Score metodları)</li>
                  <li>Gelişmiş özellik ölçeklendirme (Min-Max, Robust Scaler)</li>
                </ul>
              </div>

              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2">Kümeleme Algoritmaları</h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>K-Means ile optimal küme seçimi</li>
                  <li>DBSCAN yoğunluk tabanlı kümeleme</li>
                  <li>Hiyerarşik kümeleme yöntemleri</li>
                </ul>
              </div>

              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2">Gerçek Zamanlı Analiz</h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Akış verileri için adaptif öğrenme</li>
                  <li>Dinamik parametre optimizasyonu</li>
                  <li>Canlı performans izleme</li>
                </ul>
              </div>
            </div>
          </section>
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">📊 Performans Metrikleri</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2">Veri İşleme</h3>
                <ul className="space-y-1">
                  <li>✔️ Eksik veri oranı: &lt;%5</li>
                  <li>✔️ Aykırı değer tespit doğruluğu: %95</li>
                  <li>✔️ Ölçeklendirme stabilitesi: %98</li>
                </ul>
              </div>

              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2">Kümeleme</h3>
                <ul className="space-y-1">
                  <li>⏱️ Model güncelleme süresi: &lt;50ms</li>
                  <li>📈 Ortalama Silhouette skoru: 0.65</li>
                  <li>🔢 Küme stabilitesi: %92</li>
                </ul>
              </div>
            </div>
          </section>

          

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">📚 Teknik Detaylar</h2>
            <div className="space-y-4">
              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2">Matematiksel Modeller</h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>PCA ile boyut indirgeme</li>
                  <li>t-SNE görselleştirme</li>
                  <li>Ward hiyerarşik kümeleme</li>
                </ul>
              </div>

              <div className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm">
                <h3 className="font-semibold mb-2">Sistem Özellikleri</h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Gerçek zamanlı veri işleme</li>
                  <li>Dağıtık hesaplama desteği</li>
                  <li>API entegrasyonu</li>
                </ul>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default InformationPage; 