import React, { useState } from 'react';
import axios from 'axios';
import PreguntaForm from './PreguntaForm';
import RespuestaLegal from './RespuestaLegal';

const LegalAssistant = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // URL del backend
  const BACKEND_URL = 'http://localhost:12345';
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResponse(null); // Limpiar respuesta anterior al enviar nueva consulta
    
    try {
      // Usar la URL completa y asegurar que el cuerpo tenga el campo correcto
      const result = await axios.post(`${BACKEND_URL}/api/ask/`, { 
        query: query 
      });
      
      console.log('Respuesta del servidor:', result.data);
      
      // Pequeño retraso para que la animación sea visible
      setTimeout(() => {
        setResponse(result.data);
        setLoading(false);
      }, 300);
    } catch (err) {
      console.error('Error al enviar consulta:', err);
      setError(
        err.response?.data?.detail || 
        'Ha ocurrido un error al procesar tu consulta. Por favor, intenta nuevamente.'
      );
      setLoading(false);
    }
  };

  const handleContactRequest = () => {
    window.location.href = 'mailto:soporte@ailaborlaw.com?subject=Solicitud de revisión profesional';
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Consulta Legal Laboral</h2>
        
        <PreguntaForm 
          query={query}
          setQuery={setQuery}
          loading={loading}
          handleSubmit={handleSubmit}
        />

        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4 rounded animate-fade-in">
            <p className="font-medium">Error</p>
            <p>{error}</p>
          </div>
        )}

        {loading && !response && (
          <div className="flex justify-center items-center py-12 animate-pulse">
            <div className="text-center">
              <svg className="inline-block animate-spin h-8 w-8 text-blue-600 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-gray-600">Analizando tu consulta legal...</p>
            </div>
          </div>
        )}

        <RespuestaLegal 
          respuesta={response} 
          onContactRequest={handleContactRequest} 
        />
        
      </div>
    </div>
  );
};

export default LegalAssistant; 