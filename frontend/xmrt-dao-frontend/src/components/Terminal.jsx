import React, { useState } from 'react';

const Terminal = () => {
  const [activeMethod, setActiveMethod] = useState('qr');
  const [activeQRTab, setActiveQRTab] = useState('mycode');
  const [paymentData, setPaymentData] = useState({
    amount: '',
    description: ''
  });

  const paymentMethods = [
    { id: 'qr', label: 'QR Code', icon: '📱' },
    { id: 'nfc', label: 'NFC', icon: '📡' },
    { id: 'bluetooth', label: 'Bluetooth', icon: '🔵' },
    { id: 'stripe', label: 'Stripe', icon: '💳' }
  ];

  const handleInputChange = (e) => {
    setPaymentData({
      ...paymentData,
      [e.target.name]: e.target.value
    });
  };

  const generateQRCode = () => {
    // In a real app, this would generate an actual QR code
    return `Payment Request: $${paymentData.amount || '0.00'} - ${paymentData.description || 'No description'}`;
  };

  return (
    <div className="terminal-page fade-in">
      <h1 className="page-title">Terminal</h1>

      <div className="payment-form">
        <h2 style={{ marginBottom: '1rem', color: '#ffffff' }}>Payment Details</h2>
        <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '1.5rem' }}>
          Enter the payment information
        </p>

        <div className="form-group" style={{ marginBottom: '1rem' }}>
          <label className="form-label">Amount ($)</label>
          <input
            type="number"
            name="amount"
            className="form-input"
            placeholder="0.00"
            step="0.01"
            value={paymentData.amount}
            onChange={handleInputChange}
          />
        </div>

        <div className="form-group" style={{ marginBottom: '1.5rem' }}>
          <label className="form-label">Description (Optional)</label>
          <input
            type="text"
            name="description"
            className="form-input"
            placeholder="What's it for?"
            value={paymentData.description}
            onChange={handleInputChange}
          />
        </div>

        <div className="payment-methods">
          {paymentMethods.map((method) => (
            <button
              key={method.id}
              className={`method-btn ${activeMethod === method.id ? 'active' : ''}`}
              onClick={() => setActiveMethod(method.id)}
            >
              {method.icon} {method.label}
            </button>
          ))}
        </div>
      </div>

      {activeMethod === 'qr' && (
        <div className="qr-section">
          <h2 style={{ marginBottom: '1rem', color: '#ffffff' }}>QR Code</h2>
          
          <div className="qr-tabs">
            <button
              className={`qr-tab ${activeQRTab === 'mycode' ? 'active' : ''}`}
              onClick={() => setActiveQRTab('mycode')}
            >
              My Code
            </button>
            <button
              className={`qr-tab ${activeQRTab === 'scan' ? 'active' : ''}`}
              onClick={() => setActiveQRTab('scan')}
            >
              Scan
            </button>
          </div>

          {activeQRTab === 'mycode' ? (
            <div style={{ textAlign: 'center' }}>
              <div className="qr-code">
                <div style={{ 
                  width: '150px', 
                  height: '150px', 
                  background: '#000000',
                  margin: '0 auto',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: '8px',
                  position: 'relative'
                }}>
                  {/* Mock QR Code Pattern */}
                  <div style={{
                    width: '100%',
                    height: '100%',
                    background: `
                      repeating-linear-gradient(
                        0deg,
                        #000 0px,
                        #000 3px,
                        #fff 3px,
                        #fff 6px
                      ),
                      repeating-linear-gradient(
                        90deg,
                        #000 0px,
                        #000 3px,
                        #fff 3px,
                        #fff 6px
                      )
                    `,
                    backgroundBlendMode: 'multiply'
                  }}>
                    {/* Corner squares */}
                    <div style={{
                      position: 'absolute',
                      top: '10px',
                      left: '10px',
                      width: '30px',
                      height: '30px',
                      border: '3px solid #000',
                      background: '#fff'
                    }}>
                      <div style={{
                        width: '12px',
                        height: '12px',
                        background: '#000',
                        margin: '6px'
                      }}></div>
                    </div>
                    <div style={{
                      position: 'absolute',
                      top: '10px',
                      right: '10px',
                      width: '30px',
                      height: '30px',
                      border: '3px solid #000',
                      background: '#fff'
                    }}>
                      <div style={{
                        width: '12px',
                        height: '12px',
                        background: '#000',
                        margin: '6px'
                      }}></div>
                    </div>
                    <div style={{
                      position: 'absolute',
                      bottom: '10px',
                      left: '10px',
                      width: '30px',
                      height: '30px',
                      border: '3px solid #000',
                      background: '#fff'
                    }}>
                      <div style={{
                        width: '12px',
                        height: '12px',
                        background: '#000',
                        margin: '6px'
                      }}></div>
                    </div>
                  </div>
                </div>
              </div>
              <p style={{ 
                marginTop: '1rem', 
                color: 'rgba(255, 255, 255, 0.7)',
                fontSize: '0.875rem'
              }}>
                Share this QR code to receive payment
              </p>
              <div style={{
                marginTop: '1rem',
                padding: '1rem',
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                fontSize: '0.75rem',
                color: 'rgba(255, 255, 255, 0.6)',
                fontFamily: 'monospace'
              }}>
                {generateQRCode()}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{
                width: '200px',
                height: '200px',
                border: '2px dashed rgba(255, 255, 255, 0.3)',
                borderRadius: '12px',
                margin: '0 auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'rgba(255, 255, 255, 0.6)'
              }}>
                📷 Camera View
              </div>
              <p style={{ 
                marginTop: '1rem', 
                color: 'rgba(255, 255, 255, 0.7)',
                fontSize: '0.875rem'
              }}>
                Point your camera at a QR code to scan
              </p>
              <button style={{
                marginTop: '1rem',
                padding: '0.75rem 1.5rem',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                cursor: 'pointer'
              }}>
                Enable Camera
              </button>
            </div>
          )}
        </div>
      )}

      {activeMethod === 'nfc' && (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📡</div>
          <h3 style={{ marginBottom: '1rem', color: '#ffffff' }}>NFC Payment</h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
            Hold your device near an NFC-enabled payment terminal
          </p>
          <div className="pulse" style={{
            width: '100px',
            height: '100px',
            background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
            borderRadius: '50%',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            fontSize: '2rem'
          }}>
            📡
          </div>
        </div>
      )}

      {activeMethod === 'bluetooth' && (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔵</div>
          <h3 style={{ marginBottom: '1rem', color: '#ffffff' }}>Bluetooth Payment</h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
            Connect to nearby Bluetooth-enabled devices
          </p>
          <button style={{
            padding: '0.75rem 1.5rem',
            background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
            border: 'none',
            borderRadius: '8px',
            color: '#ffffff',
            cursor: 'pointer'
          }}>
            Search for Devices
          </button>
        </div>
      )}

      {activeMethod === 'stripe' && (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>💳</div>
          <h3 style={{ marginBottom: '1rem', color: '#ffffff' }}>Stripe Integration</h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
            Process payments through Stripe
          </p>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '12px',
            padding: '1.5rem',
            maxWidth: '300px',
            margin: '0 auto'
          }}>
            <div className="form-group" style={{ marginBottom: '1rem' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Card Number"
              />
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
              <input
                type="text"
                className="form-input"
                placeholder="MM/YY"
                style={{ flex: 1 }}
              />
              <input
                type="text"
                className="form-input"
                placeholder="CVC"
                style={{ flex: 1 }}
              />
            </div>
            <button style={{
              width: '100%',
              padding: '0.75rem',
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: 'pointer'
            }}>
              Process Payment
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Terminal;

