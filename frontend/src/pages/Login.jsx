import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Eye, EyeOff, Lock, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import './Login.css';

export const Login = () => {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  // Intent path redirect helper
  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      showToast('Please fill out all fields. 🌸', 'error');
      return;
    }

    setLoading(true);
    try {
      const user = await login(username, password);
      showToast(`Welcome back, ${user.username}! 💕`, 'success');
      
      // Redirect based on role and intent
      if (user.role === 'Seller') {
        navigate('/seller/dashboard');
      } else {
        navigate(from, { replace: true });
      }
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.message || err.response?.data?.errors?.detail || 'Invalid username or password.';
      showToast(errMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page-wrapper">
      <div className="login-split-container">
        
        {/* Left Side - Gradient & Lifestyle Branding */}
        <div className="login-branding-panel">
          <div className="branding-content">
            <h1 className="font-serif">Mahi Store</h1>
            <p>Your one-stop destination for fashion, electronics, home essentials, and more. Curated with love. 💕</p>
            <div className="decor-circle"></div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="login-form-panel">
          <div className="form-box">
            <div className="form-header">
              <h2 className="font-serif">Welcome Back</h2>
              <p>Login to your account to continue shopping ✨</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <div className="input-with-icon">
                  <UserIcon size={18} className="input-icon" />
                  <input
                    type="text"
                    id="username"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="input-with-icon">
                  <Lock size={18} className="input-icon" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div className="form-actions-row">
                <label className="remember-me-checkbox">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Remember me</span>
                </label>
                <Link to="/forgot-password" className="forgot-password-link">
                  Forgot Password?
                </Link>
              </div>

              <button type="submit" className="btn-auth-submit btn-square" disabled={loading}>
                {loading ? 'LOGGING IN...' : 'LOGIN ✨'}
              </button>
            </form>

            <div className="form-footer">
              <p>
                Don't have an account?{' '}
                <Link to="/register" className="auth-redirect-link">
                  Create account 🌸
                </Link>
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
