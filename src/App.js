import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/SignUp';   
import TrainModel from './components/TrainModel';
import ProtectedRoute from './components/ProtectedRoute';
import Footer from './components/Footer';
import InformationPage from './components/InformationPage';
import { getCurrentUser, checkAuthState } from './services/authService'; // Kullanıcı bilgilerini almak için

function App() {
  const [language, setLanguage] = useState('en'); // Varsayılan dil İngilizce
  const [userEmail, setUserEmail] = useState(null);

  useEffect(() => {
    const unsubscribe = checkAuthState((user) => {
      if (user) {
        setUserEmail(user.email);
      } else {
        setUserEmail(null);
      }
    });

    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  return (
    <Router>
      <div className="App">
        <Navbar language={language} setLanguage={setLanguage} userEmail={userEmail} setUserEmail={setUserEmail} />
        <Routes>
          <Route path="/" element={<Home language={language} />} />
          <Route path="/login" element={<Login language={language} setUserEmail={setUserEmail} />} />
          <Route path="/signup" element={<Signup language={language} />} />
          <Route 
            path="/train" 
            element={
              <ProtectedRoute>
                <TrainModel language={language} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/information" 
            element={<InformationPage language={language} />} 
          />
        </Routes>
        <Footer language={language} />
      </div>
    </Router>
  );
}

export default App;
