import React, { useState } from 'react';
import axios from 'axios';
import { BACKEND_URL } from '../config';
import AlertaRevision from './AlertaRevision';

const IndemnizacionForm = () => {
    // Estado para el formulario
    const [salarioMensual, setSalarioMensual] = useState('');
    const [salarioVariable, setSalarioVariable] = useState('');
    const [fechaInicio, setFechaInicio] = useState('');
    const [fechaTermino, setFechaTermino] = useState('');
    const [causaTermino, setCausaTermino] = useState('');
    const [contratoTiempo, setContratoTiempo] = useState('indefinido');
    const [beneficiosAdicionales, setBeneficiosAdicionales] = useState('');
    
    // Estado para resultados
    const [resultado, setResultado] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // Función para calcular periodo en años
    const calcularPeriodo = () => {
        if (!fechaInicio || !fechaTermino) return 0;
        
        const inicio = new Date(fechaInicio);
        const termino = new Date(fechaTermino);
        const diferenciaMilisegundos = termino - inicio;
        const años = diferenciaMilisegundos / (1000 * 60 * 60 * 24 * 365.25);
        
        return años;
    };
    
    // Verificar si es necesaria la revisión por un profesional
    const requiereRevisionProfesional = () => {
        const años = calcularPeriodo();
        const salarioTotal = parseInt(salarioMensual || 0) + parseInt(salarioVariable || 0);
        
        // Criterios para sugerir revisión profesional
        return (
            años > 5 || 
            salarioTotal > 2500000 || 
            causaTermino === 'despido_injustificado' ||
            beneficiosAdicionales.length > 50
        );
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validación básica
        if (!salarioMensual || !fechaInicio || !fechaTermino || !causaTermino) {
            setError('Por favor, complete todos los campos obligatorios');
            return;
        }
        
        // Validar fechas
        if (new Date(fechaInicio) > new Date(fechaTermino)) {
            setError('La fecha de inicio no puede ser posterior a la fecha de término');
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            console.log(`Consultando API en: ${BACKEND_URL}/api/indemnizacion`);
            const response = await axios.post(`${BACKEND_URL}/api/indemnizacion`, {
                salario_mensual: parseInt(salarioMensual),
                salario_variable: parseInt(salarioVariable || 0),
                fecha_inicio: fechaInicio,
                fecha_termino: fechaTermino,
                causa_termino: causaTermino,
                tipo_contrato: contratoTiempo,
                beneficios_adicionales: beneficiosAdicionales
            }, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            setResultado(response.data);
        } catch (err) {
            console.error('Error al calcular indemnización:', err);
            setError(err.response?.data?.detail || 'Error al procesar la solicitud');
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-6">Calculadora de Indemnizaciones</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Salario Mensual Fijo*
                        </label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <span className="text-gray-500 sm:text-sm">$</span>
                            </div>
                            <input
                                type="number"
                                className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-md"
                                placeholder="0.00"
                                value={salarioMensual}
                                onChange={(e) => setSalarioMensual(e.target.value)}
                                required
                            />
                        </div>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Salario Variable Promedio Mensual
                        </label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <span className="text-gray-500 sm:text-sm">$</span>
                            </div>
                            <input
                                type="number"
                                className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-md"
                                placeholder="0.00"
                                value={salarioVariable}
                                onChange={(e) => setSalarioVariable(e.target.value)}
                            />
                        </div>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Fecha de Inicio Laboral*
                        </label>
                        <input
                            type="date"
                            className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                            value={fechaInicio}
                            onChange={(e) => setFechaInicio(e.target.value)}
                            required
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Fecha de Término Laboral*
                        </label>
                        <input
                            type="date"
                            className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                            value={fechaTermino}
                            onChange={(e) => setFechaTermino(e.target.value)}
                            required
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Tipo de Contrato*
                        </label>
                        <select
                            className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            value={contratoTiempo}
                            onChange={(e) => setContratoTiempo(e.target.value)}
                            required
                        >
                            <option value="indefinido">Contrato Indefinido</option>
                            <option value="plazo_fijo">Contrato a Plazo Fijo</option>
                            <option value="obra">Contrato por Obra o Faena</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Causa de Término*
                        </label>
                        <select
                            className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            value={causaTermino}
                            onChange={(e) => setCausaTermino(e.target.value)}
                            required
                        >
                            <option value="">Seleccione causa</option>
                            <option value="renuncia_voluntaria">Renuncia Voluntaria</option>
                            <option value="mutuo_acuerdo">Mutuo Acuerdo</option>
                            <option value="vencimiento_plazo">Vencimiento del Plazo</option>
                            <option value="termino_obra">Conclusión del Trabajo o Servicio</option>
                            <option value="necesidades_empresa">Necesidades de la Empresa</option>
                            <option value="despido_injustificado">Despido Injustificado</option>
                            <option value="caso_fortuito">Caso Fortuito o Fuerza Mayor</option>
                        </select>
                    </div>
                </div>
                
                <div>
                    <label className="block text-sm font-medium text-gray-700">
                        Beneficios Adicionales (vacaciones, bonos, etc.)
                    </label>
                    <textarea
                        rows="3"
                        className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"
                        placeholder="Describa cualquier beneficio adicional relevante para el cálculo"
                        value={beneficiosAdicionales}
                        onChange={(e) => setBeneficiosAdicionales(e.target.value)}
                    ></textarea>
                </div>
                
                <div className="flex items-center justify-end space-x-3">
                    <button
                        type="button"
                        className="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        onClick={() => {
                            // Reiniciar formulario
                            setSalarioMensual('');
                            setSalarioVariable('');
                            setFechaInicio('');
                            setFechaTermino('');
                            setCausaTermino('');
                            setContratoTiempo('indefinido');
                            setBeneficiosAdicionales('');
                            setResultado(null);
                            setError(null);
                        }}
                    >
                        Reiniciar
                    </button>
                    
                    <button
                        type="submit"
                        disabled={loading}
                        className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        {loading ? 'Calculando...' : 'Calcular Indemnización'}
                    </button>
                </div>
            </form>
            
            {error && (
                <div className="mt-4 bg-red-50 border-l-4 border-red-400 p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                </div>
            )}
            
            {resultado && (
                <div className="mt-6 bg-gray-50 shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                    <div className="px-4 py-5 sm:px-6 bg-gray-100">
                        <h3 className="text-lg leading-6 font-medium text-gray-900">Resultado del Cálculo</h3>
                    </div>
                    <div className="border-t border-gray-200">
                        <dl>
                            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Años de servicio</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    {resultado.años_servicio.toFixed(2)} años
                                </dd>
                            </div>
                            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Indemnización por años de servicio</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    ${resultado.indemnizacion_años.toLocaleString()}
                                </dd>
                            </div>
                            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Indemnización sustitutiva de aviso previo</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    ${resultado.indemnizacion_aviso_previo.toLocaleString()}
                                </dd>
                            </div>
                            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Vacaciones proporcionales</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    ${resultado.vacaciones_proporcionales.toLocaleString()}
                                </dd>
                            </div>
                            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Total indemnización estimada</dt>
                                <dd className="mt-1 text-sm font-semibold text-gray-900 sm:mt-0 sm:col-span-2">
                                    ${resultado.total.toLocaleString()}
                                </dd>
                            </div>
                        </dl>
                    </div>
                    <div className="px-4 py-4 sm:px-6 bg-blue-50">
                        <p className="text-sm text-blue-700">
                            {resultado.comentario}
                        </p>
                    </div>
                </div>
            )}
            
            {requiereRevisionProfesional() && (
                <AlertaRevision 
                    mensaje="Su situación podría requerir un análisis más detallado debido a la antigüedad, salario o condiciones especiales. Considere obtener una consulta personalizada."
                    onContactoClick={() => window.location.href = '/contacto'} 
                />
            )}
        </div>
    );
};

export default IndemnizacionForm; 