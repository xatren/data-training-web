import React, { useState, useEffect } from 'react';
import translations from '../i18n/translations';
import { registerUser, loginUser } from '../services/authService';
import { storage, db, auth } from '../services/firebaseConfig';
import { ref, uploadBytes } from "firebase/storage";
import { doc, setDoc, getDoc, collection, addDoc, deleteDoc, query, where, getDocs } from "firebase/firestore";

const TrainModel = ({ language }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showAssessment, setShowAssessment] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [skillLevel, setSkillLevel] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [file, setFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isDataUploaded, setIsDataUploaded] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingStep, setTrainingStep] = useState("");
  const [progress, setProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState("");
  const [isTrainingComplete, setIsTrainingComplete] = useState(false);
  const [modelDownloadLink, setModelDownloadLink] = useState("");
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

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
      question: translations[language].question2,
      options: [
        translations[language].option2_1,
        translations[language].option2_2,
        translations[language].option2_3,
        translations[language].option2_4,
        translations[language].option2_5
      ]
    },
    {
      question: translations[language].question3,
      options: [
        translations[language].option3_1,
        translations[language].option3_2,
        translations[language].option3_3,
        translations[language].option3_4,
        translations[language].option3_5
      ]
    },
    {
      question: translations[language].question4,
      options: [
        translations[language].option4_1,
        translations[language].option4_2,
        translations[language].option4_3,
        translations[language].option4_4,
        translations[language].option4_5
      ]
    },
    {
      question: translations[language].question5,
      options: [
        translations[language].option5_1,
        translations[language].option5_2,
        translations[language].option5_3,
        translations[language].option5_4,
        translations[language].option5_5
      ]
    }
  ];

  useEffect(() => {
    const fetchUserAnswers = async () => {
      const user = auth.currentUser;
      if (user) {
        const docRef = doc(db, "userAnswers", user.uid);
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
          const data = docSnap.data();
          setAnswers(data.answers);
          setSkillLevel(data.skillLevel);
          setShowAssessment(false);
        }
      }
    };

    const fetchChatHistory = async () => {
      const user = auth.currentUser;
      if (user) {
        const chatQuery = query(collection(db, "chatHistory"), where("userId", "==", user.uid));
        const querySnapshot = await getDocs(chatQuery);
        const chats = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        setChatHistory(chats);
      }
    };

    fetchUserAnswers();
    fetchChatHistory();
  }, []);

  const handleAnswerSelect = async (answerIndex) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      const averageScore = newAnswers.reduce((a, b) => a + b, 0) / newAnswers.length;
      let level;
      if (averageScore < 1) level = "beginner";
      else if (averageScore < 2.5) level = "intermediate";
      else level = "advanced";
      
      setSkillLevel(level);
      setShowAssessment(false);

      const user = auth.currentUser;
      if (user) {
        await setDoc(doc(db, "userAnswers", user.uid), {
          answers: newAnswers,
          skillLevel: level
        });
      }
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    const validExtensions = ['.csv', '.xlsx'];

    if (selectedFile) {
      const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
      if (!validExtensions.includes(`.${fileExtension}`)) {
        setErrorMessage(translations[language].invalidFileFormat); // Geçersiz dosya formatı mesajı
        setSelectedFile(null);
      } else {
        setErrorMessage(''); // Hata mesajını sıfırla
        setSelectedFile(selectedFile);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Dosya yükleme işlemleri burada yapılacak
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

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    setSelectedFile(uploadedFile);
    
    if (uploadedFile) {
      setIsDataUploaded(true);
      
      const user = auth.currentUser;
      const storageRef = ref(storage, `uploads/${user.uid}/${uploadedFile.name}`);

      try {
        await uploadBytes(storageRef, uploadedFile);
        console.log("File uploaded successfully!");

        // Sohbet geçmişine yeni bir kayıt ekle
        if (user) {
          await addDoc(collection(db, "chatHistory"), {
            userId: user.uid,
            fileName: uploadedFile.name,
            timestamp: new Date()
          });
          // Sohbet geçmişini güncelle
          const chatQuery = query(collection(db, "chatHistory"), where("userId", "==", user.uid));
          const querySnapshot = await getDocs(chatQuery);
          const chats = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
          setChatHistory(chats);
        }
      } catch (error) {
        console.error("Error uploading file:", error);
      }
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      await deleteDoc(doc(db, "chatHistory", chatId));
      setChatHistory(chatHistory.filter(chat => chat.id !== chatId));
    } catch (error) {
      console.error("Error deleting chat:", error);
    }
  };

  const handleTrainModel = async () => {
    if (!file) return;
    setIsTraining(true);
    setTrainingStep("Veri işleniyor...");
    setProgress(10);

    // Örnek: Sunucuya dosya veya eğitim isteği gönderin
    // fetch veya WebSocket aracılığıyla Python eğitim sürecini tetikleyebilirsiniz

    // Eğitim süreci boyunca aşamaları simüle eden örnek kod (demo amaçlı):
    setTimeout(() => {
      setTrainingStep("Model eğitiliyor...");
      setProgress(50);
      setEstimatedTime("Yaklaşık 2 dakika");
    }, 2000);

    setTimeout(() => {
      setTrainingStep("Eğitim tamamlanmak üzere...");
      setProgress(90);
      setEstimatedTime("30 saniye");
    }, 4000);

    setTimeout(() => {
      setIsTrainingComplete(true);
      setIsTraining(false);
      setTrainingStep("Eğitim tamamlandı!");
      setProgress(100);
      setEstimatedTime("");
      // Eğitim sonucu modelin indirme bağlantısı örnek olarak ayarlanıyor
      setModelDownloadLink("/downloads/model_v1.h5");
    }, 6000);
  };

  const handleDownloadModel = () => {
    if (modelDownloadLink) {
      // Kullanıcıya dosyayı indirtecek bir link oluşturabilir veya
      // fetch ile blob indirip manuel indirme de yapabilirsiniz
      window.location.href = modelDownloadLink;
    }
  };

  const handleRegister = async () => {
    try {
      const user = await registerUser(email, password);
      console.log("User registered:", user);
    } catch (error) {
      console.error("Registration error:", error);
    }
  };

  const handleLogin = async () => {
    try {
      const user = await loginUser(email, password);
      console.log("User logged in:", user);
    } catch (error) {
      console.error("Login error:", error);
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
        className={`fixed top-10 left-0 h-full w-64 bg-white dark:bg-dark-100 shadow-lg z-40 transform transition-transform duration-300 ease-in-out ${
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
              className="p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-200 cursor-pointer transition-colors duration-200 relative"
            >
              <h3 className="text-sm font-medium text-gray-800 dark:text-white">{chat.fileName}</h3>
              <span className="text-xs text-gray-500 dark:text-gray-400">{new Date(chat.timestamp.seconds * 1000).toLocaleString()}</span>
              <button
                onClick={() => handleDeleteChat(chat.id)}
                className="absolute right-2 top-2 text-red-600 hover:text-red-800"
                aria-label="Delete chat"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    fillRule="evenodd"
                    d="M9 3a1 1 0 011-1h4a1 1 0 011 1v1h5a1 1 0 110 2h-1v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h5V3zm2 2h2V4h-2v1zM7 6v14h10V6H7zm3 3a1 1 0 012 0v8a1 1 0 11-2 0V9zm4 0a1 1 0 112 0v8a1 1 0 11-2 0V9z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
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
                <p className="text-gray-700 dark:text-white mb-4">
                  {questions[currentQuestion].question}
                </p>
                <div className="space-y-3">
                  {questions[currentQuestion].options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSelect(index)}
                      className="w-full p-3 text-left rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-blue-50 dark:hover:bg-dark-200 dark:text-white transition-colors duration-200"
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
                      accept=".csv, .xlsx"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="file-upload"
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
                    {selectedFile && (
                      <div className="mt-4 flex items-center justify-center">
                        <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="ml-2 text-gray-700 dark:text-gray-300">{selectedFile.name}</span>
                      </div>
                    )}
                  </div>
                  {errorMessage && <div className="text-red-600">{errorMessage}</div>}
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