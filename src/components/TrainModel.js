import React, { useState } from 'react';
import translations from '../i18n/translations';

const TrainModel = ({ language }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showAssessment, setShowAssessment] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [skillLevel, setSkillLevel] = useState(null);
  const [chatHistory] = useState([
    { id: 1, title: 'Previous Chat 1',  },
    { id: 2, title: 'Previous Chat 2',  },
  ]);

  // Seviye belirleme soruları
  const questions = [
    {
      question: translations[language].question1,
      options: [
        translations[language].option1_1,
        translations[language].option1_2,
        translations[language].option1_3,
        translations[language].option1_4,
        translations[language].option1_5
      ]
    },
    {
      question: "Have you ever trained an AI model before?",
      options: [
        "Never",
        "Once or twice",
        "Several times",
        "Regularly",
        "Expert in model training"
      ]
    },
    {
      question: "How familiar are you with data preprocessing?",
      options: [
        "Not familiar at all",
        "Basic understanding",
        "Moderate experience",
        "Advanced experience",
        "Expert level"
      ]
    },
    {
      question: "What is your understanding of model parameters and hyperparameters?",
      options: [
        "No understanding",
        "Basic concept",
        "Moderate understanding",
        "Advanced knowledge",
        "Expert level"
      ]
    },
    {
      question: "How would you rate your ability to evaluate model performance?",
      options: [
        "No ability",
        "Basic metrics only",
        "Moderate understanding",
        "Advanced understanding",
        "Expert level"
      ]
    }
  ];

  const handleAnswerSelect = (answerIndex) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Calculate skill level based on answers
      const averageScore = newAnswers.reduce((a, b) => a + b, 0) / newAnswers.length;
      let level;
      if (averageScore < 1) level = "beginner";
      else if (averageScore < 2.5) level = "intermediate";
      else level = "advanced";
      
      setSkillLevel(level);
      setShowAssessment(false);
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (selectedFile) {
      console.log('File submitted:', selectedFile);
      // Add file processing logic here
    }
  };

  const renderSkillLevelGuidance = () => {
    switch (skillLevel) {
      case "beginner":
        return (
          <div className="mb-8 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
            <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">{translations[language].beginnerRecommendations}</h3>
            <ul className="list-disc list-inside text-blue-700 dark:text-blue-300 space-y-1">
              <li>{translations[language].beginnerTip1}</li>
              <li>{translations[language].beginnerTip2}</li>
              <li>{translations[language].beginnerTip3}</li>
              <li>{translations[language].beginnerTip4}</li>
            </ul>
          </div>
        );
      case "intermediate":
        return (
          <div className="mb-8 p-4 bg-green-50 dark:bg-green-900/30 rounded-lg">
            <h3 className="font-semibold text-green-800 dark:text-green-200 mb-2">{translations[language].intermediateRecommendations}</h3>
            <ul className="list-disc list-inside text-green-700 dark:text-green-300 space-y-1">
              <li>{translations[language].intermediateTip1}</li>
              <li>{translations[language].intermediateTip2}</li>
              <li>{translations[language].intermediateTip3}</li>
              <li>{translations[language].intermediateTip4}</li>
            </ul>
          </div>
        );
      case "advanced":
        return (
          <div className="mb-8 p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
            <h3 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">{translations[language].advancedRecommendations}</h3>
            <ul className="list-disc list-inside text-purple-700 dark:text-purple-300 space-y-1">
              <li>{translations[language].advancedTip1}</li>
              <li>{translations[language].advancedTip2}</li>
              <li>{translations[language].advancedTip3}</li>
              <li>{translations[language].advancedTip4}</li>
            </ul>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-dark-400 pt-40">
      {/* Sidebar Toggle Button - Her zaman görünür */}
      <button
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className="fixed left-4 top-20 z-50 p-2 rounded-lg bg-white dark:bg-dark-100 shadow-lg hover:bg-gray-100 dark:hover:bg-dark-200 transition-all duration-200"
        aria-label={isSidebarOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {isSidebarOpen ? (
          <svg className="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        ) : (
          <svg className="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
          </svg>
        )}
      </button>

      {/* Sidebar */}
      <aside 
        className={`fixed top-0 left-0 h-full w-64 bg-white dark:bg-dark-100 shadow-lg z-40 transform transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-4 pt-20">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">{translations[language].chatHistory}</h2>
          </div>
          <div className="space-y-2">
            {chatHistory.map((chat) => (
              <div
                key={chat.id}
                className="p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-200 cursor-pointer transition-colors duration-200"
              >
                <h3 className="text-sm font-medium text-gray-800 dark:text-white">{chat.title}</h3>
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div 
        className={`flex-1 transition-all duration-300 p-8 ${
          isSidebarOpen ? 'ml-64' : 'ml-0'
        }`}
      >
        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-dark-100 rounded-xl shadow-lg p-8">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">{translations[language].trainModel}</h1>

            {showAssessment ? (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
                  {translations[language].question} {currentQuestion + 1} {translations[language].of} {questions.length}
                </h2>
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  {questions[currentQuestion].question}
                </p>
                <div className="space-y-3">
                  {questions[currentQuestion].options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSelect(index)}
                      className="w-full p-3 text-left rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors duration-200"
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {renderSkillLevelGuidance()}
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="border-2 border-dashed border-gray-300 dark:border-dark-200 rounded-lg p-8 text-center">
                    <input
                      type="file"
                      onChange={handleFileChange}
                      className="hidden"
                      id="file-upload"
                      accept=".txt,.pdf,.doc,.docx"
                    />
                    <label
                      htmlFor="file-upload"
                      className="cursor-pointer flex flex-col items-center justify-center"
                    >
                      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <span className="mt-2 text-gray-600 dark:text-gray-300">
                        {selectedFile ? selectedFile.name : translations[language].uploadPrompt}
                      </span>
                    </label>
                  </div>
                  <button
                    type="submit"
                    disabled={!selectedFile}
                    className={`w-full px-4 py-3 rounded-lg ${
                      selectedFile
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    } transition-colors duration-200`}
                  >
                    {translations[language].trainModel}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainModel; 