import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Banking = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  const bankingTabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'accounts', label: 'Accounts', icon: '🏦' },
    { id: 'cards', label: 'Cards', icon: '💳' },
    { id: 'loans', label: 'Loans', icon: '💰' }
  ];

  const mockAccounts = [
    {
      id: 1,
      name: 'XMRT Checking',
      type: 'Checking',
      balance: 2450.75,
      accountNumber: '****1234'
    },
    {
      id: 2,
      name: 'XMRT Savings',
      type: 'Savings',
      balance: 15750.00,
      accountNumber: '****5678'
    },
    {
      id: 3,
      name: 'XMRT Investment',
      type: 'Investment',
      balance: 8920.50,
      accountNumber: '****9012'
    }
  ];

  const mockCards = [
    {
      id: 1,
      name: 'XMRT Debit Card',
      type: 'Debit',
      number: '****1234',
      status: 'Active',
      limit: 5000
    },
    {
      id: 2,
      name: 'XMRT Credit Card',
      type: 'Credit',
      number: '****5678',
      status: 'Active',
      limit: 10000,
      balance: 1250.00
    }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getTotalBalance = () => {
    return mockAccounts.reduce((total, account) => total + account.balance, 0);
  };

  return (
    <div className="banking-page fade-in">
      <h1 className="page-title">Banking</h1>

      <div className="banking-tabs" style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '2rem',
        overflowX: 'auto'
      }}>
        {bankingTabs.map((tab) => (
          <button
            key={tab.id}
            className={`filter-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="banking-overview">
          <div className="balance-card" style={{ marginBottom: '2rem' }}>
            <div className="balance-header">Total Balance</div>
            <div className="balance-amount" style={{ fontSize: '2.5rem' }}>
              {formatCurrency(getTotalBalance())}
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-around', 
              marginTop: '1rem',
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '0.875rem'
            }}>
              <div>
                <div>Checking</div>
                <div style={{ color: '#10b981', fontWeight: 'bold' }}>
                  {formatCurrency(mockAccounts[0].balance)}
                </div>
              </div>
              <div>
                <div>Savings</div>
                <div style={{ color: '#10b981', fontWeight: 'bold' }}>
                  {formatCurrency(mockAccounts[1].balance)}
                </div>
              </div>
              <div>
                <div>Investment</div>
                <div style={{ color: '#10b981', fontWeight: 'bold' }}>
                  {formatCurrency(mockAccounts[2].balance)}
                </div>
              </div>
            </div>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <h3 className="feature-title">💸 Transfer Money</h3>
              <p className="feature-description">
                Transfer money between your accounts or to external accounts.
              </p>
              <button className="feature-btn">Transfer</button>
            </div>

            <div className="feature-card">
              <h3 className="feature-title">📱 Mobile Deposit</h3>
              <p className="feature-description">
                Deposit checks by taking a photo with your mobile device.
              </p>
              <button className="feature-btn">Deposit</button>
            </div>

            <div className="feature-card">
              <h3 className="feature-title">💳 Manage Cards</h3>
              <p className="feature-description">
                View and manage your debit and credit cards.
              </p>
              <button className="feature-btn">Manage</button>
            </div>

            <div className="feature-card">
              <h3 className="feature-title">📊 Account Statements</h3>
              <p className="feature-description">
                Download and view your account statements.
              </p>
              <button className="feature-btn">View</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'accounts' && (
        <div className="accounts-section">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ color: '#ffffff' }}>Your Accounts</h2>
            <button style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer'
            }}>
              + Add Account
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {mockAccounts.map((account) => (
              <div key={account.id} className="feature-card" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1.5rem'
              }}>
                <div>
                  <h3 style={{ color: '#ffffff', marginBottom: '0.5rem' }}>
                    {account.name}
                  </h3>
                  <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                    {account.type} • {account.accountNumber}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: 'bold', 
                    color: '#10b981',
                    marginBottom: '0.5rem'
                  }}>
                    {formatCurrency(account.balance)}
                  </div>
                  <button style={{
                    padding: '0.25rem 0.75rem',
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '6px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.75rem'
                  }}>
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'cards' && (
        <div className="cards-section">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ color: '#ffffff' }}>Your Cards</h2>
            <button style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer'
            }}>
              + Request Card
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {mockCards.map((card) => (
              <div key={card.id} className="feature-card" style={{
                background: card.type === 'Credit' 
                  ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)'
                  : 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
                border: `1px solid ${card.type === 'Credit' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(16, 185, 129, 0.2)'}`,
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ color: '#ffffff', marginBottom: '0.5rem' }}>
                      {card.name}
                    </h3>
                    <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                      {card.type} • {card.number}
                    </p>
                    <div style={{ 
                      display: 'inline-block',
                      padding: '0.25rem 0.5rem',
                      background: card.status === 'Active' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                      color: card.status === 'Active' ? '#10b981' : '#ef4444',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      marginTop: '0.5rem'
                    }}>
                      {card.status}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                      Limit: {formatCurrency(card.limit)}
                    </div>
                    {card.balance && (
                      <div style={{ color: '#f59e0b', fontWeight: 'bold', marginTop: '0.25rem' }}>
                        Balance: {formatCurrency(card.balance)}
                      </div>
                    )}
                  </div>
                </div>
                <div style={{ 
                  display: 'flex', 
                  gap: '0.5rem', 
                  marginTop: '1rem'
                }}>
                  <button style={{
                    padding: '0.5rem 1rem',
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '6px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.875rem'
                  }}>
                    Freeze Card
                  </button>
                  <button style={{
                    padding: '0.5rem 1rem',
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '6px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.875rem'
                  }}>
                    View PIN
                  </button>
                  <button style={{
                    padding: '0.5rem 1rem',
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '6px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.875rem'
                  }}>
                    Settings
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'loans' && (
        <div className="loans-section">
          <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>💰</div>
            <h3 style={{ marginBottom: '1rem', color: '#ffffff' }}>No Active Loans</h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
              You don't have any active loans. Apply for a loan to get started.
            </p>
            <button style={{
              padding: '0.75rem 1.5rem',
              background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '1rem'
            }}>
              Apply for Loan
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Banking;

