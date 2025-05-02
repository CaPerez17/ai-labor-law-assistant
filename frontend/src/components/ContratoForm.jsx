import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:12345';

// Preguntas del formulario conversacional
const PREGUNTAS = [
  {
    id: 'tipo_contrato',
    pregunta: '¿Qué tipo de contrato deseas generar?',
    tipo: 'select',
    opciones: [
      { value: 'termino_fijo', label: 'Término Fijo' },
      { value: 'termino_indefinido', label: 'Término Indefinido' },
      { value: 'obra_labor', label: 'Obra o Labor' },
      { value: 'domestico', label: 'Servicio Doméstico' }
    ]
  },
  {
    id: 'nombre_empleador',
    pregunta: 'Nombre completo del empleador:',
    tipo: 'text',
    placeholder: 'Ej: Empresa S.A.S. o Juan Pérez'
  },
  {
    id: 'nit_empleador',
    pregunta: 'NIT o documento del empleador:',
    tipo: 'text',
    placeholder: 'Ej: 900.123.456-7'
  },
  {
    id: 'direccion_empleador',
    pregunta: 'Dirección del empleador:',
    tipo: 'text',
    placeholder: 'Ej: Calle 123 # 45-67, Bogotá'
  },
  {
    id: 'nombre_empleado',
    pregunta: 'Nombre completo del empleado:',
    tipo: 'text',
    placeholder: 'Ej: María Rodríguez'
  },
  {
    id: 'documento_empleado',
    pregunta: 'Número de documento del empleado:',
    tipo: 'text',
    placeholder: 'Ej: 1234567890'
  },
  {
    id: 'cargo',
    pregunta: 'Cargo o posición a desempeñar:',
    tipo: 'text',
    placeholder: 'Ej: Asistente Administrativo'
  },
  {
    id: 'salario',
    pregunta: 'Salario mensual (en pesos colombianos):',
    tipo: 'number',
    placeholder: 'Ej: 2500000'
  },
  {
    id: 'duracion_meses',
    pregunta: 'Duración del contrato en meses:',
    tipo: 'number',
    placeholder: 'Ej: 12',
    dependeDe: { campo: 'tipo_contrato', valor: 'termino_fijo' }
  },
  {
    id: 'modalidad_trabajo',
    pregunta: '¿Cuál será la modalidad de trabajo?',
    tipo: 'select',
    opciones: [
      { value: 'presencial', label: 'Presencial' },
      { value: 'remoto', label: 'Remoto' },
      { value: 'hibrido', label: 'Híbrido' }
    ]
  },
  {
    id: 'fecha_inicio',
    pregunta: 'Fecha de inicio del contrato:',
    tipo: 'date'
  },
  {
    id: 'lugar_trabajo',
    pregunta: 'Ciudad o municipio donde se desarrollará el trabajo:',
    tipo: 'text',
    placeholder: 'Ej: Bogotá'
  },
  {
    id: 'funciones_principales',
    pregunta: 'Describe las funciones principales del cargo:',
    tipo: 'textarea',
    placeholder: 'Ej: 1. Gestión de documentos\n2. Atención al cliente\n3. Manejo de agenda'
  },
  {
    id: 'horario_trabajo',
    pregunta: 'Horario de trabajo acordado:',
    tipo: 'text',
    placeholder: 'Ej: Lunes a viernes de 8:00 AM a 5:00 PM'
  }
];

const ContratoForm = () => {
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
      // Convertir la fecha a formato ISO
      const datosFormateados = {
        ...respuestas,
        fecha_inicio: new Date(respuestas.fecha_inicio).toISOString().split('T')[0]
      };

      const response = await axios.post(
        `${BACKEND_URL}/api/contrato/generar`,
        datosFormateados
      );
      setResultado(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Ha ocurrido un error al generar el contrato. Por favor, intenta nuevamente.'
      );
    } finally {
      setEnviando(false);
    }
  };

  const descargarContrato = () => {
    const blob = new Blob([resultado.contrato_generado], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = resultado.nombre_archivo;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const copiarContrato = () => {
    navigator.clipboard.writeText(resultado.contrato_generado)
      .then(() => alert('Contrato copiado al portapapeles'))
      .catch(() => alert('Error al copiar el contrato'));
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
        
      case 'date':
        return (
          <input
            type="date"
            className="w-full p-2 border rounded-md"
            value={respuestas[pregunta.id] || ''}
            onChange={(e) => handleRespuesta(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
          />
        );
        
      case 'textarea':
        return (
          <textarea
            className="w-full p-2 border rounded-md h-32"
            placeholder={pregunta.placeholder}
            value={respuestas[pregunta.id] || ''}
            onChange={(e) => handleRespuesta(e.target.value)}
          />
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
        {resultado.advertencia && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 rounded">
            <p className="text-yellow-700">{resultado.advertencia}</p>
          </div>
        )}

        <div className="bg-white p-4 rounded-md shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Contrato Generado</h3>
            <div className="space-x-2">
              <button
                onClick={copiarContrato}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded"
              >
                Copiar
              </button>
              <button
                onClick={descargarContrato}
                className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded"
              >
                Descargar
              </button>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded font-mono text-sm whitespace-pre-wrap">
            {resultado.contrato_generado}
          </div>
        </div>

        <div className="mt-4">
          <button
            onClick={() => {
              setPreguntaActual(0);
              setRespuestas({});
              setResultado(null);
            }}
            className="text-blue-600 hover:text-blue-800"
          >
            Generar nuevo contrato
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
            <h2 className="text-xl font-semibold mb-2">Generación de Contrato Laboral</h2>
            <p className="text-gray-600">
              Responde las siguientes preguntas para generar un contrato laboral personalizado
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

export default ContratoForm; 