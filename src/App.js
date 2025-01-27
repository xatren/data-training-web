import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Login from './components/Login';
import SignUp from './components/SignUp';
import TrainModel from './components/TrainModel';
import ProtectedRoute from './components/ProtectedRoute';
import Footer from './components/Footer';
import InformationPage from './components/InformationPage';

function App() {
  const [language, setLanguage] = useState('en'); // Varsayılan dil İngilizce

  return (
    <Router>
      <div className="App">
        <Navbar language={language} setLanguage={setLanguage} />
        <Routes>
          <Route path="/" element={<Home language={language} />} />
          <Route path="/login" element={<Login language={language} />} />
          <Route path="/signup" element={<SignUp language={language} />} />
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
