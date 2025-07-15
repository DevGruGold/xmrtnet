import React, { createContext, useContext, useState, useEffect } from 'react';

const WalletContext = createContext();

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
};

export const WalletProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const [walletType, setWalletType] = useState('');
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check for existing wallet connection
    const savedWallet = localStorage.getItem('xmrt_wallet');
    if (savedWallet) {
      const walletData = JSON.parse(savedWallet);
      setIsConnected(walletData.isConnected);
      setWalletAddress(walletData.address);
      setWalletType(walletData.type);
      setBalance(walletData.balance);
    }
    
    // Load mock transactions
    loadTransactions();
  }, []);

  const connectWallet = async (type = 'metamask') => {
    setLoading(true);
    try {
      // Simulate wallet connection - replace with actual wallet integration
      const mockAddress = generateMockAddress();
      const mockBalance = Math.random() * 10000;
      
      setIsConnected(true);
      setWalletAddress(mockAddress);
      setWalletType(type);
      setBalance(mockBalance);
      
      // Save to localStorage
      const walletData = {
        isConnected: true,
        address: mockAddress,
        type: type,
        balance: mockBalance
      };
      localStorage.setItem('xmrt_wallet', JSON.stringify(walletData));
      
      return { success: true, address: mockAddress };
    } catch (error) {
      return { success: false, error: 'Failed to connect wallet' };
    } finally {
      setLoading(false);
    }
  };

  const disconnectWallet = () => {
    setIsConnected(false);
    setWalletAddress('');
    setWalletType('');
    setBalance(0);
    localStorage.removeItem('xmrt_wallet');
  };

  const sendTransaction = async (to, amount, description = '') => {
    setLoading(true);
    try {
      // Simulate transaction - replace with actual blockchain transaction
      const txHash = generateMockTxHash();
      const newTransaction = {
        id: txHash,
        type: 'send',
        amount: -amount,
        to: to,
        from: walletAddress,
        description: description,
        status: 'pending',
        timestamp: new Date().toISOString(),
        hash: txHash
      };
      
      // Add to transactions
      const updatedTransactions = [newTransaction, ...transactions];
      setTransactions(updatedTransactions);
      
      // Update balance
      const newBalance = balance - amount;
      setBalance(newBalance);
      
      // Simulate confirmation after delay
      setTimeout(() => {
        setTransactions(prev => 
          prev.map(tx => 
            tx.id === txHash ? { ...tx, status: 'completed' } : tx
          )
        );
      }, 3000);
      
      return { success: true, txHash: txHash };
    } catch (error) {
      return { success: false, error: 'Transaction failed' };
    } finally {
      setLoading(false);
    }
  };

  const receivePayment = async (amount, description = '') => {
    const newTransaction = {
      id: generateMockTxHash(),
      type: 'receive',
      amount: amount,
      to: walletAddress,
      from: generateMockAddress(),
      description: description,
      status: 'completed',
      timestamp: new Date().toISOString(),
      hash: generateMockTxHash()
    };
    
    // Add to transactions
    const updatedTransactions = [newTransaction, ...transactions];
    setTransactions(updatedTransactions);
    
    // Update balance
    const newBalance = balance + amount;
    setBalance(newBalance);
    
    return { success: true, transaction: newTransaction };
  };

  const loadTransactions = () => {
    // Mock transaction data
    const mockTransactions = [
      {
        id: '1',
        type: 'receive',
        amount: 200.00,
        to: '0x1234...5678',
        from: '0x8765...4321',
        description: 'Deposit from Bank Account',
        status: 'completed',
        timestamp: '2025-07-10T10:00:00Z',
        hash: '0xabc123...'
      },
      {
        id: '2',
        type: 'send',
        amount: -50.00,
        to: '0x9876...1234',
        from: '0x1234...5678',
        description: 'Dinner payment',
        status: 'completed',
        timestamp: '2025-07-13T18:30:00Z',
        hash: '0xdef456...'
      },
      {
        id: '3',
        type: 'receive',
        amount: 375.50,
        to: '0x1234...5678',
        from: '0x5555...6666',
        description: 'Withdrawal to Cold Storage',
        status: 'completed',
        timestamp: '2025-07-08T14:20:00Z',
        hash: '0xghi789...'
      },
      {
        id: '4',
        type: 'send',
        amount: -25.00,
        to: '0x7777...8888',
        from: '0x1234...5678',
        description: 'Coffee and snacks',
        status: 'pending',
        timestamp: '2025-07-14T09:15:00Z',
        hash: '0xjkl012...'
      }
    ];
    
    setTransactions(mockTransactions);
  };

  const generateMockAddress = () => {
    return '0x' + Math.random().toString(16).substr(2, 8) + '...' + Math.random().toString(16).substr(2, 4);
  };

  const generateMockTxHash = () => {
    return '0x' + Math.random().toString(16).substr(2, 64);
  };

  const value = {
    isConnected,
    walletAddress,
    walletType,
    balance,
    transactions,
    loading,
    connectWallet,
    disconnectWallet,
    sendTransaction,
    receivePayment,
    loadTransactions
  };

  return (
    <WalletContext.Provider value={value}>
      {children}
    </WalletContext.Provider>
  );
};

