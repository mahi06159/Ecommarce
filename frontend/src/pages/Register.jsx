import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShoppingBag, Store, Mail, Lock, User as UserIcon, FileText } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import './Register.css';

export const Register = () => {
  const { registerBuyer, registerSeller } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [role, setRole] = useState(null); // 'Buyer' or 'Seller'
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Seller exclusive fields
  const [storeName, setStoreName] = useState('');
  const [storeDescription, setStoreDescription] = useState('');
  
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!role) {
      showToast('Please select a role first! 🌸', 'error');
      return;
    }
    if (!username || !email || !password || !confirmPassword) {
      showToast('All fields are required. 🌸', 'error');
      return;
    }
    if (password !== confirmPassword) {
      showToast('Passwords do not match.', 'error');
      return;
    }
    if (password.length < 6) {
      showToast('Password must be at least 6 characters long.', 'error');
      return;
    }

    setLoading(true);
    try {
      if (role === 'Buyer') {
        await registerBuyer(username, email, password);
        showToast('Buyer account created successfully! 💕 Welcome!', 'success');
        navigate('/');
      } else {
        await registerSeller(username, email, password, storeName, storeDescription);
        showToast('Seller account registered successfully! 🌸 Welcome to Mahi Store!', 'success');
        navigate('/seller/dashboard');
      }
    } catch (err) {
      console.error(err);
      const errors = err.response?.data?.errors;
      const errMsg = err.response?.data?.message || (errors ? Object.entries(errors).map(([key, val]) => `${key}: ${val}`).join(', ') : 'Registration failed.');
      showToast(errMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page-wrapper">
      <div className="register-container">
        <div className="register-box">
          <div className="register-header">
            <h1 className="font-serif">Create Account</h1>
            <p>Join Mahi Store family today 🌸</p>
          </div>

          {/* Step 1: Role Selector */}
          {!role ? (
            <div className="role-selection-section">
              <h3 className="selection-title">Choose your account type:</h3>
              <div className="role-cards-container">
                <div 
                  className="role-card" 
                  onClick={() => setRole('Buyer')}
                >
                  <div className="role-card-icon-wrapper">
                    <ShoppingBag size={32} />
                  </div>
                  <h4>Shop as a Buyer</h4>
                  <p>Discover products, write reviews, and order with easy returns. ✨</p>
                  <button className="btn-role-select btn-square">SELECT BUYER 💕</button>
                </div>
                <div 
                  className="role-card seller" 
                  onClick={() => setRole('Seller')}
                >
                  <div className="role-card-icon-wrapper">
                    <Store size={32} />
                  </div>
                  <h4>Sell on Mahi Store</h4>
                  <p>Open your shop, upload inventory, track orders and analytics. 🌸</p>
                  <button className="btn-role-select btn-square">SELECT SELLER 🛍️</button>
                </div>
              </div>
            </div>
          ) : (
            /* Step 2: Form */
            <div className="register-form-section">
              <button 
                type="button" 
                onClick={() => setRole(null)} 
                className="btn-back-role"
              >
                ← Back to account choice
              </button>

              <div className="selected-role-badge">
                Registering as: <strong>{role}</strong>
              </div>

              <form onSubmit={handleRegister} className="auth-form">
                <div className="form-group">
                  <label htmlFor="reg-username">Username</label>
                  <div className="input-with-icon">
                    <UserIcon size={18} className="input-icon" />
                    <input
                      type="text"
                      id="reg-username"
                      placeholder="Choose a username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="reg-email">Email Address</label>
                  <div className="input-with-icon">
                    <Mail size={18} className="input-icon" />
                    <input
                      type="email"
                      id="reg-email"
                      placeholder="your.email@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {role === 'Seller' && (
                  <>
                    <div className="form-group">
                      <label htmlFor="store-name">Store Name</label>
                      <div className="input-with-icon">
                        <Store size={18} className="input-icon" />
                        <input
                          type="text"
                          id="store-name"
                          placeholder="Your lovely store name"
                          value={storeName}
                          onChange={(e) => setStoreName(e.target.value)}
                          required
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label htmlFor="store-description">Store Description</label>
                      <div className="input-with-icon">
                        <FileText size={18} className="input-icon" />
                        <textarea
                          id="store-description"
                          placeholder="What makes your shop special?"
                          value={storeDescription}
                          onChange={(e) => setStoreDescription(e.target.value)}
                          rows={3}
                          style={{ width: '100%', paddingLeft: '42px', border: '1px solid var(--mahi-pink-mid)', borderRadius: '4px' }}
                        />
                      </div>
                    </div>
                  </>
                )}

                <div className="form-group">
                  <label htmlFor="reg-password">Password</label>
                  <div className="input-with-icon">
                    <Lock size={18} className="input-icon" />
                    <input
                      type="password"
                      id="reg-password"
                      placeholder="At least 6 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="reg-confirm-password">Confirm Password</label>
                  <div className="input-with-icon">
                    <Lock size={18} className="input-icon" />
                    <input
                      type="password"
                      id="reg-confirm-password"
                      placeholder="Re-enter password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="btn-auth-submit btn-square" disabled={loading}>
                  {loading ? 'CREATING ACCOUNT...' : `REGISTER AS ${role.toUpperCase()} 💕`}
                </button>
              </form>
            </div>
          )}

          <div className="form-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="auth-redirect-link">
                Login here 🌸
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
