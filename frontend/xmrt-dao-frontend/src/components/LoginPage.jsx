import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { login, register } = useAuth();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let result;
      if (activeTab === 'login') {
        result = await login(formData.email, formData.password);
      } else {
        result = await register(formData.email, formData.password, formData.name);
      }

      if (result.success) {
        setSuccess('Welcome to XMRTNET!');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoAccount = (accountNumber) => {
    if (accountNumber === 1) {
      setFormData({
        email: 'user1@example.com',
        password: 'password1',
        name: 'John Doe'
      });
    } else {
      setFormData({
        email: 'user2@example.com',
        password: 'password2',
        name: 'Jane Smith'
      });
    }
  };

  return (
    <div className="login-page">
      <div className="login-container fade-in">
        <h1 className="login-title">XMRTNET</h1>
        <p className="login-subtitle">Sign in to your account</p>

        <div className="login-tabs">
          <button
            className={`login-tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => setActiveTab('login')}
          >
            Login
          </button>
          <button
            className={`login-tab ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => setActiveTab('register')}
          >
            Register
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form className="login-form" onSubmit={handleSubmit}>
          {activeTab === 'register' && (
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="name"
                className="form-input"
                placeholder="Enter your full name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              name="email"
              className="form-input"
              placeholder="your@email.com"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              className="form-input"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleInputChange}
              required
            />
          </div>

          <button
            type="submit"
            className="login-btn"
            disabled={loading}
          >
            {loading ? 'Please wait...' : (activeTab === 'login' ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="login-footer">
          {activeTab === 'login' ? (
            <p>
              Don't have an account?{' '}
              <button
                className="register-link"
                onClick={() => setActiveTab('register')}
                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
              >
                Register
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button
                className="register-link"
                onClick={() => setActiveTab('login')}
                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
              >
                Login
              </button>
            </p>
          )}
        </div>

        <div className="demo-accounts">
          <p><strong>Demo accounts:</strong></p>
          <p>
            <button
              onClick={() => fillDemoAccount(1)}
              style={{ background: 'none', border: 'none', color: '#10b981', cursor: 'pointer', textDecoration: 'underline' }}
            >
              user1@example.com / password1
            </button>
          </p>
          <p>
            <button
              onClick={() => fillDemoAccount(2)}
              style={{ background: 'none', border: 'none', color: '#10b981', cursor: 'pointer', textDecoration: 'underline' }}
            >
              user2@example.com / password2
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

