import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:12345';

// Preguntas del formulario conversacional
const PREGUNTAS = [
  {
    id: 'tipo_contrato',
    pregunta: '¿Qué tipo de contrato tienes actualmente?',
    tipo: 'select',
    opciones: [
      { value: 'prestacion_servicios', label: 'Prestación de Servicios' },
      { value: 'obra_labor', label: 'Obra o Labor' },
      { value: 'termino_fijo', label: 'Término Fijo' },
      { value: 'termino_indefinido', label: 'Término Indefinido' },
      { value: 'verbal', label: 'Verbal (Sin contrato escrito)' },
      { value: 'otro', label: 'Otro' }
    ]
  },
  {
    id: 'funciones',
    pregunta: '¿Qué funciones realizas en tu trabajo? Describe tus actividades principales',
    tipo: 'textarea',
    placeholder: 'Ej: Desarrollo software, atiendo clientes, gestiono proyectos...'
  },
  {
    id: 'tipo_salario',
    pregunta: '¿Cómo te pagan por tu trabajo?',
    tipo: 'select',
    opciones: [
      { value: 'fijo', label: 'Salario Fijo Mensual' },
      { value: 'por_tarea', label: 'Por Tarea o Proyecto' },
      { value: 'mixto', label: 'Mixto (Fijo + Variable)' },
      { value: 'otro', label: 'Otro' }
    ]
  },
  {
    id: 'salario_aproximado',
    pregunta: '¿Cuál es tu remuneración mensual aproximada?',
    tipo: 'number',
    placeholder: 'Ej: 2500000'
  },
  {
    id: 'tiene_supervisor',
    pregunta: '¿Tienes un supervisor o jefe directo?',
    tipo: 'boolean'
  },
  {
    id: 'supervisor_cargo',
    pregunta: '¿Cuál es el cargo de tu supervisor?',
    tipo: 'text',
    placeholder: 'Ej: Gerente de Proyecto',
    dependeDe: { campo: 'tiene_supervisor', valor: true }
  },
  {
    id: 'tiempo_trabajado_meses',
    pregunta: '¿Cuántos meses llevas trabajando en esta posición?',
    tipo: 'number',
    placeholder: 'Ej: 12'
  },
  {
    id: 'horario_fijo',
    pregunta: '¿Tienes un horario fijo de trabajo?',
    tipo: 'boolean'
  },
  {
    id: 'herramientas_propias',
    pregunta: '¿Utilizas tus propias herramientas de trabajo?',
    tipo: 'boolean'
  },
  {
    id: 'exclusividad',
    pregunta: '¿Tienes exclusividad con este empleador?',
    tipo: 'boolean'
  }
];

