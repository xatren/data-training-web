import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import translations from '../i18n/translations';
import { logout } from '../services/authService';

const Navbar = ({ language, setLanguage, userEmail, setUserEmail }) => {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleLogout = () => {
    logout();
    setUserEmail(null);
    navigate('/login');
  };

  return (
    <nav className="fixed top-0 left-0 w-full bg-white/80 dark:bg-dark-100 backdrop-blur-sm shadow-lg z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 text-transparent bg-clip-text">
                Muneccim
              </Link>
            </div>
            <div className="hidden md:ml-10 md:flex md:space-x-8">
              <a href="#" className="text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors duration-200">
                {translations[language].pricing}
              </a>
              <a href="#" className="text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors duration-200">
                {translations[language].enterprise}
              </a>
              <a href="/information" className="text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors duration-200">
                {translations[language].features}
              </a>
              <a href="#" className="text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition-colors duration-200">
                {translations[language].blog}
              </a>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg bg-gray-100 dark:bg-dark-200 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-dark-300 transition-colors duration-200"
            >
              {darkMode ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
            <button
              onClick={() => setLanguage(language === 'en' ? 'tr' : 'en')}
              className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-dark-200 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-dark-300 transition-colors duration-200"
            >
              {language === 'en' ? 'TR' : 'EN'}
            </button>
            {userEmail ? (
              <div className="relative">
                <button 
                  onClick={() => setDropdownOpen(!dropdownOpen)} 
                  className="flex items-center px-4 py-2 rounded-lg bg-gray-100 dark:bg-dark-200 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-dark-300 transition-colors duration-200"
                >
                  {userEmail}
                </button>
                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-dark-200 rounded-md shadow-lg z-10">
                    <Link 
                      to="/train" 
                      className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-dark-300"
                    >
                      {translations[language].trainModel}
                    </Link>
                    <button 
                      onClick={handleLogout} 
                      className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-dark-300"
                    >
                      {translations[language].logout}
                    </button>
                    <button 
                      className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-dark-300"
                    >
                      {translations[language].accountSettings}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex space-x-4">
                <Link to="/signup" className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200">
                  {translations[language].signUp}
                </Link>
                <Link to="/login" className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200">
                  {translations[language].login}
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 