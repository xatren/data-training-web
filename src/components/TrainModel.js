import React, { useState, useEffect, useMemo } from 'react';
import { usePapaParse } from 'react-papaparse';
import { useTable, usePagination, useSortBy, useFilters } from 'react-table';
import translations from '../i18n/translations';
import { registerUser, loginUser } from '../services/authService';
import { storage, db, auth } from '../services/firebaseConfig';
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { doc, setDoc, getDoc, collection, addDoc, deleteDoc, query, where, getDocs } from "firebase/firestore";
import { useCSVReader } from 'react-papaparse';

const TrainModel = ({ language }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [csvData, setCsvData] = useState([]);
  const [showAssessment, setShowAssessment] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [skillLevel, setSkillLevel] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
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
  const [isAnalyzed, setIsAnalyzed] = useState(false);
  const [pageSize, setPageSize] = useState(10);
  const [isCsvLoaded, setIsCsvLoaded] = useState(false);
  const { CSVReader } = useCSVReader();
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [visualizations, setVisualizations] = useState([]);
  const [geminiAnalysis, setGeminiAnalysis] = useState(null);

  const { readString } = usePapaParse();

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
  }, [language]);

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

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    
    // Dosya doğrulama
    if (!uploadedFile.name.endsWith('.csv')) {
        setErrorMessage('Sadece CSV dosyaları yükleyebilirsiniz');
        return;
    }
    
    if (uploadedFile.size > 5 * 1024 * 1024) {
        setErrorMessage('Dosya boyutu 5MB üzerinde olamaz');
        return;
    }
    
    setSelectedFile(uploadedFile);
    
    if (uploadedFile) {
        setIsDataUploaded(true);
        
        try {
            // Firebase storage referansı oluştur
            const storageRef = ref(storage, `uploads/${uploadedFile.name}`);

            // Firebase'e dosyayı yükle
            await uploadBytes(storageRef, uploadedFile);
            console.log("File uploaded successfully!");

            // Yüklenen dosyanın URL'sini al
            const downloadURL = await getDownloadURL(storageRef);

            // CSV'yi parse et
            const reader = new FileReader();
            reader.onload = async (e) => {
                const text = e.target.result;
                readString(text, {
                    header: true,
                    complete: async (results) => {
                        setCsvData(results.data);
                        setIsAnalyzed(true);
                        setIsCsvLoaded(true);

                        // Sohbet geçmişine kaydet
                        const user = auth.currentUser;
                        if (user) {
                            await addDoc(collection(db, "chatHistory"), {
                                userId: user.uid,
                                fileName: uploadedFile.name,
                                fileUrl: downloadURL,
                                timestamp: new Date()
                            });

                            // Sohbet geçmişini güncelle
                            const chatQuery = query(
                                collection(db, "chatHistory"), 
                                where("userId", "==", user.uid)
                            );
                            const querySnapshot = await getDocs(chatQuery);
                            const chats = querySnapshot.docs.map(doc => ({
                                id: doc.id,
                                ...doc.data()
                            }));
                            setChatHistory(chats);
                        }
                    }
                });
            };
            reader.readAsText(uploadedFile);

        } catch (error) {
            console.error("Error uploading file:", error);
            setErrorMessage(translations[language].fetchError);
            setIsDataUploaded(false);
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
    if (!selectedFile) return;
    
    try {
        setIsTraining(true);
        setTrainingStep("Veri işleniyor...");
        setProgress(10);

        // Firebase'den dosya URL'sini al
        const storageRef = ref(storage, `uploads/${selectedFile.name}`);
        const downloadURL = await getDownloadURL(storageRef);

        // Backend'e analiz isteği gönder
        const response = await fetch('http://localhost:8000/analyze/csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                file_url: downloadURL,
                file_name: selectedFile.name 
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Sunucu hatası');
        }

        setTrainingStep("Analiz tamamlandı!");
        setProgress(100);
        
        // Analiz sonuçlarını state'e kaydet
        setAnalysisResults(data);
        setIsTrainingComplete(true);

        // Görselleştirmeleri göster
        if (data.visualization_files && data.visualization_files.length > 0) {
            const visualizations = data.visualization_files.map(file => ({
                url: `http://localhost:8000/static/${file.split('/').pop()}`,
                title: file.split('/').pop().replace('.png', '')
            }));
            setVisualizations(visualizations);
        }

        // Gemini analizini göster
        if (data.gemini_analysis) {
            setGeminiAnalysis(data.gemini_analysis);
        }

    } catch (error) {
        console.error('Training error:', error);
        setErrorMessage(
            error.message === '[object Object]' 
            ? 'Beklenmeyen bir hata oluştu' 
            : error.message
        );
        setTrainingStep("Hata oluştu!");
    } finally {
        setIsTraining(false);
    }
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

  const handleAnalyze = () => {
    setIsAnalyzed(true);
  };

  const handleNewChat = () => {
    // Mevcut durumu sıfırla
    setSelectedFile(null);
    setCsvData([]);
    setIsDataUploaded(false);
    setIsAnalyzed(false);
    setIsCsvLoaded(false);
    setIsTraining(false);
    setTrainingStep("");
    setProgress(0);
    setEstimatedTime("");
    setIsTrainingComplete(false);
    setModelDownloadLink("");
    setErrorMessage("");
  };

  const handleChatSelect = async (chat) => {
    try {
      // Basitleştirilmiş dosya yolu
      const fileRef = ref(storage, `uploads/${chat.fileName}`);
      
      try {
        const url = await getDownloadURL(fileRef);
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'text/csv;charset=UTF-8',
          },
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const text = await response.text();
        
        readString(text, {
          header: true,
          complete: (results) => {
            if (results.data && results.data.length > 0) {
              setCsvData(results.data);
              setSelectedFile({ name: chat.fileName });
              setIsAnalyzed(true);
              setIsCsvLoaded(true);
              setIsDataUploaded(true);
              setErrorMessage('');
            } else {
              throw new Error('CSV data is empty or invalid');
            }
          },
          error: (error) => {
            console.error('Error parsing CSV:', error);
            setErrorMessage(translations[language].csvParseError);
          }
        });
      } catch (storageError) {
        console.error('Error accessing file in storage:', storageError);
        setErrorMessage(translations[language].fetchError);
      }
    } catch (error) {
      console.error('Error in handleChatSelect:', error);
      setErrorMessage(translations[language].fetchError);
    }
  };

  const handleAnalyzeData = async (data) => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/analyze/csv', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: data })
      });

      if (!response.ok) {
        throw new Error('Analiz sırasında bir hata oluştu');
      }

      const results = await response.json();
      setAnalysisResults(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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

  const DefaultColumnFilter = ({
    column: { filterValue, setFilter },
  }) => {
    return (
      <input
        value={filterValue || ''}
        onChange={e => {
          setFilter(e.target.value || undefined); // Set undefined to remove the filter entirely
        }}
        placeholder={`Search...`}
        className="mt-1 block w-full"
      />
    );
  };

  const columns = useMemo(() => {
    if (csvData.length === 0) return [];
    return Object.keys(csvData[0]).map(key => ({
      Header: key,
      accessor: key,
      Filter: DefaultColumnFilter,
    }));
  }, [csvData]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize: setTablePageSize,
    state: { pageIndex, pageSize: currentPageSize },
  } = useTable(
    {
      columns,
      data: csvData,
      initialState: { pageIndex: 0, pageSize },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  const renderCSVTable = () => (
    <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
      <table className="min-w-full bg-white dark:bg-dark-100">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(column => (
                <th
                  key={column.id}
                  className="px-4 py-2 border-b-2 border-gray-200 dark:border-dark-200 text-left"
                  {...column.getHeaderProps(column.getSortByToggleProps())}
                >
                  {column.render('Header')}
                  <span>
                    {column.isSorted
                      ? column.isSortedDesc
                        ? ' 🔽'
                        : ' 🔼'
                      : ''}
                  </span>
                  <div>{column.canFilter ? column.render('Filter') : null}</div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {page.map((row, rowIndex) => {
            prepareRow(row);
            return (
              <tr key={`row-${rowIndex}`} className="hover:bg-gray-100 dark:hover:bg-dark-200">
                {row.cells.map((cell, cellIndex) => (
                  <td 
                    key={`cell-${rowIndex}-${cellIndex}`}
                    className="px-4 py-2 border-b border-gray-200 dark:border-dark-200"
                  >
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="mt-4 flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => gotoPage(0)}
            disabled={!canPreviousPage}
            className="px-3 py-1 rounded border"
          >
            {'<<'}
          </button>
          <button
            onClick={() => previousPage()}
            disabled={!canPreviousPage}
            className="px-3 py-1 rounded border"
          >
            {'<'}
          </button>
          <button
            onClick={() => nextPage()}
            disabled={!canNextPage}
            className="px-3 py-1 rounded border"
          >
            {'>'}
          </button>
          <button
            onClick={() => gotoPage(pageCount - 1)}
            disabled={!canNextPage}
            className="px-3 py-1 rounded border"
          >
            {'>>'}
          </button>
        </div>
        <span>
          Sayfa{' '}
          <strong>
            {pageIndex + 1} / {pageOptions.length}
          </strong>
        </span>
        <select
          value={pageSize}
          onChange={e => {
            setPageSize(Number(e.target.value));
          }}
          className="px-2 py-1 rounded border"
        >
          {[10, 20, 30, 40, 50].map(size => (
            <option key={size} value={size}>
              {size} satır göster
            </option>
          ))}
        </select>
      </div>
    </div>
  );

  const renderContent = () => {
    if (showAssessment) {
      return (
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
      );
    }

    if (!isCsvLoaded) {
      return (
        <>
          {renderSkillLevelGuidance()}
          <form onSubmit={(e) => e.preventDefault()} className="space-y-6">
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
          </form>
        </>
      );
    }

    return (
      <div className="space-y-6">
        {renderCSVTable()}
        <div className="flex justify-center mt-6">
          <button
            onClick={handleTrainModel}
            disabled={isTraining}
            className={`px-6 py-3 rounded-lg text-white font-semibold transition-colors duration-200 ${
              isTraining 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isTraining ? translations[language].training : translations[language].trainModel}
          </button>
        </div>
        {isTraining && (
          <div className="mt-4">
            <div className="text-center text-gray-700 dark:text-gray-300 mb-2">
              {trainingStep}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            {estimatedTime && (
              <div className="text-center text-sm text-gray-600 dark:text-gray-400 mt-2">
                {estimatedTime}
              </div>
            )}
          </div>
        )}
        {isTrainingComplete && modelDownloadLink && (
          <div className="flex justify-center mt-4">
            <button
              onClick={handleDownloadModel}
              className="px-6 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold transition-colors duration-200"
            >
              {translations[language].downloadModel}
            </button>
          </div>
        )}
        {isTrainingComplete && (
          <div className="mt-8 space-y-6">
            {/* Gemini Analizi */}
            {geminiAnalysis && (
              <div className="bg-white dark:bg-dark-100 rounded-lg p-6 shadow">
                <h3 className="text-lg font-semibold mb-4">Analiz Sonuçları</h3>
                <div className="prose dark:prose-invert">
                  {geminiAnalysis}
                </div>
              </div>
            )}

            {/* Görselleştirmeler */}
            {visualizations.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {visualizations.map((viz, index) => (
                  <div key={index} className="bg-white dark:bg-dark-100 rounded-lg p-4 shadow">
                    <h4 className="text-md font-medium mb-2">{viz.title}</h4>
                    <img 
                      src={viz.url} 
                      alt={viz.title}
                      className="w-full h-auto rounded"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-dark-400">
      <div className="flex-1 pt-40 pb-24">
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
            {/* Yeni Sohbet Butonu */}
            <button
              onClick={handleNewChat}
              className="w-full mb-6 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200"
            >
              <svg 
                className="w-5 h-5" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 4v16m8-8H4" 
                />
              </svg>
              <span>{translations[language].newChat || 'New Chat'}</span>
            </button>

            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
                {translations[language].chatHistory}
              </h2>
            </div>
            <div className="space-y-2">
              {chatHistory.map((chat) => (
                <div
                  key={chat.id}
                  className="p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-200 cursor-pointer transition-colors duration-200 relative group"
                  onClick={() => handleChatSelect(chat)}
                >
                  <div className="pr-8">
                    <h3 className="text-sm font-medium text-gray-800 dark:text-white">
                      {chat.fileName}
                    </h3>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(chat.timestamp.seconds * 1000).toLocaleString()}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteChat(chat.id);
                    }}
                    className="absolute right-2 top-2 text-red-600 hover:text-red-800 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
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
          className={`transition-all duration-300 p-8 ${
            isSidebarOpen ? 'ml-64' : 'ml-0'
          }`}
        >
          <div className={`max-w-${isCsvLoaded ? '6xl' : '4xl'} mx-auto`}>
            <div className="bg-white dark:bg-dark-100 rounded-xl shadow-lg p-8">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">{translations[language].trainModel}</h1>
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainModel; 