import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, ArrowLeft } from 'lucide-react';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import './ForgotPassword.css';

export const ForgotPassword = () => {
  const { showToast } = useToast();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      showToast('Please enter your email address. 🌸', 'error');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/auth/password-reset/request/', { email });
      setSubmitted(true);
      showToast('Reset email sent if the account exists. 💕', 'success');
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.message || 'Failed to request password reset.';
      showToast(errMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-page-wrapper">
      <div className="forgot-password-split-container">
        
        {/* Left Side - Gradient & Lifestyle Branding */}
        <div className="forgot-password-branding-panel">
          <div className="branding-content">
            <h1 className="font-serif">Mahi Store</h1>
            <p>Your one-stop destination for fashion, electronics, home essentials, and more. Curated with love. 💕</p>
            <div className="decor-circle"></div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="forgot-password-form-panel">
          <div className="form-box">
            
            <div className="back-to-login-row">
              <Link to="/login" className="back-link">
                <ArrowLeft size={16} /> Back to Login
              </Link>
            </div>

            <div className="form-header">
              <h2 className="font-serif">Forgot Password?</h2>
              <p>Enter your email and we'll send you a link to reset your password ✨</p>
            </div>

            {!submitted ? (
              <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                  <label htmlFor="email">Email Address</label>
                  <div className="input-with-icon">
                    <Mail size={18} className="input-icon" />
                    <input
                      type="email"
                      id="email"
                      placeholder="Enter your registered email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="btn-auth-submit btn-square" disabled={loading}>
                  {loading ? 'SENDING LINK...' : 'SEND RESET LINK ✨'}
                </button>
              </form>
            ) : (
              <div className="success-message-box">
                <div className="success-heart">💕</div>
                <p>If an account exists with that email address, we've sent instructions to reset your password.</p>
                <p className="note">Please check your inbox (and spam folder) for the link.</p>
                <button onClick={() => setSubmitted(false)} className="btn-secondary btn-square">
                  Try another email 🌸
                </button>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
export default ForgotPassword;
