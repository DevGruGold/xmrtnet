import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useWallet } from '../context/WalletContext';

const Header = () => {
  const { user, logout } = useAuth();
  const { isConnected, walletAddress, connectWallet, disconnectWallet } = useWallet();
  const [showProfile, setShowProfile] = useState(false);

  const handleWalletClick = async () => {
    if (isConnected) {
      disconnectWallet();
    } else {
      await connectWallet();
    }
  };

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <header className="header">
      <div className="header-left">
        <a href="/" className="logo">XMRTNET</a>
      </div>

      <div className="header-right">
        <button className="language-btn">
          🌐 English
        </button>

        <button className="wallet-btn" onClick={handleWalletClick}>
          {isConnected ? (
            <>
              🔗 {formatAddress(walletAddress)}
            </>
          ) : (
            <>
              🔗 Connect Wallet
            </>
          )}
        </button>

        <button className="notification-btn">
          🔔
          <span className="notification-badge">2</span>
        </button>

        <div className="profile-container" style={{ position: 'relative' }}>
          <button 
            className="profile-btn"
            onClick={() => setShowProfile(!showProfile)}
          >
            👤
          </button>

          {showProfile && (
            <div 
              className="profile-dropdown"
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                background: 'rgba(26, 26, 26, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem',
                minWidth: '200px',
                zIndex: 1000,
                marginTop: '0.5rem'
              }}
            >
              <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <p style={{ color: '#ffffff', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                  {user?.name || 'User'}
                </p>
                <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                  {user?.email}
                </p>
              </div>
              
              <button
                onClick={() => {
                  logout();
                  setShowProfile(false);
                }}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#ffffff',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;

