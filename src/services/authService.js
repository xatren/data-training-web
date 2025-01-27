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

export default authService; 