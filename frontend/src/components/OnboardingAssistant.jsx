import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

const OnboardingAssistant = ({ onFlowSelected }) => {
    const [consulta, setConsulta] = useState('');
    const [resultado, setResultado] = useState(null);
    const [error, setError] = useState(null);
    const [enviando, setEnviando] = useState(false);

    const ejemplos = [
        "Necesito saber si mi contrato de prestación de servicios es realmente laboral",
        "Quiero calcular mi liquidación por despido",
        "Necesito generar un contrato de trabajo",
        "Quiero que analicen mi contrato actual"
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!consulta.trim()) {
            setError('Por favor, describe tu situación');
            return;
        }

        setEnviando(true);
        setError(null);

        try {
            const response = await axios.post(`${BACKEND_URL}/api/onboarding/analizar`, {
                free_text: consulta
            });
            setResultado(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error al procesar tu consulta');
        } finally {
            setEnviando(false);
        }
    };

    const handleEjemploClick = (ejemplo) => {
        setConsulta(ejemplo);
    };

    const handleFlowSelect = (flujo) => {
        if (onFlowSelected) {
            onFlowSelected(flujo);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">
                ¿En qué puedo ayudarte hoy?
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="consulta" className="block text-sm font-medium text-gray-700 mb-2">
                        Describe tu situación
                    </label>
                    <textarea
                        id="consulta"
                        value={consulta}
                        onChange={(e) => setConsulta(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        rows="4"
                        placeholder="Ej: Necesito saber si mi contrato de prestación de servicios es realmente laboral..."
                    />
                </div>

                <div className="space-y-2">
                    <p className="text-sm text-gray-600">O selecciona un ejemplo:</p>
                    <div className="flex flex-wrap gap-2">
                        {ejemplos.map((ejemplo, index) => (
                            <button
                                key={index}
                                type="button"
                                onClick={() => handleEjemploClick(ejemplo)}
                                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                            >
                                {ejemplo}
                            </button>
                        ))}
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={enviando}
                    className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
                >
                    {enviando ? 'Analizando...' : 'Analizar mi situación'}
                </button>
            </form>

            {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-red-600">{error}</p>
                </div>
            )}

            {resultado && (
                <div className="mt-6 space-y-4">
                    <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                        <p className="text-green-800">{resultado.mensaje_bienvenida}</p>
                    </div>

                    {resultado.necesita_abogado && (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                            <p className="text-yellow-800">
                                Tu caso parece complejo. Te recomendamos consultar con un abogado laboral.
                            </p>
                        </div>
                    )}

                    <div className="space-y-2">
                        <h3 className="font-medium text-gray-900">Pasos sugeridos:</h3>
                        <ul className="list-disc list-inside space-y-1 text-gray-700">
                            {resultado.pasos_sugeridos.map((paso, index) => (
                                <li key={index}>{paso}</li>
                            ))}
                        </ul>
                    </div>

                    <button
                        onClick={() => handleFlowSelect(resultado.flujo_recomendado)}
                        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    >
                        Continuar con este flujo
                    </button>
                </div>
            )}
        </div>
    );
};

export default OnboardingAssistant; 