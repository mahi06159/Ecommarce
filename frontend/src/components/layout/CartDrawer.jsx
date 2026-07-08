import React from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Trash2, Plus, Minus, ArrowRight, ShoppingBag } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import './CartDrawer.css';

export const CartDrawer = () => {
  const { 
    isCartOpen, 
    setIsCartOpen, 
    cartItems, 
    cartTotal, 
    updateCartItem, 
    removeFromCart 
  } = useCart();
  
  const navigate = useNavigate();

  if (!isCartOpen) return null;

  const handleCheckoutRedirect = () => {
    setIsCartOpen(false);
    navigate('/checkout');
  };

  const handleShopRedirect = () => {
    setIsCartOpen(false);
    navigate('/products');
  };

  const handleQuantityChange = async (itemId, currentQty, amount, stock) => {
    const nextQty = currentQty + amount;
    if (nextQty <= 0) return;
    if (nextQty > stock) {
      alert(`Oops! Only ${stock} items are in stock.`);
      return;
    }
    try {
      await updateCartItem(itemId, nextQty);
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to update quantity');
    }
  };

  const handleRemove = async (itemId) => {
    if (window.confirm('Are you sure you want to remove this item? 🌸')) {
      try {
        await removeFromCart(itemId);
      } catch (err) {
        alert('Failed to remove item');
      }
    }
  };

  // Helper to format currency
  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };

  // Helper to resolve image source
  const getImgSrc = (img) => {
    if (!img) return 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=150'; // standard placeholder
    if (img.startsWith('http')) return img;
    return `http://localhost:8000${img.startsWith('/') ? '' : '/'}${img}`;
  };

  return (
    <div className="cart-drawer-overlay" onClick={() => setIsCartOpen(false)}>
      <div className="cart-drawer-container" onClick={(e) => e.stopPropagation()}>
        
        {/* Drawer Header */}
        <div className="cart-drawer-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShoppingBag size={20} color="var(--mahi-pink)" />
            <h3 className="drawer-title font-serif">Shopping Bag</h3>
          </div>
          <button className="drawer-close-btn" onClick={() => setIsCartOpen(false)} aria-label="Close cart">
            <X size={24} />
          </button>
        </div>

        {/* Drawer Content */}
        <div className="cart-drawer-content">
          {cartItems.length === 0 ? (
            <div className="cart-empty-state">
              <span className="empty-emoji">🌸</span>
              <p className="empty-text">Your cart is waiting for something beautiful 🌸</p>
              <button className="btn-browse btn-square" onClick={handleShopRedirect}>
                BROWSE PRODUCTS
              </button>
            </div>
          ) : (
            <div className="cart-items-list">
              {cartItems.map((item) => {
                const product = item.product_details || {};
                const itemTotal = Number(product.price || 0) * item.quantity;
                return (
                  <div key={item.id} className="cart-item-card">
                    <img 
                      src={getImgSrc(product.img)} 
                      alt={product.name} 
                      className="cart-item-img"
                    />
                    <div className="cart-item-details">
                      <h4 className="cart-item-name">{product.name}</h4>
                      <p className="cart-item-meta">Price: {formatPrice(product.price)}</p>
                      
                      <div className="cart-item-actions">
                        {/* Qty controls */}
                        <div className="qty-picker">
                          <button 
                            className="qty-btn"
                            onClick={() => handleQuantityChange(item.id, item.quantity, -1, product.stock)}
                            disabled={item.quantity <= 1}
                          >
                            <Minus size={12} />
                          </button>
                          <span className="qty-value font-mono">{item.quantity}</span>
                          <button 
                            className="qty-btn"
                            onClick={() => handleQuantityChange(item.id, item.quantity, 1, product.stock)}
                            disabled={item.quantity >= product.stock}
                          >
                            <Plus size={12} />
                          </button>
                        </div>
                        
                        {/* Trash */}
                        <button className="item-remove-btn" onClick={() => handleRemove(item.id)}>
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                    <div className="cart-item-total font-mono">
                      {formatPrice(itemTotal)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        {cartItems.length > 0 && (
          <div className="cart-drawer-footer">
            <div className="cart-summary-row">
              <span>Subtotal:</span>
              <span className="font-mono">{formatPrice(cartTotal)}</span>
            </div>
            <div className="cart-summary-row total">
              <span>Estimated Total:</span>
              <span className="font-mono">{formatPrice(cartTotal)}</span>
            </div>
            
            <button className="btn-checkout btn-square" onClick={handleCheckoutRedirect}>
              PROCEED TO CHECKOUT <ArrowRight size={16} />
            </button>
          </div>
        )}

      </div>
    </div>
  );
};
