import React from 'react';

const Home = () => {
  return (
    <div className="bg-gray-50 dark:bg-dark transition-colors duration-300">
      {/* Hero Section */}
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              AIWise ile Kendi Yapay Zekanızı Oluşturun
            </h1>
            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              Kendi verilerinizi kullanarak özelleştirilmiş AI modelleri oluşturun. AIWise, kullanıcı dostu arayüzü ile yapay zeka projelerinizi hayata geçirmenizi sağlar.
            </p>
            <div className="flex justify-center gap-4">
              <button className="px-8 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200">
                Ücretsiz Başla
              </button>
              <button className="px-8 py-3 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-dark-200 transition-colors duration-200">
                Daha Fazla Bilgi
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 bg-white dark:bg-dark-100">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl bg-gray-50 dark:bg-dark-200 hover:shadow-lg transition-all duration-300">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Kendi Verilerinizi Kullanın
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                AIWise, kendi verilerinizi kullanarak özelleştirilmiş AI modelleri oluşturmanıza olanak tanır.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-gray-50 dark:bg-dark-200 hover:shadow-lg transition-all duration-300">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Kullanıcı Dostu Arayüz
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Kullanıcı dostu arayüzümüz ile AI modellerinizi kolayca oluşturun ve yönetin.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-gray-50 dark:bg-dark-200 hover:shadow-lg transition-all duration-300">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Uzman Desteği
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Deneyimli eğitmenlerden birebir destek alarak projelerinizi geliştirin.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 