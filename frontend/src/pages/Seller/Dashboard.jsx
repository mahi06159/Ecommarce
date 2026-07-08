import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Package, ShoppingBag, IndianRupee, Clock, ArrowLeft } from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Navbar } from '../../components/layout/Navbar';
import './Dashboard.css';

export const Dashboard = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    revenue: 0,
    pendingItems: 0
  });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (user.role !== 'Seller') {
      showToast('Access denied. Seller accounts only. 🌸', 'error');
      navigate('/');
      return;
    }

    const loadSellerAnalytics = async () => {
      setLoading(true);
      try {
        // Fetch seller's products and order list
        const [productsRes, ordersRes] = await Promise.all([
          api.get(`/api/products/?seller=${user.id}`),
          api.get('/api/orders/')
        ]);

        const sellerProducts = productsRes || [];
        const sellerOrders = ordersRes || [];

        // Calculate analytics metrics
        let totalRevenue = 0;
        let pendingCount = 0;
        const salesByDate = {};

        sellerOrders.forEach((ord) => {
          // Date formatting for grouping (e.g. "Jun 28")
          const dateLabel = new Date(ord.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
          });

          let orderRevenue = 0;
          ord.items?.forEach((item) => {
            const itemTotal = Number(item.price) * item.quantity;
            totalRevenue += itemTotal;
            orderRevenue += itemTotal;

            if (item.status === 'Pending') {
              pendingCount += 1;
            }
          });

          salesByDate[dateLabel] = (salesByDate[dateLabel] || 0) + orderRevenue;
        });

        // Parse chart data for Recharts
        const chartArray = Object.entries(salesByDate).map(([date, sales]) => ({
          date,
          Sales: sales
        })).reverse(); // newest last

        setStats({
          totalProducts: sellerProducts.length,
          totalOrders: sellerOrders.length,
          revenue: totalRevenue,
          pendingItems: pendingCount
        });
        setChartData(chartArray.length > 0 ? chartArray : [{ date: 'Today', Sales: 0 }]);
      } catch (err) {
        console.error('Failed to load seller analytics:', err);
        showToast('Failed to load dashboard metrics.', 'error');
      } finally {
        setLoading(false);
      }
    };

    loadSellerAnalytics();
  }, [user]);

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };

  if (loading) {
    return (
      <div className="seller-dashboard-wrapper">
        <Navbar />
        <div className="spinner-container"><div className="spinner"></div></div>
      </div>
    );
  }

  return (
    <div className="seller-dashboard-wrapper">
      <Navbar />

      <div className="dashboard-content container">
        
        {/* Back Link Header */}
        <div className="dashboard-header-row">
          <Link to="/profile" className="btn-back-profile-link">
            <ArrowLeft size={16} /> Back to Profile Info
          </Link>
          <h1 className="dashboard-title font-serif">Seller Hub Analytics</h1>
        </div>

        {/* Stats Grid Cards */}
        <div className="stats-cards-grid">
          <div className="stats-card">
            <div className="card-icon-box pink">
              <Package size={24} />
            </div>
            <div className="card-info">
              <span className="info-label">My Products</span>
              <strong className="info-value font-mono">{stats.totalProducts}</strong>
            </div>
          </div>

          <div className="stats-card">
            <div className="card-icon-box lavender">
              <ShoppingBag size={24} />
            </div>
            <div className="card-info">
              <span className="info-label">Customer Orders</span>
              <strong className="info-value font-mono">{stats.totalOrders}</strong>
            </div>
          </div>

          <div className="stats-card">
            <div className="card-icon-box green">
              <IndianRupee size={24} />
            </div>
            <div className="card-info">
              <span className="info-label">Total Revenue</span>
              <strong className="info-value font-mono">{formatPrice(stats.revenue)}</strong>
            </div>
          </div>

          <div className="stats-card">
            <div className="card-icon-box amber">
              <Clock size={24} />
            </div>
            <div className="card-info">
              <span className="info-label">Pending Shipments</span>
              <strong className="info-value font-mono">{stats.pendingItems}</strong>
            </div>
          </div>
        </div>

        {/* Sales Chart Section */}
        <div className="chart-section-box">
          <h3 className="chart-title font-serif">Sales Performance (Revenue over Time)</h3>
          
          <div className="chart-container" style={{ width: '100%', height: 350 }}>
            {chartData.length === 0 || (chartData.length === 1 && chartData[0].Sales === 0) ? (
              <div className="empty-chart-notice">
                <p>No transactions registered yet. Complete orders to see visual sales metrics here! 🌸</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="date" stroke="#666666" fontSize={12} tickLine={false} />
                  <YAxis 
                    stroke="#666666" 
                    fontSize={12} 
                    tickLine={false} 
                    tickFormatter={(val) => `₹${val}`}
                  />
                  <Tooltip 
                    formatter={(value) => [formatPrice(value), 'Sales']}
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid var(--mahi-pink-mid)' }}
                  />
                  {/* Pink gradient bars (#EC4899 -> #F9A8D4) as specified in design prompt */}
                  <Bar dataKey="Sales" fill="var(--mahi-pink)" radius={[4, 4, 0, 0]} maxBarSize={50} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Fast Action hub */}
        <div className="quick-actions-banner">
          <h3 className="font-serif">Inventory Actions</h3>
          <div className="actions-buttons">
            <button className="btn-action-go btn-square" onClick={() => navigate('/seller/products')}>
              Manage Store Products 🌸
            </button>
            <button className="btn-action-go btn-square secondary" onClick={() => navigate('/seller/orders')}>
              Update Order Statuses 📦
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
