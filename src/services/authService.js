import { createUserWithEmailAndPassword, signInWithEmailAndPassword, onAuthStateChanged } from "firebase/auth";
import { auth } from "./firebaseConfig";

const authService = {
  register: (email, password) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const userExists = users.find(user => user.email === email);
    
    if (userExists) {
      throw new Error('User already exists');
    }

    users.push({ email, password });
    localStorage.setItem('users', JSON.stringify(users));
    return { email };
  },

  login: (email, password) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const user = users.find(user => user.email === email && user.password === password);
    
    if (!user) {
      throw new Error('Invalid credentials');
    }

    localStorage.setItem('currentUser', JSON.stringify({ email }));
    return { email };
  },

  logout: () => {
    localStorage.removeItem('currentUser');
  },

  getCurrentUser: () => {
    return JSON.parse(localStorage.getItem('currentUser'));
  }
};

const login = async (email, password) => {
  // Giriş işlemleri burada yapılacak
  // Örneğin, API çağrısı yaparak kullanıcıyı doğrulama
};

export const getCurrentUser = authService.getCurrentUser;
export default authService;

export const logout = () => {
    // Kullanıcının oturumunu kapatmak için gerekli işlemler
    localStorage.removeItem('currentUser'); // Kullanıcı bilgilerini temizle
    // Diğer oturum kapatma işlemleri...
};

// Kullanıcı oluşturma
export const registerUser = async (email, password) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    return userCredential.user;
  } catch (error) {
    console.error("Error creating user:", error);
    throw error;
  }
};

// Kullanıcı girişi
export const loginUser = async (email, password) => {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return userCredential.user;
  } catch (error) {
    console.error("Error logging in:", error);
    throw error;
  }
};

// Kullanıcının oturum durumunu kontrol et
export const checkAuthState = (callback) => {
  return onAuthStateChanged(auth, (user) => {
    callback(user);
  });
}; 