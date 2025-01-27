import React from 'react';
import translations from '../i18n/translations';
import { Link } from 'react-router-dom';

const Home = ({ language }) => {
  return (
    <div className="bg-gradient-to-b from-blue-50 via-blue-200 to-blue-50 dark:from-dark-500 dark:via-dark-200 dark:to-dark-300 transition-colors duration-300 relative overflow-hidden">
      {/* Geometrik Şekiller */}
      <div className="absolute inset-0 pointer-events-none">
        <svg className="absolute top-0 left-0 transform -translate-x-1/2 -translate-y-1/2" width="800" height="800" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="400" cy="400" r="400" fill="url(#paint0_radial)" fillOpacity="0.3"/>
          <defs>
            <radialGradient id="paint0_radial" cx="0" cy="0" r="5" gradientUnits="userSpaceOnUse" gradientTransform="translate(400 400) rotate(90) scale(400)">
              <stop stopColor="#3B82F6"/>
              <stop offset="1" stopColor="#9333EA" stopOpacity="0"/>
            </radialGradient>
          </defs>
        </svg>
      </div>

      {/* Hero Section */}
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6"> 
              <span className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 text-transparent bg-clip-text">
                Muneccim
              </span>
              <span className="ml-2">
                {translations[language].homeTitle}
              </span>
            </h1>

            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              {translations[language].homeDescription}
            </p>
              
            <div className="flex justify-center gap-4">
              <a href="/signup">
                <button className="px-8 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200">
                  {translations[language].startNow}
                </button>
              </a>
              <button className="px-8 py-3 rounded-lg border border-gray-600 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-dark-200 transition-colors duration-200">
                <Link to="/information">
                  {translations[language].moreInformation}
                </Link>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">{translations[language].featuresTitle}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl bg-gray-50 dark:bg-dark-200 hover:shadow-lg transition-all duration-200">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {translations[language].feature1Title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {translations[language].feature1Description}
              </p>
            </div>

            <div className="p-6 rounded-xl bg-gray-50 dark:bg-dark-200 hover:shadow-lg transition-all duration-200">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {translations[language].feature2Title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {translations[language].feature2Description}
              </p>
            </div>

            <div className="p-6 rounded-xl bg-gray-50 dark:bg-dark-200 hover:shadow-lg transition-all duration-200">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {translations[language].feature3Title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {translations[language].feature3Description}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;