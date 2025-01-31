import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import translations from '../i18n/translations';
import { registerUser } from '../services/authService';

const SignUp = ({ language }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  // Şifre güvenlik kontrolü
  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) {
      errors.push(translations[language].passwordMinLength);
    }
    if (!/[A-Z]/.test(password)) {
      errors.push(translations[language].passwordUppercase);
    }
    if (!/[a-z]/.test(password)) {
      errors.push(translations[language].passwordLowercase);
    }
    if (!/[0-9]/.test(password)) {
      errors.push(translations[language].passwordNumber);
    }
    if (!/[!@#$%^&*]/.test(password)) {
      errors.push(translations[language].passwordSpecial);
    }
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};

    if (!email) {
      newErrors.email = translations[language].emailRequired;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = translations[language].emailInvalid;
    }

    const passwordErrors = validatePassword(password);
    if (passwordErrors.length > 0) {
      newErrors.password = passwordErrors;
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = translations[language].passwordsNotMatch;
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      const user = await registerUser(email, password);
      console.log("User registered:", user);
      setErrors({});
      navigate('/login');
    } catch (error) {
      console.error("Registration error:", error);
      setErrors({ general: error.message });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-400 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          {translations[language].createAccount}
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-dark-100 py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {errors.general && (
            <div className="mb-4 text-red-600 text-center">
              {errors.general}
            </div>
          )}
          {errors.email && (
            <div className="mb-4 text-red-600 text-center">
              {errors.email}
            </div>
          )}
          {errors.password && (
            <div className="mb-4 text-red-600 text-center">
              <ul>
                {Array.isArray(errors.password) ? 
                  errors.password.map((error, index) => (
                    <li key={index}>{error}</li>
                  )) : 
                  <li>{errors.password}</li>
                }
              </ul>
            </div>
          )}
          {errors.confirmPassword && (
            <div className="mb-4 text-red-600 text-center">
              {errors.confirmPassword}
            </div>
          )}
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {translations[language].emailLabel}
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={translations[language].emailPlaceholder}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-dark-200 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-dark-200 dark:text-white"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {translations[language].passwordLabel}
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={translations[language].passwordPlaceholder}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-dark-200 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-dark-200 dark:text-white"
                />
              </div>
            </div>

            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {translations[language].confirmPasswordLabel}
              </label>
              <div className="mt-1">
                <input
                  id="confirm-password"
                  name="confirm-password"
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder={translations[language].confirmPasswordPlaceholder}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-dark-200 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-dark-200 dark:text-white"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {translations[language].signUp}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="relative flex justify-center text-sm">
                <span className="px-2 text-gray-500 dark:text-gray-400">
                  {translations[language].haveAccount}
                </span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                to="/login"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {translations[language].login}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUp; 