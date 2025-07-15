import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useWallet } from '../context/WalletContext';

const Dashboard = () => {
  const { user } = useAuth();
  const { balance, isConnected } = useWallet();
  const [showSendModal, setShowSendModal] = useState(false);
  const [showReceiveModal, setShowReceiveModal] = useState(false);

  const displayBalance = isConnected ? balance : (user?.balance || 0);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="dashboard fade-in">
      <div className="balance-card">
        <div className="balance-header">
          Balance
        </div>
        <div className="balance-header" style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
          {user?.name || 'User'}
        </div>
        <div className="balance-amount">
          {formatCurrency(displayBalance)}
        </div>
        <div className="balance-actions">
          <button className="action-btn send" onClick={() => setShowSendModal(true)}>
            Send
          </button>
          <button className="action-btn receive" onClick={() => setShowReceiveModal(true)}>
            Receive
          </button>
          <button className="action-btn add">
            Add
          </button>
        </div>
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <h3 className="feature-title">Send Money</h3>
          <p className="feature-description">
            Send money to friends, family, or businesses instantly.
          </p>
          <button className="feature-btn" onClick={() => setShowSendModal(true)}>
            Send
          </button>
        </div>

        <div className="feature-card">
          <h3 className="feature-title">Request Money</h3>
          <p className="feature-description">
            Request money from friends, family, or customers.
          </p>
          <button className="feature-btn" onClick={() => setShowReceiveModal(true)}>
            Receive
          </button>
        </div>

        <div className="feature-card">
          <h3 className="feature-title">Add Funds</h3>
          <p className="feature-description">
            Add funds to your account from a bank or card.
          </p>
          <button className="feature-btn">
            Add
          </button>
        </div>

        <div className="feature-card">
          <h3 className="feature-title">Tokenize Asset</h3>
          <p className="feature-description">
            Convert physical assets into digital tokens.
          </p>
          <button className="feature-btn">
            Tokenize
          </button>
        </div>
      </div>

      {/* Send Modal */}
      {showSendModal && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div className="modal-content" style={{
            background: 'rgba(26, 26, 26, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '2rem',
            width: '100%',
            maxWidth: '400px'
          }}>
            <h2 style={{ marginBottom: '1rem', color: '#ffffff' }}>Send Money</h2>
            <form>
              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label className="form-label">Recipient</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Email or wallet address"
                />
              </div>
              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label className="form-label">Amount ($)</label>
                <input
                  type="number"
                  className="form-input"
                  placeholder="0.00"
                  step="0.01"
                />
              </div>
              <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                <label className="form-label">Description (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="What's it for?"
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button
                  type="button"
                  onClick={() => setShowSendModal(false)}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    background: 'transparent',
                    color: '#ffffff',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    border: 'none',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
                    color: '#ffffff',
                    cursor: 'pointer'
                  }}
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Receive Modal */}
      {showReceiveModal && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div className="modal-content" style={{
            background: 'rgba(26, 26, 26, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '2rem',
            width: '100%',
            maxWidth: '400px',
            textAlign: 'center'
          }}>
            <h2 style={{ marginBottom: '1rem', color: '#ffffff' }}>Receive Money</h2>
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{
                width: '200px',
                height: '200px',
                background: '#ffffff',
                borderRadius: '12px',
                margin: '0 auto 1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.875rem',
                color: '#000000'
              }}>
                QR Code
              </div>
              <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.875rem' }}>
                Share this QR code or your wallet address
              </p>
              <p style={{ 
                color: '#10b981', 
                fontSize: '0.75rem', 
                fontFamily: 'monospace',
                background: 'rgba(16, 185, 129, 0.1)',
                padding: '0.5rem',
                borderRadius: '6px',
                marginTop: '1rem'
              }}>
                {isConnected ? 'wallet_address_placeholder' : user?.email}
              </p>
            </div>
            <button
              onClick={() => setShowReceiveModal(false)}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: 'none',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: '#ffffff',
                cursor: 'pointer'
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

