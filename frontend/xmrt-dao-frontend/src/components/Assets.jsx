import React, { useState } from 'react';

const Assets = () => {
  const [activeTab, setActiveTab] = useState('portfolio');

  const assetTabs = [
    { id: 'portfolio', label: 'Portfolio', icon: '📊' },
    { id: 'crypto', label: 'Crypto', icon: '₿' },
    { id: 'stocks', label: 'Stocks', icon: '📈' },
    { id: 'nfts', label: 'NFTs', icon: '🎨' }
  ];

  const mockCrypto = [
    {
      id: 1,
      symbol: 'BTC',
      name: 'Bitcoin',
      amount: 0.5,
      value: 21500.00,
      change: 2.5,
      icon: '₿'
    },
    {
      id: 2,
      symbol: 'ETH',
      name: 'Ethereum',
      amount: 2.3,
      value: 4600.00,
      change: -1.2,
      icon: 'Ξ'
    },
    {
      id: 3,
      symbol: 'XMRT',
      name: 'XMRT Token',
      amount: 1000,
      value: 2500.00,
      change: 5.8,
      icon: '🚀'
    }
  ];

  const mockStocks = [
    {
      id: 1,
      symbol: 'AAPL',
      name: 'Apple Inc.',
      shares: 10,
      value: 1750.00,
      change: 1.8,
      icon: '🍎'
    },
    {
      id: 2,
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      shares: 5,
      value: 1200.00,
      change: -2.1,
      icon: '🚗'
    },
    {
      id: 3,
      symbol: 'MSFT',
      name: 'Microsoft Corp.',
      shares: 8,
      value: 2400.00,
      change: 0.9,
      icon: '💻'
    }
  ];

  const mockNFTs = [
    {
      id: 1,
      name: 'CryptoPunk #1234',
      collection: 'CryptoPunks',
      value: 15000.00,
      image: '🎭'
    },
    {
      id: 2,
      name: 'Bored Ape #5678',
      collection: 'Bored Ape Yacht Club',
      value: 8500.00,
      image: '🐵'
    },
    {
      id: 3,
      name: 'Art Block #9012',
      collection: 'Art Blocks',
      value: 3200.00,
      image: '🎨'
    }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (percentage) => {
    const sign = percentage >= 0 ? '+' : '';
    return `${sign}${percentage.toFixed(2)}%`;
  };

  const getTotalPortfolioValue = () => {
    const cryptoTotal = mockCrypto.reduce((sum, asset) => sum + asset.value, 0);
    const stocksTotal = mockStocks.reduce((sum, asset) => sum + asset.value, 0);
    const nftsTotal = mockNFTs.reduce((sum, asset) => sum + asset.value, 0);
    return cryptoTotal + stocksTotal + nftsTotal;
  };

  return (
    <div className="assets-page fade-in">
      <h1 className="page-title">Assets</h1>

      <div className="asset-tabs" style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '2rem',
        overflowX: 'auto'
      }}>
        {assetTabs.map((tab) => (
          <button
            key={tab.id}
            className={`filter-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'portfolio' && (
        <div className="portfolio-overview">
          <div className="balance-card" style={{ marginBottom: '2rem' }}>
            <div className="balance-header">Total Portfolio Value</div>
            <div className="balance-amount" style={{ fontSize: '2.5rem' }}>
              {formatCurrency(getTotalPortfolioValue())}
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-around', 
              marginTop: '1rem',
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '0.875rem'
            }}>
              <div>
                <div>Crypto</div>
                <div style={{ color: '#f59e0b', fontWeight: 'bold' }}>
                  {formatCurrency(mockCrypto.reduce((sum, asset) => sum + asset.value, 0))}
                </div>
              </div>
              <div>
                <div>Stocks</div>
                <div style={{ color: '#3b82f6', fontWeight: 'bold' }}>
                  {formatCurrency(mockStocks.reduce((sum, asset) => sum + asset.value, 0))}
                </div>
              </div>
              <div>
                <div>NFTs</div>
                <div style={{ color: '#8b5cf6', fontWeight: 'bold' }}>
                  {formatCurrency(mockNFTs.reduce((sum, asset) => sum + asset.value, 0))}
                </div>
              </div>
            </div>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <h3 className="feature-title">📈 Buy Assets</h3>
              <p className="feature-description">
                Purchase crypto, stocks, and other digital assets.
              </p>
              <button className="feature-btn">Buy</button>
            </div>

            <div className="feature-card">
              <h3 className="feature-title">💱 Trade</h3>
              <p className="feature-description">
                Trade between different assets in your portfolio.
              </p>
              <button className="feature-btn">Trade</button>
            </div>

            <div className="feature-card">
              <h3 className="feature-title">🎯 Stake</h3>
              <p className="feature-description">
                Stake your assets to earn rewards and passive income.
              </p>
              <button className="feature-btn">Stake</button>
            </div>

            <div className="feature-card">
              <h3 className="feature-title">📊 Analytics</h3>
              <p className="feature-description">
                View detailed analytics and performance metrics.
              </p>
              <button className="feature-btn">Analyze</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'crypto' && (
        <div className="crypto-section">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ color: '#ffffff' }}>Cryptocurrency</h2>
            <button style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer'
            }}>
              + Buy Crypto
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {mockCrypto.map((asset) => (
              <div key={asset.id} className="feature-card" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{
                    width: '50px',
                    height: '50px',
                    background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.5rem'
                  }}>
                    {asset.icon}
                  </div>
                  <div>
                    <h3 style={{ color: '#ffffff', marginBottom: '0.25rem' }}>
                      {asset.name}
                    </h3>
                    <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                      {asset.amount} {asset.symbol}
                    </p>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: 'bold', 
                    color: '#ffffff',
                    marginBottom: '0.25rem'
                  }}>
                    {formatCurrency(asset.value)}
                  </div>
                  <div style={{ 
                    color: asset.change >= 0 ? '#10b981' : '#ef4444',
                    fontSize: '0.875rem',
                    fontWeight: 'bold'
                  }}>
                    {formatPercentage(asset.change)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'stocks' && (
        <div className="stocks-section">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ color: '#ffffff' }}>Stocks</h2>
            <button style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer'
            }}>
              + Buy Stocks
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {mockStocks.map((asset) => (
              <div key={asset.id} className="feature-card" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{
                    width: '50px',
                    height: '50px',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.5rem'
                  }}>
                    {asset.icon}
                  </div>
                  <div>
                    <h3 style={{ color: '#ffffff', marginBottom: '0.25rem' }}>
                      {asset.name}
                    </h3>
                    <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                      {asset.shares} shares • {asset.symbol}
                    </p>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: 'bold', 
                    color: '#ffffff',
                    marginBottom: '0.25rem'
                  }}>
                    {formatCurrency(asset.value)}
                  </div>
                  <div style={{ 
                    color: asset.change >= 0 ? '#10b981' : '#ef4444',
                    fontSize: '0.875rem',
                    fontWeight: 'bold'
                  }}>
                    {formatPercentage(asset.change)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'nfts' && (
        <div className="nfts-section">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ color: '#ffffff' }}>NFTs</h2>
            <button style={{
              padding: '0.5rem 1rem',
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer'
            }}>
              + Browse NFTs
            </button>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '1rem' 
          }}>
            {mockNFTs.map((nft) => (
              <div key={nft.id} className="feature-card" style={{ textAlign: 'center' }}>
                <div style={{
                  width: '100%',
                  height: '200px',
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '4rem',
                  marginBottom: '1rem'
                }}>
                  {nft.image}
                </div>
                <h3 style={{ color: '#ffffff', marginBottom: '0.5rem' }}>
                  {nft.name}
                </h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                  {nft.collection}
                </p>
                <div style={{ 
                  fontSize: '1.25rem', 
                  fontWeight: 'bold', 
                  color: '#8b5cf6',
                  marginBottom: '1rem'
                }}>
                  {formatCurrency(nft.value)}
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button style={{
                    flex: 1,
                    padding: '0.5rem',
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '6px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.875rem'
                  }}>
                    View
                  </button>
                  <button style={{
                    flex: 1,
                    padding: '0.5rem',
                    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    border: 'none',
                    borderRadius: '6px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.875rem'
                  }}>
                    Sell
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Assets;

