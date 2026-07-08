import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export const CartProvider = ({ children }) => {
  const { user } = useAuth();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isCartOpen, setIsCartOpen] = useState(false);

  // Helper to get cart ID from storage
  const getCachedCartId = () => localStorage.getItem('cart_id');
  const cacheCartId = (id) => localStorage.setItem('cart_id', id);

  // Load cart on init or user changes
  const fetchCart = async () => {
    setLoading(true);
    try {
      const cartId = getCachedCartId();
      let url = '/api/cart/';
      if (cartId) {
        url += `?cart_id=${cartId}`;
      }
      
      const data = await api.get(url);
      setCart(data);
      if (data && data.id) {
        cacheCartId(data.id);
      }
    } catch (err) {
      console.error('Failed to fetch cart:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, [user]);

  const addToCart = async (productId, quantity = 1) => {
    try {
      const cartId = getCachedCartId();
      const payload = { product: productId, quantity };
      if (cartId) {
        payload.cart_id = cartId;
      }
      
      const updatedCart = await api.post('/api/cart/', payload);
      setCart(updatedCart);
      if (updatedCart && updatedCart.id) {
        cacheCartId(updatedCart.id);
      }
      setIsCartOpen(true); // Automatically open cart drawer on add
      return updatedCart;
    } catch (err) {
      console.error('Failed to add item to cart:', err);
      throw err;
    }
  };

  const updateCartItem = async (cartItemId, quantity) => {
    try {
      const updatedCart = await api.patch(`/api/cart/items/${cartItemId}/`, { quantity });
      setCart(updatedCart);
      return updatedCart;
    } catch (err) {
      console.error('Failed to update cart item:', err);
      throw err;
    }
  };

  const removeFromCart = async (cartItemId) => {
    try {
      const updatedCart = await api.delete(`/api/cart/items/${cartItemId}/`);
      setCart(updatedCart);
      return updatedCart;
    } catch (err) {
      console.error('Failed to remove cart item:', err);
      throw err;
    }
  };

  const clearCart = () => {
    // When order is placed, backend automatically empties cart items.
    // We just refetch cart to get it empty.
    fetchCart();
  };

  // Computations
  const cartItems = cart?.items || [];
  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  const cartTotal = Number(cart?.total_price || 0);

  return (
    <CartContext.Provider value={{
      cart,
      cartItems,
      cartCount,
      cartTotal,
      loading,
      isCartOpen,
      setIsCartOpen,
      addToCart,
      updateCartItem,
      removeFromCart,
      clearCart,
      refetchCart: fetchCart,
    }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);
export default CartContext;
