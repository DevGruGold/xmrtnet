import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import Activity from './components/Activity';
import Banking from './components/Banking';
import Terminal from './components/Terminal';
import Assets from './components/Assets';
import Settings from './components/Settings';
import Navigation from './components/Navigation';
import Header from './components/Header';

// Context
import { AuthProvider, useAuth } from './context/AuthContext';
import { WalletProvider } from './context/WalletContext';

function AppContent() {
  const { isAuthenticated } = useAuth();
  const [currentPage, setCurrentPage] = useState('home');

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Dashboard />;
      case 'activity':
        return <Activity />;
      case 'banking':
        return <Banking />;
      case 'terminal':
        return <Terminal />;
      case 'assets':
        return <Assets />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        {renderPage()}
      </main>
      <Navigation currentPage={currentPage} setCurrentPage={setCurrentPage} />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <WalletProvider>
        <div className="App">
          <AppContent />
        </div>
      </WalletProvider>
    </AuthProvider>
  );
}

export default App;

