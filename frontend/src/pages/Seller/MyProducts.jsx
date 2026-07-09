import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Plus, Edit, Trash2, ArrowLeft, Upload, Package } from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Navbar } from '../../components/layout/Navbar';
import { getImgSrc, getPrimaryImg } from '../../utils/imageUtils';
import './MyProducts.css';

export const MyProducts = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form Modal States
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null); // null for add, product object for edit
  const [name, setName] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [details, setDetails] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchInventory = async () => {
    try {
      const [prodRes, catRes] = await Promise.all([
        api.get(`/api/products/?seller=${user.id}`),
        api.get('/api/categories/')
      ]);
      setProducts(prodRes || []);
      setCategories(catRes || []);
    } catch (err) {
      console.error(err);
      showToast('Failed to load store inventory.', 'error');
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
      showToast('Sellers only. 🌸', 'error');
      navigate('/');
      return;
    }
    fetchInventory();
  }, [user]);

  const handleOpenAddModal = () => {
    setEditingProduct(null);
    setName('');
    setCategoryId(categories.length > 0 ? categories[0].id : '');
    setDetails('');
    setPrice('');
    setStock('');
    setImageFile(null);
    setImagePreview(null);
    setShowModal(true);
  };

  const handleOpenEditModal = (prod) => {
    setEditingProduct(prod);
    setName(prod.name);
    setCategoryId(prod.category);
    setDetails(prod.details || '');
    setPrice(prod.price);
    setStock(prod.stock);
    setImageFile(null);
    setImagePreview(getImgSrc(getPrimaryImg(prod)));
    setShowModal(true);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!name || !categoryId || !price || !stock) {
      showToast('Please fill out all required fields. 🌸', 'error');
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('category', categoryId);
      formData.append('details', details);
      formData.append('price', price);
      formData.append('stock', stock);
      if (imageFile) {
        formData.append('img', imageFile);
      }

      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      };

      if (editingProduct) {
        // PATCH existing product details
        await api.patch(`/api/products/${editingProduct.id}/`, formData, config);
        showToast('Product updated successfully! 💕', 'success');
      } else {
        // POST a new product listing
        await api.post('/api/products/', formData, config);
        showToast('Product created successfully! ✨', 'success');
      }

      setShowModal(false);
      fetchInventory();
    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.message || 'Failed to save product.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteProduct = async (prodId) => {
    if (window.confirm('Are you sure you want to remove this product? It will be soft-deleted. 🌸')) {
      try {
        await api.delete(`/api/products/${prodId}/`);
        showToast('Product deleted.', 'success');
        fetchInventory();
      } catch (err) {
        showToast('Failed to delete product.', 'error');
      }
    }
  };

  const formatPrice = (price) => {
    return '₹' + Number(price).toLocaleString('en-IN');
  };



  return (
    <div className="my-products-page-wrapper">
      <Navbar />

      <div className="my-products-content container">
        
        {/* Header toolbar */}
        <div className="inventory-header">
          <div>
            <Link to="/profile" className="btn-back-profile-link">
              <ArrowLeft size={16} /> Back to Profile Info
            </Link>
            <h1 className="inventory-title font-serif">Manage Store Products</h1>
          </div>
          
          <button className="btn-add-product-modal btn-square" onClick={handleOpenAddModal}>
            <Plus size={16} /> ADD NEW PRODUCT
          </button>
        </div>

        {loading ? (
          <div className="spinner-container"><div className="spinner"></div></div>
        ) : products.length === 0 ? (
          <div className="empty-inventory-state">
            <Package size={48} color="var(--mahi-pink-mid)" />
            <h3>No products listed yet</h3>
            <p>Ready to sell on Mahi Store? List your first product now! 🌸</p>
            <button className="btn-add-product-modal btn-square" onClick={handleOpenAddModal}>
              CREATE LISTING
            </button>
          </div>
        ) : (
          <div className="inventory-table-container">
            <table className="inventory-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((prod) => {
                  const stockNum = Number(prod.stock);
                  return (
                    <tr key={prod.id}>
                      <td>
                        <div className="table-product-cell">
                          <img src={getImgSrc(getPrimaryImg(prod))} alt={prod.name} className="table-product-img" />
                          <div className="table-product-details">
                            <span className="name">{prod.name}</span>
                            <span className="id font-mono">ID: #{prod.id}</span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="table-category-label">{prod.category_name}</span>
                      </td>
                      <td>
                        <span className="table-price font-mono">{formatPrice(prod.price)}</span>
                      </td>
                      <td>
                        {stockNum === 0 ? (
                          <span className="badge-stock out">Out of Stock</span>
                        ) : stockNum <= 5 ? (
                          <span className="badge-stock low">Low ({stockNum})</span>
                        ) : (
                          <span className="badge-stock in">{stockNum}</span>
                        )}
                      </td>
                      <td>
                        <div className="table-actions-cell">
                          <button 
                            className="table-action-btn edit" 
                            onClick={() => handleOpenEditModal(prod)}
                            aria-label="Edit product"
                          >
                            <Edit size={16} />
                          </button>
                          <button 
                            className="table-action-btn delete" 
                            onClick={() => handleDeleteProduct(prod.id)}
                            aria-label="Delete product"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

      </div>

      {/* Add / Edit Product Modal */}
      {showModal && (
        <div className="product-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="product-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="font-serif">
                {editingProduct ? 'Edit Product Listing' : 'Add New Product Listing'}
              </h3>
              <button className="modal-close-btn" onClick={() => setShowModal(false)}>✕</button>
            </div>
            
            <form onSubmit={handleFormSubmit} className="product-modal-form">
              <div className="form-group-image-upload">
                <label>Product Image</label>
                <div className="modal-image-preview-row">
                  <div className="modal-image-preview-box">
                    {imagePreview ? (
                      <img src={imagePreview} alt="Preview" className="preview-img" />
                    ) : (
                      <div className="empty-preview font-mono">No Image</div>
                    )}
                  </div>
                  <label className="modal-upload-btn btn-square">
                    <Upload size={16} /> Choose File
                    <input 
                      type="file" 
                      accept="image/*" 
                      onChange={handleImageChange} 
                      style={{ display: 'none' }}
                    />
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label>Product Name *</label>
                <input 
                  type="text" 
                  value={name} 
                  onChange={(e) => setName(e.target.value)} 
                  required 
                  placeholder="e.g. Vintage Leather Backpack"
                />
              </div>

              <div className="form-grid-2">
                <div className="form-group">
                  <label>Category *</label>
                  <select 
                    value={categoryId} 
                    onChange={(e) => setCategoryId(e.target.value)}
                    required
                  >
                    <option value="" disabled>Select category</option>
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Price (INR) *</label>
                  <input 
                    type="number" 
                    step="0.01" 
                    value={price} 
                    onChange={(e) => setPrice(e.target.value)} 
                    required 
                    placeholder="e.g. 1299"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Stock Level *</label>
                <input 
                  type="number" 
                  value={stock} 
                  onChange={(e) => setStock(e.target.value)} 
                  required 
                  placeholder="e.g. 20"
                />
              </div>

              <div className="form-group">
                <label>Product Specifications / Details</label>
                <textarea 
                  value={details} 
                  onChange={(e) => setDetails(e.target.value)} 
                  rows={4}
                  placeholder="Tell buyers about your product materials, sizing, and details..."
                />
              </div>

              <div className="modal-buttons-row">
                <button type="submit" className="btn-modal-save btn-square" disabled={submitting}>
                  {submitting ? 'SAVING...' : editingProduct ? 'UPDATE PRODUCT 💕' : 'LIST PRODUCT 🌸'}
                </button>
                <button type="button" className="btn-modal-cancel btn-square" onClick={() => setShowModal(false)}>
                  CANCEL
                </button>
              </div>

            </form>
          </div>
        </div>
      )}

    </div>
  );
};
