import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Eye, EyeOff, Lock, ArrowLeft } from 'lucide-react';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import './ResetPassword.css';

export const ResetPassword = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      showToast('Missing or invalid password reset token. 🌸', 'error');
      return;
    }
    if (!password || !confirmPassword) {
      showToast('Please fill out all fields. 🌸', 'error');
      return;
    }
    if (password.length < 6) {
      showToast('Password must be at least 6 characters. 🌸', 'error');
      return;
    }
    if (password !== confirmPassword) {
      showToast('Passwords do not match. 🌸', 'error');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/auth/password-reset/confirm/', {
        token,
        password
      });
      setSuccess(true);
      showToast('Password changed successfully! 💕', 'success');
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      console.error(err);
      const valErrors = err.response?.data?.errors?.password;
      const errMsg = valErrors ? valErrors.join(' ') : (err.response?.data?.message || 'Password reset failed.');
      showToast(errMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-password-page-wrapper">
      <div className="reset-password-split-container">
        
        {/* Left Side - Branding */}
        <div className="reset-password-branding-panel">
          <div className="branding-content">
            <h1 className="font-serif">Mahi Store</h1>
            <p>Your one-stop destination for fashion, electronics, home essentials, and more. Curated with love. 💕</p>
            <div className="decor-circle"></div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="reset-password-form-panel">
          <div className="form-box">
            
            <div className="back-to-login-row">
              <Link to="/login" className="back-link">
                <ArrowLeft size={16} /> Back to Login
              </Link>
            </div>

            <div className="form-header">
              <h2 className="font-serif">Reset Password</h2>
              <p>Enter your new password to regain access to your account ✨</p>
            </div>

            {!token ? (
              <div className="error-message-box">
                <div className="error-emoji">⚠️</div>
                <p>Invalid, expired, or missing reset token. Please request a new password reset link.</p>
                <Link to="/forgot-password" className="btn-auth-submit btn-square text-center block">
                  Request New Link 🌸
                </Link>
              </div>
            ) : !success ? (
              <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                  <label htmlFor="password">New Password</label>
                  <div className="input-with-icon">
                    <Lock size={18} className="input-icon" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      placeholder="Enter new password"
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

                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm Password</label>
                  <div className="input-with-icon">
                    <Lock size={18} className="input-icon" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="confirmPassword"
                      placeholder="Confirm new password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="btn-auth-submit btn-square" disabled={loading}>
                  {loading ? 'RESETTING PASSWORD...' : 'RESET PASSWORD ✨'}
                </button>
              </form>
            ) : (
              <div className="success-message-box">
                <div className="success-heart">🎉</div>
                <p>Your password has been reset successfully!</p>
                <p className="note">Redirecting you to the login page in a few seconds... 💕</p>
                <Link to="/login" className="btn-auth-submit btn-square text-center block">
                  Login Now 🌸
                </Link>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
export default ResetPassword;
