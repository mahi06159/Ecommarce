import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Star, Plus, Minus, ShoppingBag, Trash2, Edit } from 'lucide-react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { Navbar } from '../components/layout/Navbar';
import './ProductDetail.css';

export const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { addToCart } = useCart();
  const { showToast } = useToast();

  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  
  // Review form states
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [editingReviewId, setEditingReviewId] = useState(null);

  const fetchProductAndReviews = async () => {
    try {
      const [prodRes, revRes] = await Promise.all([
        api.get(`/api/products/${id}/`),
        api.get(`/api/reviews/?product=${id}`)
      ]);
      setProduct(prodRes);
      setReviews(revRes || []);
    } catch (err) {
      console.error(err);
      showToast('Product not found.', 'error');
      navigate('/products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchProductAndReviews();
  }, [id]);

  const handleQuantityChange = (amount) => {
    const nextQty = quantity + amount;
    if (nextQty > 0 && nextQty <= product.stock) {
      setQuantity(nextQty);
    }
  };

  const handleAddToCart = async () => {
    if (!product) return;
    try {
      await addToCart(product.id, quantity);
      showToast(`Added ${quantity} ${product.name} to cart! 💕`, 'success');
    } catch (err) {
      showToast(err.response?.data?.message || 'Failed to add item', 'error');
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!user) {
      showToast('Please login to write a review. 🌸', 'error');
      navigate('/login');
      return;
    }
    if (user.role !== 'Buyer') {
      showToast('Only Buyers can submit reviews.', 'error');
      return;
    }

    setSubmittingReview(true);
    try {
      if (editingReviewId) {
        // Edit existing review
        await api.patch(`/api/reviews/${editingReviewId}/`, { rating, comment });
        showToast('Review updated successfully! ✨', 'success');
      } else {
        // Create new review
        await api.post('/api/reviews/', { product: product.id, rating, comment });
        showToast('Review submitted! Thank you 💕', 'success');
      }
      
      // Reset form and reload data
      setRating(5);
      setComment('');
      setEditingReviewId(null);
      await fetchProductAndReviews();
    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.message || 'Failed to submit review.', 'error');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleReviewDelete = async (reviewId) => {
    if (window.confirm('Are you sure you want to delete your review? 🌸')) {
      try {
        await api.delete(`/api/reviews/${reviewId}/`);
        showToast('Review deleted.', 'success');
        await fetchProductAndReviews();
      } catch (err) {
        showToast('Failed to delete review.', 'error');
      }
    }
  };

  const handleReviewEditClick = (rev) => {
    setEditingReviewId(rev.id);
    setRating(rev.rating);
    setComment(rev.comment);
    // Scroll to review form
    document.getElementById('review-form-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };

  const getImgSrc = (img) => {
    if (!img) return 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=600';
    if (img.startsWith('http')) return img;
    return `http://localhost:8000${img.startsWith('/') ? '' : '/'}${img}`;
  };

  if (loading) {
    return (
      <div className="product-detail-page-wrapper">
        <Navbar />
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (!product) return null;

  const stockVal = Number(product.stock);
  const alreadyReviewed = reviews.find(r => r.buyer?.username === user?.username);

  return (
    <div className="product-detail-page-wrapper">
      <Navbar />

      <div className="product-detail-layout container">
        
        {/* Left Side: Product Image */}
        <div className="detail-image-panel">
          <img 
            src={getImgSrc(product.img)} 
            alt={product.name} 
            className="detail-main-img"
          />
        </div>

        {/* Right Side: Product Details info */}
        <div className="detail-info-panel">
          <div className="detail-meta">
            <span className="detail-category-badge">{product.category_name}</span>
            {product.seller?.profile?.store_name && (
              <span className="detail-store-name">Store: <strong>{product.seller.profile.store_name}</strong></span>
            )}
          </div>

          <h1 className="detail-title font-serif">{product.name}</h1>
          
          <div className="detail-rating-summary">
            <div className="stars-container">
              {[...Array(5)].map((_, i) => (
                <Star 
                  key={i} 
                  size={16}
                  fill={i < Math.round(product.average_rating || 0) ? 'var(--mahi-gold)' : 'none'}
                  stroke={i < Math.round(product.average_rating || 0) ? 'var(--mahi-gold)' : '#CCCCCC'}
                />
              ))}
            </div>
            <span className="rating-text">
              {product.average_rating ? `${product.average_rating} Out of 5` : 'No ratings yet'}
            </span>
            <span className="rating-count">({reviews.length} customer reviews)</span>
          </div>

          <div className="detail-price font-mono">
            {formatPrice(product.price)}
          </div>

          <hr className="detail-divider" />

          <p className="detail-description">{product.details || 'No description available for this item.'}</p>

          <hr className="detail-divider" />

          {/* Stock Availability indicator */}
          <div className="detail-stock-row">
            <span className="label">Availability:</span>
            {stockVal === 0 ? (
              <span className="badge-stock out">Out of Stock</span>
            ) : stockVal <= 5 ? (
              <span className="badge-stock low">Only {stockVal} left in stock - Order Soon!</span>
            ) : (
              <span className="badge-stock in">In Stock ({stockVal} available)</span>
            )}
          </div>

          {/* Quantity selector and checkout btn */}
          {stockVal > 0 && (
            <div className="purchase-controls-row">
              <div className="qty-picker">
                <button 
                  className="qty-btn" 
                  onClick={() => handleQuantityChange(-1)}
                  disabled={quantity <= 1}
                >
                  <Minus size={14} />
                </button>
                <span className="qty-value font-mono">{quantity}</span>
                <button 
                  className="qty-btn" 
                  onClick={() => handleQuantityChange(1)}
                  disabled={quantity >= stockVal}
                >
                  <Plus size={14} />
                </button>
              </div>

              <button className="btn-add-to-cart-primary btn-square" onClick={handleAddToCart}>
                ADD TO CART <ShoppingBag size={18} style={{ marginLeft: '8px' }} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Reviews Section */}
      <section className="reviews-section-wrapper">
        <div className="container">
          <div className="section-header">
            <h2 className="font-serif">Customer Reviews</h2>
            <div className="emoji-divider">🛍️</div>
          </div>

          <div className="reviews-layout">
            
            {/* Reviews list */}
            <div className="reviews-list-container">
              {reviews.length === 0 ? (
                <div className="no-reviews-state">
                  <p>Be the first to review this product! 🌸</p>
                </div>
              ) : (
                <div className="reviews-cards-list">
                  {reviews.map((rev) => {
                    const revStars = Number(rev.rating || 0);
                    const isOwnReview = user && rev.buyer?.username === user.username;

                    return (
                      <div key={rev.id} className="review-card-item">
                        <div className="review-card-header">
                          <div className="reviewer-avatar">
                            {rev.buyer?.username ? rev.buyer.username.slice(0, 2).toUpperCase() : 'B'}
                          </div>
                          <div className="reviewer-info">
                            <h5 className="reviewer-name">{rev.buyer?.username || 'Buyer'}</h5>
                            <span className="review-date">
                              {new Date(rev.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          
                          {/* Stars display */}
                          <div className="review-card-stars">
                            {[...Array(5)].map((_, idx) => (
                              <Star 
                                key={idx} 
                                size={12} 
                                fill={idx < revStars ? 'var(--mahi-gold)' : 'none'} 
                                stroke={idx < revStars ? 'var(--mahi-gold)' : '#CCCCCC'} 
                              />
                            ))}
                          </div>
                        </div>
                        <p className="review-comment">{rev.comment}</p>
                        
                        {isOwnReview && (
                          <div className="own-review-actions">
                            <button 
                              className="btn-review-action edit"
                              onClick={() => handleReviewEditClick(rev)}
                            >
                              <Edit size={14} /> Edit
                            </button>
                            <button 
                              className="btn-review-action delete"
                              onClick={() => handleReviewDelete(rev.id)}
                            >
                              <Trash2 size={14} /> Delete
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Review form */}
            {user && user.role === 'Buyer' && (
              <div className="review-form-container" id="review-form-section">
                <h3 className="font-serif">
                  {editingReviewId ? 'Edit Your Review' : 'Write a Review'}
                </h3>
                
                {alreadyReviewed && !editingReviewId ? (
                  <div className="already-reviewed-notice">
                    <p>You have already reviewed this product. You can edit or delete your existing review above. 💕</p>
                  </div>
                ) : (
                  <form onSubmit={handleReviewSubmit} className="review-form">
                    <div className="form-group">
                      <label>Your Rating</label>
                      <div className="star-rating-selector">
                        {[1, 2, 3, 4, 5].map((val) => (
                          <button
                            key={val}
                            type="button"
                            className="star-selector-btn"
                            onClick={() => setRating(val)}
                          >
                            <Star 
                              size={24} 
                              fill={val <= rating ? 'var(--mahi-gold)' : 'none'}
                              stroke={val <= rating ? 'var(--mahi-gold)' : '#999999'}
                            />
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="form-group">
                      <label htmlFor="review-comment-field">Your Comments</label>
                      <textarea
                        id="review-comment-field"
                        placeholder="Share your experience with this product... 🌸"
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        required
                        rows={4}
                      />
                    </div>

                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button 
                        type="submit" 
                        className="btn-review-submit btn-square"
                        disabled={submittingReview}
                      >
                        {submittingReview ? 'SUBMITTING...' : editingReviewId ? 'UPDATE REVIEW 💕' : 'SUBMIT REVIEW 💕'}
                      </button>
                      {editingReviewId && (
                        <button 
                          type="button" 
                          className="btn-review-cancel btn-square"
                          onClick={() => {
                            setEditingReviewId(null);
                            setRating(5);
                            setComment('');
                          }}
                        >
                          CANCEL
                        </button>
                      )}
                    </div>
                  </form>
                )}
              </div>
            )}

          </div>
        </div>
      </section>
    </div>
  );
};
