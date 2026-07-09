import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, ShieldCheck, CreditCard, ChevronRight, Plus, Check } from 'lucide-react';
import { motion } from 'framer-motion';
import confetti from 'canvas-confetti';
import api from '../api/client';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import { Navbar } from '../components/layout/Navbar';
import { getImgSrc, getPrimaryImg } from '../utils/imageUtils';
import './Checkout.css';

export const Checkout = () => {
  const navigate = useNavigate();
  const { cart, cartItems, cartTotal, refetchCart } = useCart();
  const { showToast } = useToast();
  const { user } = useAuth();

  const [step, setStep] = useState(1); // 1: Address, 2: Review, 3: Success
  const [addresses, setAddresses] = useState([]);
  const [selectedAddressId, setSelectedAddressId] = useState(null);
  const [loadingAddresses, setLoadingAddresses] = useState(true);

  // New Address Form
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [addressLine1, setAddressLine1] = useState('');
  const [addressLine2, setAddressLine2] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [country, setCountry] = useState('');
  const [isDefault, setIsDefault] = useState(false);
  const [submittingAddress, setSubmittingAddress] = useState(false);

  // Order placing states
  const [placingOrder, setPlacingOrder] = useState(false);
  const [createdOrder, setCreatedOrder] = useState(null);

  const fetchAddresses = async () => {
    setLoadingAddresses(true);
    try {
      const data = await api.get('/api/addresses/');
      const addrList = data || [];
      setAddresses(addrList);
      
      // Auto select default address or first one
      if (addrList.length > 0) {
        const defaultAddr = addrList.find(a => a.is_default);
        setSelectedAddressId(defaultAddr ? defaultAddr.id : addrList[0].id);
      }
    } catch (err) {
      console.error(err);
      showToast('Failed to fetch shipping addresses.', 'error');
    } finally {
      setLoadingAddresses(false);
    }
  };

  useEffect(() => {
    // If cart is empty, redirect to products listing
    if (!loadingAddresses && cartItems.length === 0 && step !== 3) {
      showToast('Your cart is empty! 🌸', 'info');
      navigate('/products');
    }
  }, [cartItems]);

  useEffect(() => {
    fetchAddresses();

    // Load Razorpay SDK
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handleAddAddress = async (e) => {
    e.preventDefault();
    if (!addressLine1 || !city || !state || !postalCode || !country) {
      showToast('Please fill out all required fields. 🌸', 'error');
      return;
    }

    setSubmittingAddress(true);
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
      
      const newAddress = await api.post('/api/addresses/', payload);
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
      
      // Reload and set selected
      await fetchAddresses();
      setSelectedAddressId(newAddress.id);
    } catch (err) {
      showToast('Failed to create address.', 'error');
    } finally {
      setSubmittingAddress(false);
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddressId) {
      showToast('Please select a shipping address. 🌸', 'error');
      return;
    }
    if (!cart?.id) {
      showToast('Cart not found.', 'error');
      return;
    }

    setPlacingOrder(true);
    try {
      // 1. Create local/Razorpay Order
      const paymentData = await api.post('/api/payments/create/', {
        cart_id: cart.id,
        shipping_address: selectedAddressId
      });

      if (!window.Razorpay) {
        showToast('Razorpay SDK failed to load. Please refresh the page.', 'error');
        setPlacingOrder(false);
        return;
      }

      // 2. Open Razorpay Checkout widget
      const options = {
        key: paymentData.key_id,
        amount: paymentData.amount,
        currency: paymentData.currency,
        name: 'Mahi Store',
        description: 'Secure Payment for Order',
        order_id: paymentData.razorpay_order_id,
        handler: async (response) => {
          setPlacingOrder(true);
          try {
            // 3. Verify Payment and create Order
            const verifyPayload = {
              razorpay_order_id: paymentData.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              cart_id: cart.id,
              shipping_address: selectedAddressId
            };
            const order = await api.post('/api/payments/verify/', verifyPayload);
            setCreatedOrder(order);

            // Celebrate with pink confetti!
            confetti({
              particleCount: 150,
              spread: 80,
              colors: ['#D4547A', '#F9E8EE', '#FBCFE8', '#FFD1DC']
            });

            showToast('Yay! Your order is on its way 💕', 'success');

            // Clear cart context
            refetchCart();

            // Progress to Success view
            setStep(3);
          } catch (err) {
            console.error(err);
            showToast(err.response?.data?.message || 'Payment verification failed.', 'error');
          } finally {
            setPlacingOrder(false);
          }
        },
        prefill: {
          name: user?.username || '',
          email: user?.email || '',
        },
        theme: {
          color: '#D4547A',
        },
        modal: {
          ondismiss: () => {
            showToast('Payment cancelled. 🌸', 'info');
            setPlacingOrder(false);
          }
        }
      };

      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', function (response) {
        showToast(response.error.description || 'Payment failed.', 'error');
        setPlacingOrder(false);
      });
      rzp.open();

    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.message || 'Failed to initiate payment.', 'error');
      setPlacingOrder(false);
    }
  };

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };

  const getSelectedAddressText = () => {
    const addr = addresses.find(a => a.id === selectedAddressId);
    if (!addr) return '';
    return `${addr.address_line1}, ${addr.address_line2 ? addr.address_line2 + ', ' : ''}${addr.city}, ${addr.state} - ${addr.postal_code}, ${addr.country}`;
  };



  return (
    <div className="checkout-page-wrapper">
      <Navbar />

      <div className="checkout-content-layout container">
        
        {/* Step Indicator Header */}
        <div className="checkout-wizard-steps">
          <div className={`wizard-step ${step === 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
            <span className="step-num">{step > 1 ? <Check size={14} /> : '1'}</span>
            <span className="step-name">Shipping</span>
          </div>
          <ChevronRight size={16} className="step-arrow" />
          <div className={`wizard-step ${step === 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
            <span className="step-num">{step > 2 ? <Check size={14} /> : '2'}</span>
            <span className="step-name">Review &amp; Pay</span>
          </div>
          <ChevronRight size={16} className="step-arrow" />
          <div className={`wizard-step ${step === 3 ? 'active' : ''}`}>
            <span className="step-num">3</span>
            <span className="step-name">Confirmation</span>
          </div>
        </div>

        {step === 1 && (
          <div className="checkout-step-container">
            <div className="checkout-main-content">
              <h2 className="step-title font-serif">Select Shipping Address</h2>
              
              {loadingAddresses ? (
                <div className="spinner-container"><div className="spinner"></div></div>
              ) : (
                <div className="addresses-select-list">
                  {addresses.map((addr) => (
                    <label 
                      key={addr.id} 
                      className={`address-select-card ${selectedAddressId === addr.id ? 'selected' : ''}`}
                    >
                      <input
                        type="radio"
                        name="shipping_address"
                        checked={selectedAddressId === addr.id}
                        onChange={() => setSelectedAddressId(addr.id)}
                        className="address-radio-input"
                      />
                      <div className="address-card-info">
                        <span className="address-lines">
                          <strong>{addr.address_line1}</strong>
                          {addr.address_line2 && `, ${addr.address_line2}`}
                        </span>
                        <span className="address-city-state">
                          {addr.city}, {addr.state} - {addr.postal_code}
                        </span>
                        <span className="address-country">{addr.country}</span>
                        {addr.is_default && <span className="default-badge">DEFAULT</span>}
                      </div>
                    </label>
                  ))}

                  {addresses.length === 0 && (
                    <div className="no-addresses-notice">
                      <p>You haven't saved any shipping addresses yet. Please add one below! 🌸</p>
                    </div>
                  )}
                </div>
              )}

              {/* Toggle Inline Address Form */}
              {!showAddressForm ? (
                <button 
                  className="btn-add-address-toggle btn-square" 
                  onClick={() => setShowAddressForm(true)}
                >
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
                        placeholder="Street address, P.O. box, company name"
                        value={addressLine1}
                        onChange={(e) => setAddressLine1(e.target.value)}
                        required
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Address Line 2 (Optional)</label>
                      <input 
                        type="text" 
                        placeholder="Apartment, suite, unit, building, floor, etc."
                        value={addressLine2}
                        onChange={(e) => setAddressLine2(e.target.value)}
                      />
                    </div>

                    <div className="form-grid-3">
                      <div className="form-group">
                        <label>City *</label>
                        <input 
                          type="text" 
                          value={city}
                          onChange={(e) => setCity(e.target.value)}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>State *</label>
                        <input 
                          type="text" 
                          value={state}
                          onChange={(e) => setState(e.target.value)}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Postal Code *</label>
                        <input 
                          type="text" 
                          value={postalCode}
                          onChange={(e) => setPostalCode(e.target.value)}
                          required
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>Country *</label>
                      <input 
                        type="text" 
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        required
                      />
                    </div>

                    <label className="checkbox-default-row">
                      <input 
                        type="checkbox" 
                        checked={isDefault}
                        onChange={(e) => setIsDefault(e.target.checked)}
                      />
                      <span>Set as default shipping address</span>
                    </label>

                    <div className="form-buttons-row">
                      <button type="submit" className="btn-add-address btn-square" disabled={submittingAddress}>
                        SAVE ADDRESS 💕
                      </button>
                      <button type="button" className="btn-cancel-address btn-square" onClick={() => setShowAddressForm(false)}>
                        CANCEL
                      </button>
                    </div>
                  </form>
                </div>
              )}

              <div className="checkout-actions-nav">
                <button 
                  className="btn-next-step btn-square"
                  onClick={() => setStep(2)}
                  disabled={!selectedAddressId}
                >
                  REVIEW ORDER →
                </button>
              </div>
            </div>

            {/* Sidebar Summary */}
            <div className="checkout-summary-sidebar">
              <h3 className="font-serif">Order Summary</h3>
              <div className="summary-items">
                {cartItems.map((item) => (
                  <div key={item.id} className="summary-item-card">
                    <span className="summary-item-name">{item.product_details?.name} (x{item.quantity})</span>
                    <span className="summary-item-total font-mono">
                      {formatPrice(Number(item.product_details?.price) * item.quantity)}
                    </span>
                  </div>
                ))}
              </div>
              <hr className="summary-divider" />
              <div className="summary-row total">
                <span>Total Amount:</span>
                <span className="font-mono">{formatPrice(cartTotal)}</span>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="checkout-step-container">
            <div className="checkout-main-content">
              <h2 className="step-title font-serif">Order Review &amp; Payment</h2>

              {/* Shipping Review */}
              <div className="review-section-box">
                <div className="box-title-row">
                  <MapPin size={18} color="var(--mahi-pink)" />
                  <h4>Shipping Destination</h4>
                </div>
                <p className="review-address-text">{getSelectedAddressText()}</p>
                <button className="btn-edit-step" onClick={() => setStep(1)}>
                  Change Address
                </button>
              </div>

              {/* Payment Info */}
              <div className="review-section-box">
                <div className="box-title-row">
                  <CreditCard size={18} color="var(--mahi-pink)" />
                  <h4>Payment Mode</h4>
                </div>
                <p className="review-payment-text">Razorpay Online Payment — Fast &amp; Secure 💳</p>
                <span className="cod-hint">Pay securely via Credit/Debit Cards, UPI, Netbanking, or Wallets.</span>
              </div>

              {/* Items Review */}
              <div className="review-section-box">
                <div className="box-title-row">
                  <ShieldCheck size={18} color="var(--mahi-pink)" />
                  <h4>Items Summary</h4>
                </div>
                <div className="review-items-list">
                  {cartItems.map((item) => {
                    const product = item.product_details || {};
                    return (
                      <div key={item.id} className="review-item-card">
                        <img src={getImgSrc(getPrimaryImg(product))} alt={product.name} className="review-item-img" />
                        <div className="review-item-details">
                          <h5>{product.name}</h5>
                          <span className="qty font-mono">Qty: {item.quantity}</span>
                        </div>
                        <span className="price font-mono">
                          {formatPrice(Number(product.price) * item.quantity)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="checkout-actions-nav">
                <button className="btn-back-step btn-square" onClick={() => setStep(1)}>
                  ← BACK
                </button>
                <motion.button 
                  className="btn-place-order btn-square" 
                  onClick={handlePlaceOrder}
                  disabled={placingOrder}
                  whileHover={placingOrder ? {} : { scale: 1.04 }}
                  whileTap={placingOrder ? {} : { scale: 0.97 }}
                >
                  {placingOrder ? 'PROCESSING PAYMENT...' : 'PAY & PLACE ORDER 💕'}
                </motion.button>
              </div>
            </div>

            {/* Sidebar Summary */}
            <div className="checkout-summary-sidebar">
              <h3 className="font-serif">Pricing Summary</h3>
              <div className="summary-row">
                <span>Subtotal:</span>
                <span className="font-mono">{formatPrice(cartTotal)}</span>
              </div>
              <div className="summary-row">
                <span>Shipping:</span>
                <span className="font-mono text-green">FREE</span>
              </div>
              <hr className="summary-divider" />
              <div className="summary-row total">
                <span>Grand Total:</span>
                <span className="font-mono">{formatPrice(cartTotal)}</span>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="checkout-success-view">
            <span className="success-emoji">🎉</span>
            <h2 className="font-serif">Yay! Your order is on its way 💕</h2>
            <p>Thank you for shopping at Mahi Store. Your package is being curated with care. 🌸</p>
            
            {createdOrder && (
              <div className="order-receipt-box">
                <span>Order Reference ID:</span>
                <strong className="font-mono">{createdOrder.id}</strong>
                <span>Total Placed: <strong>{formatPrice(createdOrder.total_price)}</strong></span>
              </div>
            )}

            <div className="success-buttons-row">
              <button className="btn-view-orders btn-square" onClick={() => navigate('/profile?tab=orders')}>
                VIEW MY ORDERS 🛍️
              </button>
              <button className="btn-continue-shopping btn-square" onClick={() => navigate('/')}>
                CONTINUE SHOPPING
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
