import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ToastProvider } from './context/ToastContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { CartDrawer } from './components/layout/CartDrawer';
import { Navbar } from './components/layout/Navbar';

// Pages
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Products } from './pages/Products';
import { ProductDetail } from './pages/ProductDetail';
import { Checkout } from './pages/Checkout';
import { Profile } from './pages/Profile';
import { ForgotPassword } from './pages/ForgotPassword';
import { ResetPassword } from './pages/ResetPassword';
import { Dashboard as SellerDashboard } from './pages/Seller/Dashboard';
import { MyProducts as SellerProducts } from './pages/Seller/MyProducts';
import { ReceivedOrders as SellerOrders } from './pages/Seller/ReceivedOrders';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="spinner-container">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

// Role Guard Wrapper
const RoleGuard = ({ children, allowedRole }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="spinner-container">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!user || user.role !== allowedRole) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <CartProvider>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/products" element={<Products />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              
              {/* Fallback about and contact simple pages */}
              <Route path="/about" element={
                <div style={{ background: 'var(--bg-light)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
                  <Navbar />
                  <div style={{ flex: 1, padding: '80px 20px', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
                    <h1 className="font-serif" style={{ fontSize: '36px', color: 'var(--mahi-pink)', marginBottom: '20px' }}>About Mahi Store</h1>
                    <p style={{ color: 'var(--mahi-gray)', lineHeight: '1.8' }}>
                      Welcome to Mahi Store! We are a curated marketplace dedicated to bringing you the best fashion, electronics, home essentials, and lifestyle accessories. Our mission is to combine top-quality curation with seamless user experience. 💕
                    </p>
                  </div>
                </div>
              } />
              <Route path="/contact" element={
                <div style={{ background: 'var(--bg-light)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
                  <Navbar />
                  <div style={{ flex: 1, padding: '80px 20px', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
                    <h1 className="font-serif" style={{ fontSize: '36px', color: 'var(--mahi-pink)', marginBottom: '20px' }}>Contact Us</h1>
                    <p style={{ color: 'var(--mahi-gray)', lineHeight: '1.8', marginBottom: '24px' }}>
                      Have questions about your order or want to list products as a seller? Reach out to us anytime! 🌸
                    </p>
                    <div style={{ background: '#fff', border: '1px solid var(--mahi-pink-mid)', padding: '20px', textAlign: 'left' }}>
                      <p>📧 Email: support@mahistore.com</p>
                      <p style={{ marginTop: '10px' }}>📞 Phone: +91 98765 43210</p>
                    </div>
                  </div>
                </div>
              } />

              {/* Protected Buyer Routes */}
              <Route path="/checkout" element={
                <ProtectedRoute>
                  <Checkout />
                </ProtectedRoute>
              } />
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } />

              {/* Protected Seller Routes */}
              <Route path="/seller/dashboard" element={
                <ProtectedRoute>
                  <RoleGuard allowedRole="Seller">
                    <SellerDashboard />
                  </RoleGuard>
                </ProtectedRoute>
              } />
              <Route path="/seller/products" element={
                <ProtectedRoute>
                  <RoleGuard allowedRole="Seller">
                    <SellerProducts />
                  </RoleGuard>
                </ProtectedRoute>
              } />
              <Route path="/seller/orders" element={
                <ProtectedRoute>
                  <RoleGuard allowedRole="Seller">
                    <SellerOrders />
                  </RoleGuard>
                </ProtectedRoute>
              } />

              {/* Catch-all Redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>

            {/* Global Slide-in Cart Drawer */}
            <CartDrawer />
          </Router>
        </CartProvider>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
