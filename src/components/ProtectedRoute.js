import React from 'react';
import { Navigate } from 'react-router-dom';
import { auth } from '../services/firebaseConfig';

const ProtectedRoute = ({ children }) => {
  const user = auth.currentUser;

  if (!user) {
    // Kullanıcı giriş yapmamışsa login sayfasına yönlendir
    return <Navigate to="/login" />;
  }

  return children;
};

export default ProtectedRoute; 