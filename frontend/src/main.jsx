import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Importar la configuración central
import { BACKEND_URL, API_PREFIX } from './config.js'

// Log completo de variables de entorno para debugging
console.log('–––– CONFIG SANITIZED ––––');
console.log('RAW VITE_BACKEND_URL →', import.meta.env.VITE_BACKEND_URL);
console.log('BACKEND_URL →', BACKEND_URL);
console.log('API_PREFIX →', API_PREFIX);
console.log('FULL LOGIN URL →', `${BACKEND_URL}${API_PREFIX}/auth/login`);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
) 