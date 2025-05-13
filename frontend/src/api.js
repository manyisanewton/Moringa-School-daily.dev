import axios from 'axios';

// Use environment variable for backend URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');
        const { data } = await axios.post(`${API_URL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` },
          withCredentials: true,
        });
        localStorage.setItem('access_token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    } else if (error.response?.status === 409) {
      if (error.response.data.suggestion === 'login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  return response;
};

export const register = async (name, email, phone, role, password) => {
  const response = await api.post('/auth/register', { name, email, phone, role, password });
  return response;
};

export const getUserProfile = async () => {
  const response = await api.get('/auth/me');
  return response;
};

export const requestPasswordReset = async (email) => {
  const response = await api.post('/auth/request-password-reset', { identifier: email });
  return response;
};

export const verifyResetCode = async (email, code) => {
  const response = await api.post('/auth/verify-reset-code', { email, code });
  return response;
};

export const resetPassword = async (code, new_password, confirm_password) => {
  const response = await api.post('/auth/reset-password', { code, new_password, confirm_password });
  return response;
};

export const getNotifications = async () => {
  const response = await api.get('/notifications');
  return response;
};

export const getContent = async (page = 1, perPage = 10) => {
  try {
    const response = await api.get(`/content?page=${page}&per_page=${perPage}`);
    return response.data.items;
  } catch (error) {
    console.error('Error fetching content:', error);
    throw error;
  }
};

export const getUserContent = async (page = 1, perPage = 10) => {
  try {
    const userId = localStorage.getItem('user_id');
    if (!userId) throw new Error('User ID not found in localStorage');
    const response = await api.get(`/content?user_id=${userId}&page=${page}&per_page=${perPage}`);
    return response.data.items;
  } catch (error) {
    console.error('Error fetching user content:', error);
    throw error;
  }
};

export const getComments = async (contentId) => {
  try {
    const response = await api.get(`/content/${contentId}/comments`);
    return response.data;
  } catch (error) {
    console.error('Error fetching comments:', error);
    throw error;
  }
};

export const getVideos = async () => {
  try {
    const response = await api.get('/proxy/youtube-videos');
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching videos:', error);
    throw error;
  }
};

export const getArticles = async () => {
  try {
    const response = await api.get('/proxy/devto-articles');
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching articles:', error);
    throw error;
  }
};

export const getArticleById = async (articleId) => {
  try {
    const response = await api.get(`/proxy/devto-article/${articleId}`);
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching article by ID:', error);
    throw error;
  }
};

export const getArticleComments = async (articleId) => {
  try {
    const response = await api.get('/proxy/devto-comments', {
      params: { a_id: articleId }
    });
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching article comments:', error);
    throw error;
  }
};

export const getAudio = async () => {
  try {
    const response = await api.get('/proxy/podcasts');
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching audio:', error);
    throw error;
  }
};

export default api;