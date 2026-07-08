import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { User, MapPin, ShoppingBag, Star, Upload, Plus, Trash2, Home } from 'lucide-react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Navbar } from '../components/layout/Navbar';
import './Profile.css';

export const Profile = () => {
  const { user, updateProfile, refreshProfile } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const currentTab = searchParams.get('tab') || 'info';

  const [loadingData, setLoadingData] = useState(false);
  const [orders, setOrders] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [reviews, setReviews] = useState([]);

  // Edit profile states
  const [email, setEmail] = useState(user?.email || '');
  const [phoneNumber, setPhoneNumber] = useState(user?.profile?.phone_number || '');
  const [storeName, setStoreName] = useState(user?.profile?.store_name || '');
  const [storeDescription, setStoreDescription] = useState(user?.profile?.store_description || '');
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [updating, setUpdating] = useState(false);

  // Address create form states
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [addressLine1, setAddressLine1] = useState('');
  const [addressLine2, setAddressLine2] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [country, setCountry] = useState('');
  const [isDefault, setIsDefault] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user]);

  // Load specific tab data
  useEffect(() => {
    if (!user) return;

    const loadTabData = async () => {
      setLoadingData(true);
      try {
        if (currentTab === 'orders') {
          const data = await api.get('/api/orders/');
          setOrders(data || []);
        } else if (currentTab === 'addresses') {
          const data = await api.get('/api/addresses/');
          const addrList = Array.isArray(data) ? data : (data?.data && Array.isArray(data.data) ? data.data : []);
          setAddresses(addrList);
        } else if (currentTab === 'reviews') {
          // Fetch reviews written by the buyer
          const data = await api.get(`/api/reviews/?buyer=${user.id}`);
          setReviews(data || []);
        }
      } catch (err) {
        console.error('Failed to load profile tab data:', err);
      } finally {
        setLoadingData(false);
      }
    };

    loadTabData();
  }, [currentTab, user]);

  const handleTabChange = (tabName) => {
    setSearchParams({ tab: tabName });
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setUpdating(true);
    try {
      const payload = {
        email,
        profile: {}
      };

      if (user.role === 'Buyer') {
        payload.profile.phone_number = phoneNumber;
        if (avatarFile) payload.profile.avatar = avatarFile;
      } else {
        payload.profile.store_name = storeName;
        payload.profile.store_description = storeDescription;
        if (avatarFile) payload.profile.store_logo = avatarFile;
      }

      await updateProfile(payload);
      showToast('Profile updated successfully! 💕', 'success');
      setAvatarFile(null);
    } catch (err) {
      console.error(err);
      showToast('Failed to update profile.', 'error');
    } finally {
      setUpdating(false);
    }
  };

  const handleAddAddress = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        address_line1: addressLine1,
        address_line2: addressLine2,
        city,
        state,
        postal_code: postalCode,
        country,
        is_default: isDefault
      };
      await api.post('/api/addresses/', payload);
      showToast('Address added! 💕', 'success');
      
      // Reset form
      setAddressLine1('');
      setAddressLine2('');
      setCity('');
      setState('');
      setPostalCode('');
      setCountry('');
      setIsDefault(false);
      setShowAddressForm(false);

      // Reload list
      const data = await api.get('/api/addresses/');
      const addrList = Array.isArray(data) ? data : (data?.data && Array.isArray(data.data) ? data.data : []);
      setAddresses(addrList);
    } catch (err) {
      showToast('Failed to save address.', 'error');
    }
  };

  const handleDeleteAddress = async (addrId) => {
    if (window.confirm('Delete this address? 🌸')) {
      try {
        await api.delete(`/api/addresses/${addrId}/`);
        showToast('Address deleted.', 'success');
        setAddresses(addresses.filter(a => a.id !== addrId));
      } catch (err) {
        showToast('Failed to delete address.', 'error');
      }
    }
  };

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };

  const getImgSrc = (img) => {
    if (!img) return null;
    if (img.startsWith('http')) return img;
    return `http://localhost:8000${img.startsWith('/') ? '' : '/'}${img}`;
  };

  return (
    <div className="profile-page-wrapper">
      <Navbar />

      <div className="profile-layout container">
        
        {/* Left column: profile card and tabs sidebar */}
        <aside className="profile-sidebar-card">
          <div className="profile-user-badge">
            <div className="profile-avatar-large">
              {avatarPreview ? (
                <img src={avatarPreview} alt="Avatar Preview" className="avatar-img" />
              ) : user?.role === 'Buyer' && user?.profile?.avatar ? (
                <img src={getImgSrc(user.profile.avatar)} alt="User avatar" className="avatar-img" />
              ) : user?.role === 'Seller' && user?.profile?.store_logo ? (
                <img src={getImgSrc(user.profile.store_logo)} alt="Store logo" className="avatar-img" />
              ) : (
                <div className="avatar-initials-gradient">
                  {user?.username ? user.username.slice(0, 2).toUpperCase() : 'US'}
                </div>
              )}
            </div>
            
            <h3 className="profile-username font-serif">{user?.username}</h3>
            <span className="profile-role-tag">{user?.role} Account</span>
          </div>

          <nav className="profile-navigation-tabs">
            <button 
              className={`profile-tab-btn ${currentTab === 'info' ? 'active' : ''}`}
              onClick={() => handleTabChange('info')}
            >
              <User size={16} /> Personal Info
            </button>

            {user?.role === 'Buyer' ? (
              <>
                <button 
                  className={`profile-tab-btn ${currentTab === 'orders' ? 'active' : ''}`}
                  onClick={() => handleTabChange('orders')}
                >
                  <ShoppingBag size={16} /> My Orders
                </button>
                <button 
                  className={`profile-tab-btn ${currentTab === 'addresses' ? 'active' : ''}`}
                  onClick={() => handleTabChange('addresses')}
                >
                  <MapPin size={16} /> My Addresses
                </button>
                <button 
                  className={`profile-tab-btn ${currentTab === 'reviews' ? 'active' : ''}`}
                  onClick={() => handleTabChange('reviews')}
                >
                  <Star size={16} /> My Reviews
                </button>
              </>
            ) : (
              <div className="seller-shortcuts-box">
                <span className="shortcuts-title">Seller Hub Shortcuts</span>
                <button className="shortcut-btn btn-square" onClick={() => navigate('/seller/dashboard')}>
                  GO TO DASHBOARD 📊
                </button>
                <button className="shortcut-btn btn-square" onClick={() => navigate('/seller/products')}>
                  MANAGE INVENTORY 🛍️
                </button>
                <button className="shortcut-btn btn-square" onClick={() => navigate('/seller/orders')}>
                  RECEIVED ORDERS 📦
                </button>
              </div>
            )}
          </nav>
        </aside>

        {/* Right column: active tab contents */}
        <main className="profile-content-area">
          
          {currentTab === 'info' && (
            <div className="profile-tab-content-box">
              <h2 className="tab-title font-serif">Edit Personal Info</h2>
              
              <form onSubmit={handleProfileUpdate} className="profile-edit-form">
                
                <div className="form-group-avatar-upload">
                  <label>Avatar / Logo File</label>
                  <div className="avatar-upload-row">
                    <label className="avatar-upload-trigger btn-square">
                      <Upload size={16} /> Choose File
                      <input 
                        type="file" 
                        accept="image/*" 
                        onChange={handleAvatarChange} 
                        style={{ display: 'none' }}
                      />
                    </label>
                    {avatarFile && <span className="selected-filename">{avatarFile.name}</span>}
                  </div>
                </div>

                <div className="form-group">
                  <label>Username (read-only)</label>
                  <input type="text" value={user?.username || ''} disabled />
                </div>

                <div className="form-group">
                  <label>Email Address</label>
                  <input 
                    type="email" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                {user?.role === 'Buyer' ? (
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input 
                      type="text" 
                      placeholder="e.g. +91 9999999999"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                    />
                  </div>
                ) : (
                  <>
                    <div className="form-group">
                      <label>Store Name</label>
                      <input 
                        type="text" 
                        value={storeName}
                        onChange={(e) => setStoreName(e.target.value)}
                        required
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Store Description</label>
                      <textarea 
                        value={storeDescription}
                        onChange={(e) => setStoreDescription(e.target.value)}
                        rows={4}
                      />
                    </div>
                  </>
                )}

                <button type="submit" className="btn-profile-save btn-square" disabled={updating}>
                  {updating ? 'SAVING CHANGES...' : 'SAVE CHANGES 💕'}
                </button>

              </form>
            </div>
          )}

          {currentTab === 'orders' && (
            <div className="profile-tab-content-box">
              <h2 className="tab-title font-serif">Order History</h2>
              
              {loadingData ? (
                <div className="spinner-container"><div className="spinner"></div></div>
              ) : orders.length === 0 ? (
                <div className="empty-tab-state">
                  <span className="empty-emoji">🛍️</span>
                  <p>You haven't placed any orders yet.</p>
                  <button className="btn-shop btn-square" onClick={() => navigate('/products')}>
                    Browse Shop Now 🌸
                  </button>
                </div>
              ) : (
                <div className="orders-history-list">
                  {orders.map((ord) => {
                    const statusClass = ord.status.toLowerCase();
                    return (
                      <div key={ord.id} className="order-history-card">
                        <div className="order-card-header">
                          <div>
                            <span className="order-id font-mono">ID: #{ord.id}</span>
                            <span className="order-date">{new Date(ord.created_at).toLocaleDateString()}</span>
                          </div>
                          <span className={`status-badge-indicator ${statusClass}`}>{ord.status}</span>
                        </div>
                        
                        <div className="order-card-body">
                          <div className="order-items-summaries">
                            {ord.items?.map((item) => (
                              <div key={item.id} className="order-item-row-detail">
                                <span className="item-name">{item.product_name_display} (x{item.quantity})</span>
                                <span className="item-price font-mono">{formatPrice(item.price)}</span>
                              </div>
                            ))}
                          </div>
                          
                          <hr className="order-card-divider" />
                          
                          <div className="order-card-footer">
                            <span className="shipping-text">Shipping: {ord.shipping_address_text}</span>
                            <span className="total font-mono">Total: {formatPrice(ord.total_price)}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {currentTab === 'addresses' && (
            <div className="profile-tab-content-box">
              <h2 className="tab-title font-serif">Shipping Addresses</h2>
              
              {loadingData ? (
                <div className="spinner-container"><div className="spinner"></div></div>
              ) : (
                <div className="profile-addresses-wrapper">
                  
                  {/* Address List */}
                  <div className="profile-saved-addresses">
                    {addresses.length === 0 ? (
                      <p className="no-address">No addresses saved yet.</p>
                    ) : (
                      <div className="addresses-cards-grid">
                        {addresses.map((addr) => (
                          <div key={addr.id} className="address-display-card">
                            <span className="lines">
                              <strong>{addr.address_line1}</strong>
                              {addr.address_line2 && `, ${addr.address_line2}`}
                            </span>
                            <span className="city-state">
                              {addr.city}, {addr.state} - {addr.postal_code}
                            </span>
                            <span className="country">{addr.country}</span>
                            
                            <div className="address-card-actions">
                              {addr.is_default && <span className="badge-default">DEFAULT</span>}
                              <button className="delete-btn" onClick={() => handleDeleteAddress(addr.id)}>
                                <Trash2 size={16} /> Delete
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Inline Address Creation Form */}
                  {!showAddressForm ? (
                    <button className="btn-add-address-profile-btn btn-square" onClick={() => setShowAddressForm(true)}>
                      <Plus size={16} /> ADD NEW ADDRESS
                    </button>
                  ) : (
                    <div className="address-form-box">
                      <h3 className="font-serif">Add New Address</h3>
                      <form onSubmit={handleAddAddress} className="address-form">
                        <div className="form-group">
                          <label>Address Line 1 *</label>
                          <input 
                            type="text" 
                            value={addressLine1}
                            onChange={(e) => setAddressLine1(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label>Address Line 2</label>
                          <input 
                            type="text" 
                            value={addressLine2}
                            onChange={(e) => setAddressLine2(e.target.value)}
                          />
                        </div>
                        
                        <div className="form-grid-3">
                          <div className="form-group">
                            <label>City *</label>
                            <input type="text" value={city} onChange={(e) => setCity(e.target.value)} required />
                          </div>
                          <div className="form-group">
                            <label>State *</label>
                            <input type="text" value={state} onChange={(e) => setState(e.target.value)} required />
                          </div>
                          <div className="form-group">
                            <label>Postal Code *</label>
                            <input type="text" value={postalCode} onChange={(e) => setPostalCode(e.target.value)} required />
                          </div>
                        </div>

                        <div className="form-group">
                          <label>Country *</label>
                          <input type="text" value={country} onChange={(e) => setCountry(e.target.value)} required />
                        </div>

                        <label className="checkbox-default-row">
                          <input 
                            type="checkbox" 
                            checked={isDefault}
                            onChange={(e) => setIsDefault(e.target.checked)}
                          />
                          <span>Set as default address</span>
                        </label>

                        <div className="form-buttons-row">
                          <button type="submit" className="btn-add-address btn-square">SAVE ADDRESS</button>
                          <button type="button" className="btn-cancel-address btn-square" onClick={() => setShowAddressForm(false)}>
                            CANCEL
                          </button>
                        </div>
                      </form>
                    </div>
                  )}

                </div>
              )}
            </div>
          )}

          {currentTab === 'reviews' && (
            <div className="profile-tab-content-box">
              <h2 className="tab-title font-serif">My Reviews</h2>
              
              {loadingData ? (
                <div className="spinner-container"><div className="spinner"></div></div>
              ) : reviews.length === 0 ? (
                <div className="empty-tab-state">
                  <span className="empty-emoji">🌸</span>
                  <p>You haven't left any reviews yet.</p>
                </div>
              ) : (
                <div className="profile-reviews-list">
                  {reviews.map((rev) => (
                    <div key={rev.id} className="profile-review-card">
                      <div className="review-header">
                        <div>
                          <h4>Product: <strong>{rev.product_name}</strong></h4>
                          <span className="date">{new Date(rev.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="stars">
                          {[...Array(5)].map((_, idx) => (
                            <Star 
                              key={idx} 
                              size={12} 
                              fill={idx < rev.rating ? 'var(--mahi-gold)' : 'none'} 
                              stroke={idx < rev.rating ? 'var(--mahi-gold)' : '#CCCCCC'} 
                            />
                          ))}
                        </div>
                      </div>
                      <p className="comment">"{rev.comment}"</p>
                      <button className="view-product-btn" onClick={() => navigate(`/products/${rev.product}`)}>
                        View Product →
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </main>

      </div>
    </div>
  );
};
