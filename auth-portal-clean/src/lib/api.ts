import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/proxy';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const cfg = err.config;
    const isNetworkError = !err.response || err.code === 'ECONNABORTED' || err.code === 'ERR_NETWORK';
    
    if (isNetworkError && (!cfg._retryCount || cfg._retryCount < 10)) {
      cfg._retryCount = (cfg._retryCount || 0) + 1;
      console.log(`Retrying (${cfg._retryCount}/10) due to cold start...`);
      await new Promise((r) => setTimeout(r, 3000));
      return api(cfg);
    }
    throw err;
  }
);

export const warmup = () => api.get('/api/health').catch(() => {});
