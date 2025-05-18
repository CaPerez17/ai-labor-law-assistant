import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Importar la configuración central
import { BACKEND_URL, API_PREFIX } from './config.js'

// Log completo de variables de entorno para debugging
console.log('VITE_BACKEND_URL →', import.meta.env.VITE_BACKEND_URL);
console.log('BACKEND_URL configurado →', BACKEND_URL);
console.log('API_PREFIX →', API_PREFIX);
console.log('URL completa API →', `${BACKEND_URL}${API_PREFIX}`);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
) 