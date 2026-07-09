import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Truck, Award, RefreshCw, Lock, ShieldCheck, Package, Headphones,
  ChevronLeft, ChevronRight, Star, ShoppingBag
} from 'lucide-react';
import { motion, useScroll, useTransform } from 'framer-motion';
import api from '../api/client';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { Navbar } from '../components/layout/Navbar';
import { getImgSrc } from '../utils/imageUtils';
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
  return null;
};

// Reusable 3D tilt card — wraps any child with a subtle perspective tilt on hover
const TiltCard = ({ children, className, onClick, style }) => {
  const ref = useRef(null);
  const handleMouseMove = (e) => {
    const el = ref.current;
    if (!el) return;
    const { left, top, width, height } = el.getBoundingClientRect();
    const x = (e.clientX - left) / width  - 0.5;  // -0.5 to 0.5
    const y = (e.clientY - top)  / height - 0.5;
    el.style.transform = `perspective(800px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) scale(1.02)`;
  };
  const handleMouseLeave = () => {
    if (ref.current) ref.current.style.transform = 'perspective(800px) rotateY(0deg) rotateX(0deg) scale(1)';
  };
  return (
    <motion.div
      ref={ref}
      className={className}
      onClick={onClick}
      style={{ ...style, transition: 'transform 0.18s ease', willChange: 'transform' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      initial={{ opacity: 0, y: 28 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
};

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 32 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.2 },
  transition: { duration: 0.5, delay, ease: 'easeOut' },
});

const slideIn = (dir = 'left', delay = 0) => ({
  initial: { opacity: 0, x: dir === 'left' ? -48 : 48 },
  whileInView: { opacity: 1, x: 0 },
  viewport: { once: true, amount: 0.2 },
  transition: { duration: 0.55, delay, ease: 'easeOut' },
});

export const Home = () => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { showToast } = useToast();
  
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const bestSellersRef = useRef(null);
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] });
  const heroImgY = useTransform(scrollYProgress, [0, 1], ['0%', '22%']);

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [catData, prodData, revData] = await Promise.all([
          api.get('/api/categories/'),
          api.get('/api/products/'),
          api.get('/api/reviews/')
        ]);
        
        setCategories(Array.isArray(catData) ? catData : []);
        setProducts(Array.isArray(prodData) ? prodData : []);
        setReviews(Array.isArray(revData) ? revData : []);
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



  return (
    <div className="home-page-wrapper">
      <Navbar />

      {/* Section 3 — Hero Banner */}
      <section className="hero-section" ref={heroRef}>
        <div className="hero-left">
          <motion.span className="hero-eyebrow" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>DISCOVER EVERYTHING YOU LOVE</motion.span>
          <motion.h1 className="hero-heading font-serif" initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}>
            Shop Smart,<br />
            Live Better<br />
            <span className="text-pink">Every Day</span>
          </motion.h1>
          <motion.p className="hero-subtext" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55, delay: 0.35 }}>
            Explore thousands of products across fashion, electronics, home & more — all in one place.
          </motion.p>
          <motion.div className="hero-buttons" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.5 }}>
            <motion.button className="btn-hero-primary btn-square" onClick={() => navigate('/products')} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}>
              SHOP NOW
            </motion.button>
            <motion.button className="btn-hero-secondary" onClick={() => navigate('/products')} whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              BROWSE COLLECTIONS →
            </motion.button>
          </motion.div>
          <div className="carousel-dots">
            <span className="dot active"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        </div>
        <div className="hero-right" style={{ overflow: 'hidden' }}>
          <motion.img 
            src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1000" 
            alt="Lifestyle Shopping" 
            className="hero-image"
            style={{ y: heroImgY }}
            initial={{ opacity: 0, scale: 1.06 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </div>
      </section>

      {/* Section 4 — Trust/Feature Bar */}
      <section className="trust-bar">
        <div className="trust-bar-container">
          <motion.div className="trust-item" {...fadeUp(0.1)}>
            <Truck size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">FREE SHIPPING</span>
              <span className="trust-sub">On all orders over ₹499</span>
            </div>
          </motion.div>
          <div className="trust-divider"></div>
          <motion.div className="trust-item" {...fadeUp(0.2)}>
            <Award size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">TOP QUALITY</span>
              <span className="trust-sub">Curated premium products</span>
            </div>
          </motion.div>
          <div className="trust-divider"></div>
          <motion.div className="trust-item" {...fadeUp(0.3)}>
            <RefreshCw size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">EASY RETURNS</span>
              <span className="trust-sub">30 days money back</span>
            </div>
          </motion.div>
          <div className="trust-divider"></div>
          <motion.div className="trust-item" {...fadeUp(0.4)}>
            <Lock size={28} className="trust-icon" />
            <div className="trust-texts">
              <span className="trust-label">SECURE PAYMENT</span>
              <span className="trust-sub">100% safe checkout</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Section 5 — Shop by Category */}
      <section className="category-section">
        <div className="container">
          <motion.div className="section-header" {...fadeUp(0)}>
            <h2>SHOP BY CATEGORY</h2>
            <div className="emoji-divider">🛍️</div>
          </motion.div>
          
          {loading ? (
            <div className="spinner-container">
              <div className="spinner"></div>
            </div>
          ) : (
            <div className="category-grid">
              {categories.slice(0, 8).map((cat, i) => {
                const catImg = getCategoryImg(cat.name);
                return (
                  <motion.div
                    key={cat.id}
                    className="category-card"
                    onClick={() => navigate(`/products?category=${cat.id}`)}
                    initial={{ opacity: 0, y: 24 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.2 }}
                    transition={{ duration: 0.42, delay: i * 0.07, ease: 'easeOut' }}
                    whileHover={{ scale: 1.06, y: -4 }}
                  >
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
                  </motion.div>
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
              {products.slice(0, 10).map((product, i) => {
                const isSale = product.stock <= 5;
                const revCount = reviewCounts[product.id] || 0;
                const stars = Math.round(product.average_rating || 0);

                return (
                  <TiltCard key={product.id} className="product-carousel-card">
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
        </div>
      </section>

      {/* Section 7 — Promo Banner (2 side-by-side cards) */}
      <section className="promo-banners-section">
        <motion.div className="promo-card left-card" onClick={() => navigate('/products')} {...slideIn('left', 0)} whileHover={{ scale: 1.02 }}>
          <div className="promo-content">
            <span className="promo-eyebrow">SPECIAL OFFER</span>
            <h3 className="promo-heading font-serif">
              Up To 30% Off<br />
              On Selected Products
            </h3>
            <motion.button className="btn-promo btn-square" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.96 }}>SHOP NOW</motion.button>
          </div>
          <img 
            src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400" 
            alt="Promo bag details" 
            className="promo-decor-img"
          />
        </motion.div>
        <motion.div className="promo-card right-card" onClick={() => navigate('/products?ordering=-created_at')} {...slideIn('right', 0.1)} whileHover={{ scale: 1.02 }}>
          <div className="promo-content">
            <span className="promo-eyebrow">NEW ARRIVALS</span>
            <h3 className="promo-heading font-serif">
              Fresh & Trending<br />
              New Collections
            </h3>
            <motion.button className="btn-promo btn-square" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.96 }}>DISCOVER NOW</motion.button>
          </div>
          <img 
            src="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=400" 
            alt="New arrivals unboxing" 
            className="promo-decor-img"
          />
        </motion.div>
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
