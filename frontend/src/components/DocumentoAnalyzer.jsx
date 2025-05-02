import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:12345';

const DocumentoAnalyzer = () => {
  const [file, setFile] = useState(null);
  const [analizando, setAnalizando] = useState(false);
  const [error, setError] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [progreso, setProgreso] = useState(0);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      // Validar tipo de archivo
      const extension = selectedFile.name.split('.').pop().toLowerCase();
      if (!['pdf', 'docx', 'txt'].includes(extension)) {
        setError('Tipo de archivo no soportado. Use PDF, DOCX o TXT.');
        return;
      }
      
      // Validar tamaño (5MB)
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError('El archivo excede el tamaño máximo permitido (5MB).');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };

  const analizarDocumento = async () => {
    if (!file) {
      setError('Por favor, seleccione un archivo.');
      return;
    }

    setAnalizando(true);
    setError(null);
    setProgreso(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simular progreso
      const progressInterval = setInterval(() => {
        setProgreso(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 500);

      const response = await axios.post(
        `${BACKEND_URL}/api/documento/analizar`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      clearInterval(progressInterval);
      setProgreso(100);
      setResultado(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Ha ocurrido un error al analizar el documento. Por favor, intente nuevamente.'
      );
    } finally {
      setAnalizando(false);
    }
  };

  const renderRiesgo = (riesgo) => {
    const colores = {
      alto: 'red',
      medio: 'orange',
      bajo: 'yellow'
    };

    return (
      <div key={riesgo.descripcion} className="mb-4">
        <div className={`bg-${colores[riesgo.nivel]}-100 border-l-4 border-${colores[riesgo.nivel]}-500 p-4 rounded`}>
          <h4 className="font-medium text-lg mb-2">{riesgo.descripcion}</h4>
          <p className="text-gray-700 mb-2">
            <span className="font-medium">Nivel de riesgo:</span> {riesgo.nivel.toUpperCase()}
          </p>
          <p className="text-gray-700 mb-2">
            <span className="font-medium">Cláusulas relacionadas:</span>
          </p>
          <ul className="list-disc list-inside mb-2">
            {riesgo.clausulas_relacionadas.map((clausula, index) => (
              <li key={index} className="text-gray-600">{clausula}</li>
            ))}
          </ul>
          <p className="text-gray-700">
            <span className="font-medium">Recomendación:</span> {riesgo.recomendacion}
          </p>
        </div>
      </div>
    );
  };

  const renderClausula = (clausula) => {
    return (
      <div key={clausula.titulo} className="mb-4">
        <div className="bg-white p-4 rounded shadow">
          <h4 className="font-medium text-lg mb-2">{clausula.titulo}</h4>
          <p className="text-gray-700 mb-2">{clausula.contenido}</p>
          {clausula.riesgo && (
            <div className="mt-2">
              <span className="font-medium">Riesgo:</span> {clausula.riesgo.toUpperCase()}
              {clausula.razon_riesgo && (
                <p className="text-sm text-gray-600 mt-1">{clausula.razon_riesgo}</p>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderResultado = () => {
    if (!resultado) return null;

    return (
      <div className="mt-8 space-y-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">Resumen del Análisis</h3>
          <p className="text-gray-700 mb-4">{resultado.resumen_general}</p>
          
          {resultado.tipo_documento && (
            <p className="text-gray-700 mb-2">
              <span className="font-medium">Tipo de documento:</span> {resultado.tipo_documento}
            </p>
          )}
          
          {resultado.fecha_documento && (
            <p className="text-gray-700 mb-4">
              <span className="font-medium">Fecha del documento:</span> {resultado.fecha_documento}
            </p>
          )}
        </div>

        {resultado.riesgos_detectados.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-4">Riesgos Detectados</h3>
            {resultado.riesgos_detectados.map(renderRiesgo)}
          </div>
        )}

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">Cláusulas Destacadas</h3>
          {resultado.clausulas_destacadas.map(renderClausula)}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">Recomendaciones</h3>
          <ul className="list-disc list-inside space-y-2">
            {resultado.recomendaciones.map((recomendacion, index) => (
              <li key={index} className="text-gray-700">{recomendacion}</li>
            ))}
          </ul>
        </div>

        <div className="mt-4">
          <button
            onClick={() => {
              setFile(null);
              setResultado(null);
              setProgreso(0);
            }}
            className="text-blue-600 hover:text-blue-800"
          >
            Analizar otro documento
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Análisis de Documentos Legales</h2>
          <p className="text-gray-600">
            Sube un documento legal (PDF, DOCX o TXT) para analizar su contenido y detectar posibles riesgos.
          </p>
        </div>

        {!resultado && (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Seleccionar archivo
              </label>
              {file && (
                <p className="mt-2 text-gray-600">
                  Archivo seleccionado: {file.name}
                </p>
              )}
            </div>

            {error && (
              <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded">
                <p>{error}</p>
              </div>
            )}

            {file && !error && (
              <button
                onClick={analizarDocumento}
                disabled={analizando}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-blue-300"
              >
                {analizando ? 'Analizando...' : 'Analizar documento'}
              </button>
            )}

            {analizando && (
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${progreso}%` }}
                ></div>
              </div>
            )}
          </div>
        )}

        {renderResultado()}
      </div>
    </div>
  );
};

export default DocumentoAnalyzer; 