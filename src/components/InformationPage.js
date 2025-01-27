import React from 'react';
import { Link } from 'react-router-dom';
import translations from '../i18n/translations';

const InformationPage = ({ language }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-400 py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {translations[language].informationTitle}
          </h1>
          <Link 
            to="/" 
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            {translations[language].backToHome}
          </Link>
        </div>

        <div className="space-y-8 text-gray-600 dark:text-gray-300">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              {translations[language].infoSection1Title}
            </h2>
            <p className="mb-4">{translations[language].infoSection1Content}</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              {translations[language].infoSection2Title}
            </h2>
            <ul className="list-disc pl-6 space-y-2">
              {translations[language].infoSection2Points.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              {translations[language].infoSection3Title}
            </h2>
            <div className="space-y-4">
              <p>{translations[language].infoSection3Step1}</p>
              <p>{translations[language].infoSection3Step2}</p>
              <p>{translations[language].infoSection3Step3}</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              {translations[language].infoSection4Title}
            </h2>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {translations[language].infoSection4Benefits.map((benefit, index) => (
                <li 
                  key={index}
                  className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm"
                >
                  {benefit}
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              {translations[language].infoSection5Title}
            </h2>
            <div className="space-y-4">
              {translations[language].infoSection5Examples.map((example, index) => (
                <div 
                  key={index}
                  className="p-4 bg-white dark:bg-dark-200 rounded-lg shadow-sm"
                >
                  <h3 className="font-medium mb-2">{example.title}</h3>
                  <p>{example.description}</p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              {translations[language].infoSection6Title}
            </h2>
            <div className="space-y-4 bg-white dark:bg-dark-200 p-6 rounded-lg">
              <ol className="list-decimal pl-6 space-y-3">
                {translations[language].infoSection6Steps.map((step, index) => (
                  <li key={index} className="leading-relaxed">
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              {translations[language].infoSection7Title}
            </h2>
            <div className="grid gap-6 md:grid-cols-2">
              {translations[language].scenarioExamples.map((example, index) => (
                <div key={index} className="bg-white dark:bg-dark-200 p-6 rounded-lg shadow-sm">
                  <h3 className="font-semibold text-lg mb-3">{example.title}</h3>
                  <ul className="list-disc pl-5 space-y-2">
                    {example.steps.map((step, stepIndex) => (
                      <li key={stepIndex} className="text-gray-600 dark:text-gray-300">
                        {step}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default InformationPage; 