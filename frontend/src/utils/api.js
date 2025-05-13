import axios from 'axios';
const API_URL = 'http://localhost:5000';
const RSS2JSON_API_KEY = 'qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz';
const VIDEO_API = `https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id=UC8butISFwT-Wl7EV0hUK0BQ&api_key=${RSS2JSON_API_KEY}`;
const ARTICLE_API = 'https://dev.to/api/articles';
const AUDIO_API = `https://api.rss2json.com/v1/api.json?rss_url=https://feeds.simplecast.com/4r7G7Z8a&api_key=${RSS2JSON_API_KEY}`;
const LISTENNOTES_API_KEY = '7414408b9ba6479aba86eb06545f7a98';
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
const CORS_PROXY = 'https://cors-anywhere.herokuapp.com/';
const useCorsProxy = (url) => `${CORS_PROXY}${url}`;
export const login = (email, password) =>
  api.post('/auth/login', { email, password });
export const register = (name, email, phone, role, password) =>
  api.post('/auth/register', { name, email, phone, role, password })
    .then(response => response)
    .catch(error => {
      if (error.response && error.response.status === 409) {
        throw new Error(error.response.data.error || 'Registration conflict');
      }
      throw error;
    });
export const getUserProfile = () =>
  api.get('/auth/me');
export const getNotifications = () =>
  api.get('/notifications');
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
    const response = await axios.get(VIDEO_API);
    return {
      data: {
        items: response.data.items.map(item => ({
          guid: item.guid,
          title: item.title,
          link: item.link,
          pubDate: item.pubDate,
        })),
      },
    };
  } catch (error) {
    console.error('Error fetching videos:', error);
    if (error.response?.status === 403 || error.response?.status === 422) {
      try {
        const response = await axios.get(useCorsProxy(VIDEO_API));
        return {
          data: {
            items: response.data.items.map(item => ({
              guid: item.guid,
              title: item.title,
              link: item.link,
              pubDate: item.pubDate,
            })),
          },
        };
      } catch (proxyError) {
        console.error('Error with CORS proxy for videos:', proxyError);
        throw proxyError;
      }
    }
    throw error;
  }
};
export const getArticles = async () => {
  try {
    const response = await axios.get(ARTICLE_API);
    return {
      data: response.data.map(article => ({
        id: article.id,
        title: article.title,
        url: article.url,
        published_at: article.published_at,
      })),
    };
  } catch (error) {
    console.error('Error fetching articles:', error);
    throw error;
  }
};
export const getArticleById = async (articleId) => {
  try {
    const response = await axios.get(`https://dev.to/api/articles/${articleId}`);
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching article by ID:', error);
    throw error;
  }
};
export const getArticleComments = async (articleId) => {
  try {
    const response = await axios.get(`https://dev.to/api/comments?a_id=${articleId}`);
    return { data: response.data };
  } catch (error) {
    console.error('Error fetching article comments:', error);
    throw error;
  }
};
export const getAudio = async () => {
  try {
    const response = await axios.get(AUDIO_API);
    return {
      data: response.data.items.map(item => ({
        title: item.title,
        category: 'Podcast',
        date: item.pubDate,
        audio_url: item.enclosure.url || '',
      })),
    };
  } catch (error) {
    console.error('Error fetching audio:', error);
    throw error;
  }
};
export default api;