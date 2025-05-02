import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

const EscalamientoHumano = ({ caso, onComplete }) => {
    const [numeroWhatsapp, setNumeroWhatsapp] = useState('');
    const [enviandoWhatsapp, setEnviandoWhatsapp] = useState(false);
    const [errorWhatsapp, setErrorWhatsapp] = useState(null);
    const [whatsappEnviado, setWhatsappEnviado] = useState(false);
    const [registrando, setRegistrando] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setRegistrando(true);
        setError(null);

        try {
            // Registrar el caso
            await axios.post(`${BACKEND_URL}/api/escalamiento/registrar`, {
                caso_id: caso.id,
                descripcion: caso.descripcion,
                prioridad: caso.prioridad
            });

            // Si se proporcionó número de WhatsApp, enviar mensaje
            if (numeroWhatsapp) {
                await enviarWhatsapp();
            }

            if (onComplete) {
                onComplete();
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Error al registrar el caso');
        } finally {
            setRegistrando(false);
        }
    };

    const enviarWhatsapp = async () => {
        setEnviandoWhatsapp(true);
        setErrorWhatsapp(null);

        try {
            const mensaje = `Resumen de tu caso:\n\n${caso.descripcion}\n\n` +
                          `Prioridad: ${caso.prioridad}\n` +
                          `ID del caso: ${caso.id}\n\n` +
                          `Un abogado se pondrá en contacto contigo pronto.`;

            const response = await axios.post(`${BACKEND_URL}/api/whatsapp/enviar`, {
                numero_whatsapp: numeroWhatsapp,
                mensaje_resumen: mensaje
            });

            if (response.data.exito) {
                setWhatsappEnviado(true);
            } else {
                setErrorWhatsapp(response.data.mensaje);
            }
        } catch (err) {
            setErrorWhatsapp(err.response?.data?.detail || 'Error al enviar WhatsApp');
        } finally {
            setEnviandoWhatsapp(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Escalar Caso a Abogado
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Descripción del Caso
                    </label>
                    <p className="text-gray-600 bg-gray-50 p-4 rounded-md">
                        {caso.descripcion}
                    </p>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Prioridad
                    </label>
                    <p className="text-gray-600 bg-gray-50 p-4 rounded-md">
                        {caso.prioridad}
                    </p>
                </div>

                <div>
                    <label htmlFor="whatsapp" className="block text-sm font-medium text-gray-700 mb-2">
                        Número de WhatsApp (opcional)
                    </label>
                    <div className="mt-1 flex rounded-md shadow-sm">
                        <input
                            type="tel"
                            id="whatsapp"
                            value={numeroWhatsapp}
                            onChange={(e) => setNumeroWhatsapp(e.target.value)}
                            placeholder="+57XXXXXXXXXX"
                            className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                    </div>
                    <p className="mt-2 text-sm text-gray-500">
                        Recibirás un resumen del caso por WhatsApp
                    </p>
                </div>

                {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-red-600">{error}</p>
                    </div>
                )}

                {errorWhatsapp && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-red-600">{errorWhatsapp}</p>
                    </div>
                )}

                {whatsappEnviado && (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                        <p className="text-green-600">
                            Resumen enviado exitosamente por WhatsApp
                        </p>
                    </div>
                )}

                <div className="flex justify-end space-x-4">
                    <button
                        type="submit"
                        disabled={registrando || enviandoWhatsapp}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                        {registrando ? 'Registrando...' : 'Registrar Caso'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default EscalamientoHumano; 