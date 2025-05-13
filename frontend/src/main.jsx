import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Importar la configuración con URLs fijas
import { BACKEND_URL } from './config_override.js'

// Log simple para debugging
console.log('[main] URL del backend:', BACKEND_URL)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
) 