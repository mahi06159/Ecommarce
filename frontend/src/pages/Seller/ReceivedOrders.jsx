import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Inbox, Clock, CheckCircle, XCircle } from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Navbar } from '../../components/layout/Navbar';
import { getImgSrc, getPrimaryImg } from '../../utils/imageUtils';
import './ReceivedOrders.css';

export const ReceivedOrders = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('All');

  const fetchReceivedOrders = async () => {
    setLoading(true);
    try {
      const data = await api.get('/api/orders/');
      setOrders(data || []);
    } catch (err) {
      console.error(err);
      showToast('Failed to fetch received orders.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (user.role !== 'Seller') {
      showToast('Sellers access only. 🌸', 'error');
      navigate('/');
      return;
    }
    fetchReceivedOrders();
  }, [user]);

  const handleStatusChange = async (itemId, nextStatus) => {
    try {
      await api.patch(`/api/orders/items/${itemId}/status/`, { status: nextStatus });
      showToast('Order item status updated! 💕', 'success');
      // Reload orders to reflect stock updates / order status recalculations
      fetchReceivedOrders();
    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.status?.[0] || 'Failed to update order status.', 'error');
    }
  };

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };



  // Extract all individual items from seller orders for list presentation
  const allOrderItems = [];
  orders.forEach((order) => {
    order.items?.forEach((item) => {
      allOrderItems.push({
        ...item,
        orderId: order.id,
        orderDate: order.created_at,
        buyerUsername: order.buyer_username,
        shippingAddress: order.shipping_address_text,
      });
    });
  });

  const filteredItems = allOrderItems.filter((item) => {
    if (statusFilter === 'All') return true;
    return item.status === statusFilter;
  });

  return (
    <div className="received-orders-page-wrapper">
      <Navbar />

      <div className="received-orders-content container">
        
        {/* Header navigation bar */}
        <div className="orders-header-row">
          <div>
            <Link to="/profile" className="btn-back-profile-link">
              <ArrowLeft size={16} /> Back to Profile Info
            </Link>
            <h1 className="orders-title font-serif">Customer Orders Received</h1>
          </div>

          {/* Tab filters */}
          <div className="status-tabs-row">
            {['All', 'Pending', 'Completed', 'Cancelled'].map((status) => (
              <button 
                key={status}
                className={`status-tab-btn ${statusFilter === status ? 'active' : ''}`}
                onClick={() => setStatusFilter(status)}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="spinner-container"><div className="spinner"></div></div>
        ) : filteredItems.length === 0 ? (
          <div className="empty-orders-state">
            <Inbox size={48} color="var(--mahi-pink-mid)" />
            <h3>No orders registered</h3>
            <p>Orders containing your products will appear here. Stay tuned! 🌸</p>
          </div>
        ) : (
          <div className="received-orders-cards-list">
            {filteredItems.map((item) => {
              const product = item.product_details || {};
              const statusClass = item.status.toLowerCase();

              return (
                <div key={item.id} className="received-order-card">
                  
                  {/* Product detail row */}
                  <div className="order-product-section">
                    <img src={getImgSrc(getPrimaryImg(product))} alt={product.name} className="product-thumb" />
                    <div className="product-details">
                      <span className="order-id font-mono">Order ID: #{item.orderId}</span>
                      <h4 className="product-name">{product.name}</h4>
                      <span className="qty-price font-mono">
                        Qty: {item.quantity} | Total: {formatPrice(Number(item.price) * item.quantity)}
                      </span>
                    </div>
                  </div>

                  {/* Customer details info */}
                  <div className="order-buyer-section">
                    <span className="buyer-username">Buyer: <strong>{item.buyerUsername}</strong></span>
                    <span className="order-date">Date: {new Date(item.orderDate).toLocaleDateString()}</span>
                    <span className="shipping-text">Address: {item.shippingAddress}</span>
                  </div>

                  {/* Actions & Status row */}
                  <div className="order-status-actions">
                    <div className="status-label-group">
                      <span className="label">Status:</span>
                      <span className={`status-badge ${statusClass}`}>
                        {item.status === 'Pending' && <Clock size={12} style={{ marginRight: '4px' }} />}
                        {item.status === 'Completed' && <CheckCircle size={12} style={{ marginRight: '4px' }} />}
                        {item.status === 'Cancelled' && <XCircle size={12} style={{ marginRight: '4px' }} />}
                        {item.status}
                      </span>
                    </div>

                    <div className="status-dropdown-group">
                      <label htmlFor={`status-select-${item.id}`}>Update:</label>
                      <select
                        id={`status-select-${item.id}`}
                        value={item.status}
                        onChange={(e) => handleStatusChange(item.id, e.target.value)}
                        className="status-dropdown-select"
                      >
                        <option value="Pending">Pending</option>
                        <option value="Completed">Completed</option>
                        <option value="Cancelled">Cancelled</option>
                      </select>
                    </div>
                  </div>

                </div>
              );
            })}
          </div>
        )}

      </div>
    </div>
  );
};
