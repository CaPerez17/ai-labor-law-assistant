import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:12345';

// Preguntas del formulario conversacional
const PREGUNTAS = [
  {
    id: 'tipo_contrato',
    pregunta: '¿Qué tipo de contrato tenías?',
    tipo: 'select',
    opciones: [
      { value: 'termino_fijo', label: 'Término Fijo' },
      { value: 'termino_indefinido', label: 'Término Indefinido' },
      { value: 'obra_labor', label: 'Obra o Labor' }
    ]
  },
  {
    id: 'salario_mensual',
    pregunta: '¿Cuál era tu salario mensual base?',
    tipo: 'number',
    placeholder: 'Ej: 2500000'
  },
  {
    id: 'tiempo_trabajado_meses',
    pregunta: '¿Cuántos meses trabajaste en total?',
    tipo: 'number',
    placeholder: 'Ej: 24'
  },
  {
    id: 'causa_despido',
    pregunta: '¿Cuál fue la razón de la terminación del contrato?',
    tipo: 'select',
    opciones: [
      { value: 'sin_justa_causa', label: 'Despido sin justa causa' },
      { value: 'justa_causa', label: 'Despido con justa causa' },
      { value: 'terminacion_contrato', label: 'Terminación del contrato' },
      { value: 'renuncia', label: 'Renuncia voluntaria' }
    ]
  },
  {
    id: 'meses_faltantes',
    pregunta: '¿Cuántos meses faltaban para terminar el contrato?',
    tipo: 'number',
    placeholder: 'Ej: 6',
    dependeDe: { campo: 'tipo_contrato', valor: 'termino_fijo' }
  },
  {
    id: 'obra_terminada',
    pregunta: '¿La obra o labor para la que fuiste contratado ya terminó?',
    tipo: 'boolean',
    dependeDe: { campo: 'tipo_contrato', valor: 'obra_labor' }
  },
  {
    id: 'auxilio_transporte',
    pregunta: '¿Recibías auxilio de transporte?',
    tipo: 'boolean'
  },
  {
    id: 'comisiones_promedio',
    pregunta: '¿Cuál era el promedio mensual de comisiones que recibías? (Si no recibías, deja 0)',
    tipo: 'number',
    placeholder: 'Ej: 500000'
  },
  {
    id: 'horas_extra_promedio',
    pregunta: '¿Cuál era el valor promedio mensual de horas extra? (Si no tenías, deja 0)',
    tipo: 'number',
    placeholder: 'Ej: 200000'
  }
];

const IndemnizacionForm = () => {
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
      // Verificar si la siguiente pregunta depende de una respuesta
      let siguientePregunta = preguntaActual + 1;
      while (siguientePregunta < PREGUNTAS.length) {
        const pregunta = PREGUNTAS[siguientePregunta];
        if (pregunta.dependeDe) {
          const { campo, valor: valorRequerido } = pregunta.dependeDe;
          if (respuestas[campo] !== valorRequerido) {
            siguientePregunta++;
            continue;
          }
        }
        break;
      }
      
      if (siguientePregunta < PREGUNTAS.length) {
        setPreguntaActual(siguientePregunta);
      } else {
        enviarFormulario();
      }
    } else {
      enviarFormulario();
    }
  };

  const enviarFormulario = async () => {
    setEnviando(true);
    setError(null);

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/indemnizacion/calcular`,
        respuestas
      );
      setResultado(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Ha ocurrido un error al calcular la indemnización. Por favor, intenta nuevamente.'
      );
    } finally {
      setEnviando(false);
    }
  };

  const formatearDinero = (valor) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(valor);
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

    return (
      <div className="mt-8 space-y-6">
        <div className={`p-4 border-l-4 rounded-r-md ${
          resultado.tiene_derecho ? 'bg-blue-100 border-blue-500' : 'bg-gray-100 border-gray-500'
        }`}>
          <h3 className="font-medium">Resultado del Cálculo</h3>
          <p className="mt-2">{resultado.mensaje_resumen}</p>
        </div>

        {resultado.tiene_derecho && (
          <div className="bg-white p-4 rounded-md shadow">
            <h3 className="font-medium mb-2">Detalle del Cálculo:</h3>
            <div className="space-y-2">
              <p>Salario base: {formatearDinero(resultado.salario_base)}</p>
              {resultado.detalle_calculo.map((detalle, index) => (
                <div key={index} className="pl-4 border-l-2 border-gray-200">
                  <p className="font-medium">{detalle.concepto}</p>
                  <p className="text-sm text-gray-600">{detalle.explicacion}</p>
                  <p className="text-right font-medium">
                    {formatearDinero(detalle.subtotal)}
                  </p>
                </div>
              ))}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-lg font-bold flex justify-between">
                  <span>Total Indemnización:</span>
                  <span>{formatearDinero(resultado.indemnizacion_total)}</span>
                </p>
              </div>
            </div>
          </div>
        )}

        {resultado.factores_considerados.length > 0 && (
          <div className="bg-white p-4 rounded-md shadow">
            <h3 className="font-medium mb-2">Factores Considerados:</h3>
            <ul className="list-disc pl-5 space-y-1">
              {resultado.factores_considerados.map((factor, index) => (
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
            Realizar nuevo cálculo
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
            <h2 className="text-xl font-semibold mb-2">Cálculo de Indemnización por Despido</h2>
            <p className="text-gray-600">
              Responde las siguientes preguntas para calcular tu indemnización aproximada
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

export default IndemnizacionForm; 