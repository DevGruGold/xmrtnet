import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useWallet } from '../context/WalletContext';

const Settings = () => {
  const { user, logout } = useAuth();
  const { isConnected, disconnectWallet } = useWallet();
  const [activeSection, setActiveSection] = useState('profile');

  const settingSections = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'preferences', label: 'Preferences', icon: '⚙️' }
  ];

  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '',
    address: ''
  });

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: false,
    biometricAuth: true,
    loginNotifications: true
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    smsNotifications: false,
    transactionAlerts: true,
    marketingEmails: false
  });

  const [preferences, setPreferences] = useState({
    language: 'English',
    currency: 'USD',
    theme: 'Dark',
    timezone: 'UTC-5'
  });

  const handleProfileChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
  };

  const handleSecurityToggle = (setting) => {
    setSecuritySettings({
      ...securitySettings,
      [setting]: !securitySettings[setting]
    });
  };

  const handleNotificationToggle = (setting) => {
    setNotificationSettings({
      ...notificationSettings,
      [setting]: !notificationSettings[setting]
    });
  };

  const handlePreferenceChange = (e) => {
    setPreferences({
      ...preferences,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="settings-page fade-in">
      <h1 className="page-title">Settings</h1>

      <div className="settings-tabs" style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '2rem',
        overflowX: 'auto'
      }}>
        {settingSections.map((section) => (
          <button
            key={section.id}
            className={`filter-btn ${activeSection === section.id ? 'active' : ''}`}
            onClick={() => setActiveSection(section.id)}
          >
            {section.icon} {section.label}
          </button>
        ))}
      </div>

      {activeSection === 'profile' && (
        <div className="profile-section">
          <div className="feature-card" style={{ marginBottom: '1.5rem' }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#ffffff' }}>Profile Information</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  name="name"
                  className="form-input"
                  value={profileData.name}
                  onChange={handleProfileChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  value={profileData.email}
                  onChange={handleProfileChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <input
                  type="tel"
                  name="phone"
                  className="form-input"
                  placeholder="+1 (555) 123-4567"
                  value={profileData.phone}
                  onChange={handleProfileChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Address</label>
                <input
                  type="text"
                  name="address"
                  className="form-input"
                  placeholder="123 Main St, City, State 12345"
                  value={profileData.address}
                  onChange={handleProfileChange}
                />
              </div>

              <button className="feature-btn" style={{ marginTop: '1rem' }}>
                Save Changes
              </button>
            </div>
          </div>

          <div className="feature-card">
            <h3 style={{ marginBottom: '1rem', color: '#ffffff' }}>Account Actions</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button style={{
                padding: '0.75rem',
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                cursor: 'pointer'
              }}>
                Change Password
              </button>
              
              <button style={{
                padding: '0.75rem',
                background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                cursor: 'pointer'
              }}>
                Download Account Data
              </button>
              
              {isConnected && (
                <button 
                  onClick={disconnectWallet}
                  style={{
                    padding: '0.75rem',
                    background: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#ffffff',
                    cursor: 'pointer'
                  }}
                >
                  Disconnect Wallet
                </button>
              )}
              
              <button 
                onClick={logout}
                style={{
                  padding: '0.75rem',
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#ffffff',
                  cursor: 'pointer'
                }}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {activeSection === 'security' && (
        <div className="security-section">
          <div className="feature-card">
            <h2 style={{ marginBottom: '1.5rem', color: '#ffffff' }}>Security Settings</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '1rem 0',
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <div>
                  <h3 style={{ color: '#ffffff', marginBottom: '0.25rem' }}>Two-Factor Authentication</h3>
                  <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                    Add an extra layer of security to your account
                  </p>
                </div>
                <button
                  onClick={() => handleSecurityToggle('twoFactorAuth')}
                  style={{
                    width: '50px',
                    height: '25px',
                    borderRadius: '25px',
                    border: 'none',
                    background: securitySettings.twoFactorAuth 
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                      : 'rgba(255, 255, 255, 0.2)',
                    cursor: 'pointer',
                    position: 'relative',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div style={{
                    width: '21px',
                    height: '21px',
                    borderRadius: '50%',
                    background: '#ffffff',
                    position: 'absolute',
                    top: '2px',
                    left: securitySettings.twoFactorAuth ? '27px' : '2px',
                    transition: 'all 0.3s ease'
                  }}></div>
                </button>
              </div>

              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '1rem 0',
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <div>
                  <h3 style={{ color: '#ffffff', marginBottom: '0.25rem' }}>Biometric Authentication</h3>
                  <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                    Use fingerprint or face recognition to login
                  </p>
                </div>
                <button
                  onClick={() => handleSecurityToggle('biometricAuth')}
                  style={{
                    width: '50px',
                    height: '25px',
                    borderRadius: '25px',
                    border: 'none',
                    background: securitySettings.biometricAuth 
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                      : 'rgba(255, 255, 255, 0.2)',
                    cursor: 'pointer',
                    position: 'relative',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div style={{
                    width: '21px',
                    height: '21px',
                    borderRadius: '50%',
                    background: '#ffffff',
                    position: 'absolute',
                    top: '2px',
                    left: securitySettings.biometricAuth ? '27px' : '2px',
                    transition: 'all 0.3s ease'
                  }}></div>
                </button>
              </div>

              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '1rem 0'
              }}>
                <div>
                  <h3 style={{ color: '#ffffff', marginBottom: '0.25rem' }}>Login Notifications</h3>
                  <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                    Get notified when someone logs into your account
                  </p>
                </div>
                <button
                  onClick={() => handleSecurityToggle('loginNotifications')}
                  style={{
                    width: '50px',
                    height: '25px',
                    borderRadius: '25px',
                    border: 'none',
                    background: securitySettings.loginNotifications 
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                      : 'rgba(255, 255, 255, 0.2)',
                    cursor: 'pointer',
                    position: 'relative',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div style={{
                    width: '21px',
                    height: '21px',
                    borderRadius: '50%',
                    background: '#ffffff',
                    position: 'absolute',
                    top: '2px',
                    left: securitySettings.loginNotifications ? '27px' : '2px',
                    transition: 'all 0.3s ease'
                  }}></div>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeSection === 'notifications' && (
        <div className="notifications-section">
          <div className="feature-card">
            <h2 style={{ marginBottom: '1.5rem', color: '#ffffff' }}>Notification Preferences</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {Object.entries(notificationSettings).map(([key, value]) => (
                <div key={key} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '1rem 0',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <div>
                    <h3 style={{ color: '#ffffff', marginBottom: '0.25rem' }}>
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </h3>
                    <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                      {getNotificationDescription(key)}
                    </p>
                  </div>
                  <button
                    onClick={() => handleNotificationToggle(key)}
                    style={{
                      width: '50px',
                      height: '25px',
                      borderRadius: '25px',
                      border: 'none',
                      background: value 
                        ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                        : 'rgba(255, 255, 255, 0.2)',
                      cursor: 'pointer',
                      position: 'relative',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <div style={{
                      width: '21px',
                      height: '21px',
                      borderRadius: '50%',
                      background: '#ffffff',
                      position: 'absolute',
                      top: '2px',
                      left: value ? '27px' : '2px',
                      transition: 'all 0.3s ease'
                    }}></div>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeSection === 'preferences' && (
        <div className="preferences-section">
          <div className="feature-card">
            <h2 style={{ marginBottom: '1.5rem', color: '#ffffff' }}>App Preferences</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="form-group">
                <label className="form-label">Language</label>
                <select
                  name="language"
                  className="form-input"
                  value={preferences.language}
                  onChange={handlePreferenceChange}
                >
                  <option value="English">English</option>
                  <option value="Spanish">Español</option>
                  <option value="French">Français</option>
                  <option value="German">Deutsch</option>
                  <option value="Chinese">中文</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Currency</label>
                <select
                  name="currency"
                  className="form-input"
                  value={preferences.currency}
                  onChange={handlePreferenceChange}
                >
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="JPY">JPY - Japanese Yen</option>
                  <option value="BTC">BTC - Bitcoin</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Theme</label>
                <select
                  name="theme"
                  className="form-input"
                  value={preferences.theme}
                  onChange={handlePreferenceChange}
                >
                  <option value="Dark">Dark</option>
                  <option value="Light">Light</option>
                  <option value="Auto">Auto</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Timezone</label>
                <select
                  name="timezone"
                  className="form-input"
                  value={preferences.timezone}
                  onChange={handlePreferenceChange}
                >
                  <option value="UTC-8">UTC-8 (Pacific)</option>
                  <option value="UTC-7">UTC-7 (Mountain)</option>
                  <option value="UTC-6">UTC-6 (Central)</option>
                  <option value="UTC-5">UTC-5 (Eastern)</option>
                  <option value="UTC+0">UTC+0 (GMT)</option>
                  <option value="UTC+1">UTC+1 (CET)</option>
                </select>
              </div>

              <button className="feature-btn" style={{ marginTop: '1rem' }}>
                Save Preferences
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const getNotificationDescription = (key) => {
  const descriptions = {
    emailNotifications: 'Receive notifications via email',
    pushNotifications: 'Receive push notifications on your device',
    smsNotifications: 'Receive notifications via SMS',
    transactionAlerts: 'Get alerts for all transactions',
    marketingEmails: 'Receive promotional emails and updates'
  };
  return descriptions[key] || '';
};

export default Settings;

