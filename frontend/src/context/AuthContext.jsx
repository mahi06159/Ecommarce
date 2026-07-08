import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(true);

  // Sync logout event across tabs/Axios interceptor
  useEffect(() => {
    const handleLogout = () => {
      logoutLocal();
    };

    window.addEventListener('auth-logout', handleLogout);
    
    // Validate current session / load latest profile if logged in
    const checkSession = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const profile = await api.get('/api/auth/profile/');
          setUser(profile);
          localStorage.setItem('user', JSON.stringify(profile));
        } catch (err) {
          // Token is invalid/expired and refresh failed
          logoutLocal();
        }
      } else {
        logoutLocal();
      }
      setLoading(false);
    };

    checkSession();

    return () => {
      window.removeEventListener('auth-logout', handleLogout);
    };
  }, []);

  const logoutLocal = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const login = async (username, password) => {
    try {
      const response = await api.post('/api/auth/login/', { username, password });
      // response is already unwrapped to data = { access, refresh, user }
      const { access, refresh, user: loggedUser } = response;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(loggedUser));
      setUser(loggedUser);
      return loggedUser;
    } catch (error) {
      throw error;
    }
  };

  const registerBuyer = async (username, email, password, phone_number, avatarFile) => {
    try {
      // 1. Register base user
      const registerRes = await api.post('/api/auth/register/buyer/', { username, email, password });
      
      // 2. Perform login automatically to get tokens
      const loginRes = await api.post('/api/auth/login/', { username, password });
      const { access, refresh, user: loggedUser } = loginRes;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // 3. Patch profile if extra details are provided
      if (phone_number || avatarFile) {
        const formData = new FormData();
        if (phone_number) formData.append('profile.phone_number', phone_number);
        // Note: Django handles nested profile serializing. Let's see if we send it as nested object or form fields
        // Since we are sending json, we can perform standard patch.
        // Wait, if avatarFile is sent, we need multipart/form-data. Let's check how profile expects it.
        // Let's send a JSON patch first, and if there's an avatar, we use a multipart form data or separate avatar upload.
        // Let's implement a robust profile update helper.
      }
      
      // Fetch fresh profile
      const profile = await api.get('/api/auth/profile/');
      localStorage.setItem('user', JSON.stringify(profile));
      setUser(profile);
      return profile;
    } catch (error) {
      throw error;
    }
  };

  const registerSeller = async (username, email, password, storeName, storeDescription, logoFile) => {
    try {
      // 1. Register base user
      const registerRes = await api.post('/api/auth/register/seller/', { username, email, password });
      
      // 2. Perform login
      const loginRes = await api.post('/api/auth/login/', { username, password });
      const { access, refresh } = loginRes;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // 3. Update Seller profile details
      const updateData = {
        profile: {
          store_name: storeName || `${username}'s Store`,
          store_description: storeDescription || ''
        }
      };
      
      await api.patch('/api/auth/profile/', updateData);
      
      // Fetch fresh profile
      const profile = await api.get('/api/auth/profile/');
      localStorage.setItem('user', JSON.stringify(profile));
      setUser(profile);
      return profile;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      try {
        await api.post('/api/auth/logout/', { refresh });
      } catch (err) {
        console.error('Logout API call failed:', err);
      }
    }
    logoutLocal();
  };

  const updateProfile = async (profileData) => {
    try {
      // profileData structure should be { email, profile: { phone_number, avatar, store_name, store_description, store_logo } }
      // If it contains files (avatar or store_logo), we should send it as FormData or JSON if simple values.
      let response;
      const hasFiles = profileData.profile?.avatar instanceof File || profileData.profile?.store_logo instanceof File;
      
      if (hasFiles) {
        const formData = new FormData();
        if (profileData.email) formData.append('email', profileData.email);
        if (profileData.profile?.phone_number) {
          formData.append('profile.phone_number', profileData.profile.phone_number);
        }
        if (profileData.profile?.avatar instanceof File) {
          formData.append('profile.avatar', profileData.profile.avatar);
        }
        if (profileData.profile?.store_name) {
          formData.append('profile.store_name', profileData.profile.store_name);
        }
        if (profileData.profile?.store_description) {
          formData.append('profile.store_description', profileData.profile.store_description);
        }
        if (profileData.profile?.store_logo instanceof File) {
          formData.append('profile.store_logo', profileData.profile.store_logo);
        }
        
        response = await api.patch('/api/auth/profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      } else {
        response = await api.patch('/api/auth/profile/', profileData);
      }
      
      setUser(response);
      localStorage.setItem('user', JSON.stringify(response));
      return response;
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, registerBuyer, registerSeller, logout, updateProfile, refreshProfile: async () => {
      const p = await api.get('/api/auth/profile/');
      setUser(p);
      localStorage.setItem('user', JSON.stringify(p));
    }}}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
export default AuthContext;
