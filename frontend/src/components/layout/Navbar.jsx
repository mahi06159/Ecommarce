import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Search, User, ShoppingBag, Menu, X, LogOut, LayoutDashboard, Settings } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import './Navbar.css';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const { cartCount, setIsCartOpen } = useCart();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showSearchInput, setShowSearchInput] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery.trim())}`);
      setShowSearchInput(false);
      setSearchQuery('');
    }
  };

  const activeClass = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      {/* Section 1 — Announcement Bar */}
      <div className="announcement-bar">
        🛍️ FREE SHIPPING on all orders over ₹499 | 30 Days Easy Returns
      </div>

      {/* Section 2 — Navbar */}
      <header className="main-header">
        <div className="header-container">
          
          {/* Mobile Hamburguer */}
          <button className="mobile-menu-btn" onClick={() => setMobileMenuOpen(true)}>
            <Menu size={24} />
          </button>

          {/* Left - Logo */}
          <Link to="/" className="header-logo">
            <svg 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="var(--mahi-pink)" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
            <div className="logo-text">
              <span className="logo-main">Mahi</span>
              <span className="logo-sub">STORE</span>
            </div>
          </Link>

          {/* Center - Nav Links */}
          <nav className="desktop-nav">
            <Link to="/" className={`nav-link ${activeClass('/')}`}>Home</Link>
            <Link to="/products" className={`nav-link ${activeClass('/products')}`}>Shop</Link>
            <Link to="/products?category=Electronics" className="nav-link">Electronics</Link>
            <Link to="/products?category=Fashion" className="nav-link">Fashion</Link>
            <Link to="/products?category=Home%20%26%20Living" className="nav-link">Home & Living</Link>
            <Link to="/products?category=Accessories" className="nav-link">Accessories</Link>
            <Link to="/about" className="nav-link">About Us</Link>
            <Link to="/contact" className="nav-link">Contact</Link>
          </nav>

          {/* Right - Icons */}
          <div className="header-actions">
            
            {/* Search Input Toggle */}
            <div className="search-container">
              {showSearchInput ? (
                <form onSubmit={handleSearchSubmit} className="search-form-inline">
                  <input
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    autoFocus
                    className="search-input-field"
                  />
                  <button type="button" onClick={() => setShowSearchInput(false)} className="search-close-btn">
                    <X size={16} />
                  </button>
                </form>
              ) : (
                <button className="action-btn" onClick={() => setShowSearchInput(true)} aria-label="Search">
                  <Search size={20} />
                </button>
              )}
            </div>

            {/* Profile Dropdown */}
            <div className="profile-menu-container">
              <button 
                className="action-btn" 
                onClick={() => setShowUserMenu(!showUserMenu)}
                aria-label="User Account"
              >
                {user ? (
                  <div className="avatar-circle">
                    {user.username ? user.username.slice(0, 2).toUpperCase() : 'U'}
                  </div>
                ) : (
                  <User size={20} />
                )}
              </button>

              {showUserMenu && (
                <div className="user-dropdown-menu">
                  {user ? (
                    <>
                      <div className="dropdown-user-info">
                        <span className="dropdown-username">{user.username}</span>
                        <span className="dropdown-role">{user.role} Account</span>
                      </div>
                      <hr className="dropdown-divider" />
                      <Link to="/profile" onClick={() => setShowUserMenu(false)} className="dropdown-item">
                        <User size={16} /> Profile Info
                      </Link>
                      {user.role === 'Seller' && (
                        <>
                          <Link to="/seller/dashboard" onClick={() => setShowUserMenu(false)} className="dropdown-item">
                            <LayoutDashboard size={16} /> Seller Dashboard
                          </Link>
                          <Link to="/seller/products" onClick={() => setShowUserMenu(false)} className="dropdown-item">
                            <Settings size={16} /> My Products
                          </Link>
                        </>
                      )}
                      <hr className="dropdown-divider" />
                      <button onClick={() => { setShowUserMenu(false); handleLogout(); }} className="dropdown-item logout-btn">
                        <LogOut size={16} /> Logout
                      </button>
                    </>
                  ) : (
                    <>
                      <Link to="/login" onClick={() => setShowUserMenu(false)} className="dropdown-item">
                        Login
                      </Link>
                      <Link to="/register" onClick={() => setShowUserMenu(false)} className="dropdown-item">
                        Register
                      </Link>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Cart Button */}
            {(!user || user.role === 'Buyer') && (
              <button className="action-btn cart-toggle-btn" onClick={() => setIsCartOpen(true)} aria-label="Open Cart">
                <ShoppingBag size={20} />
                {cartCount > 0 && <span className="cart-count-badge">{cartCount}</span>}
              </button>
            )}

          </div>
        </div>
      </header>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="mobile-menu-overlay" onClick={() => setMobileMenuOpen(false)}>
          <div className="mobile-menu-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <span className="drawer-title">MENU</span>
              <button onClick={() => setMobileMenuOpen(false)} aria-label="Close menu">
                <X size={24} />
              </button>
            </div>
            <nav className="mobile-nav-links">
              <Link to="/" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Home</Link>
              <Link to="/products" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Shop</Link>
              <Link to="/products?category=Electronics" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Electronics</Link>
              <Link to="/products?category=Fashion" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Fashion</Link>
              <Link to="/products?category=Home%20%26%20Living" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Home & Living</Link>
              <Link to="/products?category=Accessories" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Accessories</Link>
              <Link to="/about" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">About Us</Link>
              <Link to="/contact" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Contact</Link>
              
              <hr className="drawer-divider" />
              
              {user ? (
                <>
                  <Link to="/profile" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">My Profile ({user.username})</Link>
                  {user.role === 'Seller' && (
                    <Link to="/seller/dashboard" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Seller Dashboard</Link>
                  )}
                  <button 
                    onClick={() => { setMobileMenuOpen(false); handleLogout(); }} 
                    className="mobile-nav-link mobile-logout-btn"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Login</Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="mobile-nav-link">Register</Link>
                </>
              )}
            </nav>
          </div>
        </div>
      )}
    </>
  );
};
