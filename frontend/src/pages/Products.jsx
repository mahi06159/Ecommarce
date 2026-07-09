import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Filter, Star, Search, SlidersHorizontal } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../api/client';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { Navbar } from '../components/layout/Navbar';
import { getImgSrc } from '../utils/imageUtils';
import './Products.css';

// Reusable 3D tilt card
const TiltCard = ({ children, className }) => {
  const ref = useRef(null);
  const onMouseMove = (e) => {
    const el = ref.current;
    if (!el) return;
    const { left, top, width, height } = el.getBoundingClientRect();
    const x = (e.clientX - left) / width  - 0.5;
    const y = (e.clientY - top)  / height - 0.5;
    el.style.transform = `perspective(800px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) scale(1.02)`;
  };
  const onMouseLeave = () => {
    if (ref.current) ref.current.style.transform = 'perspective(800px) rotateY(0) rotateX(0) scale(1)';
  };
  return (
    <motion.div
      ref={ref}
      className={className}
      style={{ transition: 'transform 0.18s ease', willChange: 'transform' }}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.1 }}
      transition={{ duration: 0.42, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
};

export const Products = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { showToast } = useToast();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [selectedCategory, setSelectedCategory] = useState(null); // category ID
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sortBy, setSortBy] = useState('newest'); // 'newest' | 'price-asc' | 'price-desc'
  const [searchVal, setSearchVal] = useState('');
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  // Get search params from URL
  const queryParams = new URLSearchParams(location.search);
  const urlSearch = queryParams.get('search') || '';
  const urlCategoryName = queryParams.get('category') || '';
  const urlCategoryId = queryParams.get('category_id') || '';

  // Initial load categories & reviews
  useEffect(() => {
    const fetchInitData = async () => {
      try {
        const [catData, revData] = await Promise.all([
          api.get('/api/categories/'),
          api.get('/api/reviews/')
        ]);
        setCategories(Array.isArray(catData) ? catData : []);
        setReviews(Array.isArray(revData) ? revData : []);
      } catch (err) {
        console.error('Failed to load filters data:', err);
      }
    };
    fetchInitData();
  }, []);

  // Fetch products when API parameters change
  useEffect(() => {
    const loadProducts = async () => {
      setLoading(true);
      try {
        let catId = urlCategoryId;
        
        // If category is passed as name in URL (e.g. from navbar), look up its ID
        if (!catId && urlCategoryName && categories.length > 0) {
          const matchedCat = categories.find(
            c => c.name.toLowerCase() === urlCategoryName.toLowerCase()
          );
          if (matchedCat) {
            catId = matchedCat.id;
          }
        }

        // Set local state filter to match URL
        if (catId) {
          setSelectedCategory(Number(catId));
        } else {
          setSelectedCategory(null);
        }

        if (urlSearch) {
          setSearchVal(urlSearch);
        }

        // Build API query
        let query = '/api/products/';
        const params = [];
        if (catId) params.push(`category=${catId}`);
        if (urlSearch) params.push(`search=${encodeURIComponent(urlSearch)}`);
        
        if (params.length > 0) {
          query += `?${params.join('&')}`;
        }

        const data = await api.get(query);
        setProducts(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Failed to load products:', err);
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, [location.search, categories]);

  // Compute review counts map: product_id -> review count
  const reviewCounts = {};
  const reviewsList = Array.isArray(reviews) ? reviews : [];
  reviewsList.forEach(r => {
    const prodId = r.product;
    reviewCounts[prodId] = (reviewCounts[prodId] || 0) + 1;
  });

  // Handle category sidebar click
  const handleCategorySelect = (catId) => {
    const params = new URLSearchParams(location.search);
    if (catId === null) {
      params.delete('category');
      params.delete('category_id');
    } else {
      params.set('category_id', catId);
      params.delete('category'); // clear name-based param
    }
    navigate(`/products?${params.toString()}`);
  };

  // Handle text search query
  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchVal(val);
    
    // Debounce search update to URL
    const params = new URLSearchParams(location.search);
    if (val.trim()) {
      params.set('search', val);
    } else {
      params.delete('search');
    }
    navigate(`/products?${params.toString()}`);
  };

  const handleAddToCart = async (product) => {
    try {
      await addToCart(product.id, 1);
      showToast(`Added ${product.name} to cart! ✨`, 'success');
    } catch (err) {
      showToast(err.response?.data?.message || 'Failed to add item', 'error');
    }
  };

  // Filter & Sort Logic on Client Side
  const filteredProducts = products.filter((prod) => {
    const price = Number(prod.price);
    const min = minPrice ? Number(minPrice) : 0;
    const max = maxPrice ? Number(maxPrice) : Infinity;
    return price >= min && price <= max;
  });

  const sortedProducts = [...filteredProducts].sort((a, b) => {
    if (sortBy === 'newest') {
      return new Date(b.created_at) - new Date(a.created_at);
    } else if (sortBy === 'price-asc') {
      return Number(a.price) - Number(b.price);
    } else if (sortBy === 'price-desc') {
      return Number(b.price) - Number(a.price);
    }
    return 0;
  });

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };



  return (
    <div className="products-page-wrapper">
      <Navbar />

      <div className="products-content-layout container">
        
        {/* Sidebar Filters - Desktop */}
        <aside className="filters-sidebar">
          <div className="sidebar-section">
            <h3 className="sidebar-section-title font-serif">Categories</h3>
            <ul className="filter-list">
              <li 
                className={`filter-item ${selectedCategory === null ? 'active' : ''}`}
                onClick={() => handleCategorySelect(null)}
              >
                All Products
              </li>
              {categories.map((cat) => (
                <li 
                  key={cat.id} 
                  className={`filter-item ${selectedCategory === cat.id ? 'active' : ''}`}
                  onClick={() => handleCategorySelect(cat.id)}
                >
                  {cat.name}
                </li>
              ))}
            </ul>
          </div>

          <div className="sidebar-section">
            <h3 className="sidebar-section-title font-serif">Price Range</h3>
            <div className="price-filter-inputs">
              <input
                type="number"
                placeholder="Min ₹"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                className="price-input"
              />
              <span className="price-range-dash">-</span>
              <input
                type="number"
                placeholder="Max ₹"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                className="price-input"
              />
            </div>
            {(minPrice || maxPrice) && (
              <button 
                className="clear-price-btn"
                onClick={() => { setMinPrice(''); setMaxPrice(''); }}
              >
                Clear price filter
              </button>
            )}
          </div>
        </aside>

        {/* Products Grid Content Area */}
        <main className="products-main-area">
          <div className="products-toolbar">
            
            {/* Search Input bar */}
            <div className="toolbar-search-box">
              <Search size={18} className="search-box-icon" />
              <input
                type="text"
                placeholder="Search products..."
                value={searchVal}
                onChange={handleSearchChange}
                className="toolbar-search-input"
              />
            </div>

            {/* Mobile Filter Button */}
            <button className="mobile-filter-toggle btn-square" onClick={() => setMobileFilterOpen(true)}>
              <SlidersHorizontal size={18} /> Filters
            </button>

            {/* Sort Dropdown */}
            <div className="toolbar-sort-box">
              <label htmlFor="sort-dropdown">Sort by:</label>
              <select 
                id="sort-dropdown"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-dropdown-select"
              >
                <option value="newest">Newest First</option>
                <option value="price-asc">Price Low → High</option>
                <option value="price-desc">Price High → Low</option>
              </select>
            </div>
          </div>

          {/* Results count status */}
          <div className="results-status-label">
            {urlSearch && (
              <span>Search results for "<strong>{urlSearch}</strong>" in </span>
            )}
            <span>
              <strong>
                {selectedCategory ? categories.find(c => c.id === selectedCategory)?.name : 'All Collections'}
              </strong>
            </span>
            <span> ({sortedProducts.length} items found)</span>
          </div>

          {loading ? (
            <div className="products-loading-state">
              <div className="spinner"></div>
            </div>
          ) : sortedProducts.length === 0 ? (
            <div className="products-empty-state">
              <span className="empty-emoji">🛍️</span>
              <h3>No products found</h3>
              <p>We couldn't find any products matching your current filters. Try resetting them! 🌸</p>
              <button 
                className="btn-reset-filters btn-square"
                onClick={() => {
                  setMinPrice('');
                  setMaxPrice('');
                  setSearchVal('');
                  handleCategorySelect(null);
                  navigate('/products');
                }}
              >
                RESET ALL FILTERS
              </button>
            </div>
          ) : (
            <div className="products-grid">
              {sortedProducts.map((product) => {
                const stockVal = Number(product.stock);
                const isSale = stockVal <= 5 && stockVal > 0;
                const revCount = reviewCounts[product.id] || 0;
                const stars = Math.round(product.average_rating || 0);

                return (
                  <TiltCard key={product.id} className="product-listing-card">
                    <div className="product-img-box" onClick={() => navigate(`/products/${product.id}`)}>
                      {isSale && <span className="badge-sale">SALE</span>}
                      <img 
                        src={getImgSrc(product.primary_image)} 
                        alt={product.name} 
                        className="product-card-img"
                      />
                    </div>
                    <div className="product-info-box">
                      <span className="product-category-tag">{product.category_name}</span>
                      <h4 className="product-name-link" onClick={() => navigate(`/products/${product.id}`)}>
                        {product.name}
                      </h4>
                      <div className="product-price-row font-mono">
                        <span className="sale-price">{formatPrice(product.price)}</span>
                        {isSale && (
                          <span className="original-price line-through">
                            {formatPrice(Number(product.price) * 1.3)}
                          </span>
                        )}
                      </div>

                      {/* Stock badge status */}
                      <div style={{ marginBottom: '10px' }}>
                        {stockVal === 0 ? (
                          <span className="badge-stock out">Out of Stock</span>
                        ) : stockVal <= 5 ? (
                          <span className="badge-stock low">Low Stock ({stockVal})</span>
                        ) : (
                          <span className="badge-stock in">In Stock</span>
                        )}
                      </div>

                      <div className="product-rating-row">
                        <div className="stars-container">
                          {[...Array(5)].map((_, i) => (
                            <Star 
                              key={i} 
                              size={12} 
                              fill={i < stars ? 'var(--mahi-gold)' : 'none'} 
                              stroke={i < stars ? 'var(--mahi-gold)' : '#CCCCCC'} 
                            />
                          ))}
                        </div>
                        <span className="rating-count">({revCount})</span>
                      </div>
                      
                      {stockVal > 0 ? (
                        <motion.button 
                          className="btn-add-cart-simple btn-square" 
                          onClick={() => handleAddToCart(product)}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          Add to Cart ✨
                        </motion.button>
                      ) : (
                        <button className="btn-add-cart-simple btn-square out-of-stock" disabled>
                          Out of Stock
                        </button>
                      )}
                    </div>
                  </TiltCard>
                );
              })}
            </div>
          )}
        </main>

      </div>

      {/* Mobile Filters Drawer Modal */}
      {mobileFilterOpen && (
        <div className="mobile-filter-overlay" onClick={() => setMobileFilterOpen(false)}>
          <div className="mobile-filter-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <span className="drawer-title">FILTERS</span>
              <button onClick={() => setMobileFilterOpen(false)}>✕</button>
            </div>
            <div className="drawer-body">
              <div className="filter-group-mobile">
                <h4 className="font-serif">Categories</h4>
                <select 
                  value={selectedCategory || ''}
                  onChange={(e) => {
                    const val = e.target.value;
                    handleCategorySelect(val ? Number(val) : null);
                  }}
                  className="mobile-select"
                >
                  <option value="">All Categories</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group-mobile">
                <h4 className="font-serif">Price Range</h4>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <input
                    type="number"
                    placeholder="Min"
                    value={minPrice}
                    onChange={(e) => setMinPrice(e.target.value)}
                    style={{ flex: 1 }}
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={maxPrice}
                    onChange={(e) => setMaxPrice(e.target.value)}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>

              <button className="btn-apply-mobile btn-square" onClick={() => setMobileFilterOpen(false)}>
                APPLY FILTERS
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
