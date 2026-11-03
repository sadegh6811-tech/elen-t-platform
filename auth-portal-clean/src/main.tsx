import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { warmup } from './lib/api'

// Warmup backend on load to prevent cold start errors
warmup();

// Register Service Worker for PWA
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(console.error);
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
