import React, { useState } from 'react';

const Navbar = () => {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-xl font-bold text-gray-900 dark:text-white">Logo</span>
            </div>
            <div className="hidden md:ml-6 md:flex md:space-x-8">
              <a href="#" className="text-gray-900 dark:text-white hover:text-gray-700 dark:hover:text-gray-300">Pricing</a>
              <a href="#" className="text-gray-900 dark:text-white hover:text-gray-700 dark:hover:text-gray-300">Enterprise</a>
              <a href="#" className="text-gray-900 dark:text-white hover:text-gray-700 dark:hover:text-gray-300">Features</a>
              <a href="#" className="text-gray-900 dark:text-white hover:text-gray-700 dark:hover:text-gray-300">Blog</a>
            </div>
          </div>
          <div className="flex items-center">
            <button onClick={toggleDarkMode} className="text-gray-900 dark:text-white mr-4">
              {darkMode ? 'Light Mode' : 'Dark Mode'}
            </button>
            <a href="#" className="text-gray-900 dark:text-white hover:text-gray-700 dark:hover:text-gray-300">Login</a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 