const ContratoRealidadForm = () => {
  const [preguntaActual, setPreguntaActual] = useState(0);
  const [respuestas, setRespuestas] = useState({});
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);

  const handleRespuesta = (valor) => {
    setRespuestas(prev => ({
      ...prev,
      [PREGUNTAS[preguntaActual].id]: valor
    }));

    if (preguntaActual < PREGUNTAS.length - 1) {
      // Si la siguiente pregunta depende de una respuesta, verificar
      const siguientePregunta = PREGUNTAS[preguntaActual + 1];
      if (siguientePregunta.dependeDe) {
        const { campo, valor: valorRequerido } = siguientePregunta.dependeDe;
        if (respuestas[campo] !== valorRequerido) {
          // Saltar la pregunta dependiente
          setPreguntaActual(preguntaActual + 2);
          return;
        }
      }
      setPreguntaActual(preguntaActual + 1);
    } else {
      enviarFormulario();
    }
  };

  const enviarFormulario = async () => {
    setEnviando(true);
    setError(null);

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/contrato-realidad/analizar`,
        respuestas
      );
      setResultado(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Ha ocurrido un error al analizar tu caso. Por favor, intenta nuevamente.'
      );
    } finally {
      setEnviando(false);
    }
  };

  const renderPregunta = () => {
    const pregunta = PREGUNTAS[preguntaActual];
    
    switch (pregunta.tipo) {
      case 'select':
        return (
          <select
            className="w-full p-2 border rounded-md"
            onChange={(e) => handleRespuesta(e.target.value)}
            value={respuestas[pregunta.id] || ''}
          >
            <option value="">Selecciona una opción</option>
            {pregunta.opciones.map(opcion => (
              <option key={opcion.value} value={opcion.value}>
                {opcion.label}
              </option>
            ))}
          </select>
        );
        
      case 'textarea':
        return (
          <textarea
            className="w-full p-2 border rounded-md"
            placeholder={pregunta.placeholder}
            value={respuestas[pregunta.id] || ''}
            onChange={(e) => handleRespuesta(e.target.value)}
            rows={4}
          />
        );
        
      case 'number':
        return (
          <input
            type="number"
            className="w-full p-2 border rounded-md"
            placeholder={pregunta.placeholder}
            value={respuestas[pregunta.id] || ''}
            onChange={(e) => handleRespuesta(Number(e.target.value))}
          />
        );
        
      case 'boolean':
        return (
          <div className="flex gap-4">
            <button
              className={`px-4 py-2 rounded-md ${
                respuestas[pregunta.id] === true
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200'
              }`}
              onClick={() => handleRespuesta(true)}
            >
              Sí
            </button>
            <button
              className={`px-4 py-2 rounded-md ${
                respuestas[pregunta.id] === false
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200'
              }`}
              onClick={() => handleRespuesta(false)}
            >
              No
            </button>
          </div>
        );
        
      case 'text':
      default:
        return (
          <input
            type="text"
            className="w-full p-2 border rounded-md"
            placeholder={pregunta.placeholder}
            value={respuestas[pregunta.id] || ''}
            onChange={(e) => handleRespuesta(e.target.value)}
          />
        );
    }
  };

  const renderResultado = () => {
    if (!resultado) return null;

    const getNivelRiesgoColor = () => {
      switch (resultado.nivel_riesgo) {
        case 'alto':
          return 'bg-red-100 border-red-500 text-red-700';
        case 'medio':
          return 'bg-yellow-100 border-yellow-500 text-yellow-700';
        case 'bajo':
          return 'bg-green-100 border-green-500 text-green-700';
        default:
          return 'bg-gray-100 border-gray-500 text-gray-700';
      }
    };

    return (
      <div className="mt-8 space-y-6">
        <div className={`p-4 border-l-4 rounded-r-md ${getNivelRiesgoColor()}`}>
          <h3 className="font-medium">Resultado del Análisis</h3>
          <p className="mt-2">{resultado.mensaje_resumen}</p>
        </div>

        {resultado.factores_riesgo.length > 0 && (
          <div className="bg-white p-4 rounded-md shadow">
            <h3 className="font-medium mb-2">Factores de Riesgo Identificados:</h3>
            <ul className="list-disc pl-5 space-y-1">
              {resultado.factores_riesgo.map((factor, index) => (
                <li key={index}>{factor}</li>
              ))}
            </ul>
          </div>
        )}

        {resultado.recomendaciones.length > 0 && (
          <div className="bg-white p-4 rounded-md shadow">
            <h3 className="font-medium mb-2">Recomendaciones:</h3>
            <ul className="list-disc pl-5 space-y-1">
              {resultado.recomendaciones.map((recomendacion, index) => (
                <li key={index}>{recomendacion}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4">
          <button
            onClick={() => {
              setPreguntaActual(0);
              setRespuestas({});
              setResultado(null);
            }}
            className="text-blue-600 hover:text-blue-800"
          >
            Realizar nuevo análisis
          </button>
        </div>
      </div>
    );
  };

  if (error) {
    return (
      <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded">
        <p className="font-medium">Error</p>
        <p>{error}</p>
        <button
          onClick={() => {
            setError(null);
            setPreguntaActual(0);
          }}
          className="mt-2 text-red-600 hover:text-red-800"
        >
          Intentar nuevamente
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {!resultado ? (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Análisis de Contrato Realidad</h2>
            <p className="text-gray-600">
              Responde las siguientes preguntas para evaluar tu situación laboral
            </p>
          </div>

          <div className="mb-6">
            <p className="font-medium mb-4">{PREGUNTAS[preguntaActual].pregunta}</p>
            {renderPregunta()}
          </div>

          <div className="flex justify-between items-center">
            {preguntaActual > 0 && (
              <button
                onClick={() => setPreguntaActual(preguntaActual - 1)}
                className="text-blue-600 hover:text-blue-800"
              >
                Anterior
              </button>
            )}
            <div className="text-gray-500">
              Pregunta {preguntaActual + 1} de {PREGUNTAS.length}
            </div>
          </div>
        </div>
      ) : (
        renderResultado()
      )}
    </div>
  );
};

export default ContratoRealidadForm; 