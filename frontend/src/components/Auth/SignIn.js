import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

const SignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [googleAvailable, setGoogleAvailable] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if Google OAuth is available
    const checkGoogleAuth = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/auth/google/url', {
          method: 'GET',
          credentials: 'include'
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          if (errorData.development_mode) {
            setGoogleAvailable(false);
          }
        }
      } catch (err) {
        setGoogleAvailable(false);
      }
    };
    
    checkGoogleAuth();
  }, []);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Initialize Google OAuth
      const response = await fetch('http://localhost:5000/api/auth/google/url', {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        window.location.href = data.authUrl;
      } else {
        const errorData = await response.json();
        if (errorData.development_mode) {
          setError('Google sign-in is not configured for development. Please use email/password login for testing.');
        } else {
          throw new Error(errorData.message || 'Failed to get Google OAuth URL');
        }
      }
    } catch (err) {
      setError(err.message || 'Google sign-in failed. Please try again.');
      console.error('Google sign-in error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSignIn = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:5000/api/auth/signin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Sign in failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-back-button">
          <button 
            onClick={() => navigate('/')}
            className="back-btn"
            title="Back to Home"
          >
            ← Back to Home
          </button>
        </div>
        
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Sign in to access your market analysis dashboard</p>
        </div>
        
        {error && (
          <div className="auth-error">
            <span>⚠️</span>
            <p>{error}</p>
          </div>
        )}
        
        <form onSubmit={handleEmailSignIn} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "👁️" : "👁️‍🗨️"}
              </button>
            </div>
          </div>
          
          <button 
            type="submit" 
            className="auth-btn primary"
            disabled={loading}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
        
        <div className="auth-divider">
          <span>or</span>
        </div>
        
        <button 
          onClick={handleGoogleSignIn}
          className={`auth-btn ${googleAvailable ? 'google' : 'google-disabled'}`}
          disabled={loading || !googleAvailable}
        >
          <svg viewBox="0 0 24 24" className="google-icon">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          {googleAvailable ? 'Continue with Google' : 'Google Sign-in (Not Available)'}
        </button>
        
        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <button 
              onClick={() => navigate('/signup')}
              className="auth-link"
            >
              Sign up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignIn; 