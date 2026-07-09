import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Truck, Award, RefreshCw, Lock, ShieldCheck, Package, Headphones,
  ChevronLeft, ChevronRight, Star, ShoppingBag
} from 'lucide-react';
import api from '../api/client';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { Navbar } from '../components/layout/Navbar';
import './Home.css';

// Category fallback images based on common names
const categoryImages = {
  electronics:   'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=200',
  fashion:       'https://images.unsplash.com/photo-1445205170230-053b83016050?w=200',
  home:          'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=200',
  living:        'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=200',
  accessories:   'https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=200',
  beauty:        'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=200',
  sports:        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=200',
  books:         'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=200',
  toys:          'https://images.unsplash.com/photo-1560343776-97e7d202ff0e?w=200',
};

const getCategoryImg = (catName) => {
  const name = catName.toLowerCase();
  for (const key in categoryImages) {
    if (name.includes(key)) {
      return categoryImages[key];
    }
  }
  // Default gradient fallback representation
  return null;
};

export const Home = () => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { showToast } = useToast();
  
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const bestSellersRef = useRef(null);

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [catData, prodData, revData] = await Promise.all([
          api.get('/api/categories/'),
          api.get('/api/products/'),
          api.get('/api/reviews/')
        ]);
        
        setCategories(catData || []);
        setProducts(prodData || []);
        setReviews(revData || []);
      } catch (err) {
        console.error('Failed to load homepage data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadHomeData();
  }, []);

  // Compute review counts map: product_id -> review count
  const reviewCounts = {};
  const reviewsList = Array.isArray(reviews) ? reviews : [];
  reviewsList.forEach(r => {
    const prodId = r.product;
    reviewCounts[prodId] = (reviewCounts[prodId] || 0) + 1;
  });

  const scrollCarousel = (direction) => {
    if (bestSellersRef.current) {
      const scrollAmount = direction === 'left' ? -300 : 300;
      bestSellersRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  const handleAddToCart = async (product) => {
    try {
      await addToCart(product.id, 1);
      showToast(`Added ${product.name} to cart! ✨`, 'success');
    } catch (err) {
      showToast(err.response?.data?.message || 'Failed to add item to cart', 'error');
    }
  };

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };

  const getImgSrc = (img) => {
    if (!img) return 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=300';
    if (img.startsWith('http')) return img;
    return `http://localhost:8000${img.startsWith('/') ? '' : '/'}${img}`;
  };

  return (
    <div className="home-page-wrapper">
      <Navbar />

      {/* Section 3 — Hero Banner */}
      <section className="hero-section">
        <div className="hero-left">
          <span className="hero-eyebrow">DISCOVER EVERYTHING YOU LOVE</span>
          <h1 className="hero-heading font-serif">
            Shop Smart,<br />
            Live Better<br />
            <span className="text-pink">Every Day</span>
          </h1>
          <p className="hero-subtext">
            Explore thousands of products across fashion, electronics, home &amp; more — all in one place.
          </p>
          <div className="hero-buttons">
            <button className="btn-hero-primary btn-square" onClick={() => navigate('/products')}>
              SHOP NOW
            </button>
            <button className="btn-hero-secondary" onClick={() => navigate('/products')}>
              BROWSE COLLECTIONS →
            </button>
          </div>
          <div className="carousel-dots">
            <span className="dot active"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        </div>
        <div className="hero-right">
          <img 
            src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1000" 
            alt="Lifestyle Shopping" 
            className="hero-image"
          />
        </div>
      </section>

      {/* Section 4 — Trust/Feature Bar */}
      <section className="trust-bar">
        <div className="trust-bar-container">
          <div className="trust-item">
            <Truck size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">FREE SHIPPING</span>
              <span className="trust-sub">On all orders over ₹499</span>
            </div>
          </div>
          <div className="trust-divider"></div>
          <div className="trust-item">
            <Award size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">TOP QUALITY</span>
              <span className="trust-sub">Curated premium products</span>
            </div>
          </div>
          <div className="trust-divider"></div>
          <div className="trust-item">
            <RefreshCw size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">EASY RETURNS</span>
              <span className="trust-sub">30 days money back</span>
            </div>
          </div>
          <div className="trust-divider"></div>
          <div className="trust-item">
            <Lock size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">SECURE PAYMENT</span>
              <span className="trust-sub">100% safe checkout</span>
            </div>
          </div>
        </div>
      </section>

      {/* Section 5 — Shop by Category */}
      <section className="category-section">
        <div className="container">
          <div className="section-header">
            <h2>SHOP BY CATEGORY</h2>
            <div className="emoji-divider">🛍️</div>
          </div>
          
          {loading ? (
            <div className="spinner-container">
              <div className="spinner"></div>
            </div>
          ) : (
            <div className="category-grid">
              {categories.slice(0, 6).map((cat) => {
                const catImg = getCategoryImg(cat.name);
                return (
                  <div key={cat.id} className="category-card" onClick={() => navigate(`/products?category=${cat.id}`)}>
                    <div className="category-img-container">
                      {catImg ? (
                        <img src={catImg} alt={cat.name} className="category-circle-img" />
                      ) : (
                        <div className="category-circle-gradient">
                          <span>{cat.name.slice(0, 2).toUpperCase()}</span>
                        </div>
                      )}
                    </div>
                    <span className="category-name">{cat.name}</span>
                    <span className="category-action">Shop Now →</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Section 6 — Best Sellers (Product Carousel) */}
      <section className="best-sellers-section">
        <div className="container" style={{ position: 'relative' }}>
          <div className="section-header">
            <h2>BEST SELLERS</h2>
            <div className="emoji-divider">🛍️</div>
          </div>

          {/* Carousel Arrows */}
          <button className="carousel-arrow left" onClick={() => scrollCarousel('left')} aria-label="Previous products">
            <ChevronLeft size={20} />
          </button>
          <button className="carousel-arrow right" onClick={() => scrollCarousel('right')} aria-label="Next products">
            <ChevronRight size={20} />
          </button>

          {loading ? (
            <div className="spinner-container">
              <div className="spinner"></div>
            </div>
          ) : (
            <div className="best-sellers-carousel no-scrollbar" ref={bestSellersRef}>
              {products.slice(0, 10).map((product) => {
                const isSale = product.stock <= 5;
                const revCount = reviewCounts[product.id] || 0;
                
                // Round rating for displaying stars
                const stars = Math.round(product.average_rating || 0);

                return (
                  <div key={product.id} className="product-carousel-card">
                    <div className="product-img-box" onClick={() => navigate(`/products/${product.id}`)}>
                      {isSale && <span className="badge-sale">SALE</span>}
                      <img 
                        src={getImgSrc(product.img)} 
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
                      
                      {/* Ratings stars */}
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
                      
                      {product.stock > 0 ? (
                        <button 
                          className="btn-add-cart-simple btn-square" 
                          onClick={() => handleAddToCart(product)}
                        >
                          Add to Cart ✨
                        </button>
                      ) : (
                        <button className="btn-add-cart-simple btn-square out-of-stock" disabled>
                          Out of Stock
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Section 7 — Promo Banner (2 side-by-side cards) */}
      <section className="promo-banners-section">
        <div className="promo-card left-card" onClick={() => navigate('/products')}>
          <div className="promo-content">
            <span className="promo-eyebrow">SPECIAL OFFER</span>
            <h3 className="promo-heading font-serif">
              Up To 30% Off<br />
              On Selected Products
            </h3>
            <button className="btn-promo btn-square">SHOP NOW</button>
          </div>
          <img 
            src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400" 
            alt="Promo bag details" 
            className="promo-decor-img"
          />
        </div>
        <div className="promo-card right-card" onClick={() => navigate('/products?ordering=-created_at')}>
          <div className="promo-content">
            <span className="promo-eyebrow">NEW ARRIVALS</span>
            <h3 className="promo-heading font-serif">
              Fresh &amp; Trending<br />
              New Collections
            </h3>
            <button className="btn-promo btn-square">DISCOVER NOW</button>
          </div>
          <img 
            src="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=400" 
            alt="New arrivals unboxing" 
            className="promo-decor-img"
          />
        </div>
      </section>

      {/* Section 8 — Social Strip */}
      <section className="social-strip-section">
        <div className="social-header">
          <h4>FOLLOW US ON INSTAGRAM @MAHI.STORE</h4>
        </div>
        <div className="social-grid">
          <div className="social-img-box">
            <img src="https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=300" alt="Instagram electronics" />
            <div className="social-overlay">
              <span className="overlay-icon">📸</span>
            </div>
          </div>
          <div className="social-img-box">
            <img src="https://images.unsplash.com/photo-1445205170230-053b83016050?w=300" alt="Instagram fashion" />
            <div className="social-overlay">
              <span className="overlay-icon">📸</span>
            </div>
          </div>
          <div className="social-img-box">
            <img src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=300" alt="Instagram home" />
            <div className="social-overlay">
              <span className="overlay-icon">📸</span>
            </div>
          </div>
          <div className="social-img-box">
            <img src="https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=300" alt="Instagram accessories" />
            <div className="social-overlay">
              <span className="overlay-icon">📸</span>
            </div>
          </div>
          <div className="social-img-box">
            <img src="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=300" alt="Instagram shopping" />
            <div className="social-overlay">
              <span className="overlay-icon">📸</span>
            </div>
          </div>
          <div className="social-img-box">
            <img src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=300" alt="Instagram lifestyle" />
            <div className="social-overlay">
              <span className="overlay-icon">📸</span>
            </div>
          </div>
        </div>
      </section>

      {/* Section 9 — Bottom Trust Bar */}
      <section className="bottom-trust-bar">
        <div className="container trust-bar-grid">
          <div className="bottom-trust-item">
            <ShieldCheck size={22} className="bottom-trust-icon" />
            <span className="bottom-trust-label">TRUSTED STORE</span>
            <span className="bottom-trust-sub">10,000+ happy customers</span>
          </div>
          <div className="bottom-trust-item">
            <Package size={22} className="bottom-trust-icon" />
            <span className="bottom-trust-label">QUALITY PRODUCTS</span>
            <span className="bottom-trust-sub">Carefully curated for you</span>
          </div>
          <div className="bottom-trust-item">
            <RefreshCw size={22} className="bottom-trust-icon" />
            <span className="bottom-trust-label">EASY RETURNS</span>
            <span className="bottom-trust-sub">Hassle-free 30 day returns</span>
          </div>
          <div className="bottom-trust-item">
            <Headphones size={22} className="bottom-trust-icon" />
            <span className="bottom-trust-label">CUSTOMER SUPPORT</span>
            <span className="bottom-trust-sub">We're here to help you</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="container">
          <p>© {new Date().getFullYear()} Mahi Store. All Rights Reserved. Made with 💕</p>
        </div>
      </footer>
    </div>
  );
};
