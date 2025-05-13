import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Importar la configuración de emergencia primero
import './config_override.js'

// Asegurarse de que las variables de entorno estén correctamente configuradas
const backendUrl = import.meta.env.VITE_BACKEND_URL || window.VITE_BACKEND_URL || 'https://legalassista.onrender.com'
console.log('[main] URL del backend (antes de renderizar):', backendUrl)

// Intentar forzar la URL correcta antes de renderizar
if (window.forceCorrectBackendURL) {
  window.forceCorrectBackendURL()
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
) 