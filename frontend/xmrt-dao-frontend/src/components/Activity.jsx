import React, { useState } from 'react';
import { useWallet } from '../context/WalletContext';

const Activity = () => {
  const { transactions } = useWallet();
  const [activeFilter, setActiveFilter] = useState('all');

  const filters = [
    { id: 'all', label: 'All' },
    { id: 'transfers', label: 'Transfers' },
    { id: 'deposits', label: 'Deposits' },
    { id: 'withdrawals', label: 'Withdrawals' },
    { id: 'tokenization', label: 'Tokenization' }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(Math.abs(amount));
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'send':
        return '↗️';
      case 'receive':
        return '↙️';
      default:
        return '💰';
    }
  };

  const filteredTransactions = transactions.filter(transaction => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'transfers') return transaction.type === 'send' || transaction.type === 'receive';
    if (activeFilter === 'deposits') return transaction.type === 'receive';
    if (activeFilter === 'withdrawals') return transaction.type === 'send';
    return false;
  });

  return (
    <div className="activity-page fade-in">
      <h1 className="page-title">Activity</h1>

      <div className="activity-filters">
        {filters.map((filter) => (
          <button
            key={filter.id}
            className={`filter-btn ${activeFilter === filter.id ? 'active' : ''}`}
            onClick={() => setActiveFilter(filter.id)}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <div className="transaction-list">
        {filteredTransactions.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem 1rem',
            color: 'rgba(255, 255, 255, 0.6)'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
            <h3 style={{ marginBottom: '0.5rem', color: '#ffffff' }}>No transactions yet</h3>
            <p>Your transaction history will appear here</p>
          </div>
        ) : (
          filteredTransactions.map((transaction) => (
            <div key={transaction.id} className="transaction-item">
              <div className={`transaction-icon ${transaction.type}`}>
                {getTransactionIcon(transaction.type)}
              </div>
              
              <div className="transaction-details">
                <div className="transaction-title">
                  {transaction.description || (transaction.type === 'send' ? 'Payment sent' : 'Payment received')}
                </div>
                <div className="transaction-date">
                  {formatDate(transaction.timestamp)}
                </div>
                <div className={`transaction-status ${transaction.status}`}>
                  {transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1)}
                </div>
              </div>
              
              <div className="transaction-amount-container" style={{ textAlign: 'right' }}>
                <div className={`transaction-amount ${transaction.amount > 0 ? 'positive' : 'negative'}`}>
                  {transaction.amount > 0 ? '+' : '-'}{formatCurrency(transaction.amount)}
                </div>
                {transaction.hash && (
                  <div style={{ 
                    fontSize: '0.75rem', 
                    color: 'rgba(255, 255, 255, 0.5)',
                    fontFamily: 'monospace',
                    marginTop: '0.25rem'
                  }}>
                    {transaction.hash.slice(0, 10)}...
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {filteredTransactions.length > 0 && (
        <div style={{
          textAlign: 'center',
          padding: '2rem 1rem',
          color: 'rgba(255, 255, 255, 0.6)'
        }}>
          <p>Showing {filteredTransactions.length} transaction{filteredTransactions.length !== 1 ? 's' : ''}</p>
        </div>
      )}
    </div>
  );
};

export default Activity;

