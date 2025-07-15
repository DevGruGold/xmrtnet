import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem('xmrt_user');
    const savedAuth = localStorage.getItem('xmrt_auth');
    
    if (savedUser && savedAuth === 'true') {
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
    
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      // Simulate API call - replace with actual API
      const response = await simulateLogin(email, password);
      
      if (response.success) {
        const userData = {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          balance: response.user.balance
        };
        
        setUser(userData);
        setIsAuthenticated(true);
        
        // Save to localStorage
        localStorage.setItem('xmrt_user', JSON.stringify(userData));
        localStorage.setItem('xmrt_auth', 'true');
        
        return { success: true };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      return { success: false, error: 'Login failed. Please try again.' };
    }
  };

  const register = async (email, password, name) => {
    try {
      // Simulate API call - replace with actual API
      const response = await simulateRegister(email, password, name);
      
      if (response.success) {
        const userData = {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          balance: response.user.balance
        };
        
        setUser(userData);
        setIsAuthenticated(true);
        
        // Save to localStorage
        localStorage.setItem('xmrt_user', JSON.stringify(userData));
        localStorage.setItem('xmrt_auth', 'true');
        
        return { success: true };
      } else {
        return { success: false, error: response.error };
      }
    } catch (error) {
      return { success: false, error: 'Registration failed. Please try again.' };
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('xmrt_user');
    localStorage.removeItem('xmrt_auth');
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('xmrt_user', JSON.stringify(userData));
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    register,
    logout,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Placeholder API functions - replace with actual API calls
const simulateLogin = async (email, password) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Demo accounts
  const demoAccounts = [
    { email: 'user1@example.com', password: 'password1', name: 'John Doe', balance: 1250.75 },
    { email: 'user2@example.com', password: 'password2', name: 'Jane Smith', balance: 2500.00 }
  ];
  
  const account = demoAccounts.find(acc => acc.email === email && acc.password === password);
  
  if (account) {
    return {
      success: true,
      user: {
        id: Math.random().toString(36).substr(2, 9),
        email: account.email,
        name: account.name,
        balance: account.balance
      }
    };
  } else {
    return {
      success: false,
      error: 'Invalid email or password'
    };
  }
};

const simulateRegister = async (email, password, name) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Simulate successful registration
  return {
    success: true,
    user: {
      id: Math.random().toString(36).substr(2, 9),
      email: email,
      name: name,
      balance: 0.00
    }
  };
};

